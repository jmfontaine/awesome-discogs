set quiet := true

_list:
    just --list

# Check the list against the Awesome guidelines
lint:
    npx --yes awesome-lint README.md

# Check every link in the list and its guidelines
links:
    uvx --from lychee-bin lychee --config lychee.toml README.md CONTRIBUTING.md
