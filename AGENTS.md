# AGENTS.md: Rules for any AI agent working in this repo

Read `ARCHITECTURE.md` and `TASKS.md` before doing anything. After every meaningful change, append an entry to `UPDATES.md`.

## Hard rules
1. Only edit files inside the folder owned by the person you are working for (see ARCHITECTURE.md). If you need a change elsewhere, write it in `UPDATES.md` under "Requests" instead.
2. `backend/app/schema.py` is the shared contract. Never change it without the user confirming. If changed, bump the version comment at the top and log it.
3. Medical safety: never generate code or prompts that diagnose, recommend treatment, or fill in facts not in the documents.
4. Never silently resolve contradictions. Flag them.
5. "Not documented" is not the same as an explicit negative. Only set `negation=true` when the text says so.
6. Never overwrite original extracted facts. Corrections are separate records.
7. Preserve units, doses and dates exactly in `original_*` fields.
8. Every query must be scoped by `patient_id`.
9. LLM output must be validated with Pydantic. On validation failure, retry once, then log and skip.
10. Keep secrets in `.env` only. Never commit API keys.

## Code style
- Python: type hints, small functions, docstrings on public functions, pytest tests for logic in normalize, flags and timeline.
- Frontend: functional React components, no UI library unless agreed.
- Small commits, one feature per branch: `feat/<area>-<short-name>`.

## Workflow
1. Pull latest. Read UPDATES.md.
2. Pick a task from TASKS.md, mark it IN PROGRESS.
3. Build, test, commit.
4. Mark task DONE in TASKS.md and add an UPDATES.md entry.
5. When unsure about the schema or medical meaning, ask the user. Do not guess.

## Definition of done
Works on demo data, has a test (for logic modules), is logged in UPDATES.md, and does not break the API contract.
