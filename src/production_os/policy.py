from __future__ import annotations

import fnmatch
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


RISK_ORDER = {"low":0, "medium":1, "high":2, "critical":3}


@dataclass(frozen=True, slots=True)
class PolicyDecision:
    allowed: bool
    risk_class: str
    requires_approval: bool
    quarantined: bool
    reasons: tuple[str, ...]
    allowed_worker_classes: tuple[str, ...]
    budgets: dict[str, float]

    def to_dict(self) -> dict:
        return {
            "allowed": self.allowed,
            "risk_class": self.risk_class,
            "requires_approval": self.requires_approval,
            "quarantined": self.quarantined,
            "reasons": list(self.reasons),
            "allowed_worker_classes": list(self.allowed_worker_classes),
            "budgets": dict(self.budgets),
        }


class PolicySet:
    def __init__(self, payload: dict[str, Any]):
        self.payload = payload or {}

    @classmethod
    def load(cls, path: str | Path | None) -> "PolicySet":
        if not path:
            return cls({})
        source = Path(path)
        if not source.exists():
            return cls({})
        return cls(json.loads(source.read_text(encoding="utf-8")))

    def merged_for(self, repository: str) -> dict[str, Any]:
        result = dict(self.payload.get("defaults", {}))
        for rule in self.payload.get("repositories", []):
            pattern = str(rule.get("match", ""))
            if pattern and fnmatch.fnmatch(repository, pattern):
                for key, value in rule.items():
                    if key == "match":
                        continue
                    if isinstance(value, dict) and isinstance(result.get(key), dict):
                        result[key] = {**result[key], **value}
                    else:
                        result[key] = value
        return result


def classify_risk(handoff: dict) -> str:
    explicit = handoff.get("risk_class")
    if explicit in RISK_ORDER:
        return str(explicit)

    task = str(handoff.get("task", "")).lower()
    constraints = handoff.get("constraints", {}) or {}

    if constraints.get("destructive") or constraints.get("externally_privileged"):
        return "critical"
    if any(token in task for token in ("release", "deploy", "production", "publish", "migration")):
        return "high"
    if any(token in task for token in ("dependency", "refactor", "database", "schema")):
        return "medium"
    return "low"


def _freeze_active(policy: dict[str, Any], now: datetime) -> bool:
    freezes = policy.get("freeze_windows", [])
    weekday = now.strftime("%a").lower()[:3]
    hhmm = now.strftime("%H:%M")
    for freeze in freezes:
        days = [str(x).lower()[:3] for x in freeze.get("days", [])]
        if days and weekday not in days:
            continue
        start = str(freeze.get("start", "00:00"))
        end = str(freeze.get("end", "23:59"))
        if start <= end:
            if start <= hhmm <= end:
                return True
        else:
            if hhmm >= start or hhmm <= end:
                return True
    return False


def evaluate_policy(
    policy_set: PolicySet,
    handoff: dict,
    *,
    now: datetime | None = None,
) -> PolicyDecision:
    now = now or datetime.now(timezone.utc)
    repository = str(handoff.get("repository", ""))
    policy = policy_set.merged_for(repository)
    risk = classify_risk(handoff)
    reasons: list[str] = []
    allowed = True
    quarantined = False

    if bool(policy.get("disabled", False)):
        allowed = False
        reasons.append("repository policy disabled execution")

    max_risk = str(policy.get("max_risk_class", "critical"))
    if RISK_ORDER.get(risk, 99) > RISK_ORDER.get(max_risk, 3):
        allowed = False
        reasons.append(f"risk class {risk} exceeds policy maximum {max_risk}")

    if _freeze_active(policy, now):
        if risk in set(policy.get("freeze_risk_classes", ["high","critical"])):
            allowed = False
            reasons.append("release/change freeze window active")

    protected_for = set(
        str(x) for x in policy.get(
            "require_branch_protection_for",
            [],
        )
    )
    if risk in protected_for:
        if handoff.get("branch_protected") is not True:
            allowed = False
            reasons.append(
                "branch protection is required but not positively verified"
            )

    quarantine = policy.get("quarantine", {}) or {}
    if bool(quarantine.get("active", False)):
        quarantined = True
        allowed = False
        reasons.append(str(quarantine.get("reason") or "repository quarantined"))

    approval_from = str(policy.get("approval_required_from", "critical"))
    requires_approval = (
        RISK_ORDER.get(risk, 0) >= RISK_ORDER.get(approval_from, 3)
    )

    allowed_workers = tuple(
        str(x) for x in policy.get("allowed_worker_classes", []) if str(x)
    )
    budgets = {
        str(k): float(v)
        for k, v in (policy.get("budgets", {}) or {}).items()
        if isinstance(v, (int, float))
    }

    return PolicyDecision(
        allowed=allowed,
        risk_class=risk,
        requires_approval=requires_approval,
        quarantined=quarantined,
        reasons=tuple(reasons),
        allowed_worker_classes=allowed_workers,
        budgets=budgets,
    )
