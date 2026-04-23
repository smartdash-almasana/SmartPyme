import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from models.document_models import DocumentAnswer, DocumentChunk, DocumentQuery, SourceDocument


def test_document_models_smoke() -> None:
    """Verify model constructors expose required IDs and configured defaults."""
    source = SourceDocument(filename="a.pdf", text="texto base")
    chunk = DocumentChunk(source_id=source.source_id, filename=source.filename, text="trozo")
    query = DocumentQuery(query_text="proveedor x", min_confidence=0.3)
    answer = DocumentAnswer(
        query_id=query.query_id,
        answer_text="ok",
        citations=[],
        evidence_refs=[],
    )

    assert source.source_id
    assert chunk.chunk_id
    assert query.query_id
    assert query.min_confidence == 0.3
    assert answer.answer_id
