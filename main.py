import sys
from pathlib import Path
import PyPDF2
import fitz  # PyMuPDF
import os
from openai import OpenAI
from dotenv import load_dotenv
import re
import json

from decorate_pdf import decorate_pdf  # Import the decorate_pdf function

# Load environment variables from .env if it exists
load_dotenv()

# Create client (expects env var OPENAI_API_KEY to be set)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_text_from_pdf(path: Path, method: str = "pymupdf") -> str:
    """Extract text from PDF using either PyPDF2 or PyMuPDF (default)."""
    text = ""
    if method == "pypdf2":
        with open(path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() or ""
                text += "\n"
    elif method == "pymupdf":
        with fitz.open(path) as doc:
            for page in doc:
                text += page.get_text()
    else:
        raise ValueError("Unsupported method. Use 'pypdf2' or 'pymupdf'.")
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

def clean_text(text: str) -> str:
    """Fix common PDF text extraction issues (extra spaces, linebreaks)."""
    # Collapse multiple spaces into one
    text = re.sub(r"\s+", " ", text)
    # Strip leading/trailing whitespace
    return text.strip()

def query_llm(chunk: str) -> dict:
    """Send chunk to OpenAI API and return structured feedback with ratings and tags."""

    prompt = f"""
    You are reviewing part of a resume. 
    For each distinct section or element in the text, do the following:

    1. Give it a rating from 0 to 20 (integer only).
    2. Add one of these tags based on the rating:
       - [GOOD] if rating ≥ 16
       - [BAD] if rating ≤ 6
       - [CAUTION] if rating is between 7 and 10
       - Leave untagged if rating is between 11 and 15.
    3. Provide a brief justification (1–2 sentences max).

    Respond in JSON format like this:
    [
      {{
        "snippet": "summary of text element",
        "rating": 18,
        "tag": "[GOOD]",
        "feedback": "Clear and strong professional summary."
      }},
      {{
        "snippet": "education section",
        "rating": 9,
        "tag": "[CAUTION]",
        "feedback": "Needs more detail on coursework or achievements."
      }}
    ]

    Resume text:
    {chunk}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
    )

    feedback = response.choices[0].message.content.strip()
    return {"chunk": chunk[:80], "feedback": feedback}

def parse_llm_feedback(raw_feedback: str) -> list[dict]:
    """Extract and parse JSON from LLM feedback safely."""
    # Remove Markdown code fences if present
    cleaned = re.sub(r"^```json|```$", "", raw_feedback.strip(), flags=re.MULTILINE).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        print("⚠️ Could not parse feedback as JSON. Raw output returned.")
        return [{"raw_feedback": raw_feedback}]

def main():
    print("🚀 resume-radar is alive!")

    # Default to inputs/JohnDoe.pdf unless another path is provided
    pdf_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("inputs/CV_JohnDoe.pdf")

    if pdf_path.exists():
        text = extract_text_from_pdf(pdf_path)
        text = clean_text(text)
        chunks = chunk_text(text)
        results = [] 
        for c in chunks:
            raw = query_llm(c)
            parsed = parse_llm_feedback(raw["feedback"])
            results.extend(parsed)        
        for r in results:
            print(r)
    else:
        print(f"⚠️ PDF not found: {pdf_path}. Please check your inputs folder.")

    # After collecting & parsing results:
    decorate_pdf(results)



if __name__ == "__main__":
    main()