from dataclasses import replace
from datetime import date

import pytest

from tests.fakes import FakeGitHub
from tools.__main__ import main
from tools.audit import audit, render
from tools.decisions import Decision
from tools.github import GitHubError, RepoStatus
from tools.readme import Entry

TODAY = date(2026, 11, 15)
HEALTHY = RepoStatus("a/one", False, date(2020, 1, 1), date(2026, 11, 1), True, "MIT")
INACTIVE = replace(HEALTHY, last_activity=date(2024, 1, 2))


def osi() -> frozenset[str]:
    return frozenset({"MIT"})


def entry(name: str, subsection: str | None = None) -> Entry:
    section = "API Clients" if subsection else "Tools"
    return Entry(10, section, subsection, name, f"https://github.com/a/{name}", "Tool.")


def kept(name: str, revisit_after: date) -> Decision:
    return Decision(
        line=1,
        name=name,
        url=f"https://github.com/a/{name}",
        outcome="kept",
        reason="feature-complete",
        date=date(2026, 6, 1),
        reference="https://github.com/jmfontaine/awesome-discogs/issues/7",
        note="Complete.",
        revisit_after=revisit_after,
    )


def test_findings_name_the_section():
    github = FakeGitHub(
        {
            "a/one": replace(HEALTHY, archived=True),
            "a/two": replace(INACTIVE, full_name="a/two"),
            "a/three": replace(HEALTHY, full_name="a/three", first_commit=TODAY),
        }
    )
    entries = [entry("one"), entry("two", "Python"), entry("three")]
    assert audit(entries, [], github, osi_licenses=osi, today=TODAY) == [
        ("[one](https://github.com/a/one) (Tools)", ["repository archived"]),
        (
            "[two](https://github.com/a/two) (API Clients > Python)",
            ["no commit or release since 2024-01-02"],
        ),
    ]


def test_kept_decision_excuses_inactivity_until_it_expires():
    github = FakeGitHub({"a/one": INACTIVE})
    current = kept("one", date(2027, 1, 1))
    assert audit([entry("one")], [current], github, osi_licenses=osi, today=TODAY) == []

    expired = kept("one", date(2026, 11, 1))
    assert audit([entry("one")], [expired], github, osi_licenses=osi, today=TODAY) == [
        (
            "[one](https://github.com/a/one) (Tools)",
            ["no commit or release since 2024-01-02"],
        ),
        (
            "[one](https://github.com/a/one) (kept decision)",
            [
                "kept decision expired on 2026-11-01: review it, see "
                "https://github.com/jmfontaine/awesome-discogs/issues/7"
            ],
        ),
    ]


def test_entry_outside_github_is_not_looked_up():
    github = FakeGitHub()
    site = Entry(10, "Tools", None, "Site", "https://example.com/site", "Tool.")
    assert audit([site], [], github, osi_licenses=osi, today=TODAY) == []
    assert github.calls == []


def test_source_marker_is_audited():
    github = FakeGitHub({"a/one": replace(HEALTHY, license="BUSL-1.1")})
    assert audit([entry("one")], [], github, osi_licenses=osi, today=TODAY) == [
        (
            "[one](https://github.com/a/one) (Tools)",
            [
                "its license, BUSL-1.1, isn't OSI-approved, "
                "so mark it (source available)"
            ],
        )
    ]
    unidentified = FakeGitHub({"a/one": replace(HEALTHY, license="NOASSERTION")})
    assert audit([entry("one")], [], unidentified, osi_licenses=osi, today=TODAY) == []


def test_render():
    findings = [
        ("[one](https://github.com/a/one) (Tools)", ["repository archived", "x"]),
        ("[two](https://github.com/a/two) (Tools)", ["y"]),
    ]
    assert render(findings) == (
        "- [one](https://github.com/a/one) (Tools): repository archived; x.\n"
        "- [two](https://github.com/a/two) (Tools): y.\n"
    )


README = """\
# Awesome Discogs

## Contents

- [Tools](#tools)

## Tools

- [one](https://github.com/a/one) - Tool.

## Contributing
"""


@pytest.mark.parametrize(
    ("status", "code", "output"),
    [
        pytest.param(HEALTHY, 0, "No findings.\n", id="healthy"),
        pytest.param(
            None,
            1,
            "[one](https://github.com/a/one) (Tools): repository not found.\n",
            id="findings",
        ),
    ],
)
def test_main_exit_codes(tmp_path, monkeypatch, capsys, status, code, output):
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    readme = tmp_path / "README.md"
    readme.write_text(README, encoding="utf-8")
    decisions = tmp_path / "decisions.yml"
    decisions.write_text("# None yet.\n", encoding="utf-8")
    report = tmp_path / "audit.md"
    argv = [
        "audit",
        f"--readme={readme}",
        f"--decisions={decisions}",
        f"--today={TODAY}",
        f"--report={report}",
    ]

    assert main(argv, github=FakeGitHub({"a/one": status}), osi_licenses=osi) == code
    assert capsys.readouterr().out == output
    assert report.exists() == (code == 1)


def test_main_exits_2_when_github_fails(tmp_path, monkeypatch, capsys):
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    readme = tmp_path / "README.md"
    readme.write_text(README, encoding="utf-8")
    decisions = tmp_path / "decisions.yml"
    decisions.write_text("# None yet.\n", encoding="utf-8")

    class FailingGitHub:
        def status(self, owner, repo):
            raise GitHubError("GET https://api.github.com/repos/a/one failed")

    argv = ["audit", f"--readme={readme}", f"--decisions={decisions}"]
    assert main(argv, github=FailingGitHub(), osi_licenses=osi) == 2
    assert "failed" in capsys.readouterr().out
