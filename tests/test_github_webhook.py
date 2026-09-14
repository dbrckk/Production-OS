import hashlib
import hmac
import json

import pytest

from production_os.github_webhook import (
    WebhookDeliveryStore,
    WebhookError,
    parse_github_webhook,
    pull_request_event_target,
    verify_github_signature,
)
from production_os.sqlite_backend import SQLiteBackend


def signature(secret, body):
    return "sha256=" + hmac.new(
        secret.encode(),
        body,
        hashlib.sha256,
    ).hexdigest()


def test_verify_github_signature():
    body=b'{"x":1}'
    sig=signature("secret",body)
    assert verify_github_signature("secret",body,sig) is True
    assert verify_github_signature("wrong",body,sig) is False
    assert verify_github_signature("secret",body,None) is False


def test_parse_and_target_supported_pr_event():
    payload={
        "action":"synchronize",
        "repository":{"full_name":"o/a"},
        "pull_request":{"number":42},
    }
    body=json.dumps(payload).encode()
    parsed=parse_github_webhook(body)
    assert pull_request_event_target(
        "pull_request",
        parsed,
    ) == ("o/a",42,"synchronize")


def test_unsupported_pr_action_is_ignored():
    payload={
        "action":"closed",
        "repository":{"full_name":"o/a"},
        "pull_request":{"number":42},
    }
    assert pull_request_event_target(
        "pull_request",
        payload,
    ) is None


def test_invalid_pr_payload_fails_closed():
    with pytest.raises(WebhookError):
        pull_request_event_target(
            "pull_request",
            {"action":"opened"},
        )


def test_delivery_store_is_idempotent_and_releasable(tmp_path):
    backend=SQLiteBackend(tmp_path/"db.sqlite")
    store=WebhookDeliveryStore(backend)

    assert store.claim("delivery-1","pull_request","o/a") is True
    assert store.claim("delivery-1","pull_request","o/a") is False

    store.release("delivery-1")

    assert store.claim("delivery-1","pull_request","o/a") is True
