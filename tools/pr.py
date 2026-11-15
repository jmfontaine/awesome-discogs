"""Check the entries a pull request adds to the list."""

from collections.abc import Iterable
from datetime import date

from tools.decisions import Decision, kept_for
from tools.github import GitHub
from tools.health import assess
from tools.problems import Problem
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


def check_pr(
    entries: Iterable[Entry],
    base_entries: Iterable[Entry],
    decisions: list[Decision],
    github: GitHub,
    *,
    author_association: str,
    today: date,
    readme_path: str,
) -> list[Problem]:
    added = added_entries(entries, base_entries)
    problems = []
    if author_association not in MAINTAINER_ASSOCIATIONS and len(added) > 1:
        problems.append(
            Problem(
                readme_path,
                added[0].line,
                f"add one entry per pull request; this one adds {len(added)}",
            )
        )
    for entry in added:
        repo = github_repo(entry.url)
        if repo is None:
            problems.append(
                Problem(
                    readme_path,
                    entry.line,
                    f"{entry.name}: not on GitHub, so check the inclusion criteria "
                    "by hand",
                    level="notice",
                )
            )
            continue
        findings = assess(
            *repo,
            github.status(*repo),
            kept=kept_for(decisions, entry.url),
            today=today,
            new_entry=True,
        )
        problems.extend(
            Problem(readme_path, entry.line, f"{entry.name}: {finding}")
            for finding in findings
        )
    return problems
