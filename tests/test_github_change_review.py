from production_os.github_change_review import (
    review_changed_files,
    review_changed_paths,
)


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



def test_review_changed_files_flags_private_key_material_on_added_line():
    review = review_changed_files([{
        "filename":"src/config.py",
        "status":"modified",
        "changes":3,
        "patch":"@@ -1 +1,2 @@\n value = 1\n+KEY='-----BEGIN PRIVATE KEY-----'",
    }])

    assert review.requires_human_review is True
    assert "private-key-material-added" in review.blockers
    assert "credential-surface" in review.categories
    assert "src/config.py" in review.sensitive_files


def test_review_changed_files_flags_dangerous_shell_and_destructive_sql():
    review = review_changed_files([
        {
            "filename":"src/worker.py",
            "status":"modified",
            "changes":4,
            "patch":"@@ -1 +1,3 @@\n+subprocess.run(cmd, shell=True)\n+query='DROP TABLE users'",
        },
    ])

    assert "dangerous-shell-execution-added" in review.blockers
    assert "destructive-sql-added" in review.blockers
    assert "dangerous-execution" in review.categories
    assert "destructive-data" in review.categories


def test_review_changed_files_flags_tls_verification_disable():
    review = review_changed_files([{
        "filename":"src/http_client.py",
        "status":"modified",
        "changes":1,
        "patch":"@@ -10 +10 @@\n-request(url)\n+request(url, verify=False)",
    }])

    assert "tls-verification-disabled" in review.blockers
    assert "auth-or-transport-bypass" in review.categories


def test_review_changed_files_ignores_risky_text_when_removed():
    review = review_changed_files([{
        "filename":"src/worker.py",
        "status":"modified",
        "changes":2,
        "patch":"@@ -1 +1 @@\n-subprocess.run(cmd, shell=True)\n+subprocess.run(cmd)",
    }])

    assert review.requires_human_review is False
    assert review.blockers == ()


def test_review_changed_files_blocks_large_unavailable_text_diff():
    review = review_changed_files([{
        "filename":"src/generated_logic.py",
        "status":"modified",
        "changes":800,
        "patch":None,
    }])

    assert review.requires_human_review is True
    assert "diff-content-unavailable" in review.blockers
    assert "unreviewable-large-diff" in review.categories


def test_review_changed_files_allows_unavailable_binary_patch():
    review = review_changed_files([{
        "filename":"assets/screenshot.png",
        "status":"modified",
        "changes":2000,
        "patch":None,
    }])

    assert review.requires_human_review is False
