from __future__ import annotations

import os
import json
import hashlib
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from .api_auth import Principal, TokenAuthorizer
from .storage import job_queue_for, open_backend, worker_registry_for
from .workflow_engine import WorkflowEngine, WorkflowTaskSpec
from .execution_optimizer import ExecutionOptimizer
from .speculation import SpeculationManager
from .portfolio_optimizer import PortfolioOptimizer
from .github_client import GitHubClient
from .release_ledger import ReleaseLedger
from .dashboard_store import DashboardStore
from .dashboard_control import DashboardControl
from .dashboard_service import DashboardService, DashboardNotFound
from .dashboard_ui import DASHBOARD_HTML
from .dashboard_health import (
    STALE_BUSY_WORKER_SECONDS,
    STALE_RUNNING_EXECUTION_SECONDS,
)
from .dashboard_maintenance import RetentionCandidateConflict
from .dashboard_backups import BackupError, BackupRetentionCandidateConflict, BackupTempCandidateConflict
from .managed_projects import ManagedProjectService
from .database_maintenance_lock import database_server_lock
from .github_webhook import (
    WebhookDeliveryStore,
    WebhookError,
    parse_github_webhook,
    pull_request_event_target,
    verify_github_signature,
)


class ControlPlane:
    def __init__(
        self,
        database: str,
        *,
        authorizer: TokenAuthorizer | None = None,
        github_webhook_secret: str | None = None,
        trusted_validation_secrets: dict[str, str] | None = None,
        provenance_secret: str | None = None,
        trusted_validation_public_keys: dict[str, str] | None = None,
        provenance_private_key: str | None = None,
        provenance_public_key: str | None = None,
        provenance_signer=None,
        validation_signature_policy: str = "compatible",
        builder_id: str = "https://production-os.local/builder",
        builder_private_key: str | None = None,
        builder_signer=None,
        trusted_builders: dict | None = None,
        trusted_builder_keys: dict | None = None,
        require_trusted_builder: bool = False,
    ):
        self.backend = open_backend(database)
        self.dashboard_store = DashboardStore(self.backend)
        self.queue = job_queue_for(self.backend)
        self.workers = worker_registry_for(self.backend)
        self.workflows = WorkflowEngine(self.backend, self.queue)
        self.managed_projects = ManagedProjectService(self.workflows)
        github_token = str(os.getenv("GITHUB_TOKEN") or "").strip()
        actions_repository = str(
            os.getenv("PRODUCTION_OS_ACTIONS_REPOSITORY") or ""
        ).strip() or None
        actions_workflow = str(
            os.getenv("PRODUCTION_OS_ACTIONS_WORKFLOW") or ""
        ).strip() or None
        actions_ref = str(
            os.getenv("PRODUCTION_OS_ACTIONS_REF") or "main"
        ).strip() or "main"
        self.dashboard_control = DashboardControl(
            self.dashboard_store,
            self.queue,
            self.workflows,
            github=GitHubClient(github_token) if github_token else None,
            actions_repository=actions_repository,
            actions_workflow=actions_workflow,
            actions_ref=actions_ref,
        )
        self.dashboard = DashboardService(self)
        self.optimizer = ExecutionOptimizer(self.backend)
        self.speculation = SpeculationManager(self.backend, self.queue)
        self.portfolio = PortfolioOptimizer(self.workflows, self.optimizer)
        self.releases = ReleaseLedger(
            self.backend,
            self.workflows,
            trusted_validation_secrets=trusted_validation_secrets,
            provenance_secret=provenance_secret,
            trusted_validation_public_keys=(
                trusted_validation_public_keys
            ),
            provenance_private_key=provenance_private_key,
            provenance_public_key=provenance_public_key,
            provenance_signer=provenance_signer,
            validation_signature_policy=validation_signature_policy,
            builder_id=builder_id,
            builder_private_key=builder_private_key,
            builder_signer=builder_signer,
            trusted_builders=trusted_builders,
            trusted_builder_keys=trusted_builder_keys,
            require_trusted_builder=require_trusted_builder,
        )
        self.authorizer = authorizer or TokenAuthorizer([])
        self.github_webhook_secret = github_webhook_secret
        self.webhook_deliveries = WebhookDeliveryStore(self.backend)

    @staticmethod
    def _parse_timestamp(value):
        if not value:
            return None
        try:
            parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except ValueError:
            return None
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)

    def recover_abandoned_acked_jobs(self) -> list[dict]:
        now = datetime.now(timezone.utc)
        self.workers.detect_dead(timeout_seconds=STALE_BUSY_WORKER_SECONDS)
        self.workers.load()

        with self.backend.connect() as db:
            if self.backend.__class__.__name__.startswith("Postgres"):
                cursor = db.cursor()
                cursor.execute(
                    """SELECT * FROM jobs
                       WHERE status='acked'
                       ORDER BY updated_at ASC"""
                )
                rows = cursor.fetchall()
            else:
                rows = db.execute(
                    """SELECT * FROM jobs
                       WHERE status='acked'
                       ORDER BY updated_at ASC"""
                ).fetchall()

        recovered = []
        for raw in rows:
            job = dict(raw)
            worker_id = str(job.get("claimed_by") or "")
            worker = self.workers.workers.get(worker_id)
            if worker is None or worker.status != "dead":
                continue

            execution = self.dashboard_store.latest_execution(job["key"])
            if (
                execution is None
                or execution.get("status") != "running"
                or execution.get("worker_id") != worker_id
            ):
                continue
            last_activity = self._parse_timestamp(
                execution.get("last_telemetry_at")
                or execution.get("started_at")
            )
            if (
                last_activity is None
                or (now - last_activity).total_seconds()
                    <= STALE_RUNNING_EXECUTION_SECONDS
            ):
                continue

            timestamp = now.isoformat()
            with self.backend.transaction() as db:
                if self.backend.__class__.__name__.startswith("Postgres"):
                    cursor = db.cursor()
                    cursor.execute(
                        """UPDATE jobs
                           SET status='queued', claimed_by=NULL,
                               claimed_at=NULL, ack_deadline=NULL,
                               updated_at=%s
                           WHERE key=%s AND status='acked'
                             AND claimed_by=%s""",
                        (timestamp, job["key"], worker_id),
                    )
                    updated = cursor.rowcount
                else:
                    cursor = db.execute(
                        """UPDATE jobs
                           SET status='queued', claimed_by=NULL,
                               claimed_at=NULL, ack_deadline=NULL,
                               updated_at=?
                           WHERE key=? AND status='acked'
                             AND claimed_by=?""",
                        (timestamp, job["key"], worker_id),
                    )
                    updated = cursor.rowcount
                if updated != 1:
                    continue
                action = {
                    "key":job["key"],
                    "action":"queued",
                    "reason":"worker_abandoned_after_ack",
                    "worker_id":worker_id,
                    "delivery_attempt":job.get("delivery_attempt"),
                }
                self.backend.append_event(
                    db,
                    "job-recovered",
                    action,
                    repository=job["repository"],
                    task_key_value=job["key"],
                )

            self.dashboard_store.finish_execution(
                job["key"],
                worker_id,
                status="failed",
                duration_seconds=None,
                result={"reason":"worker abandoned after ack"},
                error_type="worker_abandoned",
                error_message="worker heartbeat and execution telemetry expired",
            )
            recovered.append({
                "key":job["key"],
                "worker_id":worker_id,
                "status":"queued",
            })
        return recovered


    def reconcile_worker_registration(
        self,
        worker_id: str,
        active_job_keys: list[str],
        *,
        max_attempts: int = 3,
    ) -> list[dict]:
        active = {str(key) for key in active_job_keys if str(key)}
        with self.backend.connect() as db:
            if self.backend.__class__.__name__.startswith("Postgres"):
                cursor = db.cursor()
                cursor.execute(
                    """SELECT * FROM jobs
                       WHERE claimed_by=%s
                         AND status IN ('claimed','acked')
                       ORDER BY updated_at ASC""",
                    (worker_id,),
                )
                rows = cursor.fetchall()
            else:
                rows = db.execute(
                    """SELECT * FROM jobs
                       WHERE claimed_by=?
                         AND status IN ('claimed','acked')
                       ORDER BY updated_at ASC""",
                    (worker_id,),
                ).fetchall()

        recovered = []
        now = datetime.now(timezone.utc).isoformat()
        for raw in rows:
            job = dict(raw)
            key = str(job["key"])
            if key in active:
                continue
            previous_status = str(job["status"])
            target = (
                "dead-letter"
                if int(job.get("delivery_attempt") or 0) >= int(max_attempts)
                else "queued"
            )

            with self.backend.transaction() as db:
                if self.backend.__class__.__name__.startswith("Postgres"):
                    cursor = db.cursor()
                    cursor.execute(
                        """UPDATE jobs
                           SET status=%s, claimed_by=NULL, claimed_at=NULL,
                               ack_deadline=NULL, updated_at=%s
                           WHERE key=%s AND status=%s AND claimed_by=%s""",
                        (target, now, key, previous_status, worker_id),
                    )
                    updated = cursor.rowcount
                else:
                    cursor = db.execute(
                        """UPDATE jobs
                           SET status=?, claimed_by=NULL, claimed_at=NULL,
                               ack_deadline=NULL, updated_at=?
                           WHERE key=? AND status=? AND claimed_by=?""",
                        (target, now, key, previous_status, worker_id),
                    )
                    updated = cursor.rowcount
                if updated != 1:
                    continue
                action = {
                    "key":key,
                    "action":target,
                    "reason":"worker_session_reconciled",
                    "worker_id":worker_id,
                    "previous_status":previous_status,
                    "delivery_attempt":job.get("delivery_attempt"),
                }
                self.backend.append_event(
                    db,
                    "job-recovered",
                    action,
                    repository=job["repository"],
                    task_key_value=key,
                )

            if previous_status == "acked":
                execution = self.dashboard_store.latest_execution(key)
                if (
                    execution is not None
                    and execution.get("status") == "running"
                    and execution.get("worker_id") == worker_id
                ):
                    self.dashboard_store.finish_execution(
                        key,
                        worker_id,
                        status="failed",
                        duration_seconds=None,
                        result={"reason":"worker session restarted without job"},
                        error_type="worker_restarted",
                        error_message=(
                            "worker re-registered without reporting the active job"
                        ),
                    )

            recovered.append({
                "key":key,
                "worker_id":worker_id,
                "previous_status":previous_status,
                "status":target,
            })
        return recovered


