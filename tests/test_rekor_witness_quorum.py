import json

from production_os.signing import generate_keypair, sign_payload
from production_os.sqlite_backend import SQLiteBackend
from production_os.rekor_witness_quorum import (
    REKOR_WITNESS_SCHEMA,
    RekorWitnessClient,
    RekorWitnessObservationStore,
    collect_rekor_witness_quorum,
    evaluate_rekor_witness_quorum,
    load_rekor_witness_config,
)


def _signed_observation(
    witness_id,
    private_key,
    *,
    log_id="a" * 64,
    origin="rekor.example - 42",
    tree_size=17,
    root_hash="b" * 64,
):
    observation = {
        "schema_version": REKOR_WITNESS_SCHEMA,
        "witness_id": witness_id,
        "log_id": log_id,
        "origin": origin,
        "tree_size": tree_size,
        "root_hash": root_hash,
    }
    return {
        "observation": observation,
        "signature": sign_payload(private_key, observation),
    }


def test_quorum_accepts_two_matching_valid_witnesses_out_of_three():
    keypairs = [generate_keypair() for _ in range(3)]
    responses = [
        _signed_observation(f"w{i + 1}", private)
        for i, (private, _) in enumerate(keypairs)
    ]
    public_keys = {
        f"w{i + 1}": public
        for i, (_, public) in enumerate(keypairs)
    }

    result = evaluate_rekor_witness_quorum(
        responses[:2],
        public_keys=public_keys,
        threshold=2,
        expected_log_id="a" * 64,
        expected_origin="rekor.example - 42",
        expected_tree_size=17,
        expected_root_hash="b" * 64,
    )

    assert result["valid"] is True
    assert result["valid_witnesses"] == ["w1", "w2"]
    assert result["required"] == 2
    assert result["conflicting_witnesses"] == []


def test_quorum_rejects_invalid_signature_and_fails_below_threshold():
    private1, public1 = generate_keypair()
    private2, public2 = generate_keypair()
    forged_private, _ = generate_keypair()
    first = _signed_observation("w1", private1)
    second = _signed_observation("w2", private2)
    second["signature"] = sign_payload(
        forged_private,
        second["observation"],
    )

    result = evaluate_rekor_witness_quorum(
        [first, second],
        public_keys={"w1": public1, "w2": public2},
        threshold=2,
        expected_log_id="a" * 64,
        expected_origin="rekor.example - 42",
        expected_tree_size=17,
        expected_root_hash="b" * 64,
    )

    assert result["valid"] is False
    assert result["valid_witnesses"] == ["w1"]
    assert result["rejected_witnesses"] == ["w2"]
    assert result["reason"] == "witness quorum not reached"


def test_quorum_fails_closed_on_valid_same_size_conflicting_root():
    private1, public1 = generate_keypair()
    private2, public2 = generate_keypair()
    private3, public3 = generate_keypair()
    responses = [
        _signed_observation("w1", private1),
        _signed_observation("w2", private2),
        _signed_observation("w3", private3, root_hash="c" * 64),
    ]

    result = evaluate_rekor_witness_quorum(
        responses,
        public_keys={
            "w1": public1,
            "w2": public2,
            "w3": public3,
        },
        threshold=2,
        expected_log_id="a" * 64,
        expected_origin="rekor.example - 42",
        expected_tree_size=17,
        expected_root_hash="b" * 64,
    )

    assert result["valid"] is False
    assert result["valid_witnesses"] == ["w1", "w2"]
    assert result["conflicting_witnesses"] == ["w3"]
    assert result["reason"] == "conflicting Rekor witness observation"


