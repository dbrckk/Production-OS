from pathlib import Path


def test_controller_daemon_compose_service_is_resilient_and_persistent():
    payload = Path("compose.yaml").read_text(encoding="utf-8")

    assert "production-controller:" in payload
    assert "profiles:\n      - controller-daemon" in payload
    assert "restart: unless-stopped" in payload
    assert "init: true" in payload
    assert "stop_grace_period: 20s" in payload
    assert "--daemon" in payload
    assert "PRODUCTION_OS_CONTROLLER_INTERVAL_SECONDS" in payload
    assert "PRODUCTION_OS_CONTROLLER_MAX_BACKOFF_SECONDS" in payload
    assert "/data/production.db" in payload
    assert "/data/controller-health.json" in payload
    assert "/data/controller-journal.jsonl" in payload
    assert "GITHUB_TOKEN: ${GITHUB_TOKEN:-}" in payload



def test_controller_deployment_defaults_to_managed_execution():
    payload = Path("compose.yaml").read_text(encoding="utf-8")

    assert (
        "PRODUCTION_OS_CONTROLLER_EXECUTION_MODE: "
        "${PRODUCTION_OS_CONTROLLER_EXECUTION_MODE:-managed}"
    ) in payload
    assert "--execution-mode" in payload
    assert "${PRODUCTION_OS_CONTROLLER_EXECUTION_MODE:-managed}" in payload
    assert "--project-token-budget" in payload
    assert "${PRODUCTION_OS_CONTROLLER_PROJECT_TOKEN_BUDGET:-12000}" in payload
