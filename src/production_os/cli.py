from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Iterable

from .approvals import ApprovalStore
from .audit_integrity import verify_hash_chain
from .backup import create_backup, restore_backup
from .claims import ClaimStore
from .control_surface import write_control_surface
from .controller import run_controller
from .delivery import recover_unacked_jobs
from .dispatch import dispatch_handoff
from .emergency import clear_emergency_stop, set_emergency_stop
from .execution_feedback import decide_execution_outcome
from .feedback import summarize_validation_results
from .github_client import GitHubAPIError, GitHubClient
from .github_work_state import fetch_github_work_state, runtime_decision_from_github
from .graph import build_knowledge_graph
from .health_server import serve_health
from .history import build_snapshot, detect_regressions, load_snapshot, save_snapshot
from .journal import ExecutionJournal
from .learning import build_learning_signals
from .migrations import migrate_state_file
from .models import ActionCandidate, RepoAssessment
from .reuse import detect_reuse
from .preemption import confirm_checkpoint_and_release, request_preemption
from .rate_limit import RateLimitStore
from .reconciliation import reconcile_runtime_state
from .resources import allocate_resources
from .runtime_state import RuntimeState
from .scheduler import build_schedule
from .scoring import assess_repository
from .starlist import suggest_external_references
from .trends import build_trends
from .workers import WorkerRegistry


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="production-os")
    sub = parser.add_subparsers(dest="command", required=True)

    scan = sub.add_parser("scan", help="Scan and prioritize a GitHub portfolio")
    scan.add_argument("--owner", required=True, help="GitHub owner/user")
    scan.add_argument("--include", nargs="*", default=None, help="Only these repository names")
    scan.add_argument("--exclude", nargs="*", default=[], help="Exclude repository names")
    scan.add_argument("--json", action="store_true", help="Emit complete JSON assessment")
    scan.add_argument("--handoff", action="store_true", help="Emit only the top ai-dev-server task contract")
    scan.add_argument("--snapshot", help="Persist current portfolio snapshot to this JSON file")
    scan.add_argument("--compare", help="Compare current portfolio against a previous snapshot")
    scan.add_argument("--star-list-repo", default="dbrckk/star-list")
    scan.add_argument("--star-list-path", default="catalog.json")
    scan.add_argument("--no-star-list", action="store_true")
    scan.add_argument("--include-forks", action="store_true")
    scan.add_argument("--include-archived", action="store_true")
    scan.add_argument("--schedule", action="store_true", help="Emit autonomous portfolio schedule")
    scan.add_argument("--capacity", type=int, default=3, help="Maximum concurrent active repositories")
    scan.add_argument("--slots", type=int, default=3, help="Execution slots to allocate")
    scan.add_argument("--learning-events", help="JSON file with historical execution events")
    scan.add_argument("--dashboard", help="Write an HTML control surface to this path")
    scan.add_argument("--runtime-state", help="Persistent runtime state JSON for leases/cooldowns/circuit breakers")

    validation = sub.add_parser(
        "validation-results",
        help="Evaluate execution/validation results against a generated validation plan",
    )
    validation.add_argument("--plan", required=True, help="JSON file containing an adaptation plan or validation plan")
    validation.add_argument("--results", required=True, help="JSON file containing validation results")
    validation.add_argument("--output", help="Optional path to write the summary JSON")

    feedback = sub.add_parser("execution-feedback", help="Decide promote/retry/rollback/replan from before/after snapshots and validation")
    feedback.add_argument("--before", required=True)
    feedback.add_argument("--after", required=True)
    feedback.add_argument("--repository", required=True)
    feedback.add_argument("--validation-summary", required=True)
    feedback.add_argument("--task", default="")
    feedback.add_argument("--runtime-state")
    feedback.add_argument("--journal")

    trends = sub.add_parser("trends", help="Build long-term repository score trends from snapshot JSON files")
    trends.add_argument("snapshots", nargs="+")

    heartbeat = sub.add_parser("heartbeat", help="Renew an execution lease")
    heartbeat.add_argument("--runtime-state", required=True)
    heartbeat.add_argument("--repository", required=True)
    heartbeat.add_argument("--task", required=True)
    heartbeat.add_argument("--owner", required=True)
    heartbeat.add_argument("--minutes", type=int, default=30)

    reconcile = sub.add_parser("reconcile", help="Recover expired leases and cooled-down circuits")
    reconcile.add_argument("--runtime-state", required=True)

    dispatch = sub.add_parser("dispatch", help="Dispatch a handoff to the ai-dev-server file queue")
    dispatch.add_argument("--handoff", required=True)
    dispatch.add_argument("--runtime-state", required=True)
    dispatch.add_argument("--queue-dir", required=True)
    dispatch.add_argument("--owner", default="production-os")
    dispatch.add_argument("--lease-minutes", type=int, default=30)
    dispatch.add_argument("--worker-registry")
    dispatch.add_argument("--required-capability", action="append", default=[])
    dispatch.add_argument("--receipt-dir")
    dispatch.add_argument("--emergency-stop")
    dispatch.add_argument("--rate-limit-state")
    dispatch.add_argument("--approvals")

    ghrec = sub.add_parser("github-reconcile", help="Reconcile runtime tasks from explicit GitHub issue/PR mappings")
    ghrec.add_argument("--mapping", required=True, help="JSON list of repository/task/issue_number/pr_number mappings")
    ghrec.add_argument("--runtime-state", required=True)
    ghrec.add_argument("--journal")

    controller = sub.add_parser("controller", help="Run bounded autonomous control cycles")
    controller.add_argument("--owner", required=True)
    controller.add_argument("--runtime-state", required=True)
    controller.add_argument("--queue-dir", required=True)
    controller.add_argument("--snapshot-dir", required=True)
    controller.add_argument("--metrics", required=True)
    controller.add_argument("--health", required=True)
    controller.add_argument("--journal", required=True)
    controller.add_argument("--cycles", type=int, default=1)
    controller.add_argument("--interval-seconds", type=int, default=300)
    controller.add_argument("--capacity", type=int, default=3)
    controller.add_argument("--slots", type=int, default=3)
    controller.add_argument("--lease-owner", default="production-os-controller")
    controller.add_argument("--lease-minutes", type=int, default=30)
    controller.add_argument("--github-mapping", help="Optional explicit task->issue/PR mapping JSON")
    controller.add_argument("--observability", help="Write structured observability JSON")
    controller.add_argument("--worker-registry", help="Persistent worker registry JSON")
    controller.add_argument("--receipt-dir", help="Dispatch receipt directory")
    controller.add_argument("--claims", help="Persistent claim store JSON")
    controller.add_argument("--dead-letter-dir", help="Directory for expired unacked jobs")
    controller.add_argument("--emergency-stop", help="Global emergency stop state JSON")
    controller.add_argument("--rate-limit-state", help="Persistent rate-limit state JSON")
    controller.add_argument("--approvals", help="Persistent approval gate store JSON")

    healthserver = sub.add_parser("health-server", help="Serve the health JSON over HTTP")
    healthserver.add_argument("--health", required=True)
    healthserver.add_argument("--host", default="127.0.0.1")
    healthserver.add_argument("--port", type=int, default=8765)

    workerreg = sub.add_parser("worker-register", help="Register or update a worker")
    workerreg.add_argument("--registry", required=True)
    workerreg.add_argument("--worker-id", required=True)
    workerreg.add_argument("--capability", action="append", default=[])
    workerreg.add_argument("--max-concurrency", type=int, default=1)

    workerhb = sub.add_parser("worker-heartbeat", help="Heartbeat a worker and update its active task count")
    workerhb.add_argument("--registry", required=True)
    workerhb.add_argument("--worker-id", required=True)
    workerhb.add_argument("--active-tasks", type=int)

    workerlist = sub.add_parser("worker-list", help="List worker registry state")
    workerlist.add_argument("--registry", required=True)
    workerlist.add_argument("--dead-timeout-seconds", type=int, default=120)

    jobclaim = sub.add_parser("job-claim", help="Claim a dispatched job")
    jobclaim.add_argument("--claims", required=True)
    jobclaim.add_argument("--queue-file", required=True)
    jobclaim.add_argument("--worker-id", required=True)
    jobclaim.add_argument("--ack-timeout-seconds", type=int, default=120)

    joback = sub.add_parser("job-ack", help="Acknowledge a claimed job")
    joback.add_argument("--claims", required=True)
    joback.add_argument("--key", required=True)
    joback.add_argument("--worker-id", required=True)

    jobcomplete = sub.add_parser("job-complete", help="Mark a job complete and release worker/runtime accounting")
    jobcomplete.add_argument("--claims", required=True)
    jobcomplete.add_argument("--key", required=True)
    jobcomplete.add_argument("--worker-id", required=True)
    jobcomplete.add_argument("--registry", required=True)
    jobcomplete.add_argument("--runtime-state", required=True)

    deliveryrecover = sub.add_parser("delivery-recover", help="Recover expired unacked deliveries")
    deliveryrecover.add_argument("--claims", required=True)
    deliveryrecover.add_argument("--registry", required=True)
    deliveryrecover.add_argument("--runtime-state", required=True)
    deliveryrecover.add_argument("--queue-dir", required=True)
    deliveryrecover.add_argument("--dead-letter-dir")

    preempt = sub.add_parser("preempt-request", help="Request cooperative preemption of an interruptible running task")
    preempt.add_argument("--runtime-state", required=True)
    preempt.add_argument("--repository", required=True)
    preempt.add_argument("--task", required=True)

    checkpoint = sub.add_parser("preempt-checkpoint", help="Confirm checkpoint and release a preempted task slot")
    checkpoint.add_argument("--runtime-state", required=True)
    checkpoint.add_argument("--registry", required=True)
    checkpoint.add_argument("--repository", required=True)
    checkpoint.add_argument("--task", required=True)
    checkpoint.add_argument("--worker-id", required=True)
    checkpoint.add_argument("--checkpoint-ref", required=True)

    estop = sub.add_parser("emergency-stop", help="Activate global emergency stop")
    estop.add_argument("--state", required=True)
    estop.add_argument("--reason", required=True)

    eresume = sub.add_parser("emergency-resume", help="Clear global emergency stop")
    eresume.add_argument("--state", required=True)

    auditverify = sub.add_parser("audit-verify", help="Verify execution journal hash chain")
    auditverify.add_argument("--journal", required=True)

    backup = sub.add_parser("backup", help="Backup critical state files")
    backup.add_argument("--destination-dir", required=True)
    backup.add_argument("paths", nargs="+")

    restore = sub.add_parser("restore", help="Restore or verify a backup manifest")
    restore.add_argument("--manifest", required=True)
    restore.add_argument("--verify-only", action="store_true")

    approve = sub.add_parser("approve", help="Approve a gated task key")
    approve.add_argument("--store", required=True)
    approve.add_argument("--key", required=True)
    approve.add_argument("--approved-by", required=True)
    approve.add_argument("--reason")

    revoke = sub.add_parser("revoke", help="Revoke a gated task key")
    revoke.add_argument("--store", required=True)
    revoke.add_argument("--key", required=True)
    revoke.add_argument("--approved-by", required=True)
    revoke.add_argument("--reason")

    migrate = sub.add_parser("migrate-state", help="Migrate a persistent state file to the current schema")
    migrate.add_argument("--path", required=True)

    return parser.parse_args(argv)