def test_witness_client_posts_rekor_tree_request_and_returns_signed_observation(
    monkeypatch,
):
    private_key, _ = generate_keypair()
    signed = _signed_observation("w1", private_key)
    observed = {}

    class Response:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return json.dumps(signed).encode("utf-8")

    def fake_urlopen(request, timeout):
        observed["url"] = request.full_url
        observed["timeout"] = timeout
        observed["method"] = request.get_method()
        observed["body"] = json.loads(request.data)
        return Response()

    monkeypatch.setattr(
        "production_os.rekor_witness_quorum.urlopen",
        fake_urlopen,
    )

    result = RekorWitnessClient(
        "https://w1.example/observe",
        timeout_seconds=4.5,
    ).observe(
        log_id="a" * 64,
        origin="rekor.example - 42",
        tree_size=17,
        root_hash="b" * 64,
    )

    assert observed["url"] == "https://w1.example/observe"
    assert observed["method"] == "POST"
    assert observed["timeout"] == 4.5
    assert observed["body"] == {
        "schema_version": "production-os/rekor-witness-request/v1",
        "log_id": "a" * 64,
        "origin": "rekor.example - 42",
        "tree_size": 17,
        "root_hash": "b" * 64,
    }
    assert result == signed


def test_witness_observation_store_persists_signed_audit_record(tmp_path):
    private_key, _ = generate_keypair()
    response = _signed_observation("w1", private_key)
    store = RekorWitnessObservationStore(
        SQLiteBackend(tmp_path / "state.db")
    )

    stored = store.record(
        response=response,
        verdict="valid",
    )
    rows = store.list_for_tree(
        log_id="a" * 64,
        origin="rekor.example - 42",
        tree_size=17,
    )

    assert stored["witness_id"] == "w1"
    assert stored["verdict"] == "valid"
    assert len(rows) == 1
    assert rows[0]["root_hash"] == "b" * 64
    assert rows[0]["response"] == response


def test_load_witness_config_resolves_relative_public_key_paths(tmp_path):
    _, public1 = generate_keypair()
    _, public2 = generate_keypair()
    (tmp_path / "w1.pub.pem").write_text(public1, encoding="ascii")
    (tmp_path / "w2.pub.pem").write_text(public2, encoding="ascii")
    config_path = tmp_path / "witnesses.json"
    config_path.write_text(
        json.dumps(
            {
                "threshold": 2,
                "witnesses": [
                    {
                        "id": "w1",
                        "url": "https://w1.example/observe",
                        "public_key_path": "w1.pub.pem",
                    },
                    {
                        "id": "w2",
                        "url": "https://w2.example/observe",
                        "public_key_path": "w2.pub.pem",
                    },
                ],
            }
        ),
        encoding="utf-8",
    )

    config = load_rekor_witness_config(config_path)

    assert config["threshold"] == 2
    assert [item["id"] for item in config["witnesses"]] == ["w1", "w2"]
    assert config["witnesses"][0]["public_key"] == public1
    assert config["witnesses"][1]["public_key"] == public2


def test_collect_witness_quorum_queries_all_witnesses_and_persists_verdicts(
    tmp_path, monkeypatch
):
    private1, public1 = generate_keypair()
    private2, public2 = generate_keypair()
    signed = {
        "https://w1.example/observe": _signed_observation("w1", private1),
        "https://w2.example/observe": _signed_observation("w2", private2),
    }

    def fake_observe(self, **kwargs):
        assert kwargs == {
            "log_id": "a" * 64,
            "origin": "rekor.example - 42",
            "tree_size": 17,
            "root_hash": "b" * 64,
        }
        return signed[self.url]

    monkeypatch.setattr(RekorWitnessClient, "observe", fake_observe)
    store = RekorWitnessObservationStore(
        SQLiteBackend(tmp_path / "state.db")
    )
    config = {
        "threshold": 2,
        "witnesses": [
            {
                "id": "w1",
                "url": "https://w1.example/observe",
                "public_key": public1,
            },
            {
                "id": "w2",
                "url": "https://w2.example/observe",
                "public_key": public2,
            },
        ],
    }

    result = collect_rekor_witness_quorum(
        config,
        log_id="a" * 64,
        origin="rekor.example - 42",
        tree_size=17,
        root_hash="b" * 64,
        store=store,
    )

    assert result["valid"] is True
    assert result["valid_witnesses"] == ["w1", "w2"]
    rows = store.list_for_tree(
        log_id="a" * 64,
        origin="rekor.example - 42",
        tree_size=17,
    )
    assert [row["verdict"] for row in rows] == ["valid", "valid"]
