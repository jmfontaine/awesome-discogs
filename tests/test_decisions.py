from datetime import date

import pytest

from tools.decisions import cross_check, kept_for, load
from tools.readme import Entry

TODAY = date(2026, 11, 15)
REFERENCE = "https://github.com/jmfontaine/awesome-discogs/issues/1"
BASE = {
    "name": '"Tool"',
    "url": "https://github.com/a/tool",
    "outcome": "rejected",
    "reason": "unmaintained",
    "date": "2026-11-01",
    "reference": REFERENCE,
    "note": '"No commit since 2024."',
}

VALID = f"""\
# Comments are fine.
- name: "Rejected Tool"
  url: https://github.com/a/rejected
  outcome: rejected
  reason: too-new
  date: 2026-11-01
  reference: {REFERENCE}
  note: "First commit on 2026-10-04."
  revisit_after: 2027-04-02
- name: "Removed Tool"
  url: https://example.com/removed
  outcome: removed
  reason: archived
  date: 2026-10-01
  reference: https://github.com/jmfontaine/awesome-discogs/pull/4
  note: "Archived on 2026-09-30: no longer works."
- name: "Kept Tool"
  url: https://github.com/a/kept
  outcome: kept
  reason: feature-complete
  date: 2026-10-01
  reference: https://github.com/jmfontaine/awesome-discogs/issues/5
  note: "Complete, and still works with the API."
  revisit_after: 2027-09-01
"""


def record(**overrides: str | None) -> str:
    """Return one record in YAML, with raw values; None drops a field."""
    fields = {**BASE, **overrides}
    lines = [f"{key}: {value}" for key, value in fields.items() if value is not None]
    return "- " + "\n  ".join(lines) + "\n"


def load_text(tmp_path, text: str):
    path = tmp_path / "decisions.yml"
    path.write_text(text, encoding="utf-8")
    return load(path, today=TODAY)


def test_valid_records_load(tmp_path):
    decisions, problems = load_text(tmp_path, VALID)
    assert problems == []
    assert [(d.line, d.name, d.outcome) for d in decisions] == [
        (2, "Rejected Tool", "rejected"),
        (10, "Removed Tool", "removed"),
        (17, "Kept Tool", "kept"),
    ]
    assert decisions[0].revisit_after == date(2027, 4, 2)
    assert decisions[1].note == "Archived on 2026-09-30: no longer works."


def test_comments_only_file_has_no_records(tmp_path):
    assert load_text(tmp_path, "# Nothing yet.\n") == ([], [])


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        pytest.param({"name": "'Tool'"}, "put name in double quotes", id="single"),
        pytest.param(
            {"note": "No commit #1 since 2024."},
            "put note in double quotes",
            id="unquoted-hash",
        ),
        pytest.param({"name": "123"}, '"name" must be text', id="not-text"),
        pytest.param(
            {"date": '"2026-11-01"'}, '"date" must be an unquoted date', id="quoted"
        ),
        pytest.param(
            {"date": "2026-11-01 10:00:00"},
            '"date" must be an unquoted date',
            id="datetime",
        ),
        pytest.param({"reason": None}, 'missing field "reason"', id="missing"),
        pytest.param({"tags": "x"}, 'unknown field "tags"', id="unknown-field"),
        pytest.param(
            {"url": "http://example.com/tool"}, "must be an https link", id="http"
        ),
        pytest.param(
            {"reference": "https://github.com/other/list/issues/1"},
            '"reference" must start with',
            id="reference",
        ),
        pytest.param({"outcome": "dropped"}, 'unknown outcome "dropped"', id="outcome"),
        pytest.param({"reason": "lazy"}, 'unknown reason "lazy"', id="reason"),
        pytest.param(
            {"reason": "feature-complete"},
            'doesn\'t apply to outcome "rejected"',
            id="reason-outcome",
        ),
        pytest.param({"date": "2026-12-01"}, "is in the future", id="future"),
        pytest.param(
            {"revisit_after": "2026-10-01"},
            '"revisit_after" must be after "date"',
            id="revisit-before",
        ),
        pytest.param(
            {"reason": "too-new"}, 'too-new records need "revisit_after"', id="too-new"
        ),
        pytest.param(
            {"outcome": "kept", "reason": "feature-complete"},
            'kept records need "revisit_after"',
            id="kept",
        ),
        pytest.param(
            {
                "outcome": "kept",
                "reason": "feature-complete",
                "revisit_after": "2027-12-01",
            },
            "at most 365 days",
            id="kept-too-long",
        ),
    ],
)
def test_one_problem_per_violation(tmp_path, overrides, message):
    _, problems = load_text(tmp_path, record(**overrides))
    assert len(problems) == 1, problems
    assert problems[0].line == 1
    assert message in problems[0].message


