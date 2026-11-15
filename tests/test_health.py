from datetime import date, timedelta

from tools.decisions import Decision
from tools.github import RepoStatus
from tools.health import assess

TODAY = date(2026, 11, 15)


def status(**changes) -> RepoStatus:
    fields = {
        "full_name": "Owner/Repo",
        "archived": False,
        "first_commit": date(2020, 1, 1),
        "last_activity": TODAY - timedelta(days=10),
        "has_readme": True,
        "license": "MIT",
    }
    return RepoStatus(**{**fields, **changes})


def kept(revisit_after: date) -> Decision:
    return Decision(
        line=1,
        name="Repo",
        url="https://github.com/owner/repo",
        outcome="kept",
        reason="feature-complete",
        date=date(2026, 6, 1),
        reference="https://github.com/jmfontaine/awesome-discogs/issues/1",
        note="Complete.",
        revisit_after=revisit_after,
    )


def check(repo_status, *, kept=None, new_entry=False):
    return assess(
        "owner", "repo", repo_status, kept=kept, today=TODAY, new_entry=new_entry
    )


def test_healthy_repository_has_no_findings():
    assert check(status(), new_entry=True) == []


def test_not_found():
    assert check(None, new_entry=True) == ["repository not found"]


def test_moved():
    assert check(status(full_name="new-owner/repo")) == [
        "repository moved to https://github.com/new-owner/repo; update the link"
    ]


def test_archived_and_no_readme():
    assert check(status(archived=True, has_readme=False)) == [
        "repository archived",
        "repository has no readme",
    ]


def test_inactive():
    last = TODAY - timedelta(days=400)
    assert check(status(last_activity=last)) == [f"no commit or release since {last}"]
    assert check(status(last_activity=None)) == ["no commits"]


def test_kept_record_excuses_inactivity_until_revisit():
    inactive = status(last_activity=TODAY - timedelta(days=400))
    assert check(inactive, kept=kept(TODAY)) == []
    assert check(inactive, kept=kept(TODAY - timedelta(days=1))) == [
        f"no commit or release since {TODAY - timedelta(days=400)}"
    ]


def test_too_new_only_for_new_entries():
    young = status(first_commit=TODAY - timedelta(days=30))
    assert check(young, new_entry=True) == [
        f"first commit on {TODAY - timedelta(days=30)}; the list accepts projects "
        "whose first commit is at least 180 days old, so from "
        f"{TODAY + timedelta(days=150)}"
    ]
    assert check(young, new_entry=False) == []
