from __future__ import annotations

import inspect

import pytest

from production_os.cli import _parse_args
from production_os.controller import run_control_cycle


def _cycle_kwargs(tmp_path):
    return {
        "owner":"owner",
        "runtime_state_path":str(tmp_path / "runtime.json"),
        "queue_dir":str(tmp_path / "queue"),
        "snapshot_dir":str(tmp_path / "snapshots"),
        "metrics_path":str(tmp_path / "metrics.json"),
        "health_path":str(tmp_path / "health.json"),
        "journal_path":str(tmp_path / "journal.jsonl"),
    }


def test_controller_defaults_execution_mode_to_legacy_during_migration():
    signature = inspect.signature(run_control_cycle)

    assert signature.parameters["execution_mode"].default == "legacy"
    assert signature.parameters["project_token_budget"].default == 12000


def test_controller_cli_accepts_managed_execution_mode():
    args = _parse_args([
        "controller",
        "--owner", "owner",
        "--queue-dir", "/tmp/queue",
        "--snapshot-dir", "/tmp/snapshots",
        "--metrics", "/tmp/metrics.json",
        "--health", "/tmp/health.json",
        "--journal", "/tmp/journal.jsonl",
        "--execution-mode", "managed",
        "--project-token-budget", "24000",
    ])

    assert args.execution_mode == "managed"
    assert args.project_token_budget == 24000


def test_controller_managed_mode_requires_database_path(tmp_path):
    with pytest.raises(
        ValueError,
        match="managed execution mode requires database_path",
    ):
        run_control_cycle(
            **_cycle_kwargs(tmp_path),
            execution_mode="managed",
        )


def test_controller_rejects_unknown_execution_mode(tmp_path):
    with pytest.raises(ValueError, match="execution_mode"):
        run_control_cycle(
            **_cycle_kwargs(tmp_path),
            execution_mode="both",
        )


def test_controller_rejects_nonpositive_project_token_budget(tmp_path):
    with pytest.raises(ValueError, match="project_token_budget"):
        run_control_cycle(
            **_cycle_kwargs(tmp_path),
            project_token_budget=0,
        )
