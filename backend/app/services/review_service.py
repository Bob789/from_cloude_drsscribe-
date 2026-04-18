"""
Article quality review service.
Uses Mistral (independent model) to score articles before auto-publishing.

Scoring rubric (0-100):
  - Structure & clarity        (25 pts)
  - Medical completeness       (25 pts)
  - Medical responsibility     (25 pts)  — disclaimer, when-to-see-doctor section
  - Language & accessibility   (25 pts)

Articles scoring >= ARTICLE_QUALITY_THRESHOLD are auto-published.
"""

import json
import structlog
from app.config import settings

logger = structlog.get_logger()

REVIEW_SYSTEM_PROMPT = """You are a professional medical content reviewer. 
Evaluate Hebrew medical articles objectively and return ONLY a JSON object.

Score the article on four criteria (0-25 each, total 0-100):

1. structure_score (0-25): Clear intro/hook, 3+ H2 sections, bullets, conclusion with CTA
2. completeness_score (0-25): Covers symptoms/causes/treatment/prevention relevant to topic
3. responsibility_score (0-25): Has medical disclaimer, has "מתי לפנות לרופא" section, no dangerous advice, no specific drug dosages
4. language_score (0-25): Clear Hebrew, accessible to general public, professional but warm tone

Return ONLY this JSON (no explanation, no markdown):
{
  "structure_score": 0,
  "completeness_score": 0,
  "responsibility_score": 0,
  "language_score": 0,
  "total_score": 0,
  "issues": ["issue1", "issue2"],
  "strengths": ["strength1"]
}"""


async def review_article(title: str, content_markdown: str) -> dict:
    """
    Send article to Mistral for quality review.
    Returns dict with scores and notes.
    Falls back gracefully if Mistral API key not configured.
    """
    if not settings.MISTRAL_API_KEY:
        logger.warning("mistral_api_key_not_set", action="skipping_review")
        return {"total_score": None, "skipped": True, "reason": "MISTRAL_API_KEY not configured"}

    try:
        from mistralai import Mistral
        client = Mistral(api_key=settings.MISTRAL_API_KEY)

        user_message = f"""כותרת: {title}

תוכן המאמר:
{content_markdown[:6000]}"""  # cap at 6000 chars to control cost

        response = await client.chat.complete_async(
            model=settings.MISTRAL_REVIEW_MODEL,
            messages=[
                {"role": "system", "content": REVIEW_SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
            max_tokens=500,
        )

        raw = response.choices[0].message.content.strip()
        result = json.loads(raw)

        # Ensure total_score is consistent
        computed = (
            result.get("structure_score", 0)
            + result.get("completeness_score", 0)
            + result.get("responsibility_score", 0)
            + result.get("language_score", 0)
        )
        result["total_score"] = computed
        result["skipped"] = False

        logger.info(
            "article_reviewed",
            title=title[:60],
            score=computed,
            issues=result.get("issues", []),
        )
        return result

    except Exception as exc:
        logger.error("article_review_failed", error=str(exc))
        return {"total_score": None, "skipped": True, "reason": str(exc)[:200]}
