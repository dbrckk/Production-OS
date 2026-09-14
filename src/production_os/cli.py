from __future__ import annotations

import argparse
import json
import sys
from typing import Iterable

from .github_client import GitHubAPIError, GitHubClient
from .history import build_snapshot, detect_regressions, load_snapshot, save_snapshot
from .models import ActionCandidate, RepoAssessment
from .reuse import detect_reuse
from .scoring import assess_repository


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
    scan.add_argument("--include-forks", action="store_true")
    scan.add_argument("--include-archived", action="store_true")

    return parser.parse_args(argv)


def _rank_actions(assessments: Iterable[RepoAssessment]) -> list[ActionCandidate]:
    actions = [action for assessment in assessments for action in assessment.actions]
    return sorted(actions, key=lambda action: action.priority, reverse=True)


def _handoff(action: ActionCandidate) -> dict:
    return {
        "schema_version": "production-os/task-handoff/v1",
        "source": "Production-OS",
        "executor": "ai-dev-server",
        "repository": action.repository,
        "task": action.task,
        "rationale": action.rationale,
        "acceptance_criteria": action.acceptance_criteria,
        "trigger_evidence": action.evidence,
        "priority": action.priority,
        "constraints": {
            "preserve_existing_behavior": True,
            "verify_before_completion": True,
            "no_secret_material_in_workspace": True,
        },
    }


def _print_human(
    assessments: list[RepoAssessment],
    actions: list[ActionCandidate],
    regressions: list,
    reuse: list,
) -> None:
    print("Production-OS portfolio assessment")
    print("=" * 34)
    for assessment in sorted(assessments, key=lambda item: item.score.total, reverse=True):
        e = assessment.evidence
        print(
            f"{e.full_name:<40} {assessment.score.total:>3}/100 "
            f"[{assessment.profile}]"
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
        for item in reuse[:5]:
            print(
                f"- {item.target} <- {item.source}: "
                f"{item.capability} ({item.confidence:.0%})"
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

    print()
    print("Top portfolio actions:")
    for idx, action in enumerate(actions[:10], start=1):
        print(f"{idx:>2}. {action.priority:>6}  {action.repository} — {action.task}")


def run_scan(args: argparse.Namespace) -> int:
    client = GitHubClient()
    try:
        repos = client.list_repositories(args.owner)
    except GitHubAPIError as exc:
        print(str(exc), file=sys.stderr)
        return 2

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
    snapshot = build_snapshot(args.owner, assessments)
    previous = load_snapshot(args.compare) if args.compare else None
    regressions = detect_regressions(previous, snapshot)

    if args.snapshot:
        save_snapshot(snapshot, args.snapshot)

    if args.handoff:
        payload = _handoff(actions[0]) if actions else {
            "schema_version": "production-os/task-handoff/v1",
            "status": "no_action",
        }
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    elif args.json:
        payload = {
            "schema_version": "production-os/portfolio/v2",
            "owner": args.owner,
            "repositories": [a.to_dict() for a in assessments],
            "ranked_actions": [a.to_dict() for a in actions],
            "reuse_opportunities": [item.to_dict() for item in reuse],
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
        _print_human(assessments, actions, regressions, reuse)

    return 0


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    if args.command == "scan":
        return run_scan(args)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
