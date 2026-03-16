#!/bin/bash
# Load secrets from Google Secret Manager into .env

PROJECT_ID="drscribe-prod-001"

get_secret() {
  gcloud secrets versions access latest --secret="$1" --project="$PROJECT_ID" 2>/dev/null | tr -d '\r\n\xef\xbb\xbf'
}

cat > /opt/drscribe/.env << EOF
# App
ENV_MODE=prod
APP_NAME=DoctorScribe
APP_VERSION=0.1.0
DEBUG=false

# Backend
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000

# Database
DB_HOST=postgres
DB_PORT=5432
DB_NAME=drscribe
DB_USER=drscribe
DB_PASSWORD=$(get_secret DB_PASSWORD)
DATABASE_URL=postgresql+asyncpg://drscribe:$(get_secret DB_PASSWORD)@postgres:5432/drscribe

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# JWT
JWT_SECRET=$(get_secret JWT_SECRET)
JWT_ACCESS_EXPIRE_MINUTES=30
JWT_REFRESH_EXPIRE_DAYS=7

# Google OAuth
GOOGLE_CLIENT_ID=$(get_secret GOOGLE_CLIENT_ID)
GOOGLE_CLIENT_SECRET=$(get_secret GOOGLE_CLIENT_SECRET)
GOOGLE_REDIRECT_URI=https://app.drsscribe.com/api/auth/google/callback
GOOGLE_CALENDAR_REDIRECT_URI=https://app.drsscribe.com/api/appointments/calendar/callback

# MinIO
S3_ENDPOINT=http://minio:9000
S3_PUBLIC_ENDPOINT=https://app.drsscribe.com/media
S3_ACCESS_KEY=$(get_secret S3_ACCESS_KEY)
S3_SECRET_KEY=$(get_secret S3_SECRET_KEY)
S3_BUCKET=drscribe-audio
S3_REGION=us-east-1

# OpenAI
WHISPER_API_URL=https://api.openai.com/v1/audio/transcriptions
WHISPER_API_KEY=$(get_secret OPENAI_API_KEY)
WHISPER_MODEL=whisper-1
OPENAI_API_KEY=$(get_secret OPENAI_API_KEY)
OPENAI_MODEL=gpt-4.1

# Meilisearch
MEILISEARCH_URL=http://meilisearch:7700
MEILISEARCH_KEY=$(get_secret MEILISEARCH_KEY)

# Encryption
ENCRYPTION_KEY=$(get_secret ENCRYPTION_KEY)

# Redis
REDIS_PASSWORD=$(get_secret REDIS_PASSWORD)

# MinIO Encryption
MINIO_ENCRYPTION_KEY=$(get_secret MINIO_ENCRYPTION_KEY)

# CORS
CORS_ORIGINS=https://drsscribe.com,https://app.drsscribe.com
EOF

echo "✅ .env נוצר בהצלחה"
chmod 600 /opt/drscribe/.env

