from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .key_domains import assert_separate_key_domains
from .signers import Signer


@dataclass(frozen=True)
class TrustPolicy:
    validator_keys: dict[str, Any]
    builder_keys: dict[str, Any]
    builder_private_key: str | None = None
    provenance_private_key: str | None = None
    witness_private_key: str | None = None
    builder_signer: Signer | None = None
    provenance_signer: Signer | None = None
    witness_signer: Signer | None = None
    strict_key_domains: bool = False

    def validate(self) -> dict[str, str]:
        if not self.strict_key_domains:
            return {}
        mapping = assert_separate_key_domains(
            validator_keys=self.validator_keys,
            builder_keys=self.builder_keys,
            builder_private_key=self.builder_private_key,
            provenance_private_key=self.provenance_private_key,
            witness_private_key=self.witness_private_key,
        )
        for domain, signer in (
            ("builder", self.builder_signer),
            ("provenance", self.provenance_signer),
            ("witness", self.witness_signer),
        ):
            if signer is None:
                continue
            previous = mapping.get(signer.key_id)
            if previous and previous != domain:
                from .key_domains import KeyDomainError
                raise KeyDomainError(
                    f"key {signer.key_id} reused across "
                    f"{previous} and {domain} domains"
                )
            mapping[signer.key_id] = domain
        return mapping

    @classmethod
    def create(
        cls,
        *,
        validator_keys: dict[str, Any] | None = None,
        builder_keys: dict[str, Any] | None = None,
        builder_private_key: str | None = None,
        provenance_private_key: str | None = None,
        witness_private_key: str | None = None,
        builder_signer: Signer | None = None,
        provenance_signer: Signer | None = None,
        witness_signer: Signer | None = None,
        strict_key_domains: bool = False,
    ) -> "TrustPolicy":
        policy=cls(
            validator_keys=dict(validator_keys or {}),
            builder_keys=dict(builder_keys or {}),
            builder_private_key=builder_private_key,
            provenance_private_key=provenance_private_key,
            witness_private_key=witness_private_key,
            builder_signer=builder_signer,
            provenance_signer=provenance_signer,
            witness_signer=witness_signer,
            strict_key_domains=bool(strict_key_domains),
        )
        policy.validate()
        return policy
