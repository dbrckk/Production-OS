from argparse import Namespace
from unittest.mock import patch

import pytest

from production_os.asset_forge import probe_asset_forge_remote_dispatch
from production_os.cli import _parse_args, run_asset_forge_batch
from production_os.github_client import GitHubAPIError, GitHubClient


class FakeProbeClient(GitHubClient):
    def __init__(self, outcome, *, token="test-token"):
        super().__init__(token=token)
        self.outcome = outcome
        self.calls = []

    def _request(self, method, path, payload=None):
        self.calls.append((method, path, payload))
        if isinstance(self.outcome, Exception):
            raise self.outcome
        return self.outcome


def test_workflow_dispatch_probe_treats_422_as_authorized_without_run():
    client = FakeProbeClient(
        GitHubAPIError('GitHub API 422: {"message":"Invalid request"}')
    )

    assert client.can_dispatch_workflow(
        "dbrckk/asset-forge",
        "production-os-batch.yml",
    ) is True
    method, path, payload = client.calls[0]
    assert method == "POST"
    assert path.endswith(
        "/repos/dbrckk/asset-forge/actions/workflows/"
        "production-os-batch.yml/dispatches"
    )
    assert payload == {"ref": "", "inputs": {}}


@pytest.mark.parametrize("code", [401, 403, 404])
def test_workflow_dispatch_probe_fails_closed_without_permission(code):
    client = FakeProbeClient(
        GitHubAPIError(f"GitHub API {code}: denied")
    )

    assert client.can_dispatch_workflow(
        "dbrckk/asset-forge",
        "production-os-batch.yml",
    ) is False


def test_workflow_dispatch_probe_requires_token():
    client = FakeProbeClient(None, token="")

    assert client.can_dispatch_workflow(
        "dbrckk/asset-forge",
        "production-os-batch.yml",
    ) is False
    assert client.calls == []


def test_workflow_dispatch_probe_propagates_unexpected_api_failure():
    client = FakeProbeClient(
        GitHubAPIError("GitHub API 500: unavailable")
    )

    with pytest.raises(GitHubAPIError):
        client.can_dispatch_workflow(
            "dbrckk/asset-forge",
            "production-os-batch.yml",
        )


def test_asset_forge_remote_probe_has_stable_contract():
    client = FakeProbeClient(
        GitHubAPIError('GitHub API 422: {"message":"Invalid request"}')
    )

    result = probe_asset_forge_remote_dispatch(client=client)

    assert result == {
        "schema_version": "production-os/asset-forge-remote-probe/v1",
        "repository": "dbrckk/asset-forge",
        "workflow": "production-os-batch.yml",
        "ready": True,
    }


def test_asset_forge_remote_probe_uses_dedicated_dispatch_token(monkeypatch):
    seen = []

    class DispatchClient:
        def __init__(self, token=None):
            seen.append(token)

        def can_dispatch_workflow(self, repository, workflow):
            return True

    monkeypatch.setenv("GITHUB_TOKEN", "repository-token")
    monkeypatch.setenv("ASSET_FORGE_GITHUB_TOKEN", "dispatch-token")
    monkeypatch.setattr("production_os.asset_forge.GitHubClient", DispatchClient)

    assert probe_asset_forge_remote_dispatch()["ready"] is True
    assert seen == ["dispatch-token"]


def test_asset_forge_batch_probe_does_not_require_spec():
    args = _parse_args(["asset-forge-batch", "--probe"])

    assert args.probe is True
    assert args.spec is None


def test_asset_forge_batch_probe_exit_code_reflects_readiness():
    args = Namespace(probe=True, result_file=None, spec=None)

    with patch(
        "production_os.cli.probe_asset_forge_remote_dispatch",
        return_value={
            "schema_version": "production-os/asset-forge-remote-probe/v1",
            "ready": True,
        },
    ):
        assert run_asset_forge_batch(args) == 0

    with patch(
        "production_os.cli.probe_asset_forge_remote_dispatch",
        return_value={
            "schema_version": "production-os/asset-forge-remote-probe/v1",
            "ready": False,
        },
    ):
        assert run_asset_forge_batch(args) == 1
