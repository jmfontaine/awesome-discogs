"""URL helpers shared by the README and the decisions checks."""

from urllib.parse import urlsplit, urlunsplit

GITHUB_HOSTS = frozenset({"github.com", "www.github.com"})

# First path segments of github.com pages that aren't repositories.
NOT_OWNERS = frozenset(
    {"orgs", "sponsors", "marketplace", "apps", "topics", "collections", "features"}
)


def _strip_git(name: str) -> str:
    return name.removesuffix(".git")


def github_repo(url: str) -> tuple[str, str] | None:
    """Return the owner and repository a github.com URL points to, if any."""
    parts = urlsplit(url)
    if (parts.hostname or "") not in GITHUB_HOSTS:
        return None
    segments = [segment for segment in parts.path.split("/") if segment]
    if len(segments) < 2 or segments[0].lower() in NOT_OWNERS:
        return None
    repo = _strip_git(segments[1])
    if not repo:
        return None
    return segments[0], repo


def normalize(url: str) -> str:
    """Return a form of the URL under which links to the same project match."""
    repo = github_repo(url)
    if repo is not None:
        owner, name = repo
        return f"https://github.com/{owner}/{name}".lower()
    parts = urlsplit(url)
    host = (parts.hostname or "").removeprefix("www.")
    if parts.port is not None:
        host += f":{parts.port}"
    path = _strip_git(parts.path.rstrip("/")).rstrip("/")
    return urlunsplit((parts.scheme.lower(), host, path, parts.query, ""))
