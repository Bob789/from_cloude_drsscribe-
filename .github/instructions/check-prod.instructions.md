---
description: "Check production health — all containers, logs, DB, Redis, disk, recent errors. Use when something feels wrong, after deploy, or for daily checkup."
---

# Production Health Check

Run a complete production health check across all services.

## Run these checks in parallel where possible:

### 1. Container status
```bash
docker compose -f docker-compose.prod.yml ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
```
All containers must show "Up" + "(healthy)" where applicable.

### 2. Backend health + readiness
```bash
curl -s https://app.drsscribe.com/api/health
curl -s https://app.drsscribe.com/api/ready
```
Ready endpoint checks: database, redis, S3 (MinIO), meilisearch.

### 3. Recent errors (last 20 log lines)
```bash
docker compose -f docker-compose.prod.yml logs backend --tail=20 2>&1 | grep -i -E "error|exception|traceback|critical"
docker compose -f docker-compose.prod.yml logs celery-worker --tail=20 2>&1 | grep -i -E "error|exception|traceback"
```

### 4. Database health
```bash
docker compose -f docker-compose.prod.yml exec -T postgres \
  psql -U drscribe -d drscribe -c "
    SELECT 'users' as tbl, count(*) FROM users
    UNION ALL SELECT 'visits', count(*) FROM visits
    UNION ALL SELECT 'recordings', count(*) FROM recordings
    UNION ALL SELECT 'transcriptions', count(*) FROM transcriptions
    UNION ALL SELECT 'summaries', count(*) FROM summaries;
  "
```

### 5. Redis health
```bash
docker compose -f docker-compose.prod.yml exec -T redis redis-cli -a \$REDIS_PASSWORD ping
docker compose -f docker-compose.prod.yml exec -T redis redis-cli -a \$REDIS_PASSWORD info memory | grep used_memory_human
```

### 6. Disk space
```bash
df -h / | tail -1
docker system df
```

### 7. SSL certificate expiry
```bash
echo | openssl s_client -connect app.drsscribe.com:443 -servername app.drsscribe.com 2>/dev/null | openssl x509 -noout -dates 2>/dev/null
```

### 8. Nginx access (recent 5xx errors)
```bash
docker compose -f docker-compose.prod.yml logs nginx --tail=50 2>&1 | grep -E '" [5][0-9]{2} '
```

## Report format
Present results as a clear status table:
| Service | Status | Notes |
|---------|--------|-------|
| Backend | OK/WARN/FAIL | details |
| ... | | |

Flag any WARN or FAIL items with recommended action.
