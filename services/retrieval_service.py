from __future__ import annotations

from typing import Protocol

from models.document_models import DocumentChunk, EvidenceRef, RetrievalHit


class VectorIndex(Protocol):
    """Minimal vector index contract used by ingestion and retrieval layers."""

    def upsert(self, chunks: list[DocumentChunk]) -> int:
        ...


class RetrievalService:
    """Retrieves evidence chunks using LangChain BM25 or token-overlap fallback."""

    def __init__(self, *, chunks: list[DocumentChunk] | None = None) -> None:
        """Initialize retrieval state with optional preloaded chunks."""
        self._chunks = chunks or []
        self._chunk_by_id: dict[str, DocumentChunk] = {
            chunk.chunk_id: chunk for chunk in self._chunks
        }
        self._langchain_docs: list[object] = []
        self._refresh_langchain_docs()

    def add_chunks(self, chunks: list[DocumentChunk]) -> None:
        """Append chunks and refresh the LangChain document cache."""
        self._chunks.extend(chunks)
        for chunk in chunks:
            self._chunk_by_id[chunk.chunk_id] = chunk
        self._refresh_langchain_docs()

    def _refresh_langchain_docs(self) -> None:
        """Build LangChain `Document` objects if the dependency is available."""
        self._langchain_docs = []
        try:
            from langchain_core.documents import Document as LangChainDocument  # type: ignore
        except Exception:
            return

        for chunk in self._chunks:
            self._langchain_docs.append(
                LangChainDocument(
                    page_content=chunk.text,
                    metadata={
                        "source_id": chunk.source_id,
                        "filename": chunk.filename,
                        "page": chunk.page,
                        "chunk_id": chunk.chunk_id,
                    },
                )
            )

    def _retrieve_with_langchain(self, query_text: str, top_k: int) -> list[RetrievalHit]:
        """Retrieve ranked hits via BM25 when LangChain components are installed."""
        if not self._langchain_docs:
            return []
        try:
            from langchain_community.retrievers import BM25Retriever  # type: ignore
        except Exception:
            return []

        try:
            retriever = BM25Retriever.from_documents(self._langchain_docs)
            retriever.k = top_k
            ranked_docs = retriever.get_relevant_documents(query_text)
        except Exception:
            return []

        hits: list[RetrievalHit] = []
        for rank, doc in enumerate(ranked_docs):
            metadata = getattr(doc, "metadata", {}) or {}
            chunk_id = str(metadata.get("chunk_id", "")).strip()
            chunk = self._chunk_by_id.get(chunk_id)
            if chunk is None:
                continue
            confidence = max(0.0, 1.0 - (rank * 0.1))
            evidence_ref = EvidenceRef(
                source_id=chunk.source_id,
                filename=chunk.filename,
                page=chunk.page,
                chunk_id=chunk.chunk_id,
                excerpt=chunk.text[:240],
            )
            hits.append(
                RetrievalHit(
                    source_id=chunk.source_id,
                    filename=chunk.filename,
                    page=chunk.page,
                    chunk_id=chunk.chunk_id,
                    text=chunk.text,
                    metadata=chunk.metadata,
                    confidence=confidence,
                    evidence_ref=evidence_ref,
                )
            )
        return hits

    def retrieve(self, query_text: str, *, top_k: int = 5) -> list[RetrievalHit]:
        """Return top-k grounded hits, preferring LangChain over lexical fallback."""
        query_tokens = {token.lower() for token in query_text.split() if token.strip()}
        if not query_tokens:
            return []

        langchain_hits = self._retrieve_with_langchain(query_text, top_k)
        if langchain_hits:
            return langchain_hits[:top_k]

        scored: list[tuple[float, DocumentChunk]] = []
        for chunk in self._chunks:
            chunk_tokens = {token.lower() for token in chunk.text.split() if token.strip()}
            overlap = len(query_tokens & chunk_tokens)
            if overlap == 0:
                continue
            confidence = overlap / max(1, len(query_tokens))
            scored.append((confidence, chunk))

        scored.sort(key=lambda item: item[0], reverse=True)
        hits: list[RetrievalHit] = []
        for confidence, chunk in scored[:top_k]:
            evidence_ref = EvidenceRef(
                source_id=chunk.source_id,
                filename=chunk.filename,
                page=chunk.page,
                chunk_id=chunk.chunk_id,
                excerpt=chunk.text[:240],
            )
            hits.append(
                RetrievalHit(
                    source_id=chunk.source_id,
                    filename=chunk.filename,
                    page=chunk.page,
                    chunk_id=chunk.chunk_id,
                    text=chunk.text,
                    metadata=chunk.metadata,
                    confidence=confidence,
                    evidence_ref=evidence_ref,
                )
            )
        return hits
