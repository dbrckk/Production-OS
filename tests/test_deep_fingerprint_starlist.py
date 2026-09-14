from production_os.deep_fingerprint import analyze_source_evidence
from production_os.models import RepoEvidence
from production_os.starlist import suggest_external_references


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


def test_starlist_catalog_is_ranked_by_score_and_match():
    catalog = {
        "repositories": [
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
