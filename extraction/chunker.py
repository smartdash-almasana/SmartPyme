from __future__ import annotations

from typing import Any

from models.document_models import DocumentChunk, SourceDocument


def _fallback_split_text(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    """Split text by fixed windows when LangChain splitter is unavailable."""
    if not text:
        return []
    step = max(1, chunk_size - chunk_overlap)
    parts: list[str] = []
    for start in range(0, len(text), step):
        piece = text[start : start + chunk_size].strip()
        if piece:
            parts.append(piece)
    return parts


def split_document(
    document: SourceDocument,
    *,
    chunk_size: int = 800,
    chunk_overlap: int = 120,
) -> list[DocumentChunk]:
    """Create retrievable chunks, preserving page-level provenance metadata."""

    def _split_text(text: str) -> list[str]:
        """Prefer LangChain recursive splitting and fallback to fixed windows."""
        try:
            from langchain_text_splitters import RecursiveCharacterTextSplitter  # type: ignore

            splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                separators=["\n\n", "\n", ". ", " "],
            )
            return splitter.split_text(text)
        except Exception:
            return _fallback_split_text(text, chunk_size, chunk_overlap)

    page_entries: list[dict[str, Any]] = []
    raw_pages = document.metadata.get("pages")
    if isinstance(raw_pages, list):
        for page in raw_pages:
            if not isinstance(page, dict):
                continue
            page_num = page.get("page")
            page_text = page.get("text")
            if (
                isinstance(page_num, int)
                and page_num > 0
                and isinstance(page_text, str)
                and page_text.strip()
            ):
                page_entries.append({"page": page_num, "text": page_text})

    if not page_entries:
        page_entries = [{"page": document.page, "text": document.text}]

    chunks: list[DocumentChunk] = []
    chunk_order = 0

    for page_entry in page_entries:
        texts = _split_text(page_entry["text"])
        for text in texts:
            chunk_metadata = dict(document.metadata)
            chunk_metadata["chunk_order"] = chunk_order
            chunk_metadata["page"] = page_entry["page"]
            chunks.append(
                DocumentChunk(
                    source_id=document.source_id,
                    filename=document.filename,
                    page=page_entry["page"],
                    text=text,
                    metadata=chunk_metadata,
                )
            )
            chunk_order += 1

    return chunks
