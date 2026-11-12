"""backend/app/ingest/router.py — Dispatch ingest by file type (Task A3).

Single public function: ingest_document(path) → list[(page_no, text)].

For PDFs, pages that have no extractable text are automatically routed to the
OCR path (requires a live Gemini API key). Pass ``ocr_fallback=False`` in
tests or offline environments to skip OCR and keep the empty-string page.
"""

from __future__ import annotations

import logging
from pathlib import Path

from backend.app.ingest.parsers import (
    PageList,
    ingest_docx,
    ingest_pdf,
    ingest_txt,
)
from backend.app.ingest.ocr import IMAGE_EXTENSIONS

logger = logging.getLogger(__name__)

# Maps lowercase extension → handler tag
_EXT_MAP: dict[str, str] = {
    ".pdf": "pdf",
    ".docx": "docx",
    ".doc": "docx",
    ".txt": "txt",
    ".text": "txt",
}
for _ext in IMAGE_EXTENSIONS:
    _EXT_MAP[_ext] = "image"


def ingest_document(
    path: str | Path,
    ocr_fallback: bool = True,
) -> PageList:
    """Extract (page_no, text) pairs from any supported document.

    Dispatch rules:
    - ``.pdf``  → pypdf; pages with empty text are OCR'd if ``ocr_fallback``.
    - ``.docx`` / ``.doc`` → python-docx (whole doc = page 1).
    - ``.txt``  → plain read (whole file = page 1).
    - image extensions → Gemini vision OCR (whole image = page 1).

    Args:
        path: Path to the document file.
        ocr_fallback: If True, PDF pages with no extractable text are routed
                      to Gemini vision OCR. Set False for offline tests.

    Returns:
        List of (page_no, text) tuples, page_no is 1-based.

    Raises:
        ValueError: If the file extension is not supported.
        FileNotFoundError: If the file does not exist.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Document not found: {path}")

    ext = path.suffix.lower()
    handler = _EXT_MAP.get(ext)
    if handler is None:
        raise ValueError(
            f"Unsupported file extension: {ext!r}. "
            f"Supported: {sorted(_EXT_MAP.keys())}"
        )

    logger.info("Ingesting %s as %s", path.name, handler)

    if handler == "pdf":
        pages = ingest_pdf(path)
        if ocr_fallback:
            pages = _ocr_empty_pdf_pages(path, pages)
        return pages

    if handler == "docx":
        return ingest_docx(path)

    if handler == "txt":
        return ingest_txt(path)

    if handler == "image":
        import os
        if not os.environ.get("GEMINI_API_KEY", "").strip():
            raise ValueError(
                "Image and scan documents require GEMINI_API_KEY for vision OCR. "
                "Please upload a digital PDF, DOCX, or TXT file, or set GEMINI_API_KEY in .env."
            )
        from backend.app.ingest.ocr import ingest_image  # noqa: PLC0415
        return ingest_image(path)

    raise ValueError(f"Unhandled handler tag: {handler!r}")  # pragma: no cover


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _ocr_empty_pdf_pages(path: Path, pages: PageList) -> PageList:
    """Replace empty PDF pages with OCR text using Gemini vision.

    Renders each blank page to a PNG via pypdf's page-to-image API
    (requires Pillow) and sends it to the OCR module.

    Args:
        path: Original PDF path (needed to re-open for rendering).
        pages: Output from ingest_pdf — may contain empty-text entries.

    Returns:
        Updated PageList with OCR text substituted for empty pages.
    """
    empty_indices = [i for i, (_, text) in enumerate(pages) if not text.strip()]
    if not empty_indices:
        return pages

    try:
        from pypdf import PdfReader  # noqa: PLC0415
        import io  # noqa: PLC0415
        from backend.app.ingest.ocr import ocr_pdf_page  # noqa: PLC0415

        reader = PdfReader(str(path))
        updated = list(pages)

        for i in empty_indices:
            page_no, _ = pages[i]
            pdf_page = reader.pages[page_no - 1]
            try:
                # pypdf ≥ 4.x: page.to_image() returns a Pillow Image
                img = pdf_page.to_image()
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                ocr_text = ocr_pdf_page(buf.getvalue(), "image/png")
                updated[i] = (page_no, ocr_text)
                logger.info("OCR substituted for PDF page %d", page_no)
            except Exception as exc:
                logger.warning(
                    "OCR failed for PDF page %d (%s): %s — keeping empty text",
                    page_no, path.name, exc,
                )
        return updated

    except Exception as exc:
        logger.warning("OCR fallback setup failed (%s) — keeping empty pages", exc)
        return pages
