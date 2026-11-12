"""tests/test_db.py — Unit tests for backend/app/db.py (Task A1).

Uses an in-memory SQLite database so no files are created.
All queries are scoped by patient_id to verify isolation.
"""

from __future__ import annotations

import uuid
from contextlib import contextmanager

import pytest

from backend.app import db
from backend.app.schema import (
    Correction,
    DocType,
    Fact,
    FactType,
    Flag,
    FlagKind,
    FlagSeverity,
    Source,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def conn():
    """In-memory SQLite connection with all tables created."""
    with db.get_connection(":memory:") as c:
        db.create_tables(c)
        yield c


def _make_fact(patient_id: uuid.UUID, doc_id: uuid.UUID) -> Fact:
    src = Source(doc_id=doc_id, page=1, quote="Metformin 500mg twice daily")
    return Fact(
        patient_id=patient_id,
        type=FactType.medication,
        name="Metformin",
        dose="500mg",
        frequency="twice daily",
        original_value="500mg",
        original_unit="mg",
        source=src,
    )


def _make_flag(patient_id: uuid.UUID, fact_id: uuid.UUID) -> Flag:
    return Flag(
        patient_id=patient_id,
        kind=FlagKind.duplicate,
        severity=FlagSeverity.warning,
        fact_ids=[fact_id],
        message="Duplicate medication entry",
    )


# ---------------------------------------------------------------------------
# Patient tests
# ---------------------------------------------------------------------------

class TestPatient:
    def test_create_and_get(self, conn):
        p = db.create_patient(conn, "Alice")
        fetched = db.get_patient(conn, p.id)
        assert fetched is not None
        assert fetched.name == "Alice"
        assert fetched.id == p.id

    def test_get_missing_returns_none(self, conn):
        assert db.get_patient(conn, uuid.uuid4()) is None

    def test_list_patients(self, conn):
        db.create_patient(conn, "Alice")
        db.create_patient(conn, "Bob")
        patients = db.list_patients(conn)
        names = {p.name for p in patients}
        assert {"Alice", "Bob"}.issubset(names)


# ---------------------------------------------------------------------------
# Document tests
# ---------------------------------------------------------------------------

class TestDocument:
    def test_create_and_get(self, conn):
        p = db.create_patient(conn, "Alice")
        doc = db.create_document(conn, p.id, "labs.pdf", DocType.lab_report, 3)
        fetched = db.get_document(conn, doc.id, p.id)
        assert fetched is not None
        assert fetched.filename == "labs.pdf"
        assert fetched.doc_type == DocType.lab_report
        assert fetched.page_count == 3

    def test_get_wrong_patient_returns_none(self, conn):
        p1 = db.create_patient(conn, "Alice")
        p2 = db.create_patient(conn, "Bob")
        doc = db.create_document(conn, p1.id, "labs.pdf", DocType.lab_report, 1)
        # p2 must not see p1's document
        assert db.get_document(conn, doc.id, p2.id) is None

    def test_list_documents_scoped(self, conn):
        p1 = db.create_patient(conn, "Alice")
        p2 = db.create_patient(conn, "Bob")
        db.create_document(conn, p1.id, "a.pdf", DocType.prescription, 2)
        db.create_document(conn, p2.id, "b.pdf", DocType.discharge_summary, 5)
        assert len(db.list_documents(conn, p1.id)) == 1
        assert len(db.list_documents(conn, p2.id)) == 1


# ---------------------------------------------------------------------------
# Pages tests
# ---------------------------------------------------------------------------

class TestPages:
    def test_save_and_get(self, conn):
        p = db.create_patient(conn, "Alice")
        doc = db.create_document(conn, p.id, "report.pdf", DocType.lab_report, 2)
        db.save_page(conn, doc.id, p.id, 1, "Page one text")
        db.save_page(conn, doc.id, p.id, 2, "Page two text")
        assert db.get_page_text(conn, doc.id, p.id, 1) == "Page one text"
        assert db.get_page_text(conn, doc.id, p.id, 2) == "Page two text"

    def test_get_wrong_patient_returns_none(self, conn):
        p1 = db.create_patient(conn, "Alice")
        p2 = db.create_patient(conn, "Bob")
        doc = db.create_document(conn, p1.id, "r.pdf", DocType.lab_report, 1)
        db.save_page(conn, doc.id, p1.id, 1, "secret text")
        assert db.get_page_text(conn, doc.id, p2.id, 1) is None

    def test_list_pages_ordered(self, conn):
        p = db.create_patient(conn, "Alice")
        doc = db.create_document(conn, p.id, "r.pdf", DocType.lab_report, 3)
        db.save_page(conn, doc.id, p.id, 3, "three")
        db.save_page(conn, doc.id, p.id, 1, "one")
        db.save_page(conn, doc.id, p.id, 2, "two")
        pages = db.list_pages(conn, doc.id, p.id)
        assert [pn for pn, _ in pages] == [1, 2, 3]

    def test_upsert_page(self, conn):
        p = db.create_patient(conn, "Alice")
        doc = db.create_document(conn, p.id, "r.pdf", DocType.lab_report, 1)
        db.save_page(conn, doc.id, p.id, 1, "old text")
        db.save_page(conn, doc.id, p.id, 1, "new text")  # upsert
        assert db.get_page_text(conn, doc.id, p.id, 1) == "new text"


# ---------------------------------------------------------------------------
# Facts tests (append-only)
# ---------------------------------------------------------------------------

class TestFacts:
    def test_save_and_get(self, conn):
        p = db.create_patient(conn, "Alice")
        doc = db.create_document(conn, p.id, "rx.pdf", DocType.prescription, 1)
        fact = _make_fact(p.id, doc.id)
        db.save_fact(conn, fact, doc.id, 1)
        fetched = db.get_fact(conn, fact.id, p.id)
        assert fetched is not None
        assert fetched.name == "Metformin"
        assert fetched.id == fact.id

    def test_get_wrong_patient_returns_none(self, conn):
        p1 = db.create_patient(conn, "Alice")
        p2 = db.create_patient(conn, "Bob")
        doc = db.create_document(conn, p1.id, "rx.pdf", DocType.prescription, 1)
        fact = _make_fact(p1.id, doc.id)
        db.save_fact(conn, fact, doc.id, 1)
        assert db.get_fact(conn, fact.id, p2.id) is None

    def test_list_facts_scoped(self, conn):
        p1 = db.create_patient(conn, "Alice")
        p2 = db.create_patient(conn, "Bob")
        doc1 = db.create_document(conn, p1.id, "a.pdf", DocType.prescription, 1)
        doc2 = db.create_document(conn, p2.id, "b.pdf", DocType.prescription, 1)
        f1 = _make_fact(p1.id, doc1.id)
        f2 = _make_fact(p2.id, doc2.id)
        db.save_fact(conn, f1, doc1.id, 1)
        db.save_fact(conn, f2, doc2.id, 1)
        assert len(db.list_facts(conn, p1.id)) == 1
        assert len(db.list_facts(conn, p2.id)) == 1

    def test_facts_append_only_duplicate_id_raises(self, conn):
        """Inserting the same fact ID twice should raise (PRIMARY KEY constraint)."""
        p = db.create_patient(conn, "Alice")
        doc = db.create_document(conn, p.id, "rx.pdf", DocType.prescription, 1)
        fact = _make_fact(p.id, doc.id)
        db.save_fact(conn, fact, doc.id, 1)
        import sqlite3 as _sqlite3
        with pytest.raises(_sqlite3.IntegrityError):
            db.save_fact(conn, fact, doc.id, 1)

    def test_list_facts_filtered_by_doc(self, conn):
        p = db.create_patient(conn, "Alice")
        doc1 = db.create_document(conn, p.id, "a.pdf", DocType.lab_report, 1)
        doc2 = db.create_document(conn, p.id, "b.pdf", DocType.prescription, 1)
        f1 = _make_fact(p.id, doc1.id)
        f2 = _make_fact(p.id, doc2.id)
        db.save_fact(conn, f1, doc1.id, 1)
        db.save_fact(conn, f2, doc2.id, 1)
        assert len(db.list_facts(conn, p.id, doc_id=doc1.id)) == 1
        assert len(db.list_facts(conn, p.id, doc_id=doc2.id)) == 1
        assert len(db.list_facts(conn, p.id)) == 2


# ---------------------------------------------------------------------------
# Corrections tests
# ---------------------------------------------------------------------------

class TestCorrections:
    def test_save_and_list(self, conn):
        p = db.create_patient(conn, "Alice")
        doc = db.create_document(conn, p.id, "rx.pdf", DocType.prescription, 1)
        fact = _make_fact(p.id, doc.id)
        db.save_fact(conn, fact, doc.id, 1)

        corr = Correction(
            fact_id=fact.id,
            corrected_by=uuid.uuid4(),
            new_fields={"dose": "1000mg"},
            reason="wrong dose",
        )
        db.save_correction(conn, corr, p.id)

        corrections = db.list_corrections_for_fact(conn, fact.id, p.id)
        assert len(corrections) == 1
        assert corrections[0].new_fields == {"dose": "1000mg"}

    def test_corrections_scoped_by_patient(self, conn):
        p1 = db.create_patient(conn, "Alice")
        p2 = db.create_patient(conn, "Bob")
        doc1 = db.create_document(conn, p1.id, "a.pdf", DocType.prescription, 1)
        fact = _make_fact(p1.id, doc1.id)
        db.save_fact(conn, fact, doc1.id, 1)
        corr = Correction(
            fact_id=fact.id, corrected_by=uuid.uuid4(), new_fields={}, reason="test"
        )
        db.save_correction(conn, corr, p1.id)
        # p2 should see nothing
        assert db.list_corrections(conn, p2.id) == []


# ---------------------------------------------------------------------------
# Flags tests
# ---------------------------------------------------------------------------

class TestFlags:
    def test_save_and_list(self, conn):
        p = db.create_patient(conn, "Alice")
        doc = db.create_document(conn, p.id, "a.pdf", DocType.lab_report, 1)
        fact = _make_fact(p.id, doc.id)
        db.save_fact(conn, fact, doc.id, 1)
        flag = _make_flag(p.id, fact.id)
        db.save_flag(conn, flag)
        flags = db.list_flags(conn, p.id)
        assert len(flags) == 1
        assert flags[0].kind == FlagKind.duplicate

    def test_flags_scoped(self, conn):
        p1 = db.create_patient(conn, "Alice")
        p2 = db.create_patient(conn, "Bob")
        doc = db.create_document(conn, p1.id, "a.pdf", DocType.lab_report, 1)
        fact = _make_fact(p1.id, doc.id)
        db.save_fact(conn, fact, doc.id, 1)
        flag = _make_flag(p1.id, fact.id)
        db.save_flag(conn, flag)
        assert len(db.list_flags(conn, p1.id)) == 1
        assert len(db.list_flags(conn, p2.id)) == 0

    def test_delete_flags_reruns_cleanly(self, conn):
        p = db.create_patient(conn, "Alice")
        doc = db.create_document(conn, p.id, "a.pdf", DocType.lab_report, 1)
        fact = _make_fact(p.id, doc.id)
        db.save_fact(conn, fact, doc.id, 1)
        flag = _make_flag(p.id, fact.id)
        db.save_flag(conn, flag)
        deleted = db.delete_flags_for_patient(conn, p.id)
        assert deleted == 1
        assert db.list_flags(conn, p.id) == []
