# Application stack

Tempo Board is a single-page, client-side app built with Vite and TypeScript.
It uses native browser controls and CSS rather than a UI framework. Session
state lives in memory; there is no service, database, analytics, or network API.

## Tooling

- mise pins Node.js, Python, aube, and the repository lint tools.
- aube owns the `pnpm-lock.yaml` and runs the npm scripts.
- Biome formats and lints TypeScript and CSS; TypeScript checks types; Vitest
  tests timer calculations; Vite creates the production bundle.
- The app has one runtime package, self-hosted Inter Variable from
  `@fontsource-variable/inter`.

Keep the stack small. Add a framework, persistence, or remote service only when
an agreed product requirement calls for it. Use `mise run ci` as the local and
hosted check contract.

For version selection and current dependency review, see
[the setup record](bootstrap.md) and [freshness guidance](dependency-freshness.md).
