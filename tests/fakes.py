from tools.github import RepoStatus


class FakeGitHub:
    """Return preset repository statuses and count the lookups."""

    def __init__(self, statuses: dict[str, RepoStatus | None] | None = None) -> None:
        self.statuses = statuses or {}
        self.calls: list[str] = []

    def status(self, owner: str, repo: str) -> RepoStatus | None:
        name = f"{owner}/{repo}"
        self.calls.append(name)
        return self.statuses[name]
