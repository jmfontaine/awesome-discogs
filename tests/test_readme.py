import pytest

from tools.readme import Entry, parse

HEADER = "# Awesome Discogs\n\n## Contents\n\n- [API Clients](#api-clients)\n\n"
FIRST_LINE = 7  # Line number of the first line after HEADER.


def check(body: str):
    return parse(HEADER + body + "\n## Contributing\n\nRead the guidelines.\n")


def test_valid_list_has_no_problems():
    entries, problems = check(
        "## Official Resources\n"
        "\n"
        "- [Alpha](https://example.com/alpha) - Export a collection (paid).\n"
        "- [beta](https://example.com/beta) - Sell records (paid, closed source).\n"
        "\n"
        "## API Clients\n"
        "\n"
        "### Python\n"
        "\n"
        "- [client](https://github.com/a/client) - Client for the API.\n"
        "\n"
        "## Command-Line Tools\n"
    )
    assert problems == []
    assert entries[0] == Entry(
        FIRST_LINE + 2,
        "Official Resources",
        None,
        "Alpha",
        "https://example.com/alpha",
        "Export a collection (paid).",
    )
    assert (entries[2].section, entries[2].subsection) == ("API Clients", "Python")


@pytest.mark.parametrize(
    ("body", "line", "message"),
    [
        pytest.param(
            "## Tools\n\n- [Zeta](https://e.com/z) - Zeta tool.\n"
            "- [alpha](https://e.com/a) - Alpha tool.\n",
            FIRST_LINE + 3,
            '"alpha" must come before "Zeta"',
            id="order",
        ),
        pytest.param(
            "## Tools\n\n- [A](https://e.com/a) - Tool (Paid).\n",
            FIRST_LINE + 2,
            "markers go before the final period",
            id="marker-case",
        ),
        pytest.param(
            "## Tools\n\n- [A](https://e.com/a) - Tool. (paid)\n",
            FIRST_LINE + 2,
            "markers go before the final period",
            id="marker-after-period",
        ),
        pytest.param(
            "## Tools\n\n- [A](https://e.com/a) - Tool\n",
            FIRST_LINE + 2,
            "end the description with a period",
            id="period",
        ),
        pytest.param(
            "## Tools\n\n- [A](https://e.com/a) - Powerful tool.\n",
            FIRST_LINE + 2,
            'drop the marketing word "Powerful"',
            id="marketing",
        ),
        pytest.param(
            "## Tools\n\n- [A](https://e.com/a) - Tool built on open-source code.\n",
            FIRST_LINE + 2,
            'drop the marketing word "open-source"',
            id="open-source",
        ),
        pytest.param(
            "## Tools\n\n- [A](http://e.com/a) - Tool.\n",
            FIRST_LINE + 2,
            "use an https link",
            id="http",
        ),
        pytest.param(
            "## Tools\n\n- [A](https://pypi.org/project/a) - Tool.\n",
            FIRST_LINE + 2,
            "not a package registry page",
            id="registry",
        ),
        pytest.param(
            "## API Clients\n\n- [A](https://e.com/a) - Client.\n",
            FIRST_LINE + 2,
            "API Clients entries go under a language subsection",
            id="no-subsection",
        ),
        pytest.param(
            "## Tools\n\n### Python\n\n- [A](https://e.com/a) - Tool.\n",
            FIRST_LINE + 2,
            "only API Clients has subsections",
            id="subsection-elsewhere",
        ),
        pytest.param(
            "## API Clients\n\n### Python\n\n- [A](https://e.com/a) - Client.\n\n"
            "### JavaScript\n\n- [B](https://e.com/b) - Client.\n",
            FIRST_LINE + 6,
            'subsection "JavaScript" must come before "Python"',
            id="subsection-order",
        ),
        pytest.param(
            "## API Clients\n\n### JavaScript\n\n"
            "### Python\n\n- [A](https://e.com/a) - Client.\n",
            FIRST_LINE + 2,
            'subsection "JavaScript" is empty',
            id="empty-subsection",
        ),
        pytest.param(
            "## API Clients\n\n### Python\n\n## Tools\n",
            FIRST_LINE + 2,
            'subsection "Python" is empty',
            id="empty-last-subsection",
        ),
        pytest.param(
            "## Tools\n\nSome tools worth a look.\n",
            FIRST_LINE + 2,
            "sections hold only entries",
            id="paragraph",
        ),
        pytest.param(
            "## Tools\n\n- [A](https://e.com/a)\n",
            FIRST_LINE + 2,
            "entry must read",
            id="format",
        ),
        pytest.param(
            "## Tools\n\n- [A](https://github.com/o/a) - Tool.\n"
            "- [B](https://github.com/O/A/) - Same tool.\n",
            FIRST_LINE + 3,
            f"duplicates the entry on line {FIRST_LINE + 2}",
            id="duplicate",
        ),
    ],
)
def test_one_problem_per_violation(body, line, message):
    _, problems = check(body)
    assert len(problems) == 1, problems
    assert problems[0].line == line
    assert message in problems[0].message


def test_marketing_words_match_whole_words_only():
    _, problems = check("## Tools\n\n- [A](https://e.com/a) - Bestow tags.\n")
    assert problems == []


def test_missing_contents_is_one_problem():
    entries, problems = parse("# Awesome Discogs\n\n## Tools\n")
    assert entries == []
    assert [(p.line, p.message) for p in problems] == [
        (None, 'the list needs a "## Contents" heading')
    ]
