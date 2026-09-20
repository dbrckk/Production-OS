from production_os.github_client import GitHubClient


class FakeWriteClient(GitHubClient):
    def __init__(self, existing=None):
        super().__init__(token="test-token")
        self.existing = existing
        self.requests = []

    def _get(self, path):
        if self.existing is None:
            from production_os.github_client import GitHubAPIError
            raise GitHubAPIError("GitHub API 404: not found")
        return self.existing

    def _request(self, method, path, payload=None):
        self.requests.append((method, path, payload))
        return {"content": {"path": path}, "commit": {"sha": "abc"}}


def test_put_file_creates_new_content_without_sha():
    client = FakeWriteClient()
    result = client.put_file(
        "dbrckk/deadline-zero",
        "assets/art/icon.svg",
        b"<svg/>",
        message="assets: deliver icon",
        branch="main",
    )
    method, path, payload = client.requests[0]
    assert method == "PUT"
    assert path.endswith("/repos/dbrckk/deadline-zero/contents/assets/art/icon.svg")
    assert payload["branch"] == "main"
    assert payload["message"] == "assets: deliver icon"
    assert "sha" not in payload
    assert payload["content"] == "PHN2Zy8+"
    assert result["commit"]["sha"] == "abc"


def test_put_file_updates_existing_content_with_sha():
    client = FakeWriteClient({"sha": "existing-sha"})
    client.put_file(
        "dbrckk/deadline-zero",
        "assets/art/icon.svg",
        b"<svg/>",
        message="assets: update icon",
        branch="main",
    )
    payload = client.requests[0][2]
    assert payload["sha"] == "existing-sha"
