# Contributing

Review `mise.toml`, then run `mise trust` and `mise run setup` for a new
checkout. Use `mise run dev` to start the app. Before submitting changes, run
`mise run ci`; run `mise run security` when changing workflows or security
checks. Report any unavailable checks accurately.

Keep changes focused on the browser-only starter and follow `PRODUCT.md`,
`DESIGN.md`, and `AGENTS.md`. Update the README when setup commands or project
scope change. Commit the app manifest and its single `pnpm-lock.yaml` together.
Do not commit secrets, local state, dependencies, or build output.

Hosted contributions should use a pull request against `main` with a summary
and the commands and results for relevant checks.
