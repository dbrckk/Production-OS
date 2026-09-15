from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from .key_registry import KeyRegistryError, TrustedKeyRegistry


class BuilderIdentityError(ValueError):
    pass


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
        return cls(
            builder_id=str(builder_id),
            key_owner=owner,
            allowed_repositories=repositories,
            not_before=value.get("not_before"),
            not_after=value.get("not_after"),
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
        when = datetime.fromisoformat(
            signed_at.replace("Z", "+00:00")
        )
        if identity.not_before:
            start = datetime.fromisoformat(
                identity.not_before.replace("Z", "+00:00")
            )
            if when < start:
                raise BuilderIdentityError(
                    "builder identity is not active yet"
                )
        if identity.not_after:
            end = datetime.fromisoformat(
                identity.not_after.replace("Z", "+00:00")
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
