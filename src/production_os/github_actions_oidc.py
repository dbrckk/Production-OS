"""Bounded GitHub Actions OIDC exchange for one trusted production repository.

GitHub's RS256 JWT proves workflow identity; it is never used as the regular
API bearer. Exchange returns a random, in-memory, role-scoped session token.
No long-lived GitHub Actions repository secret is required.
"""
from __future__ import annotations

import base64
import hashlib
import json
import re
import secrets
import threading
import time
import urllib.request

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa

from .api_auth import Principal

ISSUER = "https://token.actions.githubusercontent.com"
AUDIENCE = "production-os-control-plane"
JWKS_URL = ISSUER + "/.well-known/jwks"
REPOSITORY = "dbrckk/ai-dev-server"
REPOSITORY_ID = "1359122023"
OWNER_ID = "131650085"
REF = "refs/heads/main"
WORKFLOWS = {
    "dbrckk/ai-dev-server/.github/workflows/production-os-actions-worker.yml@refs/heads/main":
        ("worker", frozenset({"schedule", "workflow_dispatch", "push"})),
    "dbrckk/ai-dev-server/.github/workflows/production-os-worker-canary.yml@refs/heads/main":
        ("operator", frozenset({"push", "workflow_dispatch"})),
}
SESSION_TTL_SECONDS = 6300   # Covers a single bounded 90-minute Actions worker job.
JWKS_TTL_SECONDS = 900
MAX_JWT_BYTES = 12000
MAX_SESSIONS = 512


class OIDCRejected(ValueError):
    """Fail-closed OIDC denial. Never include token claims or credentials."""


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _b64decode(value):
    if not isinstance(value, str) or not 1 <= len(value) <= 16384:
        raise OIDCRejected("invalid token encoding")
    if not re.fullmatch(r"[A-Za-z0-9_-]+", value):
        raise OIDCRejected("invalid token encoding")
    try:
        return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))
    except (ValueError, base64.binascii.Error) as exc:
        raise OIDCRejected("invalid token encoding") from None


def _read_json_part(value):
    try:
        result = json.loads(_b64decode(value))
    except (UnicodeError, ValueError, TypeError, json.JSONDecodeError):
        raise OIDCRejected("invalid token format") from None
    if not isinstance(result, dict):
        raise OIDCRejected("invalid token format")
    return result


def _load_jwks():
    request = urllib.request.Request(
        JWKS_URL, headers={"Accept": "application/json"},
    )
    opener = urllib.request.build_opener(_NoRedirect())
    with opener.open(request, timeout=8) as response:
        if int(getattr(response, "status", 200)) != 200:
            raise OIDCRejected("signing keys unavailable")
        raw = response.read(65537)
    if len(raw) > 65536:
        raise OIDCRejected("signing keys too large")
    value = json.loads(raw)
    if not isinstance(value, dict) or not isinstance(value.get("keys"), list):
        raise OIDCRejected("invalid signing keys")
    return value


