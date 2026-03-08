#!/bin/bash
set -e

DOMAIN=${1:-"localhost"}
EMAIL=${2:-"admin@example.com"}

echo "Setting up SSL for domain: $DOMAIN"

if command -v certbot &> /dev/null; then
    certbot certonly --standalone \
        -d "$DOMAIN" \
        --email "$EMAIL" \
        --agree-tos \
        --non-interactive
    echo "Certificate obtained for $DOMAIN"
    echo "Certificate: /etc/letsencrypt/live/$DOMAIN/fullchain.pem"
    echo "Key: /etc/letsencrypt/live/$DOMAIN/privkey.pem"
else
    echo "Certbot not installed. Installing..."
    apt-get update && apt-get install -y certbot
    echo "Run this script again after installation"
fi
