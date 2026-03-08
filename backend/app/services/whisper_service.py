import asyncio
import httpx
from app.config import settings

MAX_RETRIES = 3
BACKOFF_BASE = 2


async def transcribe_audio(audio_data: bytes, filename: str = "audio.webm") -> dict:
    last_exc = None

    for attempt in range(MAX_RETRIES):
        try:
            async with httpx.AsyncClient(timeout=300.0) as client:
                response = await client.post(
                    settings.WHISPER_API_URL,
                    headers={"Authorization": f"Bearer {settings.WHISPER_API_KEY}"},
                    files={"file": (filename, audio_data, "audio/webm")},
                    data={
                        "model": settings.WHISPER_MODEL,
                        "language": "he",
                        "response_format": "verbose_json",
                        "timestamp_granularities[]": "segment",
                    },
                )
                response.raise_for_status()
                data = response.json()

                segments = []
                for seg in data.get("segments", []):
                    segments.append({
                        "start": seg.get("start", 0),
                        "end": seg.get("end", 0),
                        "text": seg.get("text", ""),
                        "speaker": "unknown",
                    })

                return {
                    "text": data.get("text", ""),
                    "segments": segments,
                    "language": data.get("language", "he"),
                    "confidence": _calc_confidence(data),
                }
        except httpx.HTTPStatusError as e:
            if e.response.status_code < 500:
                raise
            last_exc = e
        except (httpx.TimeoutException, httpx.ConnectError) as e:
            last_exc = e

        if attempt < MAX_RETRIES - 1:
            await asyncio.sleep(BACKOFF_BASE ** (attempt + 1))

    raise last_exc


def _calc_confidence(data: dict) -> float:
    segments = data.get("segments", [])
    if not segments:
        return 0.0
    avg = sum(s.get("avg_logprob", -1.0) for s in segments) / len(segments)
    return max(0.0, min(1.0, 1.0 + avg))
