import pytest

from tools.urls import github_repo, normalize


def test_github_links_to_the_same_repository_match():
    urls = [
        "https://github.com/Owner/Repo/",
        "https://github.com/owner/repo.git",
        "https://www.github.com/owner/repo#readme",
        "https://github.com/owner/repo/tree/main/x",
    ]
    assert {normalize(url) for url in urls} == {"https://github.com/owner/repo"}


def test_other_hosts_keep_path_case_and_query():
    assert (
        normalize("HTTPS://WWW.Example.com/Tool/?page=Two#top")
        == "https://example.com/Tool?page=Two"
    )


def test_github_repo_keeps_original_case():
    assert github_repo("https://github.com/Owner/Repo.git/tree/main/x") == (
        "Owner",
        "Repo",
    )


@pytest.mark.parametrize(
    "url",
    [
        "https://github.com/owner",
        "https://owner.github.io/repo",
        "https://github.com/orgs/owner/repositories",
        "https://gitlab.com/owner/repo",
    ],
)
def test_github_repo_ignores_pages_that_are_not_repositories(url):
    assert github_repo(url) is None
