from production_os.signing import generate_keypair, sign_payload
from production_os.rekor_witness_quorum import (
    REKOR_WITNESS_SCHEMA,
    evaluate_rekor_witness_quorum,
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
