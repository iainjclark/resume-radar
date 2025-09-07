from pathlib import Path

import os
os.environ["MUPDF_LOG_LEVEL"] = "0"  # attempt to silence MuPDF logs 

# PDF libraries

# ⚠️ ISSUE: Highlight annotations ignore custom fill colors in most PDF readers.
# This prints non-fatal warnings "Warning: fill color ignored for annot type 'Highlight'." 
# TODO: find a workaround or alternative annotation type.
import fitz  # PyMuPDF

placed_sections = set()

# Traffic light colors
TAG_COLORS = {
    "[GOOD]": (0.6, 0.9, 0.6),   # green
    "[CAUTION]": (1.0, 1.0, 0.6), # yellow
    "[BAD]": (1.0, 0.6, 0.6),    # red
}

def flatten_feedback(feedback_list):
    """Flatten nested feedback into simple dicts with 'snippet'."""
    flattened = []
    for item in feedback_list:
        if isinstance(item, dict):
            if "snippet" in item:
                flattened.append(item)
            elif "result" in item and isinstance(item["result"], list):
                flattened.extend(item["result"])
            else:
                for v in item.values():
                    if isinstance(v, list):
                        flattened.extend(v)
        elif isinstance(item, list):
            flattened.extend(item)
    return flattened


def overlay_pdf(input_path, output_path, *feedback_sources):
    """Overlay feedback (sectional + granular) onto PDF."""
    doc = fitz.open(input_path)

    # Flatten everything into a single list of dicts with 'snippet'
    feedback = []
    for source in feedback_sources:
        feedback.extend(flatten_feedback(source))

    for fb in feedback:
        _place_annotation(doc, fb)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(output_path))
    print(f"📄 Annotated PDF saved to {output_path}")

def _place_annotation(doc, fb, single_hit=True):
    """Helper to place a highlight+tooltip annotation."""
    snippet = fb.get("snippet", "")
    tag = fb.get("tag", "")
    feedback_text = fb.get("feedback", "")
    rating = fb.get("rating", "?")

    # Skip neutral/empty feedback
    if tag.strip().upper() in ["", "[NEUTRAL]"]:
        return
        
    color = TAG_COLORS.get(tag, (0.9, 0.9, 0.9))

    placed = False
    for page_num, page in enumerate(doc):
        rects = page.search_for(snippet)
        if rects:
            if single_hit:   # section-level feedback
                rects = rects[:1]   # 🔑 only take the first hit

            for rect in rects:
                highlight = page.add_highlight_annot(rect)
                highlight.set_colors(stroke=color, fill=color)
                highlight.update()
                highlight.set_popup(rect)
                highlight.set_info(
                    title="resume-radar",
                    content=f"{feedback_text}"
                )
                page.insert_text(
                    (rect.x0, rect.y1 + 10),
                    "⌖",
                    fontsize=12,
                    color=(0, 0, 0)
                )
                placed = True

            if placed:
                print(f"✅ Annotated '{snippet}' on page {page_num+1}")
                break

    if not placed:
        print(f"⚠️ Snippet not found in PDF: {snippet}")
