#!/usr/bin/env python3
"""Report live dependency freshness without installing or upgrading packages."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
import tomllib
from pathlib import Path

UNSUPPORTED_MANIFESTS = {
    "pyproject.toml",
    "requirements.txt",
    "Cargo.toml",
    "go.mod",
    "pom.xml",
    "build.gradle",
    "build.gradle.kts",
}


class CheckError(Exception):
    """The inventory is incomplete or unsupported."""


def version(value: str) -> tuple[int, int, int]:
    match = re.fullmatch(r"v?(\d+)\.(\d+)\.(\d+)", value)
    if not match:
        raise CheckError("only stable numeric X.Y.Z releases are supported")
    return tuple(int(n) for n in match.groups())


def query(command: list[str], root: Path, *, audit: bool = False):
    # Refresh upstream metadata; caches are not freshness evidence. Never echo
    # subprocess stderr, which may contain private registry URLs/credentials.
    env = dict(os.environ, MISE_FETCH_REMOTE_VERSIONS_CACHE="0s")
    try:
        result = subprocess.run(
            command, cwd=root, env=env, text=True, capture_output=True, timeout=90
        )
        value = json.loads(result.stdout)
    except (OSError, subprocess.TimeoutExpired, ValueError) as exc:
        raise CheckError(f"{command[0]} query failed or returned invalid JSON") from exc
    if result.returncode not in ({0, 1} if audit else {0}) or (
        isinstance(value, dict) and "error" in value
    ):
        raise CheckError(f"{command[0]} query failed (exit {result.returncode})")
    return value


def newest(releases: list[str]) -> str:
    stable = []
    for item in releases:
        try:
            stable.append((version(item), item))
        except CheckError:
            continue
    if not stable:
        raise CheckError("source returned no supported stable releases")
    return max(stable)[1]


def prefix_for(selected: str, runtime: bool = False) -> str:
    major, minor, _ = version(selected)
    # Pre-1.0 minors and Python runtime minors can be breaking/support boundaries.
    return f"{major}.{minor}" if runtime or major == 0 else str(major)


def eligible(releases: list[str], prefix: str) -> str:
    if not re.fullmatch(r"\d+(?:\.\d+){0,2}", prefix):
        raise CheckError("supported tool constraints are numeric release prefixes")
    return newest([r for r in releases if r == prefix or r.startswith(prefix + ".")])


def policy(root: Path) -> dict:
    path = root / "dependency-freshness.json"
    data = json.loads(path.read_text()) if path.exists() else {}
    if not isinstance(data, dict):
        raise CheckError("freshness policy must be an object")
    if set(data) - {"tool_constraints", "holds"}:
        raise CheckError("unknown freshness policy field")
    if not isinstance(data.get("tool_constraints", {}), dict) or not isinstance(
        data.get("holds", {}), dict
    ):
        raise CheckError("tool_constraints and holds must be objects")
    return data


def apply_hold(row: dict, holds: dict, today: dt.date) -> None:
    hold = holds.get(row["id"])
    if hold is None:
        return
    required = {"selected", "reason", "owner", "review_on"}
    if (
        not isinstance(hold, dict)
        or set(hold) != required
        or any(not isinstance(hold[k], str) or not hold[k].strip() for k in required)
    ):
        raise CheckError(f"{row['id']}: hold needs selected, reason, owner, review_on")
    try:
        review = dt.date.fromisoformat(hold["review_on"])
    except ValueError as exc:
        raise CheckError(f"{row['id']}: invalid hold review date") from exc
    if row.get("status") == "incomplete" or "selected" not in row:
        raise CheckError(f"{row['id']}: cannot apply a hold to an incomplete inventory")
    if review <= today or hold["selected"] != row["selected"]:
        raise CheckError(f"{row['id']}: hold expired or selected version changed")
    row["hold"] = hold
    if row["status"] == "update-available":
        row["status"] = "held"


def tool_inventory(root: Path, config: dict, rules: dict, today: dt.date) -> list[dict]:
    declarations = dict(config.get("tools", {}))
    for section in ("tasks", "task_templates"):
        for entry in config.get(section, {}).values():
            for name, requested in entry.get("tools", {}).items():
                if name in declarations and declarations[name] != requested:
                    raise CheckError(f"mise:{name}: conflicting task-level pins")
                declarations[name] = requested
    rows = []
    for name, requested in sorted(declarations.items()):
        row = {"id": f"mise:{name}", "declared": requested, "source": "mise ls-remote"}
        try:
            if not isinstance(requested, str):
                raise CheckError("table-form tool declarations need a native adapter")
            version(requested)
            row["selected"] = requested
            prefix = prefix_for(requested, name == "python")
            constraint = rules.get("tool_constraints", {}).get(row["id"])
            if constraint is not None:
                if not isinstance(constraint, dict) or set(constraint) != {
                    "prefix",
                    "reason",
                    "owner",
                    "review_on",
                }:
                    raise CheckError(
                        "tool constraint needs prefix, reason, owner, review_on"
                    )
                temporary = {
                    "id": row["id"],
                    "selected": requested,
                    "status": "current",
                }
                apply_hold(
                    temporary,
                    {
                        row["id"]: {
                            "selected": requested,
                            **{
                                k: constraint[k]
                                for k in ("reason", "owner", "review_on")
                            },
                        }
                    },
                    today,
                )
                prefix = constraint["prefix"]
                row["constraint_review"] = constraint
            if eligible([requested], prefix) != requested:
                raise CheckError("selected tool is outside its supported prefix")
            remote = query(
                ["mise", "ls-remote", name, "--json", "--no-versions-host"], root
            )
            if not isinstance(remote, list) or not remote:
                raise CheckError("tool source returned no release inventory")
            releases = [r["version"] if isinstance(r, dict) else r for r in remote]
            row.update(
                constraint=prefix,
                latest=newest(releases),
                current_eligible=eligible(releases, prefix),
            )
            if requested not in releases:
                raise CheckError("selected version absent from live source")
            dates = {
                r["version"]: r.get("created_at") for r in remote if isinstance(r, dict)
            }
            row["eligible_published_at"] = dates.get(row["current_eligible"])
            row["status"] = (
                "update-available"
                if version(row["current_eligible"]) > version(requested)
                else "current"
            )
        except (CheckError, KeyError, TypeError) as exc:
            row.update(status="incomplete", error=str(exc))
        rows.append(row)
    unknown = set(rules.get("tool_constraints", {})) - {r["id"] for r in rows}
    if unknown:
        raise CheckError("tool constraints refer to undeclared tools")
    return rows


def npm_inventory(root: Path, manifest: dict, lock: dict) -> list[dict]:
    if not isinstance(manifest, dict) or not isinstance(lock, dict):
        raise CheckError("manifest and lockfile must be objects")
    if any(
        manifest.get(key) for key in ("workspaces", "overrides", "resolutions")
    ) or lock.get("lockfileVersion") not in {2, 3}:
        raise CheckError(
            "npm workspaces, overrides, or legacy lockfile need a native adapter"
        )
    packages = lock.get("packages", {})
    rows = []
    for section in (
        "dependencies",
        "devDependencies",
        "optionalDependencies",
        "peerDependencies",
    ):
        for name, declared in sorted(manifest.get(section, {}).items()):
            row = {"id": f"npm:{name}", "declared": declared, "source": "npm registry"}
            try:
                if not isinstance(declared, str) or not re.fullmatch(
                    r"[0-9<>=~^*xX| .-]+", declared
                ):
                    raise CheckError("non-registry package specs need a native adapter")
                selected = packages.get(f"node_modules/{name}", {}).get("version", "")
                version(selected)
                row["selected"] = selected
                # Verify manifest and lock agree before treating selected as usable.
                allowed = query(
                    [
                        "npm",
                        "view",
                        f"{name}@{declared}",
                        "version",
                        "--json",
                        "--prefer-online",
                    ],
                    root,
                )
                allowed = [allowed] if isinstance(allowed, str) else allowed
                if selected not in allowed:
                    raise CheckError("selected lock version does not satisfy manifest")
                exact = bool(re.fullmatch(r"\d+\.\d+\.\d+", declared))
                constraint = f"^{selected}" if exact else declared
                candidates = query(
                    [
                        "npm",
                        "view",
                        f"{name}@{constraint}",
                        "version",
                        "--json",
                        "--prefer-online",
                    ],
                    root,
                )
                candidates = [candidates] if isinstance(candidates, str) else candidates
                metadata = query(
                    ["npm", "view", f"{name}@{selected}", "--json", "--prefer-online"],
                    root,
                )
                current = eligible(candidates, prefix_for(selected))
                row.update(
                    constraint=constraint,
                    current_eligible=current,
                    latest=metadata["dist-tags"]["latest"],
                    eligible_published_at=metadata["time"][current],
                    deprecated=metadata.get("deprecated"),
                    status="update-available"
                    if version(current) > version(selected)
                    else "current",
                )
                if row["deprecated"]:
                    row["status"] = "update-available"
            except (CheckError, KeyError, TypeError) as exc:
                row.update(status="incomplete", error=str(exc))
            rows.append(row)
    return rows


def application_lock(root: Path) -> tuple[dict, bool]:
    names = (
        "aube-lock.yaml",
        "pnpm-lock.yaml",
        "bun.lock",
        "yarn.lock",
        "npm-shrinkwrap.json",
        "package-lock.json",
    )
    found = [name for name in names if (root / name).is_file()]
    if len(found) != 1:
        raise CheckError(
            "application needs exactly one supported lockfile; "
            "missing or competing owners are unsupported"
        )
    if found[0] in {"package-lock.json", "npm-shrinkwrap.json"}:
        return json.loads((root / found[0]).read_text()), False
    if found[0] not in {"aube-lock.yaml", "pnpm-lock.yaml"}:
        raise CheckError(
            f"{found[0]}: unsupported; add a native inventory/audit adapter"
        )
    data = query(["aube", "list", "--json", "--depth", "0", "--lockfile-only"], root)
    if not isinstance(data, list) or len(data) != 1 or not isinstance(data[0], dict):
        raise CheckError(
            "aube list must return exactly one root project; workspaces need an adapter"
        )
    packages = {}
    for section in (
        "dependencies",
        "devDependencies",
        "optionalDependencies",
        "peerDependencies",
    ):
        for name, entry in data[0].get(section, {}).items():
            packages[f"node_modules/{name}"] = {"version": entry.get("version")}
    # Normalize only in memory; never convert or create a competing lockfile.
    return {"lockfileVersion": 3, "packages": packages}, True


def security(root: Path, has_npm: bool, native_aube: bool = False) -> dict:
    result = {"tools": "manual vendor advisory review required; not automated"}
    if not has_npm:
        return {**result, "npm": "not applicable"}
    if native_aube:
        audit = query(
            ["aube", "audit", "--json", "--audit-level", "info"], root, audit=True
        )
        if not isinstance(audit, dict):
            raise CheckError("aube audit returned an unsupported report")
        counts = audit.get("metadata", {}).get("vulnerabilities", {})
        severities = {"info", "low", "moderate", "high", "critical"}
        if (
            not isinstance(audit.get("advisories"), dict)
            or set(counts) != severities
            or any(type(n) is not int or n < 0 for n in counts.values())
        ):
            raise CheckError("aube audit returned an unsupported report")
        return {
            **result,
            "npm": audit["advisories"],
            "total": sum(counts.values()),
            "adapter": "aube audit",
        }
    audit = query(["npm", "audit", "--json", "--package-lock-only"], root, audit=True)
    if not isinstance(audit, dict):
        raise CheckError("npm audit returned an unsupported report")
    if not isinstance(audit.get("vulnerabilities"), dict) or not isinstance(
        audit.get("metadata", {}).get("vulnerabilities", {}).get("total"), int
    ):
        raise CheckError("npm audit returned an unsupported report")
    return {
        **result,
        "npm": audit["vulnerabilities"],
        "total": audit["metadata"]["vulnerabilities"]["total"],
    }


def inventory(root: Path, now: dt.datetime | None = None) -> dict:
    now = now or dt.datetime.now(dt.UTC)
    report = {
        "checked_at": now.isoformat(),
        "dependencies": [],
        "errors": [],
        "security": {},
    }
    try:
        rules = policy(root)
        for directory, children, files in os.walk(root):
            children[:] = [
                name
                for name in children
                if name
                not in {
                    ".git",
                    "node_modules",
                    ".venv",
                    ".repo-state",
                    "__pycache__",
                    "dist",
                    "build",
                }
            ]
            for name in files:
                relative = (Path(directory) / name).relative_to(root)
                if name in {
                    "package.json",
                    "mise.toml",
                    ".mise.toml",
                    *UNSUPPORTED_MANIFESTS,
                } and (len(relative.parts) > 1 or name == ".mise.toml"):
                    report["errors"].append(
                        f"{relative}: nested/alternate configuration "
                        "requires a native adapter"
                    )
        config = tomllib.loads((root / "mise.toml").read_text())
        report["dependencies"] = tool_inventory(root, config, rules, now.date())
        has_npm = (root / "package.json").is_file()
        native_aube = False
        if has_npm:
            lock, native_aube = application_lock(root)
            report["dependencies"] += npm_inventory(
                root,
                json.loads((root / "package.json").read_text()),
                lock,
            )
            report["application_adapter"] = (
                "aube list/audit" if native_aube else "npm lockfile/audit"
            )
        for path in sorted(UNSUPPORTED_MANIFESTS):
            if (root / path).exists():
                report["errors"].append(
                    f"{path}: add the ecosystem's native inventory/audit adapter"
                )
        holds = rules.get("holds", {})
        ids = {row["id"] for row in report["dependencies"]}
        if set(holds) - ids:
            report["errors"].append(
                "holds refer to dependencies outside this inventory"
            )
        for row in report["dependencies"]:
            try:
                apply_hold(row, holds, now.date())
            except CheckError as exc:
                report["errors"].append(str(exc))
        report["security"] = security(root, has_npm, native_aube)
    except (CheckError, OSError, ValueError, TypeError) as exc:
        report["errors"].append(str(exc))
    incomplete = report["errors"] or any(
        r["status"] == "incomplete" for r in report["dependencies"]
    )
    attention = any(
        r["status"] == "update-available" for r in report["dependencies"]
    ) or report["security"].get("total", 0)
    report["exit_code"] = 2 if incomplete else 1 if attention else 0
    report["result"] = {
        0: "current within declared scope; review tool advisories separately",
        1: "updates or security findings need review",
        2: "incomplete: resolve unsupported inputs or failed queries",
    }[report["exit_code"]]
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="save timestamped JSON evidence")
    args = parser.parse_args()
    report = inventory(Path.cwd())
    content = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(content)
    print(content, end="")
    return report["exit_code"]


if __name__ == "__main__":
    sys.exit(main())
