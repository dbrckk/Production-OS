from __future__ import annotations

import json
import threading
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from production_os.api_auth import TokenAuthorizer, token_digest
from production_os.control_plane import ControlPlane, make_handler


def _auth():
    return TokenAuthorizer([
        {"name":"operator","role":"operator","sha256":token_digest("operator-token")},
        {"name":"worker-a","role":"worker","sha256":token_digest("worker-a-token")},
        {"name":"worker-b","role":"worker","sha256":token_digest("worker-b-token")},
        {"name":"viewer","role":"viewer","sha256":token_digest("viewer-token")},
    ])


@pytest.fixture()
def running_control_plane(tmp_path):
    control = ControlPlane(str(tmp_path / "db.sqlite"), authorizer=_auth())
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(control))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}", control
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def get_api(base, path, token):
    req = Request(base + path, method="GET", headers=(
        {"Authorization":f"Bearer {token}"} if token else {}
    ))
    try:
        with urlopen(req, timeout=3) as res:
            return res.status, json.loads(res.read())
    except HTTPError as exc:
        return exc.code, json.loads(exc.read())


def api(base, path, token, body):
    data = json.dumps(body).encode()
    req = Request(base + path, data=data, method="POST", headers={
        "Content-Type":"application/json",
        **({"Authorization":f"Bearer {token}"} if token else {}),
    })
    try:
        with urlopen(req, timeout=3) as res:
            return res.status, json.loads(res.read())
    except HTTPError as exc:
        return exc.code, json.loads(exc.read())


def _owned_execution(control):
    control.workers.register("worker-a", ["python"], 1)
    job = control.queue.enqueue({"idempotency_key":"job-telemetry", "handoff":{"repository":"dbrckk/example","task":"ship"}, "workflow_id":"wf"})
    claimed = control.queue.claim_next("worker-a", capabilities=["python"])
    acked = control.queue.ack(claimed["key"], "worker-a")
    control.dashboard_store.start_execution(acked, "worker-a")
    return acked


def test_worker_can_publish_owned_job_telemetry(running_control_plane):
    base, control = running_control_plane
    job = _owned_execution(control)
    status, payload = api(base, f"/v1/jobs/{job['key']}/telemetry", "worker-a-token", {
        "worker_id":"worker-a", "stage":"implementation", "progress":42,
        "usage":{"total_tokens":1234},
        "logs":[{"level":"info","message":"Round 2 complete"}],
    })
    assert status == 200
    assert payload["execution"]["progress_percent"] == 42
    assert control.dashboard_store.logs_for_worker("worker-a")[0]["message"] == "Round 2 complete"


def test_other_worker_and_viewer_cannot_publish_telemetry(running_control_plane):
    base, control = running_control_plane
    job = _owned_execution(control)
    status, _ = api(base, f"/v1/jobs/{job['key']}/telemetry", "worker-b-token", {
        "worker_id":"worker-b", "progress":10,
    })
    assert status == 409
    status, _ = api(base, f"/v1/jobs/{job['key']}/telemetry", "viewer-token", {
        "worker_id":"worker-a", "progress":10,
    })
    assert status == 403
    status, _ = api(base, f"/v1/jobs/{job['key']}/telemetry", None, {
        "worker_id":"worker-a", "progress":10,
    })
    assert status == 401


def test_heartbeat_persists_only_authenticated_quota_values(running_control_plane):
    base, control = running_control_plane
    control.workers.register("worker-a", ["python"], 1)
    status, _ = api(base, "/v1/workers/heartbeat", "worker-a-token", {
        "worker_id":"worker-a",
        "capacity":{"source":"studio","status":"ok","authenticated_usage":True,
                    "used_this_month":100,"remaining_tokens":900},
    })
    assert status == 200
    quota = control.dashboard_store.latest_provider_quota_snapshots()[0]
    assert quota["remaining_value"] == 900
    assert quota["limit_value"] == 1000
    assert quota["source_status"] == "authenticated"


