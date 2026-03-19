import anthropic
from app.config import settings

_embeddings_cache: dict[str, list[float]] = {}


async def generate_embedding(text: str) -> list[float]:
    if text in _embeddings_cache:
        return _embeddings_cache[text]

    client = anthropic.AsyncAnthropic(api_key=settings.CLAUDE_API_KEY)

    try:
        import httpx
        async with httpx.AsyncClient() as http_client:
            response = await http_client.post(
                "https://api.openai.com/v1/embeddings",
                headers={"Authorization": f"Bearer {settings.WHISPER_API_KEY}"},
                json={"input": text[:8000], "model": "text-embedding-3-small"},
            )
            response.raise_for_status()
            data = response.json()
            embedding = data["data"][0]["embedding"]
            _embeddings_cache[text] = embedding
            return embedding
    except Exception:
        return [0.0] * 1536


async def semantic_search(query: str, documents: list[dict], top_k: int = 10) -> list[dict]:
    query_embedding = await generate_embedding(query)

    scored = []
    for doc in documents:
        doc_text = doc.get("text", "")
        doc_embedding = await generate_embedding(doc_text[:500])
        similarity = _cosine_similarity(query_embedding, doc_embedding)
        scored.append({**doc, "score": similarity})

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_k]


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    if len(a) != len(b) or not a:
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = sum(x * x for x in a) ** 0.5
    mag_b = sum(x * x for x in b) ** 0.5
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)
