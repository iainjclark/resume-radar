from pathlib import Path
import fitz  # PyMuPDF
import warnings

# Colors for traffic-light style tags
TAG_COLORS = {
    "[GOOD]": (0.7, 1.0, 0.7),     # light green
    "[CAUTION]": (1.0, 1.0, 0.6),  # light yellow
    "[BAD]": (1.0, 0.7, 0.7),      # light red
}


def overlay_pdf(input_path: Path, output_path: Path, feedback: list):
    """Overlay highlights + tooltips onto the original PDF based on feedback."""
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning, module="fitz")

        doc = fitz.open(input_path)

        for fb in feedback:
            snippet = fb.get("snippet", "")
            tag = fb.get("tag", "")
            feedback_text = fb.get("feedback", "")
            rating = fb.get("rating", "?")

            color = TAG_COLORS.get(tag, (0.9, 0.9, 0.9))

            for page_num, page in enumerate(doc):
                rects = page.search_for(snippet)
                if rects:
                    for rect in rects:
                        # Highlight annotation
                        highlight = page.add_highlight_annot(rect)
                        highlight.set_colors(stroke=color, fill=color)
                        highlight.update()

                        # Tooltip popup
                        highlight.set_popup(rect)
                        highlight.set_info(
                            title="resume-radar",
                            content=f"{tag} ({rating}/20): {feedback_text}"
                        )

                        # Radar marker
                        page.insert_text(
                            (rect.x0, rect.y1 + 10),
                            "⌖",
                            fontsize=12,
                            color=(0, 0, 0)
                        )

                    print(f"✅ Annotated '{snippet}' on page {page_num+1}")
                    break
            else:
                print(f"⚠️ Snippet not found in PDF: {snippet}")

        output_path.parent.mkdir(parents=True, exist_ok=True)
        doc.save(str(output_path))
        print(f"📄 Annotated PDF saved to {output_path}")
