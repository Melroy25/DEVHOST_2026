"""tests/test_api.py — Integration tests for FastAPI endpoints (backend/app/main.py)."""

from __future__ import annotations

import io
from pathlib import Path
import uuid
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app import db

DEMO_DIR = Path(__file__).parent.parent / "data" / "demo"


@pytest.fixture(autouse=True)
def setup_db():
    with db.get_connection() as conn:
        db.create_tables(conn)


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok", "version": "0.2.0"}


def test_patient_crud(client):
    # Create patient
    create_res = client.post("/patients", json={"name": "Eleanor Vance"})
    assert create_res.status_code == 201
    patient = create_res.json()
    assert patient["name"] == "Eleanor Vance"
    pid = patient["id"]

    # Get patient
    get_res = client.get(f"/patients/{pid}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == pid

    # List patients
    list_res = client.get("/patients")
    assert list_res.status_code == 200
    pids = [p["id"] for p in list_res.json()]
    assert pid in pids


def test_document_upload_and_pages(client):
    # Create patient
    patient = client.post("/patients", json={"name": "Felix Crane"}).json()
    pid = patient["id"]

    # Upload sample.txt
    txt_path = DEMO_DIR / "sample.txt"
    with open(txt_path, "rb") as f:
        upload_res = client.post(
            f"/patients/{pid}/documents",
            files={"file": ("sample.txt", f, "text/plain")},
            data={"doc_type": "prescription"},
        )
    assert upload_res.status_code == 201
    doc = upload_res.json()
    assert doc["filename"] == "sample.txt"
    assert doc["doc_type"] == "prescription"
    assert doc["page_count"] == 1
    did = doc["id"]

    # List documents
    docs_res = client.get(f"/patients/{pid}/documents")
    assert docs_res.status_code == 200
    assert len(docs_res.json()) >= 1

    # Get page 1
    page_res = client.get(f"/documents/{did}/page/1")
    assert page_res.status_code == 200
    assert "Metformin" in page_res.json()["text"]

    # Get all pages
    pages_res = client.get(f"/documents/{did}/pages")
    assert pages_res.status_code == 200
    assert len(pages_res.json()) == 1
    assert pages_res.json()[0]["page_no"] == 1


def test_document_upload_wrong_patient(client):
    fake_pid = str(uuid.uuid4())
    upload_res = client.post(
        f"/patients/{fake_pid}/documents",
        files={"file": ("sample.txt", io.BytesIO(b"Test text"), "text/plain")},
        data={"doc_type": "other"},
    )
    assert upload_res.status_code == 404
