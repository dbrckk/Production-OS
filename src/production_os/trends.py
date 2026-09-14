from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Trend:
    repository: str
    samples: int
    first_score: int
    latest_score: int
    delta: int
    direction: str

    def to_dict(self) -> dict:
        return {
            "repository": self.repository,
            "samples": self.samples,
            "first_score": self.first_score,
            "latest_score": self.latest_score,
            "delta": self.delta,
            "direction": self.direction,
        }


def build_trends(snapshots: list[dict]) -> list[Trend]:
    series: dict[str, list[int]] = {}

    for snapshot in snapshots:
        for repo, payload in snapshot.get("repositories", {}).items():
            series.setdefault(repo, []).append(int(payload.get("score", 0)))

    trends: list[Trend] = []
    for repo, scores in series.items():
        if not scores:
            continue
        delta = scores[-1] - scores[0]
        if delta > 0:
            direction = "improving"
        elif delta < 0:
            direction = "regressing"
        else:
            direction = "flat"

        trends.append(
            Trend(
                repository=repo,
                samples=len(scores),
                first_score=scores[0],
                latest_score=scores[-1],
                delta=delta,
                direction=direction,
            )
        )

    return sorted(trends, key=lambda item: (item.direction != "regressing", item.delta, item.repository))
