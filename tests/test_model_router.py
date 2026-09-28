from production_os.dashboard_store import DashboardStore
from production_os.model_router import ModelRouter, ROUTE_SCHEMA
from production_os.sqlite_backend import SQLiteBackend, SQLiteJobQueue
from production_os.workflow_engine import WorkflowEngine, WorkflowTaskSpec


def _backend(tmp_path):
    return SQLiteBackend(tmp_path / "router.sqlite")


def _job(key, repository="owner/repo"):
    return {
        "key":key,
        "repository":repository,
        "delivery_attempt":1,
        "payload":{},
    }


def _finish(store, key, provider, model, *, status="succeeded", cost=0.0, duration=10):
    store.start_execution(_job(key), "worker-a")
    return store.finish_execution(
        key,
        "worker-a",
        status=status,
        duration_seconds=duration,
        result={
            "usage":{
                "provider":provider,
                "model":model,
                "api_calls":1,
                "input_tokens":10,
                "cached_input_tokens":0,
                "output_tokens":10,
                "reasoning_tokens":0,
                "total_tokens":20,
                "estimated_cost_usd":cost,
            },
        },
    )


def test_router_prefers_capable_free_candidate_without_history(tmp_path):
    router = ModelRouter(_backend(tmp_path))

    route = router.route(
        [
            {
                "provider":"paid",
                "model":"strong",
                "capabilities":["code-implementation"],
                "free":False,
            },
            {
                "provider":"free",
                "model":"capable",
                "capabilities":["code-implementation"],
                "free":True,
            },
        ],
        required_capabilities=["code-implementation"],
    )

    assert route["schema_version"] == ROUTE_SCHEMA
    assert route["provider"] == "free"
    assert route["model"] == "capable"
    assert route["fallbacks"] == [{"provider":"paid","model":"strong"}]


def test_router_uses_success_history_between_equally_free_candidates(tmp_path):
    backend = _backend(tmp_path)
    store = DashboardStore(backend)
    for index in range(4):
        _finish(store, f"good-{index}", "p1", "m1", status="succeeded")
    for index in range(3):
        _finish(store, f"bad-{index}", "p2", "m2", status="failed")

    route = ModelRouter(backend).route([
        {"provider":"p1","model":"m1","free":True},
        {"provider":"p2","model":"m2","free":True},
    ])

    assert (route["provider"], route["model"]) == ("p1", "m1")
    ranking = {
        (row["provider"], row["model"]):row
        for row in route["ranking"]
    }
    assert ranking[("p1","m1")]["historical_success_rate"] == 1.0
    assert ranking[("p2","m2")]["historical_success_rate"] == 0.0


def test_router_rejects_exhausted_authenticated_provider_quota(tmp_path):
    backend = _backend(tmp_path)
    store = DashboardStore(backend)
    store.save_provider_quota_snapshot({
        "id":"quota-a",
        "provider":"exhausted",
        "quota_type":"tokens",
        "used_value":100,
        "limit_value":100,
        "remaining_value":0,
        "unit":"tokens",
        "source_status":"authenticated",
        "captured_at":"2026-09-28T07:00:00+00:00",
    })

    route = ModelRouter(backend).route([
        {"provider":"exhausted","model":"m1","free":True},
        {"provider":"available","model":"m2","free":False},
    ])

    assert route["provider"] == "available"
    assert route["rejected"] == [{
        "provider":"exhausted",
        "model":"m1",
        "reason":"provider quota is exhausted",
    }]


def test_router_filters_candidates_without_required_capabilities(tmp_path):
    router = ModelRouter(_backend(tmp_path))

    route = router.route(
        [
            {"provider":"text","model":"m1","capabilities":["text"],"free":True},
            {
                "provider":"code",
                "model":"m2",
                "capabilities":["code-implementation"],
                "free":False,
            },
        ],
        required_capabilities=["code-implementation"],
    )

    assert route["provider"] == "code"
    assert route["rejected"][0]["reason"] == (
        "candidate does not satisfy required capabilities"
    )


def test_workflow_dispatch_injects_model_route_without_changing_capabilities(tmp_path):
    backend = _backend(tmp_path)
    engine = WorkflowEngine(backend, SQLiteJobQueue(backend))
    workflow = engine.create(
        name="model-route",
        repository="owner/repo",
        tasks=[
            WorkflowTaskSpec(
                task_id="code",
                title="Implement feature",
                payload={
                    "handoff":{
                        "repository":"owner/repo",
                        "task":"Implement feature",
                        "required_capabilities":["code-implementation"],
                        "preferred_capabilities":["test-debug"],
                        "model_candidates":[
                            {
                                "provider":"free",
                                "model":"qwen-code",
                                "capabilities":[
                                    "code-implementation",
                                    "test-debug",
                                ],
                                "free":True,
                            },
                            {
                                "provider":"fallback",
                                "model":"fallback-code",
                                "capabilities":["code-implementation"],
                                "free":False,
                            },
                        ],
                    },
                },
            ),
        ],
    )

    job = engine.dispatch_ready(workflow["id"], limit=1)[0]
    handoff = job["payload"]["handoff"]

    assert handoff["model_route"]["provider"] == "free"
    assert handoff["model_route"]["model"] == "qwen-code"
    assert handoff["model_route"]["fallbacks"] == [
        {"provider":"fallback","model":"fallback-code"}
    ]
    assert job["payload"]["required_capabilities"] == ["code-implementation"]


