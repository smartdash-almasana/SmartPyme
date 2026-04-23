from pathlib import Path

from extraction.docling_parser import parse_pdf
from models.document_models import SourceDocument


def load_pdf_document(pdf_path: str | Path) -> SourceDocument:
    return parse_pdf(Path(pdf_path))
