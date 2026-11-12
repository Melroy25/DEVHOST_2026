# UPDATES.md

Running log. Newest entry on top. Every person and every agent adds an entry after each meaningful change.

## Entry template
```
### YYYY-MM-DD HH:MM | Person X | task id
- What changed:
- Files touched:
- Schema or API impact: none / describe
- Needs from others: none / describe
- Next:
```

## Requests (cross-folder asks; the owner picks these up)
- (none yet)

## Decisions
- LLM: Gemini API with JSON output
- DB: SQLite
- Retrieval: keyword plus type filter, no vector DB
- Flags: rule-based, no model training

## Log

### 2026-11-12 17:35 | Person C / All | Push to GitHub Repository
- What changed:
  - Added `.gitignore` protecting secrets (`.env`), SQLite databases (`data/records.db*`), uploaded files (`data/uploads/`), test caches, and `node_modules/`.
  - Initialized git repository on branch `main` and set remote origin to `https://github.com/Melroy25/DEVHOST_2026.git`.
  - Created initial commit and pushed branch `main` to `origin/main`.
- Files touched: `.gitignore`, `UPDATES.md`
- Schema or API impact: none
- Needs from others: none
- Next: Person A / B / C next phase tasks

### 2026-11-12 17:30 | Person C / All | Minimal Runnable Demo (C1 & C5)
- What changed:
  - **Backend (`backend/app/main.py`)**:
    - Added CORS middleware for `http://localhost:5173` and `http://127.0.0.1:5173`.
    - Implemented `POST /patients` (creates patient record) and `GET /patients` (list patients).
    - Implemented `GET /patients/{pid}` (retrieve patient).
    - Implemented `POST /patients/{pid}/documents`: handles multipart uploads (PDF, DOCX, TXT, images), saves file to disk scoped to patient, runs text ingest, creates document record and persists each page text to SQLite.
    - Implemented `GET /patients/{pid}/documents`: lists all documents for patient.
    - Implemented `GET /documents/{did}/page/{n}` and `GET /documents/{did}/pages`: returns extracted raw page text, scoped by patient.
    - Preserved `/health` liveness probe.
    - Automated API test suite in `tests/test_api.py` (all tests passing).
  - **Frontend (`frontend/`)**:
    - Clean, responsive React + Vite interface with custom dark medical dashboard theme.
    - API client (`src/api.js`) reading `VITE_API_URL` (default `http://localhost:8000`).
    - Live health/backend status pill.
    - Patient directory with registration form and list of registered patients.
    - Patient detail page with document upload (PDF, DOCX, TXT, image + category selector).
    - Document list with category badges and page counts.
    - In-browser document viewer with pagination and extracted text display.
    - Visible placeholders for Medication Timeline, Clinical Facts & Quotes, Quality/Safety Flags, and Grounded Q&A.
  - **Scripts & Docs**:
    - `run_dev.bat` (Windows) and `run_dev.sh` (POSIX) dev server runners.
    - `README.md` with complete "How to run" instructions.
  - **Verification**:
    - Both backend (port 8000) and frontend (port 5173) started and verified live.
    - End-to-end demo flow tested with `data/demo/sample.pdf` and `sample.txt`.
- Files touched:
  - `backend/app/main.py`
  - `tests/test_api.py`
  - `frontend/src/api.js`
  - `frontend/src/App.jsx`
  - `frontend/src/index.css`
  - `frontend/vite.config.js`
  - `run_dev.bat`
  - `run_dev.sh`
  - `README.md`
  - `TASKS.md`
  - `UPDATES.md`
- Schema or API impact: API routes implemented as specified in ARCHITECTURE.md
- Needs from others: none
- Next: A4 (`extract/prompt.py`), A5 (`extract/run.py`), A6 (`extract/verify.py`) to connect LLM fact extraction and quote verification to the upload pipeline.

### 2026-11-12 17:25 | Person A | Tasks A1–A3
- What changed:
  - **A1 (`backend/app/db.py`)**: SQLite storage with WAL mode, foreign keys, tables for patients, documents, pages, facts, corrections, flags. Every query enforces `patient_id` scoping. Facts are strictly append-only (no update queries). Corrections stored as separate audit rows. Includes CRUD helper functions and unit tests (`tests/test_db.py`).
  - **A2 (`backend/app/llm.py`)**: `call_llm_json(prompt, pydantic_model)` with Gemini JSON schema extraction, Pydantic v2 validation, single retry on failure with logging, and `call_llm_text()`. Unit tests with mock responses in `tests/test_llm.py`.
  - **A3 (`backend/app/ingest/`)**: PDF text extraction per page (`parsers.py` using `pypdf`), DOCX parser (`python-docx`), plain-text reader, image/scan OCR via Gemini vision (`ocr.py`), and unified dispatcher (`router.py`) with automatic OCR fallback for blank PDF pages. Unit tests with fixture files in `tests/test_ingest.py`.
  - Added test fixtures in `data/demo/`: `sample.txt`, `sample.pdf`, `sample.docx`.
  - All 37 pytest tests pass.
