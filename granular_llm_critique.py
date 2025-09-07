import os
import json
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

from llm_prompts import GRANULAR_CRITIQUE_PROMPT

def granular_feedback(sections: dict) -> list:
    """
    For each CV section, request granular feedback at the phrase/sentence level.
    Returns a list of dicts with: snippet, rating, tag, feedback.
    """
    all_feedback = []

    for header, content in sections.items():
        prompt = f"""{GRANULAR_CRITIQUE_PROMPT}

        Section Header: {header}
        Section Content:
        {content}
"""

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a precise CV analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
            )

            fb = response.choices[0].message.content.strip()
            fb_parsed = json.loads(fb)

            # Ensure list of dicts
            if isinstance(fb_parsed, dict):
                all_feedback.append(fb_parsed)
            elif isinstance(fb_parsed, list):
                all_feedback.extend(fb_parsed)
            else:
                print(f"⚠️ Unexpected response format for {header}: {type(fb_parsed)}")

        except Exception as e:
            print(f"⚠️ Error processing granular feedback for {header}: {e}")
            all_feedback.append({
                "snippet": header,
                "rating": "?",
                "tag": "",
                "feedback": f"LLM granular critique failed: {e}"
            })
    print(f"📝 Granular feedback generated for {len(sections)} sections, total {len(all_feedback)} items.")
    print(all_feedback)
    return all_feedback
