from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from .key_registry import KeyRegistryError, TrustedKeyRegistry


class BuilderIdentityError(ValueError):
    pass


def _parse_identity_time(
    value: str | None,
    field: str,
) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(
            str(value).replace("Z", "+00:00")
        )
    except ValueError as exc:
        raise BuilderIdentityError(
            f"invalid builder identity {field}"
        ) from exc
    if parsed.tzinfo is None:
        raise BuilderIdentityError(
            f"builder identity {field} must be timezone-aware"
        )
    return parsed


@dataclass(frozen=True)
class BuilderIdentity:
    builder_id: str
    key_owner: str
    allowed_repositories: tuple[str, ...] = ()
    not_before: str | None = None
    not_after: str | None = None

    @classmethod
    def from_dict(
        cls,
        builder_id: str,
        value: dict[str, Any],
    ) -> "BuilderIdentity":
        owner = str(value.get("key_owner") or builder_id)
        repositories = tuple(
            str(item)
            for item in value.get("allowed_repositories", [])
        )
        not_before = value.get("not_before")
        not_after = value.get("not_after")
        start = _parse_identity_time(not_before, "not_before")
        end = _parse_identity_time(not_after, "not_after")
        if start is not None and end is not None and start > end:
            raise BuilderIdentityError(
                "builder identity not_before must not be after not_after"
            )
        return cls(
            builder_id=str(builder_id),
            key_owner=owner,
            allowed_repositories=repositories,
            not_before=not_before,
            not_after=not_after,
        )

    def allows_repository(self, repository: str) -> bool:
        if not self.allowed_repositories:
            return True
        return repository in self.allowed_repositories


class BuilderTrustPolicy:
    def __init__(
        self,
        *,
        builders: dict[str, Any],
        signing_keys: dict[str, Any],
    ):
        self.builders = {
            str(builder_id):BuilderIdentity.from_dict(
                str(builder_id),
                dict(value or {}),
            )
            for builder_id, value in builders.items()
        }
        self.keys = TrustedKeyRegistry(signing_keys)

    def resolve(
        self,
        *,
        builder_id: str,
        key_id: str,
        repository: str,
        signed_at: str,
    ) -> str:
        identity = self.builders.get(str(builder_id))
        if identity is None:
            raise BuilderIdentityError("untrusted builder identity")
        if not identity.allows_repository(repository):
            raise BuilderIdentityError(
                "builder is not authorized for repository"
            )
        when = _parse_identity_time(signed_at, "signed_at")
        if when is None:
            raise BuilderIdentityError("builder identity signed_at is required")
        if identity.not_before:
            start = _parse_identity_time(
                identity.not_before, "not_before"
            )
            if when < start:
                raise BuilderIdentityError(
                    "builder identity is not active yet"
                )
        if identity.not_after:
            end = _parse_identity_time(
                identity.not_after, "not_after"
            )
            if when > end:
                raise BuilderIdentityError(
                    "builder identity has expired"
                )
        try:
            return self.keys.resolve(
                identity.key_owner,
                key_id,
                signed_at=signed_at,
            )
        except KeyRegistryError as exc:
            raise BuilderIdentityError(str(exc)) from exc
