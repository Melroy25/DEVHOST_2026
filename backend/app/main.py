"""backend/app/main.py — FastAPI Application with Auth and Two-Portal Support.

Routes:
- GET  /health
- GET  /users                                 (Demo user list for login)
- GET  /me                                    (Current authenticated user)
- GET  /me/patients                           (Patients accessible to current user)
- POST /patients                              (Create patient owned by current user)
- GET  /patients/{pid}                        (Get patient profile and access tier)
- GET  /patients/{pid}/caretakers             (Owner only: list caretakers)
- POST /patients/{pid}/caretakers             (Owner only: add/invite caretaker)
- PATCH /patients/{pid}/caretakers/{link_id}  (Owner only: update permission)
- DELETE /patients/{pid}/caretakers/{link_id} (Owner only: revoke access)
- POST /patients/{pid}/documents              (Upload & ingest document, write access required)
- GET  /patients/{pid}/documents              (List patient documents, read access required)
- GET  /documents/{did}/page/{n}              (Get page text, read access required)
- GET  /documents/{did}/pages                 (Get all pages, read access required)
"""

from __future__ import annotations

import logging
import os
import shutil
from contextlib import asynccontextmanager
from pathlib import Path
from uuid import UUID

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.app import db
from backend.app.auth import can_access, get_current_user
from backend.app.ingest.router import ingest_document
from backend.app.schema import (
    CaretakerLink,
    CaretakerPermission,
    DocType,
    Document,
    Patient,
    User,
)

logger = logging.getLogger(__name__)

UPLOADS_BASE_DIR = Path(__file__).parent.parent.parent / "data" / "uploads"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Seed demo data and ensure storage directories exist."""
    UPLOADS_BASE_DIR.mkdir(parents=True, exist_ok=True)
    with db.get_connection() as conn:
        db.seed_demo_data(conn)
    yield


app = FastAPI(
    title="One Patient, Many Records",
    description="Medical document extraction and review API with Caretaker access control.",
    version="0.3.0",
    lifespan=lifespan,
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Request & Response Models
# ---------------------------------------------------------------------------


class CreatePatientRequest(BaseModel):
    name: str = Field(..., min_length=1, description="Patient full name")


class AddCaretakerRequest(BaseModel):
    caretaker_user_id: UUID
    permission: CaretakerPermission = CaretakerPermission.view


class UpdateCaretakerRequest(BaseModel):
    permission: CaretakerPermission


class PatientAccessResponse(BaseModel):
    patient: Patient
    permission: str  # 'owner' | 'view' | 'contribute'


class MyPatientItem(BaseModel):
    patient: Patient
    permission: str


# ---------------------------------------------------------------------------
# Meta & Health
# ---------------------------------------------------------------------------


@app.get("/health", tags=["meta"])
def health() -> dict[str, str]:
    """Liveness probe."""
    return {"status": "ok", "version": "0.3.0"}


# ---------------------------------------------------------------------------
# Users & Auth Endpoints
# ---------------------------------------------------------------------------


@app.get("/users", response_model=list[User], tags=["auth"])
def list_users_endpoint():
    """List demo users for the frontend login switcher."""
    with db.get_connection() as conn:
        return db.list_users(conn)


@app.get("/me", response_model=User, tags=["auth"])
def get_me_endpoint(current_user: User = Depends(get_current_user)):
    """Return the authenticated user profile."""
    return current_user


@app.get("/me/patients", response_model=list[MyPatientItem], tags=["auth"])
def list_my_patients_endpoint(current_user: User = Depends(get_current_user)):
    """List all patients owned by or shared with the current user."""
    with db.get_connection() as conn:
        items = db.list_patients_for_user(conn, current_user)
        return [MyPatientItem(patient=item["patient"], permission=item["permission"]) for item in items]


# ---------------------------------------------------------------------------
# Patients API
# ---------------------------------------------------------------------------


@app.post("/patients", response_model=Patient, status_code=status.HTTP_201_CREATED, tags=["patients"])
def create_patient_endpoint(
    body: CreatePatientRequest,
    current_user: User = Depends(get_current_user),
):
    """Create a new patient record owned by the current authenticated user."""
    with db.get_connection() as conn:
        patient = db.create_patient(conn, name=body.name.strip(), owner_user_id=current_user.id)
        return patient


@app.get("/patients/{pid}", response_model=PatientAccessResponse, tags=["patients"])
def get_patient_endpoint(
    pid: UUID,
    current_user: User = Depends(get_current_user),
):
    """Retrieve patient details and current user's permission tier."""
    with db.get_connection() as conn:
        permission = can_access(current_user, pid, "read", conn=conn)
        patient = db.get_patient(conn, pid)
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        return PatientAccessResponse(patient=patient, permission=permission)


