from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any


def _infer_doc_type(extension: str) -> str:
    """Infer document type from file extension."""
    ext = extension.lower()
    if ext in [".csv", ".xls", ".xlsx"]:
        return "table"
    if ext in [".html", ".htm", ".xml"]:
        return "markup"
    if ext in [".txt", ".md", ".rtf"]:
        return "text"
    if ext in [".pdf", ".docx", ".doc"]:
        return "document"
    return "binary"


def _infer_has_tables(text: str) -> bool:
    """Infer whether text contains table-like structures."""
    lower_text = text.lower()
    if "<table>" in lower_text or "<tr>" in lower_text:
        return True

    lines = text.strip().split("\n")
    if len(lines) > 2:
        separators = [",", "\t", "|"]
        for sep in separators:
            lines_with_sep = [line for line in lines if sep in line]
            if len(lines_with_sep) > 1:
                counts = [line.count(sep) for line in lines_with_sep[:5]]
                if len(counts) > 1 and counts[0] > 0 and all(c == counts[0] for c in counts):
                    return True

    return False


def extract_metadata(
    text: str,
    filename: str,
    base_metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Extract deterministic metadata from text and filename."""
    metadata = (base_metadata or {}).copy()
    extension = Path(filename).suffix.lower()

    metadata.update(
        {
            "filename": filename,
            "extension": extension,
            "text_length": len(text),
            "inferred_doc_type": _infer_doc_type(extension),
            "has_tables": _infer_has_tables(text),
            "source_hash": hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest(),
        }
    )
    return metadata


def build_document_metadata(path: Path, text: str) -> dict[str, Any]:
    """Backward-compatible metadata builder for legacy callers."""
    return extract_metadata(text=text, filename=path.name)