from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_compose_persists_control_plane_and_bootstraps_auth():
    text = (ROOT / "compose.yaml").read_text(encoding="utf-8")

    assert "bootstrap-auth:" in text
    assert "control-plane:" in text
    assert "production-os-data:/data" in text
    assert "service_completed_successfully" in text
    assert "restart: unless-stopped" in text
    assert "healthcheck:" in text
    assert "PRODUCTION_OS_BIND_ADDRESS" in text
    assert "127.0.0.1" in text
    assert "auth-config-init" in text


def test_compose_worker_is_optional_persistent_runner_with_writable_workspace():
    text = (ROOT / "compose.yaml").read_text(encoding="utf-8")

    assert "worker:" in text
    assert 'profiles: ["worker"]' in text
    assert "remote-worker-run" in text
    assert "PRODUCTION_OS_WORKER_ID" in text
    assert "PRODUCTION_OS_EXECUTOR_COMMAND" in text
    assert "production-os-worker:/workspace" in text
    assert "working_dir: /workspace" in text
    assert "service_healthy" in text


def test_env_example_contains_only_placeholders_and_deployment_knobs():
    text = (ROOT / ".env.example").read_text(encoding="utf-8")

    assert "PRODUCTION_OS_OPERATOR_TOKEN=replace-with-a-long-random-token" in text
    assert "PRODUCTION_OS_WORKER_TOKEN=replace-with-another-long-random-token" in text
    assert "PRODUCTION_OS_WORKER_ID=worker-one" in text
    assert "PRODUCTION_OS_BIND_ADDRESS=127.0.0.1" in text
    assert "PRODUCTION_OS_PORT=8787" in text
    assert "PRODUCTION_OS_EXECUTOR_COMMAND=" in text
