import pytest

from production_os.browser_computer import (
    BROWSER_PLAN_SCHEMA,
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
