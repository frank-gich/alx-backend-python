#!/usr/bin/env python3
"""
Unit and Integration tests for GithubOrgClient
"""

import unittest
from unittest.mock import patch, PropertyMock, Mock
from parameterized import parameterized, parameterized_class
from client import GithubOrgClient


class TestGithubOrgClient(unittest.TestCase):
    """Unit tests for GithubOrgClient"""

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch('client.get_json')
    def test_org(self, org_name, mock_get_json):
        expected_url = f"https://api.github.com/orgs/{org_name}"
        mock_get_json.return_value = {"login": org_name}
        client = GithubOrgClient(org_name)
        self.assertEqual(client.org, {"login": org_name})
        mock_get_json.assert_called_once_with(expected_url)

    def test_public_repos_url(self):
        """Test _public_repos_url property"""
        with patch.object(GithubOrgClient, "org", new_callable=PropertyMock) as mock_org:
            mock_org.return_value = {"repos_url": "http://some_url"}
            client = GithubOrgClient("test")
            self.assertEqual(client._public_repos_url, "http://some_url")

    @patch('client.get_json')
    def test_public_repos(self, mock_get_json):
        """Test public_repos returns expected names"""
        mock_get_json.return_value = [
            {"name": "repo1"},
            {"name": "repo2"},
            {"name": "repo3"},
        ]
        with patch.object(GithubOrgClient, "_public_repos_url", new_callable=PropertyMock) as mock_url:
            mock_url.return_value = "http://mocked_url.com"
            client = GithubOrgClient("test")
            self.assertEqual(client.public_repos(), ["repo1", "repo2", "repo3"])
            mock_url.assert_called_once()
            mock_get_json.assert_called_once_with("http://mocked_url.com")

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other"}}, "my_license", False),
    ])
    def test_has_license(self, repo, license_key, expected):
        self.assertEqual(GithubOrgClient.has_license(repo, license_key), expected)


@parameterized_class([
    {
        "org_payload": {
            "login": "google",
            "id": 1,
            "repos_url": "https://api.github.com/orgs/google/repos"
        },
        "repos_payload": [
            {"id": 1, "name": "repo1", "license": {"key": "apache-2.0"}},
            {"id": 2, "name": "repo2", "license": {"key": "mit"}},
            {"id": 3, "name": "repo3", "license": {"key": "apache-2.0"}},
        ],
        "expected_repos": ["repo1", "repo2", "repo3"],
        "apache2_repos": ["repo1", "repo3"],
    }
])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests using patch on requests.get"""

    @classmethod
    def setUpClass(cls):
        cls.get_patcher = patch('requests.get')
        mock_get = cls.get_patcher.start()

        def side_effect(url):
            if url == "https://api.github.com/orgs/google":
                return Mock(json=lambda: cls.org_payload)
            elif url == cls.org_payload["repos_url"]:
                return Mock(json=lambda: cls.repos_payload)
            return Mock(json=lambda: {})

        mock_get.side_effect = side_effect

    @classmethod
    def tearDownClass(cls):
        cls.get_patcher.stop()

    def test_public_repos(self):
        client = GithubOrgClient("google")
        self.assertEqual(client.public_repos(), self.expected_repos)

    def test_public_repos_with_license(self):
        client = GithubOrgClient("google")
        self.assertEqual(
            client.public_repos(license="apache-2.0"),
            self.apache2_repos
        )


if __name__ == "__main__":
    unittest.main()
