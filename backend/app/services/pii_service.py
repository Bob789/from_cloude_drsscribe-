import re


PII_PATTERNS = [
    (r'\b\d{9}\b', 'ID_NUMBER'),
    (r'\b0[2-9]\d{7,8}\b', 'PHONE'),
    (r'\b05\d{8}\b', 'MOBILE'),
    (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 'EMAIL'),
    (r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', 'IP'),
]

POST_REDACT_PATTERNS = [
    (r'\b\d{9}\b', '[REDACTED_ID]'),
    (r'\b0[2-9]\d{7,8}\b', '[REDACTED_PHONE]'),
    (r'\b05\d{8}\b', '[REDACTED_PHONE]'),
    (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[REDACTED_EMAIL]'),
    (r'\bsk-[A-Za-z0-9]{20,}\b', '[REDACTED_KEY]'),
    (r'\bkey-[A-Za-z0-9]{20,}\b', '[REDACTED_KEY]'),
]


def mask_pii(text: str) -> tuple[str, dict]:
    pii_map = {}
    counter = 0

    for pattern, pii_type in PII_PATTERNS:
        matches = re.finditer(pattern, text)
        for match in matches:
            original = match.group()
            placeholder = f"[{pii_type}_{counter}]"
            pii_map[placeholder] = original
            text = text.replace(original, placeholder, 1)
            counter += 1

    return text, pii_map


def restore_pii(text: str, pii_map: dict) -> str:
    for placeholder, original in pii_map.items():
        text = text.replace(placeholder, original)
    return text


def post_redact(text: str) -> str:
    if not text:
        return text
    for pattern, replacement in POST_REDACT_PATTERNS:
        text = re.sub(pattern, replacement, text)
    return text


def post_redact_dict(data: dict, fields: list[str]) -> dict:
    for field in fields:
        if field in data and isinstance(data[field], str):
            data[field] = post_redact(data[field])
    if "diagnosis" in data and isinstance(data.get("diagnosis"), list):
        for diag in data["diagnosis"]:
            if isinstance(diag, dict) and "description" in diag:
                diag["description"] = post_redact(diag["description"])
    return data
