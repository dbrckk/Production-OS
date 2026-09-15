from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .key_domains import assert_separate_key_domains


@dataclass(frozen=True)
class TrustPolicy:
    validator_keys: dict[str, Any]
    builder_keys: dict[str, Any]
    builder_private_key: str | None = None
    provenance_private_key: str | None = None
    witness_private_key: str | None = None
    strict_key_domains: bool = False

    def validate(self) -> dict[str, str]:
        if not self.strict_key_domains:
            return {}
        return assert_separate_key_domains(
            validator_keys=self.validator_keys,
            builder_keys=self.builder_keys,
            builder_private_key=self.builder_private_key,
            provenance_private_key=self.provenance_private_key,
            witness_private_key=self.witness_private_key,
        )

    @classmethod
    def create(
        cls,
        *,
        validator_keys: dict[str, Any] | None = None,
        builder_keys: dict[str, Any] | None = None,
        builder_private_key: str | None = None,
        provenance_private_key: str | None = None,
        witness_private_key: str | None = None,
        strict_key_domains: bool = False,
    ) -> "TrustPolicy":
        policy=cls(
            validator_keys=dict(validator_keys or {}),
            builder_keys=dict(builder_keys or {}),
            builder_private_key=builder_private_key,
            provenance_private_key=provenance_private_key,
            witness_private_key=witness_private_key,
            strict_key_domains=bool(strict_key_domains),
        )
        policy.validate()
        return policy
