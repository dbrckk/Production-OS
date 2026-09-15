from __future__ import annotations

import json
import ssl
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .signers import PemSigner, Signer
from .vault_auth import login_approle, login_kubernetes
from .vault_signer import VaultTransitSigner


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
        retries: int = 2,
        backoff_seconds: float = 0.25,
        require_https: bool = True,
        ca_file: str | None = None,
        client_cert_file: str | None = None,
        client_key_file: str | None = None,
        circuit_failure_threshold: int = 3,
        circuit_reset_seconds: float = 30.0,
    ):
        if not endpoint.startswith(("https://", "http://")):
            raise SignerConfigurationError(
                "remote signer endpoint must be HTTP(S)"
            )
        if require_https and not endpoint.startswith("https://"):
            raise SignerConfigurationError(
                "remote signer requires HTTPS"
            )
        if not signing_key_id:
            raise SignerConfigurationError(
                "remote signer key_id is required"
            )
        self.endpoint=endpoint
        self._key_id=signing_key_id
        self.bearer_token=bearer_token
        self.timeout_seconds=float(timeout_seconds)
        self.retries=max(0,int(retries))
        self.backoff_seconds=max(0.0,float(backoff_seconds))
        self.circuit_failure_threshold=max(
            1,int(circuit_failure_threshold)
        )
        self.circuit_reset_seconds=max(
            0.0,float(circuit_reset_seconds)
        )
        self._consecutive_failures=0
        self._circuit_opened_at: float | None=None
        self.ssl_context=ssl.create_default_context(cafile=ca_file)
        if client_cert_file:
            self.ssl_context.load_cert_chain(
                certfile=client_cert_file,
                keyfile=client_key_file,
            )

    @property
    def key_id(self) -> str:
        return self._key_id

    def sign(self, payload: dict[str, Any]) -> dict[str, str]:
        now=time.monotonic()
        if self._circuit_opened_at is not None:
            if now-self._circuit_opened_at < self.circuit_reset_seconds:
                raise RemoteSignerError("remote signer circuit is open")
            self._circuit_opened_at=None
            self._consecutive_failures=0

        body=json.dumps(
            {"key_id":self.key_id,"payload":payload},
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        headers={
            "Content-Type":"application/json",
            "Accept":"application/json",
        }
        if self.bearer_token:
            headers["Authorization"]=f"Bearer {self.bearer_token}"

        last_error: Exception | None=None
        for attempt in range(self.retries+1):
            request=Request(
                self.endpoint,data=body,headers=headers,method="POST"
            )
            try:
                with urlopen(
                    request,
                    timeout=self.timeout_seconds,
                    context=self.ssl_context,
                ) as response:
                    if response.status < 200 or response.status >= 300:
                        raise RemoteSignerError(
                            f"remote signer returned HTTP {response.status}"
                        )
                    result=json.loads(response.read())
                if not isinstance(result,dict):
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
                self._consecutive_failures=0
                self._circuit_opened_at=None
                return {
                    "algorithm":"ed25519",
                    "key_id":self.key_id,
                    "signature":str(signature["signature"]),
                }
            except (
                HTTPError,URLError,TimeoutError,
                json.JSONDecodeError,RemoteSignerError,
            ) as exc:
                last_error=exc
                if attempt < self.retries:
                    time.sleep(
                        self.backoff_seconds*(2**attempt)
                    )

        self._consecutive_failures+=1
        if self._consecutive_failures >= self.circuit_failure_threshold:
            self._circuit_opened_at=time.monotonic()
        raise RemoteSignerError(
            f"remote signing failed: {last_error}"
        )



def create_signer(
    uri: str,
    *,
    pem_value: str | None = None,
    key_id: str | None = None,
    bearer_token: str | None = None,
    timeout_seconds: float = 10.0,
    retries: int = 2,
    backoff_seconds: float = 0.25,
    require_https: bool = True,
    ca_file: str | None = None,
    client_cert_file: str | None = None,
    client_key_file: str | None = None,
    vault_token: str | None = None,
    vault_namespace: str | None = None,
    vault_mount: str = "transit",
    vault_auth_method: str = "token",
    vault_role_id: str | None = None,
    vault_secret_id: str | None = None,
    vault_kubernetes_role: str | None = None,
    vault_kubernetes_jwt: str | None = None,
    vault_auth_mount: str | None = None,
) -> Signer:
    value=str(uri or "").strip()
    if value == "pem:":
        if not pem_value:
            raise SignerConfigurationError(
                "pem signer requires private key material"
            )
        return PemSigner(pem_value)
    if value.startswith("vault+https://"):
        target=value.removeprefix("vault+")
        marker="/keys/"
        if marker not in target:
            raise SignerConfigurationError(
                "Vault signer URI must end with /keys/<transit-key>"
            )
        address,key_name=target.rsplit(marker,1)
        if not key_name:
            raise SignerConfigurationError(
                "Vault transit key is required"
            )
        auth_method=str(vault_auth_method or "token").lower()
        token=str(vault_token or bearer_token or "")
        if auth_method == "approle":
            token=login_approle(
                address=address,
                role_id=str(vault_role_id or ""),
                secret_id=str(vault_secret_id or ""),
                mount=vault_auth_mount or "approle",
                namespace=vault_namespace,
                timeout_seconds=timeout_seconds,
            ).token
        elif auth_method == "kubernetes":
            token=login_kubernetes(
                address=address,
                role=str(vault_kubernetes_role or ""),
                jwt=str(vault_kubernetes_jwt or ""),
                mount=vault_auth_mount or "kubernetes",
                namespace=vault_namespace,
                timeout_seconds=timeout_seconds,
            ).token
        elif auth_method != "token":
            raise SignerConfigurationError(
                f"unsupported Vault auth method: {auth_method}"
            )
        return VaultTransitSigner(
            address=address,
            transit_key=key_name,
            signing_key_id=str(key_id or ""),
            token=token,
            mount=vault_mount,
            namespace=vault_namespace,
            timeout_seconds=timeout_seconds,
            ca_file=ca_file,
            client_cert_file=client_cert_file,
            client_key_file=client_key_file,
        )
    if value.startswith("remote+https://") or value.startswith(
        "remote+http://"
    ):
        endpoint=value.removeprefix("remote+")
        return RemoteHttpSigner(
            endpoint=endpoint,
            signing_key_id=str(key_id or ""),
            bearer_token=bearer_token,
            timeout_seconds=timeout_seconds,
            retries=retries,
            backoff_seconds=backoff_seconds,
            require_https=require_https,
            ca_file=ca_file,
            client_cert_file=client_cert_file,
            client_key_file=client_key_file,
        )
    raise SignerConfigurationError(
        f"unsupported signer URI: {value}"
    )
