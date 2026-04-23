import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from models.document_models import DocumentChunk, DocumentQuery
from services.document_query_service import INSUFFICIENT_EVIDENCE_MESSAGE, DocumentQueryService
from services.retrieval_service import RetrievalService


def test_query_without_evidence_returns_insufficient_and_clarification() -> None:
    """When no hits exist, service must return clarification-oriented response."""
    retrieval = RetrievalService(chunks=[])
    service = DocumentQueryService(retrieval)

    answer = service.answer(DocumentQuery(query_text="proveedor X"))

    assert answer.answer_text == INSUFFICIENT_EVIDENCE_MESSAGE
    assert answer.insufficient_evidence is True
    assert answer.should_trigger_clarification is True
    assert answer.citations == []


def test_query_with_citations_and_evidence_refs() -> None:
    """Grounded answers must include synchronized citations and evidence_refs."""
    chunk = DocumentChunk(
        source_id="src_1",
        filename="contrato.pdf",
        page=3,
        chunk_id="chk_1",
        text="La cláusula Z define penalidades para proveedor Y.",
        metadata={"topic": "clausulas"},
    )
    retrieval = RetrievalService(chunks=[chunk])
    service = DocumentQueryService(retrieval)

    answer = service.answer(DocumentQuery(query_text="cláusula Z proveedor Y"))

    assert answer.insufficient_evidence is False
    assert len(answer.citations) == 1
    assert answer.citations[0].filename == "contrato.pdf"
    assert answer.citations[0].page == 3
    assert answer.citations[0].chunk_id == "chk_1"
    assert answer.evidence_refs == answer.citations
    assert "filename=contrato.pdf; page=3; chunk_id=chk_1" in answer.answer_text


def test_query_with_low_confidence_triggers_clarification() -> None:
    """Low aggregate confidence must block answer generation."""
    chunk = DocumentChunk(
        source_id="src_2",
        filename="manual.pdf",
        page=2,
        chunk_id="chk_2",
        text="texto corto",
        metadata={},
    )
    retrieval = RetrievalService(chunks=[chunk])
    service = DocumentQueryService(retrieval)

    answer = service.answer(DocumentQuery(query_text="texto", min_confidence=1.1))

    assert answer.answer_text == INSUFFICIENT_EVIDENCE_MESSAGE
    assert answer.insufficient_evidence is True
    assert answer.should_trigger_clarification is True
