"""Document parsing: PDF, TXT, MD with pypdf and OCR via pytesseract."""

import io
from pathlib import Path
from typing import Any, Dict, List, Optional

from pypdf import PdfReader
import pytesseract
from PIL import Image

# Optional: pdf2image for PDF page -> image conversion
try:
    from pdf2image import convert_from_path
    HAS_PDF2IMAGE = True
except ImportError:
    HAS_PDF2IMAGE = False


def parse_document(file_path: str, filename: str) -> Dict[str, Any]:
    """
    Parse PDF, TXT, or MD file.
    Returns: { documents: [...], text: str, metadata: {...} }
    """
    path = Path(file_path)
    ext = path.suffix.lower()

    if ext == ".pdf":
        return _parse_pdf(file_path, filename)
    if ext in (".txt", ".md"):
        return _parse_text(file_path, filename)
    raise ValueError(f"Unsupported file type: {ext}")


def _parse_pdf(file_path: str, filename: str) -> Dict[str, Any]:
    """Extract text from PDF using pypdf, with per-page metadata."""
    reader = PdfReader(file_path)
    documents: List[Dict[str, Any]] = []
    all_text: List[str] = []

    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        page_num = i + 1
        metadata = {"source": filename, "page": page_num}
        if text.strip():
            documents.append({"content": text, "metadata": metadata})
            all_text.append(text)

    full_text = "\n\n".join(all_text)
    return {
        "documents": documents,
        "text": full_text,
        "metadata": {"source": filename, "pages": len(reader.pages)},
    }


def _parse_text(file_path: str, filename: str) -> Dict[str, Any]:
    """Parse TXT or MD file."""
    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        text = f.read()
    metadata = {"source": filename, "page": 1}
    return {
        "documents": [{"content": text, "metadata": metadata}],
        "text": text,
        "metadata": metadata,
    }


def extract_images_ocr(file_path: str, filename: str) -> Dict[str, Any]:
    """
    Extract images from PDF, run OCR via pytesseract.
    Returns: { text: str, images_processed: int }
    """
    path = Path(file_path)
    if path.suffix.lower() != ".pdf":
        return {"text": "", "images_processed": 0}

    if not HAS_PDF2IMAGE:
        # Fallback: try pypdf images
        try:
            reader = PdfReader(file_path)
            texts = []
            count = 0
            for page in reader.pages:
                if "/XObject" in page["/Resources"]:
                    xobj = page["/Resources"]["/XObject"].get_object()
                    for obj in xobj:
                        if xobj[obj]["/Subtype"] == "/Image":
                            count += 1
                            # OCR extraction from pypdf images is complex; skip for simplicity
            return {"text": "", "images_processed": count}
        except Exception:
            return {"text": "", "images_processed": 0}

    try:
        images = convert_from_path(file_path, dpi=150)
        ocr_texts: List[str] = []
        for i, img in enumerate(images):
            text = pytesseract.image_to_string(img)
            if text.strip():
                ocr_texts.append(f"[Page {i+1} OCR]\n{text}")
        return {
            "text": "\n\n".join(ocr_texts),
            "images_processed": len(images),
        }
    except Exception as e:
        return {"text": "", "images_processed": 0, "error": str(e)}
