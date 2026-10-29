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

    # Also constrain the active Render deployment: one $0 web service, the
    # existing persistent Neon database and explicit secret prompts. This
    # extends an existing deployment test rather than adding a new unit test.
    import re

    blueprint = Path("render.yaml").read_text(encoding="utf-8")
    assert re.findall(r"(?m)^  - type: web$", blueprint) == ["  - type: web"]
    assert "    runtime: docker\n" in blueprint
    assert "    plan: free\n" in blueprint
    assert "    region: frankfurt\n" in blueprint
    assert "    repo: https://github.com/dbrckk/Production-OS\n" in blueprint
    assert "    branch: main\n" in blueprint
    assert "    dockerfilePath: ./Dockerfile.free-hosting\n" in blueprint
    assert Path("Dockerfile.free-hosting").is_file()
    # Cheap liveness must not query Neon on every Render probe.
    # Retain separate PostgreSQL-backed /readyz for worker checks.
    assert "    healthCheckPath: /healthz\n" in blueprint
    assert "    healthCheckPath: /readyz\n" not in blueprint
    control_plane = Path("src/production_os/control_plane.py").read_text(encoding="utf-8")
    assert 'if parsed.path in {"/health", "/healthz"}:' in control_plane
    assert 'if parsed.path == "/readyz":' in control_plane
    assert 'db.execute("SELECT 1")' in control_plane
    assert "    autoDeployTrigger: commit\n" in blueprint
    assert "databases:" not in blueprint
    assert "disk:" not in blueprint
    assert "type: cron" not in blueprint
    assert "type: worker" not in blueprint
    for name in (
        "DATABASE_URL",
        "PRODUCTION_OS_WORKER_TOKEN",
        "PRODUCTION_OS_OPERATOR_TOKEN",
        "GITHUB_TOKEN",
    ):
        assert (
            "      - key: " + name + "\n"
            "        sync: false\n"
        ) in blueprint
    assert "generateValue" not in blueprint
    for name, value in (
        ("PRODUCTION_OS_WORKER_ID", "github-actions-worker"),
        ("PRODUCTION_OS_ACTIONS_REPOSITORY", "dbrckk/ai-dev-server"),
        ("PRODUCTION_OS_ACTIONS_WORKFLOW", "production-os-actions-worker.yml"),
        ("PRODUCTION_OS_ACTIONS_REF", "main"),
    ):
        assert (
            "      - key: " + name + "\n"
            "        value: " + value + "\n"
        ) in blueprint
