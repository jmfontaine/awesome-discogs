"""Load decisions.yml and check it against CONTRIBUTING.md and the list."""

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

import yaml

from tools.problems import Problem
from tools.readme import Entry
from tools.urls import normalize

REASONS: dict[str, frozenset[str]] = {
    "not-discogs-specific": frozenset({"rejected", "removed"}),
    "unmaintained": frozenset({"rejected", "removed"}),
    "archived": frozenset({"rejected", "removed"}),
    "gone": frozenset({"removed"}),
    "undocumented": frozenset({"rejected", "removed"}),
    "too-new": frozenset({"rejected"}),
    "duplicate": frozenset({"rejected", "removed"}),
    "out-of-scope": frozenset({"rejected", "removed"}),
    "editorial": frozenset({"rejected", "removed"}),
    "feature-complete": frozenset({"kept"}),
}
OUTCOMES = ("rejected", "removed", "kept")
REFERENCE_PREFIX = "https://github.com/jmfontaine/awesome-discogs/"
KEPT_MAX_DAYS = 365

TEXT_FIELDS = ("name", "url", "outcome", "reason", "reference", "note")
DATE_FIELDS = ("date", "revisit_after")
REQUIRED_FIELDS = frozenset({*TEXT_FIELDS, "date"})
FIELDS = frozenset({*TEXT_FIELDS, *DATE_FIELDS})
QUOTED_FIELDS = ("name", "note")


@dataclass(frozen=True)
class Decision:
    line: int
    name: str
    url: str
    outcome: str
    reason: str
    date: date
    reference: str
    note: str
    revisit_after: date | None


def _quoting_styles(node: yaml.Node) -> dict[str, str | None]:
    """Return the scalar style of each field whose value is a scalar."""
    if not isinstance(node, yaml.MappingNode):
        return {}
    return {
        key.value: value.style
        for key, value in node.value
        if isinstance(key, yaml.ScalarNode) and isinstance(value, yaml.ScalarNode)
    }


class _Reporter:
    def __init__(self, path: str) -> None:
        self.path = path
        self.problems: list[Problem] = []
        self.prefix = ""

    def __call__(self, line: int | None, message: str) -> None:
        self.problems.append(Problem(self.path, line, self.prefix + message))


def _check_record(
    record: dict[object, object],
    styles: dict[str, str | None],
    line: int,
    today: date,
    report: _Reporter,
) -> Decision | None:
    """Check one record's fields; return the decision when every field is usable."""
    usable = True
    for field in sorted(REQUIRED_FIELDS - record.keys()):
        report(line, f'missing field "{field}"')
        usable = False
    for field in sorted(str(key) for key in record.keys() - FIELDS):
        report(line, f'unknown field "{field}"')

    for field in TEXT_FIELDS:
        if field not in record:
            continue
        if not isinstance(record[field], str):
            report(line, f'"{field}" must be text')
            usable = False
        elif field in QUOTED_FIELDS and styles.get(field) != '"':
            report(line, f"put {field} in double quotes")
    for field in DATE_FIELDS:
        # A quoted date loads as a string, and a time makes it a datetime.
        if field in record and type(record[field]) is not date:
            report(line, f'"{field}" must be an unquoted date: YYYY-MM-DD')
            usable = False
    if not usable:
        return None

    decision = Decision(
        line=line,
        **{field: record[field] for field in REQUIRED_FIELDS},
        revisit_after=record.get("revisit_after"),
    )

    if not decision.url.startswith("https://"):
        report(line, '"url" must be an https link')
    if not decision.reference.startswith(REFERENCE_PREFIX):
        report(line, f'"reference" must start with {REFERENCE_PREFIX}')
    if decision.outcome not in OUTCOMES:
        report(
            line,
            f'unknown outcome "{decision.outcome}"; use rejected, removed or kept',
        )
    if decision.reason not in REASONS:
        report(line, f'unknown reason "{decision.reason}"')
    elif decision.outcome in OUTCOMES and (
        decision.outcome not in REASONS[decision.reason]
    ):
        report(
            line,
            f'reason "{decision.reason}" doesn\'t apply to outcome '
            f'"{decision.outcome}"',
        )
    if decision.date > today:
        report(line, f"date {decision.date} is in the future")

    revisit = decision.revisit_after
    if revisit is None:
        if decision.outcome == "kept" or decision.reason == "too-new":
            needs = "kept" if decision.outcome == "kept" else "too-new"
            report(line, f'{needs} records need "revisit_after"')
    elif revisit <= decision.date:
        report(line, '"revisit_after" must be after "date"')
    elif decision.outcome == "kept" and revisit > decision.date + timedelta(
        days=KEPT_MAX_DAYS
    ):
        report(
            line,
            f'"revisit_after" of a kept record must be at most {KEPT_MAX_DAYS} '
            'days after "date"',
        )
    return decision


