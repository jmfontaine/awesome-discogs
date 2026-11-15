from dataclasses import replace
from datetime import date

from tests.fakes import FakeGitHub
from tools.github import RepoStatus
from tools.pr import added_entries, check_pr
from tools.readme import Entry

TODAY = date(2026, 11, 15)
HEALTHY = RepoStatus("a/one", False, date(2020, 1, 1), date(2026, 11, 1), True)


def entry(name: str, url: str, line: int, section: str = "Tools") -> Entry:
    return Entry(line, section, None, name, url, "Tool.")


def check(entries, base_entries, github, association="NONE"):
    return check_pr(
        entries,
        base_entries,
        [],
        github,
        author_association=association,
        today=TODAY,
        readme_path="README.md",
    )


def test_moved_entry_is_not_added():
    base = [entry("One", "https://github.com/a/one", 10, "Tools")]
    moved = [entry("One", "https://github.com/A/One/", 20, "Other Tools")]
    assert added_entries(moved, base) == []


def test_one_entry_per_pull_request_outside_maintainers():
    github = FakeGitHub(
        {"a/one": HEALTHY, "a/two": replace(HEALTHY, full_name="a/two")}
    )
    added = [
        entry("One", "https://github.com/a/one", 10),
        entry("Two", "https://github.com/a/two", 11),
    ]
    problems = check(added, [], github)
    assert [(p.line, p.message) for p in problems] == [
        (10, "add one entry per pull request; this one adds 2")
    ]
    assert check(added, [], github, association="OWNER") == []


def test_findings_name_the_entry():
    github = FakeGitHub({"a/gone": None})
    problems = check([entry("Gone", "https://github.com/a/gone", 12)], [], github)
    assert [(p.line, p.message, p.level) for p in problems] == [
        (12, "Gone: repository not found", "error")
    ]


def test_entry_outside_github_is_a_notice_without_lookup():
    github = FakeGitHub()
    problems = check([entry("Site", "https://example.com/site", 12)], [], github)
    assert [(p.level, p.message) for p in problems] == [
        ("notice", "Site: not on GitHub, so check the inclusion criteria by hand")
    ]
    assert github.calls == []
