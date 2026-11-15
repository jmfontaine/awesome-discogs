from dataclasses import replace
from datetime import date

from tests.fakes import FakeGitHub
from tools.github import RepoStatus
from tools.pr import added_entries, check_pr
from tools.readme import Entry

TODAY = date(2026, 11, 15)
HEALTHY = RepoStatus("a/one", False, date(2020, 1, 1), date(2026, 11, 1), True, "MIT")
OSI = frozenset({"MIT", "Apache-2.0"})


def entry(
    name: str,
    url: str,
    line: int,
    section: str = "Tools",
    description: str = "Tool.",
) -> Entry:
    return Entry(line, section, None, name, url, description)


def check(entries, base_entries, github, association="NONE", osi=lambda: OSI):
    return check_pr(
        entries,
        base_entries,
        [],
        github,
        osi_licenses=osi,
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


def test_source_marker_must_match_the_license():
    one = "https://github.com/a/one"
    cases = [
        (None, "Tool.", "One: it has no license, so mark it (source available)"),
        (
            "BUSL-1.1",
            "Tool.",
            "One: its license, BUSL-1.1, isn't OSI-approved, so mark it "
            "(source available)",
        ),
        (
            "MIT",
            "Tool (paid, source available).",
            "One: its license, MIT, is open source, so drop (source available)",
        ),
        (
            None,
            "Tool (closed source).",
            "One: its source code is public under no license, so replace "
            "(closed source) with (source available)",
        ),
    ]
    for license, description, message in cases:
        github = FakeGitHub({"a/one": replace(HEALTHY, license=license)})
        problems = check([entry("One", one, 10, description=description)], [], github)
        assert [p.message for p in problems] == [message]

    for license, description in [("MIT", "Tool."), (None, "Tool (source available).")]:
        github = FakeGitHub({"a/one": replace(HEALTHY, license=license)})
        added = [entry("One", one, 10, description=description)]
        assert check(added, [], github) == []


def test_unidentified_license_is_a_notice():
    github = FakeGitHub({"a/one": replace(HEALTHY, license="NOASSERTION")})
    problems = check([entry("One", "https://github.com/a/one", 10)], [], github)
    assert [(p.level, p.message) for p in problems] == [
        (
            "notice",
            "One: GitHub can't identify its license, so check the source marker "
            "by hand",
        )
    ]


def test_changed_marker_on_a_listed_entry_is_checked_alone():
    # An inactive repository: only the marker is checked on a listed entry.
    inactive = replace(HEALTHY, last_activity=date(2020, 1, 1))
    github = FakeGitHub({"a/one": inactive})
    base = [entry("One", "https://github.com/a/one", 10)]
    remarked = [entry("One", "https://github.com/a/one", 10, description="T (paid).")]
    assert check(remarked, base, github) == []
    assert github.calls == []

    remarked = [
        entry(
            "One", "https://github.com/a/one", 10, description="T (source available)."
        )
    ]
    problems = check(remarked, base, github)
    assert [p.message for p in problems] == [
        "One: its license, MIT, is open source, so drop (source available)"
    ]
    assert github.calls == ["a/one"]


def test_license_list_is_fetched_only_when_needed():
    fetched = []

    def osi():
        fetched.append(True)
        return OSI

    base = [entry("One", "https://github.com/a/one", 10)]
    assert check(base, base, FakeGitHub(), osi=osi) == []
    assert fetched == []
