import io, contextlib
import os
os.environ["MUPDF_LOG_LEVEL"] = "0"  # attempt to silence MuPDF logs 

# PDF libraries

# ⚠️ ISSUE: Highlight annotations ignore custom fill colors in most PDF readers.
# This prints non-fatal warnings "Warning: fill color ignored for annot type 'Highlight'." 
# TODO: find a workaround or alternative annotation type.
import fitz  # PyMuPDF

import PyPDF2

from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
import re
import json

from extract_pdf import extract_text_from_pdf
from parse_cv import split_into_sections_dynamic
from global_llm_reflection import global_llm_reflection
from sectional_llm_critique import section_feedback
from granular_llm_critique import granular_feedback
from overlay_pdf import overlay_pdf

# Input / output paths
INPUT_PDF = Path("inputs/CV_RobinDoe.pdf")
OUTPUT_PDF = Path("outputs/CV_RobinDoe_reviewed.pdf")

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

# Map tags to colors (RGB format, 0–1 range)
TAG_COLORS = {
    "[GOOD]": (0.6, 0.9, 0.6),    # green
    "[CAUTION]": (1.0, 1.0, 0.6), # yellow
    "[BAD]": (1.0, 0.6, 0.6),     # red
    "": (0.9, 0.9, 0.9)           # grey/neutral
}

def main():
    print("⌖ resume-radar: starting full pipeline")

    # 1. Extract text
    cv_text = extract_text_from_pdf(INPUT_PDF)
    print("\n--- Extracted CV Text ---")
    print(cv_text[:500], "...\n")  # preview only

    # 2. Global reflection
    reflection = global_llm_reflection(cv_text)
    print("\n--- Global Reflection ---")
    print(json.dumps(reflection, indent=2))

    # 3. Split into sections
    sections = split_into_sections_dynamic(cv_text)

    # 4. Per-section feedback (mark them as "section")
    section_results = section_feedback(sections)
    for fb in section_results:
        fb["level"] = "section"

    # 5. Granular feedback (mark them as "granular")
    granular_results = granular_feedback(sections)
    for fb in granular_results:
        fb["level"] = "granular"

    # 6. Collate for overlay:
    section_feedback_list = [fb for fb in section_results if fb.get("tag")]
#    granular_feedback_list = [fb for fb in granular_results if fb.get("tag")]

    # 7. Only keep valid dicts with snippets
#    annotated_feedback = [fb for fb in annotated_feedback if isinstance(fb, dict) and "snippet" in fb]

    # 8. Overlay PDF with annotations
    overlay_pdf(INPUT_PDF, OUTPUT_PDF, section_feedback_list, granular_results)
    print(f"\n📄 Pipeline complete: annotated CV written to {OUTPUT_PDF}")

if __name__ == "__main__":
    main()