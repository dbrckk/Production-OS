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



def test_compact_archive_preserves_existing_entry_and_source(tmp_path):
    import json

    claims = ClaimStore(tmp_path / "claims.json")
    claims.claim(key="k1", worker_id="w", repository="o/a", task="t")
    claims.ack("k1", "w")
    claims.complete("k1", "w")
    queue = tmp_path / "queue"
    archive = tmp_path / "archive"
    queue.mkdir()
    archive.mkdir()
    source = queue / "k1.w.json"
    source.write_text('{"idempotency_key":"k1","data":"new"}', encoding="utf-8")
    target = archive / source.name
    target.write_text('{"data":"original archive"}', encoding="utf-8")

    actions = compact_queue(queue_dir=queue, archive_dir=archive, claims=claims)
    assert actions[0]["action"] == "archive-conflict"
    assert source.exists()
    assert json.loads(target.read_text(encoding="utf-8")) == {
        "data": "original archive",
    }
    assert not list(archive.glob("*.tmp"))

    target.unlink()
    actions = compact_queue(queue_dir=queue, archive_dir=archive, claims=claims)
    assert actions[0]["action"] == "archive-completed"
    assert not source.exists()
    assert json.loads(target.read_text(encoding="utf-8"))["data"] == "new"


def test_compact_archive_rejects_racing_target_and_malformed_rows(tmp_path, monkeypatch):
    from production_os import queue_maintenance

    claims = ClaimStore(tmp_path / "claims.json")
    claims.claim(key="k1", worker_id="w", repository="o/a", task="t")
    claims.ack("k1", "w")
    claims.complete("k1", "w")
    queue = tmp_path / "queue"
    archive = tmp_path / "archive"
    queue.mkdir()
    archive.mkdir()
    source = queue / "k1.w.json"
    source.write_text('{"idempotency_key":"k1"}', encoding="utf-8")
    (queue / "malformed.json").write_text('["unexpected"]', encoding="utf-8")

    original_link = queue_maintenance.os.link

    def collision_after_preflight(temp, target, **kwargs):
        target.write_text('{"winner":"another worker"}', encoding="utf-8")
        return original_link(temp, target, **kwargs)

    monkeypatch.setattr(queue_maintenance.os, "link", collision_after_preflight)
    actions = compact_queue(queue_dir=queue, archive_dir=archive, claims=claims)
    assert len(actions) == 1
    assert actions[0]["action"] == "archive-conflict"
    assert source.exists()
    assert (queue / "malformed.json").exists()
    assert (archive / source.name).read_text(encoding="utf-8") == (
        '{"winner":"another worker"}'
    )
    assert not list(archive.glob("*.tmp"))


def test_compact_skips_symlinked_queue_rows(tmp_path):
    claims = ClaimStore(tmp_path / "claims.json")
    claims.claim(key="k1", worker_id="w", repository="o/a", task="t")
    claims.ack("k1", "w")
    claims.complete("k1", "w")
    queue = tmp_path / "queue"
    queue.mkdir()
    outside = tmp_path / "outside.json"
    outside.write_text('{"idempotency_key":"k1"}', encoding="utf-8")
    (queue / "link.json").symlink_to(outside)
    assert compact_queue(queue_dir=queue, claims=claims) == []
    assert outside.exists()
    assert (queue / "link.json").is_symlink()

    # The compactor must not even open the symlinked path. Its target can
    # contain sensitive data and must remain unread by this queue operation.
    from pathlib import Path
    from unittest.mock import patch

    original_read_text = Path.read_text

    def reject_link_reads(path, *args, **kwargs):
        if path == queue / "link.json":
            raise AssertionError("symlink was read before validation")
        return original_read_text(path, *args, **kwargs)

    with patch.object(Path, "read_text", reject_link_reads):
        assert compact_queue(queue_dir=queue, claims=claims) == []



def test_compact_queue_rejects_symlink_swapped_during_open(tmp_path, monkeypatch):
    import os
    from production_os import queue_maintenance

    claims = ClaimStore(tmp_path / "claims.json")
    claims.claim(key="k1", worker_id="w", repository="o/a", task="t")
    claims.ack("k1", "w")
    claims.complete("k1", "w")

    queue = tmp_path / "queue"
    queue.mkdir()
    source = queue / "job.json"
    source.write_text('{"idempotency_key":"k1"}', encoding="utf-8")
    outside = tmp_path / "private.json"
    outside.write_text('{"idempotency_key":"k1"}', encoding="utf-8")
    original_open = queue_maintenance.os.open

    def swap_source(path, flags, *args, **kwargs):
        if os.fspath(path) == os.fspath(source):
            source.unlink()
            source.symlink_to(outside)
        return original_open(path, flags, *args, **kwargs)

    monkeypatch.setattr(queue_maintenance.os, "open", swap_source)
    assert compact_queue(queue_dir=queue, claims=claims) == []
    assert source.is_symlink()
    assert outside.exists()


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
        "boolean": {"idempotency_key": "safe3", "delivery_attempt": True},
        "fractional": {"idempotency_key": "safe4", "delivery_attempt": 1.75},
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


def test_retry_dead_letter_skips_symlinked_external_payload(tmp_path):
    dead = tmp_path / "dead"
    queue = tmp_path / "queue"
    dead.mkdir()
    outside = tmp_path / "external.json"
    outside.write_text(
        '{"idempotency_key":"external-job","delivery_attempt":0}',
        encoding="utf-8",
    )
    link = dead / "external.json"
    link.symlink_to(outside)

    actions = retry_dead_letters(dead_letter_dir=dead, queue_dir=queue)
    assert actions == [{
        "key": "",
        "action": "dead-letter-unsafe-source",
        "path": str(link),
    }]
    assert link.is_symlink()
    assert outside.exists()
    assert not list(queue.iterdir())


def test_retry_dead_letter_does_not_follow_symlink_replacement_race(tmp_path, monkeypatch):
    import os
    from production_os import queue_maintenance

    dead = tmp_path / "dead"
    queue = tmp_path / "queue"
    dead.mkdir()
    source = dead / "job.json"
    source.write_text('{"idempotency_key":"job"}', encoding="utf-8")
    outside = tmp_path / "outside.json"
    outside.write_text('{"idempotency_key":"outside"}', encoding="utf-8")
    original_open = queue_maintenance.os.open

    def replace_before_open(path, flags, *args, **kwargs):
        if os.fspath(path) == os.fspath(source):
            source.unlink()
            source.symlink_to(outside)
        return original_open(path, flags, *args, **kwargs)

    monkeypatch.setattr(queue_maintenance.os, "open", replace_before_open)
    actions = retry_dead_letters(dead_letter_dir=dead, queue_dir=queue)
    assert actions[0]["action"] == "dead-letter-unsafe-source"
    assert source.is_symlink()
    assert outside.exists()
    assert not list(queue.iterdir())


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
