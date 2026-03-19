#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────────
# generate_rsa_keys.sh — Generate RSA-2048 key pair for RS256 JWT signing
#
# Usage:
#   bash scripts/generate_rsa_keys.sh
#
# Output:
#   keys/jwt_private.pem   — private key (SIGN, keep secret!)
#   keys/jwt_public.pem    — public key  (VERIFY, safe to distribute)
#   Prints .env lines ready to paste
# ─────────────────────────────────────────────────────────────────────────────
set -e

KEYS_DIR="$(dirname "$0")/../keys"
mkdir -p "$KEYS_DIR"
chmod 700 "$KEYS_DIR"

PRIVATE_KEY="$KEYS_DIR/jwt_private.pem"
PUBLIC_KEY="$KEYS_DIR/jwt_public.pem"

echo "=== Generating RSA-2048 key pair ==="
openssl genrsa -out "$PRIVATE_KEY" 2048 2>/dev/null
chmod 600 "$PRIVATE_KEY"

openssl rsa -in "$PRIVATE_KEY" -pubout -out "$PUBLIC_KEY" 2>/dev/null
chmod 644 "$PUBLIC_KEY"

echo "Keys written to:"
echo "  Private: $PRIVATE_KEY"
echo "  Public:  $PUBLIC_KEY"
echo ""
echo "=== Add to your .env ==="
echo "JWT_ALGORITHM=RS256"
echo "JWT_PRIVATE_KEY=\"$(awk 'NF {sub(/\r/, ""); printf "%s\\n",$0;}' "$PRIVATE_KEY")\""
echo "JWT_PUBLIC_KEY=\"$(awk 'NF {sub(/\r/, ""); printf "%s\\n",$0;}' "$PUBLIC_KEY")\""
echo ""
echo "IMPORTANT: Never commit keys/ to git. Verify .gitignore includes keys/"
