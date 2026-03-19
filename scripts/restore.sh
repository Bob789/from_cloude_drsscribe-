#!/bin/bash
set -e

BACKUP_DIR=${1:?"Usage: restore.sh <backup_dir>"}

if [ ! -d "$BACKUP_DIR" ]; then
    echo "Error: Backup directory not found: $BACKUP_DIR"
    exit 1
fi

echo "=== MedScribe AI Restore ==="
echo "Restoring from: $BACKUP_DIR"

read -p "This will overwrite the current database. Continue? (y/N) " confirm
if [ "$confirm" != "y" ]; then
    echo "Aborted."
    exit 0
fi

echo "1. Restoring PostgreSQL..."
if [ -f "$BACKUP_DIR/db_backup.sql.gz" ]; then
    gunzip -c "$BACKUP_DIR/db_backup.sql.gz" | docker exec -i medscribe-postgres psql -U medscribe medscribe
    echo "   DB restored"
else
    echo "   No DB backup found, skipping"
fi

echo "2. Restoring config files..."
[ -f "$BACKUP_DIR/env.bak" ] && cp "$BACKUP_DIR/env.bak" .env
[ -f "$BACKUP_DIR/nginx.conf.bak" ] && cp "$BACKUP_DIR/nginx.conf.bak" nginx/nginx.conf

echo "3. Restarting services..."
docker-compose restart

echo "=== Restore complete ==="