def test_dashboard_overview_requires_viewer_and_has_stable_envelope(running_control_plane):
    base, _ = running_control_plane
    status, payload = get_api(base, "/v1/dashboard/overview?window=7d", "viewer-token")
    assert status == 200
    assert payload["schema_version"] == "production-os/dashboard-overview/v1"
    assert set(("workers","productions","usage","commits","performance","projects","errors")) <= set(payload)
    assert get_api(base, "/v1/dashboard/overview?window=7d", "worker-a-token")[0] == 403
    assert get_api(base, "/v1/dashboard/overview?window=7d", None)[0] == 401


def test_dashboard_rejects_invalid_window(running_control_plane):
    base, _ = running_control_plane
    assert get_api(base, "/v1/dashboard/overview?window=2h", "viewer-token")[0] == 400


def test_dashboard_worker_routes_and_unknown_worker(running_control_plane):
    base, control = running_control_plane
    control.workers.register("worker-a", ["python"], 1)
    assert get_api(base, "/v1/dashboard/workers", "viewer-token")[0] == 200
    status, payload = get_api(base, "/v1/dashboard/workers/worker-a", "viewer-token")
    assert status == 200 and payload["worker"]["worker_id"] == "worker-a"
    assert get_api(base, "/v1/dashboard/workers/missing", "viewer-token")[0] == 404
    status, payload = get_api(base, "/v1/dashboard/workers/worker-a/logs?limit=999999", "viewer-token")
    assert status == 200
    assert payload["limit"] == 500
    assert get_api(base, "/v1/dashboard/workers/worker-a/usage?window=30d", "viewer-token")[0] == 200


def test_dashboard_project_and_activity_routes(running_control_plane):
    base, control = running_control_plane
    assert get_api(base, "/v1/dashboard/projects", "viewer-token")[0] == 200
    assert get_api(base, "/v1/dashboard/projects/dbrckk/missing", "viewer-token")[0] == 404
    assert get_api(base, "/v1/dashboard/activity?limit=999999", "viewer-token")[0] == 200
    for suffix in ("progress","commits?window=30d","usage?window=30d","workflows","history"):
        status, _ = get_api(base, "/v1/dashboard/projects/dbrckk/missing/" + suffix, "viewer-token")
        assert status == 404


def test_dashboard_autopilot_queue_ranks_jobs_and_explains_worker_eligibility(
    running_control_plane,
):
    base, control = running_control_plane
    control.workers.register("worker-a", ["python"], 1)
    control.workers.register("worker-b", ["node"], 1)

    low = control.queue.enqueue({
        "idempotency_key":"autopilot-low",
        "handoff":{"repository":"dbrckk/example","task":"Low","priority":1},
        "required_capabilities":["python"],
    })
    high = control.queue.enqueue({
        "idempotency_key":"autopilot-high",
        "handoff":{"repository":"dbrckk/example","task":"High","priority":10},
        "required_capabilities":["python"],
    })

    status, payload = get_api(
        base,
        "/v1/dashboard/autopilot?limit=20",
        "viewer-token",
    )
    assert status == 200
    assert payload["schema_version"] == "production-os/dashboard-autopilot/v1"
    assert [row["job_key"] for row in payload["jobs"]][:2] == [
        high["key"],
        low["key"],
    ]
    assert payload["jobs"][0]["preferred_worker"] == "worker-a"
    assert payload["jobs"][0]["eligible_workers"] == ["worker-a"]
    assert payload["jobs"][0]["wait_reason"] is None


def test_dashboard_autopilot_respects_pause_capacity_and_capabilities(
    running_control_plane,
):
    base, control = running_control_plane
    control.workers.register("worker-a", ["python"], 1)
    control.workers.register("worker-b", ["node"], 1)
    control.dashboard_control.set_worker_state(
        "worker-a",
        "paused",
        requested_by="operator:test",
    )

    paused_job = control.queue.enqueue({
        "idempotency_key":"autopilot-paused",
        "handoff":{"repository":"dbrckk/example","task":"Paused","priority":30},
        "required_capabilities":["python"],
    })
    missing_job = control.queue.enqueue({
        "idempotency_key":"autopilot-missing",
        "handoff":{"repository":"dbrckk/example","task":"Android","priority":20},
        "required_capabilities":["android"],
    })

    status, payload = get_api(
        base,
        "/v1/dashboard/autopilot",
        "viewer-token",
    )
    assert status == 200
    rows = {row["job_key"]:row for row in payload["jobs"]}
    assert rows[paused_job["key"]]["wait_reason"] == "worker_controlled"
    assert rows[missing_job["key"]]["wait_reason"] == "missing_capability"

    control.dashboard_control.set_worker_state(
        "worker-a",
        "active",
        requested_by="operator:test",
    )
    control.workers.heartbeat("worker-a", active_tasks=1)
    status, payload = get_api(
        base,
        "/v1/dashboard/autopilot",
        "viewer-token",
    )
    rows = {row["job_key"]:row for row in payload["jobs"]}
    assert rows[paused_job["key"]]["wait_reason"] == "capacity_full"


