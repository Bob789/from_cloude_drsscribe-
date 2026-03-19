#!/bin/bash
set -e

BACKUP_DIR="/backups/$(date +%Y-%m-%d)"
RETENTION_DAYS=30

mkdir -p "$BACKUP_DIR"

echo "=== MedScribe AI Backup ==="
echo "Date: $(date)"
echo "Backup dir: $BACKUP_DIR"

echo "1. Backing up PostgreSQL..."
docker exec medscribe-postgres pg_dump -U medscribe medscribe | gzip > "$BACKUP_DIR/db_backup.sql.gz"
echo "   DB backup: $(du -h "$BACKUP_DIR/db_backup.sql.gz" | cut -f1)"

echo "2. Syncing S3/MinIO audio files..."
docker exec medscribe-minio mc alias set local http://localhost:9000 minioadmin "$S3_SECRET_KEY"
docker exec medscribe-minio mc mirror local/medscribe-audio "/backups/audio/" 2>/dev/null || true
echo "   Audio sync complete"

echo "3. Backing up config files..."
cp .env "$BACKUP_DIR/env.bak" 2>/dev/null || true
cp docker-compose.yml "$BACKUP_DIR/docker-compose.yml.bak"
cp nginx/nginx.conf "$BACKUP_DIR/nginx.conf.bak"

echo "4. Cleaning old backups (>${RETENTION_DAYS} days)..."
find /backups -maxdepth 1 -type d -mtime +${RETENTION_DAYS} -exec rm -rf {} \; 2>/dev/null || true

echo "=== Backup complete ==="