def _rank_actions(assessments: Iterable[RepoAssessment]) -> list[ActionCandidate]:
    actions = [action for assessment in assessments for action in assessment.actions]
    return sorted(actions, key=lambda action: action.priority, reverse=True)


def _external_refs_for_action(action: ActionCandidate, catalog: dict | None) -> list[dict]:
    mapping = {
        "Add an executable automated test baseline": "automated-tests",
        "Add continuous integration for every change": "github-actions-ci",
        "Create a deterministic release pipeline": "release-automation",
        "Add Android release-readiness gate": "android-device-qa",
        "Harden repository maintenance and supply-chain hygiene": "dependency-automation",
    }
    capability = mapping.get(action.task)
    if not capability:
        return []
    return [
        ref.to_dict()
        for ref in suggest_external_references(capability, catalog, limit=5)
    ]


def _handoff(action: ActionCandidate, reuse: list, catalog: dict | None) -> dict:
    related_reuse = [
        item.to_dict() for item in reuse if item.target == action.repository
    ][:5]

    reusable_components = []
    adaptation_plans = []

    for item in related_reuse:
        if item.get("adaptation_plan"):
            adaptation_plans.append(item["adaptation_plan"])
        for component in item.get("components", []):
            reusable_components.append({
                "source_repository": item["source"],
                "capability": item["capability"],
                **component,
            })

    reusable_components.sort(
        key=lambda item: (
            int(item.get("adaptation_risk", 101)),
            -float(item.get("confidence", 0)),
            -len(item.get("linked_tests", [])),
            item.get("source_repository", ""),
            item.get("path", ""),
            item.get("name", ""),
        )
    )

    adaptation_plans.sort(
        key=lambda item: (
            not bool(item.get("compatible_for_adaptation")),
            int(item.get("overall_risk", 101)),
            len(item.get("major_version_mismatches", [])),
            len(item.get("missing_dependencies", [])),
            item.get("source_repository", ""),
            item.get("capability", ""),
        )
    )

    recommended = [
        component
        for component in reusable_components
        if int(component.get("adaptation_risk", 101)) <= 50
        and not component.get("test_like", False)
    ]

    executable_plans = [
        plan for plan in adaptation_plans
        if plan.get("compatible_for_adaptation")
    ]

    return {
        "schema_version": "production-os/task-handoff/v9",
        "source": "Production-OS",
        "executor": "ai-dev-server",
        "repository": action.repository,
        "task": action.task,
        "rationale": action.rationale,
        "acceptance_criteria": action.acceptance_criteria,
        "trigger_evidence": action.evidence,
        "priority": action.priority,
        "reuse_candidates": related_reuse,
        "reusable_components": reusable_components[:12],
        "recommended_components": recommended[:8],
        "adaptation_plans": adaptation_plans[:5],
        "executable_adaptation_plans": executable_plans[:3],
        "external_reference_candidates": _external_refs_for_action(action, catalog),
        "constraints": {
            "preserve_existing_behavior": True,
            "verify_before_completion": True,
            "reuse_before_rebuild": True,
            "prefer_component_level_reuse": True,
            "prefer_low_risk_components": True,
            "require_linked_tests_when_available": True,
            "respect_do_not_copy_boundaries": True,
            "resolve_missing_dependencies_before_promotion": True,
            "reject_major_version_mismatch_before_promotion": True,
            "complete_validation_plan_before_promotion": True,
            "prefer_evidence_backed_references": True,
            "no_secret_material_in_workspace": True,
        },
    }


