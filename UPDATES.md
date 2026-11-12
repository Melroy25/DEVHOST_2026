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

### 2026-11-12 18:22 | Front-End / All | FyniteCare Pixel-Accurate Landing Page Built
- What changed:
  - Scaffolded modern React + TypeScript + Vite project in `fynite-care/` with Tailwind CSS and Google Font "Plus Jakarta Sans".
  - Configured exact design tokens: Primary green `#76A63F`, hover `#648F33`, heading `#0A0A0A`, body `#2E2E2E`, muted `#6B6B6B`, page background `#EFEFEF`, section background `#F5F7EF`, badge background `#F2F6E8`, divider `#DADADA`.
  - Implemented pixel-perfect components matching the design screenshot:
    - `Navbar`: FyniteCare logo (medical cross with plant leaves), centered nav links with active 5px green dot under "Home", pill-shaped "Book a Schedule" button with white right-arrow circle and green glow, 1px divider inset 60px.
    - `Hero`:
      - Left column: "Smart Healthcare, Just for You" heart pill badge, 72px H1 ("Your Health, Our Priority"), 20px subtitle, primary/secondary pill buttons, and 4K+ social proof row with 4 overlapping patient avatars.
      - Right column: Hero image card with gradient (`#E6F6D2` to `#F6FCEC`), subtle halftone dot pattern, doctor photograph, and 3 floating glass cards with blur and staggered keyframe animations (Expert Doctors, Dr. Nusrat Rahman rating card, Your Health Companion badge).
    - `WhyChooseUs`: Partially visible bottom section with "Why Choose Us" heading, green accent underline bar, and 3 rounded feature cards with green border and circular icons.
  - Verified through automated browser agent: 0 console errors/warnings, all image assets loaded with HTTP 200, crisp floating cards with zero ghosting or background artifacts.
- Files touched:
  - `fynite-care/*`
  - `.gitignore`
  - `UPDATES.md`
- Schema or API impact: none
- Needs from others: none
- Next: Ready for review and deployment.

### 2026-11-12 18:10 | Person C / All | Demo Medical Documents Created for UI Upload Testing
- What changed:
  - Created dedicated `demo_files/` folder containing realistic clinical demo records for testing every supported format:
    1. `demo_files/1_Lab_Report_Metabolic_Panel.pdf`: Multi-page clinical lab report with comprehensive metabolic and lipid panels.
    2. `demo_files/2_Prescription_Outpatient.docx`: Word document with structured prescription orders (Metformin, Atorvastatin, Lisinopril) and allergy warnings.
    3. `demo_files/3_Clinical_Scan_Note.png`: High-resolution medical consultation scan with vital signs, assessments, and orders for live vision OCR.
    4. `demo_files/4_Discharge_Summary.txt`: Multi-page discharge summary demonstrating smart pagination (`RECORD #1`, `RECORD #2`).
  - Synced files into `data/demo/` for test fixtures.
  - Added `scripts/generate_demo_files.py` utility.
  - Verified all 4 demo files ingest cleanly with text extraction and live Gemini Vision OCR.
  - All 49 pytest tests passing.
- Files touched:
  - `demo_files/*`
  - `data/demo/*`
  - `scripts/generate_demo_files.py`
  - `backend/app/ingest/router.py`
  - `UPDATES.md`
- Schema or API impact: none
- Needs from others: none
- Next: Proceed to Phase 1 extraction tasks A4–A6.

