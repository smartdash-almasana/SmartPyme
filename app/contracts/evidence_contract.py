from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


EvidenceContractStatus = Literal["implemented", "partial", "pending"]


@dataclass(frozen=True, slots=True)
class RawDocument:
    raw_document_id: str
    job_id: str | None
    plan_id: str | None
    file_path: str
    filename: str
    file_hash_sha256: str
    size_bytes: int | None = None
    mime_type: str | None = None
    source_id: str | None = None
    created_at: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class DocumentRecord:
    document_id: str
    raw_document_id: str
    job_id: str | None
    plan_id: str | None
    filename: str
    parser: str
    text_hash: str
    page_count: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class EvidenceChunk:
    evidence_id: str
    document_id: str
    raw_document_id: str | None
    job_id: str | None
    plan_id: str | None
    filename: str
    page: int
    text: str
    chunk_order: int
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class RetrievalResult:
    query_id: str
    evidence_id: str
    document_id: str | None
    job_id: str | None
    plan_id: str | None
    score: float
    text: str
    citation: dict[str, Any]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ExtractedFactCandidate:
    fact_candidate_id: str
    evidence_id: str
    job_id: str | None
    plan_id: str | None
    schema_name: str
    data: dict[str, Any]
    confidence: float
    extraction_method: str
    validation_status: str = "pending_validation"
    errors: list[str] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class CanonicalRowCandidate:
    canonical_row_id: str
    fact_candidate_id: str
    evidence_id: str
    job_id: str | None
    plan_id: str | None
    entity_type: str
    row: dict[str, Any]
    validation_status: str = "pending_validation"
    errors: list[str] = field(default_factory=list)
