from app.contracts.bem_evidence_contract import (
    BemDocumentType,
    BemEvidenceStatus,
    BemSplitSegment,
    BemTriageResult,
    segment_to_evidence_candidate,
    triage_result_to_evidence_candidates,
)


def test_segment_to_evidence_candidate():
    segment = BemSplitSegment(
        segment_id="seg1",
        document_type=BemDocumentType.INVOICE,
        source_evidence_id="ev-bulk",
        page_start=1,
        page_end=2,
        storage_ref="storage://ev-bulk/seg1.pdf",
        confidence=0.95,
    )

    candidate = segment_to_evidence_candidate(
        cliente_id="pyme_A",
        source_evidence_id="ev-bulk",
        segment=segment,
        bem_call_id="call1",
        workflow_name="smartpyme_triage",
        workflow_version="v1",
    )

    assert candidate.cliente_id == "pyme_A"
    assert candidate.evidence_id == "ev-bulk:seg1"
    assert candidate.document_type == BemDocumentType.INVOICE
    assert candidate.status == BemEvidenceStatus.CANDIDATE
    assert candidate.source_refs == ["ev-bulk:pages:1-2:segment:seg1"]
    assert candidate.bem_call_id == "call1"


def test_triage_result_to_evidence_candidates():
    result = BemTriageResult(
        cliente_id="pyme_A",
        source_evidence_id="ev-bulk",
        bem_call_id="call1",
        workflow_name="smartpyme_triage",
        workflow_version="v1",
        segments=[
            BemSplitSegment(
                segment_id="seg1",
                document_type=BemDocumentType.INVOICE,
                source_evidence_id="ev-bulk",
            ),
            BemSplitSegment(
                segment_id="seg2",
                document_type=BemDocumentType.MELI_SETTLEMENT_REPORT,
                source_evidence_id="ev-bulk",
            ),
        ],
    )

    candidates = triage_result_to_evidence_candidates(result)

    assert len(candidates) == 2
    assert candidates[0].cliente_id == "pyme_A"
    assert candidates[1].document_type == BemDocumentType.MELI_SETTLEMENT_REPORT
    assert candidates[1].workflow_name == "smartpyme_triage"


def test_unknown_document_type_supported():
    segment = BemSplitSegment(
        segment_id="seg-unknown",
        document_type=BemDocumentType.UNKNOWN,
        source_evidence_id="ev-bulk",
    )

    candidate = segment_to_evidence_candidate("pyme_A", "ev-bulk", segment)

    assert candidate.document_type == BemDocumentType.UNKNOWN
    assert candidate.status == BemEvidenceStatus.CANDIDATE
