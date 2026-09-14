from __future__ import annotations

import argparse
import json
import sys
from typing import Iterable

from .github_client import GitHubAPIError, GitHubClient
from .graph import build_knowledge_graph
from .history import build_snapshot, detect_regressions, load_snapshot, save_snapshot
from .models import ActionCandidate, RepoAssessment
from .reuse import detect_reuse
from .scoring import assess_repository
from .starlist import suggest_external_references


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
        "schema_version": "production-os/task-handoff/v8",
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

    if args.handoff:
        payload = _handoff(actions[0], reuse, catalog) if actions else {
            "schema_version": "production-os/task-handoff/v8",
            "status": "no_action",
        }
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    elif args.json:
        payload = {
            "schema_version": "production-os/portfolio/v9",
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


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    if args.command == "scan":
        return run_scan(args)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
