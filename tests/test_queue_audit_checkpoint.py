from production_os.audit_checkpoint import (
    create_audit_checkpoint,
    verify_audit_checkpoint,
)
from production_os.claims import ClaimStore
from production_os.journal import ExecutionJournal
from production_os.queue_maintenance import compact_queue, retry_dead_letters


def test_compact_completed_queue(tmp_path):
    claims=ClaimStore(tmp_path/"claims.json")
    claim=claims.claim(key="k1",worker_id="w",repository="o/a",task="t")
    claims.ack("k1","w")
    claims.complete("k1","w")

    queue=tmp_path/"queue"
    queue.mkdir()
    (queue/"k1.w.json").write_text(
        '{"idempotency_key":"k1"}',
        encoding="utf-8",
    )
    rows=compact_queue(queue_dir=queue,claims=claims)
    assert rows[0]["action"]=="delete-completed"


def test_retry_dead_letter(tmp_path):
    dead=tmp_path/"dead"
    queue=tmp_path/"queue"
    dead.mkdir()
    (dead/"k1.json").write_text(
        '{"idempotency_key":"k1","worker_id":"old"}',
        encoding="utf-8",
    )
    rows=retry_dead_letters(
        dead_letter_dir=dead,
        queue_dir=queue,
        max_attempts=2,
    )
    assert rows[0]["action"]=="requeued"


def test_retry_dead_letter_rejects_unsafe_keys_and_invalid_attempts(tmp_path):
    import json

    dead = tmp_path / "dead"
    queue = tmp_path / "queue"
    dead.mkdir()
    cases = {
        "traversal": {"idempotency_key": "../outside"},
        "absolute": {"idempotency_key": "/tmp/unsafe"},
        "invalid": {"idempotency_key": "safe", "delivery_attempt": "not-a-number"},
        "negative": {"idempotency_key": "safe2", "delivery_attempt": -3},
        "nondict": ["unexpected", "payload"],
    }
    for name, payload in cases.items():
        (dead / f"{name}.json").write_text(json.dumps(payload), encoding="utf-8")

    rows = retry_dead_letters(dead_letter_dir=dead, queue_dir=queue)
    assert len(list(dead.glob("*.json"))) == len(cases)
    assert not list(queue.iterdir())
    assert {row["action"] for row in rows} == {
        "dead-letter-invalid-key", "dead-letter-invalid-attempt",
    }
    assert not (tmp_path / "outside.retry1.json").exists()


def test_retry_dead_letter_preserves_existing_queue_targets(tmp_path):
    import json

    dead = tmp_path / "dead"
    queue = tmp_path / "queue"
    dead.mkdir()
    queue.mkdir()
    source = dead / "k1.json"
    source.write_text(json.dumps({"idempotency_key": "k1"}), encoding="utf-8")
    target = queue / "k1.retry1.json"
    target.write_text('{"existing":"do not overwrite"}', encoding="utf-8")

    rows = retry_dead_letters(dead_letter_dir=dead, queue_dir=queue)
    assert rows[0]["action"] == "dead-letter-queue-conflict"
    assert json.loads(target.read_text(encoding="utf-8")) == {
        "existing": "do not overwrite",
    }
    assert source.exists()

    target.unlink()
    outside = tmp_path / "outside.json"
    outside.write_text('{"intact":true}', encoding="utf-8")
    target.symlink_to(outside)
    rows = retry_dead_letters(dead_letter_dir=dead, queue_dir=queue)
    assert rows[0]["action"] == "dead-letter-queue-conflict"
    assert outside.read_text(encoding="utf-8") == '{"intact":true}'
    assert source.exists()


def test_dead_letter_retry_atomic_publication_rejects_racing_target(tmp_path, monkeypatch):
    import json
    from production_os import queue_maintenance

    dead = tmp_path / "dead"
    queue = tmp_path / "queue"
    dead.mkdir()
    (dead / "one.json").write_text(
        '{"idempotency_key":"one"}', encoding="utf-8",
    )
    real_link = queue_maintenance.os.link

    def concurrent_publish(source, target, **kwargs):
        # Simulate a second publisher winning after the preflight check.
        target.write_text('{"another":"worker"}', encoding="utf-8")
        return real_link(source, target, **kwargs)

    monkeypatch.setattr(queue_maintenance.os, "link", concurrent_publish)
    rows = retry_dead_letters(dead_letter_dir=dead, queue_dir=queue)
    assert rows[0]["action"] == "dead-letter-queue-conflict"
    assert json.loads((queue / "one.retry1.json").read_text()) == {
        "another": "worker",
    }
    assert (dead / "one.json").exists()
    assert not list(queue.glob("*.tmp"))


def test_signed_audit_checkpoint(tmp_path):
    journal=ExecutionJournal(tmp_path/"audit.jsonl")
    journal.append({"event":"x"})
    checkpoint=tmp_path/"checkpoint.json"
    create_audit_checkpoint(journal.path,checkpoint,secret="secret")
    assert verify_audit_checkpoint(checkpoint,secret="secret")["valid"] is True
