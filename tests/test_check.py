from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.check import check


class RepositoryCheckTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        package = {
            "name": "tempo-board",
            "private": True,
            "license": "MIT",
            "scripts": {
                "dev": "vite",
                "build": "vite build",
                "lint": "biome lint .",
                "typecheck": "tsc --noEmit",
                "test": "vitest run",
            },
        }
        files = {
            "AGENTS.md": "# Instructions\n",
            "README.md": "# Tempo Board\n",
            "PRODUCT.md": "# Product\n",
            "DESIGN.md": "# Design\n",
            "LICENSE": "MIT License\n",
            "mise.toml": '[tools]\npython = "3.13"\n',
            "package.json": json.dumps(package),
            ".npmrc": "default-lockfile-format=pnpm\n",
            "pnpm-lock.yaml": "lockfileVersion: '9.0'\n",
            "biome.json": "{}\n",
            "tsconfig.json": "{}\n",
            "renovate.json": "{}\n",
            ".github/workflows/ci.yml": "name: CI\n",
            "src/main.ts": "export {};\n",
            "src/timer.ts": "export {};\n",
            "src/style.css": ":root {}\n",
            "ruff.toml": "line-length = 88\n",
            ".rumdl.toml": "exclude = []\n",
        }
        for relative, contents in files.items():
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(contents, encoding="utf-8")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_valid_app_repository_passes(self) -> None:
        self.assertEqual(check(self.root), [])

    def test_invalid_toml_and_json_are_reported(self) -> None:
        (self.root / "ruff.toml").write_text("line-length =\n", encoding="utf-8")
        (self.root / "biome.json").write_text("{broken", encoding="utf-8")
        errors = check(self.root)
        self.assertTrue(any("invalid TOML ruff.toml" in error for error in errors))
        self.assertTrue(any("invalid JSON biome.json" in error for error in errors))

    def test_required_files_and_app_scripts_are_checked(self) -> None:
        (self.root / "src/timer.ts").unlink()
        package = json.loads((self.root / "package.json").read_text(encoding="utf-8"))
        del package["scripts"]["build"]
        (self.root / "package.json").write_text(json.dumps(package), encoding="utf-8")
        errors = check(self.root)
        self.assertTrue(
            any("required file is missing: src/timer.ts" in e for e in errors)
        )
        self.assertTrue(any("missing scripts: build" in e for e in errors))

    def test_project_requires_one_pnpm_lockfile(self) -> None:
        (self.root / "package-lock.json").write_text("{}\n", encoding="utf-8")
        errors = check(self.root)
        self.assertTrue(any("exactly one app lockfile" in error for error in errors))

    def test_committed_local_issue_and_environment_files_are_rejected(self) -> None:
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
        secret_file = self.root / ".env.local"
        secret_file.write_text("SYNTHETIC=value\n", encoding="utf-8")
        subprocess.run(["git", "add", ".env.local"], cwd=self.root, check=True)
        errors = check(self.root)
        self.assertTrue(
            any("local issue or environment files" in error for error in errors)
        )


if __name__ == "__main__":
    unittest.main()
