"""tests/test_access.py — Comprehensive unit tests for can_access permission engine."""

from __future__ import annotations

import uuid
import pytest
from fastapi import HTTPException

from backend.app import db
from backend.app.auth import can_access
from backend.app.schema import CaretakerPermission, UserRole


@pytest.fixture
def conn():
    """In-memory SQLite connection with tables created."""
    with db.get_connection(":memory:") as c:
        db.create_tables(c)
        yield c


@pytest.fixture
def setup_users_and_patient(conn):
    # 1. Patient Owner (Alice)
    alice = db.create_user(conn, name="Alice", role=UserRole.patient)
    patient = db.create_patient(conn, name="Alice Patient Record", owner_user_id=alice.id)

    # 2. View Caretaker (Bob)
    bob = db.create_user(conn, name="Bob", role=UserRole.caretaker)
    link_bob = db.create_caretaker_link(
        conn,
        patient_id=patient.id,
        caretaker_user_id=bob.id,
        permission=CaretakerPermission.view,
    )

    # 3. Contribute Caretaker (Charlie)
    charlie = db.create_user(conn, name="Charlie", role=UserRole.caretaker)
    link_charlie = db.create_caretaker_link(
        conn,
        patient_id=patient.id,
        caretaker_user_id=charlie.id,
        permission=CaretakerPermission.contribute,
    )

    # 4. Revoked Caretaker (David)
    david = db.create_user(conn, name="David", role=UserRole.caretaker)
    link_david = db.create_caretaker_link(
        conn,
        patient_id=patient.id,
        caretaker_user_id=david.id,
        permission=CaretakerPermission.view,
    )
    db.revoke_caretaker_link(conn, link_id=link_david.id, patient_id=patient.id)

    # 5. Stranger (Eve)
    eve = db.create_user(conn, name="Eve", role=UserRole.caretaker)

    return {
        "alice": alice,
        "bob": bob,
        "charlie": charlie,
        "david": david,
        "eve": eve,
        "patient": patient,
    }


def test_owner_access(conn, setup_users_and_patient):
    """Owner has read, write, and manage access."""
    alice = setup_users_and_patient["alice"]
    pid = setup_users_and_patient["patient"].id

    assert can_access(alice, pid, "read", conn=conn) == "owner"
    assert can_access(alice, pid, "write", conn=conn) == "owner"
    assert can_access(alice, pid, "manage", conn=conn) == "owner"


def test_view_caretaker_access(conn, setup_users_and_patient):
    """View caretaker can read, but is denied write and manage."""
    bob = setup_users_and_patient["bob"]
    pid = setup_users_and_patient["patient"].id

    # Read: OK
    assert can_access(bob, pid, "read", conn=conn) == "view"

    # Write: 403 Forbidden
    with pytest.raises(HTTPException) as exc_info:
        can_access(bob, pid, "write", conn=conn)
    assert exc_info.value.status_code == 403

    # Manage: 403 Forbidden
    with pytest.raises(HTTPException) as exc_info:
        can_access(bob, pid, "manage", conn=conn)
    assert exc_info.value.status_code == 403


def test_contribute_caretaker_access(conn, setup_users_and_patient):
    """Contribute caretaker can read and write, but is denied manage."""
    charlie = setup_users_and_patient["charlie"]
    pid = setup_users_and_patient["patient"].id

    # Read: OK
    assert can_access(charlie, pid, "read", conn=conn) == "contribute"

    # Write: OK
    assert can_access(charlie, pid, "write", conn=conn) == "contribute"

    # Manage: 403 Forbidden
    with pytest.raises(HTTPException) as exc_info:
        can_access(charlie, pid, "manage", conn=conn)
    assert exc_info.value.status_code == 403


def test_revoked_caretaker_access(conn, setup_users_and_patient):
    """Revoked caretaker is denied all access (read, write, manage)."""
    david = setup_users_and_patient["david"]
    pid = setup_users_and_patient["patient"].id

    for need in ("read", "write", "manage"):
        with pytest.raises(HTTPException) as exc_info:
            can_access(david, pid, need, conn=conn)
        assert exc_info.value.status_code == 403


def test_stranger_access(conn, setup_users_and_patient):
    """Stranger with no link is denied all access."""
    eve = setup_users_and_patient["eve"]
    pid = setup_users_and_patient["patient"].id

    for need in ("read", "write", "manage"):
        with pytest.raises(HTTPException) as exc_info:
            can_access(eve, pid, need, conn=conn)
        assert exc_info.value.status_code == 403


def test_nonexistent_patient(conn, setup_users_and_patient):
    """Checking access on a missing patient raises 404."""
    alice = setup_users_and_patient["alice"]
    fake_pid = uuid.uuid4()
    with pytest.raises(HTTPException) as exc_info:
        can_access(alice, fake_pid, "read", conn=conn)
    assert exc_info.value.status_code == 404


def test_invalid_need_raises_value_error(conn, setup_users_and_patient):
    alice = setup_users_and_patient["alice"]
    pid = setup_users_and_patient["patient"].id
    with pytest.raises(ValueError, match="Invalid access need"):
        can_access(alice, pid, "delete", conn=conn)