- Files touched:
  - `backend/app/db.py`
  - `backend/app/llm.py`
  - `backend/app/ingest/parsers.py`
  - `backend/app/ingest/ocr.py`
  - `backend/app/ingest/router.py`
  - `tests/test_db.py`
  - `tests/test_ingest.py`
  - `tests/test_llm.py`
  - `data/demo/sample.txt`, `sample.pdf`, `sample.docx`
  - `TASKS.md`
  - `UPDATES.md`
- Schema or API impact: none (uses existing agreed `schema.py` v0.2.1 contract)
- Needs from others: none
- Next: A4 (`extract/prompt.py`) & A5 (`extract/run.py`), or Person B / C tasks

### 2026-11-12 17:12 | Agent | Phase 0 — schema v0.2.1 AGREED
- What changed:
  - **schema.py bumped to v0.2.1** — all changes agreed by user
  - Added `Fact.rejected: bool = False` — effective-state only flag; NEVER set by extraction code
  - Fixed `apply_correction()` semantics: `correction.rejected=True` now returns a copy of the fact with `rejected=True` (the extracted fact is declared WRONG); it no longer short-circuits and returns the original unchanged
  - Added `rejected` to `_IMMUTABLE_FACT_FIELDS` so it cannot appear in `new_fields` — only `apply_correction()` may set it
  - Added `active_facts(facts) -> list[Fact]` helper: filters out facts where `rejected=True`; timeline, flags, Q&A and summary MUST use this; review screen bypasses it so rejected facts remain visible (struck-through)
  - Updated `Correction` docstring to clarify `rejected=True` means the fact is wrong, not that the correction is ignored
  - Updated `ARCHITECTURE.md`: added `rejected` to Fact summary line, documented `active_facts()` rule for all clinical output modules
  - Smoke test updated: 8 checks all pass
- Files touched: `backend/app/schema.py`, `ARCHITECTURE.md`, `UPDATES.md`
- Schema or API impact: **schema.py v0.2.1 — AGREED. Build contract in effect.**
- Needs from others: none
- Next: Person A → A1 (db.py); Person B → B1 (normalize/dates.py); Person C → C1 (main.py routes)

### 2026-11-12 16:00 | Agent | Phase 0 — schema v0.2.0 AGREED
- What changed:
  - **schema.py bumped to v0.2.0** — all changes agreed by user
  - Removed `Fact.flags` — flag linkage is one-directional via `Flag.fact_ids` only
  - Added `Correction.rejected: bool = False` — rejected corrections are excluded from effective-fact computation
  - Added `Patient` model: `id, name, created_at`
  - Added `Document` model: `id, patient_id, filename, doc_type (DocType enum), uploaded_at, page_count`
  - Added `DocType` enum: `lab_report | prescription | discharge_summary | other`
  - Changed `Fact.value` type from `str | None` to `float | str | None` (numeric lab results use float)
  - Added `apply_correction(fact, correction) -> Fact` helper: returns effective fact, never mutates original, rejects unknown/immutable keys with `ValueError`, is a no-op when `correction.rejected` is True
  - Defined `_IMMUTABLE_FACT_FIELDS` (id, patient_id, source, original_value, original_unit, created_at) and `_MUTABLE_FACT_FIELDS` constants
  - Updated `ARCHITECTURE.md` data model section: added `date_precision` values, `Patient`, `Document`, flag linkage note, `Correction.rejected`, `value (float|str|None)`
- Files touched: `backend/app/schema.py`, `ARCHITECTURE.md`, `UPDATES.md`
- Schema or API impact: **schema.py v0.2.0 — AGREED. This is now the build contract.**
- Needs from others: none — Person A/B/C may now begin Phase 1 tasks
- Next: Person A → A1 (db.py); Person B → B1 (normalize/dates.py); Person C → C1 (main.py routes)

### 2026-11-12 15:56 | Agent | Phase 0 — scaffold
- What changed:
  - Created full folder structure: `backend/app/{ingest,extract,normalize,flags,timeline,qa}`, `frontend/`, `eval/`, `data/demo/`
  - Added `__init__.py` to every Python package
  - Created `requirements.txt` (fastapi, uvicorn, pydantic, sqlmodel, python-multipart, pypdf, python-docx, pytest, google-genai, python-dotenv)
  - Created `.env.example` with `GEMINI_API_KEY` placeholder
  - Wrote `backend/app/schema.py` v0.1.0 — Pydantic v2 models: Source, Fact, Correction, Flag; enums: FactType, MedStatus, DatePrecision, FlagKind, FlagSeverity; API helpers: FactList, FlagList, CorrectionRequest, AskRequest, AskResponse
  - Created minimal `backend/app/main.py` with `/health` route (FastAPI)
  - Scaffolded React + Vite app in `frontend/` via `npm create vite@latest`
- Files touched: `requirements.txt`, `.env.example`, `backend/app/schema.py`, `backend/app/main.py`, `frontend/*`, all `__init__.py` stubs
- Schema or API impact: **schema.py v0.1.0 introduced** — awaiting team agreement before anyone builds on it
- Needs from others: **Team must review and agree `schema.py` before Phase 1 starts (rule: nobody builds until this is done)**
- Next: team agrees schema → Person A starts A1 (db.py); Person B starts B1 (dates); Person C starts C1 (routes)

### Day 0 | Setup
- What changed: repo created, ARCHITECTURE.md, AGENTS.md, TASKS.md, UPDATES.md added
- Next: finish schema.py (Phase 0)
