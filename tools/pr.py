"""Check the entries a pull request adds to the list, and their source markers."""

from collections.abc import Callable, Iterable
from datetime import date

from tools.decisions import Decision, kept_for
from tools.github import GitHub
from tools.health import assess, license_finding
from tools.problems import Level, Problem
from tools.readme import Entry
from tools.urls import github_repo, normalize

MAINTAINER_ASSOCIATIONS = frozenset({"OWNER", "MEMBER", "COLLABORATOR"})


def added_entries(
    entries: Iterable[Entry], base_entries: Iterable[Entry]
) -> list[Entry]:
    """Return the entries whose project isn't in the base list.

    Matching on the project's URL keeps an entry moved to another section, or
    reworded, from counting as added.
    """
    base = {normalize(entry.url) for entry in base_entries}
    return [entry for entry in entries if normalize(entry.url) not in base]


def changed_markers(
    entries: Iterable[Entry], base_entries: Iterable[Entry]
) -> list[Entry]:
    """Return the listed entries whose source marker this change sets or removes."""
    base = {normalize(entry.url): entry.source for entry in base_entries}
    return [
        entry
        for entry in entries
        if normalize(entry.url) in base and base[normalize(entry.url)] != entry.source
    ]


def check_pr(
    entries: Iterable[Entry],
    base_entries: Iterable[Entry],
    decisions: list[Decision],
    github: GitHub,
    *,
    osi_licenses: Callable[[], frozenset[str]],
    author_association: str,
    today: date,
    readme_path: str,
) -> list[Problem]:
    entries, base_entries = list(entries), list(base_entries)
    added = added_entries(entries, base_entries)
    problems = []

    def report(entry: Entry, message: str, level: Level = "error") -> None:
        problems.append(
            Problem(readme_path, entry.line, f"{entry.name}: {message}", level)
        )

    if author_association not in MAINTAINER_ASSOCIATIONS and len(added) > 1:
        problems.append(
            Problem(
                readme_path,
                added[0].line,
                f"add one entry per pull request; this one adds {len(added)}",
            )
        )
    remarked = changed_markers(entries, base_entries)
    for entry in added + remarked:
        is_new = entry in added
        repo = github_repo(entry.url)
        if repo is None:
            if is_new:
                report(
                    entry,
                    "not on GitHub, so check the inclusion criteria by hand",
                    "notice",
                )
            continue
        status = github.status(*repo)
        if is_new:
            for finding in assess(
                *repo,
                status,
                kept=kept_for(decisions, entry.url),
                today=today,
                new_entry=True,
            ):
                report(entry, finding)
        if status is None:
            continue
        if status.license == "NOASSERTION":
            report(
                entry,
                "GitHub can't identify its license, so check the source marker by hand",
                "notice",
            )
        elif finding := license_finding(status, entry.source, osi_licenses()):
            report(entry, finding)
    return problems
