import base64
import hashlib
import hmac
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from app.config import settings


def _get_key() -> bytes:
    key_hex = settings.ENCRYPTION_KEY
    # Try proper hex-decode first (production: openssl rand -hex 32 → 64 hex chars = 32 bytes)
    try:
        key_bytes = bytes.fromhex(key_hex)
        if len(key_bytes) in (16, 24, 32):
            return key_bytes
    except (ValueError, AttributeError):
        pass
    # Fallback for non-hex keys: derive 32 bytes via SHA-256 (no weak zero-padding)
    return hashlib.sha256(key_hex.encode("utf-8")).digest()


def encrypt_field(value: str) -> str:
    if not value:
        return value
    key = _get_key()
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    encrypted = aesgcm.encrypt(nonce, value.encode("utf-8"), None)
    return base64.b64encode(nonce + encrypted).decode("utf-8")


def decrypt_field(encrypted_value: str) -> str:
    if not encrypted_value:
        return encrypted_value
    key = _get_key()
    data = base64.b64decode(encrypted_value)
    nonce = data[:12]
    ciphertext = data[12:]
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ciphertext, None).decode("utf-8")


def hash_field(value: str) -> str:
    if not value:
        return ""
    key = _get_key()
    return hmac.new(key, value.encode("utf-8"), hashlib.sha256).hexdigest()


# ── Audio file encryption (SEC-013) ──────────────────────────────────────────

def encrypt_audio(content: bytes) -> tuple[bytes, str]:
    """Encrypt raw audio bytes with a per-file DEK (AES-256-GCM).

    Returns:
        encrypted_bytes  – nonce(12) + ciphertext, to be stored in MinIO
        encrypted_dek    – DEK encrypted with the master key, to be stored in DB
    """
    dek = os.urandom(32)            # 256-bit per-file Data Encryption Key
    nonce = os.urandom(12)
    encrypted = AESGCM(dek).encrypt(nonce, content, None)
    encrypted_dek = encrypt_field(dek.hex())   # wrap DEK with master key
    return nonce + encrypted, encrypted_dek


def decrypt_audio(encrypted_content: bytes, encrypted_dek: str) -> bytes:
    """Decrypt audio bytes previously encrypted with encrypt_audio."""
    dek = bytes.fromhex(decrypt_field(encrypted_dek))   # unwrap DEK
    nonce = encrypted_content[:12]
    ciphertext = encrypted_content[12:]
    return AESGCM(dek).decrypt(nonce, ciphertext, None)
