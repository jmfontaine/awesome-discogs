"""Pelican settings for the single-page website built from README.md.

Build with `just site`. The page lists the entries that `tools.readme` parses from
README.md, so the website never holds a second copy of the list.
"""

import re
import sys
from dataclasses import dataclass, field
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.readme import DESCRIPTION, parse  # noqa: E402

LINK = re.compile(r"\[(?P<text>[^\]]+)\]\((?P<url>[^)\s]+)\)")


@dataclass(frozen=True)
class Tool:
    name: str
    url: str
    description: str
    markers: tuple[str, ...]


@dataclass
class Group:
    title: str | None
    slug: str
    tools: list[Tool] = field(default_factory=list)


@dataclass
class Section:
    title: str
    slug: str
    groups: list[Group] = field(default_factory=list)


def _slugger():
    """Return a function that gives each heading the anchor GitHub gives it.

    GitHub suffixes repeated anchors with -1, -2, and so on, so README links keep
    working on the website.
    """
    seen: dict[str, int] = {}

    def slug(title: str) -> str:
        base = re.sub(r"[^\w\- ]", "", title.lower()).replace(" ", "-")
        count = seen.get(base, 0)
        seen[base] = count + 1
        return f"{base}-{count}" if count else base

    return slug


def _summary(readme: str) -> str:
    """Return the README's opening quote as HTML, with its links kept."""
    quote = next((line for line in readme.splitlines() if line.startswith("> ")), None)
    if quote is None:
        raise SystemExit("README.md needs a `> ` quote that describes Discogs")
    text = escape(quote.removeprefix("> "))
    return LINK.sub(lambda m: f'<a href="{m["url"]}">{m["text"]}</a>', text)


def _sections(readme: str) -> list[Section]:
    entries, problems = parse(readme)
    if problems:
        details = "\n".join(
            f"  line {p.line}: {p.message}" if p.line else f"  {p.message}"
            for p in problems
        )
        raise SystemExit(f"README.md has problems, run `just lint`:\n{details}")

    slug = _slugger()
    sections: list[Section] = []
    for entry in entries:
        if not sections or sections[-1].title != entry.section:
            sections.append(Section(entry.section, slug(entry.section)))
        section = sections[-1]
        if not section.groups or section.groups[-1].title != entry.subsection:
            group_slug = slug(entry.subsection) if entry.subsection else section.slug
            section.groups.append(Group(entry.subsection, group_slug))
        described = DESCRIPTION.match(entry.description)
        markers = described["markers"] if described else None
        section.groups[-1].tools.append(
            Tool(
                entry.name,
                entry.url,
                f"{described['text']}." if described else entry.description,
                tuple(markers.split(", ")) if markers else (),
            )
        )
    return sections


_README = (ROOT / "README.md").read_text(encoding="utf-8")

SITENAME = "Awesome Discogs"
SITEURL = ""
RELATIVE_URLS = True
REPOSITORY = "https://github.com/jmfontaine/awesome-discogs"
SUMMARY = _summary(_README)
SECTIONS = _sections(_README)
TOOL_COUNT = sum(len(g.tools) for s in SECTIONS for g in s.groups)

# The site has no articles or pages: only the theme's index.html.
PATH = str(ROOT / "site")
ARTICLE_PATHS: list[str] = []
PAGE_PATHS: list[str] = []
STATIC_PATHS: list[str] = []
DIRECT_TEMPLATES = ["index"]
THEME = str(ROOT / "site" / "theme")
JINJA_ENVIRONMENT = {"autoescape": True, "trim_blocks": True, "lstrip_blocks": True}
OUTPUT_PATH = str(ROOT / "site" / "output")
DELETE_OUTPUT_DIRECTORY = True

FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None
TIMEZONE = "UTC"
DEFAULT_LANG = "en"
