"""Check a GitHub repository against the inclusion criteria in CONTRIBUTING.md."""

from datetime import date, timedelta

from tools.decisions import Decision
from tools.github import RepoStatus

MIN_AGE_DAYS = 180
ACTIVITY_DAYS = 365


def assess(
    owner: str,
    repo: str,
    status: RepoStatus | None,
    *,
    kept: Decision | None,
    today: date,
    new_entry: bool,
) -> list[str]:
    """Return what keeps the repository from meeting the criteria."""
    if status is None:
        return ["repository not found"]
    findings = []
    if status.full_name.casefold() != f"{owner}/{repo}".casefold():
        findings.append(
            f"repository moved to https://github.com/{status.full_name}; "
            "update the link"
        )
    if status.archived:
        findings.append("repository archived")
    if not status.has_readme:
        findings.append("repository has no readme")

    kept_until = kept.revisit_after if kept else None
    excused = kept_until is not None and kept_until >= today
    if not excused:
        if status.last_activity is None:
            findings.append("no commits")
        elif status.last_activity < today - timedelta(days=ACTIVITY_DAYS):
            findings.append(f"no commit or release since {status.last_activity}")

    min_age = timedelta(days=MIN_AGE_DAYS)
    if new_entry and status.first_commit and status.first_commit > today - min_age:
        findings.append(
            f"first commit on {status.first_commit}; the list accepts projects whose "
            f"first commit is at least {MIN_AGE_DAYS} days old, "
            f"so from {status.first_commit + min_age}"
        )
    return findings
