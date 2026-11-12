"""backend/app/db.py — SQLite persistence layer (Schema v0.3.0).

Tables:
- users
- caretaker_links
- patients (with owner_user_id)
- documents (with uploaded_by)
- pages
- facts (append-only)
- corrections
- flags
"""

from __future__ import annotations

import json
import logging
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Generator
from uuid import UUID, uuid4

from backend.app.schema import (
    CaretakerLink,
    CaretakerPermission,
    Correction,
    DocType,
    Document,
    Fact,
    Flag,
    Patient,
    User,
    UserRole,
)

logger = logging.getLogger(__name__)

DEFAULT_DB_PATH = Path(__file__).parent.parent.parent / "data" / "records.db"

# Deterministic demo UUIDs for seeded accounts
DEMO_JHON_ID = UUID("11111111-1111-1111-1111-111111111111")
DEMO_MARIA_ID = UUID("22222222-2222-2222-2222-222222222222")
DEMO_SAM_ID = UUID("33333333-3333-3333-3333-333333333333")
DEMO_PATIENT_JHON_ID = UUID("44444444-4444-4444-4444-444444444444")


@contextmanager
def get_connection(path: str | Path = DEFAULT_DB_PATH) -> Generator[sqlite3.Connection, None, None]:
    """Yield an open sqlite3 connection with WAL mode and foreign keys on."""
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


DDL_TABLES = """
CREATE TABLE IF NOT EXISTS users (
    id          TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    role        TEXT NOT NULL,
    created_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS patients (
    id            TEXT PRIMARY KEY,
    name          TEXT NOT NULL,
    owner_user_id TEXT NOT NULL REFERENCES users(id),
    created_at    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS caretaker_links (
    id                TEXT PRIMARY KEY,
    patient_id        TEXT NOT NULL REFERENCES patients(id),
    caretaker_user_id TEXT NOT NULL REFERENCES users(id),
    permission        TEXT NOT NULL,
    created_at        TEXT NOT NULL,
    revoked_at        TEXT
);

CREATE TABLE IF NOT EXISTS documents (
    id          TEXT PRIMARY KEY,
    patient_id  TEXT NOT NULL REFERENCES patients(id),
    filename    TEXT NOT NULL,
    doc_type    TEXT NOT NULL,
    uploaded_by TEXT NOT NULL REFERENCES users(id),
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
    data        TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS corrections (
    id          TEXT PRIMARY KEY,
    fact_id     TEXT NOT NULL REFERENCES facts(id),
    patient_id  TEXT NOT NULL,
    data        TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS flags (
    id          TEXT PRIMARY KEY,
    patient_id  TEXT NOT NULL REFERENCES patients(id),
    data        TEXT NOT NULL
);
"""

DDL_INDEXES = """
CREATE INDEX IF NOT EXISTS idx_patients_owner    ON patients(owner_user_id);
CREATE INDEX IF NOT EXISTS idx_caretakers_pat    ON caretaker_links(patient_id);
CREATE INDEX IF NOT EXISTS idx_caretakers_user   ON caretaker_links(caretaker_user_id);
CREATE INDEX IF NOT EXISTS idx_facts_patient     ON facts(patient_id);
CREATE INDEX IF NOT EXISTS idx_corrections_fact  ON corrections(fact_id);
CREATE INDEX IF NOT EXISTS idx_flags_patient     ON flags(patient_id);
CREATE INDEX IF NOT EXISTS idx_pages_doc         ON pages(doc_id);
"""


def create_tables(conn: sqlite3.Connection) -> None:
    """Create all tables and run backward-compatible schema updates."""
    conn.executescript(DDL_TABLES)

    # Migrate older patients table if owner_user_id column is missing
    cols = [r["name"] for r in conn.execute("PRAGMA table_info(patients)").fetchall()]
    if "owner_user_id" not in cols:
        conn.execute(f"ALTER TABLE patients ADD COLUMN owner_user_id TEXT DEFAULT '{DEMO_JHON_ID}'")

    # Migrate older documents table if uploaded_by column is missing
    doc_cols = [r["name"] for r in conn.execute("PRAGMA table_info(documents)").fetchall()]
    if "uploaded_by" not in doc_cols:
        conn.execute(f"ALTER TABLE documents ADD COLUMN uploaded_by TEXT DEFAULT '{DEMO_JHON_ID}'")

    conn.executescript(DDL_INDEXES)
    conn.commit()
    seed_demo_data(conn)


