AUDIO_SIGNATURES = {
    b"RIFF": "wav",
    b"fLaC": "flac",
    b"OggS": "ogg",
    b"\x1aE\xdf\xa3": "webm",
    b"\xff\xfb": "mp3",
    b"\xff\xf3": "mp3",
    b"\xff\xf2": "mp3",
    b"ID3": "mp3",
}

MAX_FILE_SIZE = 500 * 1024 * 1024


def validate_audio_file(content: bytes, filename: str = "") -> tuple[bool, str]:
    if not content:
        return False, "Empty file"

    if len(content) > MAX_FILE_SIZE:
        return False, f"File too large ({len(content)} bytes, max {MAX_FILE_SIZE})"

    detected_format = None
    for signature, fmt in AUDIO_SIGNATURES.items():
        if content[:len(signature)] == signature:
            detected_format = fmt
            break

    if detected_format is None:
        return False, "Not a valid audio file (unknown magic bytes)"

    return True, detected_format


def validate_content_type(content_type: str) -> bool:
    allowed = {"audio/webm", "audio/wav", "audio/x-wav", "audio/flac", "audio/ogg", "audio/mpeg", "audio/mp3"}
    return content_type in allowed


ALLOWED_DOCUMENT_TYPES = {
    "application/pdf": ".pdf",
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/gif": ".gif",
    "image/webp": ".webp",
    "application/msword": ".doc",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
    "application/dicom": ".dcm",
}
MAX_DOCUMENT_SIZE = 50 * 1024 * 1024


DOCUMENT_SIGNATURES = {
    b"%PDF": "pdf",
    b"\xff\xd8\xff": "jpg",
    b"\x89PNG": "png",
    b"GIF8": "gif",
    b"RIFF": "webp",
    b"\xd0\xcf\x11\xe0": "doc",
    b"PK\x03\x04": "docx",
}


def validate_document_file(content: bytes, filename: str = "") -> tuple[bool, str]:
    if not content:
        return False, "Empty file"
    if len(content) > MAX_DOCUMENT_SIZE:
        return False, f"File too large ({len(content)} bytes, max {MAX_DOCUMENT_SIZE})"
    for signature, fmt in DOCUMENT_SIGNATURES.items():
        if content[:len(signature)] == signature:
            return True, fmt
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext in {"pdf", "jpg", "jpeg", "png", "gif", "webp", "doc", "docx", "dcm"}:
        return True, ext
    return False, "Unknown file type"
