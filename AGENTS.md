# Tempo Board contributor notes

Tempo Board is a browser-only Vite and TypeScript starter. Keep changes within
the small session queue and timer experience unless the project owner expands
its scope. Read `PRODUCT.md` and `DESIGN.md` before changing app behavior or
visual structure.

## Setup and checks

- Review `mise.toml`, then run `mise trust` and `mise run setup` on a new clone.
- Use `mise run dev` for local development.
- Run `mise run ci` after app or setup changes; run `mise run security` after
  workflow or security changes.
- Keep `pnpm-lock.yaml` as the single app lockfile and regenerate it through
  aube. Do not commit dependencies or build output.
- Keep the browser app client-side. The sample plan is synthetic and stays in
  memory; do not add network calls, analytics, or credentials without a clear
  product decision.

## Design and motion guidance

- For UI changes, use the applicable project skills in `.agents/skills` and
  follow [design setup](docs/design/setup.md). They are copied guidance, not
  installed tools; their reviewed upstream sources and revisions are recorded
  there.
- For animation changes, read both the local `animate` and
  `review-animations` skills. Respect reduced motion and keep state
  understandable without animation.
- For platform behavior not covered by the project guidance, consult the
  official Modern Web Guidance sources listed in the design setup notes.

## Delivery

Keep commits focused. For hosted changes, open a pull request against `main`
and report the checks that actually ran. Never put credentials, private user
data, local state, or unrelated workspace files in a commit.
