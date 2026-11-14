# Contribution Guidelines

This list curates the best Discogs tools, not every one of them. Before you open a pull request, check that the entry meets the criteria below. To suggest a tool without editing the list yourself, open an issue with the "Suggest an entry" form.

## Inclusion Criteria

An entry must be:

- **Discogs-specific.** It uses the Discogs API, the data dumps, or the Discogs site as a core part of what it does. A general music tool with an optional Discogs plugin belongs here only through that plugin.
- **Maintained.** It has a commit or a release in the last 12 months, and its repository is not archived. Deprecated projects are not accepted.
- **Documented.** Its readme or website explains how to install and use it.
- **Compliant with the [API Terms of Use](https://support.discogs.com/hc/en-us/articles/360009334593-API-Terms-of-Use).** Tools that work by scraping the site against those terms are not accepted.

Paid and closed-source tools are accepted when they meet the same criteria. Flag them with the markers below.

## Entry Format

```md
- [Name](https://link.to/project) - Short description of what it does.
```

- Link to the project's repository or official website, not to a blog post or a package registry page.
- Use the project's own spelling of its name.
- Separate the link and the description with ` - ` (space, hyphen, space).
- Start the description with a capital letter and end it with a period.
- Describe what the tool does in one sentence. Don't repeat the project's name or use marketing language such as "best" or "powerful".
- Add `(paid)` before the final period when the main features require payment, and `(closed source)` when the source code is not public. Combine them as `(paid, closed source)`.
- Keep entries in alphabetical order within their section.
- Don't hard-wrap lines.

Example:

```md
- [Example Tool](https://github.com/example/example-tool) - Export a Discogs collection to CSV (paid).
```

## Sections

Add each entry to the section that best describes its main purpose. The API Clients section groups clients under one subsection per language; create the subsection when its first client arrives, and add it to the Contents list. To propose a new section, open an issue first.

## Removal

Entries that stop meeting the criteria, such as archived or abandoned projects, are removed. When you spot one, open an issue with the "Report a problem" form, or a pull request.

## Pull Requests

- Add one entry per pull request.
- Title the pull request as a [Conventional Commit](https://www.conventionalcommits.org/) without a scope: `feat: add <Name>` for a new entry, `fix: <description>` for a correction or a removal. The title becomes the commit on `main`.
- Explain in the description why the tool deserves a place in the list.
- Sign your commits if you can. Edits made in GitHub's web editor are signed for you.
- Run `just lint` and `just links` before you submit, or let the checks run on the pull request.
