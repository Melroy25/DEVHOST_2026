"""tests/test_api.py — Integration tests for FastAPI endpoints with Auth."""

from __future__ import annotations

import io
from pathlib import Path
import uuid
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app import db
from backend.app.schema import CaretakerPermission

DEMO_DIR = Path(__file__).parent.parent / "data" / "demo"


@pytest.fixture(autouse=True)
def setup_db():
    with db.get_connection() as conn:
        db.seed_demo_data(conn)
        conn.execute("DELETE FROM caretaker_links WHERE patient_id = ?", (str(db.DEMO_PATIENT_JHON_ID),))


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok", "version": "0.3.0"}


def test_users_list(client):
    res = client.get("/users")
    assert res.status_code == 200
    users = res.json()
    assert len(users) >= 3
    names = {u["name"] for u in users}
    assert {"Jhon", "Maria", "Sam"}.issubset(names)


def test_patient_crud_with_auth(client):
    headers = {"X-User-Id": str(db.DEMO_JHON_ID)}

    # Create patient
    create_res = client.post("/patients", json={"name": "Eleanor Vance"}, headers=headers)
    assert create_res.status_code == 201
    patient = create_res.json()
    assert patient["name"] == "Eleanor Vance"
    pid = patient["id"]

    # Get patient
    get_res = client.get(f"/patients/{pid}", headers=headers)
    assert get_res.status_code == 200
    body = get_res.json()
    assert body["patient"]["id"] == pid
    assert body["permission"] == "owner"

    # List accessible patients
    me_res = client.get("/me/patients", headers=headers)
    assert me_res.status_code == 200
    pids = [item["patient"]["id"] for item in me_res.json()]
    assert pid in pids


def test_document_upload_and_pages_with_auth(client):
    headers = {"X-User-Id": str(db.DEMO_JHON_ID)}

    # Create patient
    patient = client.post("/patients", json={"name": "Felix Crane"}, headers=headers).json()
    pid = patient["id"]

    # Upload sample.txt
    txt_path = DEMO_DIR / "sample.txt"
    with open(txt_path, "rb") as f:
        upload_res = client.post(
            f"/patients/{pid}/documents",
            files={"file": ("sample.txt", f, "text/plain")},
            data={"doc_type": "prescription"},
            headers=headers,
        )
    assert upload_res.status_code == 201
    doc = upload_res.json()
    assert doc["filename"] == "sample.txt"
    assert doc["doc_type"] == "prescription"
    assert doc["uploaded_by"] == str(db.DEMO_JHON_ID)
    did = doc["id"]

    # List documents
    docs_res = client.get(f"/patients/{pid}/documents", headers=headers)
    assert docs_res.status_code == 200
    assert len(docs_res.json()) >= 1

    # Get page 1
    page_res = client.get(f"/documents/{did}/page/1", headers=headers)
    assert page_res.status_code == 200
    assert "Metformin" in page_res.json()["text"]


def test_caretaker_full_lifecycle(client):
    jhon_headers = {"X-User-Id": str(db.DEMO_JHON_ID)}
    maria_headers = {"X-User-Id": str(db.DEMO_MARIA_ID)}

    # 1. Jhon's default patient
    pid = str(db.DEMO_PATIENT_JHON_ID)

    # Maria cannot access Jhon's records before invitation
    res = client.get(f"/patients/{pid}/documents", headers=maria_headers)
    assert res.status_code == 403

    # 2. Jhon grants 'view' permission to Maria
    add_res = client.post(
        f"/patients/{pid}/caretakers",
        json={"caretaker_user_id": str(db.DEMO_MARIA_ID), "permission": "view"},
        headers=jhon_headers,
    )
    assert add_res.status_code == 201
    link_id = add_res.json()["id"]

    # 3. Maria can read documents now
    docs_res = client.get(f"/patients/{pid}/documents", headers=maria_headers)
    assert docs_res.status_code == 200

    # 4. Maria is denied write (upload) with 'view' permission
    txt_path = DEMO_DIR / "sample.txt"
    with open(txt_path, "rb") as f:
        upload_denied = client.post(
            f"/patients/{pid}/documents",
            files={"file": ("sample.txt", f, "text/plain")},
            data={"doc_type": "other"},
            headers=maria_headers,
        )
    assert upload_denied.status_code == 403

    # 5. Jhon promotes Maria to 'contribute'
    patch_res = client.patch(
        f"/patients/{pid}/caretakers/{link_id}",
        json={"permission": "contribute"},
        headers=jhon_headers,
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["permission"] == "contribute"

    # 6. Maria can now upload documents
    with open(txt_path, "rb") as f:
        upload_ok = client.post(
            f"/patients/{pid}/documents",
            files={"file": ("sample_maria.txt", f, "text/plain")},
            data={"doc_type": "other"},
            headers=maria_headers,
        )
    assert upload_ok.status_code == 201
    assert upload_ok.json()["uploaded_by"] == str(db.DEMO_MARIA_ID)

    # 7. Jhon revokes Maria's access
    del_res = client.delete(f"/patients/{pid}/caretakers/{link_id}", headers=jhon_headers)
    assert del_res.status_code == 200
    assert del_res.json()["revoked_at"] is not None

    # 8. Maria is now denied read access
    read_again = client.get(f"/patients/{pid}/documents", headers=maria_headers)
    assert read_again.status_code == 403
