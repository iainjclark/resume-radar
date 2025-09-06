from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from pathlib import Path


def decorate_pdf(feedback: list[dict], output_path: Path = Path("outputs/Decorated.pdf")):
    """
    Create a decorated PDF from LLM feedback.
    Each entry is displayed with colored background and ⌖ marker.
    """

    # Ensure output folder exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    c = canvas.Canvas(str(output_path), pagesize=letter)
    width, height = letter

    y = height - 50  # start from top margin

    for item in feedback:
        snippet = item.get("snippet", "")[:60]  # short preview
        rating = item.get("rating", "")
        tag = item.get("tag", "")
        note = item.get("feedback", "")

        # Choose color based on tag
        if tag == "[GOOD]":
            fill_color = colors.lightgreen
        elif tag == "[CAUTION]":
            fill_color = colors.yellow
        elif tag == "[BAD]":
            fill_color = colors.red
        else:
            fill_color = colors.whitesmoke

        # Draw background box
        c.setFillColor(fill_color)
        c.rect(40, y - 30, width - 80, 40, fill=1, stroke=0)

        # Draw ⌖ crosshair marker
        c.setFillColor(colors.black)
        c.drawString(45, y - 15, "⌖")

        # Write text on top
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 10)
        c.drawString(70, y - 10, f"{tag or '[NEUTRAL]'} ({rating}/20): {snippet}")
        y -= 60

        # New page if space runs out
        if y < 100:
            c.showPage()
            y = height - 50

    c.save()
    print(f"✅ Decorated PDF written to {output_path}")