def test_dashboard_autopilot_honors_assigned_worker_and_access_rules(
    running_control_plane,
):
    base, control = running_control_plane
    control.workers.register("worker-a", ["python"], 1)
    control.workers.register("worker-b", ["python"], 1)

    job = control.queue.enqueue({
        "idempotency_key":"autopilot-assigned",
        "handoff":{"repository":"dbrckk/example","task":"Pinned","priority":50},
        "required_capabilities":["python"],
        "worker_id":"worker-b",
    })
    status, payload = get_api(
        base,
        "/v1/dashboard/autopilot",
        "viewer-token",
    )
    assert status == 200
    row = next(item for item in payload["jobs"] if item["job_key"] == job["key"])
    assert row["assigned_worker"] == "worker-b"
    assert row["eligible_workers"] == ["worker-b"]
    assert row["preferred_worker"] == "worker-b"

    assert get_api(
        base,
        "/v1/dashboard/autopilot",
        "worker-a-token",
    )[0] == 403
    assert get_api(
        base,
        "/v1/dashboard/autopilot?limit=0",
        "viewer-token",
    )[0] == 200


def test_dashboard_autopilot_survives_stale_workflow_reference(
    running_control_plane,
):
    base, control = running_control_plane
    control.workers.register("worker-a", ["python"], 1)

    stale = control.queue.enqueue({
        "idempotency_key":"autopilot-stale",
        "handoff":{"repository":"dbrckk/example","task":"Stale workflow","priority":80},
        "workflow_id":"missing-workflow",
        "workflow_task_id":"task-a",
        "required_capabilities":["python"],
    })
    healthy = control.queue.enqueue({
        "idempotency_key":"autopilot-healthy",
        "handoff":{"repository":"dbrckk/example","task":"Healthy","priority":10},
        "required_capabilities":["python"],
    })

    status, payload = get_api(
        base,
        "/v1/dashboard/autopilot",
        "viewer-token",
    )
    assert status == 200
    rows = {row["job_key"]:row for row in payload["jobs"]}
    assert rows[stale["key"]]["ranking_status"] == "degraded"
    assert rows[stale["key"]]["ranking_error"] == "workflow_unavailable"
    assert rows[stale["key"]]["score"] == 80.0
    assert rows[healthy["key"]]["ranking_status"] == "ok"
    assert rows[healthy["key"]]["preferred_worker"] == "worker-a"


def test_dashboard_autopilot_summary_reports_capacity_and_eta(
    running_control_plane,
):
    base, control = running_control_plane
    control.workers.register("worker-a", ["python"], 2)
    control.workers.heartbeat("worker-a", active_tasks=1)
    control.queue.enqueue({
        "idempotency_key":"autopilot-summary-ready",
        "handoff":{
            "repository":"dbrckk/example",
            "task":"Ready",
            "priority":20,
            "estimated_minutes":4,
        },
        "required_capabilities":["python"],
    })
    control.queue.enqueue({
        "idempotency_key":"autopilot-summary-blocked",
        "handoff":{
            "repository":"dbrckk/example",
            "task":"Blocked",
            "priority":10,
            "estimated_minutes":6,
        },
        "required_capabilities":["android"],
    })

    status, payload = get_api(
        base,
        "/v1/dashboard/autopilot",
        "viewer-token",
    )
    assert status == 200
    summary = payload["summary"]
    assert summary["ready_now"] == 1
    assert summary["blocked"] == 1
    assert summary["free_slots"] == 1
    assert summary["known_eta_minutes"] == 10.0
    assert summary["eta_coverage_jobs"] == 2
    assert summary["eta_total_jobs"] == 2


