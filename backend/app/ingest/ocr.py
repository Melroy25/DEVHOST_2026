"""backend/app/ingest/ocr.py — Vision-based OCR for scanned pages (Task A3).

Uses a Gemini vision call to extract text from image files or PDF pages that
yielded no text in the digital extraction pass.

The returned text is treated the same as digitally extracted text: it goes
through quote-verification before any facts are stored.
"""

from __future__ import annotations

import base64
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

PageList = list[tuple[int, str]]

# Supported image extensions for direct ingest
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp", ".webp"}

_OCR_PROMPT = (
    "You are a medical document transcription assistant. "
    "Transcribe ALL text visible in this image exactly as it appears, "
    "preserving line breaks, headings, tables and numbers. "
    "Output only the transcribed text — no commentary, no summaries, "
    "no diagnoses, no treatment advice."
)


def ingest_image(path: str | Path) -> PageList:
    """Extract text from an image file using Gemini vision.

    Args:
        path: Path to the image file (PNG, JPEG, TIFF, BMP or WEBP).

    Returns:
        List with a single (1, text) tuple.

    Raises:
        ValueError: If the file extension is not a supported image type.
        RuntimeError: If GEMINI_API_KEY is not configured.
    """
    path = Path(path)
    if path.suffix.lower() not in IMAGE_EXTENSIONS:
        raise ValueError(
            f"Unsupported image type: {path.suffix}. "
            f"Supported: {IMAGE_EXTENSIONS}"
        )
    logger.info("OCR via Gemini vision: %s", path.name)
    text = _call_vision(path)
    return [(1, text.strip())]


def ocr_pdf_page(image_bytes: bytes, mime_type: str = "image/png") -> str:
    """OCR a single PDF page supplied as image bytes.

    Called by the ingest router when a PDF page has no extractable text
    (i.e. it is a scanned page). The caller renders the page to an image
    and passes the bytes here.

    Args:
        image_bytes: Raw image bytes for the page.
        mime_type: MIME type of the image bytes (default ``image/png``).

    Returns:
        Extracted text string.
    """
    logger.info("OCR PDF page via Gemini vision (%d bytes)", len(image_bytes))
    return _call_vision_bytes(image_bytes, mime_type).strip()


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _call_vision(path: Path) -> str:
    """Send an image file to Gemini and return the transcribed text."""
    import mimetypes  # noqa: PLC0415
    mime_type = mimetypes.guess_type(str(path))[0] or "image/jpeg"
    image_bytes = path.read_bytes()
    return _call_vision_bytes(image_bytes, mime_type)


def _call_vision_bytes(image_bytes: bytes, mime_type: str) -> str:
    """Send raw image bytes to Gemini vision and return the response text.

    Args:
        image_bytes: Image content.
        mime_type: MIME type string.

    Returns:
        Raw text from the model.
    """
    from backend.app.llm import _get_client, _MODEL  # noqa: PLC0415
    from google.genai import types as genai_types  # noqa: PLC0415

    client = _get_client()
    response = client.models.generate_content(
        model=_MODEL,
        contents=[
            genai_types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
            _OCR_PROMPT,
        ],
        config=genai_types.GenerateContentConfig(
            response_mime_type="text/plain",
            temperature=0.0,
        ),
    )
    return response.text
