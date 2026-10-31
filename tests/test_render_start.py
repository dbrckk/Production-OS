from pathlib import Path
import hashlib
import importlib.util
import json
import os
import stat
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
        self.assertEqual(entries["worker"]["name"], "github-actions-worker")
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
                "PRODUCTION_OS_WORKER_ID": "custom-actions-worker",
                "PORT": "9999",
                "RENDER_SERVICE_ID": "srv-dbj1hiuc6qcc73b7afvg",
                "PRODUCTION_OS_RUNTIME_DIR": td,
            },
            clear=True,
        ), patch.object(MODULE.os, "execvp") as execvp:
            # A leftover or attacker-created symlink must never cause the
            # startup to overwrite a different file with credential hashes.
            target = Path(td) / "unrelated-data.txt"
            target.write_text("must-remain-unchanged", encoding="utf-8")
            auth_path = Path(td) / "auth.json"
            auth_path.symlink_to(target)
            MODULE.main()

            self.assertEqual(
                target.read_text(encoding="utf-8"), "must-remain-unchanged"
            )
            self.assertFalse(auth_path.is_symlink())
            self.assertEqual(stat.S_IMODE(auth_path.stat().st_mode), 0o600)
            self.assertEqual(stat.S_IMODE(Path(td).stat().st_mode), 0o700)
            self.assertEqual(list(Path(td).glob(".auth-*.tmp")), [])

            execvp.assert_called_once()
            argv = execvp.call_args.args[1]
            self.assertEqual(argv[0:2], ["production-os", "control-plane"])
            self.assertNotIn("postgresql://example/db", argv)
            self.assertEqual(
                argv[argv.index("--database-env") + 1],
                "DATABASE_URL",
            )
            self.assertNotIn("--database", argv)
            self.assertIn("9999", argv)
            auth_path = Path(td) / "auth.json"
            payload = json.loads(auth_path.read_text(encoding="utf-8"))
            self.assertEqual(
                {entry["role"] for entry in payload["tokens"]},
                {"worker", "operator"},
            )
            entries = {entry["role"]: entry for entry in payload["tokens"]}
            self.assertEqual(entries["worker"]["name"], "custom-actions-worker")

    def test_invalid_port_fails_closed(self):
        with tempfile.TemporaryDirectory() as td, patch.dict(
            os.environ,
            {
                "DATABASE_URL": "postgresql://example/db",
                "PRODUCTION_OS_WORKER_TOKEN": "worker-secret",
                "PRODUCTION_OS_OPERATOR_TOKEN": "operator-secret",
                "PRODUCTION_OS_RUNTIME_DIR": str(Path(td) / "redirect"),
                "PORT": "8787",
            },
            clear=True,
        ), patch.object(MODULE.os, "execvp") as execvp:
            redirect = Path(td) / "redirect"
            redirect.symlink_to(Path(td), target_is_directory=True)
            with self.assertRaisesRegex(SystemExit, "must not be a symlink"):
                MODULE.main()
            execvp.assert_not_called()
            self.assertFalse((Path(td) / "auth.json").exists())

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


        # The free Render service must fail closed before creating any auth
        # file if an ephemeral SQLite path or shared operator token is set.
        with tempfile.TemporaryDirectory() as td:
            base = {
                "DATABASE_URL": "postgresql://example/db",
                "PRODUCTION_OS_WORKER_TOKEN": "worker-secret",
                "PRODUCTION_OS_OPERATOR_TOKEN": "operator-secret",
                "PRODUCTION_OS_RUNTIME_DIR": td,
            }
            for change, expected in (
                ({"DATABASE_URL": "/tmp/production.db"}, "PostgreSQL connection URL"),
                ({"DATABASE_URL": "sqlite:///tmp/production.db"}, "PostgreSQL connection URL"),
                ({"DATABASE_URL": "postgresql:///production_os"}, "explicit host and database"),
                ({"DATABASE_URL": "postgresql://user@/production_os"}, "explicit host and database"),
                ({"DATABASE_URL": "postgresql://example/"}, "explicit host and database"),
                ({"DATABASE_URL": "postgresql://example"}, "explicit host and database"),
                ({"DATABASE_URL": "postgresql://example:invalid/production_os"}, "explicit host and database"),
                ({"DATABASE_URL": "postgresql://example:0/production_os"}, "explicit host and database"),
                ({"DATABASE_URL": "postgresql://[invalid/production_os"}, "explicit host and database"),
                ({"DATABASE_URL": "postgresql://example/production_os#fragment"}, "explicit host and database"),
                ({"PRODUCTION_OS_OPERATOR_TOKEN": "worker-secret"}, "must be distinct"),
                ({"RENDER_SERVICE_ID": "srv-dancka740ujc73bgdddg"}, "retired Render"),
                ({"RENDER_SERVICE_ID": "srv-dancjugae00c73earbe0"}, "retired Render"),
                ({"RENDER_SERVICE_ID": "srv-dancfm3tqb8s73bek920"}, "retired Render"),
            ):
                with self.subTest(change=change), patch.dict(
                    os.environ, {**base, **change}, clear=True
                ), patch.object(MODULE.os, "execvp") as execvp:
                    with self.assertRaisesRegex(SystemExit, expected):
                        MODULE.main()
                    execvp.assert_not_called()
                    self.assertFalse((Path(td) / "auth.json").exists())


if __name__ == "__main__":
    unittest.main()