def _print_human(assessments, actions, regressions, reuse, catalog_loaded: bool) -> None:
    print("Production-OS portfolio assessment")
    print("=" * 34)
    print(f"star-list catalog: {'loaded' if catalog_loaded else 'unavailable'}")
    print()

    for assessment in sorted(assessments, key=lambda item: item.score.total, reverse=True):
        e = assessment.evidence
        print(
            f"{e.full_name:<40} {assessment.score.total:>3}/100 "
            f"[{assessment.profile}] caps={len(assessment.capabilities)} "
            f"components={len(assessment.components)} sampled={len(e.source_documents)}"
        )

    print()
    if regressions:
        print("REGRESSIONS")
        for regression in regressions:
            print(
                f"- {regression.repository}: "
                f"{regression.previous_score} -> {regression.current_score} "
                f"({regression.delta})"
            )
        print()

    if reuse:
        print("TOP REUSE OPPORTUNITIES")
        for item in reuse[:8]:
            plan = item.adaptation_plan or {}
            print(
                f"- {item.target} <- {item.source}: {item.capability} "
                f"({item.confidence:.0%}) risk={plan.get('overall_risk', 'n/a')} "
                f"missing={len(plan.get('missing_dependencies', []))} "
                f"version-conflicts={len(plan.get('major_version_mismatches', []))} "
                f"compatible={plan.get('compatible_for_adaptation', False)}"
            )
        print()

    if not actions:
        print("No improvement action generated from the current evidence.")
        return

    top = actions[0]
    print("NEXT BEST ACTION")
    print(f"Repository : {top.repository}")
    print(f"Priority   : {top.priority}")
    print(f"Task       : {top.task}")
    print(f"Why        : {top.rationale}")


