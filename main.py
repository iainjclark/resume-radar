import sys
from pathlib import Path
import PyPDF2


def extract_text_from_pdf(path: Path) -> str:
    """Extract all text from a PDF file."""
    text = ""
    with open(path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text += page.extract_text() or ""  # handle pages with no text
            text += "\n"
    return text

def main():
    print("🚀 resume-radar is alive!")

    # Default to inputs/JohnDoe.pdf unless another path is provided
    pdf_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("inputs/CV_JohnDoe.pdf")

    if pdf_path.exists():
        sample_text = extract_text_from_pdf(pdf_path)
        print(f"✅ Extracted text from: {pdf_path}\n")
        print(sample_text[:500])  # preview first 500 chars
    else:
        print(f"⚠️ PDF not found: {pdf_path}. Please check your inputs folder.")


if __name__ == "__main__":
    main()