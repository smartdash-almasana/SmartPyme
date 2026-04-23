from __future__ import annotations

from pathlib import Path
from typing import Any

from extraction.metadata_extractor import build_document_metadata
from extraction.ocr_fallback import run_ocr_fallback
from models.document_models import SourceDocument


def _safe_page_number(page_obj: Any, fallback: int) -> int:
    """Resolve a positive page number from heterogeneous Docling page objects."""
    for attr in ("page_no", "page_number", "number", "id"):
        value = getattr(page_obj, attr, None)
        if isinstance(value, int) and value > 0:
            return value
    return fallback


def _safe_page_text(page_obj: Any) -> str:
    """Extract best-effort page text from Docling page representations."""
    export_to_markdown = getattr(page_obj, "export_to_markdown", None)
    if callable(export_to_markdown):
        try:
            value = export_to_markdown()
            if value:
                return str(value).strip()
        except Exception:
            pass

    for attr in ("text", "content", "markdown"):
        value = getattr(page_obj, attr, None)
        if isinstance(value, str) and value.strip():
            return value.strip()

    return ""


def _docling_extract_text(pdf_path: Path) -> tuple[str, list[dict[str, Any]]]:
    """Parse a PDF with Docling and return full text plus page-level evidence."""
    try:
        from docling.document_converter import DocumentConverter  # type: ignore
    except Exception:
        return "", []

    try:
        converter = DocumentConverter()
        result = converter.convert(str(pdf_path))
        doc = getattr(result, "document", None)
        if doc is None:
            return str(result).strip(), []

        pages: list[dict[str, Any]] = []
        page_items = getattr(doc, "pages", None)
        if isinstance(page_items, list):
            for idx, page_obj in enumerate(page_items, start=1):
                page_text = _safe_page_text(page_obj)
                if page_text:
                    pages.append(
                        {
                            "page": _safe_page_number(page_obj, idx),
                            "text": page_text,
                        }
                    )

        export = getattr(doc, "export_to_markdown", None)
        full_text = ""
        if callable(export):
            full_text = str(export()).strip()
        if not full_text and pages:
            full_text = "\n\n".join(page["text"] for page in pages).strip()

        return full_text, pages
    except Exception:
        return "", []


def _read_text_best_effort(path: Path) -> str:
    """Fallback reader for text-like files when structured parsing fails."""
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        try:
            return path.read_text(encoding="latin-1", errors="ignore")
        except Exception:
            return ""


def parse_pdf(pdf_path: Path) -> SourceDocument:
    """Parse a PDF into a SourceDocument using Docling first, then fallbacks."""
    text, pages = _docling_extract_text(pdf_path)
    parser_used = "docling"
    if not text.strip():
        text = run_ocr_fallback(pdf_path)
        parser_used = "ocr_fallback"
        if text.strip():
            pages = [{"page": 1, "text": text}]
    if not text.strip():
        text = _read_text_best_effort(pdf_path)
        parser_used = "plain_text_fallback"
        if text.strip():
            pages = [{"page": 1, "text": text}]

    metadata = build_document_metadata(pdf_path, text)
    metadata["parser_used"] = parser_used
    metadata["pages"] = pages
    return SourceDocument(
        filename=pdf_path.name,
        text=text,
        page=1,
        metadata=metadata,
    )
