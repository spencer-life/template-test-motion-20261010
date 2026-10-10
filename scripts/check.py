#!/usr/bin/env python3
"""Check core app, repository, and development-tool configuration."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tomllib
from pathlib import Path

REQUIRED_FILES = (
    "AGENTS.md",
    "README.md",
    "PRODUCT.md",
    "DESIGN.md",
    "LICENSE",
    "mise.toml",
    "package.json",
    ".npmrc",
    "pnpm-lock.yaml",
    "biome.json",
    "tsconfig.json",
    "renovate.json",
    ".github/workflows/ci.yml",
    "src/main.ts",
    "src/timer.ts",
    "src/style.css",
)
TOML_CONFIGS = ("mise.toml", "ruff.toml", ".rumdl.toml")
JSON_CONFIGS = ("package.json", "biome.json", "tsconfig.json", "renovate.json")
PACKAGE_SCRIPTS = {"dev", "build", "lint", "typecheck", "test"}
LOCKFILES = (
    "pnpm-lock.yaml",
    "package-lock.json",
    "npm-shrinkwrap.json",
    "aube-lock.yaml",
    "yarn.lock",
    "bun.lock",
    "bun.lockb",
)


def _load_json(root: Path, relative: str, errors: list[str]) -> dict | None:
    path = root / relative
    if not path.is_file():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        errors.append(f"invalid JSON {relative}: {exc}")
        return None
    if not isinstance(value, dict):
        errors.append(f"{relative}: must contain a JSON object")
        return None
    return value


def _check_package(package: dict | None, errors: list[str]) -> None:
    if package is None:
        return
    if package.get("name") != "tempo-board":
        errors.append("package.json: name must be tempo-board")
    if package.get("private") is not True:
        errors.append("package.json: private must be true for this starter")
    if package.get("license") != "MIT":
        errors.append("package.json: license must match the repository MIT license")
    scripts = package.get("scripts")
    if not isinstance(scripts, dict):
        errors.append("package.json: scripts must be an object")
    else:
        missing = sorted(PACKAGE_SCRIPTS - set(scripts))
        if missing:
            errors.append(f"package.json: missing scripts: {', '.join(missing)}")


def check(root: Path) -> list[str]:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (root / relative).is_file():
            errors.append(f"required file is missing: {relative}")

    for relative in TOML_CONFIGS:
        path = root / relative
        if not path.is_file():
            continue
        try:
            tomllib.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, tomllib.TOMLDecodeError) as exc:
            errors.append(f"invalid TOML {relative}: {exc}")

    json_values = {
        relative: _load_json(root, relative, errors) for relative in JSON_CONFIGS
    }
    _check_package(json_values["package.json"], errors)

    lockfiles = [name for name in LOCKFILES if (root / name).is_file()]
    if lockfiles != ["pnpm-lock.yaml"]:
        errors.append(
            "exactly one app lockfile is required, and it must be pnpm-lock.yaml"
        )
    npmrc = root / ".npmrc"
    if npmrc.is_file() and not re.search(
        r"(?m)^\s*default-lockfile-format\s*=\s*pnpm\s*$",
        npmrc.read_text(encoding="utf-8"),
    ):
        errors.append(".npmrc: aube must be configured to create pnpm-lock.yaml")

    try:
        result = subprocess.run(
            [
                "git",
                "ls-files",
                "--",
                ".issues",
                ".issues/**",
                ".env",
                ".env.*",
                "!.env.example",
            ],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        result = None
    if result is not None:
        tracked = [line for line in result.stdout.splitlines() if line]
        if tracked:
            errors.append(
                "local issue or environment files must not be committed: "
                f"{', '.join(tracked)}"
            )
    return errors


def main() -> int:
    errors = check(Path.cwd())
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("Tempo Board app and development configuration are valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
