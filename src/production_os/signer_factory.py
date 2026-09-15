from __future__ import annotations

import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .signers import PemSigner, Signer


class SignerConfigurationError(ValueError):
    pass


class RemoteSignerError(RuntimeError):
    pass


class RemoteHttpSigner(Signer):
    def __init__(
        self,
        *,
        endpoint: str,
        signing_key_id: str,
        bearer_token: str | None = None,
        timeout_seconds: float = 10.0,
    ):
        if not endpoint.startswith(("https://", "http://")):
            raise SignerConfigurationError(
                "remote signer endpoint must be HTTP(S)"
            )
        if not signing_key_id:
            raise SignerConfigurationError(
                "remote signer key_id is required"
            )
        self.endpoint=endpoint
        self._key_id=signing_key_id
        self.bearer_token=bearer_token
        self.timeout_seconds=float(timeout_seconds)

    @property
    def key_id(self) -> str:
        return self._key_id

    def sign(self, payload: dict[str, Any]) -> dict[str, str]:
        body=json.dumps(
            {
                "key_id":self.key_id,
                "payload":payload,
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        headers={
            "Content-Type":"application/json",
            "Accept":"application/json",
        }
        if self.bearer_token:
            headers["Authorization"]=(
                f"Bearer {self.bearer_token}"
            )
        request=Request(
            self.endpoint,
            data=body,
            headers=headers,
            method="POST",
        )
        try:
            with urlopen(
                request,
                timeout=self.timeout_seconds,
            ) as response:
                if response.status < 200 or response.status >= 300:
                    raise RemoteSignerError(
                        f"remote signer returned HTTP {response.status}"
                    )
                result=json.loads(response.read())
        except (
            HTTPError,
            URLError,
            TimeoutError,
            json.JSONDecodeError,
        ) as exc:
            raise RemoteSignerError(
                f"remote signing failed: {exc}"
            ) from exc
        if not isinstance(result, dict):
            raise RemoteSignerError(
                "remote signer response must be an object"
            )
        signature=dict(result.get("signature") or result)
        if signature.get("key_id") != self.key_id:
            raise RemoteSignerError(
                "remote signer key_id mismatch"
            )
        if signature.get("algorithm") != "ed25519":
            raise RemoteSignerError(
                "remote signer algorithm mismatch"
            )
        if not signature.get("signature"):
            raise RemoteSignerError(
                "remote signer returned no signature"
            )
        return {
            "algorithm":"ed25519",
            "key_id":self.key_id,
            "signature":str(signature["signature"]),
        }


def create_signer(
    uri: str,
    *,
    pem_value: str | None = None,
    key_id: str | None = None,
    bearer_token: str | None = None,
    timeout_seconds: float = 10.0,
) -> Signer:
    value=str(uri or "").strip()
    if value == "pem:":
        if not pem_value:
            raise SignerConfigurationError(
                "pem signer requires private key material"
            )
        return PemSigner(pem_value)
    if value.startswith("remote+https://") or value.startswith(
        "remote+http://"
    ):
        endpoint=value.removeprefix("remote+")
        return RemoteHttpSigner(
            endpoint=endpoint,
            signing_key_id=str(key_id or ""),
            bearer_token=bearer_token,
            timeout_seconds=timeout_seconds,
        )
    raise SignerConfigurationError(
        f"unsupported signer URI: {value}"
    )
