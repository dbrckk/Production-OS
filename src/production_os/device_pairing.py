from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from .api_auth import Principal, token_digest


PAIRING_CODE_TTL_SECONDS = 600
DEVICE_SESSION_TTL_DAYS = 90
PAIRING_CODE_PREFIX = "posp_"
DEVICE_TOKEN_PREFIX = "posd_"


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _device_name(value: str | None) -> str:
    name = "dashboard-device" if value is None else str(value).strip()
    if not name:
        name = "dashboard-device"
    return name[:80]


class DevicePairingManager:
    def __init__(self, store):
        self.store = store

    def issue_pairing_code(
        self,
        *,
        requested_by: str,
        now: datetime | None = None,
    ) -> dict:
        issued_at = now or _now()
        self.store.prune_expired_device_auth(at=issued_at.isoformat())
        code = PAIRING_CODE_PREFIX + secrets.token_urlsafe(24)
        expires_at = issued_at + timedelta(seconds=PAIRING_CODE_TTL_SECONDS)
        row = self.store.create_pairing_code(
            code_sha256=token_digest(code),
            requested_by=str(requested_by),
            expires_at=expires_at.isoformat(),
            at=issued_at.isoformat(),
        )
        return {
            "code":code,
            "expires_at":row["expires_at"],
            "ttl_seconds":PAIRING_CODE_TTL_SECONDS,
        }

    def exchange(
        self,
        code: str,
        *,
        device_name: str | None = None,
        now: datetime | None = None,
    ) -> dict:
        value = str(code or "").strip()
        if not value.startswith(PAIRING_CODE_PREFIX) or len(value) > 256:
            raise ValueError("pairing code invalid or expired")

        issued_at = now or _now()
        self.store.prune_expired_device_auth(at=issued_at.isoformat())
        token = DEVICE_TOKEN_PREFIX + secrets.token_urlsafe(32)
        expires_at = issued_at + timedelta(days=DEVICE_SESSION_TTL_DAYS)
        session_id = uuid4().hex
        try:
            session = self.store.exchange_pairing_code(
                code_sha256=token_digest(value),
                session_id=session_id,
                token_sha256=token_digest(token),
                name=_device_name(device_name),
                role="operator",
                expires_at=expires_at.isoformat(),
                at=issued_at.isoformat(),
            )
        except KeyError as exc:
            raise ValueError("pairing code invalid or expired") from exc
        return {
            "session_token":token,
            "session_id":session["id"],
            "role":session["role"],
            "expires_at":session["expires_at"],
        }

    def authenticate(
        self,
        token: str | None,
        *,
        now: datetime | None = None,
    ) -> Principal | None:
        value = str(token or "").strip()
        if not value.startswith(DEVICE_TOKEN_PREFIX) or len(value) > 512:
            return None
        timestamp = (now or _now()).isoformat()
        session = self.store.device_session(
            token_sha256=token_digest(value),
            at=timestamp,
        )
        if session is None:
            return None
        role = str(session.get("role") or "")
        if role != "operator":
            return None
        return Principal(
            name="device:" + str(session["id"])[:12],
            role=role,
        )

    def revoke(self, token: str | None, *, now: datetime | None = None) -> bool:
        value = str(token or "").strip()
        if not value.startswith(DEVICE_TOKEN_PREFIX):
            return False
        return self.store.revoke_device_session(
            token_sha256=token_digest(value),
            at=(now or _now()).isoformat(),
        )

    def revoke_session(
        self,
        session_id: str,
        *,
        now: datetime | None = None,
    ) -> bool:
        value = str(session_id or "").strip()
        if not value or len(value) > 128:
            return False
        return self.store.revoke_device_session_by_id(
            session_id=value,
            at=(now or _now()).isoformat(),
        )

    def sessions(self, *, limit: int = 50) -> list[dict]:
        self.store.prune_expired_device_auth(at=_now().isoformat())
        return self.store.active_device_sessions(limit=limit)
