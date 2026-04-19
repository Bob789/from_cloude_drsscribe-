"""Mistral pipeline diagnostic."""
import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app.config import settings
from app.services.review_service import review_article, fix_article_with_gpt

BAD = "# Headache\n\nIt happens. Take a pill. End.\n"

def hr(label=""):
    print("\n" + "="*70)
    if label: print("  " + label); print("="*70)

async def main():
    hr("STEP 1: Configuration")
    print("MISTRAL_API_KEY set:        " + str(bool(settings.MISTRAL_API_KEY)))
    print("MISTRAL_REVIEW_MODEL:       " + str(settings.MISTRAL_REVIEW_MODEL))
    print("OPENAI_API_KEY set:         " + str(bool(settings.OPENAI_API_KEY)))
    print("ARTICLE_QUALITY_THRESHOLD:  " + str(settings.ARTICLE_QUALITY_THRESHOLD))
    if not settings.MISTRAL_API_KEY:
        print("MISTRAL_API_KEY missing - stopping."); return

    hr("STEP 2: Review BAD article (expect low score)")
    r1 = await review_article(title="Headache", content_markdown=BAD)
    for k in ("expired","skipped","total_score","structure_score","completeness_score","responsibility_score","language_score","factual_score","logic_style_score","safety_score","issues","strengths"):
        print(f"  {k:18s}: {r1.get(k)}")
    if r1.get("expired"): print("KEY EXPIRED - stop"); return
    if r1.get("skipped"): print("SKIPPED - stop"); return
    s1 = r1.get("total_score") or 0

    hr("STEP 3: GPT fix")
    issues = r1.get("issues") or ["Too short","No disclaimer","No when-to-see-doctor"]
    fx = await fix_article_with_gpt(title="Headache", content_markdown=BAD, issues=issues)
    if not fx or not fx.get("content_markdown"):
        print("GPT fix empty - check OPENAI_API_KEY"); return
    print(f"GPT returned {len(fx.get('content_markdown',''))} chars")
    print(f"new title: {fx.get('title','')[:80]}")

    hr("STEP 4: Re-review FIXED article")
    r2 = await review_article(title=fx.get("title","Headache"), content_markdown=fx.get("content_markdown",""))
    s2 = r2.get("total_score") or 0
    print(f"  total_score: {s2}/100  (was {s1}/100)  delta: {s2-s1:+d}")
    print(f"  issues:      {r2.get('issues')}")

    hr("RESULT")
    if s2 > s1: print(f"OK pipeline works  {s1} -> {s2}")
    elif s2 == s1: print(f"WARN same score {s2}")
    else: print(f"FAIL score dropped {s1} -> {s2}")
    if s2 >= settings.ARTICLE_QUALITY_THRESHOLD:
        print(f"OK >= threshold {settings.ARTICLE_QUALITY_THRESHOLD} -> would auto-publish")
    else:
        print(f"INFO < threshold -> would save as DRAFT")

if __name__ == "__main__":
    asyncio.run(main())