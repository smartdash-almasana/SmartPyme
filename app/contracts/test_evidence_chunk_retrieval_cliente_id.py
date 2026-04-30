import pytest
from app.contracts.evidence_contract import EvidenceChunk, RetrievalResult


def test_evidence_chunk_requires_cliente_id():
    with pytest.raises(ValueError, match="cliente_id is required"):
        EvidenceChunk(
            cliente_id="",
            evidence_id="ev_001",
            document_id="doc_001",
            raw_document_id="raw_001",
            job_id="job_001",
            plan_id="plan_001",
            filename="test.pdf",
            page=1,
            text="some text",
            chunk_order=1,
        )


def test_retrieval_result_requires_cliente_id():
    with pytest.raises(ValueError, match="cliente_id is required"):
        RetrievalResult(
            cliente_id="",
            query_id="q_001",
            evidence_id="ev_001",
            document_id="doc_001",
            job_id="job_001",
            plan_id="plan_001",
            score=0.9,
            text="some text",
            citation={},
        )

def test_valid_instantiation():
    chunk = EvidenceChunk(
        cliente_id="cliente_123",
        evidence_id="ev_001",
        document_id="doc_001",
        raw_document_id="raw_001",
        job_id="job_001",
        plan_id="plan_001",
        filename="test.pdf",
        page=1,
        text="some text",
        chunk_order=1,
    )
    assert chunk.cliente_id == "cliente_123"

    result = RetrievalResult(
        cliente_id="cliente_123",
        query_id="q_001",
        evidence_id="ev_001",
        document_id="doc_001",
        job_id="job_001",
        plan_id="plan_001",
        score=0.9,
        text="some text",
        citation={},
    )
    assert result.cliente_id == "cliente_123"
