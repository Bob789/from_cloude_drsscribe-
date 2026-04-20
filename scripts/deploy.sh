#!/bin/bash
set -e

echo "=== MedScribe AI Production Deployment ==="
echo "Date: $(date)"

if [ ! -f .env ]; then
    echo "ERROR: .env file not found. Copy .env.example and configure."
    exit 1
fi

echo "0. Securing .env permissions..."
chmod 600 .env
chown "$(whoami):$(whoami)" .env
echo "   .env: permissions set to 600"

echo "1. Pulling latest code..."
git pull origin main

echo "2. Building Docker images..."
docker-compose -f docker-compose.prod.yml build --no-cache

echo "3. Running database migrations..."
docker-compose -f docker-compose.prod.yml run --rm backend alembic upgrade head

echo "4. Starting services..."
docker-compose -f docker-compose.prod.yml up -d

echo "4b. Starting dev-tools (cpanel)..."
docker-compose -f docker-compose.prod.yml up -d dev-tools

echo "5. Waiting for services to start..."
sleep 10

echo "6. Health check..."
HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/api/health)
if [ "$HEALTH" = "200" ]; then
    echo "   Backend: OK"
else
    echo "   Backend: FAILED (HTTP $HEALTH)"
    echo "   Check logs: docker-compose -f docker-compose.prod.yml logs backend"
    exit 1
fi

DEV_TOOLS_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8090/health)
if [ "$DEV_TOOLS_HEALTH" = "200" ]; then
    echo "   Dev-Tools: OK"
else
    echo "   Dev-Tools: WARN (HTTP $DEV_TOOLS_HEALTH) — cpanel may not work"
fi

echo "7. Checking all services..."
docker-compose -f docker-compose.prod.yml ps

echo "=== Deployment complete ==="
echo "Access: http://$(hostname -f)"
