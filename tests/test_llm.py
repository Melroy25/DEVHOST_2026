"""tests/test_llm.py — Unit tests for backend/app/llm.py (Task A2).

Tests:
- Valid JSON parsing into Pydantic model
- Single retry on invalid JSON / schema failure
- Logging and re-raising after failed retry
- Plain text generation
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch
import pytest
from pydantic import BaseModel, Field, ValidationError

from backend.app.llm import call_llm_json, call_llm_text


class SampleOutput(BaseModel):
    name: str
    count: int = Field(gt=0)


def test_call_llm_json_success(monkeypatch):
    """Succeeds on first attempt."""
    monkeypatch.setenv("GEMINI_API_KEY", "mock-key")
    with patch("backend.app.llm._call_api", return_value='{"name": "test", "count": 5}') as mock_call:
        res = call_llm_json("give me json", SampleOutput)
        assert res.name == "test"
        assert res.count == 5
        assert mock_call.call_count == 1


def test_call_llm_json_retry_success(monkeypatch):
    """First attempt invalid, second attempt valid -> succeeds after 1 retry."""
    monkeypatch.setenv("GEMINI_API_KEY", "mock-key")
    responses = ['{"name": "invalid", "count": -1}', '{"name": "valid", "count": 2}']
    with patch("backend.app.llm._call_api", side_effect=responses) as mock_call:
        res = call_llm_json("give me json", SampleOutput)
        assert res.name == "valid"
        assert res.count == 2
        assert mock_call.call_count == 2


def test_call_llm_json_retry_fails_and_raises(monkeypatch):
    """Both attempts fail -> raises ValidationError on second attempt."""
    monkeypatch.setenv("GEMINI_API_KEY", "mock-key")
    responses = ['{"name": "bad1", "count": 0}', '{"name": "bad2", "count": -5}']
    with patch("backend.app.llm._call_api", side_effect=responses) as mock_call:
        with pytest.raises(ValidationError):
            call_llm_json("give me json", SampleOutput)
        assert mock_call.call_count == 2


def test_call_llm_text(monkeypatch):
    """Returns raw text from _call_api."""
    monkeypatch.setenv("GEMINI_API_KEY", "mock-key")
    with patch("backend.app.llm._call_api", return_value="plain response"):
        res = call_llm_text("say hello")
        assert res == "plain response"


def test_call_llm_missing_api_key(monkeypatch):
    """Raises RuntimeError if GEMINI_API_KEY is missing."""
    import backend.app.llm as llm_mod
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    llm_mod._client = None
    with pytest.raises(RuntimeError, match="GEMINI_API_KEY is not set"):
        llm_mod._get_client()
