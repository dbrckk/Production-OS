from __future__ import annotations

from typing import Any

from .key_registry import TrustedKeyRegistry
from .signing import key_id, load_private_key


class KeyDomainError(ValueError):
    pass


def private_key_id(private_key_pem: str | None) -> str | None:
    if not private_key_pem:
        return None
    private_key = load_private_key(private_key_pem)
    return key_id(private_key.public_key())


def registry_key_ids(entries: dict[str, Any] | None) -> set[str]:
    registry = TrustedKeyRegistry(dict(entries or {}))
    return {
        item.key_id
        for keys in registry.by_owner.values()
        for item in keys.values()
    }


def assert_separate_key_domains(
    *,
    validator_keys: dict[str, Any] | None = None,
    builder_keys: dict[str, Any] | None = None,
    builder_private_key: str | None = None,
    provenance_private_key: str | None = None,
    witness_private_key: str | None = None,
) -> dict[str, str]:
    domains: dict[str, set[str]] = {
        "validator":registry_key_ids(validator_keys),
        "builder":registry_key_ids(builder_keys),
    }
    for domain, pem in (
        ("builder", builder_private_key),
        ("provenance", provenance_private_key),
        ("witness", witness_private_key),
    ):
        value = private_key_id(pem)
        if value:
            domains.setdefault(domain, set()).add(value)

    owners: dict[str, str] = {}
    for domain, values in domains.items():
        for value in values:
            previous = owners.get(value)
            if previous and previous != domain:
                raise KeyDomainError(
                    f"key {value} reused across "
                    f"{previous} and {domain} domains"
                )
            owners[value] = domain
    return {
        value:domain
        for value, domain in owners.items()
    }
