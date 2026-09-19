import unittest

from production_os.github_client import GitHubClient


class _Client(GitHubClient):
    def __init__(self, token, pages):
        super().__init__(token=token)
        self.pages = list(pages)
        self.paths = []

    def _get(self, path):
        self.paths.append(path)
        if not self.pages:
            return []
        return self.pages.pop(0)


class GitHubRepositoryPickerTests(unittest.TestCase):
    def test_authenticated_picker_uses_accessible_repository_endpoint(self):
        client = _Client(
            "token",
            [[
                {
                    "name": "private-a",
                    "full_name": "dbrckk/private-a",
                    "private": True,
                    "owner": {"login": "dbrckk"},
                },
                {
                    "name": "shared",
                    "full_name": "other/shared",
                    "private": True,
                    "owner": {"login": "other"},
                },
            ]],
        )

        rows = client.list_accessible_repositories("dbrckk")

        self.assertEqual([row["full_name"] for row in rows], ["dbrckk/private-a"])
        self.assertTrue(rows[0]["private"])
        self.assertTrue(client.paths[0].startswith("/user/repos?"))
        self.assertIn("visibility=all", client.paths[0])
        self.assertIn("affiliation=owner%2Ccollaborator%2Corganization_member", client.paths[0])

    def test_unauthenticated_picker_falls_back_to_public_owner_repositories(self):
        client = _Client(
            None,
            [[
                {
                    "name": "public-a",
                    "full_name": "dbrckk/public-a",
                    "private": False,
                    "owner": {"login": "dbrckk"},
                }
            ]],
        )

        rows = client.list_accessible_repositories("dbrckk")

        self.assertEqual([row["full_name"] for row in rows], ["dbrckk/public-a"])
        self.assertTrue(client.paths[0].startswith("/users/dbrckk/repos?"))


if __name__ == "__main__":
    unittest.main()
