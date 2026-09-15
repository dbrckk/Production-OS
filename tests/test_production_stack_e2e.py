import hashlib
import json
import os
import threading
import urllib.request
import uuid
from contextlib import contextmanager
from http.server import ThreadingHTTPServer

import psycopg
from psycopg import sql
from psycopg.conninfo import make_conninfo
import pytest

from production_os.api_auth import TokenAuthorizer, token_digest
from production_os.attestations import create_validation_attestation
from production_os.control_plane import ControlPlane, make_handler
from production_os.remote_worker import RemoteWorkerClient


def _api(base: str, path: str, token: str, payload=None):
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        base + path,
        data=data,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST" if payload is not None else "GET",
    )
    with urllib.request.urlopen(request, timeout=5) as response:
        raw = response.read()
        return response.status, json.loads(raw or b"{}")


@contextmanager
def _isolated_postgres_database(base_dsn: str, run_id: str):
    database_name = f"production_os_e2e_{run_id[:24]}"
    admin_dsn = make_conninfo(base_dsn, dbname="postgres")
    test_dsn = make_conninfo(base_dsn, dbname=database_name)

    with psycopg.connect(admin_dsn, autocommit=True) as connection:
        connection.execute(
            sql.SQL("CREATE DATABASE {}").format(sql.Identifier(database_name))
        )

    try:
        yield test_dsn
    finally:
        with psycopg.connect(admin_dsn, autocommit=True) as connection:
            connection.execute(
                sql.SQL("DROP DATABASE {} WITH (FORCE)").format(
                    sql.Identifier(database_name)
                )
            )


@pytest.mark.e2e
def test_postgres_http_worker_workflow_release_pipeline_end_to_end():
    base_database = os.getenv("PRODUCTION_OS_TEST_POSTGRES")
    if not base_database:
        pytest.skip("PRODUCTION_OS_TEST_POSTGRES is required for production E2E")

    run_id = uuid.uuid4().hex
    operator_token = f"operator-{run_id}"
    worker_token = f"worker-{run_id}"
    worker_id = f"python-e2e-{run_id}"
    repository = f"e2e/production-stack-{run_id}"
    source_revision = f"revision-{run_id}"
    validator_id = f"validator-{run_id}"
    validator_secret = f"validator-secret-{run_id}"
    provenance_secret = f"provenance-secret-{run_id}"

    auth = TokenAuthorizer(
        [
            {
                "name": "e2e-operator",
                "role": "operator",
                "sha256": token_digest(operator_token),
            },
            {
                "name": "e2e-worker",
                "role": "worker",
                "sha256": token_digest(worker_token),
            },
        ]
    )

    with _isolated_postgres_database(base_database, run_id) as database:
        control = ControlPlane(
            database,
            authorizer=auth,
            trusted_validation_secrets={validator_id: validator_secret},
            provenance_secret=provenance_secret,
        )
        server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(control))
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base = f"http://127.0.0.1:{server.server_port}"

        try:
            status, registered = _api(
                base,
                "/v1/workers/register",
                operator_token,
                {
                    "worker_id": worker_id,
                    "capabilities": ["python"],
                    "max_concurrency": 1,
                },
            )
            assert status == 200
            assert registered["worker"]["worker_id"] == worker_id

            status, created = _api(
                base,
                "/v1/workflows",
                operator_token,
                {
                    "name": f"production-e2e-{run_id}",
                    "repository": repository,
                    "metadata": {
                        "github_pr_number": 900001,
                        "github_pr_head_sha": source_revision,
                        "github_pr_generation": 1,
                    },
                    "tasks": [
                        {
                            "task_id": "build",
                            "title": "Build",
                            "payload": {"required_capabilities": ["python"]},
                        },
                        {
                            "task_id": "package",
                            "title": "Package",
                            "dependencies": ["build"],
                            "payload": {"required_capabilities": ["python"]},
                        },
                    ],
                },
            )
            assert status == 201
            workflow_id = created["workflow"]["id"]

            status, dispatched = _api(
                base,
                f"/v1/workflows/{workflow_id}/dispatch",
                operator_token,
                {},
            )
            assert status == 200
            assert len(dispatched["jobs"]) == 1

            worker = RemoteWorkerClient(
                base,
                worker_token,
                worker_id,
                ["python"],
                timeout=5,
            )

            build_job = worker.claim()
            assert build_job is not None
            assert build_job.payload["payload"]["workflow_task_id"] == "build"
            assert worker.ack(build_job.key)["status"] == "acked"
            assert worker.complete(
                build_job.key,
                result_payload={"tests": "passed"},
                duration_seconds=1.25,
            )["status"] == "completed"

            package_job = worker.claim()
            assert package_job is not None
            assert package_job.payload["payload"]["workflow_task_id"] == "package"
            assert worker.ack(package_job.key)["status"] == "acked"
            assert worker.complete(
                package_job.key,
                result_payload={"artifact": "release.bin"},
                duration_seconds=0.75,
            )["status"] == "completed"

            status, workflow_status = _api(
                base,
                f"/v1/workflows/{workflow_id}",
                operator_token,
            )
            assert status == 200
            assert workflow_status["workflow"]["status"] == "succeeded"

            artifact_sha256 = hashlib.sha256(run_id.encode("utf-8")).hexdigest()
            status, artifact_payload = _api(
                base,
                f"/v1/workflows/{workflow_id}/artifacts",
                operator_token,
                {
                    "task_id": "package",
                    "name": "release.bin",
                    "uri": f"artifact://production-e2e/{run_id}/release.bin",
                    "sha256": artifact_sha256,
                    "metadata": {
                        "source_revision": source_revision,
                        "workflow_generation": 1,
                    },
                },
            )
            assert status == 201
            artifact = artifact_payload["artifact"]
            assert artifact["sha256"] == artifact_sha256

            validation = {
                "status": "passed",
                "promotion_allowed": True,
                "blocking_failures": [],
            }
            attestation = create_validation_attestation(
                validator_id=validator_id,
                secret=validator_secret,
                workflow_id=workflow_id,
                artifact_id=artifact["id"],
                artifact_sha256=artifact_sha256,
                source_revision=source_revision,
                workflow_generation=1,
                validation=validation,
            )
            status, promoted_payload = _api(
                base,
                f"/v1/workflows/{workflow_id}/promote",
                operator_token,
                {
                    "artifact_id": artifact["id"],
                    "validation": validation,
                    "attestation": attestation,
                    "metadata": {"channel": "e2e"},
                },
            )
            assert status == 201
            release = promoted_payload["release"]
            assert release["status"] == "promoted"
            assert release["metadata"]["approval"]["approved_by"] == "e2e-operator"

            status, verified_payload = _api(
                base,
                f"/v1/releases/{release['id']}/verify",
                operator_token,
            )
            assert status == 200
            verification = verified_payload["verification"]
            assert verification["valid"] is True
            assert verification["validator_id"] == validator_id
            assert verification["artifact_sha256"] == artifact_sha256

            status, transparency = _api(
                base,
                "/v1/transparency",
                operator_token,
            )
            assert status == 200
            assert transparency["verification"]["valid"] is True
            assert any(
                entry["release_id"] == release["id"]
                for entry in transparency["entries"]
            )

            status, stats = _api(base, "/v1/stats", operator_token)
            assert status == 200
            assert stats["online_workers"] == 1
            assert stats["jobs"].get("completed", 0) == 2
            assert stats["workflows"].get("succeeded", 0) == 1
        finally:
            server.shutdown()
            server.server_close()
