from pathlib import Path
import json
from openai import OpenAI
from dotenv import load_dotenv
import os

# Load environment variables (API key)
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def global_llm_reflection(cv_text: str, scale: int = 20):
    """
    Ask the LLM for a holistic CV review.
    Returns structured JSON with rating, strengths, weaknesses, and feedback.
    """
    prompt = f"""
    You are a professional CV reviewer.
    Read the CV in full and provide a JSON object with these fields:
    - rating: integer out of {scale}
    - strengths: list of 3 concise bullet points
    - weaknesses: list of 3 concise bullet points
    - feedback: a short paragraph of overall impressions

    CV:
    {cv_text}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    content = response.choices[0].message.content

    # Try to parse JSON safely
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {"raw_output": content}

if __name__ == "__main__":
    # Demo run on sample CV
    sample_text = Path("inputs/CV_JohnDoe.txt").read_text(encoding="utf-8")
    result = global_llm_reflection(sample_text, scale=20)

    Path("outputs/global_llm_reflection.json").write_text(json.dumps(result, indent=2))
    print("📊 Global reflection saved to outputs/global_llm_reflection.json")
