from pathlib import Path
import os
os.environ["MUPDF_LOG_LEVEL"] = "0"  # attempt to silence MuPDF logs 

# PDF libraries

# ⚠️ ISSUE: Highlight annotations ignore custom fill colors in most PDF readers.
# This prints non-fatal warnings "Warning: fill color ignored for annot type 'Highlight'." 
# TODO: find a workaround or alternative annotation type.
import fitz  # PyMuPDF

def extract_text_from_pdf(path: Path) -> str:
    """Extract text from a PDF using PyMuPDF (fitz)."""
    text = []
    with fitz.open(path) as doc:
        for page in doc:
            text.append(page.get_text("text"))
    return "\n".join(text)
