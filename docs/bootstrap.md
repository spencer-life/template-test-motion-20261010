# Starter setup record

## Origin and process

This repository started from the public `main` branch of
[`spencer-life/project-template`](https://github.com/spencer-life/project-template)
at source commit `6c934bca6f67dcbc1830d398edd4da9232be9fe2` on 2026-10-10. The
template's `scripts/project_init.py` was run in check mode and then applied for
repository name `template-test-motion-20261010` and public visibility. The
result was adapted to this app: template-only metadata, initialization code,
maintenance workflows and guidance were removed; the relevant public CI,
Renovate configuration, and reusable validation/security checks were retained.

The project followed the template's new-project and project-adaptation recipe,
its design setup and motion-skill instructions, and its dependency freshness
gate. Project adaptation used this tracked setup record in place of a hosted
issue. The setup is published on the `chore/tempo-board-starter` review branch
and proposed in a draft pull request against `main`, so it can be audited before
any merge. No issue, repository-setting changes, or deployment is part of the
starter.

## Stack and version choices

The official Vite scaffold was used as a starting point, then checked against
the current official sources for the chosen tools and packages. The app remains
a small, browser-only Vite + TypeScript screen with native controls, no framework,
and no backend. Node.js `24.21.0` satisfies the selected tool engine ranges.
At setup, the selected versions were mise `2026.10.7`, Python `3.12.15`, Node.js
`24.21.0`, aube `2.7.0`, Ruff `0.16.10`, Taplo `0.10.0`, rumdl `0.2.79`, Biome
`2.5.15`, Vite `8.3.4`, TypeScript `7.0.2`, Vitest `5.0.3`, and Inter Variable
`5.3.0`. Security task tools include actionlint `1.7.12`, uv `0.12.24`, Pyflakes
`4.0.3`, zizmor `1.30.1`, and Gitleaks `8.30.1`. The live freshness query found
rumdl `0.2.79` and uv `0.12.24` newer within their selected release lines, so
those pins were updated before the app commit. The Vite scaffold's TypeScript
range was updated to the current stable TypeScript 7 line after the tool's engine
requirements were checked.

The project-authored app source and documentation use the MIT License. The
template source at the recorded commit has no `LICENSE` file. Adapted template
infrastructure such as CI and validation scripts is identified by the source
commit above but is not covered by this new MIT grant. Copied skill guidance
stays under the separate upstream licenses included with each skill.

GitHub Actions use reviewed immutable pins: checkout `v7.0.1` at
`3d3c42e5aac5ba805825da76410c181273ba90b1`, cache `v6.1.0` at
`55cc8345863c7cc4c66a329aec7e433d2d1c52a9`, and mise-action `v5.1.1` at
`2d8d4cafcbd33be2ea37d2b6f5ad595363d1f1ca`. Renovate uses its public
`config:best-practices` preset and keeps automerge disabled.

## Template gaps addressed

- The source is a repository foundation rather than an app scaffold, so it had
  no application manifest, browser entry point, or actual product behavior.
- Its initializer retained private-template metadata and private workflow
  references; these were removed before publishing this public project.
- Its generic contributor, security, design, and stack guidance described
  template maintenance and private-owner processes. Those files were replaced
  with instructions and truthful security guidance for this standalone app.
- The template's base checks did not validate app code. This repository adds
  lint, typecheck, unit, build, and app configuration checks to mise and CI.

See the README for setup commands. The official registry inventory completed
at `2026-10-10T22:35:48Z`: all 16 declared tool and direct package rows were
current within their selected release ranges, there were no incomplete rows,
and the npm lock audit reported 0 advisories. Manual vendor-tool advisory review
remains outside the adapter's coverage. The generated freshness JSON lives in
ignored `.repo-state/` and is not committed.

The direct setup steps passed with project-pinned tools: mise task validation
(22 tasks), `python scripts/check.py`, and `aube install --frozen-lockfile`.
Local validation also passed 39 Python tooling tests, Ruff, Taplo, rumdl, Biome
format/lint, TypeScript, all 6 Vitest tests, the Vite production build,
actionlint, zizmor, and a Gitleaks directory scan. Impeccable reported no primary
findings, and desktop and mobile screenshots were reviewed.

The aggregate `mise run ci` did not complete in this restricted host: its mise
runner tried to install unrelated inherited tools, and its default aube virtual
store was under a read-only home directory. A clean `aube ci` install and the
component checks passed with caches isolated under `/tmp`. Hosted Actions have
not yet run for the draft pull request. The setup does not claim configured
branch protection, private vulnerability reporting, Renovate bot access, or
native skill discovery.
