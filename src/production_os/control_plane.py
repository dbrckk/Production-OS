from __future__ import annotations

import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from .api_auth import Principal, TokenAuthorizer
from .sqlite_backend import (
    SQLiteBackend,
    SQLiteJobQueue,
    SQLiteWorkerRegistry,
)


class ControlPlane:
    def __init__(
        self,
        database: str,
        *,
        authorizer: TokenAuthorizer,
    ):
        self.backend = SQLiteBackend(database)
        self.queue = SQLiteJobQueue(self.backend)
        self.workers = SQLiteWorkerRegistry(self.backend)
        self.authorizer = authorizer


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
  const [stats,workers,events]=await Promise.all([
   api('/v1/stats'),api('/v1/workers'),api('/v1/events?limit=30')
  ]);
  document.getElementById('stats').innerHTML=Object.entries(stats.jobs||{}).map(
   ([k,v])=>'<div class="card"><b>'+k+'</b><div>'+v+'</div></div>'
  ).join('');
  document.getElementById('workers').textContent=JSON.stringify(workers.workers,null,2);
  document.getElementById('events').textContent=JSON.stringify(events.events,null,2);
 }catch(e){document.getElementById('events').textContent=String(e)}
}
</script>
</body>
</html>"""


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
            self.end_headers()
            self.wfile.write(body)

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
            self.end_headers()
            self.wfile.write(body)

        def _read_json(self) -> dict:
            raw_length = self.headers.get("Content-Length", "0")
            try:
                length = int(raw_length)
            except ValueError as exc:
                raise ValueError("invalid Content-Length") from exc
            if length < 0 or length > 1024 * 1024:
                raise ValueError("request body too large")
            if length == 0:
                return {}
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
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
                self._send(
                    HTTPStatus.OK,
                    {
                        "jobs":{row["status"]:row["count"] for row in rows},
                        "online_workers":workers,
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
            try:
                body = self._read_json()
            except (ValueError, json.JSONDecodeError) as exc:
                self._send(
                    HTTPStatus.BAD_REQUEST,
                    {"error":str(exc)},
                )
                return

            try:
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
                    self._send(HTTPStatus.OK, {"worker":worker.to_dict()})
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
                    job = control.queue.claim_next(
                        str(body["worker_id"]),
                        capabilities=[
                            str(x)
                            for x in body.get("capabilities", [])
                        ],
                        ack_timeout_seconds=int(
                            body.get("ack_timeout_seconds", 120)
                        ),
                    )
                    if job is None:
                        self._send(
                            HTTPStatus.NO_CONTENT,
                            {},
                        )
                        return
                    self._send(HTTPStatus.OK, {"job":job})
                    return

                if parsed.path == "/v1/jobs/ack":
                    principal = self._require("worker")
                    if principal is None:
                        return
                    job = control.queue.ack(
                        str(body["key"]),
                        str(body["worker_id"]),
                    )
                    self._send(HTTPStatus.OK, {"job":job})
                    return

                if parsed.path == "/v1/jobs/complete":
                    principal = self._require("worker")
                    if principal is None:
                        return
                    job = control.queue.complete(
                        str(body["key"]),
                        str(body["worker_id"]),
                    )
                    self._send(HTTPStatus.OK, {"job":job})
                    return

                if parsed.path == "/v1/jobs/fail":
                    principal = self._require("worker")
                    if principal is None:
                        return
                    job = control.queue.fail(
                        str(body["key"]),
                        str(body["worker_id"]),
                        str(body.get("reason", "worker failure")),
                    )
                    self._send(HTTPStatus.OK, {"job":job})
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
) -> None:
    control = ControlPlane(
        database,
        authorizer=TokenAuthorizer.load(auth_config),
    )
    server = ThreadingHTTPServer(
        (host, port),
        make_handler(control),
    )
    server.serve_forever()
