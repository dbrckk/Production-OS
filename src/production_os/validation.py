from __future__ import annotations

from dataclasses import dataclass

from .models import RepoAssessment


@dataclass(frozen=True, slots=True)
class ValidationStep:
    order: int
    kind: str
    required: bool
    description: str

    def to_dict(self) -> dict:
        return {
            "order": self.order,
            "kind": self.kind,
            "required": self.required,
            "description": self.description,
        }


def build_validation_plan(
    target: RepoAssessment,
    capability: str,
    adaptation_plan: dict,
    dependency_checks: list[dict],
) -> list[ValidationStep]:
    steps: list[ValidationStep] = []
    order = 1

    def add(kind: str, description: str, required: bool = True) -> None:
        nonlocal order
        steps.append(ValidationStep(order, kind, required, description))
        order += 1

    missing = [
        item["dependency"]
        for item in dependency_checks
        if item["status"] != "available"
    ]

    if missing:
        add(
            "dependency",
            "Resolve or explicitly bind missing/unverified dependencies: "
            + ", ".join(sorted(set(missing))),
        )

    if adaptation_plan.get("copy_or_adapt"):
        add("compile", "Compile/build the target after component adaptation.")

    reused_tests = adaptation_plan.get("reuse_tests", [])
    if reused_tests:
        add(
            "unit-tests",
            f"Port or recreate {len(reused_tests)} linked source test(s) and make them pass.",
        )
    else:
        add(
            "unit-tests",
            "Create focused automated tests for the adapted capability because no linked source tests were found.",
        )

    if capability.startswith("android-"):
        add("android-build", "Build a debug APK/AAB successfully.")
        add("device-smoke", "Install and run a smoke test on emulator/device.")
        if capability == "android-play-billing":
            add("billing", "Verify purchase, acknowledgement and restore/entitlement behavior.")
        elif capability == "android-admob":
            add("ads", "Verify ad initialization and no-crash behavior with test configuration.")
        elif capability == "android-consent":
            add("consent", "Verify consent state transitions and persistence.")

    if target.evidence.has_ci:
        add("ci", "Default-branch/PR CI must be green after the change.")
    else:
        add("ci", "Add or run an equivalent reproducible verification command before promotion.")

    add(
        "regression",
        "Run existing target tests and verify no previously working behavior regressed.",
    )

    return steps
