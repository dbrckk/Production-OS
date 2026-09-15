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
        self.authorizer = authorizer or TokenAuthorizer([])
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
                # Consume at most one byte beyond the supported limit. This
                # keeps the rejection bounded while allowing ordinary clients
                # that sent max_body + 1 bytes to receive the 413 response.
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
