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



def test_worker_compose_exposes_specialist_pool_without_replacing_generic_worker():
    payload = Path("compose.worker.yaml").read_text(encoding="utf-8")

    for service in (
        "production-worker-code:",
        "production-worker-debug:",
        "production-worker-review:",
        "production-worker-browser:",
    ):
        assert service in payload

    assert payload.count("worker-specialists") >= 4
    assert "--capability\n      - code-implementation" in payload
    assert "--capability\n      - test-debug" in payload
    assert "--capability\n      - code-review" in payload
    assert "--capability\n      - browser-ui-validation" not in payload

    assert "PRODUCTION_OS_WORKER_SPECIALTIES: code" in payload
    assert "PRODUCTION_OS_WORKER_SPECIALTIES: debug" in payload
    assert "PRODUCTION_OS_WORKER_SPECIALTIES: review" in payload
    assert "PRODUCTION_OS_WORKER_SPECIALTIES: browser" in payload
    # Browser worker is present but cannot claim browser validation until a real runtime is provisioned.
    assert "PRODUCTION_OS_SPECIALIST_MAX_CONCURRENCY" in payload
