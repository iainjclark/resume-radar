import sys
from pathlib import Path
import PyPDF2
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env if it exists
load_dotenv()

# Create client (expects env var OPENAI_API_KEY to be set)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_text_from_pdf(path: Path) -> str:
    """Extract all text from a PDF file."""
    text = ""
    with open(path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text += page.extract_text() or ""  # handle pages with no text
            text += "\n"
    return text

def chunk_text(text: str, max_chars: int = 1500) -> list[str]:
    """Split text into chunks of up to max_chars."""
    chunks = []
    current = ""
    for line in text.splitlines():
        if len(current) + len(line) < max_chars:
            current += line + "\n"
        else:
            chunks.append(current.strip())
            current = line + "\n"
    if current:
        chunks.append(current.strip())
    return chunks

def query_llm(chunk: str) -> dict:
    """Send chunk to LLM and return feedback (stub)."""
    # TODO: integrate with OpenAI API
    return {"chunk": chunk[:50], "feedback": "Placeholder feedback"}

def main():
    print("🚀 resume-radar is alive!")

    # Default to inputs/JohnDoe.pdf unless another path is provided
    pdf_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("inputs/CV_JohnDoe.pdf")

    if pdf_path.exists():
#       sample_text = extract_text_from_pdf(pdf_path)
#       print(f"✅ Extracted text from: {pdf_path}\n")
#       print(sample_text[:500])  # preview first 500 chars
        text = extract_text_from_pdf(pdf_path)
        chunks = chunk_text(text)
        results = [query_llm(c) for c in chunks]
        print(results)
    else:
        print(f"⚠️ PDF not found: {pdf_path}. Please check your inputs folder.")


if __name__ == "__main__":
    main()