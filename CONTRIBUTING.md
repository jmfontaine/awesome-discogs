# Contribution Guidelines

This list curates the best Discogs tools, not every one of them. Before you open a pull request, check that the entry meets the criteria below. To suggest a tool without editing the list yourself, open an issue with the "Suggest an entry" form.

## Inclusion Criteria

An entry must be:

- **Discogs-specific.** It uses the Discogs API, the data dumps, or the Discogs site as a core part of what it does. A general music tool with an optional Discogs plugin belongs here only through that plugin.
- **Maintained.** It has a commit or a release in the last 12 months, and its repository is not archived. Deprecated projects are not accepted.
- **Established.** Its first commit is at least 180 days old; for a project without a public repository, its first public release is. Younger projects can be suggested again once they reach that age.
- **Documented.** Its readme or website explains how to install and use it.
- **Compliant with the [API Terms of Use](https://support.discogs.com/hc/en-us/articles/360009334593-API-Terms-of-Use).** Tools that work by scraping the site against those terms are not accepted.

Paid, source-available and closed-source tools are accepted when they meet the same criteria. Flag them with the markers below.

## What Does Not Qualify

- General music tools whose Discogs support is one option among many, unless that support is a separate plugin you can link to.
- Forks that add nothing substantial to a listed project.
- Tutorials, blog posts, example code, course projects, and one-off scripts.
- Sites and bots that only serve their author's own collection or account.

## Entry Format

```md
- [Name](https://link.to/project) - Short description of what it does.
```

- Link to the project's repository or official website, not to a blog post or a package registry page.
- Use the project's own spelling of its name.
- Separate the link and the description with ` - ` (space, hyphen, space).
- Start the description with a capital letter and end it with a period.
- Describe what the tool does in one sentence, without repeating the project's name.
- Leave out marketing words: best, powerful, amazing, awesome, ultimate, seamless, effortless, blazing, cutting-edge, state-of-the-art, world-class, revolutionary. Unmarked entries are open source, so don't say it; the markers flag the rest.
- Add `(paid)` before the final period when the main features require payment. Add `(source available)` when the source code is public but not under a license approved by the [Open Source Initiative](https://opensource.org/licenses), including code published without a license, and `(closed source)` when the source code is not public. Combine them as `(paid, source available)` or `(paid, closed source)`.
- Use an `https` link.
- Keep entries in alphabetical order within their section.
- Don't hard-wrap lines.

Example:

```md
- [Example Tool](https://github.com/example/example-tool) - Export a Discogs collection to CSV (paid).
```

## Sections

Add each entry to the section that best describes its main purpose. The API Clients section groups clients under one subsection per language; create the subsection when its first client arrives, and add it to the Contents list. To propose a new section, open an issue first. Only API Clients has subsections, in alphabetical order.

## Removal

- Entries that stop meeting the criteria are removed.
- When you spot one, open a "Report a problem" issue. Or open a pull request that deletes the line, adds a `removed` record to `decisions.yml`, and is titled `fix: remove <Name> (<reason code>)`.
- Exception: a feature-complete project that still works with Discogs can stay without recent activity; see [Decisions](#decisions).

## Decisions

`decisions.yml` records the decisions the list itself doesn't show: suggestions that were rejected, entries that were removed, and quiet projects kept on purpose. Check it before you suggest a tool.

It is a list with one record per project. Put `name` and `note` in double quotes: unquoted, a ` #` cuts the text short and a `: ` breaks the file.

|Field|Content|
|---|---|
|`name`|Project name, in double quotes|
|`url`|`https` link|
|`outcome`|`rejected`, `removed` or `kept`|
|`reason`|A reason code|
|`date`|Date of the decision, `YYYY-MM-DD`, unquoted|
|`reference`|URL of the issue, pull request or discussion in this repository where the decision was made|
|`note`|One sentence of evidence, in double quotes|
|`revisit_after`|Optional date, `YYYY-MM-DD`, unquoted|

- A rejected or removed project can be suggested again once its reason no longer holds, and not before its `revisit_after` date when it has one. The pull request that adds it back deletes its record and says what changed.
- `too-new` records set `revisit_after` to the first commit date plus 180 days.
- A `kept` record needs `revisit_after`, at most 365 days after `date`: the date when the project gets another look.

### Reason Codes

The maintainers paste the Reply when closing; `<…>` marks the parts to fill in. Every reply to a rejection starts with "Thanks for the suggestion."

|Code|Outcomes|Meaning|Reply|
|---|---|---|---|
|`not-discogs-specific`|rejected, removed|Discogs isn't a core part of what it does.|"This list covers tools built around Discogs, and Discogs is one option among many here."|
|`unmaintained`|rejected, removed|No commit or release in the last 12 months.|"The list needs a commit or a release in the last 12 months; the latest is from \<date\>. Suggest it again once it's active."|
|`archived`|rejected, removed|Repository archived, or project deprecated.|"The repository is archived (or the project deprecated), so it can't be listed."|
|`gone`|removed|The repository and website no longer exist.|"The project's repository and website no longer exist."|
|`undocumented`|rejected, removed|No install and usage instructions.|"Its readme or website needs to explain how to install and use it. Suggest it again once it does."|
|`terms-of-use`|rejected, removed|Works against the API Terms of Use, such as by scraping.|"It \<does X\>, which the Discogs API Terms of Use don't allow."|
|`too-new`|rejected|First commit less than 180 days old.|"The list accepts projects whose first commit is at least 180 days old. Suggest it again after \<revisit_after\>."|
|`duplicate`|rejected, removed|Already listed, or a fork adding nothing substantial.|"It's already listed as \<entry\>." or "It's a fork of \<listed project\> without substantial additions."|
|`out-of-scope`|rejected, removed|Matches What Does Not Qualify.|"\<Kind of project\> is outside what the list covers; see What Does Not Qualify."|
|`editorial`|rejected, removed|Meets the criteria but falls short of the listed alternatives; the note says how.|"The list curates the best tools, and \<listed alternative\> covers the same need with \<difference\>."|
|`feature-complete`|kept|No recent activity, but complete and still working with Discogs.|(none)|

## Pull Requests

- Add one entry per pull request.
- Title the pull request as a [Conventional Commit](https://www.conventionalcommits.org/) without a scope: `feat: add <Name>` for a new entry, `fix: <description>` for a correction or a removal. The title becomes the commit on `main`.
- Explain in the description why the tool deserves a place in the list.
- Sign your commits if you can. Edits made in GitHub's web editor are signed for you.
- Check the two entries above and below yours. If one no longer meets the criteria, say so in the pull request description.
- Run `just lint` and `just links` before you submit, or let the checks run on the pull request.
