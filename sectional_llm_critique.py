import os
import json
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

from llm_prompts import SECTION_CRITIQUE_PROMPT

def section_feedback(sections: dict) -> list:
    """
    Call the LLM for each CV section and return structured feedback.
    Model is forced to return valid JSON.
    """
    feedback = []

    for header, content in sections.items():
        prompt = f"""{SECTION_CRITIQUE_PROMPT}

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
                response_format={"type": "json_object"},  # Force JSON output
            )

            fb = response.choices[0].message.content
            fb_parsed = json.loads(fb)

            # Force snippet to just be the section header
            fb_parsed["snippet"] = header.strip().split("\n")[0]

            feedback.append(fb_parsed)

        except Exception as e:
            print(f"⚠️ Error processing section {header}: {e}")
            feedback.append({
                "snippet": header.strip().split("\n")[0],  # ensure we still use header
                "rating": "?",
                "tag": "",
                "feedback": f"LLM output could not be parsed. Error: {e}"
            })

    return feedback