def _json_bytes(payload: dict | list) -> bytes:
    return json.dumps(
        payload,
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")





class RequestBodyTooLarge(ValueError):
    pass


def make_handler(control: ControlPlane):
    class Handler(BaseHTTPRequestHandler):
        server_version = "ProductionOS"

        def version_string(self) -> str:
            return self.server_version

        def log_message(self, format: str, *args) -> None:
            return

        def _send_html(self, status: int, html: str) -> None:
            body = html.encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("X-Frame-Options", "DENY")
            self.send_header("Referrer-Policy", "no-referrer")
            self.end_headers()
            try:
                self.wfile.write(body)
            except (BrokenPipeError, ConnectionResetError):
                return

        def _send(
            self,
            status: int,
            payload: dict | list,
            *,
            headers: dict[str, str] | None = None,
        ) -> None:
            body = _json_bytes(payload)
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("X-Frame-Options", "DENY")
            self.send_header("Referrer-Policy", "no-referrer")
            if headers:
                for name, value in headers.items():
                    self.send_header(name, value)
            self.end_headers()
            try:
                self.wfile.write(body)
            except (BrokenPipeError, ConnectionResetError):
                return

        def _method_not_allowed(self) -> None:
            self._send(
                HTTPStatus.METHOD_NOT_ALLOWED,
                {"error": "method not allowed"},
                headers={"Allow": "GET, POST"},
            )

        def do_PUT(self) -> None:
            self._method_not_allowed()

        def do_PATCH(self) -> None:
            self._method_not_allowed()

        def do_DELETE(self) -> None:
            self._method_not_allowed()

        def _read_body(self) -> bytes:
            raw_length = self.headers.get("Content-Length", "0")
            try:
                length = int(raw_length)
            except ValueError as exc:
                raise ValueError("invalid Content-Length") from exc
            if length < 0:
                raise ValueError("invalid Content-Length")
            max_body = 1024 * 1024
            if length > max_body:
                self.rfile.read(min(length, max_body + 1))
                raise RequestBodyTooLarge("request body too large")
            if not length:
                return b""
            body = self.rfile.read(length)
            if len(body) != length:
                raise ValueError("truncated request body")
            return body

        def _read_json(self) -> dict:
            raw = self._read_body()
            if not raw:
                return {}
            try:
                payload = json.loads(raw.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise ValueError("invalid JSON body") from exc
            if not isinstance(payload, dict):
                raise ValueError("JSON object body required")
            return payload

        def _principal(self) -> Principal | None:
            header = self.headers.get("Authorization", "")
            prefix = "Bearer "
            token = header[len(prefix):] if header.startswith(prefix) else None
            return control.authorizer.authenticate(token)

        def _require(self, role: str) -> Principal | None:
            principal = self._principal()
            if principal is None:
                self._send(
                    HTTPStatus.UNAUTHORIZED,
                    {"error":"unauthorized"},
                )
                return None
            if not principal.allows(role):
                self._send(
                    HTTPStatus.FORBIDDEN,
                    {
                        "error":"forbidden",
                        "required_role":role,
                        "role":principal.role,
                    },
                )
                return None
            return principal

        def do_GET(self) -> None:
            parsed = urlparse(self.path)
            if parsed.path == "/dashboard":
                self._send_html(HTTPStatus.OK, DASHBOARD_HTML)
                return

            if parsed.path == "/":
                self.send_response(HTTPStatus.FOUND)
                self.send_header("Location", "/dashboard")
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                return

            if parsed.path in {"/health", "/healthz"}:
                self._send(
                    HTTPStatus.OK,
                    {
                        "status":"healthy",
                        "schema_version":"production-os/control-plane/v1",
                    },
                )
                return

            principal = self._require("viewer")
            if principal is None:
                return

            if parsed.path.startswith("/v1/dashboard/") and principal.role == "worker":
                self._send(
                    HTTPStatus.FORBIDDEN,
                    {"error":"forbidden","required_role":"viewer","role":principal.role},
                )
                return

            if parsed.path.startswith("/v1/dashboard/"):
                query = parse_qs(parsed.query)
                try:
                    window = query.get("window", ["7d"])[0]
                    parts = [part for part in parsed.path.split("/") if part]
                    service = control.dashboard
                    if parsed.path == "/v1/dashboard/overview":
                        payload = service.overview(window)
                    elif parsed.path == "/v1/dashboard/launch-readiness":
                        payload = service.launch_readiness(
                            query.get("repository", [""])[0],
                        )
                    elif parsed.path == "/v1/dashboard/production-status":
                        payload = service.production_status(
                            query.get("project_id", [""])[0],
                        )
                    elif parsed.path == "/v1/dashboard/productions":
                        payload = service.production_inbox(
                            limit=int(query.get("limit", ["50"])[0]),
                            category=query.get("filter", ["all"])[0],
                        )
                    elif parsed.path == "/v1/dashboard/attention":
                        payload = service.attention(
                            limit=int(query.get("limit", ["50"])[0]),
                        )
                    elif parsed.path == "/v1/dashboard/health":
                        payload = service.health()
                    elif parsed.path == "/v1/dashboard/autopilot":
                        payload = service.autopilot_queue(
                            int(query.get("limit", ["50"])[0])
                        )
                    elif parsed.path == "/v1/dashboard/workers":
                        payload = service.workers()
                    elif len(parts) >= 3 and parts[1] == "dashboard" and parts[2] == "workers":
                        worker_id = parts[3] if len(parts) >= 4 else ""
                        if len(parts) == 4:
                            payload = service.worker_detail(worker_id)
                        elif len(parts) == 5 and parts[4] == "logs":
                            payload = service.worker_logs(worker_id, query.get("after",[None])[0], query.get("limit",["100"])[0])
                        elif len(parts) == 5 and parts[4] == "usage":
                            payload = service.worker_usage(worker_id, window)
                        else:
                            raise DashboardNotFound(parsed.path)
                    elif parsed.path == "/v1/dashboard/maintenance":
                        payload = service.maintenance()
                    elif parsed.path == "/v1/dashboard/backups":
                        payload = service.backups()
                    elif parsed.path == "/v1/dashboard/repositories":
                        payload = service.repositories()
                    elif parsed.path == "/v1/dashboard/projects":
                        payload = service.projects()
                    elif len(parts) >= 4 and parts[1] == "dashboard" and parts[2] == "projects":
                        if len(parts) < 5:
                            raise DashboardNotFound(parsed.path)
                        repository = parts[3] + "/" + parts[4]
                        if any(x in {".",".."} for x in (parts[3],parts[4])):
                            raise ValueError("invalid repository")
                        if len(parts) == 5:
                            payload = service.project_detail(repository)
                        elif len(parts) == 6 and parts[5] == "progress":
                            payload = service.project_progress(repository)
                        elif len(parts) == 6 and parts[5] == "commits":
                            payload = service.project_commits(repository, window)
                        elif len(parts) == 6 and parts[5] == "usage":
                            payload = service.project_usage(repository, window)
                        elif len(parts) == 6 and parts[5] == "workflows":
                            payload = service.project_workflows(repository)
                        elif len(parts) == 6 and parts[5] == "history":
                            payload = service.project_history(repository)
                        else:
                            raise DashboardNotFound(parsed.path)
                    elif parsed.path == "/v1/dashboard/control-audit":
                        payload = service.control_audit(
                            int(query.get("limit", ["100"])[0])
                        )
                    elif parsed.path == "/v1/dashboard/remediations":
                        payload = service.remediation_history(
                            limit=int(query.get("limit", ["100"])[0]),
                            incident_id=query.get("incident_id", [None])[0],
                        )
                    elif parsed.path == "/v1/dashboard/remediation-analytics":
                        payload = service.remediation_analytics(
                            query.get("window", ["24h"])[0],
                        )
                    elif parsed.path == "/v1/dashboard/incidents":
                        payload = service.incidents(
                            limit=int(query.get("limit", ["100"])[0]),
                            status=query.get("status", [None])[0],
                        )
                    elif parsed.path == "/v1/dashboard/activity":
                        payload = service.activity(
                            repository=query.get("repository",[None])[0],
                            worker_id=query.get("worker_id",[None])[0],
                            event_type=query.get("event_type",[None])[0],
                            after=int(query.get("after",["0"])[0]),
                            limit=int(query.get("limit",["100"])[0]),
                        )
                    else:
                        raise DashboardNotFound(parsed.path)
                    self._send(HTTPStatus.OK, payload)
                except DashboardNotFound:
                    self._send(HTTPStatus.NOT_FOUND, {"error":"dashboard resource not found"})
                except (ValueError, TypeError):
                    self._send(HTTPStatus.BAD_REQUEST, {"error":"invalid dashboard query"})
                return

            if parsed.path == "/v1/stats":
                with control.backend.connect() as db:
                    rows = db.execute(
                        "SELECT status, COUNT(*) AS count FROM jobs GROUP BY status"
                    ).fetchall()
                    workers = db.execute(
                        "SELECT COUNT(*) AS count FROM workers WHERE status='online'"
                    ).fetchone()["count"]
                    workflow_rows = db.execute(
                        "SELECT status, COUNT(*) AS count FROM workflows GROUP BY status"
                    ).fetchall()
                self._send(
                    HTTPStatus.OK,
                    {
                        "jobs":{row["status"]:row["count"] for row in rows},
                        "workflows":{
                            row["status"]:row["count"]
                            for row in workflow_rows
                        },
                        "online_workers":workers,
                    },
                )
                return

            if parsed.path == "/v1/stragglers":
                control.workers.load()
                self._send(
                    HTTPStatus.OK,
                    {
                        "stragglers":control.optimizer.stragglers(
                            workers=list(
                                control.workers.workers.values()
                            )
                        )
                    },
                )
                return

            if parsed.path == "/v1/workflows":
                with control.backend.connect() as db:
                    rows = db.execute(
                        """
                        SELECT id, name, repository, status, created_at, updated_at
                        FROM workflows
                        ORDER BY created_at DESC
                        LIMIT 100
                        """
                    ).fetchall()
                self._send(
                    HTTPStatus.OK,
                    {
                        "workflows":[
                            {
                                "id":row["id"],
                                "name":row["name"],
                                "repository":row["repository"],
                                "status":row["status"],
                                "created_at":row["created_at"],
                                "updated_at":row["updated_at"],
                            }
                            for row in rows
                        ]
                    },
                )
                return

            if parsed.path == "/v1/events":
                query = parse_qs(parsed.query)
                try:
                    after = int(query.get("after", ["0"])[0])
                    limit = int(query.get("limit", ["100"])[0])
                except ValueError:
                    self._send(
                        HTTPStatus.BAD_REQUEST,
                        {"error":"invalid pagination"},
                    )
                    return
                self._send(
                    HTTPStatus.OK,
                    {
                        "events":control.backend.events_after(after, limit),
                    },
                )
                return

            if parsed.path.startswith("/v1/jobs/"):
                key = parsed.path.split("/", 3)[-1]
                try:
                    job = control.queue.get(key)
                except KeyError:
                    self._send(
                        HTTPStatus.NOT_FOUND,
                        {"error":"job not found"},
                    )
                    return
                self._send(HTTPStatus.OK, {"job":job})
                return

            if parsed.path.startswith("/v1/workflows/"):
                parts = [part for part in parsed.path.split("/") if part]
                if len(parts) >= 3:
                    workflow_id = parts[2]
                    try:
                        if len(parts) == 4 and parts[3] == "critical-path":
                            payload = control.workflows.critical_path(workflow_id)
                            self._send(HTTPStatus.OK, payload)
                            return
                        if len(parts) == 4 and parts[3] == "eta":
                            workflow = control.workflows.get(workflow_id)
                            payload = control.optimizer.workflow_eta(workflow)
                            self._send(HTTPStatus.OK, payload)
                            return
                        if len(parts) == 4 and parts[3] == "releases":
                            self._send(
                                HTTPStatus.OK,
                                {
                                    "releases":
                                        control.releases.list_for_workflow(
                                            workflow_id
                                        )
                                },
                            )
                            return
                        if len(parts) == 3:
                            payload = control.workflows.get(workflow_id)
                            self._send(
                                HTTPStatus.OK,
                                {"workflow":payload},
                            )
                            return
                    except KeyError:
                        self._send(
                            HTTPStatus.NOT_FOUND,
                            {"error":"workflow not found"},
                        )
                        return

            if parsed.path == "/v1/incident-history/verify":
                self._send(
                    HTTPStatus.OK,
                    {
                        "schema_version":
                            "production-os/trust-incident-history-verification/v1",
                        **control.releases.verify_incident_history(),
                    },
                )
                return

            if parsed.path == "/v1/incident-history":
                query = parse_qs(parsed.query)
                incident_id = (
                    query.get("incident_id") or [None]
                )[0]
                self._send(
                    HTTPStatus.OK,
                    {
                        "schema_version":
                            "production-os/trust-incident-history/v1",
                        "incident_id": incident_id,
                        "entries": control.releases.incident_history(
                            incident_id=incident_id
                        ),
                    },
                )
                return

            if parsed.path == "/v1/incident-report":
                query = parse_qs(parsed.query)
                report = control.releases.incident_report(
                    validator_id=(query.get("validator_id") or [None])[0],
                    builder_id=(query.get("builder_id") or [None])[0],
                    key_id=(query.get("key_id") or [None])[0],
                )
                self._send(HTTPStatus.OK, report)
                return

            if parsed.path == "/v1/trust-status":
                query = parse_qs(parsed.query)
                result = control.releases.trust_status(
                    validator_id=(query.get("validator_id") or [None])[0],
                    builder_id=(query.get("builder_id") or [None])[0],
                    key_id=(query.get("key_id") or [None])[0],
                )
                self._send(
                    HTTPStatus.OK,
                    {
                        "schema_version":
                            "production-os/trust-status/v1",
                        **result,
                    },
                )
                return

            if parsed.path == "/v1/transparency":
                self._send(
                    HTTPStatus.OK,
                    {
                        "verification":
                            control.releases.verify_transparency(),
                        "entries":
                            control.releases.transparency_log(),
                    },
                )
                return

            if parsed.path.startswith("/v1/releases/"):
                parts = [
                    part
                    for part in parsed.path.split("/")
                    if part
                ]
                if (
                    len(parts) == 4
                    and parts[1] == "releases"
                    and parts[3] == "verify"
                ):
                    try:
                        verification = control.releases.verify(
                            parts[2]
                        )
                    except KeyError:
                        self._send(
                            HTTPStatus.NOT_FOUND,
                            {"error":"release not found"},
                        )
                        return
                    self._send(
                        HTTPStatus.OK,
                        {"verification":verification},
                    )
                    return
                if len(parts) == 3 and parts[1] == "releases":
                    try:
                        release = control.releases.get(parts[2])
                    except KeyError:
                        self._send(
                            HTTPStatus.NOT_FOUND,
                            {"error":"release not found"},
                        )
                        return
                    self._send(
                        HTTPStatus.OK,
                        {"release":release},
                    )
                    return

            if parsed.path == "/v1/managed-projects":
                principal = self._require("viewer")
                if principal is None:
                    return
                if principal.role == "worker":
                    self._send(
                        HTTPStatus.FORBIDDEN,
                        {
                            "error":"forbidden",
                            "required_role":"viewer",
                            "role":principal.role,
                        },
                    )
                    return
                self._send(
                    HTTPStatus.OK,
                    {"projects":control.managed_projects.list()},
                )
                return

            if parsed.path.startswith("/v1/managed-projects/"):
                principal = self._require("viewer")
                if principal is None:
                    return
                if principal.role == "worker":
                    self._send(
                        HTTPStatus.FORBIDDEN,
                        {
                            "error":"forbidden",
                            "required_role":"viewer",
                            "role":principal.role,
                        },
                    )
                    return
                parts = [part for part in parsed.path.split("/") if part]
                if len(parts) == 3:
                    try:
                        project = control.managed_projects.get(parts[2])
                    except KeyError:
                        self._send(
                            HTTPStatus.NOT_FOUND,
                            {"error":"managed project not found"},
                        )
                        return
                    self._send(HTTPStatus.OK, {"project":project})
                    return

            if parsed.path == "/v1/workers":
                control.workers.detect_dead()
                control.workers.load()
                self._send(
                    HTTPStatus.OK,
                    {
                        "workers":[
                            worker.to_dict()
                            for worker in control.workers.workers.values()
                        ]
                    },
                )
                return

            self._send(HTTPStatus.NOT_FOUND, {"error":"not found"})

        def do_POST(self) -> None:
            parsed = urlparse(self.path)

            if parsed.path == "/v1/dashboard/launch":
                principal = self._require("operator")
                if principal is None:
                    return
                try:
                    body = self._read_json()
                    request_id = str(body.get("request_id") or "").strip()
                    project_id = None
                    if request_id:
                        if (
                            not (8 <= len(request_id) <= 128)
                            or any(
                                not (
                                    char.isalnum()
                                    or char in {"-", "_", ".", ":"}
                                )
                                for char in request_id
                            )
                        ):
                            raise ValueError("request_id is invalid")
                        actor = f"{principal.role}:{principal.name}"
                        project_id = hashlib.sha256(
                            (
                                "dashboard-launch/v1\0"
                                + actor
                                + "\0"
                                + request_id
                            ).encode("utf-8")
                        ).hexdigest()[:32]
                    project = control.managed_projects.create(
                        repository=str(body.get("repository") or ""),
                        final_goal=str(body.get("instruction") or ""),
                        token_budget=30000,
                        agent_preference="auto",
                        requested_by=(
                            f"{principal.role}:{principal.name}"
                        ),
                        project_id=project_id,
                    )
                except ValueError as exc:
                    self._send(
                        HTTPStatus.BAD_REQUEST,
                        {"error":str(exc)},
                    )
                    return
                except RuntimeError as exc:
                    self._send(
                        HTTPStatus.CONFLICT,
                        {"error":str(exc)},
                    )
                    return
                self._send(
                    HTTPStatus.CREATED,
                    {
                        "project":project,
                        "launch":{
                            "mode":"managed-project",
                            "persistent":True,
                            "token_budget":30000,
                            "agent_preference":"auto",
                            **(
                                {
                                    "request_id":request_id,
                                    "idempotent":True,
                                }
                                if request_id
                                else {}
                            ),
                        },
                    },
                )
                return

            if parsed.path == "/v1/managed-projects":
                principal = self._require("operator")
                if principal is None:
                    return
                try:
                    body = self._read_json()
                    project = control.managed_projects.create(
                        repository=str(body.get("repository") or ""),
                        final_goal=str(body.get("final_goal") or ""),
                        token_budget=body.get("token_budget"),
                        agent_preference=str(
                            body.get("agent_preference") or "auto"
                        ),
                        requested_by=(
                            f"{principal.role}:{principal.name}"
                        ),
                    )
                except ValueError as exc:
                    self._send(
                        HTTPStatus.BAD_REQUEST,
                        {"error":str(exc)},
                    )
                    return
                self._send(HTTPStatus.CREATED, {"project":project})
                return

            if parsed.path.startswith("/v1/managed-projects/"):
                principal = self._require("operator")
                if principal is None:
                    return
                parts = [part for part in parsed.path.split("/") if part]
                if len(parts) == 4:
                    workflow_id = parts[2]
                    action = parts[3]
                    try:
                        body = self._read_json()
                        if action == "instructions":
                            project = control.managed_projects.add_instruction(
                                workflow_id,
                                str(body.get("instruction") or ""),
                                requested_by=(
                                    f"{principal.role}:{principal.name}"
                                ),
                            )
                        elif action == "verify":
                            project = (
                                control.managed_projects.request_verification(
                                    workflow_id,
                                    requested_by=(
                                        f"{principal.role}:{principal.name}"
                                    ),
                                )
                            )
                        elif action == "complete":
                            if str(body.get("confirm") or "") != "MARK_PROJECT_DONE":
                                self._send(
                                    HTTPStatus.BAD_REQUEST,
                                    {"error":"confirm MARK_PROJECT_DONE required"},
                                )
                                return
                            project = control.managed_projects.mark_done(
                                workflow_id,
                                approved_by=(
                                    f"{principal.role}:{principal.name}"
                                ),
                            )
                        elif action == "cancel":
                            if str(body.get("confirm") or "") != "CANCEL_ACTIVE_PRODUCTION":
                                self._send(
                                    HTTPStatus.BAD_REQUEST,
                                    {"error":"confirm CANCEL_ACTIVE_PRODUCTION required"},
                                )
                                return
                            result = control.dashboard.cancel_production(
                                workflow_id,
                                requested_by=(
                                    f"{principal.role}:{principal.name}"
                                ),
                            )
                            self._send(
                                HTTPStatus.ACCEPTED
                                if result["status"] == "cancel_requested"
                                else HTTPStatus.OK,
                                result,
                            )
                            return
                        else:
                            self._send(
                                HTTPStatus.NOT_FOUND,
                                {"error":"not found"},
                            )
                            return
                    except KeyError:
                        self._send(
                            HTTPStatus.NOT_FOUND,
                            {"error":"managed project not found"},
                        )
                        return
                    except ValueError as exc:
                        self._send(
                            HTTPStatus.BAD_REQUEST,
                            {"error":str(exc)},
                        )
                        return
                    except RuntimeError as exc:
                        self._send(
                            HTTPStatus.CONFLICT,
                            {"error":str(exc)},
                        )
                        return
                    self._send(HTTPStatus.OK, {"project":project})
                    return

            if parsed.path == "/v1/github/webhook":
                if not control.github_webhook_secret:
                    self._send(
                        HTTPStatus.SERVICE_UNAVAILABLE,
                        {"error":"github webhook secret not configured"},
                    )
                    return
                try:
                    raw = self._read_body()
                except RequestBodyTooLarge as exc:
                    self._send(
                        HTTPStatus.REQUEST_ENTITY_TOO_LARGE,
                        {"error":str(exc)},
                    )
                    return
                except ValueError as exc:
                    self._send(
                        HTTPStatus.BAD_REQUEST,
                        {"error":str(exc)},
                    )
                    return

                if not verify_github_signature(
                    control.github_webhook_secret,
                    raw,
                    self.headers.get("X-Hub-Signature-256"),
                ):
                    self._send(
                        HTTPStatus.UNAUTHORIZED,
                        {"error":"invalid github webhook signature"},
                    )
                    return

                delivery_id = self.headers.get(
                    "X-GitHub-Delivery",
                    "",
                )
                event_name = self.headers.get(
                    "X-GitHub-Event",
                    "",
                )
                try:
                    payload = parse_github_webhook(raw)
                    target = pull_request_event_target(
                        event_name,
                        payload,
                    )
                except WebhookError as exc:
                    self._send(
                        HTTPStatus.BAD_REQUEST,
                        {"error":str(exc)},
                    )
                    return

                repository = target[0] if target else None
                try:
                    claimed = control.webhook_deliveries.claim(
                        delivery_id,
                        event_name,
                        repository,
                    )
                except WebhookError as exc:
                    self._send(
                        HTTPStatus.BAD_REQUEST,
                        {"error":str(exc)},
                    )
                    return

                if not claimed:
                    self._send(
                        HTTPStatus.OK,
                        {
                            "status":"duplicate",
                            "delivery_id":delivery_id,
                        },
                    )
                    return

                try:
                    if target is None:
                        self._send(
                            HTTPStatus.ACCEPTED,
                            {
                                "status":"ignored",
                                "delivery_id":delivery_id,
                                "event":event_name,
                            },
                        )
                        return

                    repository, pr_number, action, head_sha = target
                    generation, superseded = (
                        control.workflows.ensure_pr_generation(
                            repository,
                            pr_number,
                            head_sha,
                        )
                    )
                    if generation is None:
                        generation = (
                            control.workflows.create_from_pr_template(
                                repository,
                                pr_number,
                                head_sha,
                            )
                        )
                    workflows = [generation] if generation else []
                    refreshable = [
                        workflow
                        for workflow in workflows
                        if control.workflows.generation_refreshable(
                            workflow
                        )
                    ]
                    changed_paths = (
                        GitHubClient().list_pull_request_files(
                            repository,
                            pr_number,
                        )
                        if refreshable
                        else []
                    )
                    refreshed = []
                    dispatched = []
                    for workflow in workflows:
                        if workflow not in refreshable:
                            refreshed.append({
                                "workflow_id":workflow["id"],
                                "generation":workflow.get(
                                    "metadata", {}
                                ).get("github_pr_generation"),
                                "head_sha":head_sha,
                                "decisions":[],
                                "generation_noop":True,
                                "workflow":workflow,
                            })
                            continue

                        decisions = control.workflows.apply_change_impact(
                            workflow["id"],
                            changed_paths,
                        )
                        jobs = control.workflows.dispatch_ready(
                            workflow["id"],
                        )
                        refreshed.append({
                            "workflow_id":workflow["id"],
                            "generation":workflow.get(
                                "metadata", {}
                            ).get("github_pr_generation"),
                            "head_sha":head_sha,
                            "decisions":decisions,
                            "generation_noop":False,
                            "workflow":control.workflows.get(
                                workflow["id"]
                            ),
                        })
                        dispatched.extend(jobs)

                    self._send(
                        HTTPStatus.OK,
                        {
                            "status":"processed",
                            "delivery_id":delivery_id,
                            "event":event_name,
                            "action":action,
                            "repository":repository,
                            "pr_number":pr_number,
                            "head_sha":head_sha,
                            "changed_paths":changed_paths,
                            "refreshed":len(refreshed),
                            "workflows":refreshed,
                            "superseded_workflows":[
                                item["id"]
                                for item in superseded
                            ],
                            "dispatched_jobs":dispatched,
                        },
                    )
                    return
                except Exception:
                    control.webhook_deliveries.release(delivery_id)
                    raise

            try:
                body = self._read_json()
            except RequestBodyTooLarge as exc:
                self._send(
                    HTTPStatus.REQUEST_ENTITY_TOO_LARGE,
                    {"error":str(exc)},
                )
                return
            except ValueError as exc:
                self._send(
                    HTTPStatus.BAD_REQUEST,
                    {"error":str(exc)},
                )
                return

            try:
                parts = [part for part in parsed.path.split("/") if part]
                if (
                    len(parts) == 5
                    and parts[0] == "v1"
                    and parts[1] == "dashboard"
                    and parts[2] == "backups"
                    and parts[4] == "stage-restore"
                ):
                    principal = self._require("operator")
                    if principal is None:
                        return
                    if str(body.get("confirm") or "") != "STAGE_VERIFIED_RESTORE":
                        self._send(
                            HTTPStatus.BAD_REQUEST,
                            {"error":"exact restore staging confirmation required"},
                        )
                        return
                    backup_id = parts[3]
                    requested_by = f"{principal.role}:{principal.name}"
                    audit = control.dashboard_store.append_control_audit(
                        action="backup-stage-restore",
                        worker_id="control-plane",
                        requested_by=requested_by,
                        outcome="requested",
                    )
                    try:
                        result = control.dashboard.stage_backup_restore(
                            backup_id
                        )
                    except BackupError as exc:
                        control.dashboard_store.update_control_audit(
                            audit["id"],
                            outcome="failed",
                            error_code="backup_stage_restore_failed",
                        )
                        self._send(
                            HTTPStatus.CONFLICT,
                            {"error":str(exc)},
                        )
                        return
                    except Exception:
                        control.dashboard_store.update_control_audit(
                            audit["id"],
                            outcome="failed",
                            error_code="backup_stage_restore_failed",
                        )
                        raise
                    control.dashboard_store.update_control_audit(
                        audit["id"],
                        outcome="succeeded",
                    )
                    self._send(HTTPStatus.CREATED, result)
                    return

                if (
                    len(parts) == 5
                    and parts[0] == "v1"
                    and parts[1] == "dashboard"
                    and parts[2] == "backups"
                    and parts[4] == "verify"
                ):
                    principal = self._require("operator")
                    if principal is None:
                        return
                    if str(body.get("confirm") or "") != "VERIFY_BACKUP_FOR_RESTORE":
                        self._send(
                            HTTPStatus.BAD_REQUEST,
                            {"error":"exact restore verification confirmation required"},
                        )
                        return
                    backup_id = parts[3]
                    requested_by = f"{principal.role}:{principal.name}"
                    audit = control.dashboard_store.append_control_audit(
                        action="backup-verify",
                        worker_id="control-plane",
                        requested_by=requested_by,
                        outcome="requested",
                    )
                    try:
                        result = (
                            control.dashboard.verify_backup_restore_readiness(
                                backup_id
                            )
                        )
                    except BackupError as exc:
                        control.dashboard_store.update_control_audit(
                            audit["id"],
                            outcome="failed",
                            error_code="backup_verify_failed",
                        )
                        self._send(
                            HTTPStatus.CONFLICT,
                            {"error":str(exc)},
                        )
                        return
                    except Exception:
                        control.dashboard_store.update_control_audit(
                            audit["id"],
                            outcome="failed",
                            error_code="backup_verify_failed",
                        )
                        raise
                    control.dashboard_store.update_control_audit(
                        audit["id"],
                        outcome="succeeded",
                    )
                    self._send(HTTPStatus.OK, result)
                    return

                if parsed.path == "/v1/dashboard/backups/prune-expired":
                    principal = self._require("operator")
                    if principal is None:
                        return
                    if (
                        str(body.get("confirm") or "")
                        != "PRUNE_EXPIRED_VERIFIED_BACKUPS"
                    ):
                        self._send(
                            HTTPStatus.BAD_REQUEST,
                            {"error":"exact backup retention prune confirmation required"},
                        )
                        return
                    expected_count = body.get("expected_candidate_count")
                    expected_fingerprint = str(
                        body.get("expected_candidate_fingerprint") or ""
                    ).strip().lower()
                    if (
                        isinstance(expected_count, bool)
                        or not isinstance(expected_count, int)
                        or expected_count < 0
                    ):
                        self._send(
                            HTTPStatus.BAD_REQUEST,
                            {
                                "error":(
                                    "expected_candidate_count must be "
                                    "a non-negative integer"
                                )
                            },
                        )
                        return
                    if (
                        len(expected_fingerprint) != 64
                        or any(
                            ch not in "0123456789abcdef"
                            for ch in expected_fingerprint
                        )
                    ):
                        self._send(
                            HTTPStatus.BAD_REQUEST,
                            {
                                "error":(
                                    "expected_candidate_fingerprint must be "
                                    "a SHA-256 hex digest"
                                )
                            },
                        )
                        return
                    requested_by = f"{principal.role}:{principal.name}"
                    audit = control.dashboard_store.append_control_audit(
                        action="backup-retention-prune",
                        worker_id="control-plane",
                        requested_by=requested_by,
                        outcome="requested",
                    )
                    try:
                        result = control.dashboard.prune_expired_backups(
                            expected_count,
                            expected_fingerprint,
                        )
                    except BackupRetentionCandidateConflict as exc:
                        control.dashboard_store.update_control_audit(
                            audit["id"],
                            outcome="conflict",
                            error_code="candidate_set_changed",
                        )
                        self._send(
                            HTTPStatus.CONFLICT,
                            {
                                "error":"backup retention candidate set changed",
                                "expected_candidate_count":exc.expected_count,
                                "actual_candidate_count":exc.actual_count,
                                "fingerprint_changed":exc.fingerprint_changed,
                                "deleted_count":0,
                                "deleted_bytes":0,
                            },
                        )
                        return
                    except BackupError as exc:
                        control.dashboard_store.update_control_audit(
                            audit["id"],
                            outcome="failed",
                            error_code="backup_retention_prune_unavailable",
                        )
                        self._send(
                            HTTPStatus.CONFLICT,
                            {"error":str(exc)},
                        )
                        return
                    except Exception:
                        control.dashboard_store.update_control_audit(
                            audit["id"],
                            outcome="failed",
                            error_code="backup_retention_prune_failed",
                        )
                        raise
                    control.dashboard_store.update_control_audit(
                        audit["id"],
                        outcome="succeeded",
                    )
                    self._send(HTTPStatus.OK, result)
                    return

                if parsed.path == "/v1/dashboard/backups/prune-temp":
                    principal = self._require("operator")
                    if principal is None:
                        return
                    if (
                        str(body.get("confirm") or "")
                        != "PRUNE_STALE_BACKUP_TEMPS"
                    ):
                        self._send(
                            HTTPStatus.BAD_REQUEST,
                            {"error":"exact backup temp prune confirmation required"},
                        )
                        return
                    expected = body.get("expected_candidate_count")
                    if (
                        isinstance(expected, bool)
                        or not isinstance(expected, int)
                        or expected < 0
                    ):
                        self._send(
                            HTTPStatus.BAD_REQUEST,
                            {
                                "error":(
                                    "expected_candidate_count must be "
                                    "a non-negative integer"
                                )
                            },
                        )
                        return
                    requested_by = f"{principal.role}:{principal.name}"
                    audit = control.dashboard_store.append_control_audit(
                        action="backup-temp-prune",
                        worker_id="control-plane",
                        requested_by=requested_by,
                        outcome="requested",
                    )
                    try:
                        result = control.dashboard.prune_backup_temps(
                            expected
                        )
                    except BackupTempCandidateConflict as exc:
                        control.dashboard_store.update_control_audit(
                            audit["id"],
                            outcome="conflict",
                            error_code="candidate_count_mismatch",
                        )
                        self._send(
                            HTTPStatus.CONFLICT,
                            {
                                "error":"backup temp candidate count changed",
                                "expected_candidate_count":exc.expected,
                                "actual_candidate_count":exc.actual,
                                "deleted_count":0,
                                "deleted_bytes":0,
                            },
                        )
                        return
                    except BackupError as exc:
                        control.dashboard_store.update_control_audit(
                            audit["id"],
                            outcome="failed",
                            error_code="backup_temp_prune_unavailable",
                        )
                        self._send(
                            HTTPStatus.CONFLICT,
                            {"error":str(exc)},
                        )
                        return
                    except Exception:
                        control.dashboard_store.update_control_audit(
                            audit["id"],
                            outcome="failed",
                            error_code="backup_temp_prune_failed",
                        )
                        raise
                    control.dashboard_store.update_control_audit(
                        audit["id"],
                        outcome="succeeded",
                    )
                    self._send(HTTPStatus.OK, result)
                    return

                if parsed.path == "/v1/dashboard/backups/create":
                    principal = self._require("operator")
                    if principal is None:
                        return
                    if str(body.get("confirm") or "") != "CREATE_VERIFIED_BACKUP":
                        self._send(
                            HTTPStatus.BAD_REQUEST,
                            {"error":"exact backup confirmation required"},
                        )
                        return
                    requested_by = f"{principal.role}:{principal.name}"
                    audit = control.dashboard_store.append_control_audit(
                        action="backup-create",
                        worker_id="control-plane",
                        requested_by=requested_by,
                        outcome="requested",
                    )
                    try:
                        result = control.dashboard.create_verified_backup()
                    except BackupError as exc:
                        control.dashboard_store.update_control_audit(
                            audit["id"],
                            outcome="failed",
                            error_code="backup_unavailable",
                        )
                        self._send(
                            HTTPStatus.CONFLICT,
                            {"error":str(exc)},
                        )
                        return
                    except Exception:
                        control.dashboard_store.update_control_audit(
                            audit["id"],
                            outcome="failed",
                            error_code="backup_failed",
                        )
                        raise
                    control.dashboard_store.update_control_audit(
                        audit["id"],
                        outcome="succeeded",
                    )
                    self._send(HTTPStatus.CREATED, result)
                    return

                if parsed.path == "/v1/dashboard/maintenance/prune":
                    principal = self._require("operator")
                    if principal is None:
                        return
                    if str(body.get("confirm") or "") != "PRUNE_EXPIRED_HISTORY":
                        self._send(
                            HTTPStatus.BAD_REQUEST,
                            {"error":"exact prune confirmation required"},
                        )
                        return
                    expected = body.get("expected_candidate_rows")
                    if (
                        isinstance(expected, bool)
                        or not isinstance(expected, int)
                        or expected < 0
                    ):
                        self._send(
                            HTTPStatus.BAD_REQUEST,
                            {"error":"expected_candidate_rows must be a non-negative integer"},
                        )
                        return
                    requested_by = f"{principal.role}:{principal.name}"
                    audit = control.dashboard_store.append_control_audit(
                        action="retention-prune",
                        worker_id="control-plane",
                        requested_by=requested_by,
                        outcome="requested",
                    )
                    try:
                        result = control.dashboard.prune_maintenance(expected)
                    except RetentionCandidateConflict as exc:
                        control.dashboard_store.update_control_audit(
                            audit["id"],
                            outcome="conflict",
                            error_code="candidate_count_mismatch",
                        )
                        self._send(
                            HTTPStatus.CONFLICT,
                            {
                                "error":"retention candidate count changed",
                                "expected_candidate_rows":exc.expected,
                                "actual_candidate_rows":exc.actual,
                                "deleted_rows":0,
                            },
                        )
                        return
                    except Exception:
                        control.dashboard_store.update_control_audit(
                            audit["id"],
                            outcome="failed",
                            error_code="retention_prune_failed",
                        )
                        raise
                    control.dashboard_store.update_control_audit(
                        audit["id"],
                        outcome="succeeded",
                    )
                    self._send(
                        HTTPStatus.OK,
                        {
                            **result,
                            "protected_candidate_rows":(
                                result.get("maintenance", {}).get(
                                    "protected_candidate_rows",
                                    0,
                                )
                            ),
                        },
                    )
                    return

                if (
                    len(parts) == 5
                    and parts[0] == "v1"
                    and parts[1] == "dashboard"
                    and parts[2] == "incidents"
                    and parts[4] == "acknowledge"
                ):
                    principal = self._require("operator")
                    if principal is None:
                        return
                    incident_id = parts[3]
                    try:
                        incident = control.dashboard_store.acknowledge_dashboard_incident(
                            incident_id,
                            acknowledged_by=f"{principal.role}:{principal.name}",
                        )
                    except KeyError:
                        self._send(
                            HTTPStatus.NOT_FOUND,
                            {"error":"incident not found"},
                        )
                        return
                    self._send(
                        HTTPStatus.OK,
                        {"incident":incident},
                    )
                    return

                if (
                    len(parts) == 5
                    and parts[0] == "v1"
                    and parts[1] == "dashboard"
                    and parts[2] == "workers"
                    and parts[4] == "control"
                ):
                    principal = self._require("operator")
                    if principal is None:
                        return
                    action = str(body.get("action") or "").strip()
                    state_by_action = {
                        "pause":"paused",
                        "resume":"active",
                        "drain":"draining",
                    }
                    worker_id = parts[3]
                    requested_by = f"{principal.role}:{principal.name}"
                    audit_job_key = (
                        str(body.get("job_key") or "").strip() or None
                    )
                    incident_id = (
                        str(body.get("incident_id") or "").strip() or None
                    )
                    remediation_event = None
                    if incident_id is not None:
                        incident_rows = control.dashboard.incidents(
                            limit=500,
                        )["incidents"]
                        incident = next(
                            (
                                item for item in incident_rows
                                if str(item.get("id") or "") == incident_id
                            ),
                            None,
                        )
                        if incident is None:
                            self._send(
                                HTTPStatus.NOT_FOUND,
                                {"error":"incident not found"},
                            )
                            return
                        matched = next(
                            (
                                item
                                for item in (
                                    (incident.get("playbook") or {}).get(
                                        "suggestions"
                                    ) or []
                                )
                                if str(item.get("action") or "") == action
                                and str(item.get("worker_id") or "") == worker_id
                                and (
                                    str(item.get("job_key") or "")
                                    == str(audit_job_key or "")
                                )
                                and str(item.get("availability") or "")
                                in {"available", "fallback"}
                            ),
                            None,
                        )
                        if matched is None:
                            self._send(
                                HTTPStatus.CONFLICT,
                                {"error":"incident remediation is stale or unavailable"},
                            )
                            return
                        remediation_event = (
                            control.dashboard_store.append_remediation_event(
                                incident_id=incident_id,
                                action=action,
                                worker_id=worker_id,
                                job_key=audit_job_key,
                                requested_by=requested_by,
                                outcome="requested",
                            )
                        )
                    audit_event = control.dashboard_store.append_control_audit(
                        action=action or "invalid",
                        worker_id=worker_id,
                        job_key=audit_job_key,
                        requested_by=requested_by,
                        outcome="requested",
                    )

                    def audit_control(
                        outcome: str,
                        *,
                        job_key: str | None = None,
                        error_code: str | None = None,
                    ) -> None:
                        del job_key
                        try:
                            control.dashboard_store.update_control_audit(
                                audit_event["id"],
                                outcome=outcome,
                                error_code=error_code,
                            )
                        except Exception:
                            # The pre-action reservation remains durable even
                            # if result finalization cannot be written.
                            pass
                        if remediation_event is not None:
                            try:
                                control.dashboard_store.update_remediation_event(
                                    remediation_event["id"],
                                    outcome=outcome,
                                    error_code=error_code,
                                )
                            except Exception:
                                # Keep the requested remediation event durable
                                # even if final outcome persistence fails.
                                pass

                    if action == "recover-stuck":
                        job_key = str(body.get("job_key") or "").strip()
                        if not job_key:
                            audit_control(
                                "failed",
                                error_code="job_key_required",
                            )
                            self._send(
                                HTTPStatus.BAD_REQUEST,
                                {"error":"job_key required"},
                            )
                            return
                        try:
                            job = control.queue.get(job_key)
                        except KeyError:
                            audit_control(
                                "failed",
                                job_key=job_key,
                                error_code="job_not_found",
                            )
                            self._send(
                                HTTPStatus.NOT_FOUND,
                                {"error":"job not found"},
                            )
                            return
                        if str(job.get("claimed_by") or "") != worker_id:
                            audit_control(
                                "failed",
                                job_key=job_key,
                                error_code="job_not_claimed_by_worker",
                            )
                            self._send(
                                HTTPStatus.CONFLICT,
                                {"error":"job not claimed by worker"},
                            )
                            return
                        try:
                            recovered = control.queue.recover_job(
                                job_key,
                                max_attempts=int(body.get("max_attempts", 3)),
                            )
                        except RuntimeError:
                            audit_control(
                                "failed",
                                job_key=job_key,
                                error_code="job_not_recoverable",
                            )
                            raise
                        audit_control(
                            str(recovered.get("status") or "recovered"),
                            job_key=job_key,
                        )
                        self._send(
                            HTTPStatus.OK,
                            {
                                "accepted":True,
                                "worker_id":worker_id,
                                "job":recovered,
                            },
                        )
                        return

                    if action == "kick":
                        kicked = control.dashboard_control.kick_worker(worker_id)
                        status = (
                            HTTPStatus.BAD_GATEWAY
                            if kicked.get("status") == "failed"
                            else HTTPStatus.ACCEPTED
                        )
                        audit_control(
                            str(kicked.get("status") or "failed"),
                            error_code=(
                                str(kicked.get("error"))
                                if kicked.get("status") == "failed"
                                else None
                            ),
                        )
                        self._send(
                            status,
                            {
                                "accepted":kicked.get("status") != "failed",
                                "worker_id":worker_id,
                                **kicked,
                            },
                        )
                        return

                    if action == "retry":
                        job_key = str(body.get("job_key") or "").strip()
                        if not job_key:
                            audit_control("failed", error_code="job_key_required")
                            self._send(
                                HTTPStatus.BAD_REQUEST,
                                {"error":"job_key required"},
                            )
                            return
                        try:
                            retried = control.dashboard_control.retry_job(
                                job_key,
                                requested_by=requested_by,
                            )
                        except RuntimeError:
                            audit_control(
                                "failed",
                                job_key=job_key,
                                error_code="retry_rejected",
                            )
                            raise
                        audit_control("accepted", job_key=job_key)
                        self._send(
                            HTTPStatus.CREATED,
                            {
                                "accepted":True,
                                "source_job_key":job_key,
                                "workflow_id":retried["workflow_id"],
                                "workflow_task_id":retried["workflow_task_id"],
                                "job":retried["replacement_job"],
                            },
                        )
                        return

                    if action == "cancel-current":
                        job_key = str(body.get("job_key") or "").strip()
                        if not job_key:
                            audit_control("failed", error_code="job_key_required")
                            self._send(
                                HTTPStatus.BAD_REQUEST,
                                {"error":"job_key required"},
                            )
                            return
                        try:
                            job = control.queue.get(job_key)
                        except KeyError:
                            audit_control(
                                "failed",
                                job_key=job_key,
                                error_code="job_not_found",
                            )
                            self._send(
                                HTTPStatus.NOT_FOUND,
                                {"error":"job not found"},
                            )
                            return
                        if str(job.get("claimed_by") or "") != worker_id:
                            audit_control(
                                "failed",
                                job_key=job_key,
                                error_code="job_not_claimed_by_worker",
                            )
                            self._send(
                                HTTPStatus.CONFLICT,
                                {"error":"job not claimed by worker"},
                            )
                            return
                        if str(job.get("status") or "") not in {
                            "claimed","acked","running"
                        }:
                            audit_control(
                                "failed",
                                job_key=job_key,
                                error_code="job_not_active",
                            )
                            self._send(
                                HTTPStatus.CONFLICT,
                                {"error":"job is not active"},
                            )
                            return
                        state = control.dashboard_control.request_job_cancel(
                            job_key,
                            requested_by=requested_by,
                            reason=(
                                str(body.get("reason")).strip()
                                if body.get("reason") is not None
                                else None
                            ),
                        )
                        audit_control("accepted", job_key=job_key)
                        self._send(
                            HTTPStatus.ACCEPTED,
                            {
                                "accepted":True,
                                "worker_id":worker_id,
                                "job_key":job_key,
                                "desired_state":state["desired_state"],
                                "requested_at":state.get("requested_at"),
                                "acknowledged":state.get("acknowledged_at") is not None,
                                "acknowledged_at":state.get("acknowledged_at"),
                            },
                        )
                        return

                    desired_state = state_by_action.get(action)
                    if desired_state is None:
                        audit_control(
                            "failed",
                            error_code="invalid_worker_control_action",
                        )
                        self._send(
                            HTTPStatus.BAD_REQUEST,
                            {"error":"invalid worker control action"},
                        )
                        return
                    state = control.dashboard_control.set_worker_state(
                        worker_id,
                        desired_state,
                        requested_by=requested_by,
                        reason=(
                            str(body.get("reason")).strip()
                            if body.get("reason") is not None
                            else None
                        ),
                    )
                    audit_control("accepted")
                    self._send(
                        HTTPStatus.ACCEPTED,
                        {
                            "accepted":True,
                            "worker_id":worker_id,
                            "desired_state":state["desired_state"],
                            "requested_at":state.get("requested_at"),
                            "acknowledged":state.get("acknowledged_at") is not None,
                            "acknowledged_at":state.get("acknowledged_at"),
                        },
                    )
                    return

                if parsed.path == "/v1/stragglers/speculate":
                    principal = self._require("operator")
                    if principal is None:
                        return
                    control.workers.load()
                    stragglers = control.optimizer.stragglers(
                        threshold_factor=float(
                            body.get("threshold_factor", 1.75)
                        ),
                        min_runtime_seconds=float(
                            body.get("min_runtime_seconds", 60.0)
                        ),
                        min_samples=int(
                            body.get("min_samples", 2)
                        ),
                        workers=list(
                            control.workers.workers.values()
                        ),
                    )
                    spawned = []
                    skipped = []
                    for item in stragglers:
                        alternate = item.get("alternate_worker")
                        if not alternate:
                            skipped.append({
                                "job_key":item["job_key"],
                                "reason":"no alternate worker",
                            })
                            continue
                        try:
                            job = control.speculation.spawn(
                                item["job_key"],
                                target_worker=str(
                                    alternate["worker_id"]
                                ),
                            )
                        except RuntimeError as exc:
                            skipped.append({
                                "job_key":item["job_key"],
                                "reason":str(exc),
                            })
                            continue
                        spawned.append(job)

                    self._send(
                        HTTPStatus.OK,
                        {
                            "spawned":spawned,
                            "skipped":skipped,
                        },
                    )
                    return

                if parsed.path == "/v1/github/pr-refresh":
                    principal = self._require("operator")
                    if principal is None:
                        return
                    repository = str(body["repository"])
                    pr_number = int(body["pr_number"])
                    workflows = control.workflows.find_by_github_pr(
                        repository,
                        pr_number,
                    )
                    if not workflows:
                        self._send(
                            HTTPStatus.OK,
                            {
                                "repository":repository,
                                "pr_number":pr_number,
                                "changed_paths":[],
                                "workflows":[],
                                "refreshed":0,
                            },
                        )
                        return

                    changed_paths = GitHubClient().list_pull_request_files(
                        repository,
                        pr_number,
                    )
                    refreshed = []
                    for workflow in workflows:
                        decisions = control.workflows.apply_change_impact(
                            workflow["id"],
                            changed_paths,
                        )
                        refreshed.append({
                            "workflow_id":workflow["id"],
                            "decisions":decisions,
                            "workflow":control.workflows.get(
                                workflow["id"]
                            ),
                        })
                    self._send(
                        HTTPStatus.OK,
                        {
                            "repository":repository,
                            "pr_number":pr_number,
                            "changed_paths":changed_paths,
                            "workflows":refreshed,
                            "refreshed":len(refreshed),
                        },
                    )
                    return

                if parsed.path == "/v1/workflows":
                    principal = self._require("operator")
                    if principal is None:
                        return
                    tasks = [
                        WorkflowTaskSpec.from_dict(item)
                        for item in body.get("tasks", [])
                    ]
                    workflow = control.workflows.create(
                        name=str(body["name"]),
                        repository=str(body["repository"]),
                        tasks=tasks,
                        metadata=dict(body.get("metadata") or {}),
                        workflow_id=(
                            str(body["workflow_id"])
                            if body.get("workflow_id")
                            else None
                        ),
                    )
                    self._send(
                        HTTPStatus.CREATED,
                        {"workflow":workflow},
                    )
                    return

                if parsed.path.startswith("/v1/workflows/"):
                    parts = [part for part in parsed.path.split("/") if part]
                    if len(parts) >= 4:
                        principal = self._require("operator")
                        if principal is None:
                            return
                        workflow_id = parts[2]
                        action = parts[3]
                        if action == "dispatch":
                            jobs = control.workflows.dispatch_ready(
                                workflow_id,
                                limit=int(body.get("limit", 10)),
                            )
                            self._send(HTTPStatus.OK, {"jobs":jobs})
                            return
                        if action == "impact":
                            decisions = control.workflows.apply_change_impact(
                                workflow_id,
                                [
                                    str(path)
                                    for path in body.get(
                                        "changed_paths",
                                        [],
                                    )
                                ],
                            )
                            self._send(
                                HTTPStatus.OK,
                                {
                                    "decisions":decisions,
                                    "workflow":control.workflows.get(
                                        workflow_id
                                    ),
                                },
                            )
                            return
                        if action == "impact-pr":
                            repository = str(body["repository"])
                            pr_number = int(body["pr_number"])
                            changed_paths = GitHubClient().list_pull_request_files(
                                repository,
                                pr_number,
                            )
                            decisions = control.workflows.apply_change_impact(
                                workflow_id,
                                changed_paths,
                            )
                            self._send(
                                HTTPStatus.OK,
                                {
                                    "repository":repository,
                                    "pr_number":pr_number,
                                    "changed_paths":changed_paths,
                                    "decisions":decisions,
                                    "workflow":control.workflows.get(
                                        workflow_id
                                    ),
                                },
                            )
                            return
                        if action == "cancel":
                            workflow = control.workflows.cancel(workflow_id)
                            self._send(
                                HTTPStatus.OK,
                                {"workflow":workflow},
                            )
                            return
                        if action == "promote":
                            release = control.releases.promote(
                                workflow_id=workflow_id,
                                artifact_id=str(body["artifact_id"]),
                                validation=dict(
                                    body.get("validation") or {}
                                ),
                                attestation=dict(
                                    body.get("attestation") or {}
                                ),
                                approval={
                                    "approved":True,
                                    "approved_by":principal.name,
                                    "role":principal.role,
                                    **(
                                        {
                                            "reason":str(
                                                body["approval_reason"]
                                            )
                                        }
                                        if body.get("approval_reason")
                                        else {}
                                    ),
                                },
                                metadata=dict(
                                    body.get("metadata") or {}
                                ),
                            )
                            self._send(
                                HTTPStatus.CREATED,
                                {"release":release},
                            )
                            return
                        if action == "releases":
                            self._send(
                                HTTPStatus.OK,
                                {
                                    "releases":
                                        control.releases.list_for_workflow(
                                            workflow_id
                                        )
                                },
                            )
                            return
                        if action == "artifacts":
                            artifact = control.workflows.add_artifact(
                                workflow_id,
                                task_id=(
                                    str(body["task_id"])
                                    if body.get("task_id")
                                    else None
                                ),
                                name=str(body["name"]),
                                uri=str(body["uri"]),
                                sha256=(
                                    str(body["sha256"])
                                    if body.get("sha256")
                                    else None
                                ),
                                metadata=dict(body.get("metadata") or {}),
                            )
                            self._send(
                                HTTPStatus.CREATED,
                                {"artifact":artifact},
                            )
                            return

                if parsed.path == "/v1/workers/register":
                    principal = self._require("operator")
                    if principal is None:
                        return
                    worker_id = str(body["worker_id"])
                    worker = control.workers.register(
                        worker_id,
                        [str(x) for x in body.get("capabilities", [])],
                        int(body.get("max_concurrency", 1)),
                    )
                    reconciliation = None
                    if "active_job_keys" in body:
                        raw_active = body.get("active_job_keys")
                        if not isinstance(raw_active, list):
                            raise ValueError("active_job_keys must be a list")
                        active_job_keys = sorted({
                            str(key).strip()
                            for key in raw_active
                            if str(key).strip()
                        })
                        recovered = control.reconcile_worker_registration(
                            worker_id,
                            active_job_keys,
                        )
                        worker = control.workers.heartbeat(
                            worker_id,
                            active_tasks=len(active_job_keys),
                        )
                        reconciliation = {
                            "reported_active_job_keys":active_job_keys,
                            "recovered_jobs":recovered,
                        }
                    self._send(
                        HTTPStatus.OK,
                        {
                            "worker":worker.to_dict(),
                            "reconciliation":reconciliation,
                        },
                    )
                    return

                if parsed.path == "/v1/workers/heartbeat":
                    principal = self._require("worker")
                    if principal is None:
                        return
                    worker = control.workers.heartbeat(
                        str(body["worker_id"]),
                        active_tasks=(
                            int(body["active_tasks"])
                            if "active_tasks" in body
                            else None
                        ),
                    )
                    capacity = body.get("capacity")
                    if isinstance(capacity, dict):
                        source = str(capacity.get("source") or "").strip()
                        source_status = str(capacity.get("status") or "unavailable")
                        used = capacity.get("used_this_month")
                        remaining = capacity.get("remaining_tokens")
                        if source:
                            authenticated = (
                                source_status == "ok"
                                and capacity.get("authenticated_usage") is True
                            )
                            used_value = used if authenticated and isinstance(used, int) else None
                            remaining_value = (
                                remaining
                                if authenticated and isinstance(remaining, int)
                                else None
                            )
                            limit_value = (
                                used_value + remaining_value
                                if used_value is not None and remaining_value is not None
                                else None
                            )
                            control.dashboard_store.save_provider_quota_snapshot({
                                "id": f"{source}:{__import__('time').time_ns()}",
                                "provider": source,
                                "quota_type": "monthly_tokens",
                                "used_value": used_value,
                                "limit_value": limit_value,
                                "remaining_value": remaining_value,
                                "unit": "tokens",
                                "source_status": "authenticated" if authenticated else "unavailable",
                                "captured_at": __import__("datetime").datetime.now(
                                    __import__("datetime").timezone.utc
                                ).isoformat(),
                            })
                    active_job_keys = body.get(
                        "active_job_keys",
                        [],
                    )
                    if not isinstance(active_job_keys, list):
                        raise ValueError(
                            "active_job_keys must be a list"
                        )
                    stale_job_keys = []
                    for key in active_job_keys:
                        try:
                            job = control.queue.get(str(key))
                        except KeyError:
                            stale_job_keys.append(str(key))
                            continue
                        if not control.workflows.job_generation_current(
                            job
                        ):
                            stale_job_keys.append(str(key))
                    control_state = body.get("control_state")
                    if control_state is not None:
                        current_control = control.dashboard_control.worker_state(
                            str(body["worker_id"])
                        )
                        if str(control_state) == current_control["desired_state"]:
                            current_control = (
                                control.dashboard_control.acknowledge_worker_state(
                                    str(body["worker_id"]),
                                    str(control_state),
                                )
                            )
                    else:
                        current_control = control.dashboard_control.worker_state(
                            str(body["worker_id"])
                        )

                    job_control_states = body.get("job_control_states", {})
                    if not isinstance(job_control_states, dict):
                        raise ValueError("job_control_states must be an object")
                    for raw_key, raw_state in job_control_states.items():
                        job_key = str(raw_key)
                        reported_state = str(raw_state)
                        current_job_control = control.dashboard_control.job_state(job_key)
                        if (
                            reported_state == "cancel_requested"
                            and current_job_control["desired_state"] == "cancel_requested"
                            and current_job_control.get("acknowledged_at") is None
                        ):
                            job = control.queue.get(job_key)
                            if str(job.get("claimed_by") or "") != str(body["worker_id"]):
                                raise RuntimeError("job claim owner mismatch")
                            cancelled_job = control.queue.cancel(
                                job_key,
                                str(body["worker_id"]),
                            )
                            control.dashboard_control.acknowledge_job_cancel(job_key)
                            control.dashboard_store.finish_execution(
                                job_key,
                                str(body["worker_id"]),
                                status="cancelled",
                                duration_seconds=None,
                                result={"reason":"operator cancel"},
                            )
                            payload = cancelled_job.get("payload") or {}
                            workflow_id = payload.get("workflow_id")
                            workflow_task_id = payload.get("workflow_task_id")
                            if workflow_id and workflow_task_id:
                                control.workflows.record_cancelled(
                                    str(workflow_id),
                                    str(workflow_task_id),
                                    result={"reason":"operator cancel"},
                                )

                    self._send(
                        HTTPStatus.OK,
                        {
                            "worker":worker.to_dict(),
                            "stale_job_keys":stale_job_keys,
                            "control":{
                                "worker":current_control,
                                "jobs":{
                                    str(key):control.dashboard_control.job_state(str(key))
                                    for key in active_job_keys
                                },
                            },
                        },
                    )
                    return

                if parsed.path == "/v1/incident-snapshot":
                    principal = self._require("operator")
                    if principal is None:
                        return
                    allowed = {"validator_id", "builder_id", "key_id"}
                    unknown = sorted(set(body) - allowed)
                    if unknown:
                        self._send(
                            HTTPStatus.BAD_REQUEST,
                            {
                                "error": "unknown incident snapshot fields",
                                "fields": unknown,
                            },
                        )
                        return
                    filters = {}
                    for name in allowed:
                        value = body.get(name)
                        if value is None:
                            filters[name] = None
                            continue
                        if not isinstance(value, str) or not value.strip():
                            self._send(
                                HTTPStatus.BAD_REQUEST,
                                {
                                    "error":
                                        f"{name} must be a non-empty string",
                                },
                            )
                            return
                        if len(value) > 512:
                            self._send(
                                HTTPStatus.BAD_REQUEST,
                                {"error": f"{name} is too long"},
                            )
                            return
                        filters[name] = value.strip()
                    result = control.releases.record_incident_report(
                        validator_id=filters["validator_id"],
                        builder_id=filters["builder_id"],
                        key_id=filters["key_id"],
                    )
                    self._send(
                        HTTPStatus.CREATED if result["recorded"]
                        else HTTPStatus.OK,
                        {
                            "schema_version":
                                "production-os/trust-incident-snapshot/v1",
                            **result,
                        },
                    )
                    return

                if parsed.path.startswith("/v1/releases/"):
                    parts = [
                        part
                        for part in parsed.path.split("/")
                        if part
                    ]
                    if (
                        len(parts) == 4
                        and parts[1] == "releases"
                        and parts[3] == "rollback"
                    ):
                        principal = self._require("operator")
                        if principal is None:
                            return
                        release = control.releases.rollback(
                            parts[2],
                            reason=str(body.get("reason") or ""),
                            metadata=dict(
                                body.get("metadata") or {}
                            ),
                        )
                        self._send(
                            HTTPStatus.CREATED,
                            {"release":release},
                        )
                        return

                if parsed.path == "/v1/jobs/enqueue":
                    principal = self._require("operator")
                    if principal is None:
                        return
                    job = control.queue.enqueue(body)
                    self._send(HTTPStatus.CREATED, {"job":job})
                    return

                if parsed.path == "/v1/jobs/claim":
                    principal = self._require("worker")
                    if principal is None:
                        return

                    control.queue.recover_expired(max_attempts=3)
                    control.recover_abandoned_acked_jobs()

                    worker_id = str(body["worker_id"])
                    capabilities = [
                        str(x) for x in body.get("capabilities", [])
                    ]

                    desired = control.dashboard_control.worker_state(worker_id)
                    if desired["desired_state"] in {"paused", "draining"}:
                        self._send(HTTPStatus.NO_CONTENT, {})
                        return

                    compatible = []
                    for queued in control.queue.peek_candidates(
                        worker_id=worker_id,
                        limit=100,
                    ):
                        job_control = control.dashboard_control.job_state(
                            str(queued.get("key") or "")
                        )
                        if (
                            job_control.get("desired_state")
                            == "cancel_requested"
                        ):
                            try:
                                control.dashboard.finalize_queued_cancel(
                                    queued,
                                    requested_by=str(
                                        job_control.get("requested_by")
                                        or "operator"
                                    ),
                                )
                            except RuntimeError:
                                pass
                            continue
                        if not control.workflows.job_generation_current(
                            queued
                        ):
                            continue
                        required = set(
                            queued["payload"].get(
                                "required_capabilities",
                                [],
                            )
                        )
                        if required.issubset(set(capabilities)):
                            compatible.append(queued)

                    if not compatible:
                        self._send(HTTPStatus.NO_CONTENT, {})
                        return

                    ranked = control.portfolio.rank(compatible)
                    candidate = ranked[0]["job"]

                    assigned = candidate.get("assigned_worker")
                    control.workers.load()
                    available_workers = list(
                        control.workers.workers.values()
                    )
                    if assigned:
                        available_workers = [
                            worker
                            for worker in available_workers
                            if worker.worker_id == assigned
                        ]

                    placement = control.optimizer.choose_worker(
                        repository=candidate["repository"],
                        task=candidate["task"],
                        workers=available_workers,
                        required_capabilities=list(
                            candidate["payload"].get(
                                "required_capabilities",
                                [],
                            )
                        ),
                        fallback_minutes=float(
                            candidate["payload"]
                            .get("handoff", {})
                            .get("estimated_minutes", 1.0)
                        ),
                    )
                    if (
                        placement is not None
                        and placement.worker_id != worker_id
                    ):
                        self._send(HTTPStatus.NO_CONTENT, {})
                        return

                    job = control.queue.claim_key(
                        candidate["key"],
                        worker_id,
                        ack_timeout_seconds=int(
                            body.get("ack_timeout_seconds", 120)
                        ),
                    )
                    if job is None:
                        self._send(HTTPStatus.NO_CONTENT, {})
                        return

                    self._send(
                        HTTPStatus.OK,
                        {
                            "job":job,
                            "optimization":{
                                "portfolio_score":ranked[0]["score"],
                                "critical":ranked[0]["critical"],
                                "descendants":ranked[0]["descendants"],
                                "predicted_minutes":ranked[0][
                                    "predicted_minutes"
                                ],
                            },
                        },
                    )
                    return

                if parsed.path == "/v1/jobs/ack":
                    principal = self._require("worker")
                    if principal is None:
                        return
                    key = str(body["key"])
                    before = control.queue.get(key)
                    if not control.workflows.job_generation_current(
                        before
                    ):
                        self._send(
                            HTTPStatus.CONFLICT,
                            {
                                "error":"stale workflow generation",
                                "key":key,
                            },
                        )
                        return
                    worker_id = str(body["worker_id"])
                    job = control.queue.ack(key, worker_id)
                    control.dashboard_store.start_execution(job, worker_id)
                    self._send(HTTPStatus.OK, {"job":job})
                    return

                if (
                    parsed.path.startswith("/v1/jobs/")
                    and parsed.path.endswith("/telemetry")
                ):
                    principal = self._require("worker")
                    if principal is None:
                        return
                    parts = [part for part in parsed.path.split("/") if part]
                    if len(parts) != 4 or parts[:2] != ["v1", "jobs"]:
                        self._send(HTTPStatus.NOT_FOUND, {"error":"not found"})
                        return
                    key = parts[2]
                    worker_id = str(body.get("worker_id") or "")
                    job = control.queue.get(key)
                    if job.get("claimed_by") != worker_id:
                        self._send(
                            HTTPStatus.CONFLICT,
                            {"error":"job claim owner mismatch"},
                        )
                        return
                    execution = control.dashboard_store.update_live_execution(
                        key, worker_id, body
                    )
                    logs = body.get("logs") or []
                    if logs:
                        if not isinstance(logs, list):
                            raise ValueError("logs must be a list")
                        enriched = [
                            {
                                **dict(row),
                                "repository": job.get("repository"),
                                "job_key": key,
                            }
                            for row in logs
                            if isinstance(row, dict)
                        ]
                        control.dashboard_store.append_logs(worker_id, enriched)
                    self._send(HTTPStatus.OK, {"execution":execution})
                    return

                if parsed.path == "/v1/jobs/stale-checkpoint":
                    principal = self._require("worker")
                    if principal is None:
                        return
                    key = str(body["key"])
                    worker_id = str(body["worker_id"])
                    checkpoint_ref = str(
                        body.get("checkpoint_ref") or ""
                    ).strip()
                    if not checkpoint_ref:
                        raise ValueError("checkpoint_ref is required")

                    job = control.queue.get(key)
                    if job.get("claimed_by") != worker_id:
                        raise RuntimeError("job claim owner mismatch")
                    if control.workflows.job_generation_current(job):
                        raise RuntimeError(
                            "job is not from a stale workflow generation"
                        )

                    payload = dict(job.get("payload") or {})
                    with control.backend.transaction() as db:
                        control.backend.append_event(
                            db,
                            "stale-job-checkpointed",
                            {
                                "job_key":key,
                                "worker_id":worker_id,
                                "checkpoint_ref":checkpoint_ref,
                                "workflow_id":payload.get(
                                    "workflow_id"
                                ),
                                "workflow_generation":payload.get(
                                    "workflow_generation"
                                ),
                                "source_revision":payload.get(
                                    "source_revision"
                                ),
                            },
                            repository=job.get("repository"),
                            task_key_value=key,
                        )

                    self._send(
                        HTTPStatus.OK,
                        {
                            "status":"checkpointed",
                            "key":key,
                            "checkpoint_ref":checkpoint_ref,
                        },
                    )
                    return

                if parsed.path == "/v1/jobs/complete":
                    principal = self._require("worker")
                    if principal is None:
                        return
                    key = str(body["key"])
                    worker_id = str(body["worker_id"])
                    before = control.queue.get(key)
                    if not control.workflows.job_generation_current(
                        before
                    ):
                        self._send(
                            HTTPStatus.CONFLICT,
                            {
                                "error":"stale workflow generation",
                                "key":key,
                            },
                        )
                        return

                    duration_seconds = body.get("duration_seconds")
                    if duration_seconds is not None:
                        control.optimizer.record_execution(
                            repository=before["repository"],
                            task=before["task"],
                            worker_id=worker_id,
                            duration_seconds=float(duration_seconds),
                            succeeded=True,
                            capabilities=[
                                str(x)
                                for x in body.get("capabilities", [])
                            ],
                        )

                    group_id = control.speculation.group_for_job(key)
                    if (
                        group_id is not None
                        and not control.speculation.try_win(
                            group_id,
                            key,
                        )
                    ):
                        job = control.speculation.cancel_job(key)
                        self._send(
                            HTTPStatus.OK,
                            {
                                "job":job,
                                "workflow":None,
                                "speculation":{
                                    "group_id":group_id,
                                    "winner":False,
                                },
                            },
                        )
                        return

                    job = control.queue.complete(key, worker_id)
                    control.dashboard_store.finish_execution(
                        key,
                        worker_id,
                        status="succeeded",
                        duration_seconds=(
                            float(duration_seconds)
                            if duration_seconds is not None
                            else None
                        ),
                        result=dict(body.get("result") or {}),
                    )
                    cancelled = []
                    if group_id is not None:
                        cancelled = control.speculation.cancel_losers(
                            group_id,
                            key,
                        )

                    workflow_id = before["payload"].get("workflow_id")
                    workflow_task_id = before["payload"].get(
                        "workflow_task_id"
                    )
                    workflow = None
                    if workflow_id and workflow_task_id:
                        workflow = control.workflows.record_result(
                            str(workflow_id),
                            str(workflow_task_id),
                            succeeded=True,
                            result=dict(body.get("result") or {}),
                        )

                    self._send(
                        HTTPStatus.OK,
                        {
                            "job":job,
                            "workflow":workflow,
                            "speculation":{
                                "group_id":group_id,
                                "winner":True,
                                "cancelled_losers":cancelled,
                            } if group_id else None,
                        },
                    )
                    return

                if parsed.path == "/v1/jobs/fail":
                    principal = self._require("worker")
                    if principal is None:
                        return
                    key = str(body["key"])
                    worker_id = str(body["worker_id"])
                    reason = str(body.get("reason", "worker failure"))
                    before = control.queue.get(key)
                    if not control.workflows.job_generation_current(
                        before
                    ):
                        self._send(
                            HTTPStatus.CONFLICT,
                            {
                                "error":"stale workflow generation",
                                "key":key,
                            },
                        )
                        return

                    duration_seconds = body.get("duration_seconds")
                    if duration_seconds is not None:
                        control.optimizer.record_execution(
                            repository=before["repository"],
                            task=before["task"],
                            worker_id=worker_id,
                            duration_seconds=float(duration_seconds),
                            succeeded=False,
                            capabilities=[
                                str(x)
                                for x in body.get("capabilities", [])
                            ],
                        )

                    job = control.queue.fail(
                        key,
                        worker_id,
                        reason,
                    )
                    control.dashboard_store.finish_execution(
                        key,
                        worker_id,
                        status="failed",
                        duration_seconds=(
                            float(duration_seconds)
                            if duration_seconds is not None
                            else None
                        ),
                        result=dict(body.get("result") or {}),
                        error_message=reason,
                    )
                    group_id = control.speculation.group_for_job(key)
                    if (
                        group_id is not None
                        and not control.speculation.failure_is_terminal(
                            group_id,
                            key,
                        )
                    ):
                        self._send(
                            HTTPStatus.OK,
                            {
                                "job":job,
                                "workflow":None,
                                "speculation":{
                                    "group_id":group_id,
                                    "terminal_failure":False,
                                },
                            },
                        )
                        return

                    workflow_id = before["payload"].get("workflow_id")
                    workflow_task_id = before["payload"].get(
                        "workflow_task_id"
                    )
                    workflow = None
                    if workflow_id and workflow_task_id:
                        workflow = control.workflows.record_result(
                            str(workflow_id),
                            str(workflow_task_id),
                            succeeded=False,
                            result={
                                "reason":reason,
                                **dict(body.get("result") or {}),
                            },
                        )

                    self._send(
                        HTTPStatus.OK,
                        {
                            "job":job,
                            "workflow":workflow,
                            "speculation":{
                                "group_id":group_id,
                                "terminal_failure":True,
                            } if group_id else None,
                        },
                    )
                    return

                if parsed.path == "/v1/jobs/recover":
                    principal = self._require("operator")
                    if principal is None:
                        return
                    actions = control.queue.recover_expired(
                        max_attempts=int(body.get("max_attempts", 3))
                    )
                    self._send(
                        HTTPStatus.OK,
                        {"actions":actions},
                    )
                    return

                self._send(HTTPStatus.NOT_FOUND, {"error":"not found"})
            except KeyError as exc:
                self._send(
                    HTTPStatus.BAD_REQUEST,
                    {"error":f"missing field: {exc.args[0]}"},
                )
            except (ValueError, RuntimeError) as exc:
                self._send(
                    HTTPStatus.CONFLICT,
                    {"error":str(exc)},
                )

    return Handler


def serve_control_plane(
    database: str,
    auth_config: str,
    *,
    host: str = "127.0.0.1",
    port: int = 8787,
    github_webhook_secret: str | None = None,
    trusted_validation_secrets: dict[str, str] | None = None,
    provenance_secret: str | None = None,
    trusted_validation_public_keys: dict[str, str] | None = None,
    provenance_private_key: str | None = None,
    provenance_public_key: str | None = None,
    provenance_signer=None,
    validation_signature_policy: str = "compatible",
    builder_id: str = "https://production-os.local/builder",
    builder_private_key: str | None = None,
    builder_signer=None,
    trusted_builders: dict | None = None,
    trusted_builder_keys: dict | None = None,
    require_trusted_builder: bool = False,
) -> None:
    with database_server_lock(database):
        control = ControlPlane(
            database,
            authorizer=TokenAuthorizer.load(auth_config),
            github_webhook_secret=github_webhook_secret,
            trusted_validation_secrets=trusted_validation_secrets,
            provenance_secret=provenance_secret,
            trusted_validation_public_keys=trusted_validation_public_keys,
            provenance_private_key=provenance_private_key,
            provenance_public_key=provenance_public_key,
        )
        server = ThreadingHTTPServer(
            (host, port),
            make_handler(control),
        )
        try:
            server.serve_forever()
        finally:
            server.server_close()
