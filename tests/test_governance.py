from production_os.governance import apply_governance
from production_os.policy import PolicySet
from production_os.quarantine import QuarantineStore
from production_os.runtime_state import RuntimeState


def test_auto_quarantine_after_failures(tmp_path):
    runtime=RuntimeState(tmp_path/"runtime.json")
    rec=runtime.get("o/a","task")
    rec.consecutive_failures=3
    rec.status="failed"
    runtime.save()

    quarantine=QuarantineStore(tmp_path/"quarantine.json")
    policies=PolicySet({
        "repositories":[
            {"match":"o/a","auto_quarantine_after_failures":3}
        ]
    })
    actions=apply_governance(runtime,policies,quarantine)
    assert actions
    assert quarantine.active("o/a")[0] is True
