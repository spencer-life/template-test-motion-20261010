# Bootstrap freshness check

After mechanical initialization and the chosen official scaffold, before the
first development commit, run `mise run deps:freshness -- --output .repo-state/freshness.json`.
Review the timestamped report, select compatible updates deliberately, regenerate
the existing lockfile with its owner, and run the real project checks. Rerun after
updating; keep concise evidence in `docs/bootstrap.md` or the pull request. This task never installs,
rewrites requests, or upgrades dependencies. Do not add it to frozen CI installs:
normal CI validates reproducibility; live registry checks require network access.

The adapter is one input to the [required freshness gate](dependency-freshness.md#required-new-project-freshness-gate),
not a complete inventory of every tool or ecosystem. Separately inspect inputs
outside its scope, including GitHub Action/reusable-workflow pins, container
images, and copied component/skill revisions. Its compatible-major result does
not discharge the new-project requirement to review newer stable major releases.
Use native inventories and official upstream checks for uncovered inputs, and
record unresolved coverage before declaring setup complete.

The initial adapter inventories root `mise.toml` tools, including task/template
pins, root npm v2/v3 lockfiles, and root pnpm/aube lockfiles through the
project-pinned `aube list --json --depth 0 --lockfile-only` inventory. Exactly one lockfile owner
is required; no conversion or competing lockfile is created. Direct dependencies
are queried through npm registry metadata with its native range semantics. npm queries use
its configured registry and `--prefer-online`; mise queries bypass its versions
host with an expired remote cache. Every row records the selected request/lock
version, current eligible release, latest available release, and the check time.
The tool's source can omit release dates; the report does not claim release-age
verification. npm includes the eligible release's published time.

Default eligibility stays within the selected stable major, the selected minor
for pre-1.0 packages, and the selected Python runtime minor. An exact npm pin is
compared with its compatible caret range so exact pins cannot silently hide drift;
other npm ranges remain constraints. These are conservative candidate boundaries,
not proof of API compatibility, engine support, peer compatibility, or vendor
support. Review release notes and actual runtime/SDK constraints before applying
updates. Breaking majors are visible as `latest` and require manual planning.

A project's optional `dependency-freshness.json` records tighter numeric tool
prefixes and justified holds. For example:

```json
{
  "tool_constraints": {
    "mise:node": {
      "prefix": "24",
      "reason": "Supported deployment runtime",
      "owner": "runtime maintainer",
      "review_on": "2026-10-20"
    }
  },
  "holds": {
    "npm:react": {
      "selected": "19.0.0",
      "reason": "Chosen Expo SDK requires this version; see setup issue",
      "owner": "mobile maintainer",
      "review_on": "2026-10-20"
    }
  }
}
```

Replace example dates and versions with the actual decision. Holds bind to the
selected version and expire on the review date. Unknown dependencies, missing
owners/reasons, expired dates, and changed versions fail the check. Holds preserve
ordinary update visibility and cannot suppress security findings. Tool constraints
must identify an actually declared tool; require a reason, owner, and future
review date. Use a hold for a deferred eligible update.

Exit `0` means current or explicitly held **within this adapter's declared scope**;
exit `1` means available updates, deprecation, or npm vulnerability findings need
review; exit `2` means incomplete, unsupported, failed source queries, or invalid
holds. Network errors and unsupported lockfiles never become a clean result.
Security uses `npm audit --package-lock-only --json` for npm lockfiles, or native
`aube audit --json --audit-level info` for pnpm/aube lockfiles, separately from ordinary updates.
Both include transitive lockfile dependencies. No audit fix is applied.
Tool/vendor advisory review remains manual and is explicitly reported.

Yarn, Bun, workspaces, nested manifests, alternate mise configs, complex
tool declarations, overrides, and non-npm application ecosystems need their native
inventory/security adapter. This checker does not create a competing npm lockfile
or replace the chosen package manager. If the project needs one of these, implement
and validate the native adapter before declaring its bootstrap review complete;
record blocked coverage explicitly. CI and hosted Renovate still need their own
checks and verified app access.

References: [mise remote versions](https://mise.jdx.dev/cli/ls-remote.html),
[mise cache lifetime](https://mise.jdx.dev/configuration/settings.html#fetch_remote_versions_cache),
[npm registry queries](https://docs.npmjs.com/cli/v11/commands/npm-view/), and
[npm audit](https://docs.npmjs.com/cli/v11/commands/npm-audit/),
[aube lockfiles](https://aube.sh/package-manager/lockfiles.html), and
[aube audit](https://aube.sh/cli/audit.html).
