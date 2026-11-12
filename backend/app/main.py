"""backend/app/main.py — FastAPI application (Minimal Runnable Demo).

Endpoints:
- GET  /health
- POST /patients
- GET  /patients
- GET  /patients/{pid}
- POST /patients/{pid}/documents (file upload + ingest + DB storage)
- GET  /patients/{pid}/documents
- GET  /documents/{did}/page/{n}
- GET  /documents/{did}/pages
"""

from __future__ import annotations

import logging
import shutil
from contextlib import asynccontextmanager
from pathlib import Path
from uuid import UUID

from fastapi import FastAPI, File, Form, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.app import db
from backend.app.ingest.router import ingest_document
from backend.app.schema import DocType, Document, Patient

logger = logging.getLogger(__name__)

# Base storage directory for uploaded raw files
UPLOADS_BASE_DIR = Path(__file__).parent.parent.parent / "data" / "uploads"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ensure database schema tables are created before serving requests."""
    UPLOADS_BASE_DIR.mkdir(parents=True, exist_ok=True)
    with db.get_connection() as conn:
        db.create_tables(conn)
    yield


app = FastAPI(
    title="One Patient, Many Records",
    description="Medical document extraction and review API.",
    version="0.2.0",
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
# Request Models
# ---------------------------------------------------------------------------


class CreatePatientRequest(BaseModel):
    name: str = Field(..., min_length=1, description="Patient full name")


# ---------------------------------------------------------------------------
# Meta & Health
# ---------------------------------------------------------------------------


@app.get("/health", tags=["meta"])
def health() -> dict[str, str]:
    """Liveness probe."""
    return {"status": "ok", "version": "0.2.0"}


# ---------------------------------------------------------------------------
# Patients API
# ---------------------------------------------------------------------------


@app.post("/patients", response_model=Patient, status_code=status.HTTP_201_CREATED, tags=["patients"])
def create_patient_endpoint(body: CreatePatientRequest):
    """Create a new patient record."""
    with db.get_connection() as conn:
        patient = db.create_patient(conn, name=body.name.strip())
        return patient


@app.get("/patients", response_model=list[Patient], tags=["patients"])
def list_patients_endpoint():
    """List all registered patients."""
    with db.get_connection() as conn:
        return db.list_patients(conn)


@app.get("/patients/{pid}", response_model=Patient, tags=["patients"])
def get_patient_endpoint(pid: UUID):
    """Get a single patient by ID."""
    with db.get_connection() as conn:
        patient = db.get_patient(conn, pid)
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        return patient


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
):
    """Upload a medical document, parse its text per page, and store it.

    Supports PDF, DOCX, TXT, and scanned image formats.
    """
    with db.get_connection() as conn:
        patient = db.get_patient(conn, pid)
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")

    # Persist uploaded file to patient-scoped disk directory
    patient_upload_dir = UPLOADS_BASE_DIR / str(pid)
    patient_upload_dir.mkdir(parents=True, exist_ok=True)
    saved_file_path = patient_upload_dir / file.filename

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

    # Ingest document into (page_no, text) pairs
    try:
        pages = ingest_document(saved_file_path, ocr_fallback=True)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as exc:
        logger.exception("Ingest failed for %s", file.filename)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document parsing failed: {exc}",
        )

    page_count = max(len(pages), 1)

    # Persist document metadata and extracted page texts into DB
    with db.get_connection() as conn:
        doc = db.create_document(
            conn=conn,
            patient_id=pid,
            filename=file.filename,
            doc_type=doc_type,
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


@app.get(
    "/patients/{pid}/documents",
    response_model=list[Document],
    tags=["documents"],
)
def list_patient_documents(pid: UUID):
    """List all documents belonging to a patient."""
    with db.get_connection() as conn:
        patient = db.get_patient(conn, pid)
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        return db.list_documents(conn, patient_id=pid)


@app.get("/documents/{did}/page/{n}", tags=["documents"])
def get_document_page_endpoint(
    did: UUID,
    n: int,
    patient_id: UUID | None = None,
):
    """Retrieve raw text of page n for a document."""
    with db.get_connection() as conn:
        row = conn.execute(
            "SELECT patient_id FROM documents WHERE id = ?", (str(did),)
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Document not found")

        doc_patient_id = UUID(row["patient_id"])
        if patient_id and patient_id != doc_patient_id:
            raise HTTPException(status_code=403, detail="Patient mismatch")

        text = db.get_page_text(conn, doc_id=did, patient_id=doc_patient_id, page_no=n)
        if text is None:
            raise HTTPException(status_code=404, detail=f"Page {n} not found for document")

        return {"doc_id": str(did), "page_no": n, "text": text}


@app.get("/documents/{did}/pages", tags=["documents"])
def list_document_pages_endpoint(
    did: UUID,
    patient_id: UUID | None = None,
):
    """Retrieve all pages with text for a document."""
    with db.get_connection() as conn:
        row = conn.execute(
            "SELECT patient_id FROM documents WHERE id = ?", (str(did),)
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Document not found")

        doc_patient_id = UUID(row["patient_id"])
        if patient_id and patient_id != doc_patient_id:
            raise HTTPException(status_code=403, detail="Patient mismatch")

        pages = db.list_pages(conn, doc_id=did, patient_id=doc_patient_id)
        return [{"page_no": p, "text": t} for p, t in pages]
