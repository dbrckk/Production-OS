from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from .signing import key_id, load_private_key, sign_payload


class Signer(ABC):
    @property
    @abstractmethod
    def key_id(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def sign(self, payload: dict[str, Any]) -> dict[str, str]:
        raise NotImplementedError


class PemSigner(Signer):
    def __init__(self, private_key_pem: str):
        self.private_key_pem = private_key_pem
        private_key = load_private_key(private_key_pem)
        self._key_id = key_id(private_key.public_key())

    @property
    def key_id(self) -> str:
        return self._key_id

    def sign(self, payload: dict[str, Any]) -> dict[str, str]:
        return sign_payload(self.private_key_pem, payload)


def coerce_signer(
    *,
    signer: Signer | None = None,
    private_key_pem: str | None = None,
) -> Signer | None:
    if signer is not None:
        return signer
    if private_key_pem:
        return PemSigner(private_key_pem)
    return None