# ---------------------------------------------------------------------------
# Caretaker Links API (Manage = Owner only)
# ---------------------------------------------------------------------------


@app.get("/patients/{pid}/caretakers", response_model=list[CaretakerLink], tags=["caretakers"])
def list_caretakers_endpoint(
    pid: UUID,
    current_user: User = Depends(get_current_user),
):
    """List active caretakers for a patient (Owner only)."""
    with db.get_connection() as conn:
        can_access(current_user, pid, "manage", conn=conn)
        return db.list_caretaker_links(conn, patient_id=pid, include_revoked=False)


@app.post(
    "/patients/{pid}/caretakers",
    response_model=CaretakerLink,
    status_code=status.HTTP_201_CREATED,
    tags=["caretakers"],
)
def add_caretaker_endpoint(
    pid: UUID,
    body: AddCaretakerRequest,
    current_user: User = Depends(get_current_user),
):
    """Grant caretaker access to a user (Owner only)."""
    with db.get_connection() as conn:
        can_access(current_user, pid, "manage", conn=conn)

        # Target user must exist and be a caretaker
        target_user = db.get_user(conn, body.caretaker_user_id)
        if not target_user:
            raise HTTPException(status_code=404, detail="Target caretaker user not found")

        link = db.create_caretaker_link(
            conn=conn,
            patient_id=pid,
            caretaker_user_id=body.caretaker_user_id,
            permission=body.permission,
        )
        return link


@app.patch("/patients/{pid}/caretakers/{link_id}", response_model=CaretakerLink, tags=["caretakers"])
def update_caretaker_endpoint(
    pid: UUID,
    link_id: UUID,
    body: UpdateCaretakerRequest,
    current_user: User = Depends(get_current_user),
):
    """Update caretaker permission tier (Owner only)."""
    with db.get_connection() as conn:
        can_access(current_user, pid, "manage", conn=conn)
        updated = db.update_caretaker_permission(
            conn=conn,
            link_id=link_id,
            patient_id=pid,
            permission=body.permission,
        )
        if not updated:
            raise HTTPException(status_code=404, detail="Active caretaker link not found")
        return updated


@app.delete("/patients/{pid}/caretakers/{link_id}", response_model=CaretakerLink, tags=["caretakers"])
def revoke_caretaker_endpoint(
    pid: UUID,
    link_id: UUID,
    current_user: User = Depends(get_current_user),
):
    """Revoke caretaker access (sets revoked_at timestamp; Owner only)."""
    with db.get_connection() as conn:
        can_access(current_user, pid, "manage", conn=conn)
        revoked = db.revoke_caretaker_link(conn=conn, link_id=link_id, patient_id=pid)
        if not revoked:
            raise HTTPException(status_code=404, detail="Active caretaker link not found")
        return revoked


# ---------------------------------------------------------------------------
# Documents & Ingest API
# ---------------------------------------------------------------------------