def seed_demo_data(conn: sqlite3.Connection) -> None:
    """Seed demo accounts: Jhon (patient), Maria (caretaker), Sam (caretaker).

    Also ensures a Patient record owned by Jhon exists.
    No caretaker links are created by default.
    """
    # 1. Jhon (patient)
    if not get_user(conn, DEMO_JHON_ID):
        conn.execute(
            "INSERT INTO users(id, name, role, created_at) VALUES (?, ?, ?, ?)",
            (str(DEMO_JHON_ID), "Jhon", UserRole.patient.value, datetime.utcnow().isoformat()),
        )

    # 2. Maria (caretaker)
    if not get_user(conn, DEMO_MARIA_ID):
        conn.execute(
            "INSERT INTO users(id, name, role, created_at) VALUES (?, ?, ?, ?)",
            (str(DEMO_MARIA_ID), "Maria", UserRole.caretaker.value, datetime.utcnow().isoformat()),
        )

    # 3. Sam (caretaker)
    if not get_user(conn, DEMO_SAM_ID):
        conn.execute(
            "INSERT INTO users(id, name, role, created_at) VALUES (?, ?, ?, ?)",
            (str(DEMO_SAM_ID), "Sam", UserRole.caretaker.value, datetime.utcnow().isoformat()),
        )

    # 4. Patient record for Jhon
    existing_patient = get_patient(conn, DEMO_PATIENT_JHON_ID)
    if not existing_patient:
        conn.execute(
            "INSERT INTO patients(id, name, owner_user_id, created_at) VALUES (?, ?, ?, ?)",
            (str(DEMO_PATIENT_JHON_ID), "Jhon", str(DEMO_JHON_ID), datetime.utcnow().isoformat()),
        )

    conn.commit()


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------


def create_user(
    conn: sqlite3.Connection,
    name: str,
    role: UserRole,
    user_id: UUID | None = None,
) -> User:
    """Create a new user."""
    uid = user_id or uuid4()
    now = datetime.utcnow()
    user = User(id=uid, name=name.strip(), role=role, created_at=now)
    conn.execute(
        "INSERT INTO users(id, name, role, created_at) VALUES (?, ?, ?, ?)",
        (str(user.id), user.name, user.role.value, user.created_at.isoformat()),
    )
    return user


def get_user(conn: sqlite3.Connection, user_id: UUID) -> User | None:
    """Retrieve user by ID."""
    row = conn.execute(
        "SELECT id, name, role, created_at FROM users WHERE id = ?",
        (str(user_id),),
    ).fetchone()
    if not row:
        return None
    return User(id=row["id"], name=row["name"], role=UserRole(row["role"]), created_at=row["created_at"])


def list_users(conn: sqlite3.Connection) -> list[User]:
    """Return all registered users."""
    rows = conn.execute("SELECT id, name, role, created_at FROM users ORDER BY created_at").fetchall()
    return [User(id=r["id"], name=r["name"], role=UserRole(r["role"]), created_at=r["created_at"]) for r in rows]


# ---------------------------------------------------------------------------
# Patients
# ---------------------------------------------------------------------------


def create_patient(
    conn: sqlite3.Connection,
    name: str,
    owner_user_id: UUID | None = None,
    patient_id: UUID | None = None,
) -> Patient:
    """Insert a new patient row owned by owner_user_id."""
    pid = patient_id or uuid4()
    owner_id = owner_user_id or DEMO_JHON_ID
    now = datetime.utcnow()
    patient = Patient(id=pid, name=name.strip(), owner_user_id=owner_id, created_at=now)
    conn.execute(
        "INSERT INTO patients(id, name, owner_user_id, created_at) VALUES (?, ?, ?, ?)",
        (str(patient.id), patient.name, str(patient.owner_user_id), patient.created_at.isoformat()),
    )
    return patient


def get_patient(conn: sqlite3.Connection, patient_id: UUID) -> Patient | None:
    """Fetch patient by ID."""
    row = conn.execute(
        "SELECT id, name, owner_user_id, created_at FROM patients WHERE id = ?",
        (str(patient_id),),
    ).fetchone()
    if not row:
        return None
    return Patient(id=row["id"], name=row["name"], owner_user_id=row["owner_user_id"], created_at=row["created_at"])


