import re

def split_into_sections_dynamic(cv_text: str):
    """
    Detect section headers dynamically and split CV text into sections.
    Returns a dict {header: content}.
    """
    lines = cv_text.splitlines()
    headers = []
    sections = {}

    # Step 1: detect candidate headers
    for i, line in enumerate(lines):
        clean = line.strip()
        if not clean:
            continue
        # Heuristic: Title Case or ALL CAPS, short (≤ 5 words)
        if re.match(r"^[A-Z][A-Za-z ]+$", clean) or clean.isupper():
            if len(clean.split()) <= 5:
                headers.append((i, clean))

    # Step 2: slice into sections
    for idx, (line_num, header) in enumerate(headers):
        start = line_num
        end = headers[idx + 1][0] if idx + 1 < len(headers) else len(lines)
        section_text = "\n".join(lines[start:end]).strip()
        sections[header] = section_text

    return sections

if __name__ == "__main__":
    # Demo with sample CV text file
    from pathlib import Path
    cv_text = Path("inputs/CV_JohnDoe.txt").read_text(encoding="utf-8")
    sections = split_into_sections_dynamic(cv_text)
    for header, content in sections.items():
        print(f"--- {header} ---\n{content[:200]}...\n")
