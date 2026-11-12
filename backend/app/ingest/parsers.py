"""backend/app/ingest/parsers.py — Text extraction for digital documents (Task A3).

Handles PDF, DOCX and plain-text files. Each function returns a list of
(page_no, text) tuples where page_no is 1-based.

For image/scan files use ingest/ocr.py instead.
"""

from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

PageList = list[tuple[int, str]]


def ingest_pdf(path: str | Path) -> PageList:
    """Extract text from a digital (non-scanned) PDF, one item per page.

    Uses pypdf. If a page yields no text (likely a scanned page), that page
    is included with an empty string so the caller knows it exists and can
    route it to OCR.

    Args:
        path: Path to the PDF file.

    Returns:
        List of (page_no, text) tuples, 1-based page numbers.
    """
    from pypdf import PdfReader  # noqa: PLC0415

    path = Path(path)
    logger.info("Ingesting PDF: %s", path.name)
    reader = PdfReader(str(path))
    pages: PageList = []
    for i, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        text = _clean(text)
        pages.append((i, text))
        if not text.strip():
            logger.debug("PDF page %d has no extractable text (may be a scan)", i)
    return pages


def ingest_docx(path: str | Path) -> PageList:
    """Extract text from a DOCX file.

    DOCX has no native page boundaries, so the whole document is returned as
    a single page (page_no=1) with paragraphs joined by newlines.

    Args:
        path: Path to the DOCX file.

    Returns:
        List with a single (1, text) tuple.
    """
    from docx import Document as DocxDocument  # noqa: PLC0415

    path = Path(path)
    logger.info("Ingesting DOCX: %s", path.name)
    doc = DocxDocument(str(path))
    paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
    text = _clean("\n".join(paragraphs))
    return [(1, text)]


def ingest_txt(path: str | Path) -> PageList:
    """Read a plain-text file as a single page.

    Args:
        path: Path to the text file.

    Returns:
        List with a single (1, text) tuple.
    """
    path = Path(path)
    logger.info("Ingesting TXT: %s", path.name)
    text = _clean(path.read_text(encoding="utf-8", errors="replace"))
    return [(1, text)]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _clean(text: str) -> str:
    """Normalise whitespace while keeping newlines.

    - Strips leading/trailing whitespace per line.
    - Collapses runs of blank lines to a single blank line.
    - Strips the overall string.
    """
    lines = [line.strip() for line in text.splitlines()]
    # Collapse consecutive blank lines
    cleaned: list[str] = []
    prev_blank = False
    for line in lines:
        if line == "":
            if not prev_blank:
                cleaned.append("")
            prev_blank = True
        else:
            cleaned.append(line)
            prev_blank = False
    return "\n".join(cleaned).strip()
