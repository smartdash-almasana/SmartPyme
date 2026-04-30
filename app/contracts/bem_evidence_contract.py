from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class BemEvidenceStatus(str, Enum):
    CANDIDATE = "CANDIDATE"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    PENDING_REVIEW = "PENDING_REVIEW"


class BemDocumentType(str, Enum):
    INVOICE = "invoice"
    RECEIPT = "receipt"
    MELI_SALES_REPORT = "meli_sales_report"
    MELI_SETTLEMENT_REPORT = "meli_settlement_report"
    BANK_STATEMENT = "bank_statement"
    TAX_DOCUMENT = "tax_document"
    CATALOG_OR_PRICE_LIST = "catalog_or_price_list"
    UNKNOWN = "unknown"


class BemSplitSegment(BaseModel):
    segment_id: str
    document_type: BemDocumentType
    source_evidence_id: str
    page_start: int | None = None
    page_end: int | None = None
    storage_ref: str | None = None
    confidence: float | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class BemEvidenceCandidate(BaseModel):
    cliente_id: str
    evidence_id: str
    source_evidence_id: str
    segment_id: str
    document_type: BemDocumentType
    status: BemEvidenceStatus = BemEvidenceStatus.CANDIDATE
    storage_ref: str | None = None
    source_refs: list[str] = Field(default_factory=list)
    confidence: float | None = None
    bem_call_id: str | None = None
    workflow_name: str | None = None
    workflow_version: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class BemTriageResult(BaseModel):
    cliente_id: str
    source_evidence_id: str
    bem_call_id: str | None = None
    workflow_name: str
    workflow_version: str | None = None
    segments: list[BemSplitSegment]
    metadata: dict[str, Any] = Field(default_factory=dict)


def segment_to_evidence_candidate(
    cliente_id: str,
    source_evidence_id: str,
    segment: BemSplitSegment,
    bem_call_id: str | None = None,
    workflow_name: str | None = None,
    workflow_version: str | None = None,
) -> BemEvidenceCandidate:
    evidence_id = f"{source_evidence_id}:{segment.segment_id}"
    source_ref = _build_source_ref(source_evidence_id, segment)

    return BemEvidenceCandidate(
        cliente_id=cliente_id,
        evidence_id=evidence_id,
        source_evidence_id=source_evidence_id,
        segment_id=segment.segment_id,
        document_type=segment.document_type,
        storage_ref=segment.storage_ref,
        source_refs=[source_ref],
        confidence=segment.confidence,
        bem_call_id=bem_call_id,
        workflow_name=workflow_name,
        workflow_version=workflow_version,
        metadata=segment.metadata,
    )


def triage_result_to_evidence_candidates(result: BemTriageResult) -> list[BemEvidenceCandidate]:
    return [
        segment_to_evidence_candidate(
            cliente_id=result.cliente_id,
            source_evidence_id=result.source_evidence_id,
            segment=segment,
            bem_call_id=result.bem_call_id,
            workflow_name=result.workflow_name,
            workflow_version=result.workflow_version,
        )
        for segment in result.segments
    ]


def _build_source_ref(source_evidence_id: str, segment: BemSplitSegment) -> str:
    if segment.page_start is not None and segment.page_end is not None:
        return f"{source_evidence_id}:pages:{segment.page_start}-{segment.page_end}:segment:{segment.segment_id}"
    return f"{source_evidence_id}:segment:{segment.segment_id}"
