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


def test_starlist_reference_filtering():
    refs = suggest_external_references(
        "backtesting",
        {"QuantConnect/Lean", "other/repo"},
    )
    assert [ref.repository for ref in refs] == ["QuantConnect/Lean"]
