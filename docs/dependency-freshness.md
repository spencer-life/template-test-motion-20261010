# Start current, then stay reproducible

Reproducible installs and current dependencies answer different questions.
Pinned tools and committed lockfiles reproduce the chosen inputs. `mise install`,
`npm ci`, and other frozen installs do not establish that those inputs are fresh.
An official scaffold tagged `latest` can select older vendor-tested packages.

## Required new-project freshness gate

New repositories must start with the newest stable, supported versions that work
together for the chosen stack and deployment target. Do not blindly inherit old
template pins, scaffold defaults, cached installs, or version numbers in examples.
Review newer major releases at setup rather than hiding behind the template's
old major. Prefer the current supported release line; use an older line only
with a documented compatibility, support, or approved release-age reason.

Inventory every versioned input the generated project actually uses: runtime and
compiler, package manager, global/task-scoped mise tools, direct application and
development dependencies, resolved transitive dependencies, GitHub Actions and
reusable-workflow revisions, and container/service images where present. Check
official registries or upstream releases at setup time. Review engine and peer
constraints, support status, platform compatibility and applicable advisories.
Use stable releases by default; prereleases need an explicit project decision.

Update compatible selections and regenerate the existing lockfile with its owner.
Review major migrations before applying them. Pin the resulting tool versions,
commit lockfiles, and retain immutable reviewed Action SHAs/digests where used;
fresh setup does not mean floating `latest` during CI. For copied registry
components and skills, inspect the current upstream revision and local changes;
a package update cannot maintain copied source automatically.

Record check time, sources, selected versions, newer releases considered, and
every justified hold with its reason, owner and review date in the setup record
or pull request. Missing network access or unsupported inventory means incomplete
coverage, not permission to call dependencies current. Do not suppress Renovate
or security alerts to make setup look clean. Releases after the check can
legitimately produce new PRs; zero future update PRs is not a completion guarantee.

Before the first development commit, after mechanical initialization and the
chosen scaffold, query live registries/tool sources and record the check time,
selected versions, supported constraints, newest eligible releases, and available
major upgrades. Use the project's validated freshness task or native inventory
and audit tools. Review compatible updates, regenerate the existing lockfile with
its owner, and run the actual project checks. Record unavailable/unsupported
coverage explicitly; cached installs and passing CI are not freshness evidence.
Use `docs/bootstrap.md` for the initial setup record and
`mise run deps:freshness -- --output .repo-state/freshness.json` for a current
inventory.

For hosted repositories using Renovate, keep compatible updates moving through
the existing maintenance flow. Verify bot access and recent Dashboard/run
activity at setup and when returning to a project; periodically review unresolved
updates and tool pins. For local-only projects, run the validated freshness task
or native inventory and audit commands at setup, when returning to development,
and after material stack changes; review and apply compatible updates manually.
Local-only projects do not need a hosted bot or background automation. Release-age
cooldowns reduce immediate exposure to new releases; they do not detect stale
pins, prove compatibility, or guarantee a merge. Maintain reproducibility while
reviewing updates intentionally. Major upgrades require manual migration review.

A vendor/SDK-supported older version can be intentional. Record its constraint or
hold with the selected version, reason, accountable owner, and future review date.
Recheck on expiry, vendor changes, or a material stack/runtime change. An expired
or unexplained hold requires review. Do not blindly replace pins with `latest` or
assume equal release numbers mean coupled packages are compatible.

Review security findings promptly in a separate lane. Ordinary cooldowns and
compatibility holds must not hide or delay the security decision. A fix still
needs relevant checks and migration review; availability, severity, exposure,
and accepted risk determine urgency. Audit coverage is limited to supported
sources/ecosystems, so report manual tool/vendor advisory review and unknown
coverage separately. No freshness policy grants automerge, deployment, new app
permissions, or repository-security-settings authority.

References: [mise upgrade](https://mise.jdx.dev/cli/upgrade.html),
[mise locks](https://mise.jdx.dev/dev-tools/mise-lock.html),
[npm frozen installation](https://docs.npmjs.com/cli/v11/commands/npm-ci/),
[Renovate release age](https://docs.renovatebot.com/key-concepts/minimum-release-age/),
and [Expo SDK compatibility](https://docs.expo.dev/workflow/upgrading-expo-sdk-walkthrough/).
