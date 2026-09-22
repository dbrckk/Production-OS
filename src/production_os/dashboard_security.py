from __future__ import annotations

import re


_SENSITIVE_KEYS = {
    "authorization",
    "token",
    "api_key",
    "apikey",
    "secret",
    "password",
    "cookie",
}

_AUTH_BEARER_RE = re.compile(
    r"(?i)(Authorization\s*:\s*Bearer\s+)([^\s,;]+)"
)
_BEARER_RE = re.compile(r"(?i)\bBearer\s+([A-Za-z0-9._~+/-]{12,})")
_SK_RE = re.compile(r"\bsk-[A-Za-z0-9_-]{6,}\b")
_COOKIE_RE = re.compile(r"(?i)\bcookie\s*=\s*([^;\s]+)")


def _scrub_secret_patterns(value: str) -> str:
    value = _AUTH_BEARER_RE.sub(r"\1[REDACTED]", value)
    value = _BEARER_RE.sub("Bearer [REDACTED]", value)
    value = _SK_RE.sub("[REDACTED]", value)
    value = _COOKIE_RE.sub("cookie=[REDACTED]", value)
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
