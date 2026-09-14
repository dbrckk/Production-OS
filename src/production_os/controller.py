from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path

from .claims import ClaimStore
from .delivery import recover_unacked_jobs
from .dispatch import dispatch_handoff
from .emergency import emergency_stop_active
from .github_client import GitHubClient
from .github_work_state import fetch_github_work_state, runtime_decision_from_github
from .health import build_health, write_health
from .heartbeat_manager import renew_active_leases
from .history import build_snapshot, save_snapshot
from .journal import ExecutionJournal
from .metrics import MetricsStore
from .observability import build_observability_payload, write_observability
from .rate_limit import RateLimitStore
from .reconciliation import reconcile_runtime_state
from .resources import allocate_resources
from .reuse import detect_reuse
from .runtime_state import RuntimeState
from .scheduler import build_schedule
from .scoring import assess_repository
from .self_healing import apply_self_healing
from .workers import WorkerRegistry


def _rank_actions(assessments):
    actions = [action for assessment in assessments for action in assessment.actions]
    return sorted(actions, key=lambda action: action.priority, reverse=True)


def _handoff_for_action(action, reuse):
    related = [item.to_dict() for item in reuse if item.target == action.repository][:5]
    return {
        "schema_version":"production-os/task-handoff/controller-v2",
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


def _load_github_mappings(path: str | None) -> list[dict]:
    if not path:
        return []
    source = Path(path)
    if not source.exists():
        return []
    payload = json.loads(source.read_text(encoding="utf-8"))
    rows = payload.get("mappings", payload)
    return rows if isinstance(rows, list) else []


def _reconcile_github(
    client: GitHubClient,
    state: RuntimeState,
    journal: ExecutionJournal,
    mappings: list[dict],
) -> list[dict]:
    results = []
    for item in mappings:
        repository = str(item.get("repository", ""))
        task = str(item.get("task", ""))
        if not repository or not task:
            continue

        work_state = fetch_github_work_state(
            client,
            repository,
            issue_number=item.get("issue_number"),
            pr_number=item.get("pr_number"),
        )
        decision = runtime_decision_from_github(work_state)
        updated = None
        if decision in {"promote","retry","replan"}:
            updated = state.record_outcome(repository, task, decision).to_dict()

        row = {
            "repository":repository,
            "task":task,
            "decision":decision,
            "github":work_state.to_dict(),
            "runtime_state":updated,
        }
        results.append(row)
        journal.append({
            "source":"controller-github-reconcile",
            **row,
        })
    return results


def run_control_cycle(
    *,
    owner: str,
    runtime_state_path: str,
    queue_dir: str,
    snapshot_dir: str,
    metrics_path: str,
    health_path: str,
    journal_path: str,
    observability_path: str | None = None,
    github_mapping_path: str | None = None,
    worker_registry_path: str | None = None,
    receipt_dir: str | None = None,
    claims_path: str | None = None,
    dead_letter_dir: str | None = None,
    emergency_stop_path: str | None = None,
    rate_limit_path: str | None = None,
    capacity: int = 3,
    slots: int = 3,
    lease_owner: str = "production-os-controller",
    lease_minutes: int = 30,
) -> dict:
    state = RuntimeState(runtime_state_path)
    metrics_store = MetricsStore(metrics_path)
    journal = ExecutionJournal(journal_path)
    worker_registry = WorkerRegistry(worker_registry_path) if worker_registry_path else None
    rate_limit_store = RateLimitStore(rate_limit_path) if rate_limit_path else None
    delivery_recovery = []
    if worker_registry is not None:
        worker_registry.detect_dead()
        if claims_path:
            delivery_recovery = recover_unacked_jobs(
                claims=ClaimStore(claims_path),
                runtime_state=state,
                workers=worker_registry,
                queue_dir=queue_dir,
                dead_letter_dir=dead_letter_dir,
            )
            for item in delivery_recovery:
                journal.append({
                    "source":"controller",
                    "event":"delivery-recovery",
                    **item,
                })

    reconcile_actions = reconcile_runtime_state(state)
    metrics_store.metrics.reconciliations += len(reconcile_actions)

    healing_actions = apply_self_healing(state)
    metrics_store.metrics.self_healing_actions += len(healing_actions)

    heartbeat_results = renew_active_leases(
        state,
        owner=lease_owner,
        minutes=lease_minutes,
    )
    metrics_store.metrics.heartbeats_renewed += sum(
        1 for item in heartbeat_results if item.renewed
    )

    client = GitHubClient()
    github_results = _reconcile_github(
        client,
        state,
        journal,
        _load_github_mappings(github_mapping_path),
    )
    metrics_store.metrics.github_reconciliations += len(github_results)

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
    assessment_lookup = {a.evidence.full_name: a for a in assessments}
    dispatches = []
    emergency_stopped = emergency_stop_active(emergency_stop_path)
    for item in schedule.get("work", []):
        if item.get("lane") not in {"NOW","PARALLEL"}:
            continue
        if emergency_stopped:
            journal.append({"source":"controller","event":"dispatch-blocked","repository":item["repository"],"task":item["task"],"reason":"emergency-stop"})
            continue
        action = action_lookup.get((item["repository"], item["task"]))
        if action is None:
            continue
        handoff = _handoff_for_action(action, reuse)
        assessment = assessment_lookup.get(action.repository)
        required_capabilities = []
        if assessment is not None:
            if assessment.profile in {"android-app","android-game"}:
                required_capabilities.append("android")
            elif assessment.evidence.language:
                lang = assessment.evidence.language.lower()
                if "python" in lang:
                    required_capabilities.append("python")
                elif "javascript" in lang or "typescript" in lang:
                    required_capabilities.append("node")
        try:
            result = dispatch_handoff(
                handoff,
                queue_dir,
                state,
                lease_owner=lease_owner,
                lease_minutes=lease_minutes,
                worker_registry=worker_registry,
                required_capabilities=required_capabilities,
                receipt_dir=receipt_dir,
                emergency_stop_path=emergency_stop_path,
                rate_limit_store=rate_limit_store,
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

    observability = build_observability_payload(
        health=health,
        metrics=metrics_store.metrics.to_dict(),
        runtime_records=[record.to_dict() for record in state.records.values()],
    )
    if observability_path:
        write_observability(observability, observability_path)

    return {
        "schema_version":"production-os/control-cycle/v2",
        "snapshot":snapshot_path,
        "schedule":schedule,
        "resource_allocation":allocation,
        "dispatches":dispatches,
        "reconciliation":[a.to_dict() for a in reconcile_actions],
        "self_healing":[a.to_dict() for a in healing_actions],
        "heartbeats":[a.to_dict() for a in heartbeat_results],
        "github_reconciliation":github_results,
        "workers":[w.to_dict() for w in worker_registry.workers.values()] if worker_registry else [],
        "delivery_recovery":delivery_recovery,
        "emergency_stop":emergency_stopped,
        "health":health,
        "observability":observability,
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
        try:
            results.append(run_control_cycle(**kwargs))
        except Exception as exc:
            metrics_path = kwargs.get("metrics_path")
            health_path = kwargs.get("health_path")
            runtime_state_path = kwargs.get("runtime_state_path")
            if metrics_path and runtime_state_path:
                metrics_store = MetricsStore(metrics_path)
                metrics_store.metrics.last_error = str(exc)
                metrics_store.metrics.cycles += 1
                metrics_store.save()
                if health_path:
                    state = RuntimeState(runtime_state_path)
                    write_health(
                        build_health(state, metrics_store.metrics.to_dict()),
                        health_path,
                    )
            raise
        if index + 1 < cycles:
            time.sleep(max(1, interval_seconds))
    return results
