from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from .signing import key_id, load_public_key


class KeyRegistryError(ValueError):
    pass


def _parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(
            str(value).replace("Z", "+00:00")
        )
    except ValueError as exc:
        raise KeyRegistryError("invalid key validity timestamp") from exc
    if parsed.tzinfo is None:
        raise KeyRegistryError(
            "key validity timestamp must be timezone-aware"
        )
    return parsed


@dataclass(frozen=True)
class TrustedKey:
    owner: str
    public_key: str
    key_id: str
    not_before: datetime | None = None
    not_after: datetime | None = None
    revoked_at: datetime | None = None

    @classmethod
    def from_dict(
        cls,
        owner: str,
        payload: dict[str, Any],
    ) -> "TrustedKey":
        public_key = str(payload.get("public_key") or "")
        if not public_key:
            raise KeyRegistryError("public_key is required")
        computed = key_id(load_public_key(public_key))
        supplied = str(payload.get("key_id") or computed)
        if supplied != computed:
            raise KeyRegistryError("key_id does not match public key")
        return cls(
            owner=str(owner),
            public_key=public_key,
            key_id=computed,
            not_before=_parse_time(payload.get("not_before")),
            not_after=_parse_time(payload.get("not_after")),
            revoked_at=_parse_time(payload.get("revoked_at")),
        )

    def usable_at(self, when: datetime) -> tuple[bool, str | None]:
        if self.not_before and when < self.not_before:
            return False, "signing key is not active yet"
        if self.not_after and when > self.not_after:
            return False, "signing key has expired"
        if self.revoked_at and when >= self.revoked_at:
            return False, "signing key is revoked"
        return True, None


class TrustedKeyRegistry:
    def __init__(self, entries: dict[str, Any] | None = None):
        self.by_owner: dict[str, dict[str, TrustedKey]] = {}
        for owner, value in dict(entries or {}).items():
            rows = value if isinstance(value, list) else [value]
            for row in rows:
                if isinstance(row, str):
                    row = {"public_key":row}
                if not isinstance(row, dict):
                    raise KeyRegistryError(
                        "key registry entries must be objects"
                    )
                item = TrustedKey.from_dict(str(owner), row)
                self.by_owner.setdefault(
                    str(owner), {}
                )[item.key_id] = item

    def resolve(
        self,
        owner: str,
        key_id_value: str,
        *,
        signed_at: str,
    ) -> str:
        item = self.by_owner.get(str(owner), {}).get(
            str(key_id_value)
        )
        if item is None:
            raise KeyRegistryError("untrusted signing key")
        when = _parse_time(signed_at)
        if when is None:
            raise KeyRegistryError("signed_at is required")
        usable, reason = item.usable_at(when)
        if not usable:
            raise KeyRegistryError(str(reason))
        return item.public_key
