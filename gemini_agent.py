import os
from dotenv import load_dotenv
from google import genai

load_dotenv()


def generate_hr_insights(audit_results):
    """Use Gemini to interpret HR OpsGuard audit results."""

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return "Gemini API key not found. Please check your .env file."

    client = genai.Client(api_key=api_key)

    audit_data = audit_results.to_json(orient="records")

    prompt = f"""
You are HR OpsGuard, an AI analyst supporting HR Operations.

Analyze the following HR audit results.

Your task is to:
1. Give a short executive summary.
2. Identify the top operational risks.
3. Identify recurring patterns in the exceptions.
4. Recommend practical HR process improvements.
5. Explain which areas should be prioritized.

Important rules:
- Use ONLY the audit results provided below.
- Do not invent policies, employee information, or facts.
- Do not make hiring, firing, compensation, or other employment decisions.
- Treat the data as synthetic HR operations data.
- Keep the response concise and professional.

Audit results:
{audit_data}
"""

    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt
    )

    return response.text