def test_problems_point_at_the_record_start(tmp_path):
    text = record() + record(name='"Second"', url="https://github.com/a/b", date='"x"')
    _, problems = load_text(tmp_path, text)
    assert [(p.line, p.message) for p in problems] == [
        (8, 'decision "Second": "date" must be an unquoted date: YYYY-MM-DD')
    ]


def test_duplicate_urls(tmp_path):
    text = record() + record(name='"Again"', url="https://github.com/A/Tool/")
    _, problems = load_text(tmp_path, text)
    assert [(p.line, p.message) for p in problems] == [
        (8, 'decision "Again": duplicates the record on line 1')
    ]


@pytest.mark.parametrize(
    ("text", "line", "message"),
    [
        pytest.param('- name: "Tool\n', 2, "invalid YAML", id="syntax"),
        pytest.param('name: "Tool"\n', None, "must be a list of records", id="mapping"),
        pytest.param("- just text\n", 1, "must be a mapping of fields", id="item"),
    ],
)
def test_file_level_problems(tmp_path, text, line, message):
    _, problems = load_text(tmp_path, text)
    assert len(problems) == 1, problems
    assert problems[0].line == line
    assert message in problems[0].message


def entry(name: str, url: str, line: int = 30) -> Entry:
    return Entry(line, "Tools", None, name, url, "Tool.")


def test_listed_project_recorded_as_excluded(tmp_path):
    decisions, _ = load_text(tmp_path, VALID)
    entries = [
        entry("Rejected", "https://github.com/A/Rejected", line=30),
        entry("Removed", "https://example.com/removed/", line=31),
        entry("Kept", "https://github.com/a/kept", line=32),
    ]
    problems = cross_check(
        entries,
        decisions,
        readme_path="README.md",
        decisions_path="decisions.yml",
        today=TODAY,
    )
    assert [(p.path, p.line, p.message) for p in problems] == [
        (
            "README.md",
            30,
            '"Rejected" is recorded as rejected (too-new) on 2026-11-01: First '
            f"commit on 2026-10-04. See {REFERENCE}. It can't come back before "
            "2027-04-02.",
        ),
        (
            "README.md",
            31,
            '"Removed" is recorded as removed (archived) on 2026-10-01: Archived on '
            "2026-09-30: no longer works. See "
            "https://github.com/jmfontaine/awesome-discogs/pull/4. Delete its "
            "record in decisions.yml once the reason no longer holds.",
        ),
    ]


def test_kept_record_without_entry(tmp_path):
    decisions, _ = load_text(tmp_path, VALID)
    problems = cross_check(
        [],
        decisions,
        readme_path="README.md",
        decisions_path="decisions.yml",
        today=TODAY,
    )
    assert [(p.path, p.line, p.message) for p in problems] == [
        (
            "decisions.yml",
            17,
            'decision "Kept Tool": kept record matches no entry in README.md; '
            "delete it",
        )
    ]


def test_kept_for_matches_normalized_url(tmp_path):
    decisions, _ = load_text(tmp_path, VALID)
    assert kept_for(decisions, "https://github.com/A/Kept#readme").name == "Kept Tool"
    assert kept_for(decisions, "https://github.com/a/rejected") is None
