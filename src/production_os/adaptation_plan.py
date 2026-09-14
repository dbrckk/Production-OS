from __future__ import annotations

from dataclasses import dataclass

from .models import RepoAssessment


@dataclass(frozen=True, slots=True)
class AdaptationPlan:
    source_repository: str
    target_repository: str
    capability: str
    strategy: str
    copy_or_adapt: tuple[dict, ...]
    recreate: tuple[str, ...]
    reuse_tests: tuple[dict, ...]
    do_not_copy: tuple[dict, ...]
    target_changes: tuple[str, ...]
    overall_risk: int

    def to_dict(self) -> dict:
        return {
            "source_repository": self.source_repository,
            "target_repository": self.target_repository,
            "capability": self.capability,
            "strategy": self.strategy,
            "copy_or_adapt": list(self.copy_or_adapt),
            "recreate": list(self.recreate),
            "reuse_tests": list(self.reuse_tests),
            "do_not_copy": list(self.do_not_copy),
            "target_changes": list(self.target_changes),
            "overall_risk": self.overall_risk,
        }


def _is_ui_coupled(component: dict) -> bool:
    name = str(component.get("name", "")).lower()
    path = str(component.get("path", "")).lower()
    return any(token in name or token in path for token in (
        "screen", "view", "activity", "fragment", "ui", "compose",
    ))


def _is_low_value_for_reuse(component: dict) -> bool:
    return (
        bool(component.get("test_like"))
        or int(component.get("adaptation_risk", 101)) > 50
        or _is_ui_coupled(component)
    )


def build_adaptation_plan(
    source: RepoAssessment,
    target: RepoAssessment,
    capability: str,
    components: list[dict],
) -> AdaptationPlan:
    copy_or_adapt: list[dict] = []
    do_not_copy: list[dict] = []
    tests: list[dict] = []
    recreate: set[str] = set()
    target_changes: set[str] = set()

    for component in components:
        if _is_low_value_for_reuse(component):
            do_not_copy.append(component)
            continue

        copy_or_adapt.append(component)

        for dep in component.get("dependencies", []):
            dep_name = str(dep)
            if dep_name:
                recreate.add(dep_name)

        for linked_test in component.get("linked_tests", []):
            tests.append(linked_test)

        if source.evidence.full_name != target.evidence.full_name:
            target_changes.add("replace source package/module namespace with target namespace")

        if source.profile != target.profile:
            target_changes.add(
                f"adapt project-family assumptions from {source.profile} to {target.profile}"
            )

        if component.get("language") and target.evidence.language:
            target_lang = target.evidence.language.lower()
            source_lang = str(component["language"]).lower()
            if source_lang not in target_lang and not (
                source_lang in {"java", "kotlin"} and target_lang in {"java", "kotlin"}
            ):
                target_changes.add(
                    f"port component language from {component['language']} to {target.evidence.language}"
                )

    unique_tests = {
        (str(item.get("path", "")), str(item.get("name", ""))): item
        for item in tests
    }

    if copy_or_adapt:
        avg_risk = round(
            sum(int(item.get("adaptation_risk", 50)) for item in copy_or_adapt)
            / len(copy_or_adapt)
        )
        strategy = "component-adaptation"
    else:
        candidate_risks = [
            int(item.get("adaptation_risk", 75))
            for item in components
        ]
        avg_risk = min(candidate_risks) if candidate_risks else 75
        strategy = "architecture-pattern-only"
        target_changes.add("reimplement capability locally using source architecture only")

    if capability.startswith("android-"):
        target_changes.add("replace app-specific IDs, package names and product configuration")
    if capability in {"audit-trail", "queued-workers", "experiment-registry"}:
        target_changes.add("bind target storage/configuration explicitly")

    return AdaptationPlan(
        source_repository=source.evidence.full_name,
        target_repository=target.evidence.full_name,
        capability=capability,
        strategy=strategy,
        copy_or_adapt=tuple(copy_or_adapt[:8]),
        recreate=tuple(sorted(recreate)),
        reuse_tests=tuple(unique_tests.values())[:8],
        do_not_copy=tuple(do_not_copy[:8]),
        target_changes=tuple(sorted(target_changes)),
        overall_risk=max(0, min(100, avg_risk)),
    )
