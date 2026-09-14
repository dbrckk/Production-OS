from __future__ import annotations

from dataclasses import dataclass

from .policy import RISK_ORDER


@dataclass(frozen=True, slots=True)
class PolicyValidation:
    valid: bool
    errors: tuple[str, ...]

    def to_dict(self) -> dict:
        return {"valid": self.valid, "errors": list(self.errors)}


def validate_policy_payload(payload: dict) -> PolicyValidation:
    errors: list[str] = []

    def validate_scope(scope: dict, label: str) -> None:
        max_risk = scope.get("max_risk_class")
        if max_risk is not None and str(max_risk) not in RISK_ORDER:
            errors.append(f"{label}.max_risk_class invalid")

        approval = scope.get("approval_required_from")
        if approval is not None and str(approval) not in RISK_ORDER:
            errors.append(f"{label}.approval_required_from invalid")

        budgets = scope.get("budgets", {}) or {}
        for key, value in budgets.items():
            if not isinstance(value, (int, float)) or value < 0:
                errors.append(f"{label}.budgets.{key} must be >= 0")

        for index, freeze in enumerate(scope.get("freeze_windows", []) or []):
            for key in ("start", "end"):
                value = str(freeze.get(key, ""))
                if len(value) != 5 or value[2] != ":":
                    errors.append(
                        f"{label}.freeze_windows[{index}].{key} invalid"
                    )

        slo = scope.get("slo", {}) or {}
        for key in (
            "max_runtime_minutes",
            "max_attempts",
            "max_consecutive_failures",
        ):
            if key in slo:
                value = slo[key]
                if not isinstance(value, (int, float)) or value < 0:
                    errors.append(f"{label}.slo.{key} must be >= 0")

    defaults = payload.get("defaults", {}) or {}
    if not isinstance(defaults, dict):
        errors.append("defaults must be an object")
    else:
        validate_scope(defaults, "defaults")

    repositories = payload.get("repositories", []) or []
    if not isinstance(repositories, list):
        errors.append("repositories must be a list")
    else:
        for index, rule in enumerate(repositories):
            if not isinstance(rule, dict):
                errors.append(f"repositories[{index}] must be an object")
                continue
            if not rule.get("match"):
                errors.append(f"repositories[{index}].match is required")
            validate_scope(rule, f"repositories[{index}]")

    portfolio = payload.get("portfolio_budgets", {}) or {}
    for key, value in portfolio.items():
        if not isinstance(value, (int, float)) or value < 0:
            errors.append(f"portfolio_budgets.{key} must be >= 0")

    return PolicyValidation(valid=not errors, errors=tuple(errors))