def list_patients(conn: sqlite3.Connection) -> list[Patient]:
    """Return all patients in the system."""
    rows = conn.execute("SELECT id, name, owner_user_id, created_at FROM patients ORDER BY created_at").fetchall()
    return [Patient(id=r["id"], name=r["name"], owner_user_id=r["owner_user_id"], created_at=r["created_at"]) for r in rows]


def list_patients_for_user(conn: sqlite3.Connection, user: User) -> list[dict]:
    """Return list of patients accessible to the given user along with granted permission.

    Returned item: {"patient": Patient, "permission": "manage" | "view" | "contribute"}
    """
    results: list[dict] = []
    seen_ids = set()

    # 1. Patients owned by user
    owned_rows = conn.execute(
        "SELECT id, name, owner_user_id, created_at FROM patients WHERE owner_user_id = ? ORDER BY created_at",
        (str(user.id),),
    ).fetchall()
    for r in owned_rows:
        pat = Patient(id=r["id"], name=r["name"], owner_user_id=r["owner_user_id"], created_at=r["created_at"])
        results.append({"patient": pat, "permission": "manage"})
        seen_ids.add(pat.id)

    # 2. Patients linked as active caretaker
    linked_rows = conn.execute(
        """
        SELECT p.id, p.name, p.owner_user_id, p.created_at, cl.permission
        FROM caretaker_links cl
        JOIN patients p ON cl.patient_id = p.id
        WHERE cl.caretaker_user_id = ? AND cl.revoked_at IS NULL
        ORDER BY cl.created_at
        """,
        (str(user.id),),
    ).fetchall()
    for r in linked_rows:
        pid = UUID(r["id"])
        if pid not in seen_ids:
            pat = Patient(id=r["id"], name=r["name"], owner_user_id=r["owner_user_id"], created_at=r["created_at"])
            results.append({"patient": pat, "permission": r["permission"]})
            seen_ids.add(pid)

    return results


# ---------------------------------------------------------------------------
# Caretaker Links
# ---------------------------------------------------------------------------


def create_caretaker_link(
    conn: sqlite3.Connection,
    patient_id: UUID,
    caretaker_user_id: UUID,
    permission: CaretakerPermission = CaretakerPermission.view,
) -> CaretakerLink:
    """Create or reactivate a caretaker link for a patient."""
    # Check if a link already exists
    row = conn.execute(
        "SELECT id, patient_id, caretaker_user_id, permission, created_at, revoked_at "
        "FROM caretaker_links WHERE patient_id = ? AND caretaker_user_id = ?",
        (str(patient_id), str(caretaker_user_id)),
    ).fetchone()

    if row:
        link_id = UUID(row["id"])
        conn.execute(
            "UPDATE caretaker_links SET permission = ?, revoked_at = NULL WHERE id = ?",
            (permission.value, str(link_id)),
        )
        return CaretakerLink(
            id=link_id,
            patient_id=patient_id,
            caretaker_user_id=caretaker_user_id,
            permission=permission,
            created_at=row["created_at"],
            revoked_at=None,
        )

    link = CaretakerLink(
        patient_id=patient_id,
        caretaker_user_id=caretaker_user_id,
        permission=permission,
    )
    conn.execute(
        "INSERT INTO caretaker_links(id, patient_id, caretaker_user_id, permission, created_at, revoked_at) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (
            str(link.id),
            str(link.patient_id),
            str(link.caretaker_user_id),
            link.permission.value,
            link.created_at.isoformat(),
            None,
        ),
    )
    return link


def get_caretaker_link(conn: sqlite3.Connection, link_id: UUID) -> CaretakerLink | None:
    """Fetch caretaker link by its ID."""
    row = conn.execute(
        "SELECT id, patient_id, caretaker_user_id, permission, created_at, revoked_at "
        "FROM caretaker_links WHERE id = ?",
        (str(link_id),),
    ).fetchone()
    if not row:
        return None
    return CaretakerLink(
        id=row["id"],
        patient_id=row["patient_id"],
        caretaker_user_id=row["caretaker_user_id"],
        permission=CaretakerPermission(row["permission"]),
        created_at=row["created_at"],
        revoked_at=row["revoked_at"],
    )


