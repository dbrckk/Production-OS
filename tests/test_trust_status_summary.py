from production_os.release_ledger import ReleaseLedger


def test_trust_status_aggregates_affected_entities_and_reasons(monkeypatch):
    ledger = object.__new__(ReleaseLedger)
    rows = [
        {
            "id": "r1", "workflow_id": "w1", "artifact_id": "a1",
            "repository": "org/repo-a", "source_revision": "s1",
            "workflow_generation": 1, "validation_json": "{}",
            "metadata_json": '{"validation_attestation":{"validator_id":"v1"},"slsa_provenance":{"statement":{"predicate":{"runDetails":{"builder":{"id":"b1"}}}}}}',
            "status": "promoted", "rollback_of": None, "created_at": "2026-09-15T10:00:00+00:00",
        },
        {
            "id": "r2", "workflow_id": "w2", "artifact_id": "a2",
            "repository": "org/repo-a", "source_revision": "s2",
            "workflow_generation": 1, "validation_json": "{}",
            "metadata_json": '{"validation_attestation":{"validator_id":"v1"},"slsa_provenance":{"statement":{"predicate":{"runDetails":{"builder":{"id":"b1"}}}}}}',
            "status": "promoted", "rollback_of": None, "created_at": "2026-09-15T10:01:00+00:00",
        },
        {
            "id": "r3", "workflow_id": "w3", "artifact_id": "a3",
            "repository": "org/repo-b", "source_revision": "s3",
            "workflow_generation": 1, "validation_json": "{}",
            "metadata_json": '{"validation_attestation":{"validator_id":"v2"},"slsa_provenance":{"statement":{"predicate":{"runDetails":{"builder":{"id":"b2"}}}}}}',
            "status": "promoted", "rollback_of": None, "created_at": "2026-09-15T10:02:00+00:00",
        },
    ]

    class Result:
        def fetchall(self):
            return rows

    class DB:
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass

    class Backend:
        def connect(self):
            return DB()

    ledger.backend = Backend()
    monkeypatch.setattr(
        "production_os.release_ledger._execute",
        lambda *args, **kwargs: Result(),
    )
    outcomes = {
        "r1": {"valid": False, "reason": "signing key is compromised"},
        "r2": {"valid": False, "reason": "signing key is compromised"},
        "r3": {"valid": False, "reason": "untrusted SLSA provenance statement"},
    }
    ledger.verify = lambda release_id: outcomes[release_id]

    result = ledger.trust_status()

    assert result["affected_releases"] == 3
    assert result["severity"] == "high"
    assert result["summary"]["affected_repositories"] == [
        "org/repo-a", "org/repo-b"
    ]
    assert result["summary"]["affected_validators"] == ["v1", "v2"]
    assert result["summary"]["affected_builders"] == ["b1", "b2"]
    assert result["summary"]["reasons"] == {
        "signing key is compromised": 2,
        "untrusted SLSA provenance statement": 1,
    }


def test_incident_report_id_is_stable_for_same_blast_radius(monkeypatch):
    ledger = object.__new__(ReleaseLedger)
    row = {
        "id": "r1", "workflow_id": "w1", "artifact_id": "a1",
        "repository": "org/repo", "source_revision": "s1",
        "workflow_generation": 1, "validation_json": "{}",
        "metadata_json": '{"validation_attestation":{"validator_id":"v1"},"slsa_provenance":{"statement":{"predicate":{"runDetails":{"builder":{"id":"b1"}}}}}}',
        "status": "promoted", "rollback_of": None,
        "created_at": "2026-09-15T10:00:00+00:00",
    }

    class Result:
        def fetchall(self):
            return [row]

    class DB:
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass

    class Backend:
        def connect(self):
            return DB()

    ledger.backend = Backend()
    monkeypatch.setattr(
        "production_os.release_ledger._execute",
        lambda *args, **kwargs: Result(),
    )
    ledger.verify = lambda release_id: {
        "valid": False,
        "reason": "signing key is compromised",
    }

    first = ledger.incident_report(key_id="sha256:deadbeef")
    second = ledger.incident_report(key_id="sha256:deadbeef")

    assert first["schema_version"] == (
        "production-os/trust-incident-report/v1"
    )
    assert first["incident_id"] == second["incident_id"]
    assert first["generated_at"] != ""
    assert first["severity"] == "medium"
    assert first["counts"]["affected_releases"] == 1
    assert first["affected_releases"][0]["release_id"] == "r1"
