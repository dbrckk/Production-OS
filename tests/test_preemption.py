from production_os.preemption import (
    choose_preemption_victim,
    confirm_checkpoint_and_release,
    request_preemption,
)
from production_os.runtime_state import RuntimeState
from production_os.workers import WorkerRegistry


def test_safe_preemption_requires_interruptible_and_priority_gap(tmp_path):
    state = RuntimeState(tmp_path/"state.json")
    workers = WorkerRegistry(tmp_path/"workers.json")
    workers.register("w1",["python"],1)
    workers.workers["w1"].active_tasks = 1
    workers.save()

    rec = state.get("o/a","low")
    rec.status = "running"
    rec.lease_owner = "w1"
    rec.interruptible = True
    rec.priority = 10
    state.save()

    decision = choose_preemption_victim(
        state,
        workers,
        required_capabilities=["python"],
        incoming_priority=50,
        minimum_priority_gap=20,
    )
    assert decision.should_preempt is True

    request_preemption(state,"o/a","low")
    paused = confirm_checkpoint_and_release(
        state,workers,"o/a","low","w1","checkpoint://abc"
    )
    assert paused["status"] == "paused"
    assert workers.workers["w1"].active_tasks == 0
