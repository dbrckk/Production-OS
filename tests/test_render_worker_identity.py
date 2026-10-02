from pathlib import Path
import importlib.util
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "render-start.py"
SPEC = importlib.util.spec_from_file_location("render_start_identity", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class RenderWorkerIdentityTests(unittest.TestCase):
    def test_render_worker_identity_matches_actions_worker(self):
        payload = MODULE._auth_payload("worker-value", "operator-value")
        worker = next(item for item in payload["tokens"] if item["role"] == "worker")
        self.assertEqual(worker["name"], "github-actions-worker")


if __name__ == "__main__":
    unittest.main()
