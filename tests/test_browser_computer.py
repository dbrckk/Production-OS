import pytest

from production_os.browser_computer import (
    BROWSER_PLAN_SCHEMA,
    BROWSER_SESSION_SCHEMA,
    _load_browser_session,
    _safe_resume_url,
    _write_browser_session,
    validate_browser_plan,
)
from production_os.sqlite_backend import SQLiteBackend, SQLiteJobQueue
from production_os.workflow_engine import WorkflowEngine, WorkflowTaskSpec


def test_browser_plan_validates_bounded_actions_and_redacts_fill_value():
    plan = validate_browser_plan({
        "schema_version":BROWSER_PLAN_SCHEMA,
        "allowed_hosts":["example.com"],
        "persist_session":True,
        "actions":[
            {"action":"navigate","url":"https://example.com"},
            {"action":"fill","selector":"#email","value":"user@example.com"},
            {"action":"click","selector":"button[type=submit]"},
            {"action":"extract_text","selector":"main","name":"result"},
            {"action":"screenshot","name":"final"},
        ],
    })

    assert plan.allowed_hosts == ("example.com",)
    assert plan.persist_session is True
    assert plan.allow_private_network is False
    assert plan.actions[1].value == "user@example.com"
    assert "value" not in plan.actions[1].to_dict()


@pytest.mark.parametrize(
    "payload,match",
    [
        (
            {
                "schema_version":BROWSER_PLAN_SCHEMA,
                "allowed_hosts":["example.com"],
                "actions":[
                    {"action":"navigate","url":"https://evil.example"},
                ],
            },
            "host is not allowed",
        ),
        (
            {
                "schema_version":BROWSER_PLAN_SCHEMA,
                "allowed_hosts":["example.com"],
                "actions":[
                    {"action":"navigate","url":"javascript:alert(1)"},
                ],
            },
            "http or https",
        ),
        (
            {
                "schema_version":BROWSER_PLAN_SCHEMA,
                "allowed_hosts":["example.com"],
                "actions":[
                    {"action":"evaluate","value":"document.cookie"},
                ],
            },
            "unsupported browser action",
        ),
        (
            {
                "schema_version":BROWSER_PLAN_SCHEMA,
                "allowed_hosts":["example.com"],
                "actions":[
                    {"action":"navigate","url":"https://user:pass@example.com"},
                ],
            },
            "must not contain credentials",
        ),
    ],
)
def test_browser_plan_rejects_unsafe_navigation_and_actions(payload, match):
    with pytest.raises(ValueError, match=match):
        validate_browser_plan(payload)


def test_workflow_injects_browser_computer_contract(tmp_path):
    backend = SQLiteBackend(tmp_path / "browser.sqlite")
    queue = SQLiteJobQueue(backend)
    engine = WorkflowEngine(backend, queue)
    workflow = engine.create(
        name="browser task",
        repository="owner/repo",
        tasks=[
            WorkflowTaskSpec(
                task_id="browse",
                title="Browse",
                payload={
                    "handoff":{
                        "repository":"owner/repo",
                        "task":"Inspect the web application.",
                        "required_capabilities":["browser-computer-use"],
                        "preferred_capabilities":["browser-computer-use"],
                    },
                },
            ),
        ],
    )

    job = engine.dispatch_ready(workflow["id"])[0]
    contract = job["payload"]["handoff"]["tool_contracts"][
        "browser_computer"
    ]

    assert job["payload"]["required_capabilities"] == [
        "browser-computer-use"
    ]
    assert contract["schema"] == BROWSER_PLAN_SCHEMA
    assert contract["max_actions"] == 64
    assert contract["requires_allowed_hosts"] is True
    assert contract["persistent_session"] is True



def test_browser_plan_cli_parses_runtime_paths():
    from production_os.cli import _parse_args

    args = _parse_args([
        "browser-plan-run",
        "--plan", "/tmp/plan.json",
        "--artifacts-dir", "/tmp/artifacts",
        "--storage-state", "/tmp/state.json",
        "--session-state", "/tmp/session.json",
    ])

    assert args.plan == "/tmp/plan.json"
    assert args.artifacts_dir == "/tmp/artifacts"
    assert args.storage_state == "/tmp/state.json"
    assert args.session_state == "/tmp/session.json"
    assert args.headed is False



