# ARCHITECTURE: One Patient, Many Records

## Goal
Turn a patient's pile of medical documents into a verified, dated history:
conditions, medications (start/change/stop), allergies, labs, events.
Every fact links to its source passage. Contradictions and gaps are FLAGGED, never silently resolved.
The system never diagnoses, never gives treatment advice, never invents facts.

## Pipeline
1. Upload: documents are stored under a `patient_id`.
2. Text extraction: digital PDF/DOCX via parsers; scans/images via an OCR or vision model. Output: text per page.
3. LLM extraction: text goes in, JSON facts come out (strict schema, see `backend/app/schema.py`).
4. Verify: each fact's `quote` must appear in the source page text. If not, drop the fact (and log it).
5. Normalize (code, not LLM): ISO dates, unit conversion (keep original value and unit), drug name to generic.
6. Flag (rules, no ML): duplicates, contradictions, stale meds, gaps.
7. Build: medication timeline, dated history view, patient summary.
8. Q&A: retrieve facts, answer only from them, cite fact IDs, refuse if no evidence.
9. Review: a human corrects a fact via a correction record. The original is never overwritten.

## Stack
- Backend: Python 3.11, FastAPI, Pydantic v2
- DB: SQLite (via SQLModel or plain sqlite3). Swap later if needed.
- LLM: Gemini API with JSON output (change in `backend/app/llm.py` only)
- Frontend: React + Vite
- Tests: pytest

## Folder layout and OWNERS
```
backend/app/schema.py        SHARED CONTRACT (change only via PR, tell everyone)
backend/app/db.py            Person A
backend/app/llm.py           Person A
backend/app/ingest/          Person A  (parse, OCR, page text)
backend/app/extract/         Person A  (prompts, extraction, quote verify)
backend/app/normalize/       Person B  (dates, units, drug names)
backend/app/flags/           Person B  (duplicate, contradiction, stale, gap)
backend/app/timeline/        Person B  (medication events, current list)
backend/app/qa/              Person C  (retrieval, grounded answer, summary)
backend/app/main.py          Person C  (API routes, auth/patient scoping)
frontend/                    Person C
eval/                        Person B  (ground truth, precision/recall, timing)
data/demo/                   ALL (5 patients x 5+ docs, planted errors)
```

## Data model (summary; full version in schema.py)
Fact: `id, patient_id, type, name, value (float|str|None), unit, original_value, original_unit, dose, frequency, status, date, date_precision, negation, rejected, source{doc_id,page,quote}, confidence`
- type: condition | medication | allergy | lab_result | procedure | event
- status (meds): started | changed | stopped | current | unknown
- date_precision: full | month | year | unknown  (full = YYYY-MM-DD; month = YYYY-MM; year = YYYY only; unknown = no date)
- negation: true ONLY if the document explicitly says "no X". Absence is absence (not documented).
- rejected: False by default; set to True by apply_correction() when a reviewer declares the fact is wrong. NEVER set by extraction.
- Flags link to facts via Flag.fact_ids — Fact does NOT carry a flags list.
Correction: `id, fact_id, corrected_by, new_fields, reason, rejected (bool), timestamp`. Effective fact = apply_correction(original, correction). If correction.rejected=True, effective fact gets rejected=True (fact declared WRONG). Original always kept.
Flag: `id, patient_id, kind, severity, fact_ids[], message`
- kind: duplicate | contradiction | stale_medication | missing_date | missing_unit | unit_mismatch
Patient: `id, name, created_at`
Document: `id, patient_id, filename, doc_type (lab_report|prescription|discharge_summary|other), uploaded_at, page_count`

**active_facts() rule**: timeline, flags, Q&A and summary MUST call active_facts() to filter out rejected facts before processing. The review screen bypasses this filter — rejected facts remain visible (struck-through) so the original source evidence is never lost.

## API (contract between backend and frontend)
- POST   /patients
- POST   /patients/{pid}/documents          upload, triggers pipeline
- GET    /patients/{pid}/facts
- GET    /patients/{pid}/timeline
- GET    /patients/{pid}/flags
- GET    /patients/{pid}/summary
- POST   /patients/{pid}/ask                {question} -> {answer, fact_ids, declined}
- POST   /facts/{fid}/correct               creates a Correction
- GET    /documents/{did}/page/{n}          raw page text for source popup

## Rules the code must enforce
- Every fact has a verifiable quote. No quote match, no fact.
- Patient isolation: every query filters by `patient_id`; users only reach their own patients.
- Adding a document appends facts and re-runs flags. Earlier evidence is never deleted.
- Units, doses, dates are preserved exactly in `original_*` fields.
- Q&A and summary use only stored facts. Every sentence cites fact IDs; invalid IDs are dropped.
- Declines: diagnosis, treatment advice, anything without evidence.

## Flag logic
- Duplicate: same patient, type, normalized name, date (and dose for meds). Merge display, keep all sources.
- Contradiction: allergy present vs explicit "no known allergies"; same drug, same date, different dose; drug stopped then shown current later without a restart.
- Stale: medication with no mention for more than N years (config, default 2). Show "last seen YYYY".
- Gap: medication without start date, lab without unit, fact with only year precision.

## Evaluation
Hand-label facts for 3 to 5 documents. Report precision and recall per fact type. Also time a person answering 5 questions from raw docs vs the tool.
