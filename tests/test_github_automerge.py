import pytest

from production_os.github_client import GitHubAPIError, GitHubClient


class Client(GitHubClient):
    def __init__(self, token="token"):
        super().__init__(token=token)
        self.calls = []

    def _request(self, method, path, payload=None):
        self.calls.append((method, path, payload))
        return {
            "sha":"b" * 40,
            "merged":True,
            "message":"Pull Request successfully merged",
        }


def test_merge_pull_request_is_pinned_to_observed_head_sha():
    client = Client()

    result = client.merge_pull_request(
        "owner/repo",
        42,
        head_sha="a" * 40,
        method="squash",
        commit_title="Production-OS promotion",
    )

    assert result["merged"] is True
    assert client.calls == [(
        "PUT",
        "/repos/owner/repo/pulls/42/merge",
        {
            "sha":"a" * 40,
            "merge_method":"squash",
            "commit_title":"Production-OS promotion",
        },
    )]


def test_merge_pull_request_requires_token():
    client = Client(token=None)
    client.token = None

    with pytest.raises(
        GitHubAPIError,
        match="GITHUB_TOKEN is required",
    ):
        client.merge_pull_request(
            "owner/repo",
            42,
            head_sha="a" * 40,
        )


@pytest.mark.parametrize("sha", ["", "abc1234", "g" * 40])
def test_merge_pull_request_rejects_unpinned_or_invalid_sha(sha):
    client = Client()

    with pytest.raises(ValueError, match="full commit sha"):
        client.merge_pull_request(
            "owner/repo",
            42,
            head_sha=sha,
        )


def test_merge_pull_request_rejects_unknown_method():
    client = Client()

    with pytest.raises(ValueError, match="unsupported merge method"):
        client.merge_pull_request(
            "owner/repo",
            42,
            head_sha="a" * 40,
            method="force",
        )