### 2026-11-12 18:05 | Person A / All | Gemini API Key Configured & Live Ingest Tested
- What changed:
  - Configured `GEMINI_API_KEY` in `.env` (gitignored, per AGENTS.md Hard Rule #10).
  - Sanitized `.env.example` with placeholder to prevent accidental secret leak.
  - Updated default model in `backend/app/llm.py` to `gemini-3.5-flash-lite` (verified available on current Google AI Studio API).
  - Added `load_dotenv()` on startup in `backend/app/main.py` and `tests/test_ingest.py`.
  - Added sample image fixture `data/demo/sample.png` and verified full OCR pipeline end-to-end (POST `/patients/{pid}/documents` extracted verbatim text via Gemini vision).
  - All 49 pytest tests passing (0 skipped, 0 failed).
- Files touched:
  - `.env`
  - `.env.example`
  - `backend/app/llm.py`
  - `backend/app/main.py`
  - `tests/test_api.py`
  - `tests/test_ingest.py`
  - `data/demo/sample.png`
  - `UPDATES.md`
- Schema or API impact: none
- Needs from others: none
- Next: Proceed to Phase 1 extraction tasks A4–A6.

### 2026-11-12 18:00 | Person C / All | Healthcare Dashboard Theme Restyle (Theme-Only)
- What changed:
  - **Restyled Frontend Theme**:
    - Centralized all palette colors, gradients, typography scale, radii, and shadows in `:root` CSS custom properties inside `frontend/src/index.css`.
    - Implemented exact palette: canvas background `#BFE3E0`, surfaces `#FFFFFF` / `#F4FBFA`, mint tint `#E6F4F2`, vertical sidebar gradient `#2F6F68` to `#4FC9B2`, primary dark teal `#0E5E56`, primary accent teal `#14A38B`, deep teal `#0B524B`, heading `#0F3D3A`, muted body `#5E7F7B`, positive text `#1E9E74`, and status badges (Success `#D7F3E8` / `#17805E`, Warning `#FDF1D6` / `#B7791F`, Info `#DDEFF7` / `#22658C`).
    - Styled outer app frame with 14px border radius and 16px padding on outer canvas.
    - Added left vertical gradient sidebar with translucent white active pill, brand header, and pinned footer.
    - Added top header bar with pill-shaped search filter input, notification icon, backend status pill, and user avatar chip.
    - Added 4 stat cards with mint tint (#E6F4F2), 3px top accent border (#14A38B), and dark teal square icon chips displaying real application metrics (documents, pages, permissions, pipeline health).
    - Added Promo / Call-to-action card with gradient `#2E7D72` to `#3DB7A0` and light button (`#CFEDE7` at 80% opacity, `#0E5E56` text).
    - Preserved 100% of existing logic, text, routes, forms, API calls, and access controls.
    - Installed `lucide-react` for stroke width 1.75-2 line icons matching target aesthetic.
  - **Testing**:
    - Verified `npm run build` succeeds in < 1s with 0 errors.
    - Verified through automated browser agent: 0 console errors/warnings, all endpoints return HTTP 200, full interactive flows tested across patient and caretaker portals.
- Files touched:
  - `frontend/src/index.css`
  - `frontend/src/App.jsx`
  - `frontend/package.json`
  - `UPDATES.md`
- Schema or API impact: none (pure theme restyling)
- Needs from others: none
- Next: Ready for Phase 1 extraction tasks A4–A6.

### 2026-11-12 17:46 | All | Two-Portal System with Caretaker Access Control (Schema v0.3.0)
- What changed:
  - **Schema bumped to v0.3.0 (agreed)**:
    - Added `UserRole` enum (`patient`, `caretaker`) and `User` model (`id`, `name`, `role`, `created_at`).
    - Added `CaretakerPermission` enum (`view`, `contribute`) and `CaretakerLink` model (`id`, `patient_id`, `caretaker_user_id`, `permission`, `created_at`, `revoked_at`).
    - Added `owner_user_id` to `Patient`, `uploaded_by` to `Document`, and set `Correction.corrected_by` to user UUID.
    - Updated `ARCHITECTURE.md` data model and access control sections.
  - **Auth & Access Control (`backend/app/auth.py`)**:
    - Centralized `get_current_user` dependency reading `X-User-Id` request header.
    - `can_access(user, patient_id, need)` enforcing:
      - Patient owner: read, write, manage
      - Caretaker (view): read only
      - Caretaker (contribute): read, write (no manage)
      - Revoked / Stranger: 403 Forbidden
    - Seeded demo users on startup: Jhon (patient), Maria (caretaker), Sam (caretaker), and Jhon's patient record.
  - **API Endpoints (`backend/app/main.py`)**:
    - `GET /users`: demo user list for login selection.
    - `GET /me`: authenticated user profile.
    - `GET /me/patients`: accessible patients with granted permissions.
    - `GET/POST/PATCH/DELETE /patients/{pid}/caretakers`: caretaker management (owner only; DELETE performs soft revocation via `revoked_at`).
    - Scoped existing document and patient routes with `can_access` and recorded `uploaded_by`.
  - **Smart Pagination & Offline Safety (`backend/app/ingest/`)**:
    - `.txt` pagination splits on form feeds, `RECORD #` markers, or chunks at ~3,000 characters.
    - Digital PDF, DOCX, and TXT parse fully offline without Gemini API key; image/scan upload returns clear error when key is absent.
    - Transactional upload ensures failed parsing leaves zero orphan DB rows.
  - **Frontend Two-Portal Experience (`frontend/`)**:
    - Demo user login switcher persisting `X-User-Id`.
    - Patient portal (`/patient`) with Document Upload, Document Viewer, Caretaker management tab (grant/modify/revoke access).
    - Caretaker portal (`/caretaker`) with "My Patients" directory, permission badges, and empty-state messaging.
    - Shared `PatientRecordView` component with permission-driven UI controls (hiding uploads for view-only, hiding caretaker tab for caretakers).
    - Placeholder cards for Facts/Timeline, Flags, Q&A, and Summary clearly labeled "Coming soon" with zero fake clinical data.
  - **Testing**:
    - Added `tests/test_access.py` covering owner, view caretaker, contribute caretaker, revoked caretaker, stranger, and 404/403 branches.
    - Updated `tests/test_api.py` covering full multi-user caretaker lifecycle.
    - 48 passed, 1 skipped (offline OCR), 0 failed.
- Files touched:
  - `backend/app/schema.py`
  - `backend/app/db.py`
  - `backend/app/auth.py`
  - `backend/app/main.py`
  - `backend/app/ingest/parsers.py`
  - `backend/app/ingest/router.py`
  - `tests/test_access.py`
  - `tests/test_api.py`
  - `tests/test_db.py`
  - `frontend/src/api.js`
  - `frontend/src/App.jsx`
  - `frontend/src/index.css`
  - `ARCHITECTURE.md`
  - `README.md`
  - `TASKS.md`
  - `UPDATES.md`
- Schema or API impact: Schema v0.3.0 agreed and enforced across all routes.
- Needs from others: none
- Next: Phase 1 extraction tasks A4–A6.

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
