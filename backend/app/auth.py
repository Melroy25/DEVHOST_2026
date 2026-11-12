"""backend/app/auth.py — Authentication and Access Control.

Single source of truth for user resolution and permission checking:
- get_current_user: reads X-User-Id header and validates against DB.
- can_access: enforces role-based access for patient records:
    * Owner (patient): read, write, manage
    * Caretaker (view): read only
    * Caretaker (contribute): read, write (no manage)
    * Revoked / Stranger: 403 Forbidden
"""

from __future__ import annotations

import sqlite3
from uuid import UUID

from fastapi import Header, HTTPException, status

from backend.app import db
from backend.app.schema import CaretakerPermission, Patient, User


def get_current_user(x_user_id: str | None = Header(None, alias="X-User-Id")) -> User:
    """Resolve current user from the X-User-Id HTTP header.

    This is the ONLY function that decides who the user is.
    """
    if not x_user_id or not x_user_id.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please provide a valid X-User-Id header.",
        )

    try:
        user_uuid = UUID(x_user_id.strip())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid UUID format in X-User-Id header.",
        )

    with db.get_connection() as conn:
        user = db.get_user(conn, user_uuid)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"User {user_uuid} not found.",
            )
        return user


def can_access(
    user: User,
    patient_id: UUID,
    need: str,
    conn: sqlite3.Connection | None = None,
) -> str:
    """Validate whether user has requested access level for patient_id.

    Args:
        user: Authenticated User object.
        patient_id: Target patient UUID.
        need: 'read' | 'write' | 'manage'.
        conn: Optional existing open DB connection.

    Returns:
        Access tier string ('owner' | 'view' | 'contribute').

    Raises:
        HTTPException(404): If patient record does not exist.
        HTTPException(403): If user lacks required permission.
    """
    if need not in ("read", "write", "manage"):
        raise ValueError(f"Invalid access need: {need!r}. Must be 'read', 'write', or 'manage'.")

    def _check(c: sqlite3.Connection) -> str:
        patient: Patient | None = db.get_patient(c, patient_id)
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient {patient_id} not found.",
            )

        # 1. Patient Owner: has full read, write, and manage access
        if patient.owner_user_id == user.id:
            return "owner"

        # 2. Caretaker: check active link
        link = db.get_active_caretaker_link(c, patient_id=patient_id, caretaker_user_id=user.id)
        if link is not None:
            if link.permission == CaretakerPermission.view:
                if need == "read":
                    return "view"
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Forbidden: 'view' permission is read-only. Modifications and uploads are disabled.",
                )
            if link.permission == CaretakerPermission.contribute:
                if need in ("read", "write"):
                    return "contribute"
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Forbidden: 'contribute' permission allows reading and uploading, but managing caretakers requires the patient owner.",
                )

        # 3. Revoked caretaker or stranger
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: you do not have permission for this patient record.",
        )

    if conn is not None:
        return _check(conn)

    with db.get_connection() as new_conn:
        return _check(new_conn)
