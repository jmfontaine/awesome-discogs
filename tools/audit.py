"""Check every listed GitHub project against the inclusion criteria again."""

from collections.abc import Callable, Iterable
from datetime import date

from tools.decisions import Decision, kept_for
from tools.github import GitHub
from tools.health import assess, license_finding
from tools.readme import Entry
from tools.urls import github_repo

Findings = list[tuple[str, list[str]]]


def audit(
    entries: Iterable[Entry],
    decisions: list[Decision],
    github: GitHub,
    *,
    osi_licenses: Callable[[], frozenset[str]],
    today: date,
) -> Findings:
    """Return each listed project or kept decision to review, with its findings."""
    results: Findings = []
    for entry in entries:
        repo = github_repo(entry.url)
        if repo is None:
            continue
        status = github.status(*repo)
        # A listed project only gets older, so its age isn't audited.
        findings = assess(
            *repo,
            status,
            kept=kept_for(decisions, entry.url),
            today=today,
            new_entry=False,
        )
        if status is not None and (
            finding := license_finding(status, entry.source, osi_licenses())
        ):
            findings.append(finding)
        if findings:
            where = entry.section
            if entry.subsection:
                where += f" > {entry.subsection}"
            results.append((f"[{entry.name}]({entry.url}) ({where})", findings))
    for decision in decisions:
        revisit = decision.revisit_after
        if decision.outcome == "kept" and revisit is not None and revisit < today:
            results.append(
                (
                    f"[{decision.name}]({decision.url}) (kept decision)",
                    [
                        f"kept decision expired on {revisit}: review it, "
                        f"see {decision.reference}"
                    ],
                )
            )
    return results


def render(findings: Findings) -> str:
    """Return the findings as a Markdown list, one line per subject."""
    return "".join(f"- {subject}: {'; '.join(items)}.\n" for subject, items in findings)
