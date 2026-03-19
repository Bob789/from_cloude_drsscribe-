---
description: "Backup or restore the database and configuration. Use before risky operations, periodically, or when something goes wrong."
---

# Backup & Restore — DoctorScribe Production

## Backup

### Quick backup (database only)
```bash
BACKUP_DIR="/opt/drscribe/backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
docker compose -f docker-compose.prod.yml exec -T postgres \
  pg_dump -U drscribe -d drscribe --format=custom \
  > "$BACKUP_DIR/drscribe.dump"
echo "Backup saved to $BACKUP_DIR/drscribe.dump"
ls -lh "$BACKUP_DIR/drscribe.dump"
```

### Full backup (DB + config + audio)
```bash
BACKUP_DIR="/opt/drscribe/backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Database
docker compose -f docker-compose.prod.yml exec -T postgres \
  pg_dump -U drscribe -d drscribe --format=custom \
  > "$BACKUP_DIR/drscribe.dump"

# Config files
cp /opt/drscribe/.env "$BACKUP_DIR/env.bak" 2>/dev/null
cp /opt/drscribe/docker-compose.prod.yml "$BACKUP_DIR/"
cp /opt/drscribe/nginx/nginx.conf "$BACKUP_DIR/"

echo "Full backup completed: $BACKUP_DIR"
ls -lh "$BACKUP_DIR/"
```

### List existing backups
```bash
ls -lhd /opt/drscribe/backups/*/ 2>/dev/null || echo "No backups found"
```

## Restore

### BEFORE RESTORING — always confirm with user!

### Restore database from backup
```bash
# DANGEROUS — will replace current data
BACKUP_FILE="/opt/drscribe/backups/YYYYMMDD_HHMMSS/drscribe.dump"

# Terminate existing connections
docker compose -f docker-compose.prod.yml exec -T postgres \
  psql -U drscribe -d postgres -c "
    SELECT pg_terminate_backend(pid) FROM pg_stat_activity
    WHERE datname = 'drscribe' AND pid <> pg_backend_pid();
  "

# Drop and recreate
docker compose -f docker-compose.prod.yml exec -T postgres \
  psql -U drscribe -d postgres -c "DROP DATABASE drscribe; CREATE DATABASE drscribe OWNER drscribe;"

# Restore
docker compose -f docker-compose.prod.yml exec -T postgres \
  pg_restore -U drscribe -d drscribe < "$BACKUP_FILE"

# Restart backend
docker compose -f docker-compose.prod.yml restart backend celery-worker
```

## Rules
- ALWAYS backup before destructive operations (DROP TABLE, schema changes)
- ALWAYS confirm with the user before restoring
- Keep at least 3 recent backups
- Clean backups older than 30 days: `find /opt/drscribe/backups -maxdepth 1 -mtime +30 -exec rm -rf {} \;`
