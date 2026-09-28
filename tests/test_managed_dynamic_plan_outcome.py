from production_os.managed_projects import _outcome_from_workflow


def test_managed_outcome_exposes_dynamic_model_plan_summary():
    outcome = _outcome_from_workflow({
        "status":"running",
        "updated_at":"2026-09-27T19:00:00+00:00",
        "artifacts":[],
        "tasks":[
            {
                "task_id":"planner.agent.backend",
                "payload":{
                    "dynamic_agent_child":True,
                    "dynamic_agent_plan_source":"model",
                },
                "result":{"summary":"backend"},
            },
            {
                "task_id":"planner.agent.tests",
                "payload":{
                    "dynamic_agent_child":True,
                    "dynamic_agent_plan_source":"model",
                },
                "result":{"summary":"tests"},
            },
        ],
    })

    assert outcome["dynamic_plan"] == {
        "source":"model",
        "child_agent_count":2,
        "task_ids":[
            "planner.agent.backend",
            "planner.agent.tests",
        ],
    }


def test_managed_outcome_exposes_fallback_plan_summary():
    outcome = _outcome_from_workflow({
        "status":"running",
        "updated_at":"2026-09-27T19:00:00+00:00",
        "artifacts":[],
        "tasks":[
            {
                "task_id":"planner.agent.code",
                "payload":{
                    "dynamic_agent_child":True,
                    "dynamic_agent_plan_source":"fallback",
                },
                "result":{"summary":"code"},
            },
            {
                "task_id":"planner.agent.tests",
                "payload":{
                    "dynamic_agent_child":True,
                    "dynamic_agent_plan_source":"fallback",
                },
                "result":{"summary":"tests"},
            },
        ],
    })

    assert outcome["dynamic_plan"]["source"] == "fallback"
    assert outcome["dynamic_plan"]["child_agent_count"] == 2


def test_managed_outcome_has_no_dynamic_plan_for_legacy_workflow():
    outcome = _outcome_from_workflow({
        "status":"succeeded",
        "updated_at":"2026-09-27T19:00:00+00:00",
        "artifacts":[],
        "tasks":[
            {
                "task_id":"implementation",
                "payload":{},
                "result":{"summary":"done"},
            },
        ],
    })

    assert outcome["dynamic_plan"] is None
