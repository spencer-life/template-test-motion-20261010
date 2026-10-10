#!/usr/bin/env python3
"""Run the pinned workflow and secret audits for the current repository."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def workflow_files(root: Path) -> list[str]:
    """Return all tracked workflow YAML files that need an audit."""
    directory = root / ".github/workflows"
    files = sorted(
        path.relative_to(root).as_posix()
        for path in directory.rglob("*")
        if path.is_file() and path.suffix.lower() in {".yml", ".yaml"}
    )
    if not files:
        raise FileNotFoundError("required GitHub workflow is missing")
    return files


def run_security(root: Path, *, workflows: bool = True, secrets: bool = True) -> None:
    if workflows:
        files = workflow_files(root)
        pyflakes = shutil.which("pyflakes")
        if pyflakes is None:
            raise FileNotFoundError(
                "Pyflakes is required for inline Python coverage; "
                "run the repository security task through Mise"
            )
        commands = (
            ["actionlint", f"-pyflakes={pyflakes}", *files],
            ["zizmor", "--offline", "--no-progress", *files],
        )
        for command in commands:
            subprocess.run(command, cwd=root, check=True)
    if secrets:
        subprocess.run(
            ["gitleaks", "git", "--redact", "--no-banner", "."],
            cwd=root,
            check=True,
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    audit_mode = parser.add_mutually_exclusive_group()
    audit_mode.add_argument(
        "--workflows-only",
        action="store_true",
        help="run workflow audits without scanning Git history for secrets",
    )
    audit_mode.add_argument(
        "--secrets-only",
        action="store_true",
        help="scan Git history for secrets without running workflow audits",
    )
    args = parser.parse_args()
    try:
        run_security(
            Path.cwd(), workflows=not args.secrets_only, secrets=not args.workflows_only
        )
    except subprocess.CalledProcessError as exc:
        print(
            f"security check failed: {exc.cmd[0]} exited with {exc.returncode}",
            file=sys.stderr,
        )
        return exc.returncode or 1
    except (FileNotFoundError, OSError) as exc:
        print(f"security check failed: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
