from production_os.change_impact import analyze_change_impact


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
    rows=analyze_change_impact(tasks,["android/app/Main.kt"])
    result={row.task_id:row for row in rows}
    assert result["android-tests"].affected is True
    assert result["backend-tests"].affected is False
    assert result["release"].affected is True


def test_change_impact_defaults_to_fail_safe_execution():
    rows=analyze_change_impact(
        [{"task_id":"x","payload":{},"dependencies":[]}],
        ["README.md"],
    )
    assert rows[0].affected is True
