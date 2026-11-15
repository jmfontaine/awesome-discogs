"""Read what the inclusion criteria need to know about a GitHub repository."""

import json
import re
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any
from urllib.parse import quote

API = "https://api.github.com"
TIMEOUT_SECONDS = 30
LAST_PAGE = re.compile(r'<([^>]+)>;\s*rel="last"')


@dataclass(frozen=True)
class RepoStatus:
    full_name: str
    archived: bool
    first_commit: date | None
    last_activity: date | None
    has_readme: bool
    # SPDX identifier of the license GitHub detects: NOASSERTION when it finds a
    # license it can't identify, None when it finds none.
    license: str | None


class GitHubError(Exception):
    pass


def _date(timestamp: str | None) -> date | None:
    return datetime.fromisoformat(timestamp).date() if timestamp else None


class GitHub:
    def __init__(self, token: str | None) -> None:
        self.headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "awesome-discogs-checks",
        }
        if token:
            self.headers["Authorization"] = f"Bearer {token}"

    def _get(self, url: str, *, expected: tuple[int, ...] = ()) -> tuple[int, Any, str]:
        """Return the status, the JSON body and the Link header of a GET request.

        Statuses in `expected` come back with no body; any other error raises.
        """
        if url.startswith("/"):
            url = API + url
        request = urllib.request.Request(url, headers=self.headers)
        try:
            with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
                return (
                    response.status,
                    json.load(response),
                    response.headers.get("Link", ""),
                )
        except urllib.error.HTTPError as error:
            if error.code in expected:
                return error.code, None, ""
            raise GitHubError(f"GET {url} failed with HTTP {error.code}") from error
        except urllib.error.URLError as error:
            raise GitHubError(f"GET {url} failed: {error.reason}") from error

    def status(self, owner: str, repo: str) -> RepoStatus | None:
        """Return the repository's status, or None when it doesn't exist."""
        # urllib follows the redirect GitHub sends for a renamed repository.
        code, repository, _ = self._get(
            f"/repos/{quote(owner)}/{quote(repo)}", expected=(404,)
        )
        if code == 404:
            return None
        full_name = repository["full_name"]
        branch = quote(repository["default_branch"], safe="")

        first_commit = last_commit = None
        code, commits, link = self._get(
            f"/repos/{full_name}/commits?sha={branch}&per_page=1", expected=(409,)
        )
        if code != 409 and commits:  # 409 means the repository is empty.
            newest = commits[0]["commit"]
            last_commit = _date(newest["committer"]["date"])
            first_commit = _date(newest["author"]["date"])
            if match := LAST_PAGE.search(link):
                _, oldest, _ = self._get(match[1])
                first_commit = _date(oldest[0]["commit"]["author"]["date"])

        code, release, _ = self._get(
            f"/repos/{full_name}/releases/latest", expected=(404,)
        )
        last_release = _date(release["published_at"]) if code != 404 else None

        code, _, _ = self._get(f"/repos/{full_name}/readme", expected=(404,))

        activity = [d for d in (last_commit, last_release) if d is not None]
        return RepoStatus(
            full_name=full_name,
            archived=repository["archived"],
            first_commit=first_commit,
            last_activity=max(activity, default=None),
            has_readme=code != 404,
            license=(repository["license"] or {}).get("spdx_id"),
        )
