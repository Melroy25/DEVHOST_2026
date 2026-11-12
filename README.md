# One Patient, Many Records

Turn a patient's pile of medical documents into a verified, dated clinical history.

Every fact links to its source passage with verifiable quotes. Contradictions and gaps are flagged, never silently resolved. The system never diagnoses, never invents facts, and never gives treatment advice.

---

## How to run

### Prerequisites
- Python 3.11+
- Node.js 18+ and npm

### 1. Environment Configuration
Copy `.env.example` to `.env` and fill in your Gemini API key (needed for OCR and extraction):
```bash
cp .env.example .env
```
*(On Windows: `copy .env.example .env`)*

### 2. Backend Setup
Install Python dependencies:
```bash
pip install -r requirements.txt
```

### 3. Frontend Setup
Install frontend dependencies:
```bash
cd frontend
npm install
cd ..
```

### 4. Running the Development Servers

#### Option A: Quick-launch scripts
- **Windows**: Double-click `run_dev.bat` or execute in terminal:
  ```cmd
  run_dev.bat
  ```
- **macOS / Linux**:
  ```bash
  chmod +x run_dev.sh
  ./run_dev.sh
  ```

#### Option B: Separate terminals

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

Run all unit and integration tests:
```bash
python -m pytest tests/ -v
```

---

## Project Structure

```
backend/
  app/
    db.py            # SQLite database with patient-scoping & append-only facts
    llm.py           # Gemini JSON extraction with Pydantic validation & retry
    main.py          # FastAPI application & REST endpoints
    schema.py        # Shared clinical contract (v0.2.1)
    ingest/          # PDF, DOCX, TXT & Gemini vision OCR parsers
    extract/         # Extraction prompts & quote verification
    normalize/       # Date, unit, and drug normalizers
    flags/           # Clinical quality & safety flag rules
    timeline/        # Medication timeline derivation
    qa/              # Grounded Q&A and summary
frontend/            # React + Vite mobile-responsive UI
eval/                # Ground truth evaluation datasets
data/
  demo/              # Sample medical documents for demonstration
  uploads/           # Patient-scoped uploaded documents
```