def test_dashboard_health_requires_viewer_and_has_stable_shape(running_control_plane):
    base, _ = running_control_plane
    status, payload = get_api(base, "/v1/dashboard/health", "viewer-token")
    assert status == 200
    assert payload["status"] in {"healthy", "degraded"}
    assert isinstance(payload["reasons"], list)
    assert get_api(base, "/v1/dashboard/health", "worker-a-token")[0] == 403


def test_worker_detail_includes_recoverable_jobs(running_control_plane):
    base, control = running_control_plane
    control.workers.register("worker-a", ["python"], 1)
    job = control.queue.enqueue({
        "handoff":{"repository":"dbrckk/example","task":"expired claim"},
        "required_capabilities":["python"],
    })
    assert control.queue.claim_key(job["key"], "worker-a") is not None
    with control.backend.transaction() as db:
        db.execute(
            "UPDATE jobs SET ack_deadline=? WHERE key=?",
            ("2000-01-01T00:00:00+00:00", job["key"]),
        )
    status, payload = get_api(
        base,
        "/v1/dashboard/workers/worker-a",
        "viewer-token",
    )
    assert status == 200
    assert [row["key"] for row in payload["recoverable_jobs"]] == [job["key"]]

def test_one_tap_launch_creates_persistent_managed_project_with_server_defaults(
    running_control_plane,
):
    base, control = running_control_plane

    status, payload = api(
        base,
        "/v1/dashboard/launch",
        "viewer-token",
        {
            "repository":"dbrckk/example",
            "instruction":"Implement the requested feature and validate it.",
        },
    )
    assert status == 403

    status, payload = api(
        base,
        "/v1/dashboard/launch",
        "operator-token",
        {
            "repository":"dbrckk/example",
            "instruction":"",
        },
    )
    assert status == 400

    status, payload = api(
        base,
        "/v1/dashboard/launch",
        "operator-token",
        {
            "repository":"dbrckk/example",
            "instruction":"Implement the requested feature and validate it.",
            "token_budget":999999,
            "agent_preference":"codex",
        },
    )
    assert status == 201
    project = payload["project"]
    launch = payload["launch"]
    assert project["repository"] == "dbrckk/example"
    assert project["final_goal"] == "Implement the requested feature and validate it."
    assert project["status"] == "ACTIVE"
    assert project["generation"] == 1
    assert project["current_workflow_id"]
    assert project["token_budget"] == 30000
    assert project["agent_preference"] == "auto"
    assert launch == {
        "mode":"managed-project",
        "persistent":True,
        "token_budget":30000,
        "agent_preference":"auto",
    }

    persisted = control.managed_projects.get(project["project_id"])
    assert persisted["project_id"] == project["project_id"]
    assert persisted["current_workflow_id"] == project["current_workflow_id"]
    assert persisted["runs"][0]["kind"] == "initial"

def test_attention_feed_is_viewer_visible_and_worker_forbidden(running_control_plane):
    base, _control = running_control_plane

    status, payload = get_api(
        base,
        "/v1/dashboard/attention?limit=20",
        "viewer-token",
    )
    assert status == 200
    assert payload["schema_version"] == "production-os/dashboard-attention/v1"
    assert "summary" in payload
    assert "items" in payload

    status, payload = get_api(
        base,
        "/v1/dashboard/attention?limit=20",
        "worker-a-token",
    )
    assert status == 403
    assert payload["required_role"] == "viewer"

def test_attention_action_metadata_does_not_bypass_operator_permissions(
    running_control_plane,
):
    base, _control = running_control_plane

    status, created = api(
        base,
        "/v1/managed-projects",
        "operator-token",
        {
            "repository":"dbrckk/attention-permissions",
            "final_goal":"Validate attention action permissions.",
            "token_budget":30000,
            "agent_preference":"auto",
        },
    )
    assert status == 201
    project_id = created["project"]["project_id"]

    status, payload = get_api(
        base,
        "/v1/dashboard/attention?limit=50",
        "viewer-token",
    )
    assert status == 200
    assert payload["schema_version"] == "production-os/dashboard-attention/v1"

    status, payload = api(
        base,
        f"/v1/managed-projects/{project_id}/verify",
        "viewer-token",
        {},
    )
    assert status == 403
    assert payload["required_role"] == "operator"

