import os
import json
import threading
import uuid
from argparse import Namespace
from concurrent.futures import ThreadPoolExecutor

import pytest

from production_os.postgres_backend import PostgresBackend, PostgresJobQueue
from production_os.cli import run_db_init, run_dispatch
from production_os.release_ledger import ReleaseLedger
from production_os.workflow_engine import WorkflowEngine, WorkflowTaskSpec
from test_production_stack_e2e import _isolated_postgres_database
from test_release_ledger import approval, passed_validation, signed_attestation


pytestmark = pytest.mark.e2e


@pytest.fixture
def ledger():
    dsn = os.getenv("PRODUCTION_OS_TEST_POSTGRES")
    if not dsn:
        pytest.skip("PRODUCTION_OS_TEST_POSTGRES is required")
    with _isolated_postgres_database(dsn, uuid.uuid4().hex) as database:
        backend = PostgresBackend(database)
        workflows = WorkflowEngine(backend, PostgresJobQueue(backend))
        releases = ReleaseLedger(
            backend, workflows,
            trusted_validation_secrets={"validator-1": "validator-secret"},
            provenance_secret="provenance-secret",
        )
        yield backend, workflows, releases


def prepared_release(workflows):
    workflow = workflows.create(
        name="release", repository="test/postgres-release",
        metadata={"github_pr_number": 12, "github_pr_head_sha": "sha-1", "github_pr_generation": 1},
        tasks=[WorkflowTaskSpec("build", "Build", {})],
    )
    workflows.dispatch_ready(workflow["id"])
    workflows.record_result(workflow["id"], "build", succeeded=True, result={"ok": True})
    artifact = workflows.add_artifact(
        workflow["id"], name="app", uri="artifact://app", sha256="a" * 64,
        metadata={"source_revision": "sha-1", "workflow_generation": 1},
    )
    return {
        "workflow_id": workflow["id"], "artifact_id": artifact["id"],
        "validation": passed_validation(), "attestation": signed_attestation(workflow, artifact),
        "approval": approval(),
    }


def test_postgres_upgrade_restores_missing_ledgers_without_losing_workflows(ledger):
    backend, workflows, releases = ledger
    prepared = prepared_release(workflows)
    with backend.connect() as db:
        db.execute("DROP TABLE transparency_log, trust_incident_reports")
        db.execute("UPDATE schema_meta SET value='18' WHERE key='schema_version'")

    backend.initialize()
    backend.initialize()

    release = releases.promote(**prepared)
    assert release["status"] == "promoted"
    assert releases.verify_transparency()["valid"]
    snapshot = releases.record_incident_report()
    assert snapshot["recorded"]
    assert releases.record_incident_report()["deduplicated"]
    assert releases.verify_incident_history()["valid"]


def test_concurrent_postgres_promotions_keep_one_valid_transparency_chain(ledger):
    _, workflows, releases = ledger
    prepared = [prepared_release(workflows) for _ in range(4)]
    barrier = threading.Barrier(4)

    def promote(payload):
        barrier.wait(timeout=10)
        return releases.promote(**payload)

    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(promote, prepared))

    assert len({release["id"] for release in results}) == 4
    assert releases.verify_transparency()["valid"]
    assert [entry["sequence"] for entry in releases.transparency_log()] == [1, 2, 3, 4]


def test_concurrent_postgres_incident_snapshots_keep_one_valid_hash_chain(ledger):
    _, _, releases = ledger
    barrier = threading.Barrier(4)

    def snapshot(scope):
        barrier.wait(timeout=10)
        return releases.record_incident_report(validator_id=scope)

    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(snapshot, ["one", "two", "three", "four"]))

    assert all(result["recorded"] for result in results)
    assert len(releases.incident_history()) == 4
    assert releases.verify_incident_history()["valid"]


def test_keyword_dsn_cli_reports_postgres_backend(ledger, tmp_path, capsys):
    backend, _, _ = ledger
    assert run_db_init(Namespace(database=backend.dsn)) == 0
    assert json.loads(capsys.readouterr().out)["backend"] == "postgres"
    handoff = tmp_path / "handoff.json"
    handoff.write_text(json.dumps({"repository": "test/postgres", "task": "test task"}))
    assert run_dispatch(Namespace(
        database=backend.dsn, handoff=str(handoff), required_capability=[],
    )) == 0
    assert json.loads(capsys.readouterr().out)["backend"] == "postgres"
