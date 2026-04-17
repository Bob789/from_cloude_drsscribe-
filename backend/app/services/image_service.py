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


async def generate_with_gpt_image(topic: str, category: str) -> dict | None:
    """
    Generate a photorealistic editorial image with gpt-image-1.
    Prompt is crafted to produce stock-photo look, no AI artifacts.
    Returns {"url": <data-url or minio-url>, "alt": ..., "attribution": "AI generated"}
    """
    try:
        from openai import AsyncOpenAI
        from app.config import settings
        api_key = getattr(settings, 'OPENAI_API_KEY', '')
        if not api_key:
            return None

        client = AsyncOpenAI(api_key=api_key)

        # Photorealistic prompt — avoids illustrative / "AI art" look
        prompt = (
            f"Photorealistic editorial photograph, natural lighting, "
            f"shot on Canon EOS R5 with 35mm f/2.8 lens, shallow depth of field, "
            f"documentary medical photography style. "
            f"Subject matter: {topic}. Medical domain: {category}. "
            f"Clean professional composition, warm tones, honest and human. "
            f"No text, no watermarks, no synthetic or illustrated look."
        )

        resp = await client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size="1024x1024",
            quality="high",
            n=1,
        )

        import base64, uuid, io, httpx
        from app.services.storage_service import get_minio_client

        b64 = resp.data[0].b64_json
        if not b64:
            return None

        image_bytes = base64.b64decode(b64)

        # Upload to MinIO and return a persistent URL
        try:
            minio = get_minio_client()
            object_name = f"article-images/{uuid.uuid4()}.jpg"
            bucket = getattr(settings, 'MINIO_BUCKET', 'drscribe-audio')

            from minio.commonconfig import ENABLED
            import minio as minio_pkg
            from io import BytesIO

            minio.put_object(
                bucket, object_name,
                BytesIO(image_bytes), len(image_bytes),
                content_type="image/jpeg",
            )
            # Build public URL (MinIO or S3-compatible)
            minio_endpoint = getattr(settings, 'MINIO_ENDPOINT', 'minio:9000')
            url = f"http://{minio_endpoint}/{bucket}/{object_name}"
            return {"url": url, "alt": topic, "attribution": "AI generated"}
        except Exception as upload_err:
            logger.warning("gpt_image_minio_upload_failed", error=str(upload_err))
            # Fallback: return as base64 data-URL (works but heavy)
            data_url = f"data:image/jpeg;base64,{b64}"
            return {"url": data_url, "alt": topic, "attribution": "AI generated"}

    except Exception as e:
        logger.error("gpt_image_error", error=str(e))
        return None


async def find_hero_image(topic: str, category: str = "general") -> dict | None:
    """
    Find/generate a hero image for an article.
    Priority: gpt-image-1 → Unsplash → Pexels → generic fallback.
    """
    search_term = CATEGORY_IMAGE_TERMS.get(category, "medical health")

    # Primary: generate with gpt-image-1 (photorealistic, topic-specific)
    result = await generate_with_gpt_image(topic, category)
    if result:
        return result

    # Fallback 1: Unsplash stock photo
    result = await search_unsplash(f"{search_term} {topic}")
    if result:
        return result

    # Fallback 2: Pexels
    result = await search_pexels(f"{search_term} {topic}")
    if result:
        return result

    # Fallback 3: generic medical image
    return await search_unsplash("medical healthcare professional")
