#!/usr/bin/env python3
"""Read-only HTTP gate for the Production-OS Render migration.

This gate cannot prove that the old Render service is durably suspended:
that requires checking Render's service state independently before cutover.
No credential is ever sent to the legacy URL or printed to stdout/stderr.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from urllib.parse import urlsplit

NEW_URL = "https://production-os-control-plane.onrender.com"
LEGACY_URL = "https://production-os1.onrender.com"
READ_LIMIT = 8192


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def validated_origin(raw: str) -> str:
    value = str(raw).strip().rstrip("/")
    parsed = urlsplit(value)
    loopback = parsed.hostname in {"localhost", "127.0.0.1", "::1"}
    if (
        (parsed.scheme != "https" and not (loopback and parsed.scheme == "http"))
        or not parsed.netloc
        or parsed.username is not None
        or parsed.password is not None
        or parsed.path not in ("", "/")
        or parsed.query or parsed.fragment
        or not parsed.hostname
    ):
        raise ValueError("Render origin must be HTTPS without a path or credentials")
    try:
        _ = parsed.port
    except ValueError as exc:
        raise ValueError("Render origin has invalid port") from exc
    return value


def probe(origin: str, path: str, *, token: str | None = None,
          payload: dict | None = None, timeout: float = 5.0) -> tuple[int | None, dict | None]:
    """Return sanitized (HTTP status, bounded JSON) without raising network errors."""
    headers = {"Accept": "application/json", "User-Agent": "production-os-cutover-check"}
    if token:
        headers["Authorization"] = "Bearer " + token
    if payload is not None:
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(
        origin + path,
        data=(json.dumps(payload, separators=(",", ":")).encode("utf-8")
              if payload is not None else None),
        headers=headers,
        method="POST" if payload is not None else "GET",
    )
    opener = urllib.request.build_opener(NoRedirect())
    try:
        with opener.open(request, timeout=timeout) as response:
            raw = response.read(READ_LIMIT + 1)
            if len(raw) > READ_LIMIT:
                return response.status, None
            try:
                data = json.loads(raw)
            except (UnicodeDecodeError, ValueError):
                data = None
            return response.status, data if isinstance(data, dict) else None
    except urllib.error.HTTPError as exc:
        # Do not expose HTTP error bodies, Location headers or auth credentials.
        return exc.code, None
    except (urllib.error.URLError, OSError, TimeoutError):
        return None, None


def check_new(origin: str, *, attempts: int, interval: float, timeout: float) -> bool:
    for index in range(attempts):
        health_status, health = probe(origin, "/healthz", timeout=timeout)
        ready_status, ready = probe(origin, "/readyz", timeout=timeout)
        if (health_status == 200 and isinstance(health, dict)
                and health.get("status") == "healthy"
                and ready_status == 200 and isinstance(ready, dict)
                and ready.get("status") == "ready"
                and ready.get("database") == "reachable"):
            print("PASS new Render health and PostgreSQL readiness")
            return True
        if index + 1 < attempts:
            time.sleep(interval)
    print("BLOCK new Render health or PostgreSQL readiness not verified")
    return False


def check_legacy(origin: str, *, attempts: int, interval: float, timeout: float) -> bool:
    # A Render Free instance may initially return 503 and then wake into a
    # healthy, DB-connected controller. One 503 is not evidence of isolation.
    for index in range(attempts):
        status, ready = probe(origin, "/readyz", timeout=timeout)
        if status == 200:
            print("BLOCK legacy controller is responsive; prevent concurrent DB writers")
            return False
        if status != 503:
            print("BLOCK legacy controller isolation cannot be established by HTTP")
            return False
        if index + 1 < attempts:
            time.sleep(interval)
    print("PASS legacy HTTP readiness remained unavailable during observation")
    print("NOTE HTTP 503 does not prove Render suspension; verify service state separately")
    return True


def check_auth(origin: str, *, worker_token: str, operator_token: str,
               timeout: float) -> bool:
    if not worker_token or not operator_token:
        missing = [key for key, value in (
            ("PRODUCTION_OS_WORKER_TOKEN", worker_token),
            ("PRODUCTION_OS_OPERATOR_TOKEN", operator_token),
        ) if not value]
        print("BLOCK missing environment variables: " + ", ".join(missing))
        return False
    if worker_token == operator_token:
        print("BLOCK operator and worker tokens must be distinct")
        return False
    status, _ = probe(origin, "/v1/workflows", timeout=timeout)
    if status != 401:
        print("BLOCK unauthenticated workflow endpoint is not HTTP 401")
        return False
    status, result = probe(
        origin, "/v1/jobs/availability", token=worker_token,
        payload={"worker_id": "github-actions-worker", "capabilities": ["python"]},
        timeout=timeout,
    )
    if status != 200 or not isinstance(result, dict) or result.get("schema_version") != "production-os/job-availability/v1":
        print("BLOCK worker role authentication failed or availability contract invalid")
        return False
    status, result = probe(origin, "/v1/stats", token=operator_token, timeout=timeout)
    if status != 200 or not isinstance(result, dict) or not isinstance(result.get("jobs"), dict):
        print("BLOCK operator role authentication failed or statistics contract invalid")
        return False
    print("PASS protected API, worker token and operator token validated")
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--new-url", default=NEW_URL)
    parser.add_argument("--legacy-url", default=LEGACY_URL)
    parser.add_argument("--attempts", type=int, default=12)
    parser.add_argument("--interval", type=float, default=5.0)
    parser.add_argument("--timeout", type=float, default=5.0)
    parser.add_argument("--public-only", action="store_true",
                        help="Skip authenticated probes (diagnostic only, not full acceptance)")
    args = parser.parse_args(argv)
    if args.attempts < 2 or args.interval < 0 or args.timeout <= 0:
        parser.error("attempts must be >=2, interval >=0 and timeout >0")
    try:
        new = validated_origin(args.new_url)
        legacy = validated_origin(args.legacy_url)
    except ValueError as exc:
        parser.error(str(exc))
    if new == legacy:
        parser.error("new and legacy origins must differ")

    # Check both endpoints regardless of readiness result: the old controller
    # can still be live when the intended new service is failing.
    new_ok = check_new(new, attempts=args.attempts, interval=args.interval,
                       timeout=args.timeout)
    legacy_ok = check_legacy(legacy, attempts=args.attempts, interval=args.interval,
                             timeout=args.timeout)
    auth_ok = True
    if args.public_only:
        print("NOTE authentication skipped; this is not a full acceptance test")
    elif new_ok:
        auth_ok = check_auth(
            new, worker_token=os.environ.get("PRODUCTION_OS_WORKER_TOKEN", "").strip(),
            operator_token=os.environ.get("PRODUCTION_OS_OPERATOR_TOKEN", "").strip(),
            timeout=args.timeout,
        )
    else:
        print("BLOCK auth not attempted because new controller is unready")
        auth_ok = False
    if new_ok and legacy_ok and auth_ok:
        if args.public_only:
            print("INCOMPLETE HTTP-only diagnostic; authenticated probes were not run")
            return 2
        print("PASS HTTP checks; require independent Render suspension proof and a real worker canary")
        return 0
    print("FAIL Render cutover HTTP checks; no production mutation performed")
    return 1


if __name__ == "__main__":
    sys.exit(main())
