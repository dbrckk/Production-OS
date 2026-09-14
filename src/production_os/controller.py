from __future__ import annotations

import time
from datetime import datetime, timezone
from pathlib import Path

from .dispatch import dispatch_handoff
from .github_client import GitHubClient
from .health import build_health, write_health
from .history import build_snapshot, save_snapshot
from .journal import ExecutionJournal
from .metrics import MetricsStore
from .reconciliation import reconcile_runtime_state
from .resources import allocate_resources
from .reuse import detect_reuse
from .runtime_state import RuntimeState
from .scheduler import build_schedule
from .scoring import assess_repository


def _rank_actions(assessments):
    actions = [action for assessment in assessments for action in assessment.actions]
    return sorted(actions, key=lambda action: action.priority, reverse=True)


def _handoff_for_action(action, reuse):
    related = [item.to_dict() for item in reuse if item.target == action.repository][:5]
    return {
        "schema_version":"production-os/task-handoff/controller-v1",
        "source":"Production-OS",
        "executor":"ai-dev-server",
        "repository":action.repository,
        "task":action.task,
        "rationale":action.rationale,
        "acceptance_criteria":action.acceptance_criteria,
        "trigger_evidence":action.evidence,
        "priority":action.priority,
        "reuse_candidates":related,
        "constraints":{
            "preserve_existing_behavior":True,
            "verify_before_completion":True,
            "reuse_before_rebuild":True,
        },
    }


def run_control_cycle(
    *,
    owner: str,
    runtime_state_path: str,
    queue_dir: str,
    snapshot_dir: str,
    metrics_path: str,
    health_path: str,
    journal_path: str,
    capacity: int = 3,
    slots: int = 3,
    lease_owner: str = "production-os-controller",
    lease_minutes: int = 30,
) -> dict:
    state = RuntimeState(runtime_state_path)
    metrics_store = MetricsStore(metrics_path)
    journal = ExecutionJournal(journal_path)

    reconcile_actions = reconcile_runtime_state(state)
    metrics_store.metrics.reconciliations += len(reconcile_actions)

    client = GitHubClient()
    repos = client.list_repositories(owner)
    assessments = []
    for repo in repos:
        if repo.get("fork") or repo.get("archived"):
            continue
        try:
            assessments.append(assess_repository(client.collect_evidence(repo)))
        except Exception as exc:
            journal.append({
                "source":"controller",
                "event":"scan-error",
                "repository":repo.get("full_name"),
                "error":str(exc),
            })

    metrics_store.metrics.scans += 1
    actions = _rank_actions(assessments)
    reuse = detect_reuse(assessments)
    schedule = build_schedule(
        assessments,
        actions,
        capacity=capacity,
        runtime_state=state,
    )
    allocation = allocate_resources(schedule, total_slots=slots)

    action_lookup = {(a.repository, a.task): a for a in actions}
    dispatches = []
    for item in schedule.get("work", []):
        if item.get("lane") not in {"NOW","PARALLEL"}:
            continue
        action = action_lookup.get((item["repository"], item["task"]))
        if action is None:
            continue
        handoff = _handoff_for_action(action, reuse)
        try:
            result = dispatch_handoff(
                handoff,
                queue_dir,
                state,
                lease_owner=lease_owner,
                lease_minutes=lease_minutes,
            )
            dispatches.append(result.to_dict())
            metrics_store.metrics.dispatched += 1
            journal.append({
                "source":"controller",
                "event":"dispatch",
                **result.to_dict(),
            })
        except RuntimeError as exc:
            metrics_store.metrics.dispatch_failures += 1
            journal.append({
                "source":"controller",
                "event":"dispatch-skipped",
                "repository":item["repository"],
                "task":item["task"],
                "error":str(exc),
            })

    snapshot = build_snapshot(owner, assessments)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    snapshot_path = str(Path(snapshot_dir) / f"{stamp}.json")
    save_snapshot(snapshot, snapshot_path)

    metrics_store.metrics.cycles += 1
    metrics_store.metrics.last_error = None
    metrics_store.save()
    health = build_health(state, metrics_store.metrics.to_dict())
    write_health(health, health_path)

    return {
        "schema_version":"production-os/control-cycle/v1",
        "snapshot":snapshot_path,
        "schedule":schedule,
        "resource_allocation":allocation,
        "dispatches":dispatches,
        "reconciliation":[a.to_dict() for a in reconcile_actions],
        "health":health,
    }


def run_controller(
    *,
    cycles: int,
    interval_seconds: int,
    **kwargs,
) -> list[dict]:
    if cycles < 1:
        raise ValueError("cycles must be >= 1")
    results = []
    for index in range(cycles):
        results.append(run_control_cycle(**kwargs))
        if index + 1 < cycles:
            time.sleep(max(1, interval_seconds))
    return results
