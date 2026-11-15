"""Parse the list in README.md and check its entries against CONTRIBUTING.md.

awesome-lint already checks the ` - ` separator, the initial capital, the final
punctuation, descriptions starting with the name, duplicate exact links and the
Contents list, so these rules leave them out.
"""

import re
from dataclasses import dataclass
from urllib.parse import urlsplit

from tools.problems import Problem
from tools.urls import normalize

ENTRY = re.compile(
    r"^- \[(?P<name>[^\]]+)\]\((?P<url>[^)\s]+)\) - (?P<description>.+)$"
)
MARKERS = (
    "paid",
    "source available",
    "closed source",
    "paid, source available",
    "paid, closed source",
)
DESCRIPTION = re.compile(
    r"^(?P<text>.+?)"
    r"(?: \((?P<markers>" + "|".join(re.escape(m) for m in MARKERS) + r")\))?\.$"
)
MARKER_TEXT = re.compile(r"\(paid|source available|closed source", re.IGNORECASE)
SOURCE_MARKERS = ("source available", "closed source")

# The words CONTRIBUTING.md asks entries to leave out.
MARKETING_WORDS = (
    "best",
    "powerful",
    "amazing",
    "awesome",
    "ultimate",
    "seamless",
    "effortless",
    "blazing",
    "cutting-edge",
    "state-of-the-art",
    "world-class",
    "revolutionary",
    "open source",
    "open-source",
)
MARKETING = re.compile(
    r"\b(?:" + "|".join(re.escape(word) for word in MARKETING_WORDS) + r")\b",
    re.IGNORECASE,
)

PACKAGE_REGISTRIES = frozenset(
    {
        "pypi.org",
        "npmjs.com",
        "www.npmjs.com",
        "crates.io",
        "rubygems.org",
        "pkg.go.dev",
        "packagist.org",
        "nuget.org",
        "www.nuget.org",
        "hex.pm",
        "metacpan.org",
    }
)

CONTENTS = "## Contents"
END_HEADINGS = frozenset({"## Contributing", "## Footnotes"})
SUBSECTION_PARENT = "API Clients"


@dataclass(frozen=True)
class Entry:
    line: int
    section: str
    subsection: str | None
    name: str
    url: str
    description: str

    @property
    def source(self) -> str | None:
        """Return the entry's source marker: source available or closed source."""
        described = DESCRIPTION.match(self.description)
        markers = (described["markers"] or "") if described else ""
        return next((m for m in SOURCE_MARKERS if m in markers), None)


@dataclass
class _Subsection:
    title: str
    line: int
    entries: int = 0


def parse(text: str, path: str = "README.md") -> tuple[list[Entry], list[Problem]]:
    """Return the entries of the list and the problems found in it."""
    entries: list[Entry] = []
    problems: list[Problem] = []

    def problem(line: int, message: str) -> None:
        problems.append(Problem(path, line, message))

    lines = text.splitlines()
    try:
        contents = next(i for i, line in enumerate(lines) if line.rstrip() == CONTENTS)
    except StopIteration:
        return [], [Problem(path, None, f'the list needs a "{CONTENTS}" heading')]

    section: str | None = None
    subsection: _Subsection | None = None
    previous_subsection: str | None = None
    previous_names: dict[tuple[str, str | None], str] = {}
    seen_urls: dict[str, int] = {}

    def close_subsection() -> None:
        if subsection is not None and subsection.entries == 0:
            problem(subsection.line, f'subsection "{subsection.title}" is empty')

    for number, raw in enumerate(lines[contents + 1 :], start=contents + 2):
        line = raw.rstrip()
        if line.startswith("## "):
            close_subsection()
            if line in END_HEADINGS:
                break
            section = line.removeprefix("## ").strip()
            subsection = None
            previous_subsection = None
            continue
        if section is None or not line:
            continue

        if line.startswith("### "):
            close_subsection()
            title = line.removeprefix("### ").strip()
            if section != SUBSECTION_PARENT:
                problem(number, "only API Clients has subsections")
                subsection = None
                continue
            if previous_subsection is not None and (
                title.casefold() < previous_subsection.casefold()
            ):
                problem(
                    number,
                    f'subsection "{title}" must come before "{previous_subsection}"',
                )
            subsection = _Subsection(title, number)
            previous_subsection = title
            continue

        if not line.startswith("- "):
            problem(number, "sections hold only entries")
            continue

        match = ENTRY.match(line)
        if match is None:
            problem(number, "entry must read `- [Name](https://link) - Description.`")
            continue

        name, url, description = match["name"], match["url"], match["description"]
        if subsection is not None:
            subsection.entries += 1
        elif section == SUBSECTION_PARENT:
            problem(number, "API Clients entries go under a language subsection")

        if not url.startswith("https://"):
            problem(number, "use an https link")
        if (urlsplit(url).hostname or "") in PACKAGE_REGISTRIES:
            problem(
                number,
                "link to the project's repository or website, "
                "not a package registry page",
            )

        described = DESCRIPTION.match(description)
        description_text = described["text"] if described else description
        if MARKER_TEXT.search(description_text):
            problem(
                number,
                "markers go before the final period: "
                + ", ".join(f"({m})" for m in MARKERS[:-1])
                + f" or ({MARKERS[-1]})",
            )
        elif described is None:
            problem(number, "end the description with a period")
        for word in MARKETING.finditer(description_text):
            problem(number, f'drop the marketing word "{word.group()}"')

        group = (section, subsection.title if subsection else None)
        previous_name = previous_names.get(group)
        if previous_name is not None and name.casefold() < previous_name.casefold():
            problem(number, f'"{name}" must come before "{previous_name}"')
        previous_names[group] = name

        key = normalize(url)
        if key in seen_urls:
            problem(number, f"duplicates the entry on line {seen_urls[key]}")
        else:
            seen_urls[key] = number

        entries.append(Entry(number, section, group[1], name, url, description))
    else:
        close_subsection()

    return entries, problems
