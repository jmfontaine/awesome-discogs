set quiet := true

_list:
    just --list

# Check the list against the Awesome guidelines and the contribution guidelines
lint:
    npx --yes awesome-lint README.md
    uv run python -m tools check

# Check every link in the list and its guidelines
links:
    uvx --from lychee-bin lychee --config lychee.toml README.md CONTRIBUTING.md

# Report listed GitHub projects that no longer meet the inclusion criteria
audit:
    GITHUB_TOKEN="${GITHUB_TOKEN:-$(gh auth token)}" uv run python -m tools audit

# Format the checking tools
format:
    uv run ruff format
    uv run ruff check --fix

# Run every check on the list and its tools
qa: lint
    uv run ruff format --check
    uv run ruff check
    uv run pytest
