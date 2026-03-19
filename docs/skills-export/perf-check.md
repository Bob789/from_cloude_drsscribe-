---
name: perf-check
description: "Diagnose performance issues — slow endpoints, DB queries, memory, container resources. Use when something is slow or before scaling."
---

# Performance Check — DoctorScribe Production

Diagnose and fix performance issues across the stack.

## Quick diagnostics (run in parallel)

### 1. Container resource usage
```bash
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
```
Red flags: CPU > 80%, Memory near limit (backend: 2GB, redis: 256MB)

### 2. Slow API endpoints
```bash
# Check nginx access logs for slow responses (> 2 seconds)
docker compose -f docker-compose.prod.yml logs nginx --tail=200 2>&1 | grep -oP 'upstream_response_time[=:]\K[0-9.]+' | awk '$1 > 2.0'
```

### 3. Database performance
```bash
docker compose -f docker-compose.prod.yml exec -T postgres \
  psql -U drscribe -d drscribe -c "
    -- Active queries (look for long-running)
    SELECT pid, now() - pg_stat_activity.query_start AS duration, query
    FROM pg_stat_activity
    WHERE state = 'active' AND query NOT LIKE '%pg_stat%'
    ORDER BY duration DESC LIMIT 5;
  "
```

```bash
docker compose -f docker-compose.prod.yml exec -T postgres \
  psql -U drscribe -d drscribe -c "
    -- Table sizes
    SELECT relname, pg_size_pretty(pg_total_relation_size(relid))
    FROM pg_catalog.pg_statio_user_tables
    ORDER BY pg_total_relation_size(relid) DESC LIMIT 10;
  "
```

```bash
docker compose -f docker-compose.prod.yml exec -T postgres \
  psql -U drscribe -d drscribe -c "
    -- Missing indexes (sequential scans on large tables)
    SELECT relname, seq_scan, idx_scan,
           CASE WHEN seq_scan > 0 THEN round(100.0 * idx_scan / (seq_scan + idx_scan)) ELSE 100 END AS idx_pct
    FROM pg_stat_user_tables
    WHERE seq_scan > 100
    ORDER BY seq_scan DESC LIMIT 10;
  "
```

### 4. Redis performance
```bash
docker compose -f docker-compose.prod.yml exec -T redis redis-cli -a $REDIS_PASSWORD info stats | grep -E "instantaneous_ops|used_memory|keyspace_hits|keyspace_misses"
```

### 5. Celery queue depth
```bash
docker compose -f docker-compose.prod.yml exec -T redis redis-cli -a $REDIS_PASSWORD llen celery
```
Queue > 10 means tasks are backing up.

### 6. Disk I/O
```bash
iostat -x 1 3 2>/dev/null || echo "iostat not available"
```

## Common fixes

### Slow DB queries
- Add missing indexes: `CREATE INDEX CONCURRENTLY`
- Use `.options(selectinload(...))` for relationships instead of lazy loading
- Add pagination (already exists: `offset/limit` pattern)
- Use `select(Model.id, Model.name)` instead of full model when you only need few columns

### High memory
- Check for unbounded result sets (missing `.limit()`)
- Ensure Celery tasks clean up large objects
- Redis: check for key bloat with `redis-cli --bigkeys`

### Slow transcription/summarization
- Check Celery worker logs for retry storms
- Check OpenAI API latency
- Verify concurrent task limit (prefetch=1, concurrency=4)

## Output
Present as a status dashboard with metrics and specific recommendations.
