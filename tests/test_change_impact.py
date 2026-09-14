from production_os.change_impact import analyze_change_impact


def _result(tasks, changed_paths):
    return {
        row.task_id:row
        for row in analyze_change_impact(tasks, changed_paths)
    }


def test_change_impact_skips_unrelated_opt_in_tasks():
    tasks=[
        {
            "task_id":"backend-tests",
            "payload":{
                "impact":{
                    "paths":["backend/**"],
                    "skip_when_unaffected":True,
                }
            },
            "dependencies":[],
        },
        {
            "task_id":"android-tests",
            "payload":{
                "impact":{
                    "paths":["android/**"],
                    "skip_when_unaffected":True,
                }
            },
            "dependencies":[],
        },
        {
            "task_id":"release",
            "payload":{},
            "dependencies":["backend-tests"],
        },
    ]
    result=_result(tasks,["android/app/Main.kt"])
    assert result["android-tests"].affected is True
    assert result["backend-tests"].affected is False
    assert result["release"].affected is True


def test_change_impact_defaults_to_fail_safe_execution():
    rows=analyze_change_impact(
        [{"task_id":"x","payload":{},"dependencies":[]}],
        ["README.md"],
    )
    assert rows[0].affected is True


def test_change_impact_empty_change_set_is_fail_closed():
    tasks=[{
        "task_id":"tests",
        "payload":{
            "impact":{
                "paths":["src/**"],
                "skip_when_unaffected":True,
            }
        },
        "dependencies":[],
    }]
    row=analyze_change_impact(tasks,[])[0]
    assert row.affected is True
    assert row.reason == "fail-safe: no changed paths supplied"


def test_change_impact_can_explicitly_allow_empty_change_skip():
    tasks=[{
        "task_id":"tests",
        "payload":{
            "impact":{
                "paths":["src/**"],
                "skip_when_unaffected":True,
                "allow_empty_changes":True,
            }
        },
        "dependencies":[],
    }]
    row=analyze_change_impact(tasks,[])[0]
    assert row.affected is False


def test_change_impact_excludes_generated_paths():
    tasks=[{
        "task_id":"python-tests",
        "payload":{
            "impact":{
                "paths":["src/**"],
                "exclude_paths":["src/generated/**"],
                "skip_when_unaffected":True,
            }
        },
        "dependencies":[],
    }]
    row=analyze_change_impact(
        tasks,
        ["src/generated/schema.py"],
    )[0]
    assert row.affected is False


def test_change_impact_normalizes_windows_and_dot_paths():
    tasks=[{
        "task_id":"android-tests",
        "payload":{
            "impact":{
                "paths":["android/**"],
                "skip_when_unaffected":True,
            }
        },
        "dependencies":[],
    }]
    result=_result(
        tasks,
        [".\\android\\app\\Main.kt"],
    )
    assert result["android-tests"].affected is True


def test_change_impact_propagates_to_downstream_tasks():
    tasks=[
        {
            "task_id":"build",
            "payload":{
                "impact":{
                    "paths":["src/**"],
                    "skip_when_unaffected":True,
                }
            },
            "dependencies":[],
        },
        {
            "task_id":"package",
            "payload":{
                "impact":{
                    "paths":["package/**"],
                    "skip_when_unaffected":True,
                }
            },
            "dependencies":["build"],
        },
    ]
    result=_result(tasks,["src/core.py"])
    assert result["build"].affected is True
    assert result["package"].affected is True
    assert result["package"].reason == "downstream of affected task build"
