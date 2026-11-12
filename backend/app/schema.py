# schema.py — SHARED CONTRACT v0.2.1
# Change only after team agreement. Bump version and log in UPDATES.md.
#
# Version history:
#   v0.1.0  2026-11-12  Initial schema (Phase 0, all)
#   v0.2.0  2026-11-12  AGREED — see UPDATES.md for change list
#   v0.2.1  2026-11-12  AGREED — Fact.rejected; apply_correction semantics fix; active_facts()

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class FactType(str, Enum):
    """The clinical category of a fact."""

    condition = "condition"
    medication = "medication"
    allergy = "allergy"
    lab_result = "lab_result"
    procedure = "procedure"
    event = "event"


class MedStatus(str, Enum):
    """Lifecycle status — only meaningful when fact_type is medication."""

    started = "started"
    changed = "changed"
    stopped = "stopped"
    current = "current"
    unknown = "unknown"


class DatePrecision(str, Enum):
    """How precise the extracted date is.

    full    — YYYY-MM-DD known
    month   — YYYY-MM known
    year    — only YYYY known
    unknown — no date at all
    """

    full = "full"
    month = "month"
    year = "year"
    unknown = "unknown"


class FlagKind(str, Enum):
    """Category of a clinical-quality flag."""

    duplicate = "duplicate"
    contradiction = "contradiction"
    stale_medication = "stale_medication"
    missing_date = "missing_date"
    missing_unit = "missing_unit"
    unit_mismatch = "unit_mismatch"


class FlagSeverity(str, Enum):
    """How urgently a flag needs human review."""

    info = "info"
    warning = "warning"
    critical = "critical"


class DocType(str, Enum):
    """Broad category of an uploaded medical document."""

    lab_report = "lab_report"
    prescription = "prescription"
    discharge_summary = "discharge_summary"
    other = "other"


# ---------------------------------------------------------------------------
# Sub-models
# ---------------------------------------------------------------------------


class Source(BaseModel):
    """Pointer to the exact passage that supports a fact.

    The ``quote`` field must be a verbatim substring of the page text.
    If the quote cannot be found in the page text the fact must be dropped.
    """

    doc_id: UUID = Field(..., description="ID of the uploaded document.")
    page: int = Field(..., ge=1, description="1-based page number.")
    quote: str = Field(
        ...,
        min_length=1,
        description="Verbatim text excerpt from the page that supports this fact.",
    )


# ---------------------------------------------------------------------------
# Domain models
# ---------------------------------------------------------------------------


class Patient(BaseModel):
    """A patient whose documents are managed by the system."""

    id: UUID = Field(default_factory=uuid4)
    name: str = Field(..., min_length=1)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Document(BaseModel):
    """An uploaded medical document belonging to a patient."""

    id: UUID = Field(default_factory=uuid4)
    patient_id: UUID = Field(..., description="Patient this document belongs to.")
    filename: str = Field(..., min_length=1)
    doc_type: DocType = DocType.other
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    page_count: int = Field(..., ge=1, description="Total number of pages extracted.")


