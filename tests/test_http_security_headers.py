import threading
import urllib.request
from http.server import ThreadingHTTPServer

from production_os.api_auth import TokenAuthorizer
from production_os.control_plane import ControlPlane, make_handler


SECURITY_HEADERS = {
    "Cache-Control": "no-store",
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
}


def _server(tmp_path):
    control = ControlPlane(
        str(tmp_path / "db.sqlite"),
        authorizer=TokenAuthorizer([]),
    )
    server = ThreadingHTTPServer(
        ("127.0.0.1", 0),
        make_handler(control),
    )
    thread = threading.Thread(
        target=server.serve_forever,
        daemon=True,
    )
    thread.start()
    return server


def _assert_security_headers(response):
    for name, expected in SECURITY_HEADERS.items():
        assert response.headers.get(name) == expected


def test_json_health_response_has_security_headers(tmp_path):
    server = _server(tmp_path)
    try:
        url = f"http://127.0.0.1:{server.server_port}/health"
        with urllib.request.urlopen(url, timeout=3) as response:
            assert response.status == 200
            assert response.headers.get("Content-Type") == (
                "application/json; charset=utf-8"
            )
            _assert_security_headers(response)
    finally:
        server.shutdown()
        server.server_close()


def test_dashboard_html_response_has_security_headers(tmp_path):
    server = _server(tmp_path)
    try:
        url = f"http://127.0.0.1:{server.server_port}/dashboard"
        with urllib.request.urlopen(url, timeout=3) as response:
            assert response.status == 200
            assert response.headers.get("Content-Type") == (
                "text/html; charset=utf-8"
            )
            _assert_security_headers(response)
    finally:
        server.shutdown()
        server.server_close()


def test_server_header_identifies_product_without_exposing_route_data(tmp_path):
    server = _server(tmp_path)
    try:
        url = f"http://127.0.0.1:{server.server_port}/healthz"
        with urllib.request.urlopen(url, timeout=3) as response:
            server_header = response.headers.get("Server", "")
            assert server_header.startswith("ProductionOS/")
            assert "127.0.0.1" not in server_header
            assert str(server.server_port) not in server_header
    finally:
        server.shutdown()
        server.server_close()
