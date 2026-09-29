import pytest

from production_os.agent_plan import PLAN_SCHEMA, validate_agent_plan


def test_agent_plan_accepts_bounded_ordered_dependency_graph():
    tasks = validate_agent_plan(
        {
            "schema_version":PLAN_SCHEMA,
            "tasks":[
                {
                    "task_id":"backend",
                    "title":"Implement backend",
                    "instruction":"Implement the backend change.",
                    "token_budget":300,
                    "preferred_capabilities":["code-implementation"],
                    "estimated_minutes":30,
                },
                {
                    "task_id":"tests",
                    "title":"Add tests",
                    "instruction":"Add regression tests.",
                    "token_budget":200,
                    "preferred_capabilities":["test-debug"],
                    "dependencies":["backend"],
                    "estimated_minutes":20,
                },
            ],
        },
        available_token_budget=500,
        max_agents=4,
    )

    assert [task.task_id for task in tasks] == ["backend", "tests"]
    assert tasks[1].dependencies == ("backend",)
    assert sum(task.token_budget for task in tasks) == 500


def test_agent_plan_rejects_budget_overflow():
    with pytest.raises(ValueError, match="exceeds available token budget"):
        validate_agent_plan(
            {
                "schema_version":PLAN_SCHEMA,
                "tasks":[
                    {
                        "task_id":"one",
                        "title":"One",
                        "instruction":"Do one.",
                        "token_budget":6,
                    },
                    {
                        "task_id":"two",
                        "title":"Two",
                        "instruction":"Do two.",
                        "token_budget":5,
                    },
                ],
            },
            available_token_budget=10,
        )


def test_agent_plan_rejects_too_many_agents():
    with pytest.raises(ValueError, match="exceeds max_agents"):
        validate_agent_plan(
            {
                "schema_version":PLAN_SCHEMA,
                "tasks":[
                    {
                        "task_id":f"task-{index}",
                        "title":f"Task {index}",
                        "instruction":"Work.",
                        "token_budget":1,
                    }
                    for index in range(4)
                ],
            },
            available_token_budget=10,
            max_agents=3,
        )


@pytest.mark.parametrize(
    "payload,match",
    [
        (
            {
                "schema_version":PLAN_SCHEMA,
                "tasks":[
                    {
                        "task_id":"same",
                        "title":"One",
                        "instruction":"One.",
                        "token_budget":1,
                    },
                    {
                        "task_id":"same",
                        "title":"Two",
                        "instruction":"Two.",
                        "token_budget":1,
                    },
                ],
            },
            "duplicate agent task_id",
        ),
        (
            {
                "schema_version":PLAN_SCHEMA,
                "tasks":[
                    {
                        "task_id":"later",
                        "title":"Later",
                        "instruction":"Later.",
                        "token_budget":1,
                        "dependencies":["missing"],
                    },
                ],
            },
            "earlier planned task",
        ),
        (
            {
                "schema_version":PLAN_SCHEMA,
                "tasks":[
                    {
                        "task_id":"bad/id",
                        "title":"Bad",
                        "instruction":"Bad.",
                        "token_budget":1,
                    },
                ],
            },
            "invalid agent task_id",
        ),
    ],
)
def test_agent_plan_rejects_unsafe_graph_shapes(payload, match):
    with pytest.raises(ValueError, match=match):
        validate_agent_plan(
            payload,
            available_token_budget=20,
        )



@pytest.mark.parametrize("token_budget", [True, False, 1.0, 1.9, "2"])
def test_agent_plan_rejects_non_integer_token_budget_types(token_budget):
    with pytest.raises(ValueError, match="invalid token_budget"):
        validate_agent_plan(
            {
                "schema_version":PLAN_SCHEMA,
                "tasks":[{
                    "task_id":"typed-budget",
                    "title":"Typed budget",
                    "instruction":"Validate strict budget typing.",
                    "token_budget":token_budget,
                }],
            },
            available_token_budget=20,
        )


@pytest.mark.parametrize(
    "field,value",
    [
        ("preferred_capabilities", False),
        ("preferred_capabilities", 0),
        ("preferred_capabilities", ""),
        ("dependencies", False),
        ("dependencies", 0),
        ("dependencies", ""),
    ],
)
def test_agent_plan_rejects_supplied_non_list_collection_values(field, value):
    task = {
        "task_id":"strict-collections",
        "title":"Strict collections",
        "instruction":"Validate strict collection typing.",
        "token_budget":1,
        field:value,
    }

    with pytest.raises(ValueError, match=f"{field} must be a list"):
        validate_agent_plan(
            {
                "schema_version":PLAN_SCHEMA,
                "tasks":[task],
            },
            available_token_budget=20,
        )


def test_agent_plan_allows_null_optional_collections_as_empty():
    tasks = validate_agent_plan(
        {
            "schema_version":PLAN_SCHEMA,
            "tasks":[{
                "task_id":"null-collections",
                "title":"Null collections",
                "instruction":"Treat explicit null optional collections as empty.",
                "token_budget":1,
                "preferred_capabilities":None,
                "dependencies":None,
            }],
        },
        available_token_budget=20,
    )

    assert tasks[0].preferred_capabilities == ()
    assert tasks[0].dependencies == ()
