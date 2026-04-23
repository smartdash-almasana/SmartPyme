from __future__ import annotations

from models.document_models import DocumentAnswer, DocumentQuery, EvidenceRef
from services.retrieval_service import RetrievalService

INSUFFICIENT_EVIDENCE_MESSAGE = "No tengo evidencia documental suficiente para responder con certeza."


class DocumentQueryService:
    """Builds grounded answers constrained to retrieved documentary evidence."""

    def __init__(self, retrieval_service: RetrievalService) -> None:
        """Bind the service to a retrieval backend."""
        self._retrieval = retrieval_service

    def answer(self, query: DocumentQuery) -> DocumentAnswer:
        """Answer a query only when retrieval confidence passes the threshold."""
        hits = self._retrieval.retrieve(query.query_text, top_k=query.top_k)
        if not hits:
            return DocumentAnswer(
                query_id=query.query_id,
                answer_text=INSUFFICIENT_EVIDENCE_MESSAGE,
                confidence=0.0,
                citations=[],
                evidence_refs=[],
                insufficient_evidence=True,
                should_trigger_clarification=True,
            )

        confidence = sum(hit.confidence for hit in hits) / max(1, len(hits))
        if confidence < query.min_confidence:
            return DocumentAnswer(
                query_id=query.query_id,
                answer_text=INSUFFICIENT_EVIDENCE_MESSAGE,
                confidence=confidence,
                citations=[],
                evidence_refs=[],
                insufficient_evidence=True,
                should_trigger_clarification=True,
            )

        refs: list[EvidenceRef] = [hit.evidence_ref for hit in hits]
        lines: list[str] = []
        for idx, hit in enumerate(hits, start=1):
            # Keep answer text explicitly traceable to filename/page/chunk_id.
            excerpt = " ".join(hit.text.split())[:280].strip()
            citation = f"filename={hit.filename}; page={hit.page}; chunk_id={hit.chunk_id}"
            lines.append(f"{idx}. {excerpt} [{citation}]")

        return DocumentAnswer(
            query_id=query.query_id,
            answer_text="\n".join(lines),
            confidence=confidence,
            citations=refs,
            evidence_refs=refs,
            insufficient_evidence=False,
            should_trigger_clarification=False,
            metadata={"policy": "grounded_only"},
        )