def run_scan(args: argparse.Namespace) -> int:
    client = GitHubClient()
    try:
        repos = client.list_repositories(args.owner)
    except GitHubAPIError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    catalog = None
    if not args.no_star_list:
        try:
            catalog = client.read_json_file(args.star_list_repo, args.star_list_path)
        except GitHubAPIError as exc:
            print(f"warning: star-list unavailable: {exc}", file=sys.stderr)

    include = set(args.include or [])
    exclude = set(args.exclude or [])
    selected = []
    for repo in repos:
        if include and repo["name"] not in include:
            continue
        if repo["name"] in exclude:
            continue
        if repo.get("fork") and not args.include_forks:
            continue
        if repo.get("archived") and not args.include_archived:
            continue
        selected.append(repo)

    assessments: list[RepoAssessment] = []
    for repo in selected:
        try:
            evidence = client.collect_evidence(repo)
        except GitHubAPIError as exc:
            print(f"warning: {repo['full_name']}: {exc}", file=sys.stderr)
            continue
        assessments.append(assess_repository(evidence))

    actions = _rank_actions(assessments)
    reuse = detect_reuse(assessments)
    graph = build_knowledge_graph(assessments)
    snapshot = build_snapshot(args.owner, assessments)
    previous = load_snapshot(args.compare) if args.compare else None
    regressions = detect_regressions(previous, snapshot)

    if args.snapshot:
        save_snapshot(snapshot, args.snapshot)

    if args.schedule:
        learning_signals = []
        if args.learning_events:
            events_payload = json.loads(Path(args.learning_events).read_text(encoding="utf-8"))
            events = events_payload.get("events", events_payload)
            if not isinstance(events, list):
                raise SystemExit("learning events must be a JSON list or contain events")
            learning_signals = build_learning_signals(events)

        runtime_state = RuntimeState(args.runtime_state) if args.runtime_state else None
        schedule = build_schedule(
            assessments,
            actions,
            capacity=args.capacity,
            learning_signals=learning_signals,
            runtime_state=runtime_state,
        )
        payload = {
            "schema_version": "production-os/portfolio-control/v1",
            "schedule": schedule,
            "resource_allocation": allocate_resources(schedule, total_slots=args.slots),
            "learning_signals": [signal.to_dict() for signal in learning_signals],
        }
        if args.dashboard:
            write_control_surface(payload, args.dashboard)
            payload["dashboard"] = args.dashboard
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    elif args.handoff:
        payload = _handoff(actions[0], reuse, catalog) if actions else {
            "schema_version": "production-os/task-handoff/v9",
            "status": "no_action",
        }
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    elif args.json:
        payload = {
            "schema_version": "production-os/portfolio/v10",
            "owner": args.owner,
            "star_list": {
                "repository": args.star_list_repo,
                "path": args.star_list_path,
                "loaded": bool(catalog),
                "repository_count": len(catalog.get("repositories", [])) if catalog else 0,
            },
            "repositories": [a.to_dict() for a in assessments],
            "ranked_actions": [a.to_dict() for a in actions],
            "reuse_opportunities": [item.to_dict() for item in reuse],
            "knowledge_graph": graph,
            "regressions": [
                {
                    "repository": item.repository,
                    "previous_score": item.previous_score,
                    "current_score": item.current_score,
                    "delta": item.delta,
                }
                for item in regressions
            ],
            "snapshot": snapshot,
        }
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        _print_human(assessments, actions, regressions, reuse, bool(catalog))

    return 0


