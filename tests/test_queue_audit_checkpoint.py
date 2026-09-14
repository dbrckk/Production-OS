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


def test_signed_audit_checkpoint(tmp_path):
    journal=ExecutionJournal(tmp_path/"audit.jsonl")
    journal.append({"event":"x"})
    checkpoint=tmp_path/"checkpoint.json"
    create_audit_checkpoint(journal.path,checkpoint,secret="secret")
    assert verify_audit_checkpoint(checkpoint,secret="secret")["valid"] is True
