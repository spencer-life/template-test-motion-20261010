#!/usr/bin/env python3
"""Classify pull request changes for CI and workflow security audits."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import NamedTuple

SHA_PATTERN = re.compile(r"[0-9a-fA-F]{40}\Z")
WORKFLOW_AUDIT_FILES = {
    "scripts/security.py",
    "tests/test_security.py",
    "scripts/ci_scope.py",
    "tests/test_ci_scope.py",
    "mise.toml",
    "mise.lock",
    ".actionlint.yaml",
    ".actionlint.yml",
    ".github/actionlint.yaml",
    ".github/actionlint.yml",
    ".zizmor.yaml",
    ".zizmor.yml",
    "zizmor.yaml",
    "zizmor.yml",
    ".github/zizmor.yaml",
    ".github/zizmor.yml",
    ".gitleaks.toml",
    ".gitleaksignore",
    "gitleaks.toml",
}


class Scope(NamedTuple):
    full_ci: bool
    workflow_audits: bool


def _safe_scope() -> Scope:
    return Scope(full_ci=True, workflow_audits=True)


def _is_markdown_document(path: str) -> bool:
    if not path.endswith(".md"):
        return False
    return "/" not in path or path.startswith("docs/")


def _needs_workflow_audits(path: str) -> bool:
    return (
        path.startswith(".github/workflows/")
        or path.startswith(".github/actions/")
        or path in WORKFLOW_AUDIT_FILES
    )


def classify_changes(event_path: Path, event_name: str, repo_root: Path) -> Scope:
    """Return a fail-closed scope for a GitHub pull request event."""
    if event_name != "pull_request":
        return _safe_scope()

    try:
        event = json.loads(event_path.read_text(encoding="utf-8"))
        pull_request = event["pull_request"]
        base_sha = pull_request["base"]["sha"]
        head_sha = pull_request["head"]["sha"]
        if not isinstance(base_sha, str) or not SHA_PATTERN.fullmatch(base_sha):
            return _safe_scope()
        if not isinstance(head_sha, str) or not SHA_PATTERN.fullmatch(head_sha):
            return _safe_scope()

        merge_base = subprocess.run(
            ["git", "merge-base", base_sha, head_sha],
            cwd=repo_root,
            check=True,
            capture_output=True,
        ).stdout.strip()
        if not SHA_PATTERN.fullmatch(os.fsdecode(merge_base)):
            return _safe_scope()

        changed = subprocess.run(
            [
                "git",
                "diff",
                "--name-only",
                "-z",
                "--no-renames",
                os.fsdecode(merge_base),
                head_sha,
            ],
            cwd=repo_root,
            check=True,
            capture_output=True,
        ).stdout
        paths = [os.fsdecode(path) for path in changed.split(b"\0") if path]
    except (KeyError, TypeError, ValueError, OSError, subprocess.SubprocessError):
        return _safe_scope()

    if not paths:
        return _safe_scope()

    workflow_audits = any(_needs_workflow_audits(path) for path in paths)
    full_ci = any(not _is_markdown_document(path) for path in paths)
    return Scope(full_ci=full_ci, workflow_audits=workflow_audits)


def main() -> int:
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    event_name = os.environ.get("GITHUB_EVENT_NAME", "")
    scope = (
        classify_changes(Path(event_path), event_name, Path.cwd())
        if event_path
        else _safe_scope()
    )
    output_path = os.environ.get("GITHUB_OUTPUT")
    if output_path:
        try:
            with Path(output_path).open("a", encoding="utf-8") as output:
                output.write(f"full_ci={str(scope.full_ci).lower()}\n")
                output.write(f"workflow_audits={str(scope.workflow_audits).lower()}\n")
        except OSError as exc:
            print(f"could not write CI scope output: {exc}", file=sys.stderr)
            return 2
    print(
        "CI scope: "
        f"full_ci={str(scope.full_ci).lower()}, "
        f"workflow_audits={str(scope.workflow_audits).lower()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
