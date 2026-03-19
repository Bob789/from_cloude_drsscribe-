import time
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from fastapi import FastAPI

REQUEST_COUNT = Counter("http_requests_total", "Total HTTP requests", ["method", "endpoint", "status"])
REQUEST_LATENCY = Histogram("http_request_duration_seconds", "HTTP request latency", ["method", "endpoint"])
ACTIVE_REQUESTS = Gauge("http_active_requests", "Active HTTP requests")
STT_DURATION = Histogram("stt_processing_seconds", "Speech-to-text processing duration")
LLM_DURATION = Histogram("llm_processing_seconds", "LLM summarization duration")
ERROR_COUNT = Counter("error_total", "Total errors", ["type"])


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        ACTIVE_REQUESTS.inc()
        start_time = time.time()
        try:
            response = await call_next(request)
            duration = time.time() - start_time
            endpoint = request.url.path
            REQUEST_COUNT.labels(request.method, endpoint, response.status_code).inc()
            REQUEST_LATENCY.labels(request.method, endpoint).observe(duration)
            return response
        except Exception as e:
            ERROR_COUNT.labels(type(e).__name__).inc()
            raise
        finally:
            ACTIVE_REQUESTS.dec()


def setup_metrics(app: FastAPI):
    app.add_middleware(MetricsMiddleware)

    @app.get("/metrics")
    async def metrics():
        return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
