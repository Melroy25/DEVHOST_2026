# TASKS.md

Status: TODO | IN PROGRESS | DONE. Update when you start or finish.
Rename Person A/B/C to your names.

## Phase 0: Together (first hour)
- [x] Create repo, folders, `.env.example`, `requirements.txt`  ← DONE (agent, 2026-11-12)
- [x] Write and agree `backend/app/schema.py` (Fact, Correction, Flag, Source). **Nobody builds until this is done.**  ← v0.2.0 AGREED (2026-11-12)
- [ ] Agree the API list in ARCHITECTURE.md
- [ ] Decide the demo cast of 5 patients (see Phase 5)

## Person A: Extraction (ingest, extract, db, llm)
- [x] A1 `db.py`: tables for patients, documents, pages, facts, corrections, flags  ← DONE (2026-11-12)
- [x] A2 `llm.py`: one function `call_llm_json(prompt, schema)` with retry  ← DONE (2026-11-12)
- [x] A3 `ingest/`: PDF text parser, DOCX parser, image/scan OCR; output list of (page_no, text)  ← DONE (2026-11-12)
- [ ] A4 `extract/prompt.py`: extraction prompt (facts only, verbatim quote, no inference, no diagnosis)
- [ ] A5 `extract/run.py`: run per page, validate with Pydantic, return facts
- [ ] A6 `extract/verify.py`: drop facts whose quote is not found in page text (fuzzy match on whitespace)
- [ ] A7 Save facts to DB; re-run safely when a new document is added (append only)

## Person B: Logic (normalize, flags, timeline, eval)
- [ ] B1 `normalize/dates.py`: many formats (DD/MM/YYYY, 12 Mar 21, "March 2021") to ISO plus `date_precision`
- [ ] B2 `normalize/units.py`: glucose, cholesterol, creatinine etc. mmol/L and mg/dL, keep original
- [ ] B3 `normalize/drugs.py`: brand to generic map (small dictionary for demo drugs)
- [ ] B4 `flags/duplicates.py`
- [ ] B5 `flags/contradictions.py`
- [ ] B6 `flags/stale_gaps.py`
- [ ] B7 `timeline/meds.py`: events per drug (start, change, stop), derive current list and "last seen"
- [ ] B8 pytest tests for B1 to B7 using demo data
- [ ] B9 `eval/`: ground truth JSON, script for precision/recall, timing sheet

## Person C: Product (api, qa, frontend)
- [x] C1 `main.py`: FastAPI routes from ARCHITECTURE.md, patient scoping, upload + ingest + page viewer  ← DONE (demo subset, 2026-11-12)
- [ ] C2 `qa/retrieve.py`: pick relevant facts for a question (keyword plus type filter, no vector DB needed)
- [ ] C3 `qa/answer.py`: grounded answer, cites fact IDs, declines when no evidence or when advice/diagnosis is asked
- [ ] C4 `qa/summary.py`: patient summary from facts only, sentence-level citations, lists flags
- [x] C5 Frontend: patient list and upload page, document viewer, layout placeholders  ← DONE (2026-11-12)
- [ ] C6 Frontend: dated timeline (conditions, meds, labs, events) with source popup (doc, page, highlighted quote)
- [ ] C7 Frontend: flags panel (contradictions, duplicates, stale, gaps) linking to facts
- [ ] C8 Frontend: Q&A box showing answer and source chips
- [ ] C9 Frontend: reviewer edit screen (edit a fact, original shown beside corrected)

## Phase 5: Everyone, demo data (`data/demo/`)
5 patients, 5+ documents each, at least 2 document types (lab report, prescription, discharge summary).
Plant these:
- [ ] A duplicate (same medication in two documents)
- [ ] An allergy contradiction (allergy in one doc, "no known allergies" in another)
- [ ] A stopped medication that still appears in an old prescription
- [ ] A unit mismatch (mmol/L in one lab, mg/dL in another)
- [ ] A missing date
- [ ] A question the records cannot answer (for the decline demo)

## Integration order
1. Schema (Phase 0)
2. A: one document, end to end into DB. B: flags working on hand-made JSON. C: UI on mock JSON.
3. Connect real extraction to flags to API to UI.
4. Q&A and summary.
5. Evaluation numbers.
6. Demo rehearsal.

## Suggested first prompt in Antigravity (for each person)
"Read AGENTS.md, ARCHITECTURE.md and TASKS.md. I am Person X. Start with task X1. Stay inside my folders, log changes in UPDATES.md."
