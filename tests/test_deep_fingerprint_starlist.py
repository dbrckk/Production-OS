import json
from unittest.mock import patch

from production_os.deep_fingerprint import analyze_source_evidence
from production_os.models import ActionCandidate, RepoEvidence
from production_os.starlist import rank_website_catalog, suggest_external_references


def test_deep_fingerprint_detects_real_dependencies():
    evidence = RepoEvidence(
        name="app",
        full_name="owner/app",
        html_url="https://github.com/owner/app",
        source_documents={
            "build.gradle.kts": 'implementation("com.android.billingclient:billing:7.1.1")',
            "pyproject.toml": 'dependencies = ["pytest>=8"]',
        },
    )
    signals = analyze_source_evidence(evidence)
    values = {(signal.kind, signal.value) for signal in signals}
    assert ("android-library", "play-billing") in values
    assert ("python-library", "pytest") in values


def test_starlist_catalog_is_ranked_by_score_and_match(capsys):
    catalog = {
        "repositories": [
            {
                "repo": "audit/example",
                "score": 9.9,
                "tier": "audit",
                "capabilities": ["backtesting"],
            },
            {
                "repo": "archived/example",
                "score": 9.9,
                "tier": "core",
                "capabilities": ["backtesting"],
                "github": {"archived": True},
            },
            {
                "repo": "disabled/example",
                "score": 9.9,
                "tier": "core",
                "capabilities": ["backtesting"],
                "github": {"disabled": True},
            },
            {
                "repo": "legacy/example",
                "score": 9.9,
                "tier": "core",
                "capabilities": ["backtesting"],
                "lifecycle": "legacy",
            },
            {
                "repo": "low/example",
                "score": 8.1,
                "tier": "specialized",
                "domain": "trading",
                "capabilities": ["backtesting"],
                "bestFor": ["quant backtesting"],
            },
            {
                "repo": "high/example",
                "score": 9.7,
                "tier": "core",
                "domain": "trading",
                "capabilities": ["backtesting"],
                "bestFor": ["quant trading backtesting"],
            },
        ]
    }
    refs = suggest_external_references("backtesting", catalog)
    assert [ref.repository for ref in refs] == ["high/example", "low/example"]
    assert refs[0].star_score == 9.7

    # Catalog capability IDs contain hyphens; they must be recognized without
    # depending on free-text descriptions or an exact repository name.
    tool_catalog = {
        "repositories": [
            {
                "repo": "BerriAI/litellm",
                "score": 9.7,
                "tier": "core",
                "capabilities": ["model-routing", "llm-gateway"],
            },
        ],
    }
    assert [
        ref.repository for ref in suggest_external_references("model-routing", tool_catalog)
    ] == ["BerriAI/litellm"]

    # "avoidWhen" documents where NOT to use a repository. It must never
    # count as positive capability evidence when ranking free tools.
    defensive_catalog = {
        "repositories": [
            {
                "repo": "desktop/only",
                "score": 9.9,
                "tier": "core",
                "bestFor": ["desktop tooling"],
                "avoidWhen": ["android device emulator testing"],
            },
            {
                "repo": "broken/score",
                "score": "not-a-number",
                "capabilities": ["android-device-qa"],
            },
            {
                "repo": "nan/score",
                "score": "NaN",
                "capabilities": ["android-device-qa"],
            },
            {
                "repo": "infinity/score",
                "score": "Infinity",
                "capabilities": ["android-device-qa"],
            },
            {
                "repo": "valid/android-qa",
                "score": 9.3,
                "tier": "core",
                "capabilities": ["android-device-qa"],
            },
        ]
    }
    assert [
        ref.repository
        for ref in suggest_external_references("android-device-qa", defensive_catalog)
    ] == ["valid/android-qa"]
    assert suggest_external_references(
        "android-device-qa", {"repositories": None}
    ) == []

    # Very short identifiers must not match inside unrelated words:
    # "ci" was previously found within the "specialized" tier itself.
    ci_catalog = {
        "repositories": [
            {
                "repo": "desktop/productivity",
                "score": 9.9,
                "tier": "specialized",
                "bestFor": ["desktop productivity"],
            },
            {
                "repo": "tools/build",
                "score": 9.1,
                "tier": "specialized",
                "capabilities": ["github-actions-ci"],
            },
        ]
    }
    assert [
        ref.repository
        for ref in suggest_external_references("github-actions-ci", ci_catalog)
    ] == ["tools/build"]


    # The independent websites.json index is inspected without treating
    # websites (including agent-skill directories) as installable components.
    websites = {
        "websites": [
            {
                "name": "Skill Issue",
                "url": "https://skill-issue.in/",
                "tags": ["agent", "automation", "workflow", "coding"],
                "bestFor": ["Coding agent workflows"],
                "reuse": "reference-only",
                "caution": "Review upstream licenses and instructions.",
            },
            {
                "name": "Motion Gallery",
                "url": "https://60fps.design/",
                "tags": ["mobile", "motion"],
                "bestFor": ["Mobile UI animations"],
            },
            {
                "name": "Unsafe Scheme",
                "url": "http://example.com/agent/automation",
                "tags": ["agent", "automation"],
            },
            {
                "name": "Duplicate",
                "url": "https://skill-issue.in",
                "tags": ["agent", "automation"],
            },
        ]
    }
    references = rank_website_catalog("agent coding automation", websites)
    assert [item["url"] for item in references] == ["https://skill-issue.in/"]
    assert references[0]["integrationEligible"] is False
    assert references[0]["reviewRequired"] is True
    assert references[0]["reuse"] == "reference-only"
    assert "agent" in references[0]["match_terms"]
    assert rank_website_catalog("mobile QA release", websites) == []
    assert rank_website_catalog("", websites) == []
    assert rank_website_catalog("agent coding", websites, limit=0) == []

    from production_os.cli import _handoff, _parse_args

    scan_args = _parse_args([
        "scan", "--owner", "dbrckk", "--star-list-websites-path",
        "websites.json",
    ])
    assert scan_args.star_list_websites_path == "websites.json"
    action = ActionCandidate(
        repository="dbrckk/Jumpy",
        task="Improve agent coding automation",
        rationale="Support coding agent workflows",
        acceptance_criteria=[],
        evidence=[],
        impact=5,
        urgency=5,
        risk_reduction=5,
        release_proximity=5,
        effort=3,
    )
    handoff = _handoff(action, [], catalog, websites)
    assert handoff["external_catalog_coverage"] == {
        "github_entries": 6,
        "website_entries": 4,
    }
    assert [item["url"] for item in handoff["external_website_candidates"]] == [
        "https://skill-issue.in/"
    ]
    assert handoff["external_website_candidates"][0]["integrationEligible"] is False


    # Exercise the real scan/report wiring with the external GitHub boundary
    # stubbed: both independent feeds must load, and each action is evaluated.
    from production_os.cli import run_scan

    with (
        patch("production_os.cli.GitHubClient") as github,
        patch("production_os.cli._rank_actions", return_value=[action]),
    ):
        github.return_value.list_repositories.return_value = []
        github.return_value.read_json_file.side_effect = [catalog, websites]
        assert run_scan(scan_args) == 0
        assert github.return_value.read_json_file.call_count == 2
    scan_output = json.loads(capsys.readouterr().out)
    assert scan_output["star_list"]["website_count"] == 4
    assert scan_output["star_list"]["websites_loaded"] is True
    assert scan_output["website_reference_matches"][0]["repository"] == "dbrckk/Jumpy"
    assert scan_output["website_reference_matches"][0]["references"][0]["url"] == (
        "https://skill-issue.in/"
    )

    no_feeds = _parse_args(["scan", "--owner", "dbrckk", "--no-star-list", "--json"])
    with (
        patch("production_os.cli.GitHubClient") as github,
        patch("production_os.cli._rank_actions", return_value=[action]),
    ):
        github.return_value.list_repositories.return_value = []
        assert run_scan(no_feeds) == 0
        github.return_value.read_json_file.assert_not_called()
    no_feed_output = json.loads(capsys.readouterr().out)
    assert no_feed_output["star_list"]["website_count"] == 0
    assert no_feed_output["website_reference_matches"] == []