def test_launch_readiness_endpoint_is_viewer_visible_and_worker_forbidden(
    running_control_plane,
):
    base, control = running_control_plane
    control.dashboard.launch_readiness = lambda repository: {
        "schema_version":"production-os/launch-readiness/v1",
        "repository":repository,
        "can_launch":True,
        "execution":"queued",
        "available_workers":0,
        "online_workers":0,
        "queued_jobs":0,
        "message":"queued",
        "generated_at":"2026-09-25T19:00:00+00:00",
    }

    status, payload = get_api(
        base,
        "/v1/dashboard/launch-readiness?repository=dbrckk%2Fexample",
        "viewer-token",
    )
    assert status == 200
    assert payload["repository"] == "dbrckk/example"
    assert payload["execution"] == "queued"

    status, payload = get_api(
        base,
        "/v1/dashboard/launch-readiness?repository=dbrckk%2Fexample",
        "worker-a-token",
    )
    assert status == 403
    assert payload["required_role"] == "viewer"

def test_production_status_endpoint_is_viewer_visible_and_worker_forbidden(
    running_control_plane,
):
    base, control = running_control_plane
    control.dashboard.production_status = lambda project_id: {
        "schema_version":"production-os/production-status/v1",
        "project":{"project_id":project_id},
        "runtime":{
            "phase":"running",
            "message":"En cours · implementation · 50 %",
            "worker_id":"worker-a",
            "attempt":1,
            "stage":"implementation",
            "progress_percent":50.0,
        },
        "generated_at":"2026-09-25T19:00:00+00:00",
    }

    status, payload = get_api(
        base,
        "/v1/dashboard/production-status?project_id=project-live",
        "viewer-token",
    )
    assert status == 200
    assert payload["project"]["project_id"] == "project-live"
    assert payload["runtime"]["phase"] == "running"

    status, payload = get_api(
        base,
        "/v1/dashboard/production-status?project_id=project-live",
        "worker-a-token",
    )
    assert status == 403
    assert payload["required_role"] == "viewer"

def test_one_tap_launch_request_id_is_idempotent_and_conflict_safe(
    running_control_plane,
):
    base, control = running_control_plane
    request_id = "android-retry-20260925-001"
    body = {
        "repository":"dbrckk/idempotent",
        "instruction":"Implement exactly once.",
        "request_id":request_id,
    }

    first_status, first = api(
        base,
        "/v1/dashboard/launch",
        "operator-token",
        body,
    )
    replay_status, replay = api(
        base,
        "/v1/dashboard/launch",
        "operator-token",
        body,
    )

    assert first_status == 201
    assert replay_status == 201
    assert first["project"]["project_id"] == replay["project"]["project_id"]
    assert first["project"]["workflow_id"] == replay["project"]["workflow_id"]
    assert first["launch"]["request_id"] == request_id
    assert first["launch"]["idempotent"] is True
    assert replay["launch"]["request_id"] == request_id

    with control.backend.connect() as db:
        assert db.execute(
            "SELECT COUNT(*) AS count FROM managed_projects WHERE repository=?",
            ("dbrckk/idempotent",),
        ).fetchone()["count"] == 1
        assert db.execute(
            "SELECT COUNT(*) AS count FROM jobs WHERE repository=?",
            ("dbrckk/idempotent",),
        ).fetchone()["count"] == 1

    status, payload = api(
        base,
        "/v1/dashboard/launch",
        "operator-token",
        {
            "repository":"dbrckk/idempotent",
            "instruction":"A different instruction must not reuse the request.",
            "request_id":request_id,
        },
    )
    assert status == 409
    assert "different launch parameters" in payload["error"]


