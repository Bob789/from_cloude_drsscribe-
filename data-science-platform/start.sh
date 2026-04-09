#!/bin/bash
set -e

echo "=== Starting FastAPI backend on :8000 ==="
uvicorn app_fastapi.app_fastapi:app --host 0.0.0.0 --port 8000 &
FASTAPI_PID=$!

echo "=== Waiting for FastAPI to be ready ==="
for i in $(seq 1 30); do
    if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
        echo "FastAPI ready after ${i}s"
        break
    fi
    sleep 1
done

echo "=== Starting Streamlit frontend on :8501 ==="
streamlit run app_streamlit/app_streamlit.py \
    --server.address=0.0.0.0 \
    --server.port=8501 \
    --server.headless=true \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false

# Streamlit exited — shut down FastAPI too
kill $FASTAPI_PID 2>/dev/null || true
