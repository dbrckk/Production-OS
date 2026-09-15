from production_os.release_ledger import ReleaseLedger
from production_os.sqlite_backend import SQLiteBackend, SQLiteJobQueue
from production_os.workflow_engine import WorkflowEngine


def ledger(tmp_path):
    backend = SQLiteBackend(tmp_path / "state.sqlite")
    return ReleaseLedger(
        backend,
        WorkflowEngine(backend, SQLiteJobQueue(backend)),
    )


def test_incident_history_is_hash_chained_and_verifiable(tmp_path, monkeypatch):
    item = ledger(tmp_path)
    reports = iter([
        {
            "schema_version": "production-os/trust-incident-report/v1",
            "incident_id": "trust-one",
            "generated_at": "2026-09-15T12:00:00+00:00",
            "severity": "medium",
            "valid": False,
            "scope": {},
            "counts": {"total_releases": 1, "matched_releases": 1, "affected_releases": 1},
            "summary": {"affected_repositories": ["org/a"], "affected_validators": [], "affected_builders": [], "reasons": {"compromised": 1}},
            "affected_releases": [{"release_id": "r1", "valid": False}],
        },
        {
            "schema_version": "production-os/trust-incident-report/v1",
            "incident_id": "trust-two",
            "generated_at": "2026-09-15T12:01:00+00:00",
            "severity": "medium",
            "valid": False,
            "scope": {},
            "counts": {"total_releases": 2, "matched_releases": 1, "affected_releases": 1},
            "summary": {"affected_repositories": ["org/b"], "affected_validators": [], "affected_builders": [], "reasons": {"revoked": 1}},
            "affected_releases": [{"release_id": "r2", "valid": False}],
        },
    ])
    monkeypatch.setattr(item, "incident_report", lambda **kwargs: next(reports))

    first = item.record_incident_report()
    second = item.record_incident_report()

    assert second["previous_hash"] == first["report_hash"]
    verification = item.verify_incident_history()
    assert verification["valid"] is True
    assert verification["entries"] == 2
    assert verification["head_hash"] == second["report_hash"]


def test_incident_history_detects_report_tampering(tmp_path, monkeypatch):
    item = ledger(tmp_path)
    report = {
        "schema_version": "production-os/trust-incident-report/v1",
        "incident_id": "trust-one",
        "generated_at": "2026-09-15T12:00:00+00:00",
        "severity": "medium",
        "valid": False,
        "scope": {},
        "counts": {"total_releases": 1, "matched_releases": 1, "affected_releases": 1},
        "summary": {"affected_repositories": ["org/a"], "affected_validators": [], "affected_builders": [], "reasons": {"compromised": 1}},
        "affected_releases": [{"release_id": "r1", "valid": False}],
    }
    monkeypatch.setattr(item, "incident_report", lambda **kwargs: report)
    item.record_incident_report()

    with item.backend.transaction() as db:
        row = db.execute(
            "SELECT sequence, report_json FROM trust_incident_reports LIMIT 1"
        ).fetchone()
        import json
        payload = json.loads(row["report_json"])
        payload["severity"] = "none"
        db.execute(
            "UPDATE trust_incident_reports SET report_json=? WHERE sequence=?",
            (json.dumps(payload), row["sequence"]),
        )

    verification = item.verify_incident_history()
    assert verification["valid"] is False
    assert verification["reason"] == "incident report hash mismatch"


def test_incident_snapshot_deduplicates_unchanged_state(tmp_path, monkeypatch):
    item = ledger(tmp_path)
    counter = {"n": 0}

    def report(**kwargs):
        counter["n"] += 1
        return {
            "schema_version": "production-os/trust-incident-report/v1",
            "incident_id": "trust-stable",
            "generated_at": f"2026-09-15T12:0{counter['n']}:00+00:00",
            "severity": "medium",
            "valid": False,
            "scope": {},
            "counts": {"total_releases": 1, "matched_releases": 1, "affected_releases": 1},
            "summary": {"affected_repositories": ["org/a"], "affected_validators": [], "affected_builders": [], "reasons": {"compromised": 1}},
            "affected_releases": [{"release_id": "r1", "valid": False}],
        }

    monkeypatch.setattr(item, "incident_report", report)
    first = item.record_incident_report()
    second = item.record_incident_report()

    assert first["recorded"] is True
    assert second["recorded"] is False
    assert second["deduplicated"] is True
    assert second["report_hash"] == first["report_hash"]
    assert len(item.incident_history()) == 1


def test_incident_snapshot_records_changed_blast_radius(tmp_path, monkeypatch):
    item = ledger(tmp_path)
    state = {"affected": 1}

    def report(**kwargs):
        n = state["affected"]
        releases = [
            {"release_id": f"r{i}", "valid": False}
            for i in range(1, n + 1)
        ]
        return {
            "schema_version": "production-os/trust-incident-report/v1",
            "incident_id": "trust-changing",
            "generated_at": "2026-09-15T12:00:00+00:00",
            "severity": "medium" if n < 3 else "high",
            "valid": False,
            "scope": {},
            "counts": {"total_releases": n, "matched_releases": n, "affected_releases": n},
            "summary": {"affected_repositories": ["org/a"], "affected_validators": [], "affected_builders": [], "reasons": {"compromised": n}},
            "affected_releases": releases,
        }

    monkeypatch.setattr(item, "incident_report", report)
    first = item.record_incident_report()
    state["affected"] = 3
    second = item.record_incident_report()

    assert first["recorded"] is True
    assert second["recorded"] is True
    assert second["deduplicated"] is False
    assert second["previous_hash"] == first["report_hash"]
    assert len(item.incident_history()) == 2
    assert item.verify_incident_history()["valid"] is True
