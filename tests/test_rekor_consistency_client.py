import json

from production_os.rekor_checkpoint_state import RekorV1ConsistencyClient


def test_consistency_client_calls_rekor_v1_proof_endpoint(monkeypatch):
    observed = {}

    class Response:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return json.dumps(
                {
                    "rootHash": "b" * 64,
                    "hashes": ["c" * 64],
                }
            ).encode("utf-8")

    def fake_urlopen(request, timeout):
        observed["url"] = request.full_url
        observed["method"] = request.get_method()
        observed["timeout"] = timeout
        return Response()

    monkeypatch.setattr(
        "production_os.rekor_checkpoint_state.urlopen",
        fake_urlopen,
    )

    client = RekorV1ConsistencyClient(
        "https://rekor.example/api/v1/log/entries",
        timeout_seconds=7.5,
    )
    result = client.fetch(first_size=10, last_size=20, tree_id="42")

    assert observed["method"] == "GET"
    assert observed["timeout"] == 7.5
    assert observed["url"].startswith(
        "https://rekor.example/api/v1/log/proof?"
    )
    assert "firstSize=10" in observed["url"]
    assert "lastSize=20" in observed["url"]
    assert "treeID=42" in observed["url"]
    assert result == {"rootHash": "b" * 64, "hashes": ["c" * 64]}
