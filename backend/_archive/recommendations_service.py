from openai import AsyncOpenAI
from app.config import settings


async def generate_recommendations(summary_text: str, patient_history: str = "", diagnosis_tags: list = None) -> str:
    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    diagnosis_str = ""
    if diagnosis_tags:
        diagnosis_str = "\n".join([f"- {t.get('tag_code', '')}: {t.get('tag_label', '')}" for t in diagnosis_tags])

    prompt = f"""Based on the following medical visit summary and patient history, provide treatment recommendations.

Summary:
{summary_text}

{f'Diagnoses:{chr(10)}{diagnosis_str}' if diagnosis_str else ''}

{f'Patient History:{chr(10)}{patient_history}' if patient_history else ''}

Provide recommendations in Hebrew. Include:
1. Immediate treatment steps
2. Medications if appropriate
3. Follow-up timeline
4. Warning signs to watch for
5. Lifestyle recommendations if relevant

Be concise and clinically accurate."""

    response = await client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )

    return response.choices[0].message.content