def load(path: Path, *, today: date) -> tuple[list[Decision], list[Problem]]:
    """Return the decisions recorded in the file and the problems found in it."""
    report = _Reporter(str(path))
    text = path.read_text(encoding="utf-8")
    try:
        root = yaml.compose(text, Loader=yaml.SafeLoader)
        values = yaml.safe_load(text)
    except yaml.YAMLError as error:
        mark = getattr(error, "problem_mark", None)
        report(mark.line + 1 if mark else None, f"invalid YAML: {error}")
        return [], report.problems
    except ValueError as error:  # Such as a date that doesn't exist: 2026-02-30.
        report(None, f"invalid YAML: {error}")
        return [], report.problems

    if root is None:
        return [], []
    if not isinstance(root, yaml.SequenceNode) or not isinstance(values, list):
        report(None, "decisions.yml must be a list of records")
        return [], report.problems

    decisions: list[Decision] = []
    first_by_url: dict[str, Decision] = {}
    for index, (node, record) in enumerate(zip(root.value, values, strict=True)):
        line = node.start_mark.line + 1
        if not isinstance(record, dict):
            report.prefix = f"decision {index + 1}: "
            report(line, "must be a mapping of fields")
            continue
        name = record.get("name")
        report.prefix = (
            f'decision "{name}": '
            if isinstance(name, str)
            else f"decision {index + 1}: "
        )
        decision = _check_record(record, _quoting_styles(node), line, today, report)
        if decision is None:
            continue
        key = normalize(decision.url)
        if key in first_by_url:
            report(line, f"duplicates the record on line {first_by_url[key].line}")
        else:
            first_by_url[key] = decision
        decisions.append(decision)
    return decisions, report.problems


def kept_for(decisions: Iterable[Decision], url: str) -> Decision | None:
    """Return the kept record for the project at this URL, if any."""
    key = normalize(url)
    return next(
        (d for d in decisions if d.outcome == "kept" and normalize(d.url) == key),
        None,
    )


def cross_check(
    entries: Iterable[Entry],
    decisions: Iterable[Decision],
    *,
    readme_path: str,
    decisions_path: str,
    today: date,
) -> list[Problem]:
    """Find listed projects recorded as rejected or removed, and orphan kept records."""
    decisions = list(decisions)
    excluded = {
        normalize(d.url): d for d in decisions if d.outcome in ("rejected", "removed")
    }
    listed = set()
    problems = []
    for entry in entries:
        key = normalize(entry.url)
        listed.add(key)
        decision = excluded.get(key)
        if decision is None:
            continue
        message = (
            f'"{entry.name}" is recorded as {decision.outcome} ({decision.reason}) '
            f"on {decision.date}: {decision.note} See {decision.reference}."
        )
        if decision.revisit_after is not None and decision.revisit_after > today:
            message += f" It can't come back before {decision.revisit_after}."
        else:
            message += (
                " Delete its record in decisions.yml once the reason no longer holds."
            )
        problems.append(Problem(readme_path, entry.line, message))
    for decision in decisions:
        if decision.outcome == "kept" and normalize(decision.url) not in listed:
            problems.append(
                Problem(
                    decisions_path,
                    decision.line,
                    f'decision "{decision.name}": kept record matches no entry in '
                    "README.md; delete it",
                )
            )
    return problems
