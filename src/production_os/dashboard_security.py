from __future__ import annotations

import re

_SENSITIVE_KEYS = {
    "authorization", "token", "api_key", "apikey", "secret", "password", "cookie"
}

_PATTERNS = (
    re.compile(r"(?i)(authorization\s*:\s*bearer\s+)[^\s,;]+"),
    re.compile(r"(?i)((?:api[_-]?key|token|password|secret)\s*[=:]\s*)[^\s,;]+"),
)


def _scrub_secret_patterns(value: str) -> str:
    for pattern in _PATTERNS:
        value = pattern.sub(r"\1[REDACTED]", value)
    return value


def redact_log_value(value: object) -> object:
    if isinstance(value, dict):
        return {
            str(key): (
                "[REDACTED]"
                if str(key).lower() in _SENSITIVE_KEYS
                else redact_log_value(child)
            )
            for key, child in value.items()
        }
    if isinstance(value, list):
        return [redact_log_value(child) for child in value]
    if isinstance(value, tuple):
        return tuple(redact_log_value(child) for child in value)
    if isinstance(value, str):
        return _scrub_secret_patterns(value)
    return value