@app.post(
    "/patients/{pid}/documents",
    response_model=Document,
    status_code=status.HTTP_201_CREATED,
    tags=["documents"],
)
async def upload_patient_document(
    pid: UUID,
    file: UploadFile = File(...),
    doc_type: DocType = Form(DocType.other),
    current_user: User = Depends(get_current_user),
):
    """Upload a medical document, parse text per page, and store transactional records.

    Requires 'write' access (Patient Owner or 'contribute' Caretaker).
    """
    with db.get_connection() as conn:
        can_access(current_user, pid, "write", conn=conn)

    patient_upload_dir = UPLOADS_BASE_DIR / str(pid)
    patient_upload_dir.mkdir(parents=True, exist_ok=True)
    saved_file_path = patient_upload_dir / file.filename

    # Save to disk
    try:
        with open(saved_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as exc:
        logger.error("Failed to save uploaded file %s: %s", file.filename, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {exc}",
        )
    finally:
        await file.close()

    # Parse document BEFORE writing any rows to DB (transactional safety)
    try:
        pages = ingest_document(saved_file_path, ocr_fallback=True)
    except ValueError as ve:
        # Clean up disk file so no orphan remains
        if saved_file_path.exists():
            saved_file_path.unlink()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as exc:
        if saved_file_path.exists():
            saved_file_path.unlink()
        logger.exception("Ingest failed for %s", file.filename)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document parsing failed: {exc}",
        )

    page_count = max(len(pages), 1)

    # Atomically persist document metadata and extracted page texts in one transaction
    try:
        with db.get_connection() as conn:
            doc = db.create_document(
                conn=conn,
                patient_id=pid,
                filename=file.filename,
                doc_type=doc_type,
                uploaded_by=current_user.id,
                page_count=page_count,
            )
            for page_no, text in pages:
                db.save_page(
                    conn=conn,
                    doc_id=doc.id,
                    patient_id=pid,
                    page_no=page_no,
                    text=text,
                )
            return doc
    except Exception as exc:
        if saved_file_path.exists():
            saved_file_path.unlink()
        logger.exception("Database persistence failed for %s", file.filename)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record document in database: {exc}",
        )


@app.get(
    "/patients/{pid}/documents",
    response_model=list[Document],
    tags=["documents"],
)
def list_patient_documents(
    pid: UUID,
    current_user: User = Depends(get_current_user),
):
    """List all documents for a patient (Requires read access)."""
    with db.get_connection() as conn:
        can_access(current_user, pid, "read", conn=conn)
        return db.list_documents(conn, patient_id=pid)


@app.get("/documents/{did}/page/{n}", tags=["documents"])
def get_document_page_endpoint(
    did: UUID,
    n: int,
    current_user: User = Depends(get_current_user),
):
    """Retrieve raw text of page n for a document (Requires read access)."""
    with db.get_connection() as conn:
        row = conn.execute(
            "SELECT patient_id FROM documents WHERE id = ?", (str(did),)
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Document not found")

        doc_patient_id = UUID(row["patient_id"])
        can_access(current_user, doc_patient_id, "read", conn=conn)

        text = db.get_page_text(conn, doc_id=did, patient_id=doc_patient_id, page_no=n)
        if text is None:
            raise HTTPException(status_code=404, detail=f"Page {n} not found for document")

        return {"doc_id": str(did), "page_no": n, "text": text}


@app.get("/documents/{did}/pages", tags=["documents"])
def list_document_pages_endpoint(
    did: UUID,
    current_user: User = Depends(get_current_user),
):
    """Retrieve all pages with text for a document (Requires read access)."""
    with db.get_connection() as conn:
        row = conn.execute(
            "SELECT patient_id FROM documents WHERE id = ?", (str(did),)
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Document not found")

        doc_patient_id = UUID(row["patient_id"])
        can_access(current_user, doc_patient_id, "read", conn=conn)

        pages = db.list_pages(conn, doc_id=did, patient_id=doc_patient_id)
        return [{"page_no": p, "text": t} for p, t in pages]
