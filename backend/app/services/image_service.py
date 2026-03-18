"""
Image service for fetching stock medical images from Unsplash/Pexels.
"""

import httpx
import structlog
from app.config import settings

logger = structlog.get_logger()

UNSPLASH_API = "https://api.unsplash.com"
PEXELS_API = "https://api.pexels.com/v1"

# Medical image search terms mapping (Hebrew category -> English search)
CATEGORY_IMAGE_TERMS = {
    "cardiology": "heart health medical",
    "neurology": "brain neuroscience",
    "orthopedics": "physical therapy bones",
    "nutrition": "healthy food diet",
    "sleep": "sleep wellness",
    "mental": "mental health meditation",
    "general": "medical health wellness",
    "dermatology": "skin care dermatology",
    "gastroenterology": "digestive health",
    "urology": "medical healthcare",
    "ophthalmology": "eye health vision",
    "pulmonology": "breathing respiratory",
}


async def search_unsplash(query: str) -> dict | None:
    """Search Unsplash for a medical image."""
    key = getattr(settings, 'UNSPLASH_ACCESS_KEY', '')
    if not key:
        return None

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                f"{UNSPLASH_API}/search/photos",
                params={"query": query, "per_page": 1, "orientation": "landscape"},
                headers={"Authorization": f"Client-ID {key}"},
            )
            if resp.status_code != 200:
                logger.warning("unsplash_search_failed", status=resp.status_code)
                return None
            data = resp.json()
            results = data.get("results", [])
            if not results:
                return None
            photo = results[0]
            return {
                "url": photo["urls"]["regular"],
                "alt": photo.get("alt_description") or query,
                "attribution": f"Photo by {photo['user']['name']} on Unsplash",
            }
    except Exception as e:
        logger.error("unsplash_error", error=str(e))
        return None


async def search_pexels(query: str) -> dict | None:
    """Search Pexels for a medical image."""
    key = getattr(settings, 'PEXELS_API_KEY', '')
    if not key:
        return None

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                f"{PEXELS_API}/search",
                params={"query": query, "per_page": 1, "orientation": "landscape"},
                headers={"Authorization": key},
            )
            if resp.status_code != 200:
                return None
            data = resp.json()
            photos = data.get("photos", [])
            if not photos:
                return None
            photo = photos[0]
            return {
                "url": photo["src"]["large"],
                "alt": photo.get("alt") or query,
                "attribution": f"Photo by {photo['photographer']} on Pexels",
            }
    except Exception as e:
        logger.error("pexels_error", error=str(e))
        return None


async def find_hero_image(topic: str, category: str = "general") -> dict | None:
    """Find a hero image for an article. Tries Unsplash first, then Pexels."""
    search_term = CATEGORY_IMAGE_TERMS.get(category, "medical health")

    # Try Unsplash first
    result = await search_unsplash(f"{search_term} {topic}")
    if result:
        return result

    # Fallback to Pexels
    result = await search_pexels(f"{search_term} {topic}")
    if result:
        return result

    # Fallback to generic medical image
    result = await search_unsplash("medical healthcare professional")
    return result
