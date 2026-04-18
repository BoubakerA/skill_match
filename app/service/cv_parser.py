import os
import json
from mistralai.client import Mistral


def parse_cv_with_mistral(cv_text: str) -> dict:
    api_key = os.environ.get("MISTRAL_API_KEY")

    if not api_key:
        raise ValueError("MISTRAL_API_KEY non définie")

    client = Mistral(api_key=api_key)

    prompt = f"""
You are an expert CV parser.

The CV may be written in French or English.

Extract structured information from the CV.

Return ONLY a valid JSON with this structure:

{{
  "name": "",
  "email": "",
  "phone": "",
  "location": "",
  "summary": "",
  "skills": [],
  "languages": [],
  "experience": [],
  "education": []
}}

Rules:
- Do NOT translate
- Keep original language
- Return JSON only
- No explanation

CV:
{cv_text}
"""

    response = client.chat.complete(
        model="mistral-small-latest",
        messages=[
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"}
    )

    content = response.choices[0].message.content

    return json.loads(content)