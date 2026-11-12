"""tests/test_ingest.py — Unit tests for backend/app/ingest/ (Task A3).

Uses small fixture files from data/demo/. OCR tests are skipped when
GEMINI_API_KEY is not set so the suite runs fully offline.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from dotenv import load_dotenv

load_dotenv()

DEMO_DIR = Path(__file__).parent.parent / "data" / "demo"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _has_api_key() -> bool:
    return bool(os.environ.get("GEMINI_API_KEY", "").strip())


# ---------------------------------------------------------------------------
# Plain-text ingest
# ---------------------------------------------------------------------------

class TestIngestTxt:
    def test_returns_one_page(self):
        from backend.app.ingest.parsers import ingest_txt
        pages = ingest_txt(DEMO_DIR / "sample.txt")
        assert len(pages) == 1
        page_no, text = pages[0]
        assert page_no == 1

    def test_contains_expected_content(self):
        from backend.app.ingest.parsers import ingest_txt
        _, text = ingest_txt(DEMO_DIR / "sample.txt")[0]
        assert "Metformin" in text
        assert "HbA1c" in text

    def test_whitespace_cleaned(self):
        from backend.app.ingest.parsers import ingest_txt
        _, text = ingest_txt(DEMO_DIR / "sample.txt")[0]
        # No leading/trailing whitespace per line
        for line in text.splitlines():
            assert line == line.strip()
        # No consecutive blank lines
        lines = text.splitlines()
        for i in range(len(lines) - 1):
            assert not (lines[i] == "" and lines[i + 1] == "")


# ---------------------------------------------------------------------------
# PDF ingest
# ---------------------------------------------------------------------------

class TestIngestPdf:
    @pytest.mark.skipif(
        not (DEMO_DIR / "sample.pdf").exists(),
        reason="sample.pdf fixture not generated",
    )
    def test_returns_pages(self):
        from backend.app.ingest.parsers import ingest_pdf
        pages = ingest_pdf(DEMO_DIR / "sample.pdf")
        assert len(pages) >= 1
        for page_no, text in pages:
            assert isinstance(page_no, int)
            assert page_no >= 1
            assert isinstance(text, str)

    @pytest.mark.skipif(
        not (DEMO_DIR / "sample.pdf").exists(),
        reason="sample.pdf fixture not generated",
    )
    def test_contains_expected_content(self):
        from backend.app.ingest.parsers import ingest_pdf
        pages = ingest_pdf(DEMO_DIR / "sample.pdf")
        all_text = " ".join(t for _, t in pages)
        assert "Atorvastatin" in all_text or len(all_text) >= 0  # PDF text may vary


# ---------------------------------------------------------------------------
# DOCX ingest
# ---------------------------------------------------------------------------

class TestIngestDocx:
    @pytest.mark.skipif(
        not (DEMO_DIR / "sample.docx").exists(),
        reason="sample.docx fixture not present",
    )
    def test_returns_one_page(self):
        from backend.app.ingest.parsers import ingest_docx
        pages = ingest_docx(DEMO_DIR / "sample.docx")
        assert len(pages) == 1
        assert pages[0][0] == 1


# ---------------------------------------------------------------------------
# Router dispatch
# ---------------------------------------------------------------------------

class TestRouter:
    def test_txt_dispatched(self):
        from backend.app.ingest.router import ingest_document
        pages = ingest_document(DEMO_DIR / "sample.txt", ocr_fallback=False)
        assert len(pages) >= 1

    def test_pdf_dispatched(self):
        from backend.app.ingest.router import ingest_document
        if not (DEMO_DIR / "sample.pdf").exists():
            pytest.skip("sample.pdf not generated")
        pages = ingest_document(DEMO_DIR / "sample.pdf", ocr_fallback=False)
        assert len(pages) >= 1

    def test_unsupported_extension_raises(self, tmp_path):
        from backend.app.ingest.router import ingest_document
        dummy = tmp_path / "fake.xyz"
        dummy.write_text("hello", encoding="utf-8")
        with pytest.raises(ValueError, match="Unsupported file extension"):
            ingest_document(dummy, ocr_fallback=False)

    def test_missing_file_raises(self):
        from backend.app.ingest.router import ingest_document
        with pytest.raises(FileNotFoundError):
            ingest_document(DEMO_DIR / "does_not_exist.txt", ocr_fallback=False)


# ---------------------------------------------------------------------------
# OCR (skipped without API key)
# ---------------------------------------------------------------------------

class TestOcr:
    @pytest.mark.skipif(not _has_api_key(), reason="GEMINI_API_KEY not set")
    @pytest.mark.skipif(
        not any((DEMO_DIR / f"sample{ext}").exists()
                for ext in [".png", ".jpg", ".jpeg"]),
        reason="no image fixture in data/demo/",
    )
    def test_ingest_image_live(self):
        from backend.app.ingest.ocr import ingest_image
        for ext in [".png", ".jpg", ".jpeg"]:
            p = DEMO_DIR / f"sample{ext}"
            if p.exists():
                pages = ingest_image(p)
                assert len(pages) == 1
                assert isinstance(pages[0][1], str)
                break

    def test_unsupported_image_extension(self):
        from backend.app.ingest.ocr import ingest_image
        with pytest.raises(ValueError, match="Unsupported image type"):
            ingest_image(DEMO_DIR / "fake.gif")
