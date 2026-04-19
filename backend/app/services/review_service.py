"""
Article quality review service.
Uses Mistral (independent model) to score articles before auto-publishing.
Also offers GPT-based fix when score < threshold, then re-reviews.

Scoring rubric (0-100) — 7 criteria:
  1. Structure & clarity        (15 pts)
  2. Medical completeness       (15 pts)
  3. Medical responsibility     (15 pts)  — disclaimer, when-to-see-doctor section
  4. Language & accessibility   (15 pts)
  5. Factual accuracy           (15 pts)  — correct dates, stats, medical facts
  6. Logic & style consistency  (15 pts)  — no contradictions, uniform style
  7. Content safety & relevance (10 pts)  — no offensive/profanity, relevant to title

Articles scoring >= ARTICLE_QUALITY_THRESHOLD are auto-published.
"""

import json
import structlog
from app.config import settings

logger = structlog.get_logger()

REVIEW_SYSTEM_PROMPT = """You are a professional medical content reviewer.
Evaluate medical articles objectively and return ONLY a JSON object.

Score the article on seven criteria:

1. structure_score (0-15): Clear intro/hook, 3+ H2 sections, bullets, conclusion with CTA
2. completeness_score (0-15): Covers symptoms/causes/treatment/prevention relevant to topic
3. responsibility_score (0-15): Has medical disclaimer, has "when to see a doctor" section, no dangerous advice, no specific drug dosages
4. language_score (0-15): Clear language, accessible to general public, professional but warm tone, correct grammar and punctuation
5. factual_score (0-15): No incorrect dates, statistics, medical facts; data is consistent and plausible
6. logic_style_score (0-15): No internal contradictions, consistent arguments, uniform style throughout
7. safety_score (0-10): No offensive content, no profanity, no personal attacks, article is clearly relevant to the requested title

Return ONLY this JSON (no explanation, no markdown):
{
  "structure_score": 0,
  "completeness_score": 0,
  "responsibility_score": 0,
  "language_score": 0,
  "factual_score": 0,
  "logic_style_score": 0,
  "safety_score": 0,
  "total_score": 0,
  "issues": ["issue1", "issue2"],
  "strengths": ["strength1"]
}"""

FIX_SYSTEM_PROMPT = """You are a professional medical writer.
You will receive a medical article and a list of issues found during quality review.
Fix ALL the listed issues and return the improved article as a JSON object.
Keep the same title, structure and language. Only fix the problems listed.
Return ONLY this JSON (no explanation, no markdown):
{
  "title": "...",
  "subtitle": "...",
  "content_markdown": "...",
  "summary": "..."
}"""


async def review_article(title: str, content_markdown: str) -> dict:
    """
    Send article to Mistral for quality review.
    Returns dict with scores and notes.
    Falls back gracefully if Mistral API key not configured or expired.
    """
    if not settings.MISTRAL_API_KEY:
        logger.warning("mistral_api_key_not_set", action="skipping_review")
        return {"total_score": None, "skipped": True, "reason": "MISTRAL_API_KEY not configured"}

    try:
        from mistralai import Mistral
        client = Mistral(api_key=settings.MISTRAL_API_KEY)

        user_message = f"""Title: {title}

Article content:
{content_markdown[:6000]}"""

        response = await client.chat.complete_async(
            model=settings.MISTRAL_REVIEW_MODEL,
            messages=[
                {"role": "system", "content": REVIEW_SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
            max_tokens=600,
        )

        raw = response.choices[0].message.content.strip()
        result = json.loads(raw)

        computed = (
            result.get("structure_score", 0)
            + result.get("completeness_score", 0)
            + result.get("responsibility_score", 0)
            + result.get("language_score", 0)
            + result.get("factual_score", 0)
            + result.get("logic_style_score", 0)
            + result.get("safety_score", 0)
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
        err_str = str(exc)
        # Detect API key expiry / auth failure
        if any(k in err_str.lower() for k in ("401", "unauthorized", "authentication", "api key", "expired", "invalid_api_key")):
            logger.error("mistral_api_key_expired_or_invalid", error=err_str[:200])
            return {"total_score": None, "skipped": True, "expired": True,
                    "reason": "MISTRAL_API_KEY פג תוקף או לא תקין — יש לעדכן ב-.env"}
        logger.error("article_review_failed", error=err_str)
        return {"total_score": None, "skipped": True, "reason": err_str[:200]}


async def fix_article_with_gpt(title: str, content_markdown: str, issues: list[str]) -> dict | None:
    """
    Send article + Mistral issues list to ChatGPT to fix.
    Returns fixed article dict or None on failure.
    """
    if not settings.OPENAI_API_KEY:
        logger.warning("openai_api_key_not_set", action="skipping_fix")
        return None

    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

        issues_text = "\n".join(f"- {i}" for i in issues)
        user_message = f"""Title: {title}

Issues found in quality review that MUST be fixed:
{issues_text}

Original article:
{content_markdown[:7000]}"""

        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": FIX_SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
            max_tokens=3000,
        )

        raw = response.choices[0].message.content.strip()
        result = json.loads(raw)
        logger.info("article_fixed_by_gpt", title=title[:60], issues_count=len(issues))
        return result

    except Exception as exc:
        logger.error("article_fix_failed", error=str(exc)[:200])
        return None
