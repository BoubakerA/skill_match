import os
import json
from mistralai.client import Mistral


def parse_job_with_mistral(job_text: str) -> dict:
    api_key = os.environ.get("MISTRAL_API_KEY")

    if not api_key:
        raise ValueError("Clé API Mistral manquante")

    client = Mistral(api_key=api_key)

    prompt = f"""
You are an expert job description parser.

Extract structured information from this job description.

Return ONLY a valid JSON with this format:

{{
  "job_title": "",
  "required_skills": [],
  "optional_skills": [],
  "min_experience_years": 0
}}

Rules:
- Do NOT translate
- Keep original language (French or English)
- Required skills = mandatory skills
- Optional skills = nice-to-have skills
- Estimate experience if possible
- Return JSON only

Job description:
{job_text}
"""

    response = client.chat.complete(
        model="mistral-small-latest",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )

    content = response.choices[0].message.content
    return json.loads(content)