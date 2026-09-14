from __future__ import annotations

from collections import defaultdict, deque


def round_robin_by_repository(rows: list[tuple]) -> list[tuple]:
    """Interleave already-ranked rows by repository while preserving per-repo order."""
    buckets: dict[str, deque] = defaultdict(deque)
    repo_order: list[str] = []

    for row in rows:
        action = row[0]
        repo = action.repository
        if repo not in buckets:
            repo_order.append(repo)
        buckets[repo].append(row)

    ordered: list[tuple] = []
    remaining = True
    while remaining:
        remaining = False
        for repo in repo_order:
            if buckets[repo]:
                ordered.append(buckets[repo].popleft())
                remaining = True
    return ordered
