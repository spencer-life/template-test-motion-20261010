# Tempo Board

Tempo Board is a small browser app for arranging personal focus sessions and
working through one timer at a time. This repository is a starter: its sample
sessions and controls are intentionally simple, with no account, backend,
notifications, or storage. Session edits live only for the current page load.

## Get started

Install [mise](https://mise.jdx.dev/) and review the repository's `mise.toml`
before trusting it. From the repository root:

```sh
mise trust
mise run setup
mise run dev
```

The development server prints its local URL. `mise run setup` installs the
pinned Node.js and aube versions, validates the repository tasks, checks core
configuration, and installs the frozen app dependencies. The first setup needs
network access to the official tool and npm registries.

## Checks

| Command | What it checks |
| --- | --- |
| `mise run format` | Format Python, TOML, and app sources |
| `mise run ci` | Run formatting, lint, type, unit, and production build checks |
| `mise run security` | Audit GitHub Actions and scan Git history for secrets |
| `mise run deps:freshness -- --output .repo-state/freshness.json` | Review current versions and lockfile advisories |

App checks can also be run separately with `mise run app:lint`,
`mise run app:typecheck`, `mise run app:test`, and `mise run app:build`.

## Project notes

- The interface is a single responsive Vite + TypeScript screen. Its queue and
  timer are client-side state; refreshing the page restores the sample plan.
- Design choices and product scope live in [PRODUCT.md](PRODUCT.md) and
  [DESIGN.md](DESIGN.md).
- Development instructions and project-local design guidance live in
  [AGENTS.md](AGENTS.md) and [`.agents/skills`](.agents/skills/).
- Repository setup and dependency decisions are recorded in
  [the stack notes](docs/stacks.md) and [freshness guidance](docs/dependency-freshness.md).

## License

Project-authored starter files use the MIT License. The copied design guidance
in `.agents/skills` carries its own upstream license files.
