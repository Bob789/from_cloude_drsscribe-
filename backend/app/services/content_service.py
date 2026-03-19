"""
Content generation service for medical articles.
Uses GPT-4 to generate Hebrew medical content with anti-injection protection.
"""

import json
import re
from markdown_it import MarkdownIt
import structlog
from openai import AsyncOpenAI
from app.config import settings
from app.services.prompts.article_generation import (
    ARTICLE_SYSTEM_PROMPT, SEO_SYSTEM_PROMPT,
    AUTHOR_PERSONAS,
    build_article_prompt, build_seo_prompt,
    sanitize_external_input,
)

logger = structlog.get_logger()


async def generate_article(topic: str, config: dict | None = None) -> dict:
    """Generate a full medical article using GPT-4.
    Returns dict with title, subtitle, content_markdown, content_html, summary, etc."""
    config = config or {}
    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    user_prompt = build_article_prompt(topic, config)

    logger.info("generating_article", topic=topic[:80])

    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": ARTICLE_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.7,
        max_tokens=4000,
        response_format={"type": "json_object"},
    )

    raw = response.choices[0].message.content or "{}"

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        # Try to extract JSON from response
        json_match = re.search(r'\{[\s\S]+\}', raw)
        if json_match:
            result = json.loads(json_match.group())
        else:
            raise ValueError("GPT-4 did not return valid JSON")

    # Convert markdown to HTML
    md_content = result.get("content_markdown", "")
    md_parser = MarkdownIt("commonmark", {"breaks": True}).enable("table")
    html_content = md_parser.render(md_content)

    # Add medical disclaimer if not present
    disclaimer = "מאמר זה נועד למטרות מידע כללי בלבד ואינו מהווה תחליף לייעוץ רפואי מקצועי."
    if disclaimer not in md_content:
        html_content += f'\n<p style="color:#888;font-size:13px;margin-top:24px;border-top:1px solid #333;padding-top:12px"><em>{disclaimer}</em></p>'
        md_content += f"\n\n---\n*{disclaimer}*"

    # Set author persona
    persona_key = config.get("persona", "general")
    persona = AUTHOR_PERSONAS.get(persona_key, AUTHOR_PERSONAS["general"])

    result["content_html"] = html_content
    result["content_markdown"] = md_content
    result["author_name"] = persona["name"]
    result["author_title"] = persona["title"]
    result["generation_prompt"] = user_prompt
    result["read_time_minutes"] = estimate_read_time(md_content)

    logger.info("article_generated", title=result.get("title", "")[:60])
    return result


async def generate_seo_metadata(title: str, content: str) -> dict:
    """Generate SEO metadata (title, description, keywords, slug) using GPT-4."""
    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    user_prompt = build_seo_prompt(title, content)

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SEO_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
        max_tokens=500,
        response_format={"type": "json_object"},
    )

    raw = response.choices[0].message.content or "{}"
    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        result = {}

    # Ensure slug is URL-safe
    slug = result.get("slug", "")
    slug = re.sub(r'[^a-z0-9-]', '', slug.lower().replace(' ', '-'))
    slug = re.sub(r'-+', '-', slug).strip('-')
    if not slug:
        slug = f"article-{hash(title) % 100000}"
    result["slug"] = slug

    return result


def estimate_read_time(text: str) -> int:
    """Estimate reading time in minutes for Hebrew text (200 words/min)."""
    words = len(text.split())
    return max(1, round(words / 200))