def test_browser_plan_cli_defaults_storage_state_to_runtime_workspace(monkeypatch):
    from argparse import Namespace

    from production_os.cli import _browser_storage_state

    monkeypatch.setenv(
        "PRODUCTION_OS_RUNTIME_WORKSPACE",
        "/var/lib/production-os/runtime/job-a",
    )
    args = Namespace(storage_state="")

    assert _browser_storage_state(args) == (
        "/var/lib/production-os/runtime/job-a/browser-state.json"
    )


def test_browser_plan_cli_explicit_storage_state_wins(monkeypatch):
    from argparse import Namespace

    from production_os.cli import _browser_storage_state

    monkeypatch.setenv(
        "PRODUCTION_OS_RUNTIME_WORKSPACE",
        "/var/lib/production-os/runtime/job-a",
    )
    args = Namespace(storage_state="/tmp/custom-state.json")

    assert _browser_storage_state(args) == "/tmp/custom-state.json"



def test_browser_plan_blocks_private_network_by_default():
    with pytest.raises(ValueError, match="private-network"):
        validate_browser_plan({
            "schema_version":BROWSER_PLAN_SCHEMA,
            "allowed_hosts":["127.0.0.1"],
            "actions":[
                {"action":"navigate","url":"http://127.0.0.1:8000"},
            ],
        })


def test_browser_plan_allows_private_network_only_with_explicit_opt_in():
    plan = validate_browser_plan({
        "schema_version":BROWSER_PLAN_SCHEMA,
        "allowed_hosts":["127.0.0.1"],
        "allow_private_network":True,
        "actions":[
            {"action":"navigate","url":"http://127.0.0.1:8000"},
        ],
    })

    assert plan.allow_private_network is True



def test_browser_session_resume_url_strips_query_and_fragment():
    safe = _safe_resume_url(
        "https://example.com/app/path?token=secret#section",
        {"example.com"},
        allow_private_network=False,
    )

    assert safe == "https://example.com/app/path"


def test_browser_session_metadata_round_trips_only_safe_location(tmp_path):
    plan = validate_browser_plan({
        "schema_version":BROWSER_PLAN_SCHEMA,
        "allowed_hosts":["example.com"],
        "persist_session":True,
        "actions":[
            {"action":"navigate","url":"https://example.com/app"},
        ],
    })
    path = tmp_path / "browser-session.json"

    written = _write_browser_session(
        path,
        last_url="https://example.com/app?access_token=secret#fragment",
        plan=plan,
    )
    loaded = _load_browser_session(path, plan)

    assert written is not None
    assert written["schema_version"] == BROWSER_SESSION_SCHEMA
    assert written["last_url"] == "https://example.com/app"
    assert loaded["last_url"] == "https://example.com/app"
    payload = path.read_text(encoding="utf-8")
    assert "access_token" not in payload
    assert "secret" not in payload


def test_browser_session_rejects_stale_disallowed_host(tmp_path):
    plan = validate_browser_plan({
        "schema_version":BROWSER_PLAN_SCHEMA,
        "allowed_hosts":["example.com"],
        "persist_session":True,
        "actions":[
            {"action":"extract_text","selector":"main","name":"result"},
        ],
    })
    path = tmp_path / "browser-session.json"
    path.write_text(
        '{"schema_version":"production-os/browser-computer-session/v1",'
        '"last_url":"https://evil.example/private"}',
        encoding="utf-8",
    )

    assert _load_browser_session(path, plan) == {}


def test_browser_session_state_defaults_to_runtime_workspace(monkeypatch):
    from argparse import Namespace
    from production_os.cli import _browser_session_state

    monkeypatch.setenv(
        "PRODUCTION_OS_RUNTIME_WORKSPACE",
        "/var/lib/production-os/runtime/job-a",
    )
    args = Namespace(session_state="")

    assert _browser_session_state(args) == (
        "/var/lib/production-os/runtime/job-a/browser-session.json"
    )
