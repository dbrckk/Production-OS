from __future__ import annotations

import base64
import json
import ssl
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from .signers import Signer
from .signing import canonical_json


class VaultSignerError(RuntimeError):
    pass


class VaultTransitSigner(Signer):
    def __init__(
        self,
        *,
        address: str,
        transit_key: str,
        signing_key_id: str,
        token: str,
        mount: str = "transit",
        namespace: str | None = None,
        timeout_seconds: float = 10.0,
        ca_file: str | None = None,
        client_cert_file: str | None = None,
        client_key_file: str | None = None,
    ):
        if not address.startswith("https://"):
            raise VaultSignerError("Vault address must use HTTPS")
        if not transit_key or not signing_key_id or not token:
            raise VaultSignerError(
                "Vault transit key, key_id and token are required"
            )
        self.address=address.rstrip("/")
        self.transit_key=transit_key
        self._key_id=signing_key_id
        self.token=token
        self.mount=mount.strip("/")
        self.namespace=namespace
        self.timeout_seconds=float(timeout_seconds)
        self.ssl_context=ssl.create_default_context(cafile=ca_file)
        if client_cert_file:
            self.ssl_context.load_cert_chain(
                client_cert_file,
                client_key_file,
            )

    @property
    def key_id(self) -> str:
        return self._key_id

    def sign(self, payload: dict[str, Any]) -> dict[str, str]:
        raw=canonical_json(payload).encode("utf-8")
        request_body=json.dumps({
            "input":base64.b64encode(raw).decode("ascii"),
            "prehashed":False,
            "signature_algorithm":"ed25519",
        }).encode("utf-8")
        headers={
            "Content-Type":"application/json",
            "Accept":"application/json",
            "X-Vault-Token":self.token,
        }
        if self.namespace:
            headers["X-Vault-Namespace"]=self.namespace
        url=(
            f"{self.address}/v1/{quote(self.mount,safe='')}/sign/"
            f"{quote(self.transit_key,safe='')}"
        )
        try:
            with urlopen(
                Request(url,data=request_body,headers=headers,method="POST"),
                timeout=self.timeout_seconds,
                context=self.ssl_context,
            ) as response:
                result=json.loads(response.read())
        except (HTTPError,URLError,TimeoutError,json.JSONDecodeError) as exc:
            raise VaultSignerError(
                f"Vault Transit signing failed: {exc}"
            ) from exc
        signature=str(
            dict(result.get("data") or {}).get("signature") or ""
        )
        if not signature.startswith("vault:v"):
            raise VaultSignerError(
                "Vault returned an invalid Transit signature"
            )
        parts=signature.split(":",2)
        if len(parts) != 3 or not parts[2]:
            raise VaultSignerError(
                "Vault returned a malformed Transit signature"
            )
        return {
            "algorithm":"ed25519",
            "key_id":self.key_id,
            "signature":parts[2],
            "provider":"vault-transit",
            "provider_signature":signature,
        }
