# One Patient, Many Records

Turn a patient's pile of medical documents into a verified, dated clinical history.

Features two specialized portals (Patient Portal & Caretaker Portal) sharing a unified backend with role-based access control, document ingestion, and verifiable quote tracking.

---

## Demo Accounts

The application automatically seeds three demo personas:
- **Jhon (Patient)**: Owns health record `Jhon`, uploads documents, grants/revokes caretaker access.
- **Maria (Caretaker)**: Can be granted `view` (read-only) or `contribute` (read + upload) access by Jhon.
- **Sam (Caretaker)**: Demonstrates uninvited/stranger isolation and independent caretaker workflows.

---

## How to run

### Prerequisites
- Python 3.11+
- Node.js 18+ and npm

### 1. Environment Configuration
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
*(On Windows: `copy .env.example .env`)*

Optional: Add your `GEMINI_API_KEY` for OCR on scanned pages. Note that plain text, digital PDFs, and DOCX files ingest fully offline without an API key.

### 2. Backend Setup
Install Python dependencies:
```bash
pip install -r requirements.txt
```

### 3. Frontend Setup
Install frontend packages:
```bash
cd frontend
npm install
cd ..
```

### 4. Running the Development Servers

#### Option A: One-click launcher scripts
- **Windows**: Double-click `run_dev.bat` or run:
  ```cmd
  run_dev.bat
  ```
- **macOS / Linux**:
  ```bash
  chmod +x run_dev.sh
  ./run_dev.sh
  ```

#### Option B: Individual terminal sessions

**Terminal 1 — Backend (FastAPI)**:
```bash
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
- API Base: `http://localhost:8000`
- Interactive OpenAPI Docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

**Terminal 2 — Frontend (React + Vite)**:
```bash
cd frontend
npm run dev
```
- Web Application: `http://localhost:5173`

---

## Testing

Run all unit, access control, and integration tests:
```bash
python -m pytest tests/ -v
```

---

## Architecture & Portals

- **Shared Patient View (`PatientRecordView`)**: Built once and shared across both portals. Dynamically adapts controls based on role and access permissions (`owner`, `contribute`, or `view`).
- **Access Control Matrix (`can_access`)**:
  - **Owner**: Full access (`read`, `write`, `manage`).
  - **Caretaker (contribute)**: Review records, view extracted text, and upload documents (`read`, `write`).
  - **Caretaker (view)**: Read-only access to records (`read`). Uploading and caretaker management are disabled.
  - **Stranger / Revoked**: Access denied (`403 Forbidden`).
- **Ingestion Pipeline**: Digital PDF (`pypdf`), DOCX (`python-docx`), plain text with smart pagination (`RECORD #` and form feeds), and vision OCR for scanned pages.