def test_workflow_without_candidates_keeps_existing_handoff_shape(tmp_path):
    backend = _backend(tmp_path)
    engine = WorkflowEngine(backend, SQLiteJobQueue(backend))
    workflow = engine.create(
        name="no-route",
        repository="owner/repo",
        tasks=[
            WorkflowTaskSpec(
                task_id="plain",
                title="Plain task",
                payload={
                    "handoff":{
                        "repository":"owner/repo",
                        "task":"Plain task",
                    },
                },
            ),
        ],
    )

    job = engine.dispatch_ready(workflow["id"], limit=1)[0]

    assert "model_route" not in job["payload"]["handoff"]



def test_worker_catalog_is_deduplicated_and_reused_for_one_tap_dispatch(tmp_path):
    backend = _backend(tmp_path)
    router = ModelRouter(backend)
    candidates = [
        {
            "provider":"cloudflare",
            "model":"qwen-code",
            "capabilities":["code-implementation", "test-debug"],
            "free":True,
            "priority":20,
        },
        {
            "provider":"fallback",
            "model":"code-model",
            "capabilities":["code-implementation"],
            "free":False,
            "priority":5,
        },
    ]

    assert router.record_worker_catalog("worker-a", candidates) is True
    assert router.record_worker_catalog("worker-a", candidates) is False
    assert router.catalog_candidates() == candidates

    engine = WorkflowEngine(backend, SQLiteJobQueue(backend))
    workflow = engine.create(
        name="catalog-route",
        repository="owner/repo",
        tasks=[
            WorkflowTaskSpec(
                task_id="code",
                title="Implement",
                payload={
                    "handoff":{
                        "repository":"owner/repo",
                        "task":"Implement",
                        "required_capabilities":["code-implementation"],
                    },
                },
            ),
        ],
    )

    job = engine.dispatch_ready(workflow["id"], limit=1)[0]
    route = job["payload"]["handoff"]["model_route"]

    assert route["provider"] == "cloudflare"
    assert route["model"] == "qwen-code"
    assert route["fallbacks"] == [
        {"provider":"fallback","model":"code-model"}
    ]


def test_worker_catalog_never_blocks_task_when_no_candidate_fits(tmp_path):
    backend = _backend(tmp_path)
    router = ModelRouter(backend)
    router.record_worker_catalog(
        "worker-a",
        [
            {
                "provider":"text-only",
                "model":"general",
                "capabilities":["text"],
                "free":True,
            },
        ],
    )
    engine = WorkflowEngine(backend, SQLiteJobQueue(backend))
    workflow = engine.create(
        name="catalog-nonblocking",
        repository="owner/repo",
        tasks=[
            WorkflowTaskSpec(
                task_id="code",
                title="Implement",
                payload={
                    "handoff":{
                        "repository":"owner/repo",
                        "task":"Implement",
                        "required_capabilities":["code-implementation"],
                    },
                },
            ),
        ],
    )

    job = engine.dispatch_ready(workflow["id"], limit=1)[0]

    assert "model_route" not in job["payload"]["handoff"]


def test_explicit_model_candidates_override_worker_catalog(tmp_path):
    backend = _backend(tmp_path)
    ModelRouter(backend).record_worker_catalog(
        "worker-a",
        [
            {
                "provider":"catalog",
                "model":"catalog-model",
                "capabilities":["code-implementation"],
                "free":True,
            },
        ],
    )
    engine = WorkflowEngine(backend, SQLiteJobQueue(backend))
    workflow = engine.create(
        name="explicit-route",
        repository="owner/repo",
        tasks=[
            WorkflowTaskSpec(
                task_id="code",
                title="Implement",
                payload={
                    "handoff":{
                        "repository":"owner/repo",
                        "task":"Implement",
                        "required_capabilities":["code-implementation"],
                        "model_candidates":[
                            {
                                "provider":"explicit",
                                "model":"explicit-model",
                                "capabilities":["code-implementation"],
                                "free":False,
                            },
                        ],
                    },
                },
            ),
        ],
    )

    job = engine.dispatch_ready(workflow["id"], limit=1)[0]

    assert job["payload"]["handoff"]["model_route"]["provider"] == "explicit"