def get_active_caretaker_link(
    conn: sqlite3.Connection,
    patient_id: UUID,
    caretaker_user_id: UUID,
) -> CaretakerLink | None:
    """Return active (non-revoked) link between patient and caretaker."""
    row = conn.execute(
        "SELECT id, patient_id, caretaker_user_id, permission, created_at, revoked_at "
        "FROM caretaker_links WHERE patient_id = ? AND caretaker_user_id = ? AND revoked_at IS NULL",
        (str(patient_id), str(caretaker_user_id)),
    ).fetchone()
    if not row:
        return None
    return CaretakerLink(
        id=row["id"],
        patient_id=row["patient_id"],
        caretaker_user_id=row["caretaker_user_id"],
        permission=CaretakerPermission(row["permission"]),
        created_at=row["created_at"],
        revoked_at=None,
    )


def list_caretaker_links(
    conn: sqlite3.Connection,
    patient_id: UUID,
    include_revoked: bool = False,
) -> list[CaretakerLink]:
    """List caretaker links for a patient."""
    if include_revoked:
        rows = conn.execute(
            "SELECT id, patient_id, caretaker_user_id, permission, created_at, revoked_at "
            "FROM caretaker_links WHERE patient_id = ? ORDER BY created_at",
            (str(patient_id),),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT id, patient_id, caretaker_user_id, permission, created_at, revoked_at "
            "FROM caretaker_links WHERE patient_id = ? AND revoked_at IS NULL ORDER BY created_at",
            (str(patient_id),),
        ).fetchall()

    return [
        CaretakerLink(
            id=r["id"],
            patient_id=r["patient_id"],
            caretaker_user_id=r["caretaker_user_id"],
            permission=CaretakerPermission(r["permission"]),
            created_at=r["created_at"],
            revoked_at=r["revoked_at"],
        )
        for r in rows
    ]


def update_caretaker_permission(
    conn: sqlite3.Connection,
    link_id: UUID,
    patient_id: UUID,
    permission: CaretakerPermission,
) -> CaretakerLink | None:
    """Update permission on an active caretaker link."""
    cur = conn.execute(
        "UPDATE caretaker_links SET permission = ? WHERE id = ? AND patient_id = ? AND revoked_at IS NULL",
        (permission.value, str(link_id), str(patient_id)),
    )
    if cur.rowcount == 0:
        return None
    return get_caretaker_link(conn, link_id)


def revoke_caretaker_link(
    conn: sqlite3.Connection,
    link_id: UUID,
    patient_id: UUID,
) -> CaretakerLink | None:
    """Revoke caretaker access (soft delete via revoked_at timestamp)."""
    now = datetime.utcnow().isoformat()
    cur = conn.execute(
        "UPDATE caretaker_links SET revoked_at = ? WHERE id = ? AND patient_id = ? AND revoked_at IS NULL",
        (now, str(link_id), str(patient_id)),
    )
    if cur.rowcount == 0:
        return None
    return get_caretaker_link(conn, link_id)


# ---------------------------------------------------------------------------
# Documents
# ---------------------------------------------------------------------------


def create_document(
    conn: sqlite3.Connection,
    patient_id: UUID,
    filename: str,
    doc_type: DocType,
    page_count: int,
    uploaded_by: UUID | None = None,
) -> Document:
    """Insert a document row with uploader ID."""
    uploader = uploaded_by or DEMO_JHON_ID
    doc = Document(
        patient_id=patient_id,
        filename=filename,
        doc_type=doc_type,
        uploaded_by=uploader,
        page_count=page_count,
    )
    conn.execute(
        "INSERT INTO documents(id, patient_id, filename, doc_type, uploaded_by, uploaded_at, page_count) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            str(doc.id),
            str(doc.patient_id),
            doc.filename,
            doc.doc_type.value,
            str(doc.uploaded_by),
            doc.uploaded_at.isoformat(),
            doc.page_count,
        ),
    )
    return doc


def get_document(conn: sqlite3.Connection, doc_id: UUID, patient_id: UUID) -> Document | None:
    """Fetch document scoped to patient_id."""
    row = conn.execute(
        "SELECT * FROM documents WHERE id = ? AND patient_id = ?",
        (str(doc_id), str(patient_id)),
    ).fetchone()
    if not row:
        return None
    return _row_to_document(row)


def list_documents(conn: sqlite3.Connection, patient_id: UUID) -> list[Document]:
    """List documents for patient."""
    rows = conn.execute(
        "SELECT * FROM documents WHERE patient_id = ? ORDER BY uploaded_at DESC",
        (str(patient_id),),
    ).fetchall()
    return [_row_to_document(r) for r in rows]


