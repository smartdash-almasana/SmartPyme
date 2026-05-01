import shutil
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from extraction.chunker import split_document
from models.document_models import SourceDocument
from services.document_ingestion_service import DocumentIngestionService


def test_chunking_basic_generates_chunks() -> None:
    """Ensure long text is split into multiple chunks with stable source linkage."""
    doc = SourceDocument(filename="demo.pdf", text="A" * 2000)
    chunks = split_document(doc, chunk_size=400, chunk_overlap=40)
    assert len(chunks) >= 4
    assert all(chunk.source_id == doc.source_id for chunk in chunks)


def test_ingestion_writes_evidence_outputs() -> None:
    """Validate ingestion writes expected evidence artifacts to disk."""
    root = Path(__file__).resolve().parents[1] / ".tmp" / f"doc_ingest_{uuid.uuid4().hex}"
    root.mkdir(parents=True, exist_ok=False)
    try:
        pdf = root / "sample.pdf"
        pdf.write_text("Proveedor Y tiene cláusula Z en página 1.", encoding="utf-8")

        service = DocumentIngestionService(evidence_root=root / "evidence_store")
        result = service.ingest_pdfs([pdf])

        assert result.source_count == 1
        assert result.chunk_count >= 1
        assert (root / "evidence_store" / "raw_documents" / "documents.jsonl").exists()
        assert (root / "evidence_store" / "document_chunks" / "chunks.jsonl").exists()
        assert (root / "evidence_store" / "citation_index" / "citations.json").exists()
        assert result.parser in {"docling", "ocr_fallback", "plain_text_fallback", "mixed"}
    finally:
        shutil.rmtree(root, ignore_errors=True)
