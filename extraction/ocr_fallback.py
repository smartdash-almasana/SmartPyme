from __future__ import annotations

from pathlib import Path


def run_ocr_fallback(pdf_path: Path) -> str:
    """Run a defensive OCR fallback for PDF documents when text extraction fails."""
    try:
        import pytesseract  # type: ignore
        from pdf2image import convert_from_path  # type: ignore
        from pdf2image.exceptions import PDFInfoNotInstalledError  # type: ignore
    except ImportError:
        return ""

    try:
        pages = convert_from_path(str(pdf_path), timeout=30)
    except (PDFInfoNotInstalledError, FileNotFoundError, Exception):
        return ""

    if not pages:
        return ""

    extracted_texts: list[str] = []
    for image in pages:
        try:
            text = pytesseract.image_to_string(
                image,
                lang="spa+eng",
                timeout=20,
            ).strip()
            if text:
                extracted_texts.append(text)
        except (pytesseract.TesseractNotFoundError, FileNotFoundError, Exception):
            continue

    return "\n\n<page_break>\n\n".join(extracted_texts)
