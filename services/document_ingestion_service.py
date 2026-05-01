from __future__ import annotations

import json
from pathlib import Path

from extraction.chunker import split_document
from extraction.docling_parser import parse_pdf
from models.document_models import DocumentChunk, DocumentIngestionResult, SourceDocument
from services.retrieval_service import RetrievalService, VectorIndex


class DocumentIngestionService:
    """Orchestrates parsing, chunking, persistence, and optional vector indexing."""

    def __init__(
        self,
        *,
        evidence_root: Path = Path("evidence_store"),
        retrieval_service: RetrievalService | None = None,
        vector_index: VectorIndex | None = None,
    ) -> None:
        """Create an ingestion service bound to a local evidence store."""
        self._evidence_root = evidence_root
        self._retrieval = retrieval_service or RetrievalService()
        self._vector_index = vector_index

    def ingest_pdfs(self, pdf_paths: list[Path]) -> DocumentIngestionResult:
        """Ingest PDFs and return an operational summary with parser provenance."""
        self._ensure_evidence_dirs()
        documents: list[SourceDocument] = []
        chunks: list[DocumentChunk] = []
        errors: list[str] = []

        for pdf_path in pdf_paths:
            try:
                document = parse_pdf(pdf_path)
                # Preserve original path for downstream tracing and audits.
                document.metadata["source_path"] = str(pdf_path)
                documents.append(document)
                chunks.extend(split_document(document))
            except Exception as exc:
                errors.append(f"{pdf_path}: {exc}")

        self._retrieval.add_chunks(chunks)
        self._write_jsonl(self._evidence_root / "raw_documents" / "documents.jsonl", documents)
        self._write_jsonl(self._evidence_root / "document_chunks" / "chunks.jsonl", chunks)
        self._write_citation_index(chunks)

        indexed = 0
        if self._vector_index is not None:
            try:
                indexed = int(self._vector_index.upsert(chunks))
            except Exception as exc:
                errors.append(f"vector_index: {exc}")

        parser_names = {
            str(document.metadata.get("parser_used", "unknown"))
            for document in documents
        }
        parser_name = (
            "mixed"
            if len(parser_names) > 1
            else (next(iter(parser_names)) if parser_names else "unknown")
        )
        return DocumentIngestionResult(
            parser=str(parser_name),
            source_count=len(documents),
            chunk_count=len(chunks),
            indexed_vector_count=indexed,
            source_ids=[document.source_id for document in documents],
            errors=errors,
        )

    def _ensure_evidence_dirs(self) -> None:
        """Ensure on-disk folders exist for all ingestion artifacts."""
        for rel in ("raw_documents", "document_chunks", "citation_index", "vector_index"):
            (self._evidence_root / rel).mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _write_jsonl(path: Path, rows: list[SourceDocument] | list[DocumentChunk]) -> None:
        """Write typed model rows as JSONL in UTF-8."""
        with path.open("w", encoding="utf-8") as handle:
            for row in rows:
                handle.write(json.dumps(row.model_dump(mode="json"), ensure_ascii=False) + "\n")

    def _write_citation_index(self, chunks: list[DocumentChunk]) -> None:
        """Persist lightweight citation entries for quick evidence lookup."""
        citation_rows = [
            {
                "source_id": chunk.source_id,
                "filename": chunk.filename,
                "page": chunk.page,
                "chunk_id": chunk.chunk_id,
                "excerpt": chunk.text[:240],
            }
            for chunk in chunks
        ]
        with (
            self._evidence_root / "citation_index" / "citations.json"
        ).open("w", encoding="utf-8") as handle:
            handle.write(json.dumps(citation_rows, ensure_ascii=False, indent=2))