class GitHubActionsOIDC:
    def __init__(self, *, enabled=False, fetch_jwks=None, clock=None):
        self.enabled = enabled is True
        self._fetch_jwks = fetch_jwks or _load_jwks
        self._clock = clock or time.time
        self._lock = threading.Lock()
        self._jwks = None
        self._jwks_until = 0.0
        self._sessions = {}

    def _key(self, kid):
        now = self._clock()
        with self._lock:
            current = self._jwks if now < self._jwks_until else None
        if current is not None:
            for key in current.get("keys", []):
                if key.get("kid") == kid:
                    return key
        # Fetch outside the lock; deny issuance on failed refresh.
        try:
            fresh = self._fetch_jwks()
        except (OSError, TimeoutError, ValueError, TypeError, KeyError):
            raise OIDCRejected("signing keys unavailable") from None
        if not isinstance(fresh, dict) or not isinstance(fresh.get("keys"), list):
            raise OIDCRejected("invalid signing keys")
        with self._lock:
            self._jwks = fresh
            self._jwks_until = self._clock() + JWKS_TTL_SECONDS
        for key in fresh["keys"]:
            if isinstance(key, dict) and key.get("kid") == kid:
                return key
        raise OIDCRejected("unknown signing key")

    def _verify(self, assertion):
        if not isinstance(assertion, str) or not 32 <= len(assertion) <= MAX_JWT_BYTES:
            raise OIDCRejected("invalid assertion")
        parts = assertion.split(".")
        if len(parts) != 3:
            raise OIDCRejected("invalid assertion")
        header = _read_json_part(parts[0])
        claims = _read_json_part(parts[1])
        if header.get("alg") != "RS256" or header.get("typ") not in (None, "JWT"):
            raise OIDCRejected("unsupported assertion algorithm")
        kid = header.get("kid")
        if not isinstance(kid, str) or not 1 <= len(kid) <= 128:
            raise OIDCRejected("missing signing key")
        jwk = self._key(kid)
        if (jwk.get("kty") != "RSA" or jwk.get("alg") not in (None, "RS256")
                or jwk.get("use") not in (None, "sig")):
            raise OIDCRejected("invalid signing key")
        try:
            n = int.from_bytes(_b64decode(jwk["n"]), "big")
            e = int.from_bytes(_b64decode(jwk["e"]), "big")
            if n.bit_length() < 2048 or e not in (3, 65537):
                raise ValueError("invalid RSA parameters")
            key = rsa.RSAPublicNumbers(e, n).public_key()
            key.verify(
                _b64decode(parts[2]), (parts[0] + "." + parts[1]).encode("ascii"),
                padding.PKCS1v15(), hashes.SHA256(),
            )
        except (KeyError, ValueError, TypeError, InvalidSignature):
            raise OIDCRejected("invalid assertion signature") from None

        now = self._clock()
        exp, iat, nbf = (claims.get("exp"), claims.get("iat"), claims.get("nbf"))
        if (type(exp) is not int or type(iat) is not int
                or not now < exp <= now + 600
                or not now - 600 <= iat <= now + 60
                or (nbf is not None and (type(nbf) is not int or nbf > now + 30))):
            raise OIDCRejected("invalid assertion lifetime")
        allowed_subs = {
            f"repo:{REPOSITORY}:ref:{REF}",
            f"repo:dbrckk@{OWNER_ID}/ai-dev-server@{REPOSITORY_ID}:ref:{REF}",
        }
        if (claims.get("iss") != ISSUER or claims.get("aud") != AUDIENCE
                or claims.get("repository") != REPOSITORY
                or str(claims.get("repository_id") or "") != REPOSITORY_ID
                or str(claims.get("repository_owner_id") or "") != OWNER_ID
                or claims.get("ref") != REF or claims.get("sub") not in allowed_subs
                or not re.fullmatch(r"[a-f0-9]{40}", str(claims.get("sha") or ""))
                or not re.fullmatch(r"[1-9][0-9]*", str(claims.get("run_id") or ""))):
            raise OIDCRejected("untrusted workflow identity")
        rule = WORKFLOWS.get(claims.get("workflow_ref"))
        if rule is None or claims.get("event_name") not in rule[1]:
            raise OIDCRejected("untrusted workflow")
        return rule[0]

    def exchange(self, assertion, *, requested_role=None):
        if not self.enabled:
            raise OIDCRejected("OIDC integration is disabled")
        granted_role = self._verify(assertion)
        role = requested_role or granted_role
        # An operator may explicitly request a less-privileged worker session.
        if role != granted_role and (granted_role, role) != ("operator", "worker"):
            raise OIDCRejected("untrusted requested role")
        raw = "pos-gha-" + secrets.token_urlsafe(32)
        digest = hashlib.sha256(raw.encode("ascii")).digest()
        now = self._clock()
        with self._lock:
            self._sessions = {
                k: v for k, v in self._sessions.items() if v[1] > now
            }
            # Fail closed if suspiciously many concurrent token exchanges.
            if len(self._sessions) >= MAX_SESSIONS:
                raise OIDCRejected("session capacity reached")
            self._sessions[digest] = (role, now + SESSION_TTL_SECONDS)
        return {
            "access_token": raw,
            "token_type": "Bearer",
            "role": role,
            "expires_in": SESSION_TTL_SECONDS,
        }

    def authenticate(self, bearer):
        if (not self.enabled or not isinstance(bearer, str)
                or not bearer.startswith("pos-gha-") or len(bearer) > 100):
            return None
        digest = hashlib.sha256(bearer.encode("ascii", "ignore")).digest()
        with self._lock:
            item = self._sessions.get(digest)
        if item is None or item[1] <= self._clock():
            return None
        return Principal(name="github-actions-" + item[0], role=item[0])