def _row_to_document(row: sqlite3.Row) -> Document:
    return Document(
        id=row["id"],
        patient_id=row["patient_id"],
        filename=row["filename"],
        doc_type=DocType(row["doc_type"]),
        uploaded_by=UUID(row["uploaded_by"]) if "uploaded_by" in row.keys() and row["uploaded_by"] else DEMO_JHON_ID,
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
    """Save or update page text."""
    conn.execute(
        "INSERT OR REPLACE INTO pages(doc_id, patient_id, page_no, text) VALUES (?, ?, ?, ?)",
        (str(doc_id), str(patient_id), page_no, text),
    )


def get_page_text(
    conn: sqlite3.Connection,
    doc_id: UUID,
    patient_id: UUID,
    page_no: int,
) -> str | None:
    """Return raw text for a specific page."""
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
    """Return all (page_no, text) pairs for a document."""
    rows = conn.execute(
        "SELECT page_no, text FROM pages WHERE doc_id = ? AND patient_id = ? ORDER BY page_no",
        (str(doc_id), str(patient_id)),
    ).fetchall()
    return [(r["page_no"], r["text"]) for r in rows]


# ---------------------------------------------------------------------------
# Facts (APPEND-ONLY)
# ---------------------------------------------------------------------------


def save_fact(
    conn: sqlite3.Connection,
    fact: Fact,
    doc_id: UUID,
    page_no: int,
) -> None:
    """Append a new fact row."""
    conn.execute(
        "INSERT INTO facts(id, patient_id, doc_id, page_no, data) VALUES (?, ?, ?, ?, ?)",
        (str(fact.id), str(fact.patient_id), str(doc_id), page_no, fact.model_dump_json()),
    )


def get_fact(conn: sqlite3.Connection, fact_id: UUID, patient_id: UUID) -> Fact | None:
    """Fetch fact scoped to patient_id."""
    row = conn.execute(
        "SELECT data FROM facts WHERE id = ? AND patient_id = ?",
        (str(fact_id), str(patient_id)),
    ).fetchone()
    return Fact.model_validate_json(row["data"]) if row else None


def list_facts(
    conn: sqlite3.Connection,
    patient_id: UUID,
    doc_id: UUID | None = None,
) -> list[Fact]:
    """Return facts for patient."""
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
    """Persist a correction row."""
    conn.execute(
        "INSERT INTO corrections(id, fact_id, patient_id, data) VALUES (?, ?, ?, ?)",
        (str(correction.id), str(correction.fact_id), str(patient_id), correction.model_dump_json()),
    )


def list_corrections_for_fact(
    conn: sqlite3.Connection,
    fact_id: UUID,
    patient_id: UUID,
) -> list[Correction]:
    """Return corrections for fact."""
    rows = conn.execute(
        "SELECT data FROM corrections WHERE fact_id = ? AND patient_id = ? ORDER BY rowid",
        (str(fact_id), str(patient_id)),
    ).fetchall()
    return [Correction.model_validate_json(r["data"]) for r in rows]


def list_corrections(conn: sqlite3.Connection, patient_id: UUID) -> list[Correction]:
    """Return all corrections for patient."""
    rows = conn.execute(
        "SELECT data FROM corrections WHERE patient_id = ? ORDER BY rowid",
        (str(patient_id),),
    ).fetchall()
    return [Correction.model_validate_json(r["data"]) for r in rows]


# ---------------------------------------------------------------------------
# Flags
# ---------------------------------------------------------------------------


def save_flag(conn: sqlite3.Connection, flag: Flag) -> None:
    """Persist a flag."""
    conn.execute(
        "INSERT OR REPLACE INTO flags(id, patient_id, data) VALUES (?, ?, ?)",
        (str(flag.id), str(flag.patient_id), flag.model_dump_json()),
    )


def list_flags(conn: sqlite3.Connection, patient_id: UUID) -> list[Flag]:
    """List flags for patient."""
    rows = conn.execute(
        "SELECT data FROM flags WHERE patient_id = ? ORDER BY rowid",
        (str(patient_id),),
    ).fetchall()
    return [Flag.model_validate_json(r["data"]) for r in rows]


def delete_flags_for_patient(conn: sqlite3.Connection, patient_id: UUID) -> int:
    """Clear all flags for patient."""
    cur = conn.execute("DELETE FROM flags WHERE patient_id = ?", (str(patient_id),))
    return cur.rowcount
