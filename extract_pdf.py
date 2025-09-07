from pathlib import Path
import fitz  # PyMuPDF


def extract_text_from_pdf(path: Path) -> str:
    """Extract text from a PDF using PyMuPDF (fitz)."""
    text = []
    with fitz.open(path) as doc:
        for page in doc:
            text.append(page.get_text("text"))
    return "\n".join(text)
