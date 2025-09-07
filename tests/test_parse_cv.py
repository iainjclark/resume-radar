import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from parse_cv import split_into_sections_dynamic

def test_detects_sections():
    sample_cv = """
    John Doe
    New York, NY

    Professional Summary
    Visionary leader with experience driving change.

    Professional Experience
    Director, Strategy & Transformation, GlobalCorp

    Education
    MBA, University of Somewhere
    """

    sections = split_into_sections_dynamic(sample_cv)

    # Basic expectations
    assert "Professional Summary" in sections
    assert "Professional Experience" in sections
    assert "Education" in sections

    # Content is preserved
    assert "Visionary leader" in sections["Professional Summary"]
    assert "Director, Strategy & Transformation" in sections["Professional Experience"]
