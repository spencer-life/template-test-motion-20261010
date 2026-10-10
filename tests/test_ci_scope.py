from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.ci_scope import Scope, classify_changes


class CiScopeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        subprocess.run(
            ["git", "-C", str(self.root), "config", "user.email", "test@example.com"],
            check=True,
        )
        subprocess.run(
            ["git", "-C", str(self.root), "config", "user.name", "Test"],
            check=True,
        )
        self.base_sha = self._commit("base", {"README.md": "base\n"})

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _commit(self, message: str, files: dict[str, str]) -> str:
        for name, content in files.items():
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        subprocess.run(["git", "-C", str(self.root), "add", "-A"], check=True)
        subprocess.run(
            ["git", "-C", str(self.root), "commit", "-qm", message], check=True
        )
        return subprocess.run(
            ["git", "-C", str(self.root), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()

    def _scope(self, head_sha: str, base_sha: str | None = None) -> Scope:
        event_path = self.root / "event.json"
        event_path.write_text(
            json.dumps(
                {
                    "pull_request": {
                        "base": {"sha": base_sha or self.base_sha},
                        "head": {"sha": head_sha},
                    }
                }
            ),
            encoding="utf-8",
        )
        return classify_changes(event_path, "pull_request", self.root)

    def test_root_and_docs_markdown_are_documentation_only(self) -> None:
        head = self._commit("docs", {"GUIDE.md": "guide\n", "docs/setup.md": "setup\n"})
        self.assertEqual(self._scope(head), Scope(False, False))

    def test_markdown_outside_documentation_locations_runs_full_ci(self) -> None:
        head = self._commit("nested markdown", {"examples/README.md": "example\n"})
        self.assertEqual(self._scope(head), Scope(True, False))

    def test_code_and_mixed_changes_run_full_ci(self) -> None:
        code = self._commit("code", {"scripts/check.py": "print('ok')\n"})
        self.assertEqual(self._scope(code), Scope(True, False))
        mixed = self._commit(
            "mixed", {"README.md": "new docs\n", "src/app.py": "print('app')\n"}
        )
        self.assertEqual(self._scope(mixed), Scope(True, False))

    def test_workflow_security_changes_enable_both_scopes(self) -> None:
        head = self._commit(
            "security",
            {
                "scripts/security.py": "print('audit')\n",
                ".github/actions/check/action.yml": "name: check\n",
            },
        )
        self.assertEqual(self._scope(head), Scope(True, True))

    def test_workflow_tool_configuration_names_enable_audits(self) -> None:
        for name in (
            ".github/actionlint.yaml",
            ".github/actionlint.yml",
            "zizmor.yaml",
            "zizmor.yml",
            ".github/zizmor.yaml",
            ".github/zizmor.yml",
        ):
            with self.subTest(name=name):
                previous = self._commit("before config", {"README.md": name + "\n"})
                head = self._commit("config", {name: "rules: {}\n"})
                self.assertEqual(self._scope(head, previous), Scope(True, True))

    def test_full_pull_request_range_includes_earlier_commits(self) -> None:
        self._commit("first", {"src/first.py": "first\n"})
        head = self._commit("second", {"docs/second.md": "second\n"})
        self.assertEqual(self._scope(head), Scope(True, False))

    def test_deleted_and_renamed_paths_are_classified(self) -> None:
        base = self._commit("workflow", {".github/workflows/old.yml": "name: old\n"})
        (self.root / ".github/workflows/old.yml").unlink()
        head = self._commit(
            "move workflow",
            {"docs/old.md": "name: old\n"},
        )
        self.assertEqual(self._scope(head, base), Scope(True, True))

    def test_unusual_path_bytes_are_safe_and_unknown_paths_fail_closed(self) -> None:
        head = self._commit("unusual", {"examples/line\nbreak.md": "text\n"})
        self.assertEqual(self._scope(head), Scope(True, False))

    def test_empty_diff_fails_closed(self) -> None:
        self.assertEqual(self._scope(self.base_sha), Scope(True, True))

    def test_manual_non_pr_missing_or_invalid_event_fails_closed(self) -> None:
        event_path = self.root / "event.json"
        event_path.write_text("{}", encoding="utf-8")
        self.assertEqual(
            classify_changes(event_path, "workflow_dispatch", self.root),
            Scope(True, True),
        )
        self.assertEqual(
            classify_changes(self.root / "missing.json", "pull_request", self.root),
            Scope(True, True),
        )
        event_path.write_text(
            json.dumps(
                {
                    "pull_request": {
                        "base": {"sha": "a" * 39 + "!"},
                        "head": {"sha": self.base_sha},
                    }
                }
            ),
            encoding="utf-8",
        )
        with patch("scripts.ci_scope.subprocess.run") as git:
            self.assertEqual(
                classify_changes(event_path, "pull_request", self.root),
                Scope(True, True),
            )
        git.assert_not_called()

    def test_invalid_refs_are_rejected_before_git_is_called(self) -> None:
        event_path = self.root / "event.json"
        event_path.write_text(
            json.dumps(
                {
                    "pull_request": {
                        "base": {"sha": "--upload-pack=bad"},
                        "head": {"sha": self.base_sha},
                    }
                }
            ),
            encoding="utf-8",
        )
        with patch("scripts.ci_scope.subprocess.run") as git:
            self.assertEqual(
                classify_changes(event_path, "pull_request", self.root),
                Scope(True, True),
            )
        git.assert_not_called()

    def test_git_failures_fail_closed(self) -> None:
        event_path = self.root / "event.json"
        event_path.write_text(
            json.dumps(
                {
                    "pull_request": {
                        "base": {"sha": "a" * 40},
                        "head": {"sha": "b" * 40},
                    }
                }
            ),
            encoding="utf-8",
        )
        self.assertEqual(
            classify_changes(event_path, "pull_request", self.root),
            Scope(True, True),
        )


if __name__ == "__main__":
    unittest.main()