def test_one_tap_launch_rejects_invalid_request_id(running_control_plane):
    base, _control = running_control_plane

    status, payload = api(
        base,
        "/v1/dashboard/launch",
        "operator-token",
        {
            "repository":"dbrckk/example",
            "instruction":"Ship",
            "request_id":"../bad",
        },
    )
    assert status == 400
    assert payload["error"] == "request_id is invalid"

def test_managed_production_cancel_requires_operator_and_exact_confirmation(
    running_control_plane,
):
    base, control = running_control_plane
    project = control.managed_projects.create(
        repository="dbrckk/cancel-api",
        final_goal="Cancel this queued production.",
        token_budget=30000,
        agent_preference="auto",
    )
    project_id = project["project_id"]

    status, payload = api(
        base,
        f"/v1/managed-projects/{project_id}/cancel",
        "viewer-token",
        {"confirm":"CANCEL_ACTIVE_PRODUCTION"},
    )
    assert status == 403

    status, payload = api(
        base,
        f"/v1/managed-projects/{project_id}/cancel",
        "operator-token",
        {"confirm":"wrong"},
    )
    assert status == 400
    assert "CANCEL_ACTIVE_PRODUCTION" in payload["error"]

    status, payload = api(
        base,
        f"/v1/managed-projects/{project_id}/cancel",
        "operator-token",
        {"confirm":"CANCEL_ACTIVE_PRODUCTION"},
    )
    assert status == 200
    assert payload["status"] == "cancelled"
    assert payload["project"]["status"] == "NEEDS_ATTENTION"
    assert payload["project"]["current_workflow"]["status"] == "cancelled"

    status, replay = api(
        base,
        f"/v1/managed-projects/{project_id}/cancel",
        "operator-token",
        {"confirm":"CANCEL_ACTIVE_PRODUCTION"},
    )
    assert status == 200
    assert replay["status"] == "cancelled"

    audit = control.dashboard_store.control_audit_events(limit=10)
    assert any(
        row["action"] == "cancel-production"
        and row["outcome"] == "cancelled"
        for row in audit
    )

def test_production_inbox_is_viewer_visible_and_worker_forbidden(
    running_control_plane,
):
    base, control = running_control_plane
    control.managed_projects.create(
        repository="dbrckk/inbox-api",
        final_goal="Show server production.",
        token_budget=30000,
        agent_preference="auto",
    )

    status, payload = get_api(
        base,
        "/v1/dashboard/productions?limit=20",
        "viewer-token",
    )
    assert status == 200
    assert payload["schema_version"] == "production-os/production-inbox/v1"
    assert payload["summary"]["visible"] == 1
    assert payload["items"][0]["repository"] == "dbrckk/inbox-api"

    status, payload = get_api(
        base,
        "/v1/dashboard/productions?limit=20",
        "worker-a-token",
    )
    assert status == 403
    assert payload["required_role"] == "viewer"

def test_production_inbox_query_parameters_reach_server_search_and_sort(
    running_control_plane,
):
    base, control = running_control_plane
    control.managed_projects.create(
        repository="dbrckk/navigation-alpha",
        final_goal="Ship the searchable alpha target.",
        token_budget=30000,
        agent_preference="auto",
    )
    control.managed_projects.create(
        repository="dbrckk/navigation-beta",
        final_goal="Ship an unrelated beta target.",
        token_budget=30000,
        agent_preference="auto",
    )

    status, payload = get_api(
        base,
        (
            "/v1/dashboard/productions"
            "?limit=20&filter=active&q=SEARCHABLE%20ALPHA&sort=recent"
        ),
        "viewer-token",
    )

    assert status == 200
    assert payload["filter"] == "active"
    assert payload["search"] == "SEARCHABLE ALPHA"
    assert payload["sort"] == "recent"
    assert payload["summary"]["matching"] == 1
    assert payload["summary"]["total"] == 2
    assert [row["repository"] for row in payload["items"]] == [
        "dbrckk/navigation-alpha"
    ]


def test_production_inbox_rejects_invalid_sort_over_http(running_control_plane):
    base, _control = running_control_plane

    status, payload = get_api(
        base,
        "/v1/dashboard/productions?sort=oldest",
        "viewer-token",
    )

    assert status == 400
    assert payload["error"] == "invalid dashboard query"

