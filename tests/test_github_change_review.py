from production_os.github_change_review import review_changed_paths


def test_review_changed_paths_allows_ordinary_source_changes():
    review = review_changed_paths([
        "src/production_os/dashboard_ui.py",
        "tests/test_dashboard_ui_v3.py",
    ])

    assert review.requires_human_review is False
    assert review.blockers == ()
    assert review.sensitive_files == ()


def test_review_changed_paths_flags_security_runtime_and_schema_surfaces():
    review = review_changed_paths([
        ".github/workflows/ci.yml",
        "src/production_os/api_auth.py",
        "src/production_os/workflow_engine.py",
        "migrations/0042_add_jobs.sql",
    ])

    assert review.requires_human_review is True
    assert "sensitive-files-changed" in review.blockers
    assert set(review.categories) >= {
        "security-or-deployment",
        "execution-runtime",
        "data-or-schema",
    }
    assert "src/production_os/api_auth.py" in review.sensitive_files


def test_review_changed_paths_flags_credential_material():
    review = review_changed_paths([
        "config/.env.production",
        "certs/signing.key",
    ])

    assert review.requires_human_review is True
    assert "credential-surface-changed" in review.blockers
    assert "credential-material-file" in review.blockers
    assert "credential-surface" in review.categories


def test_review_changed_paths_fails_closed_when_file_list_unavailable():
    review = review_changed_paths([])

    assert review.requires_human_review is True
    assert review.blockers == ("changed-files-unavailable",)