def run_validation_results(args: argparse.Namespace) -> int:
    plan_payload = json.loads(Path(args.plan).read_text(encoding="utf-8"))
    results_payload = json.loads(Path(args.results).read_text(encoding="utf-8"))

    validation_plan = plan_payload.get("validation_plan", plan_payload)
    if isinstance(validation_plan, dict):
        validation_plan = validation_plan.get("steps", [])
    results = results_payload.get("results", results_payload)

    if not isinstance(validation_plan, list):
        raise SystemExit("validation plan must be a JSON list or contain validation_plan")
    if not isinstance(results, list):
        raise SystemExit("validation results must be a JSON list or contain results")

    summary = summarize_validation_results(validation_plan, results)
    payload = {
        "schema_version": "production-os/validation-feedback/v1",
        "summary": summary.to_dict(),
        "promotion_allowed": summary.status == "passed",
        "results": results,
    }

    rendered = json.dumps(payload, indent=2, ensure_ascii=False)
    if args.output:
        destination = Path(args.output)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)

    return 0 if summary.status == "passed" else 3


def run_execution_feedback(args: argparse.Namespace) -> int:
    before = json.loads(Path(args.before).read_text(encoding="utf-8"))
    after = json.loads(Path(args.after).read_text(encoding="utf-8"))
    validation_payload = json.loads(Path(args.validation_summary).read_text(encoding="utf-8"))

    before_score = int(before.get("repositories", {}).get(args.repository, {}).get("score", 0))
    after_score = int(after.get("repositories", {}).get(args.repository, {}).get("score", 0))
    summary = validation_payload.get("summary", validation_payload)

    decision = decide_execution_outcome(before_score, after_score, summary)
    payload = {
        "schema_version": "production-os/execution-feedback/v2",
        "repository": args.repository,
        "before_score": before_score,
        "after_score": after_score,
        "decision": decision.to_dict(),
    }
    if args.runtime_state and args.task:
        state = RuntimeState(args.runtime_state)
        record = state.record_outcome(args.repository, args.task, decision.decision)
        payload["runtime_state"] = record.to_dict()

    if args.journal:
        journal = ExecutionJournal(args.journal)
        journal.append({
            "repository": args.repository,
            "task": args.task,
            "decision": decision.decision,
            "score_delta": decision.score_delta,
            "validation_status": decision.validation_status,
        })
        payload["journal"] = args.journal

    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0 if decision.decision in {"promote", "replan"} else 4


