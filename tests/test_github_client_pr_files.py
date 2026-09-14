from production_os.github_client import GitHubAPIError, GitHubClient


class FakeGitHubClient(GitHubClient):
    def __init__(self, pages):
        super().__init__(token="test")
        self.pages = pages
        self.calls = []

    def _get(self, path):
        self.calls.append(path)
        page = int(path.rsplit("page=", 1)[1])
        value = self.pages[page - 1]
        if isinstance(value, Exception):
            raise value
        return value


def test_list_pull_request_files_collects_and_deduplicates():
    first = [
        {"filename":f"src/file-{index}.py"}
        for index in range(100)
    ]
    second = [
        {"filename":"src/file-1.py"},
        {"filename":"tests/test_new.py"},
    ]
    client = FakeGitHubClient([first, second])

    files = client.list_pull_request_files("o/a", 7)

    assert len(files) == 101
    assert "tests/test_new.py" in files
    assert len(client.calls) == 2
    assert client.calls[0].endswith("per_page=100&page=1")
    assert client.calls[1].endswith("per_page=100&page=2")


def test_list_pull_request_files_ignores_empty_rows():
    client = FakeGitHubClient([[
        {"filename":"src/a.py"},
        {"filename":""},
        {},
        None,
    ]])

    assert client.list_pull_request_files("o/a", 1) == ["src/a.py"]


def test_list_pull_request_files_fails_closed_on_api_error():
    client = FakeGitHubClient([
        GitHubAPIError("GitHub API unavailable")
    ])

    try:
        client.list_pull_request_files("o/a", 1)
    except GitHubAPIError:
        pass
    else:
        raise AssertionError("expected GitHubAPIError")


def test_list_pull_request_files_rejects_invalid_payload():
    client = FakeGitHubClient([{"files":[]}])

    try:
        client.list_pull_request_files("o/a", 1)
    except GitHubAPIError as exc:
        assert "not a list" in str(exc)
    else:
        raise AssertionError("expected GitHubAPIError")