class Fact(BaseModel):
    """A single clinical fact extracted from a document page.

    Rules (enforced in code, not just comments):
    - ``quote`` must appear in the source page text; facts that fail this check
      are dropped and logged — never stored.
    - ``negation`` is True ONLY when the document explicitly says "no X".
      Absence of information must NOT be recorded as negation.
    - ``original_value`` and ``original_unit`` preserve the raw text exactly;
      ``value`` and ``unit`` hold the normalised versions.
    - Every query that reads facts must filter by ``patient_id``.
    - Flags are linked via Flag.fact_ids; facts do NOT carry a flags list.
    - ``rejected`` is NEVER set by extraction; it is only set by apply_correction()
      when a reviewer marks the extracted fact as wrong. Use active_facts() to
      exclude rejected facts from timeline, flags, Q&A and summary.
    """

    id: UUID = Field(default_factory=uuid4)
    patient_id: UUID = Field(..., description="Patient this fact belongs to.")

    # What kind of fact
    type: FactType

    # Human-readable name, e.g. "Metformin", "Type 2 Diabetes", "HbA1c"
    name: str = Field(..., min_length=1)

    # Extracted value — numeric lab results use float; everything else uses str
    value: float | str | None = None
    unit: str | None = None

    # Raw values exactly as they appear in the document
    original_value: str | None = None
    original_unit: str | None = None

    # Medication-specific
    dose: str | None = None
    frequency: str | None = None
    status: MedStatus | None = None  # only set when type == medication

    # Date of the fact (ISO 8601 string "YYYY-MM-DD", "YYYY-MM", or "YYYY")
    date: str | None = None
    date_precision: DatePrecision = DatePrecision.unknown

    # Explicit negation — see docstring
    negation: bool = False

    # Reviewer verdict — True means the extracted fact is WRONG and must be
    # excluded from all clinical outputs. Never set by extraction code.
    rejected: bool = False

    # Where this fact came from
    source: Source

    # LLM confidence in [0, 1]; None means not provided
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)

    # Audit
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # NOTE: flags are NOT stored here.
    # To find flags for this fact, query Flag where fact_ids contains this id.


class Correction(BaseModel):
    """A human reviewer's correction to a stored Fact.

    The original Fact is NEVER overwritten. The effective state of a fact is
    computed by apply_correction(original, correction):
    - correction.rejected=True  → the reviewer says the extracted fact is WRONG;
      the returned effective fact has rejected=True and is excluded from all
      clinical outputs (timeline, flags, Q&A, summary). The original evidence
      is still kept and shown struck-through on the review screen.
    - correction.rejected=False → new_fields are applied to the original fact.
    """

    id: UUID = Field(default_factory=uuid4)
    fact_id: UUID = Field(..., description="The Fact being corrected.")
    corrected_by: str = Field(..., description="Username or reviewer ID.")

    # Only the fields that changed; use the original for everything else.
    # Unknown keys (not present on Fact) are rejected by apply_correction().
    new_fields: dict[str, Any] = Field(
        ...,
        description="Partial dict of Fact fields with their corrected values.",
    )
    reason: str = Field(..., min_length=1, description="Why the correction was made.")
    rejected: bool = Field(
        default=False,
        description=(
            "True when the reviewer declares the extracted fact itself is WRONG. "
            "apply_correction() will mark the effective fact as rejected=True, "
            "excluding it from clinical outputs. The original is always kept."
        ),
    )
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    new_fields: dict[str, Any] = Field(
        ...,
        description="Partial dict of Fact fields with their corrected values.",
    )
    reason: str = Field(..., min_length=1, description="Why the correction was made.")
    rejected: bool = Field(
        default=False,
        description="True when a senior reviewer has rejected this correction. "
                    "Rejected corrections are excluded from apply_correction().",
    )
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Flag(BaseModel):
    """A data-quality or clinical-safety flag raised by the rules engine.

    Flags are raised by the flags module and stored; they are NEVER raised by
    the LLM.  Every flag must reference at least one fact.
    Fact-to-flag linkage is one-directional: Flag carries fact_ids;
    facts do NOT carry a flag list.
    """

    id: UUID = Field(default_factory=uuid4)
    patient_id: UUID = Field(..., description="Patient whose facts triggered this flag.")
    kind: FlagKind
    severity: FlagSeverity = FlagSeverity.warning

    # The facts involved (≥1 required)
    fact_ids: list[UUID] = Field(..., min_length=1)

    # Human-readable explanation
    message: str = Field(..., min_length=1)

    created_at: datetime = Field(default_factory=datetime.utcnow)


# ---------------------------------------------------------------------------
# Helpers — apply_correction, active_facts
# ---------------------------------------------------------------------------

