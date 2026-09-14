from __future__ import annotations

import hashlib
import hmac
import json
from dataclasses import dataclass
from pathlib import Path


ROLE_LEVEL = {
    "viewer": 10,
    "worker": 20,
    "operator": 30,
    "admin": 40,
}


def token_digest(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class Principal:
    name: str
    role: str

    def allows(self, required_role: str) -> bool:
        return ROLE_LEVEL.get(self.role, 0) >= ROLE_LEVEL.get(required_role, 999)


class TokenAuthorizer:
    def __init__(self, entries: list[dict]):
        self.entries = entries

    @classmethod
    def load(cls, path: str | Path | None) -> "TokenAuthorizer":
        if not path:
            return cls([])
        source = Path(path)
        if not source.exists():
            raise FileNotFoundError(source)
        payload = json.loads(source.read_text(encoding="utf-8"))
        entries = payload.get("tokens", [])
        if not isinstance(entries, list):
            raise ValueError("auth config tokens must be a list")
        return cls(entries)

    def authenticate(self, token: str | None) -> Principal | None:
        if not token:
            return None
        digest = token_digest(token)
        for entry in self.entries:
            expected = str(entry.get("sha256", ""))
            if expected and hmac.compare_digest(digest, expected):
                role = str(entry.get("role", "viewer"))
                if role not in ROLE_LEVEL:
                    return None
                return Principal(
                    name=str(entry.get("name", "token")),
                    role=role,
                )
        return None
