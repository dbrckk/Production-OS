from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


class _Handler(BaseHTTPRequestHandler):
    health_path: Path

    def do_GET(self) -> None:
        if self.path not in {"/health","/healthz","/"}:
            self.send_response(404)
            self.end_headers()
            return

        if not self.health_path.exists():
            payload = {"status":"unknown","reason":"health file not found"}
            body = json.dumps(payload).encode("utf-8")
            self.send_response(503)
        else:
            body = self.health_path.read_bytes()
            try:
                payload = json.loads(body.decode("utf-8"))
                code = 200 if payload.get("status") == "healthy" else 503
            except Exception:
                code = 503
            self.send_response(code)

        self.send_header("Content-Type","application/json; charset=utf-8")
        self.send_header("Content-Length",str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args) -> None:
        return


def serve_health(
    health_path: str | Path,
    *,
    host: str = "127.0.0.1",
    port: int = 8765,
) -> None:
    handler = type(
        "ProductionOSHealthHandler",
        (_Handler,),
        {"health_path":Path(health_path)},
    )
    server = ThreadingHTTPServer((host, port), handler)
    server.serve_forever()
