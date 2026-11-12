"""backend/app/llm.py — Gemini LLM client (Task A2).

Single public function: call_llm_json(prompt, pydantic_model).

Rules (from AGENTS.md):
- LLM output must be validated with Pydantic.
- On validation failure: retry once, then log and raise.
- API key comes from .env only. Never hard-coded.
- This file is the only place that imports google.genai; swap model here only.
"""

from __future__ import annotations

import json
import logging
import os
from typing import TYPE_CHECKING, Any, TypeVar

from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError

load_dotenv()

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Lazy client — only instantiated when first called so tests that mock the
# environment do not fail at import time.
# ---------------------------------------------------------------------------

_client: Any = None  # google.genai.Client, typed as Any to avoid hard import


def _get_client() -> Any:
    """Return (and cache) a Gemini API client.

    Raises:
        RuntimeError: If GEMINI_API_KEY is not set in the environment.
    """
    global _client
    if _client is None:
        api_key = os.environ.get("GEMINI_API_KEY", "")
        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not set. Add it to your .env file."
            )
        from google import genai  # noqa: PLC0415
        _client = genai.Client(api_key=api_key)
    return _client


# Default model — change here only.
_MODEL = "gemini-2.0-flash"

T = TypeVar("T", bound=BaseModel)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def call_llm_json(prompt: str, pydantic_model: type[T]) -> T:
    """Call Gemini with JSON output mode and validate the response with Pydantic.

    Retries once on a Pydantic validation failure, then logs and re-raises.

    Args:
        prompt: The full prompt text to send. The caller is responsible for
                including schema context and safety instructions.
        pydantic_model: Pydantic v2 model class to parse the JSON response into.

    Returns:
        A validated instance of ``pydantic_model``.

    Raises:
        ValidationError: If both attempts fail Pydantic validation.
        RuntimeError: If GEMINI_API_KEY is not configured.
        Exception: For network or API errors (not retried).
    """
    client = _get_client()
    last_exc: Exception | None = None

    for attempt in range(1, 3):  # attempt 1, then 1 retry (attempt 2)
        try:
            raw_text = _call_api(client, prompt)
            return _parse_response(raw_text, pydantic_model, attempt)
        except ValidationError as exc:
            last_exc = exc
            logger.warning(
                "LLM JSON validation failed (attempt %d/%d): %s",
                attempt, 2, exc,
            )
            if attempt == 1:
                logger.info("Retrying LLM call...")
                continue
            # Second failure — log and re-raise
            logger.error(
                "LLM JSON validation failed on retry. Logging and skipping. "
                "prompt_start=%r", prompt[:200]
            )
            raise

    # Unreachable, but satisfies type checkers
    assert last_exc is not None
    raise last_exc


def call_llm_text(prompt: str) -> str:
    """Call Gemini and return the raw text response.

    Used by the OCR path and Q&A where the response is prose, not JSON.

    Args:
        prompt: Full prompt text.

    Returns:
        Raw model response string.
    """
    client = _get_client()
    return _call_api(client, prompt)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _call_api(client: Any, prompt: str) -> str:
    """Send a request to the Gemini API and return the text content.

    Args:
        client: Initialised google.genai.Client.
        prompt: Prompt text.

    Returns:
        Raw text from the first response candidate.
    """
    from google.genai import types as genai_types  # noqa: PLC0415

    response = client.models.generate_content(
        model=_MODEL,
        contents=prompt,
        config=genai_types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.0,  # deterministic for extraction
        ),
    )
    return response.text


def _parse_response(raw: str, model_cls: type[T], attempt: int) -> T:
    """Parse raw JSON text into a Pydantic model.

    Args:
        raw: JSON string from the LLM.
        model_cls: Pydantic model class.
        attempt: Current attempt number (for logging).

    Returns:
        Validated model instance.

    Raises:
        ValidationError: If the JSON does not match the schema.
    """
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        logger.warning("LLM response is not valid JSON (attempt %d): %s", attempt, exc)
        # Wrap in ValidationError-like by raising a generic ValueError so the
        # caller's retry loop fires. We re-raise as RuntimeError on attempt 2.
        if attempt == 2:
            raise RuntimeError(f"LLM returned non-JSON twice: {exc}") from exc
        raise ValidationError.from_exception_data(  # type: ignore[attr-defined]
            title=model_cls.__name__,
            input_data={"__root__": raw},
            input_type="python",
            line_errors=[],
        ) from exc

    return model_cls.model_validate(data)
