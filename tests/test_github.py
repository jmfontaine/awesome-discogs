from datetime import date

import pytest

from tools.github import GitHub, RepoStatus

REPO = {"full_name": "Owner/Repo", "archived": False, "default_branch": "main"}
COMMITS = "/repos/Owner/Repo/commits?sha=main&per_page=1"
LAST_PAGE = "https://api.github.com/repositories/1/commits?sha=main&per_page=1&page=90"


def commit(authored: str, committed: str) -> list[dict]:
    return [
        {"commit": {"author": {"date": authored}, "committer": {"date": committed}}}
    ]


def client(monkeypatch, replies: dict[str, tuple[int, object, str]]) -> GitHub:
    """Return a client whose requests get the replies set for their URLs."""
    github = GitHub(token=None)

    def get(url, *, expected=()):
        code, body, link = replies[url]
        assert code < 400 or code in expected
        return code, body, link

    monkeypatch.setattr(github, "_get", get)
    return github


def replies(**changes) -> dict[str, tuple[int, object, str]]:
    base = {
        "/repos/owner/repo": (200, REPO, ""),
        COMMITS: (
            200,
            commit("2024-03-01T10:00:00Z", "2024-03-02T10:00:00Z"),
            f'<{LAST_PAGE}>; rel="last"',
        ),
        LAST_PAGE: (200, commit("2019-05-01T10:00:00Z", "2019-05-01T10:00:00Z"), ""),
        "/repos/Owner/Repo/releases/latest": (
            200,
            {"published_at": "2025-01-10T00:00:00Z"},
            "",
        ),
        "/repos/Owner/Repo/readme": (200, {}, ""),
    }
    return {**base, **changes}


def test_release_newer_than_last_commit_counts_as_activity(monkeypatch):
    github = client(monkeypatch, replies())
    assert github.status("owner", "repo") == RepoStatus(
        full_name="Owner/Repo",
        archived=False,
        first_commit=date(2019, 5, 1),
        last_activity=date(2025, 1, 10),
        has_readme=True,
    )


def test_single_page_of_commits_and_no_release_or_readme(monkeypatch):
    github = client(
        monkeypatch,
        replies(
            **{
                COMMITS: (
                    200,
                    commit("2024-03-01T10:00:00Z", "2024-03-02T10:00:00Z"),
                    "",
                ),
                "/repos/Owner/Repo/releases/latest": (404, None, ""),
                "/repos/Owner/Repo/readme": (404, None, ""),
            }
        ),
    )
    status = github.status("owner", "repo")
    assert (status.first_commit, status.last_activity, status.has_readme) == (
        date(2024, 3, 1),
        date(2024, 3, 2),
        False,
    )


@pytest.mark.parametrize(
    ("changes", "expected"),
    [
        pytest.param({"/repos/owner/repo": (404, None, "")}, None, id="not-found"),
        pytest.param(
            {
                COMMITS: (409, None, ""),
                "/repos/Owner/Repo/releases/latest": (404, None, ""),
            },
            RepoStatus("Owner/Repo", False, None, None, True),
            id="empty",
        ),
    ],
)
def test_missing_and_empty_repositories(monkeypatch, changes, expected):
    assert client(monkeypatch, replies(**changes)).status("owner", "repo") == expected
