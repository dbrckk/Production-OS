from __future__ import annotations

import json
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
        authorizer: TokenAuthorizer,
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
        self.queue = job_queue_for(self.backend)
        self.workers = worker_registry_for(self.backend)
        self.workflows = WorkflowEngine(self.backend, self.queue)
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
        self.authorizer = authorizer
        self.github_webhook_secret = github_webhook_secret
        self.webhook_deliveries = WebhookDeliveryStore(self.backend)


def _json_bytes(payload: dict | list) -> bytes:
    return json.dumps(
        payload,
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")


DASHBOARD_HTML = """<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Production-OS</title>
<style>
body{font-family:system-ui,sans-serif;max-width:1100px;margin:24px auto;padding:0 16px}
input,button{font:inherit;padding:8px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px}
.card{border:1px solid #ddd;border-radius:10px;padding:14px}
pre{white-space:pre-wrap;overflow:auto}
</style>
</head>
<body>
<h1>Production-OS Control Plane</h1>
<p><input id="token" type="password" placeholder="Bearer token"> <button onclick="refresh()">Refresh</button></p>
<div id="stats" class="grid"></div>
<h2>Workflows</h2><pre id="workflows"></pre>
<h2>Workers</h2><pre id="workers"></pre>
<h2>Recent events</h2><pre id="events"></pre>
<script>
async function api(path){
 const token=document.getElementById('token').value;
 const r=await fetch(path,{headers:{Authorization:'Bearer '+token}});
 if(!r.ok) throw new Error(await r.text());
 return await r.json();
}
async function refresh(){
 try{
  const [stats,workflows,workers,events]=await Promise.all([
   api('/v1/stats'),api('/v1/workflows'),api('/v1/workers'),
   api('/v1/events?limit=30')
  ]);
  document.getElementById('stats').innerHTML=Object.entries(stats.jobs||{}).map(
   ([k,v])=>'<div class="card"><b>'+k+'</b><div>'+v+'</div></div>'
  ).join('');
  document.getElementById('workflows').textContent=JSON.stringify(workflows.workflows,null,2);
  document.getElementById('workers').textContent=JSON.stringify(workers.workers,null,2);
  document.getElementById('events').textContent=JSON.stringify(events.events,null,2);
 }catch(e){document.getElementById('events').textContent=String(e)}
}
</script>
</body>
</html>"""


class RequestBodyTooLarge(ValueError):
    pass


def make_handler(control: ControlPlane):
    class Handler(BaseHTTPRequestHandler):
        server_version = "ProductionOS/0.8"

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
        ) -> None:
            body = _json_bytes(payload)
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
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

        def _read_body(self) -> bytes:
            raw_length = self.headers.get("Content-Length", "0")
            try:
                length = int(raw_length)
            except ValueError as exc:
                raise ValueError("invalid Content-Length") from exc
            if length < 0:
                raise ValueError("invalid Content-Length")
            if length > 1024 * 1024:
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
                raise ValueError("JSON body must be an object")
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

            if parsed.path in {"/", "/health", "/healthz"}:
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

            if parsed.path == "/v1/workers":
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
                    worker = control.workers.register(
                        str(body["worker_id"]),
                        [str(x) for x in body.get("capabilities", [])],
                        int(body.get("max_concurrency", 1)),
                    )
                    self._send(HTTPStatus.OK, {"worker":worker.to_dict()})
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
                    self._send(
                        HTTPStatus.OK,
                        {
                            "worker":worker.to_dict(),
                            "stale_job_keys":stale_job_keys,
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

                    worker_id = str(body["worker_id"])
                    capabilities = [
                        str(x) for x in body.get("capabilities", [])
                    ]

                    compatible = []
                    for queued in control.queue.peek_candidates(
                        worker_id=worker_id,
                        limit=100,
                    ):
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
                    job = control.queue.ack(
                        key,
                        str(body["worker_id"]),
                    )
                    self._send(HTTPStatus.OK, {"job":job})
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
    server.serve_forever()
