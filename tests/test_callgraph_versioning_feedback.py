from production_os.callgraph import build_call_import_graph
from production_os.feedback import summarize_validation_results
from production_os.models import RepoAssessment, RepoEvidence, ScoreBreakdown
from production_os.versioning import compare_dependency_versions


def assessment(name, docs, components=None):
    return RepoAssessment(
        evidence=RepoEvidence(
            name=name,
            full_name=f"owner/{name}",
            html_url=f"https://github.com/owner/{name}",
            source_documents=docs,
        ),
        score=ScoreBreakdown(0,0,0,0,0,0,0,0,0),
        actions=[],
        components=components or [],
    )


def test_version_compatibility_detects_major_mismatch():
    src = assessment("src", {"build.gradle.kts": 'implementation("com.example:lib:2.1.0")'})
    dst = assessment("dst", {"build.gradle.kts": 'implementation("com.example:lib:1.9.0")'})
    rows = compare_dependency_versions(src, dst)
    assert rows[0].status == "major-version-mismatch"


def test_feedback_blocks_required_failure():
    plan = [
        {"kind": "compile", "required": True},
        {"kind": "ci", "required": True},
    ]
    result = summarize_validation_results(
        plan,
        [{"kind": "compile", "status": "passed"}, {"kind": "ci", "status": "failed"}],
    )
    assert result.status == "blocked"
    assert result.blocking_failures == ("ci",)
