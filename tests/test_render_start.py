from pathlib import Path
import hashlib
import importlib.util
import json
import os
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "render-start.py"
SPEC = importlib.util.spec_from_file_location("render_start", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class RenderStartTests(unittest.TestCase):
    def test_auth_payload_hashes_tokens_without_storing_plaintext(self):
        payload = MODULE._auth_payload("worker-secret", "operator-secret")
        rendered = json.dumps(payload)

        self.assertNotIn("worker-secret", rendered)
        self.assertNotIn("operator-secret", rendered)
        entries = {entry["role"]: entry for entry in payload["tokens"]}
        self.assertEqual(
            entries["worker"]["sha256"],
            hashlib.sha256(b"worker-secret").hexdigest(),
        )
        self.assertEqual(
            entries["operator"]["sha256"],
            hashlib.sha256(b"operator-secret").hexdigest(),
        )

    def test_main_builds_control_plane_command_from_environment(self):
        with tempfile.TemporaryDirectory() as td, patch.dict(
            os.environ,
            {
                "DATABASE_URL": "postgresql://example/db",
                "PRODUCTION_OS_WORKER_TOKEN": "worker-secret",
                "PRODUCTION_OS_OPERATOR_TOKEN": "operator-secret",
                "PORT": "9999",
                "PRODUCTION_OS_RUNTIME_DIR": td,
            },
            clear=True,
        ), patch.object(MODULE.os, "execvp") as execvp:
            MODULE.main()

            execvp.assert_called_once()
            argv = execvp.call_args.args[1]
            self.assertEqual(argv[0:2], ["production-os", "control-plane"])
            self.assertIn("postgresql://example/db", argv)
            self.assertIn("9999", argv)
            auth_path = Path(td) / "auth.json"
            payload = json.loads(auth_path.read_text(encoding="utf-8"))
            self.assertEqual(
                {entry["role"] for entry in payload["tokens"]},
                {"worker", "operator"},
            )

    def test_invalid_port_fails_closed(self):
        with patch.dict(
            os.environ,
            {
                "DATABASE_URL": "postgresql://example/db",
                "PRODUCTION_OS_WORKER_TOKEN": "worker-secret",
                "PRODUCTION_OS_OPERATOR_TOKEN": "operator-secret",
                "PORT": "not-a-port",
            },
            clear=True,
        ):
            with self.assertRaises(SystemExit):
                MODULE.main()


if __name__ == "__main__":
    unittest.main()
