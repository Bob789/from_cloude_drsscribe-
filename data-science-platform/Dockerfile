FROM python:3.11-slim

WORKDIR /app

# curl needed in start.sh for FastAPI readiness check
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app_fastapi/ ./app_fastapi/
COPY app_streamlit/ ./app_streamlit/
COPY .streamlit/ ./.streamlit/
COPY sample_data/ ./sample_data/
COPY start.sh .

RUN chmod +x start.sh \
    && mkdir -p app_fastapi/data/uploads \
                app_fastapi/models/trained \
                app_fastapi/models/metadata \
                app_fastapi/logs

EXPOSE 8000 8501

CMD ["./start.sh"]