def run_trends(args: argparse.Namespace) -> int:
    snapshots = [
        json.loads(Path(path).read_text(encoding="utf-8"))
        for path in args.snapshots
    ]
    payload = {
        "schema_version": "production-os/trends/v1",
        "trends": [trend.to_dict() for trend in build_trends(snapshots)],
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


def run_heartbeat(args: argparse.Namespace) -> int:
    state = RuntimeState(args.runtime_state)
    record = state.heartbeat_lease(
        args.repository,
        args.task,
        owner=args.owner,
        minutes=args.minutes,
    )
    print(json.dumps({
        "schema_version": "production-os/lease-heartbeat/v1",
        "record": record.to_dict(),
    }, indent=2, ensure_ascii=False))
    return 0


def run_reconcile(args: argparse.Namespace) -> int:
    state = RuntimeState(args.runtime_state)
    actions = reconcile_runtime_state(state)
    print(json.dumps({
        "schema_version": "production-os/reconciliation/v1",
        "actions": [action.to_dict() for action in actions],
    }, indent=2, ensure_ascii=False))
    return 0


def run_dispatch(args: argparse.Namespace) -> int:
    handoff = json.loads(Path(args.handoff).read_text(encoding="utf-8"))
    state = RuntimeState(args.runtime_state)
    worker_registry = WorkerRegistry(args.worker_registry) if args.worker_registry else None
    rate_limit_store = RateLimitStore(args.rate_limit_state) if args.rate_limit_state else None
    approval_store = ApprovalStore(args.approvals) if args.approvals else None
    result = dispatch_handoff(
        handoff,
        args.queue_dir,
        state,
        lease_owner=args.owner,
        lease_minutes=args.lease_minutes,
        worker_registry=worker_registry,
        required_capabilities=args.required_capability,
        receipt_dir=args.receipt_dir,
        emergency_stop_path=args.emergency_stop,
        rate_limit_store=rate_limit_store,
        approval_store=approval_store,
    )
    print(json.dumps({
        "schema_version": "production-os/dispatch-result/v2",
        "result": result.to_dict(),
    }, indent=2, ensure_ascii=False))
    return 0

def run_github_reconcile(args: argparse.Namespace) -> int:
    payload = json.loads(Path(args.mapping).read_text(encoding="utf-8"))
    mappings = payload.get("mappings", payload)
    if not isinstance(mappings, list):
        raise SystemExit("mapping must be a JSON list or contain mappings")

    client = GitHubClient()
    state = RuntimeState(args.runtime_state)
    journal = ExecutionJournal(args.journal) if args.journal else None
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
        if decision in {"promote", "retry", "replan"}:
            updated = state.record_outcome(repository, task, decision).to_dict()

        row = {
            "repository": repository,
            "task": task,
            "github": work_state.to_dict(),
            "decision": decision,
            "runtime_state": updated,
        }
        results.append(row)

        if journal is not None:
            journal.append({
                "repository": repository,
                "task": task,
                "source": "github-reconcile",
                "decision": decision,
                "github": work_state.to_dict(),
            })

    print(json.dumps({
        "schema_version": "production-os/github-reconciliation/v1",
        "results": results,
    }, indent=2, ensure_ascii=False))
    return 0


def run_controller_command(args: argparse.Namespace) -> int:
    results = run_controller(
        cycles=args.cycles,
        interval_seconds=args.interval_seconds,
        owner=args.owner,
        runtime_state_path=args.runtime_state,
        queue_dir=args.queue_dir,
        snapshot_dir=args.snapshot_dir,
        metrics_path=args.metrics,
        health_path=args.health,
        journal_path=args.journal,
        observability_path=args.observability,
        github_mapping_path=args.github_mapping,
        worker_registry_path=args.worker_registry,
        receipt_dir=args.receipt_dir,
        claims_path=args.claims,
        dead_letter_dir=args.dead_letter_dir,
        emergency_stop_path=args.emergency_stop,
        rate_limit_path=args.rate_limit_state,
        approval_path=args.approvals,
        capacity=args.capacity,
        slots=args.slots,
        lease_owner=args.lease_owner,
        lease_minutes=args.lease_minutes,
    )
    print(json.dumps({
        "schema_version":"production-os/controller-run/v2",
        "cycles":len(results),
        "results":results,
    }, indent=2, ensure_ascii=False))
    return 0

def run_worker_register(args: argparse.Namespace) -> int:
    registry = WorkerRegistry(args.registry)
    worker = registry.register(
        args.worker_id,
        args.capability,
        args.max_concurrency,
    )
    print(json.dumps({
        "schema_version":"production-os/worker-register/v1",
        "worker":worker.to_dict(),
    }, indent=2, ensure_ascii=False))
    return 0


def run_worker_heartbeat(args: argparse.Namespace) -> int:
    registry = WorkerRegistry(args.registry)
    worker = registry.heartbeat(args.worker_id, active_tasks=args.active_tasks)
    print(json.dumps({
        "schema_version":"production-os/worker-heartbeat/v1",
        "worker":worker.to_dict(),
    }, indent=2, ensure_ascii=False))
    return 0


def run_worker_list(args: argparse.Namespace) -> int:
    registry = WorkerRegistry(args.registry)
    dead = registry.detect_dead(args.dead_timeout_seconds)
    print(json.dumps({
        "schema_version":"production-os/worker-list/v1",
        "workers":[w.to_dict() for w in registry.workers.values()],
        "dead":[w.worker_id for w in dead],
    }, indent=2, ensure_ascii=False))
    return 0




def run_job_claim(args: argparse.Namespace) -> int:
    payload = json.loads(Path(args.queue_file).read_text(encoding="utf-8"))
    handoff = payload.get("handoff", {})
    key = str(payload.get("idempotency_key", ""))
    repository = str(handoff.get("repository", ""))
    task = str(handoff.get("task", ""))
    assigned_worker = payload.get("worker_id")
    if assigned_worker and assigned_worker != args.worker_id:
        raise SystemExit("job assigned to a different worker")
    if not key or not repository or not task:
        raise SystemExit("invalid dispatch payload")

    store = ClaimStore(args.claims)
    claim = store.claim(
        key=key,
        worker_id=args.worker_id,
        repository=repository,
        task=task,
        ack_timeout_seconds=args.ack_timeout_seconds,
    )
    print(json.dumps({
        "schema_version":"production-os/job-claim/v1",
        "claim":claim.to_dict(),
    }, indent=2, ensure_ascii=False))
    return 0


def run_job_ack(args: argparse.Namespace) -> int:
    store = ClaimStore(args.claims)
    claim = store.ack(args.key, args.worker_id)
    print(json.dumps({
        "schema_version":"production-os/job-ack/v1",
        "claim":claim.to_dict(),
    }, indent=2, ensure_ascii=False))
    return 0


def run_job_complete(args: argparse.Namespace) -> int:
    store = ClaimStore(args.claims)
    claim = store.complete(args.key, args.worker_id)

    registry = WorkerRegistry(args.registry)
    worker = registry.workers.get(args.worker_id)
    if worker is not None:
        worker = registry.adjust_active_tasks(args.worker_id, -1)

    state = RuntimeState(args.runtime_state)
    record = state.get(claim.repository, claim.task)
    if record.lease_owner == args.worker_id:
        state.release_lease(claim.repository, claim.task)

    print(json.dumps({
        "schema_version":"production-os/job-complete/v1",
        "claim":claim.to_dict(),
        "worker":worker.to_dict() if worker else None,
        "runtime":state.get(claim.repository, claim.task).to_dict(),
    }, indent=2, ensure_ascii=False))
    return 0


def run_delivery_recover(args: argparse.Namespace) -> int:
    claims = ClaimStore(args.claims)
    registry = WorkerRegistry(args.registry)
    state = RuntimeState(args.runtime_state)
    rows = recover_unacked_jobs(
        claims=claims,
        runtime_state=state,
        workers=registry,
        queue_dir=args.queue_dir,
        dead_letter_dir=args.dead_letter_dir,
        emergency_stop_path=args.emergency_stop,
        rate_limit_path=args.rate_limit_state,
    )
    print(json.dumps({
        "schema_version":"production-os/delivery-recovery/v1",
        "recovered":rows,
    }, indent=2, ensure_ascii=False))
    return 0



def run_preempt_request(args: argparse.Namespace) -> int:
    state = RuntimeState(args.runtime_state)
    record = request_preemption(state, args.repository, args.task)
    print(json.dumps({
        "schema_version":"production-os/preempt-request/v1",
        "record":record,
    }, indent=2, ensure_ascii=False))
    return 0


def run_preempt_checkpoint(args: argparse.Namespace) -> int:
    state = RuntimeState(args.runtime_state)
    registry = WorkerRegistry(args.registry)
    record = confirm_checkpoint_and_release(
        state,
        registry,
        args.repository,
        args.task,
        args.worker_id,
        args.checkpoint_ref,
    )
    print(json.dumps({
        "schema_version":"production-os/preempt-checkpoint/v1",
        "record":record,
    }, indent=2, ensure_ascii=False))
    return 0



def run_emergency_stop(args: argparse.Namespace) -> int:
    payload = set_emergency_stop(args.state, reason=args.reason)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


def run_emergency_resume(args: argparse.Namespace) -> int:
    payload = clear_emergency_stop(args.state)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


def run_audit_verify(args: argparse.Namespace) -> int:
    payload = verify_hash_chain(args.journal)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0 if payload.get("valid") else 5


def run_backup(args: argparse.Namespace) -> int:
    payload = create_backup(args.paths, args.destination_dir)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


def run_restore(args: argparse.Namespace) -> int:
    payload = restore_backup(args.manifest, verify_only=args.verify_only)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0



def run_approve(args: argparse.Namespace) -> int:
    store = ApprovalStore(args.store)
    item = store.set(
        args.key,
        approved=True,
        approved_by=args.approved_by,
        reason=args.reason,
    )
    print(json.dumps({
        "schema_version":"production-os/approval/v1",
        "approval":item.to_dict(),
    }, indent=2, ensure_ascii=False))
    return 0


def run_revoke(args: argparse.Namespace) -> int:
    store = ApprovalStore(args.store)
    item = store.set(
        args.key,
        approved=False,
        approved_by=args.approved_by,
        reason=args.reason,
    )
    print(json.dumps({
        "schema_version":"production-os/approval/v1",
        "approval":item.to_dict(),
    }, indent=2, ensure_ascii=False))
    return 0


def run_migrate_state(args: argparse.Namespace) -> int:
    payload = migrate_state_file(args.path)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0

def run_health_server(args: argparse.Namespace) -> int:
    serve_health(args.health, host=args.host, port=args.port)
    return 0


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    if args.command == "scan":
        return run_scan(args)
    if args.command == "validation-results":
        return run_validation_results(args)
    if args.command == "execution-feedback":
        return run_execution_feedback(args)
    if args.command == "trends":
        return run_trends(args)
    if args.command == "heartbeat":
        return run_heartbeat(args)
    if args.command == "reconcile":
        return run_reconcile(args)
    if args.command == "dispatch":
        return run_dispatch(args)
    if args.command == "github-reconcile":
        return run_github_reconcile(args)
    if args.command == "controller":
        return run_controller_command(args)
    if args.command == "health-server":
        return run_health_server(args)
    if args.command == "worker-register":
        return run_worker_register(args)
    if args.command == "worker-heartbeat":
        return run_worker_heartbeat(args)
    if args.command == "worker-list":
        return run_worker_list(args)
    if args.command == "job-claim":
        return run_job_claim(args)
    if args.command == "job-ack":
        return run_job_ack(args)
    if args.command == "job-complete":
        return run_job_complete(args)
    if args.command == "delivery-recover":
        return run_delivery_recover(args)
    if args.command == "preempt-request":
        return run_preempt_request(args)
    if args.command == "preempt-checkpoint":
        return run_preempt_checkpoint(args)
    if args.command == "emergency-stop":
        return run_emergency_stop(args)
    if args.command == "emergency-resume":
        return run_emergency_resume(args)
    if args.command == "audit-verify":
        return run_audit_verify(args)
    if args.command == "backup":
        return run_backup(args)
    if args.command == "restore":
        return run_restore(args)
    if args.command == "approve":
        return run_approve(args)
    if args.command == "revoke":
        return run_revoke(args)
    if args.command == "migrate-state":
        return run_migrate_state(args)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
