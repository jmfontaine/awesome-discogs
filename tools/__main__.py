"""Command line for the list checks: `uv run python -m tools <command>`."""

import argparse
import os
import subprocess
import sys
from collections.abc import Callable
from datetime import UTC, date, datetime
from functools import cache
from pathlib import Path

from tools.audit import audit, render
from tools.decisions import Decision, cross_check, load
from tools.github import GitHub, GitHubError
from tools.licenses import LicenseListError, osi_approved
from tools.pr import check_pr
from tools.problems import Problem, emit
from tools.readme import Entry, parse


def _parser() -> argparse.ArgumentParser:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--readme", type=Path, default=Path("README.md"))
    common.add_argument("--decisions", type=Path, default=Path("decisions.yml"))
    common.add_argument(
        "--today",
        type=date.fromisoformat,
        default=datetime.now(UTC).date(),
        help="date to check against, YYYY-MM-DD (default: today in UTC)",
    )

    parser = argparse.ArgumentParser(prog="python -m tools", description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser(
        "check",
        parents=[common],
        help="check README.md and decisions.yml against the contribution guidelines",
    )
    pr = commands.add_parser(
        "pr",
        parents=[common],
        help="check the GitHub projects a pull request adds against the criteria",
    )
    pr.add_argument("--base", required=True, help="revision of the base README.md")
    pr.add_argument(
        "--author-association",
        required=True,
        help="the pull request author's association, such as OWNER or NONE",
    )
    audit_command = commands.add_parser(
        "audit",
        parents=[common],
        help="report listed GitHub projects that no longer meet the criteria",
    )
    audit_command.add_argument(
        "--report", type=Path, help="write the findings to this Markdown file"
    )
    return parser


def _github() -> GitHub:
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print(
            "warning: GITHUB_TOKEN is not set; unauthenticated GitHub API requests "
            "are limited to 60 per hour",
            file=sys.stderr,
        )
    return GitHub(token)


def _fail(message: str, *, annotations: bool) -> int:
    print(f"::error::{message}" if annotations else f"error: {message}")
    return 2


def _audit(
    args: argparse.Namespace,
    entries: list[Entry],
    decisions: list[Decision],
    github: GitHub | None,
    *,
    annotations: bool,
) -> int:
    """Print the audit findings; exit 1 with findings, 0 without."""
    try:
        findings = audit(entries, decisions, github or _github(), today=args.today)
    except GitHubError as error:
        return _fail(str(error), annotations=annotations)
    if not findings:
        print("No findings.")
        return 0
    for subject, items in findings:
        print(f"{subject}: {'; '.join(items)}.")
    if args.report:
        args.report.write_text(render(findings), encoding="utf-8")
    return 1


def main(
    argv: list[str] | None = None,
    github: GitHub | None = None,
    osi_licenses: Callable[[], frozenset[str]] | None = None,
) -> int:
    args = _parser().parse_args(argv)
    annotations = os.environ.get("GITHUB_ACTIONS") == "true"
    readme_path = str(args.readme)

    entries, problems = parse(args.readme.read_text(encoding="utf-8"), readme_path)
    decisions, decision_problems = load(args.decisions, today=args.today)

    if args.command == "audit":
        return _audit(args, entries, decisions, github, annotations=annotations)

    found: list[Problem]
    if args.command == "check":
        found = problems + decision_problems
        found += cross_check(
            entries,
            decisions,
            readme_path=readme_path,
            decisions_path=str(args.decisions),
            today=args.today,
        )
    else:
        try:
            base = subprocess.run(
                ["git", "show", f"{args.base}:README.md"],
                capture_output=True,
                check=True,
                text=True,
            ).stdout
        except subprocess.CalledProcessError as error:
            return _fail(
                f"can't read README.md at {args.base}: {error.stderr.strip()}",
                annotations=annotations,
            )
        base_entries, _ = parse(base)
        try:
            found = check_pr(
                entries,
                base_entries,
                decisions,
                github or _github(),
                osi_licenses=osi_licenses or cache(osi_approved),
                author_association=args.author_association,
                today=args.today,
                readme_path=readme_path,
            )
        except (GitHubError, LicenseListError) as error:
            return _fail(str(error), annotations=annotations)

    emit(found, annotations=annotations)
    return 1 if any(problem.level == "error" for problem in found) else 0


if __name__ == "__main__":
    sys.exit(main())
