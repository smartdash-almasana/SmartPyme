from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


def _new_id(prefix: str) -> str:
    """Build a stable prefixed identifier for domain entities."""
    return f"{prefix}_{uuid4().hex}"


class SourceDocument(BaseModel):
    """Canonical representation of a parsed source document."""

    source_id: str = Field(default_factory=lambda: _new_id("src"))
    filename: str
    text: str
    page: int = 1
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DocumentChunk(BaseModel):
    """Atomic retrievable fragment derived from a source document."""

    chunk_id: str = Field(default_factory=lambda: _new_id("chk"))
    source_id: str
    filename: str
    page: int = 1
    text: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class EvidenceRef(BaseModel):
    """Citation pointer to the exact evidence used for an answer."""

    source_id: str
    filename: str
    page: int
    chunk_id: str
    excerpt: str


class RetrievalHit(BaseModel):
    """Retrieved candidate chunk with confidence and citation metadata."""

    source_id: str
    filename: str
    page: int
    chunk_id: str
    text: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    confidence: float = 0.0
    evidence_ref: EvidenceRef


class DocumentQuery(BaseModel):
    """Normalized user question parameters for the retrieval layer."""

    query_id: str = Field(default_factory=lambda: _new_id("qry"))
    query_text: str
    top_k: int = 5
    min_confidence: float = 0.2
    metadata: dict[str, Any] = Field(default_factory=dict)


class DocumentAnswer(BaseModel):
    """Final grounded answer enriched with evidence and control flags."""

    answer_id: str = Field(default_factory=lambda: _new_id("ans"))
    query_id: str
    answer_text: str
    confidence: float = 0.0
    citations: list[EvidenceRef] = Field(default_factory=list)
    evidence_refs: list[EvidenceRef] = Field(default_factory=list)
    insufficient_evidence: bool = False
    should_trigger_clarification: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class DocumentIngestionResult(BaseModel):
    """Operational summary produced after document ingestion and indexing."""

    ingestion_id: str = Field(default_factory=lambda: _new_id("ing"))
    parser: str
    source_count: int = 0
    chunk_count: int = 0
    indexed_vector_count: int = 0
    source_ids: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
