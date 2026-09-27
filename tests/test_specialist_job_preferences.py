from production_os.sqlite_backend import SQLiteBackend, SQLiteJobQueue


def queue(tmp_path):
    backend = SQLiteBackend(tmp_path / "jobs.sqlite")
    return SQLiteJobQueue(backend)


def test_claim_prefers_specialist_within_same_priority(tmp_path):
    q = queue(tmp_path)
    generic = q.enqueue({
        "idempotency_key":"generic",
        "handoff":{"repository":"o/a","task":"generic","priority":50},
        "preferred_capabilities":["code-implementation"],
    })
    specialist = q.enqueue({
        "idempotency_key":"specialist",
        "handoff":{"repository":"o/a","task":"debug","priority":50},
        "preferred_capabilities":["test-debug"],
    })

    claimed = q.claim_next(
        "worker-debug",
        capabilities=["test-debug"],
    )

    assert claimed["key"] == specialist["key"]
    assert q.get(generic["key"])["status"] == "queued"


def test_claim_keeps_higher_priority_ahead_of_specialization(tmp_path):
    q = queue(tmp_path)
    high = q.enqueue({
        "idempotency_key":"high",
        "handoff":{"repository":"o/a","task":"urgent","priority":100},
        "preferred_capabilities":[],
    })
    q.enqueue({
        "idempotency_key":"lower-specialist",
        "handoff":{"repository":"o/a","task":"debug","priority":50},
        "preferred_capabilities":["test-debug"],
    })

    claimed = q.claim_next(
        "worker-debug",
        capabilities=["test-debug"],
    )

    assert claimed["key"] == high["key"]


def test_claim_falls_back_to_generic_worker_when_preference_not_available(tmp_path):
    q = queue(tmp_path)
    job = q.enqueue({
        "idempotency_key":"review",
        "handoff":{"repository":"o/a","task":"review","priority":50},
        "preferred_capabilities":["code-review"],
    })

    claimed = q.claim_next(
        "worker-generic",
        capabilities=[],
    )

    assert claimed["key"] == job["key"]


def test_required_capability_remains_strict(tmp_path):
    q = queue(tmp_path)
    q.enqueue({
        "idempotency_key":"visual",
        "handoff":{"repository":"o/a","task":"visual","priority":50},
        "required_capabilities":["visual-asset-production"],
        "preferred_capabilities":["visual-asset-production"],
    })

    assert q.claim_next("worker-generic", capabilities=[]) is None
