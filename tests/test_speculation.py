from production_os.speculation import SpeculationManager
from production_os.sqlite_backend import SQLiteBackend, SQLiteJobQueue


def test_speculative_first_success_wins(tmp_path):
    backend=SQLiteBackend(tmp_path/"db.sqlite")
    queue=SQLiteJobQueue(backend)
    manager=SpeculationManager(backend,queue)

    original=queue.enqueue({
        "handoff":{
            "repository":"o/a",
            "task":"Build",
            "constraints":{"speculative_safe":True},
        },
        "required_capabilities":["python"],
    })
    queue.claim_next("slow",capabilities=["python"])
    duplicate=manager.spawn(
        original["key"],
        target_worker="fast",
    )
    assert duplicate["assigned_worker"]=="fast"

    group=manager.group_for_job(duplicate["key"])
    assert group is not None
    assert manager.try_win(group,duplicate["key"]) is True
    losers=manager.cancel_losers(group,duplicate["key"])
    assert original["key"] in losers
    assert queue.get(original["key"])["status"]=="cancelled"
    assert manager.try_win(group,original["key"]) is False
