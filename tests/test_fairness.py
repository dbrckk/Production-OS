from production_os.fairness import round_robin_by_repository


class Action:
    def __init__(self, repository, task):
        self.repository=repository
        self.task=task


def test_round_robin_preserves_repo_internal_order():
    rows=[
        (Action("a","a1"),None,100,()),
        (Action("a","a2"),None,90,()),
        (Action("b","b1"),None,80,()),
        (Action("b","b2"),None,70,()),
    ]
    result=round_robin_by_repository(rows)
    assert [r[0].task for r in result]==["a1","b1","a2","b2"]
