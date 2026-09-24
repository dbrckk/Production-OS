from production_os.dashboard_playbooks import derive_incident_playbook


def test_queue_without_worker_playbook_is_truthful_about_kick_mode():
    incident = {
        "id":"i1",
        "code":"queue_without_worker",
        "target_type":"control-plane",
        "target_id":"global",
    }
    immediate = derive_incident_playbook(
        incident,
        actions_kick_mode="immediate",
    )
    fallback = derive_incident_playbook(
        incident,
        actions_kick_mode="scheduled_fallback",
    )
    assert immediate["suggestions"][0]["action"] == "kick"
    assert immediate["suggestions"][0]["availability"] == "available"
    assert fallback["suggestions"][0]["availability"] == "fallback"
    assert immediate["suggestions"][0]["interrupting"] is False


def test_stale_worker_recovery_is_suggested_only_for_server_recoverable_jobs():
    incident = {
        "id":"i2",
        "code":"stale_busy_workers",
        "target_type":"worker",
        "target_id":"worker-a",
    }
    result = derive_incident_playbook(
        incident,
        recoverable_jobs=[{"key":"job-expired"}],
    )
    actions = [(x["action"], x["job_key"]) for x in result["suggestions"]]
    assert ("inspect-worker", None) in actions
    assert ("recover-stuck", "job-expired") in actions


def test_stale_job_cancel_requires_active_owned_job():
    incident = {
        "id":"i3",
        "code":"stale_running_executions",
        "target_type":"job",
        "target_id":"job-a",
    }
    active = derive_incident_playbook(
        incident,
        job={"key":"job-a","status":"acked","claimed_by":"worker-a"},
    )
    cancel = next(x for x in active["suggestions"] if x["action"] == "cancel-current")
    assert cancel["availability"] == "available"
    assert cancel["worker_id"] == "worker-a"
    assert cancel["interrupting"] is True

    terminal = derive_incident_playbook(
        incident,
        job={"key":"job-a","status":"completed","claimed_by":"worker-a"},
    )
    cancel = next(x for x in terminal["suggestions"] if x["action"] == "cancel-current")
    assert cancel["availability"] == "unavailable"


def test_playbook_derivation_has_no_execution_side_effect_contract():
    result = derive_incident_playbook({
        "id":"i4",
        "code":"unknown",
        "target_type":"control-plane",
        "target_id":"global",
    })
    assert result["suggestions"] == []


def test_resolved_incident_has_no_remediation_actions():
    result = derive_incident_playbook({
        "id":"i5",
        "code":"queue_without_worker",
        "target_type":"control-plane",
        "target_id":"global",
        "status":"resolved",
    }, actions_kick_mode="immediate")
    assert result["suggestions"] == []