# Fields that are immutable and must never be overwritten by a correction.
_IMMUTABLE_FACT_FIELDS: frozenset[str] = frozenset({
    "id",
    "patient_id",
    "source",
    "original_value",
    "original_unit",
    "created_at",
    "rejected",   # only apply_correction() may set this; new_fields may not
})

# Valid mutable fields (all Fact fields minus the immutable ones).
_MUTABLE_FACT_FIELDS: frozenset[str] = frozenset(Fact.model_fields.keys()) - _IMMUTABLE_FACT_FIELDS


def apply_correction(fact: Fact, correction: Correction) -> Fact:
    """Return the effective Fact after applying *correction*.

    Semantics (v0.2.1):
    - The original ``fact`` is NEVER mutated; a new Fact instance is always
      returned.
    - If ``correction.rejected`` is True the reviewer has declared the extracted
      fact is WRONG. The returned fact is a copy of the original with
      ``rejected=True``. It will be excluded from clinical outputs by
      ``active_facts()``, but the original evidence is preserved in the DB and
      shown struck-through on the review screen.
    - If ``correction.rejected`` is False, ``new_fields`` are merged onto the
      original fact's data and a corrected copy is returned (rejected=False).
    - Keys in ``new_fields`` that are not valid mutable Fact fields raise
      ``ValueError`` — unknown or immutable keys are never silently ignored.
    - ``rejected`` itself cannot appear in ``new_fields``; it is controlled
      exclusively via ``correction.rejected``.

    Args:
        fact: The stored, original Fact (never modified).
        correction: The Correction to apply.

    Returns:
        A new Fact instance representing the effective (post-correction) state.

    Raises:
        ValueError: If new_fields targets an unknown or immutable field.
    """
    if correction.rejected:
        # Mark the fact as wrong; original data unchanged except rejected flag.
        effective_data = fact.model_dump()
        effective_data["rejected"] = True
        return Fact.model_validate(effective_data)

    # Validate new_fields keys before touching anything.
    unknown_keys = set(correction.new_fields.keys()) - _MUTABLE_FACT_FIELDS
    if unknown_keys:
        raise ValueError(
            f"Correction {correction.id} targets unknown or immutable Fact "
            f"field(s): {sorted(unknown_keys)}. Allowed mutable fields: "
            f"{sorted(_MUTABLE_FACT_FIELDS)}."
        )

    # Build the effective fact without touching the original object.
    effective_data = fact.model_dump()
    effective_data.update(correction.new_fields)
    return Fact.model_validate(effective_data)


def active_facts(facts: list[Fact]) -> list[Fact]:
    """Return only the facts that have not been rejected by a reviewer.

    Timeline, flags, Q&A, and summary MUST call this before processing.
    The review screen bypasses this filter so rejected facts are still visible
    (struck-through) and the original source evidence is never lost.

    Args:
        facts: Mixed list of effective (post-correction) Fact objects.

    Returns:
        A new list containing only facts where ``rejected`` is False.
    """
    return [f for f in facts if not f.rejected]


# ---------------------------------------------------------------------------
# API request / response helpers (thin wrappers; not stored in DB)
# ---------------------------------------------------------------------------


class FactList(BaseModel):
    """Paginated list of facts for a patient."""

    patient_id: UUID
    total: int
    facts: list[Fact]


class FlagList(BaseModel):
    """All flags for a patient."""

    patient_id: UUID
    flags: list[Flag]


class CorrectionRequest(BaseModel):
    """Body for POST /facts/{fid}/correct."""

    corrected_by: str
    new_fields: dict[str, Any]
    reason: str


class AskRequest(BaseModel):
    """Body for POST /patients/{pid}/ask."""

    question: str = Field(..., min_length=1)


class AskResponse(BaseModel):
    """Answer from the Q&A module."""

    answer: str
    fact_ids: list[UUID]  # facts cited
    declined: bool = False  # True when the system refuses to answer
