from __future__ import annotations

import hashlib
import hmac
import json
from datetime import datetime, timezone
from typing import Any


SUPPORTED_PULL_REQUEST_ACTIONS = {
    "opened",
    "reopened",
    "synchronize",
}


class WebhookError(ValueError):
    pass


def verify_github_signature(
    secret: str,
    body: bytes,
    signature_header: str | None,
) -> bool:
    if not secret or not signature_header:
        return False
    prefix = "sha256="
    if not signature_header.startswith(prefix):
        return False
    expected = hmac.new(
        secret.encode("utf-8"),
        body,
        hashlib.sha256,
    ).hexdigest()
    supplied = signature_header[len(prefix):]
    return hmac.compare_digest(expected, supplied)


def parse_github_webhook(body: bytes) -> dict[str, Any]:
    try:
        payload = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise WebhookError("invalid JSON webhook body") from exc
    if not isinstance(payload, dict):
        raise WebhookError("webhook JSON body must be an object")
    return payload


def pull_request_event_target(
    event_name: str,
    payload: dict[str, Any],
) -> tuple[str, int, str] | None:
    if event_name != "pull_request":
        return None

    action = str(payload.get("action") or "")
    if action not in SUPPORTED_PULL_REQUEST_ACTIONS:
        return None

    repository = payload.get("repository")
    pull_request = payload.get("pull_request")
    if not isinstance(repository, dict) or not isinstance(
        pull_request,
        dict,
    ):
        raise WebhookError(
            "pull_request webhook requires repository and pull_request"
        )

    full_name = str(repository.get("full_name") or "").strip()
    number = pull_request.get("number", payload.get("number"))
    if not full_name or number is None:
        raise WebhookError(
            "pull_request webhook missing repository or PR number"
        )

    try:
        pr_number = int(number)
    except (TypeError, ValueError) as exc:
        raise WebhookError("invalid pull request number") from exc

    if pr_number < 1:
        raise WebhookError("invalid pull request number")

    return full_name, pr_number, action


class WebhookDeliveryStore:
    def __init__(self, backend):
        self.backend = backend
        self.postgres = backend.__class__.__name__.startswith(
            "Postgres"
        )

    def claim(
        self,
        delivery_id: str,
        event_name: str,
        repository: str | None = None,
    ) -> bool:
        delivery_id = str(delivery_id or "").strip()
        if not delivery_id:
            raise WebhookError("missing X-GitHub-Delivery")

        received_at = datetime.now(timezone.utc).isoformat()
        with self.backend.transaction() as db:
            if self.postgres:
                with db.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO webhook_deliveries(
                            delivery_id, event_name,
                            repository, received_at
                        )
                        VALUES(%s, %s, %s, %s)
                        ON CONFLICT(delivery_id) DO NOTHING
                        """,
                        (
                            delivery_id,
                            event_name,
                            repository,
                            received_at,
                        ),
                    )
                    return cur.rowcount == 1

            cursor = db.execute(
                """
                INSERT OR IGNORE INTO webhook_deliveries(
                    delivery_id, event_name,
                    repository, received_at
                )
                VALUES(?, ?, ?, ?)
                """,
                (
                    delivery_id,
                    event_name,
                    repository,
                    received_at,
                ),
            )
            return cursor.rowcount == 1

    def release(self, delivery_id: str) -> None:
        with self.backend.transaction() as db:
            if self.postgres:
                with db.cursor() as cur:
                    cur.execute(
                        "DELETE FROM webhook_deliveries "
                        "WHERE delivery_id=%s",
                        (delivery_id,),
                    )
                return
            db.execute(
                "DELETE FROM webhook_deliveries "
                "WHERE delivery_id=?",
                (delivery_id,),
            )
