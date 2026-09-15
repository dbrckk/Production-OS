from __future__ import annotations

import json
import ssl
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class VaultAuthError(RuntimeError):
    pass


@dataclass(frozen=True)
class VaultToken:
    token: str
    renewable: bool = False
    lease_duration: int = 0


def _post(
    *,
    address: str,
    path: str,
    payload: dict[str, Any],
    namespace: str | None = None,
    timeout_seconds: float = 10.0,
    ssl_context: ssl.SSLContext | None = None,
) -> dict[str, Any]:
    if not address.startswith("https://"):
        raise VaultAuthError("Vault authentication requires HTTPS")
    headers={
        "Content-Type":"application/json",
        "Accept":"application/json",
    }
    if namespace:
        headers["X-Vault-Namespace"]=namespace
    request=Request(
        f"{address.rstrip('/')}/v1/{path.lstrip('/')}",
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        with urlopen(
            request,
            timeout=timeout_seconds,
            context=ssl_context or ssl.create_default_context(),
        ) as response:
            result=json.loads(response.read())
    except (
        HTTPError,URLError,TimeoutError,json.JSONDecodeError
    ) as exc:
        raise VaultAuthError(
            f"Vault authentication failed: {exc}"
        ) from exc
    if not isinstance(result,dict):
        raise VaultAuthError("Vault auth response must be an object")
    return result


def _token(result: dict[str, Any]) -> VaultToken:
    auth=dict(result.get("auth") or {})
    value=str(auth.get("client_token") or "")
    if not value:
        raise VaultAuthError("Vault returned no client token")
    return VaultToken(
        token=value,
        renewable=bool(auth.get("renewable",False)),
        lease_duration=int(auth.get("lease_duration") or 0),
    )


def login_approle(
    *,
    address: str,
    role_id: str,
    secret_id: str,
    mount: str = "approle",
    namespace: str | None = None,
    timeout_seconds: float = 10.0,
    ssl_context: ssl.SSLContext | None = None,
) -> VaultToken:
    if not role_id or not secret_id:
        raise VaultAuthError("AppRole role_id and secret_id are required")
    return _token(_post(
        address=address,
        path=f"auth/{mount.strip('/')}/login",
        payload={"role_id":role_id,"secret_id":secret_id},
        namespace=namespace,
        timeout_seconds=timeout_seconds,
        ssl_context=ssl_context,
    ))


def login_kubernetes(
    *,
    address: str,
    role: str,
    jwt: str,
    mount: str = "kubernetes",
    namespace: str | None = None,
    timeout_seconds: float = 10.0,
    ssl_context: ssl.SSLContext | None = None,
) -> VaultToken:
    if not role or not jwt:
        raise VaultAuthError("Kubernetes role and JWT are required")
    return _token(_post(
        address=address,
        path=f"auth/{mount.strip('/')}/login",
        payload={"role":role,"jwt":jwt},
        namespace=namespace,
        timeout_seconds=timeout_seconds,
        ssl_context=ssl_context,
    ))
