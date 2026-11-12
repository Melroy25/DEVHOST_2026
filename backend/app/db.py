"""backend/app/db.py — SQLite persistence layer (Task A1).

Design decisions:
- Plain sqlite3 (no ORM) for auditability and simplicity; swap later if needed.
- Facts, corrections and flags are stored as JSON blobs so the Pydantic schema
  is the single source of truth for field shapes.
- Facts are APPEND-ONLY. There is no update path for the facts table.
- Every public query accepts patient_id and filters by it (rule 8).
- Pages table stores raw per-page text so the quote-verify step can re-read it
  without touching the original file.
"""

from __future__ import annotations

import json
import logging
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator
from uuid import UUID, uuid4

from backend.app.schema import (
    Correction,
    Document,
    DocType,
    Fact,
    Flag,
    Patient,
)

logger = logging.getLogger(__name__)

# Default DB path — can be overridden via get_connection(path=...) or the
# DB_PATH environment variable.
DEFAULT_DB_PATH = Path(__file__).parent.parent.parent / "data" / "records.db"

# ---------------------------------------------------------------------------
# Connection & schema
# ---------------------------------------------------------------------------

@contextmanager
def get_connection(path: str | Path = DEFAULT_DB_PATH) -> Generator[sqlite3.Connection, None, None]:
    """Yield an open sqlite3 connection with WAL mode and foreign keys on.

    Args:
        path: Filesystem path for the SQLite file, or ``:memory:``.
    """
    conn = sqlite3.connect(str(path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


DDL = """
CREATE TABLE IF NOT EXISTS patients (
    id          TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    created_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS documents (
    id          TEXT PRIMARY KEY,
    patient_id  TEXT NOT NULL REFERENCES patients(id),
    filename    TEXT NOT NULL,
    doc_type    TEXT NOT NULL,
    uploaded_at TEXT NOT NULL,
    page_count  INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS pages (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    doc_id      TEXT NOT NULL REFERENCES documents(id),
    patient_id  TEXT NOT NULL,
    page_no     INTEGER NOT NULL,
    text        TEXT NOT NULL,
    UNIQUE(doc_id, page_no)
);

CREATE TABLE IF NOT EXISTS facts (
    id          TEXT PRIMARY KEY,
    patient_id  TEXT NOT NULL REFERENCES patients(id),
    doc_id      TEXT NOT NULL REFERENCES documents(id),
    page_no     INTEGER NOT NULL,
    data        TEXT NOT NULL   -- full Fact JSON blob
);

CREATE TABLE IF NOT EXISTS corrections (
    id          TEXT PRIMARY KEY,
    fact_id     TEXT NOT NULL REFERENCES facts(id),
    patient_id  TEXT NOT NULL,
    data        TEXT NOT NULL   -- full Correction JSON blob
);

CREATE TABLE IF NOT EXISTS flags (
    id          TEXT PRIMARY KEY,
    patient_id  TEXT NOT NULL REFERENCES patients(id),
    data        TEXT NOT NULL   -- full Flag JSON blob
);

CREATE INDEX IF NOT EXISTS idx_facts_patient     ON facts(patient_id);
CREATE INDEX IF NOT EXISTS idx_corrections_fact  ON corrections(fact_id);
CREATE INDEX IF NOT EXISTS idx_flags_patient     ON flags(patient_id);
CREATE INDEX IF NOT EXISTS idx_pages_doc         ON pages(doc_id);
"""


def create_tables(conn: sqlite3.Connection) -> None:
    """Create all tables and indexes if they do not already exist."""
    conn.executescript(DDL)
    conn.commit()


# ---------------------------------------------------------------------------
# Patient
# ---------------------------------------------------------------------------

def create_patient(conn: sqlite3.Connection, name: str) -> Patient:
    """Insert a new patient row and return the Patient model.

    Args:
        conn: Open DB connection.
        name: Patient display name.

    Returns:
        The newly created Patient.
    """
    patient = Patient(name=name)
    conn.execute(
        "INSERT INTO patients(id, name, created_at) VALUES (?, ?, ?)",
        (str(patient.id), patient.name, patient.created_at.isoformat()),
    )
    logger.info("Created patient %s (%s)", patient.id, patient.name)
    return patient


def get_patient(conn: sqlite3.Connection, patient_id: UUID) -> Patient | None:
    """Fetch a patient by ID.

    Args:
        conn: Open DB connection.
        patient_id: UUID of the patient.

    Returns:
        Patient model or None if not found.
    """
    row = conn.execute(
        "SELECT id, name, created_at FROM patients WHERE id = ?",
        (str(patient_id),),
    ).fetchone()
    if row is None:
        return None
    return Patient(id=row["id"], name=row["name"], created_at=row["created_at"])


def list_patients(conn: sqlite3.Connection) -> list[Patient]:
    """Return all patients ordered by creation time."""
    rows = conn.execute(
        "SELECT id, name, created_at FROM patients ORDER BY created_at"
    ).fetchall()
    return [Patient(id=r["id"], name=r["name"], created_at=r["created_at"]) for r in rows]


# ---------------------------------------------------------------------------
# Document
# ---------------------------------------------------------------------------

def create_document(
    conn: sqlite3.Connection,
    patient_id: UUID,
    filename: str,
    doc_type: DocType,
    page_count: int,
) -> Document:
    """Insert a document row and return the Document model.

    Args:
        conn: Open DB connection.
        patient_id: Owning patient.
        filename: Original filename.
        doc_type: DocType enum value.
        page_count: Number of pages extracted.

    Returns:
        The newly created Document.
    """
    doc = Document(
        patient_id=patient_id,
        filename=filename,
        doc_type=doc_type,
        page_count=page_count,
    )
    conn.execute(
        "INSERT INTO documents(id, patient_id, filename, doc_type, uploaded_at, page_count) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (
            str(doc.id),
            str(doc.patient_id),
            doc.filename,
            doc.doc_type.value,
            doc.uploaded_at.isoformat(),
            doc.page_count,
        ),
    )
    logger.info("Created document %s for patient %s", doc.id, patient_id)
    return doc


def get_document(
    conn: sqlite3.Connection, doc_id: UUID, patient_id: UUID
) -> Document | None:
    """Fetch a document, scoped to patient_id.

    Args:
        conn: Open DB connection.
        doc_id: UUID of the document.
        patient_id: Must match the document's owner.

    Returns:
        Document model or None.
    """
    row = conn.execute(
        "SELECT * FROM documents WHERE id = ? AND patient_id = ?",
        (str(doc_id), str(patient_id)),
    ).fetchone()
    if row is None:
        return None
    return _row_to_document(row)


def list_documents(conn: sqlite3.Connection, patient_id: UUID) -> list[Document]:
    """Return all documents for a patient.

    Args:
        conn: Open DB connection.
        patient_id: Scoping patient ID.

    Returns:
        List of Document models ordered by upload time.
    """
    rows = conn.execute(
        "SELECT * FROM documents WHERE patient_id = ? ORDER BY uploaded_at",
        (str(patient_id),),
    ).fetchall()
    return [_row_to_document(r) for r in rows]


def _row_to_document(row: sqlite3.Row) -> Document:
    return Document(
        id=row["id"],
        patient_id=row["patient_id"],
        filename=row["filename"],
        doc_type=DocType(row["doc_type"]),
        uploaded_at=row["uploaded_at"],
        page_count=row["page_count"],
    )


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------

def save_page(
    conn: sqlite3.Connection,
    doc_id: UUID,
    patient_id: UUID,
    page_no: int,
    text: str,
) -> None:
    """Upsert a page text row (insert or replace on conflict).

    Args:
        conn: Open DB connection.
        doc_id: Owning document.
        patient_id: Owning patient (denormalised for fast scoped lookups).
        page_no: 1-based page number.
        text: Extracted plain text for this page.
    """
    conn.execute(
        "INSERT OR REPLACE INTO pages(doc_id, patient_id, page_no, text) "
        "VALUES (?, ?, ?, ?)",
        (str(doc_id), str(patient_id), page_no, text),
    )


def get_page_text(
    conn: sqlite3.Connection,
    doc_id: UUID,
    patient_id: UUID,
    page_no: int,
) -> str | None:
    """Return the raw text for a specific page, scoped to patient_id.

    Args:
        conn: Open DB connection.
        doc_id: Document UUID.
        patient_id: Must match the page's owning patient.
        page_no: 1-based page number.

    Returns:
        Plain text string or None if not found.
    """
    row = conn.execute(
        "SELECT text FROM pages WHERE doc_id = ? AND patient_id = ? AND page_no = ?",
        (str(doc_id), str(patient_id), page_no),
    ).fetchone()
    return row["text"] if row else None


def list_pages(
    conn: sqlite3.Connection,
    doc_id: UUID,
    patient_id: UUID,
) -> list[tuple[int, str]]:
    """Return all (page_no, text) pairs for a document, scoped to patient_id.

    Args:
        conn: Open DB connection.
        doc_id: Document UUID.
        patient_id: Scoping patient ID.

    Returns:
        List of (page_no, text) sorted by page_no.
    """
    rows = conn.execute(
        "SELECT page_no, text FROM pages "
        "WHERE doc_id = ? AND patient_id = ? ORDER BY page_no",
        (str(doc_id), str(patient_id)),
    ).fetchall()
    return [(r["page_no"], r["text"]) for r in rows]


# ---------------------------------------------------------------------------
# Facts  (APPEND-ONLY — no update path)
# ---------------------------------------------------------------------------

def save_fact(
    conn: sqlite3.Connection,
    fact: Fact,
    doc_id: UUID,
    page_no: int,
) -> None:
    """Append a new fact row. Facts are never updated in place.

    Args:
        conn: Open DB connection.
        fact: Validated Fact model to persist.
        doc_id: Document the fact was extracted from.
        page_no: Page within that document.
    """
    conn.execute(
        "INSERT INTO facts(id, patient_id, doc_id, page_no, data) VALUES (?, ?, ?, ?, ?)",
        (
            str(fact.id),
            str(fact.patient_id),
            str(doc_id),
            page_no,
            fact.model_dump_json(),
        ),
    )


def get_fact(
    conn: sqlite3.Connection,
    fact_id: UUID,
    patient_id: UUID,
) -> Fact | None:
    """Fetch the original (un-corrected) fact row, scoped to patient_id.

    Args:
        conn: Open DB connection.
        fact_id: UUID of the fact.
        patient_id: Must match the fact's patient.

    Returns:
        Original Fact model or None.
    """
    row = conn.execute(
        "SELECT data FROM facts WHERE id = ? AND patient_id = ?",
        (str(fact_id), str(patient_id)),
    ).fetchone()
    if row is None:
        return None
    return Fact.model_validate_json(row["data"])


def list_facts(
    conn: sqlite3.Connection,
    patient_id: UUID,
    doc_id: UUID | None = None,
) -> list[Fact]:
    """Return original fact rows for a patient, optionally filtered by document.

    These are the raw stored facts. Callers that need effective facts must call
    ``apply_correction()`` and ``active_facts()`` themselves.

    Args:
        conn: Open DB connection.
        patient_id: Scoping patient ID.
        doc_id: If given, limit to facts from this document.

    Returns:
        List of original Fact models.
    """
    if doc_id is not None:
        rows = conn.execute(
            "SELECT data FROM facts WHERE patient_id = ? AND doc_id = ? ORDER BY rowid",
            (str(patient_id), str(doc_id)),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT data FROM facts WHERE patient_id = ? ORDER BY rowid",
            (str(patient_id),),
        ).fetchall()
    return [Fact.model_validate_json(r["data"]) for r in rows]


# ---------------------------------------------------------------------------
# Corrections
# ---------------------------------------------------------------------------

def save_correction(
    conn: sqlite3.Connection,
    correction: Correction,
    patient_id: UUID,
) -> None:
    """Persist a Correction row.

    Args:
        conn: Open DB connection.
        correction: Validated Correction model.
        patient_id: Denormalised for fast patient-scoped lookups.
    """
    conn.execute(
        "INSERT INTO corrections(id, fact_id, patient_id, data) VALUES (?, ?, ?, ?)",
        (
            str(correction.id),
            str(correction.fact_id),
            str(patient_id),
            correction.model_dump_json(),
        ),
    )


def list_corrections_for_fact(
    conn: sqlite3.Connection,
    fact_id: UUID,
    patient_id: UUID,
) -> list[Correction]:
    """Return all corrections for a fact, scoped to patient_id, oldest-first.

    The last element is the most recent correction; pass it to
    ``apply_correction()`` to get the effective fact.

    Args:
        conn: Open DB connection.
        fact_id: UUID of the fact.
        patient_id: Scoping patient ID.

    Returns:
        List of Correction models, oldest first.
    """
    rows = conn.execute(
        "SELECT data FROM corrections "
        "WHERE fact_id = ? AND patient_id = ? ORDER BY rowid",
        (str(fact_id), str(patient_id)),
    ).fetchall()
    return [Correction.model_validate_json(r["data"]) for r in rows]


def list_corrections(
    conn: sqlite3.Connection,
    patient_id: UUID,
) -> list[Correction]:
    """Return all corrections for a patient, scoped to patient_id.

    Args:
        conn: Open DB connection.
        patient_id: Scoping patient ID.

    Returns:
        List of Correction models, insertion order.
    """
    rows = conn.execute(
        "SELECT data FROM corrections WHERE patient_id = ? ORDER BY rowid",
        (str(patient_id),),
    ).fetchall()
    return [Correction.model_validate_json(r["data"]) for r in rows]


# ---------------------------------------------------------------------------
# Flags
# ---------------------------------------------------------------------------

def save_flag(conn: sqlite3.Connection, flag: Flag) -> None:
    """Persist a Flag row.

    Args:
        conn: Open DB connection.
        flag: Validated Flag model.
    """
    conn.execute(
        "INSERT OR REPLACE INTO flags(id, patient_id, data) VALUES (?, ?, ?)",
        (str(flag.id), str(flag.patient_id), flag.model_dump_json()),
    )


def list_flags(conn: sqlite3.Connection, patient_id: UUID) -> list[Flag]:
    """Return all flags for a patient.

    Args:
        conn: Open DB connection.
        patient_id: Scoping patient ID.

    Returns:
        List of Flag models.
    """
    rows = conn.execute(
        "SELECT data FROM flags WHERE patient_id = ? ORDER BY rowid",
        (str(patient_id),),
    ).fetchall()
    return [Flag.model_validate_json(r["data"]) for r in rows]


def delete_flags_for_patient(conn: sqlite3.Connection, patient_id: UUID) -> int:
    """Delete all flags for a patient (called before re-running the flag pass).

    Flags are re-derived from facts on every new document upload, so stale
    flags must be cleared first.

    Args:
        conn: Open DB connection.
        patient_id: Scoping patient ID.

    Returns:
        Number of rows deleted.
    """
    cur = conn.execute(
        "DELETE FROM flags WHERE patient_id = ?", (str(patient_id),)
    )
    return cur.rowcount
