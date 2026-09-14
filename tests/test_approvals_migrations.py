import json

from production_os.approvals import ApprovalStore
from production_os.migrations import migrate_state_file


def test_approval_store(tmp_path):
    store=ApprovalStore(tmp_path/"approvals.json")
    item=store.set("task-key",approved=True,approved_by="human",reason="ok")
    assert item.approved is True
    assert store.is_approved("task-key") is True


def test_runtime_state_v1_migration(tmp_path):
    path=tmp_path/"state.json"
    path.write_text(json.dumps({
        "schema_version":"production-os/runtime-state/v1",
        "records":{}
    }),encoding="utf-8")
    result=migrate_state_file(path)
    assert result["migrated"] is True
    assert json.loads(path.read_text())["schema_version"].endswith("/v2")
