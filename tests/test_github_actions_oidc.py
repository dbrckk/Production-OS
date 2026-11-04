"""Security regression suite for GitHub Actions OIDC credential exchange."""
import base64
import json

import pytest
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa

from production_os.github_actions_oidc import (
    AUDIENCE, ISSUER, OWNER_ID, REF, REPOSITORY, REPOSITORY_ID,
    GitHubActionsOIDC, OIDCRejected,
)

NOW = 1_800_000_000
WORKER = "dbrckk/ai-dev-server/.github/workflows/production-os-actions-worker.yml@refs/heads/main"
CANARY = "dbrckk/ai-dev-server/.github/workflows/production-os-worker-canary.yml@refs/heads/main"


def b64(value):
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


@pytest.fixture
def signing():
    private = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public = private.public_key().public_numbers()
    jwks = {"keys": [{
        "kid": "test-key-1", "kty": "RSA", "alg": "RS256", "use": "sig",
        "n": b64(public.n.to_bytes((public.n.bit_length() + 7) // 8, "big")),
        "e": b64(public.e.to_bytes((public.e.bit_length() + 7) // 8, "big")),
    }]}
    def sign(override=None, *, kind="worker", private_key=None):
        claims = {
            "iss": ISSUER, "aud": AUDIENCE,
            "sub": "repo:dbrckk/ai-dev-server:ref:refs/heads/main",
            "repository": REPOSITORY, "repository_id": REPOSITORY_ID,
            "repository_owner_id": OWNER_ID, "ref": REF,
            "workflow_ref": WORKER if kind == "worker" else CANARY,
            "event_name": "schedule" if kind == "worker" else "workflow_dispatch",
            "sha": "a" * 40, "run_id": "12345",
            "iat": NOW - 10, "nbf": NOW - 10, "exp": NOW + 300,
        }
        claims.update(override or {})
        header = {"alg": "RS256", "typ": "JWT", "kid": "test-key-1"}
        first = b64(json.dumps(header).encode())
        second = b64(json.dumps(claims).encode())
        signing_input = (first + "." + second).encode()
        sig = (private_key or private).sign(signing_input, padding.PKCS1v15(), hashes.SHA256())
        return first + "." + second + "." + b64(sig)
    return jwks, sign


def test_worker_oidc_exchange_is_role_scoped_and_ephemeral(signing):
    jwks, sign = signing
    auth = GitHubActionsOIDC(enabled=True, fetch_jwks=lambda: jwks, clock=lambda: NOW)
    response = auth.exchange(sign())
    assert response["role"] == "worker"
    assert response["expires_in"] == 6300
    assert response["token_type"] == "Bearer"
    assert response["access_token"].startswith("pos-gha-")
    assert auth.authenticate(response["access_token"]).allows("worker")
    assert not auth.authenticate(response["access_token"]).allows("operator")
    assert auth.authenticate(response["access_token"] + "bad") is None
    assert auth.authenticate(response["access_token"] + "☃") is None
    assert auth.authenticate("other-secret") is None
    with pytest.raises(OIDCRejected):
        auth.exchange(sign(), requested_role="operator")


def test_canary_operator_can_request_narrow_worker_session(signing):
    jwks, sign = signing
    auth = GitHubActionsOIDC(enabled=True, fetch_jwks=lambda: jwks, clock=lambda: NOW)
    operator = auth.exchange(sign(kind="canary"))
    assert auth.authenticate(operator["access_token"]).role == "operator"
    worker = auth.exchange(sign(kind="canary"), requested_role="worker")
    assert auth.authenticate(worker["access_token"]).role == "worker"
    assert operator["access_token"] != worker["access_token"]
    with pytest.raises(OIDCRejected):
        auth.exchange(sign(kind="canary"), requested_role="admin")


def test_signed_claims_and_trust_rules_are_mandatory(signing):
    jwks, sign = signing
    auth = GitHubActionsOIDC(enabled=True, fetch_jwks=lambda: jwks, clock=lambda: NOW)
    invalid = [
        {"aud": "another-app"},
        {"iss": "https://attacker.invalid"},
        {"repository": "someone/else"},
        {"repository_id": "1"},
        {"repository_owner_id": "2"},
        {"ref": "refs/heads/feature"},
        {"sub": "repo:someone/else:ref:refs/heads/main"},
        {"sub": ["repo:dbrckk/ai-dev-server:ref:refs/heads/main"]},
        {"workflow_ref": ["bad"]},
        {"event_name": ["schedule"]},
        {"workflow_ref": "dbrckk/ai-dev-server/.github/workflows/untrusted.yml@refs/heads/main"},
        {"event_name": "pull_request"},
        {"sha": "not-a-sha"},
        {"run_id": "0"},
        {"exp": NOW - 1},
        {"exp": NOW + 7200},
        {"iat": NOW - 7200},
        {"nbf": NOW + 120},
    ]
    for claim in invalid:
        with pytest.raises(OIDCRejected), pytest.MonkeyPatch.context():
            auth.exchange(sign(claim))
    assert auth.exchange(sign({"sub": (
        f"repo:dbrckk@{OWNER_ID}/ai-dev-server@{REPOSITORY_ID}:ref:{REF}"
    )}))["role"] == "worker"


def test_signature_and_key_substitution_rejected(signing):
    jwks, sign = signing
    auth = GitHubActionsOIDC(enabled=True, fetch_jwks=lambda: jwks, clock=lambda: NOW)
    another = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    for forged in (sign(private_key=another), "not-a-jwt", sign() + "X"):
        with pytest.raises(OIDCRejected):
            auth.exchange(forged)
    failed = GitHubActionsOIDC(enabled=True, fetch_jwks=lambda: {"keys": []}, clock=lambda: NOW)
    with pytest.raises(OIDCRejected):
        failed.exchange(sign())
    offline = GitHubActionsOIDC(
        enabled=True, fetch_jwks=lambda: (_ for _ in ()).throw(OSError("network down")),
        clock=lambda: NOW,
    )
    with pytest.raises(OIDCRejected):
        offline.exchange(sign())


def test_disabled_expired_and_restart_sessions_are_rejected(signing):
    jwks, sign = signing
    now = [NOW]
    disabled = GitHubActionsOIDC(fetch_jwks=lambda: jwks, clock=lambda: now[0])
    with pytest.raises(OIDCRejected):
        disabled.exchange(sign())
    auth = GitHubActionsOIDC(enabled=True, fetch_jwks=lambda: jwks, clock=lambda: now[0])
    session = auth.exchange(sign())["access_token"]
    assert auth.authenticate(session) is not None
    now[0] += 6300
    assert auth.authenticate(session) is None
    assert GitHubActionsOIDC(enabled=True, fetch_jwks=lambda: jwks).authenticate(session) is None
    assert disabled.authenticate(session) is None
