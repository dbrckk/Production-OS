from pathlib import Path


def test_worker_compose_profile_is_safe_and_deployable():
    payload = Path("compose.worker.yaml").read_text(encoding="utf-8")

    assert "production-worker:" in payload
    assert "profiles:\n      - worker" in payload
    assert "condition: service_healthy" in payload
    assert "/healthz" in payload
    assert "init: true" in payload
    assert "stop_grace_period: 15s" in payload

    assert "PRODUCTION_OS_WORKER_TOKEN:" in payload
    assert "--token" not in payload
    assert "--executor-command" in payload
    assert "PRODUCTION_OS_WORKER_EXECUTOR_COMMAND" in payload
    assert "PRODUCTION_OS_WORKER_MAX_CONCURRENCY" in payload
