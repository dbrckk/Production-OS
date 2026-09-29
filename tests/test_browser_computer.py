import pytest

from production_os.browser_computer import (
    BROWSER_PLAN_SCHEMA,
    BROWSER_SESSION_SCHEMA,
    BROWSER_CHECKPOINT_SCHEMA,
    BrowserRecoveryProbe,
    _browser_action_fingerprint,
    _browser_plan_fingerprint,
    _browser_page_snapshot,
    _evaluate_recovery_probe,
    _load_browser_checkpoint,
    _load_browser_session,
    _safe_resume_url,
    _write_browser_checkpoint,
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
    assert contract["checkpoint_actions"] is True
    assert contract["structured_snapshot"] is True
    assert contract["snapshot_action"] == "snapshot"
    assert contract["non_replayable_actions"] == ["click", "press"]
    assert contract["recovery_probes"] == [
        "selector_present",
        "selector_absent",
        "text_contains",
    ]
    assert contract["recovery_policy"] == "positive-proof-only"
    assert contract["arbitrary_evaluate"] is False
    assert contract["multi_turn"] == {
        "supported":True,
        "config_schema":"production-os/browser-computer-loop/v1",
        "turn_schema":"production-os/browser-computer-turn/v1",
        "turn_result_schema":"production-os/browser-computer-turn-result/v1",
        "loop_result_schema":"production-os/browser-computer-loop-result/v1",
        "transport":"jsonl-stdin-stdout",
        "max_turns":128,
        "turn_id_idempotency":{
            "supported":True,
            "requires_checkpoint_state":True,
        },
        "immutable_turn_plan_binding":{
            "supported":True,
            "requires_checkpoint_state":True,
        },
        "stop_after_runtime_failure":True,
    }



def test_browser_plan_cli_parses_runtime_paths():
    from production_os.cli import _parse_args

    args = _parse_args([
        "browser-plan-run",
        "--plan", "/tmp/plan.json",
        "--artifacts-dir", "/tmp/artifacts",
        "--storage-state", "/tmp/state.json",
        "--session-state", "/tmp/session.json",
        "--checkpoint-state", "/tmp/checkpoint.json",
    ])

    assert args.plan == "/tmp/plan.json"
    assert args.artifacts_dir == "/tmp/artifacts"
    assert args.storage_state == "/tmp/state.json"
    assert args.session_state == "/tmp/session.json"
    assert args.checkpoint_state == "/tmp/checkpoint.json"
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



def test_browser_plan_accepts_explicit_checkpoint_action():
    plan = validate_browser_plan({
        "schema_version":BROWSER_PLAN_SCHEMA,
        "allowed_hosts":["example.com"],
        "persist_session":True,
        "actions":[
            {"action":"navigate","url":"https://example.com/app"},
            {"action":"checkpoint"},
            {"action":"extract_text","selector":"main","name":"result"},
        ],
    })

    assert plan.actions[1].action == "checkpoint"


def test_browser_checkpoint_round_trips_only_matching_plan(tmp_path):
    plan = validate_browser_plan({
        "schema_version":BROWSER_PLAN_SCHEMA,
        "allowed_hosts":["example.com"],
        "persist_session":True,
        "actions":[
            {"action":"navigate","url":"https://example.com/app"},
            {"action":"checkpoint"},
            {"action":"extract_text","selector":"main","name":"result"},
        ],
    })
    checkpoint = tmp_path / "browser-checkpoint.json"

    written = _write_browser_checkpoint(
        checkpoint,
        plan=plan,
        next_action_index=2,
        last_url="https://example.com/app?token=secret#frag",
    )
    loaded = _load_browser_checkpoint(checkpoint, plan)

    assert written["schema_version"] == BROWSER_CHECKPOINT_SCHEMA
    assert written["last_url"] == "https://example.com/app"
    assert loaded["next_action_index"] == 2
    assert loaded["last_url"] == "https://example.com/app"
    payload = checkpoint.read_text(encoding="utf-8")
    assert "token=secret" not in payload

    changed_plan = validate_browser_plan({
        "schema_version":BROWSER_PLAN_SCHEMA,
        "allowed_hosts":["example.com"],
        "persist_session":True,
        "actions":[
            {"action":"navigate","url":"https://example.com/app"},
            {"action":"checkpoint"},
            {"action":"extract_text","selector":"aside","name":"result"},
        ],
    })
    assert _load_browser_checkpoint(checkpoint, changed_plan) == {}


def test_browser_plan_fingerprint_distinguishes_fill_values_without_storing_them():
    first = validate_browser_plan({
        "schema_version":BROWSER_PLAN_SCHEMA,
        "allowed_hosts":["example.com"],
        "persist_session":True,
        "actions":[
            {"action":"fill","selector":"#email","value":"alice@example.com"},
        ],
    })
    second = validate_browser_plan({
        "schema_version":BROWSER_PLAN_SCHEMA,
        "allowed_hosts":["example.com"],
        "persist_session":True,
        "actions":[
            {"action":"fill","selector":"#email","value":"other@example.com"},
        ],
    })

    assert _browser_plan_fingerprint(first) != _browser_plan_fingerprint(second)


def test_browser_checkpoint_state_defaults_to_runtime_workspace(monkeypatch):
    from argparse import Namespace
    from production_os.cli import _browser_checkpoint_state

    monkeypatch.setenv(
        "PRODUCTION_OS_RUNTIME_WORKSPACE",
        "/var/lib/production-os/runtime/job-a",
    )
    args = Namespace(checkpoint_state="")

    assert _browser_checkpoint_state(args) == (
        "/var/lib/production-os/runtime/job-a/browser-checkpoint.json"
    )



def test_browser_checkpoint_round_trips_uncertain_non_replayable_action(tmp_path):
    plan = validate_browser_plan({
        "schema_version":BROWSER_PLAN_SCHEMA,
        "allowed_hosts":["example.com"],
        "persist_session":True,
        "actions":[
            {"action":"navigate","url":"https://example.com/app"},
            {"action":"click","selector":"button[type=submit]"},
            {"action":"extract_text","selector":"main","name":"result"},
        ],
    })
    checkpoint = tmp_path / "browser-checkpoint.json"
    action = plan.actions[1]

    written = _write_browser_checkpoint(
        checkpoint,
        plan=plan,
        next_action_index=1,
        last_url="https://example.com/app",
        in_flight_action=action,
        in_flight_index=2,
    )
    loaded = _load_browser_checkpoint(checkpoint, plan)

    assert written["in_flight_action"] == {
        "index":2,
        "action":"click",
        "fingerprint":_browser_action_fingerprint(action),
    }
    assert loaded["next_action_index"] == 1
    assert loaded["in_flight_action"] == written["in_flight_action"]


def test_browser_checkpoint_rejects_tampered_uncertain_action_fingerprint(tmp_path):
    import json

    plan = validate_browser_plan({
        "schema_version":BROWSER_PLAN_SCHEMA,
        "allowed_hosts":["example.com"],
        "persist_session":True,
        "actions":[
            {"action":"navigate","url":"https://example.com/app"},
            {"action":"press","selector":"form","key":"Enter"},
        ],
    })
    checkpoint = tmp_path / "browser-checkpoint.json"
    _write_browser_checkpoint(
        checkpoint,
        plan=plan,
        next_action_index=1,
        last_url="https://example.com/app",
        in_flight_action=plan.actions[1],
        in_flight_index=2,
    )
    payload = json.loads(checkpoint.read_text(encoding="utf-8"))
    payload["in_flight_action"]["fingerprint"] = "0" * 64
    checkpoint.write_text(json.dumps(payload), encoding="utf-8")

    assert _load_browser_checkpoint(checkpoint, plan) == {}


def test_browser_checkpoint_completed_side_effect_clears_uncertain_marker(tmp_path):
    plan = validate_browser_plan({
        "schema_version":BROWSER_PLAN_SCHEMA,
        "allowed_hosts":["example.com"],
        "persist_session":True,
        "actions":[
            {"action":"navigate","url":"https://example.com/app"},
            {"action":"click","selector":"#save"},
            {"action":"checkpoint"},
        ],
    })
    checkpoint = tmp_path / "browser-checkpoint.json"
    _write_browser_checkpoint(
        checkpoint,
        plan=plan,
        next_action_index=1,
        last_url="https://example.com/app",
        in_flight_action=plan.actions[1],
        in_flight_index=2,
    )

    completed = _write_browser_checkpoint(
        checkpoint,
        plan=plan,
        next_action_index=2,
        last_url="https://example.com/app/saved",
    )
    loaded = _load_browser_checkpoint(checkpoint, plan)

    assert "in_flight_action" not in completed
    assert loaded["in_flight_action"] is None
    assert loaded["next_action_index"] == 2


def test_browser_checkpoint_rejects_inflight_marker_for_replayable_action(tmp_path):
    plan = validate_browser_plan({
        "schema_version":BROWSER_PLAN_SCHEMA,
        "allowed_hosts":["example.com"],
        "persist_session":True,
        "actions":[
            {"action":"navigate","url":"https://example.com/app"},
            {"action":"fill","selector":"#name","value":"Alice"},
        ],
    })

    with pytest.raises(ValueError, match="must be non-replayable"):
        _write_browser_checkpoint(
            tmp_path / "browser-checkpoint.json",
            plan=plan,
            next_action_index=1,
            last_url="https://example.com/app",
            in_flight_action=plan.actions[1],
            in_flight_index=2,
        )



def test_browser_click_accepts_positive_recovery_probe():
    plan = validate_browser_plan({
        "schema_version":BROWSER_PLAN_SCHEMA,
        "allowed_hosts":["example.com"],
        "persist_session":True,
        "actions":[
            {"action":"navigate","url":"https://example.com/settings"},
            {
                "action":"click",
                "selector":"#save",
                "recovery_probe":{
                    "kind":"text_contains",
                    "selector":"#status",
                    "value":"Saved",
                    "timeout_ms":4000,
                },
            },
        ],
    })

    probe = plan.actions[1].recovery_probe
    assert probe == BrowserRecoveryProbe(
        kind="text_contains",
        selector="#status",
        value="Saved",
        timeout_ms=4000,
    )
    assert plan.actions[1].to_dict()["recovery_probe"] == {
        "kind":"text_contains",
        "selector":"#status",
        "value":"Saved",
        "timeout_ms":4000,
    }


def test_browser_recovery_probe_is_rejected_for_replayable_action():
    with pytest.raises(
        ValueError,
        match="only valid for click or press",
    ):
        validate_browser_plan({
            "schema_version":BROWSER_PLAN_SCHEMA,
            "allowed_hosts":["example.com"],
            "actions":[
                {
                    "action":"fill",
                    "selector":"#name",
                    "value":"Alice",
                    "recovery_probe":{
                        "kind":"selector_present",
                        "selector":"#saved",
                    },
                },
            ],
        })


@pytest.mark.parametrize(
    "probe_payload,match",
    [
        (
            {"kind":"unknown","selector":"#status"},
            "unsupported browser recovery probe",
        ),
        (
            {"kind":"selector_present","selector":""},
            "requires selector",
        ),
        (
            {
                "kind":"text_contains",
                "selector":"#status",
                "value":"",
            },
            "requires value",
        ),
        (
            {
                "kind":"selector_present",
                "selector":"#status",
                "timeout_ms":99,
            },
            "timeout must be 100-30000",
        ),
    ],
)
def test_browser_recovery_probe_validation_rejects_malformed_probe(
    probe_payload,
    match,
):
    with pytest.raises(ValueError, match=match):
        validate_browser_plan({
            "schema_version":BROWSER_PLAN_SCHEMA,
            "allowed_hosts":["example.com"],
            "actions":[
                {
                    "action":"click",
                    "selector":"#save",
                    "recovery_probe":probe_payload,
                },
            ],
        })


class _FakeLocator:
    def __init__(self, *, attached=True, text=""):
        self.attached = attached
        self.text = text
        self.wait_calls = []

    def wait_for(self, *, state, timeout):
        self.wait_calls.append((state, timeout))
        if state == "attached" and not self.attached:
            raise RuntimeError("not attached")
        if state == "detached" and self.attached:
            raise RuntimeError("still attached")

    def inner_text(self, *, timeout):
        if not self.attached:
            raise RuntimeError("not attached")
        return self.text


class _FakePage:
    def __init__(self, locator):
        self._locator = locator

    def locator(self, selector):
        assert selector
        return self._locator


def test_browser_recovery_probe_evaluates_only_positive_evidence():
    assert _evaluate_recovery_probe(
        _FakePage(_FakeLocator(attached=True)),
        BrowserRecoveryProbe(
            kind="selector_present",
            selector="#saved",
        ),
    ) is True
    assert _evaluate_recovery_probe(
        _FakePage(_FakeLocator(attached=False)),
        BrowserRecoveryProbe(
            kind="selector_absent",
            selector="#save",
        ),
    ) is True
    assert _evaluate_recovery_probe(
        _FakePage(_FakeLocator(attached=True, text="Saved successfully")),
        BrowserRecoveryProbe(
            kind="text_contains",
            selector="#status",
            value="Saved",
        ),
    ) is True

    assert _evaluate_recovery_probe(
        _FakePage(_FakeLocator(attached=True, text="Still saving")),
        BrowserRecoveryProbe(
            kind="text_contains",
            selector="#status",
            value="Saved",
        ),
    ) is False


def test_recovery_probe_changes_browser_plan_fingerprint():
    without_probe = validate_browser_plan({
        "schema_version":BROWSER_PLAN_SCHEMA,
        "allowed_hosts":["example.com"],
        "actions":[
            {"action":"click","selector":"#save"},
        ],
    })
    with_probe = validate_browser_plan({
        "schema_version":BROWSER_PLAN_SCHEMA,
        "allowed_hosts":["example.com"],
        "actions":[
            {
                "action":"click",
                "selector":"#save",
                "recovery_probe":{
                    "kind":"selector_present",
                    "selector":"#saved",
                },
            },
        ],
    })

    assert _browser_plan_fingerprint(without_probe) != (
        _browser_plan_fingerprint(with_probe)
    )



class _SnapshotElement:
    def __init__(self, *, visible=True, text="", attributes=None):
        self.visible = visible
        self.text = text
        self.attributes = dict(attributes or {})

    def is_visible(self):
        return self.visible

    def inner_text(self, *, timeout):
        return self.text

    def get_attribute(self, name):
        return self.attributes.get(name)


class _SnapshotCollection:
    def __init__(self, elements):
        self.elements = list(elements)

    def count(self):
        return len(self.elements)

    def nth(self, index):
        return self.elements[index]


class _SnapshotBody:
    def __init__(self, text):
        self.text = text

    def inner_text(self, *, timeout):
        return self.text


class _SnapshotPage:
    def __init__(
        self,
        *,
        url,
        title,
        body_text,
        elements,
        selector_counts=None,
    ):
        self.url = url
        self._title = title
        self._body = _SnapshotBody(body_text)
        self._elements = _SnapshotCollection(elements)
        self._selector_counts = dict(selector_counts or {})

    def title(self):
        return self._title

    def locator(self, selector):
        if selector == "body":
            return self._body
        if selector in self._selector_counts:
            return _SnapshotCollection([
                _SnapshotElement()
                for _ in range(self._selector_counts[selector])
            ])
        return self._elements


def test_browser_plan_accepts_bounded_snapshot_action():
    plan = validate_browser_plan({
        "schema_version":BROWSER_PLAN_SCHEMA,
        "allowed_hosts":["example.com"],
        "actions":[
            {"action":"navigate","url":"https://example.com/app"},
            {"action":"snapshot","name":"observe"},
        ],
    })

    assert plan.actions[1].action == "snapshot"
    assert plan.actions[1].name == "observe"


def test_browser_snapshot_is_bounded_structured_and_omits_field_values():
    plan = validate_browser_plan({
        "schema_version":BROWSER_PLAN_SCHEMA,
        "allowed_hosts":["example.com"],
        "actions":[
            {"action":"snapshot","name":"observe"},
        ],
    })
    page = _SnapshotPage(
        url="https://example.com/app?token=secret#frag",
        title="Dashboard",
        body_text="Visible page text",
        elements=[
            _SnapshotElement(
                text="Save",
                attributes={
                    "id":"save",
                    "role":"button",
                    "aria-label":"Save changes",
                    "value":"TOP-SECRET",
                },
            ),
            _SnapshotElement(
                text="",
                attributes={
                    "name":"email",
                    "placeholder":"Email",
                    "type":"email",
                    "value":"alice@example.com",
                },
            ),
            _SnapshotElement(
                visible=False,
                text="Hidden",
                attributes={"id":"hidden"},
            ),
        ],
    )

    snapshot = _browser_page_snapshot(page, plan)

    assert snapshot["url"] == "https://example.com/app"
    assert snapshot["title"] == "Dashboard"
    assert snapshot["text_excerpt"] == "Visible page text"
    assert snapshot["element_count"] == 2
    assert snapshot["elements"][0]["text"] == "Save"
    assert snapshot["elements"][0]["aria_label"] == "Save changes"
    assert snapshot["elements"][1]["name"] == "email"
    assert snapshot["elements"][1]["placeholder"] == "Email"
    serialized = str(snapshot)
    assert "TOP-SECRET" not in serialized
    assert "alice@example.com" not in serialized
    assert "token=secret" not in serialized


def test_browser_snapshot_caps_elements_and_text():
    plan = validate_browser_plan({
        "schema_version":BROWSER_PLAN_SCHEMA,
        "allowed_hosts":["example.com"],
        "actions":[
            {"action":"snapshot","name":"observe"},
        ],
    })
    page = _SnapshotPage(
        url="https://example.com/",
        title="x" * 1000,
        body_text="y" * 60000,
        elements=[
            _SnapshotElement(text=f"item-{index}")
            for index in range(250)
        ],
    )

    snapshot = _browser_page_snapshot(
        page,
        plan,
        max_elements=10,
        max_text_chars=2000,
    )

    assert len(snapshot["title"]) == 500
    assert len(snapshot["text_excerpt"]) == 2000
    assert snapshot["element_count"] == 10
    assert snapshot["truncated"] is True
    assert snapshot["elements"][0]["selector"].endswith("nth=0")
    assert snapshot["elements"][-1]["selector"].endswith("nth=9")



def test_browser_snapshot_prefers_verified_unique_attribute_selector():
    plan = validate_browser_plan({
        "schema_version":BROWSER_PLAN_SCHEMA,
        "allowed_hosts":["example.com"],
        "actions":[{"action":"snapshot","name":"observe"}],
    })
    page = _SnapshotPage(
        url="https://example.com/app",
        title="App",
        body_text="",
        elements=[
            _SnapshotElement(
                text="Save",
                attributes={"id":"save", "name":"submit"},
            ),
        ],
        selector_counts={
            '[id="save"]':1,
            '[name="submit"]':1,
        },
    )

    snapshot = _browser_page_snapshot(page, plan)

    element = snapshot["elements"][0]
    assert element["selector"] == '[id="save"]'
    assert element["selector_stability"] == "attribute"


def test_browser_snapshot_falls_back_when_attribute_selector_is_not_unique():
    plan = validate_browser_plan({
        "schema_version":BROWSER_PLAN_SCHEMA,
        "allowed_hosts":["example.com"],
        "actions":[{"action":"snapshot","name":"observe"}],
    })
    page = _SnapshotPage(
        url="https://example.com/app",
        title="App",
        body_text="",
        elements=[
            _SnapshotElement(
                text="Save",
                attributes={"name":"action"},
            ),
            _SnapshotElement(
                text="Delete",
                attributes={"name":"action"},
            ),
        ],
        selector_counts={
            '[name="action"]':2,
        },
    )

    snapshot = _browser_page_snapshot(page, plan)

    assert snapshot["elements"][0]["selector"].endswith("nth=0")
    assert snapshot["elements"][0]["selector_stability"] == "positional"
    assert snapshot["elements"][1]["selector"].endswith("nth=1")


def test_browser_snapshot_selector_escapes_attribute_quotes():
    plan = validate_browser_plan({
        "schema_version":BROWSER_PLAN_SCHEMA,
        "allowed_hosts":["example.com"],
        "actions":[{"action":"snapshot","name":"observe"}],
    })
    page = _SnapshotPage(
        url="https://example.com/app",
        title="App",
        body_text="",
        elements=[
            _SnapshotElement(
                attributes={"aria-label":'Save "draft"'},
            ),
        ],
        selector_counts={
            '[aria-label="Save \\"draft\\""]':1,
        },
    )

    snapshot = _browser_page_snapshot(page, plan)

    assert snapshot["elements"][0]["selector"] == (
        '[aria-label="Save \\"draft\\""]'
    )
    assert snapshot["elements"][0]["selector_stability"] == "attribute"
