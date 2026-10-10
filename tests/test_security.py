from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import call, patch

from scripts.security import main, run_security


class SecurityRunnerTests(unittest.TestCase):
    def setUp(self) -> None:
        pyflakes = patch(
            "scripts.security.shutil.which", return_value="/tools/pyflakes"
        )
        pyflakes.start()
        self.addCleanup(pyflakes.stop)
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / ".github/workflows/nested").mkdir(parents=True)
        (self.root / ".github/workflows/z.yml").write_text("name: z\n")
        (self.root / ".github/workflows/nested/a.yaml").write_text("name: a\n")
        (self.root / ".github/workflows/ignored.txt").write_text("not yaml\n")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_audits_every_workflow(self) -> None:
        with patch("scripts.security.subprocess.run") as runner:
            run_security(self.root)

        files = [
            ".github/workflows/nested/a.yaml",
            ".github/workflows/z.yml",
        ]
        self.assertEqual(
            runner.call_args_list,
            [
                call(
                    ["actionlint", "-pyflakes=/tools/pyflakes", *files],
                    cwd=self.root,
                    check=True,
                ),
                call(
                    ["zizmor", "--offline", "--no-progress", *files],
                    cwd=self.root,
                    check=True,
                ),
                call(
                    ["gitleaks", "git", "--redact", "--no-banner", "."],
                    cwd=self.root,
                    check=True,
                ),
            ],
        )

    def test_missing_workflow_fails_before_workflow_checks_can_pass(self) -> None:
        for path in (self.root / ".github/workflows").rglob("*"):
            if path.is_file():
                path.unlink()
        with self.assertRaisesRegex(FileNotFoundError, "required GitHub workflow"):
            run_security(self.root, workflows=True, secrets=False)

    def test_tool_failure_stops_and_propagates(self) -> None:
        failure = subprocess.CalledProcessError(9, ["zizmor"])
        with patch(
            "scripts.security.subprocess.run",
            side_effect=[None, failure],
        ) as runner:
            with self.assertRaises(subprocess.CalledProcessError) as caught:
                run_security(self.root)
        self.assertIs(caught.exception, failure)
        self.assertEqual(runner.call_count, 2)

    def test_missing_pyflakes_fails_before_workflow_checks_can_pass(self) -> None:
        with patch("scripts.security.shutil.which", return_value=None):
            with patch("scripts.security.subprocess.run") as runner:
                with self.assertRaisesRegex(FileNotFoundError, "Pyflakes is required"):
                    run_security(self.root, workflows=True, secrets=False)
        runner.assert_not_called()

    def test_workflows_only_skips_secret_scan(self) -> None:
        with patch("scripts.security.subprocess.run") as runner:
            run_security(self.root, workflows=True, secrets=False)

        self.assertEqual(runner.call_count, 2)
        self.assertEqual(runner.call_args_list[0].args[0][0], "actionlint")
        self.assertEqual(runner.call_args_list[1].args[0][0], "zizmor")

    def test_workflows_only_audit_failure_propagates(self) -> None:
        failure = subprocess.CalledProcessError(7, ["actionlint"])
        with patch("scripts.security.subprocess.run", side_effect=failure) as runner:
            with self.assertRaises(subprocess.CalledProcessError) as caught:
                run_security(self.root, workflows=True, secrets=False)
        self.assertIs(caught.exception, failure)
        runner.assert_called_once()

    def test_secrets_only_skips_workflow_validation(self) -> None:
        with patch("scripts.security.workflow_files") as workflow_files:
            with patch("scripts.security.subprocess.run") as runner:
                run_security(self.root, workflows=False, secrets=True)

        workflow_files.assert_not_called()
        runner.assert_called_once_with(
            ["gitleaks", "git", "--redact", "--no-banner", "."],
            cwd=self.root,
            check=True,
        )

    def test_secrets_only_failure_propagates(self) -> None:
        failure = subprocess.CalledProcessError(5, ["gitleaks"])
        with patch("scripts.security.subprocess.run", side_effect=failure) as runner:
            with self.assertRaises(subprocess.CalledProcessError) as caught:
                run_security(self.root, workflows=False, secrets=True)
        self.assertIs(caught.exception, failure)
        runner.assert_called_once()

    def test_secrets_only_cli_selects_secret_scan(self) -> None:
        with patch.object(sys, "argv", ["security.py", "--secrets-only"]):
            with patch("scripts.security.Path.cwd", return_value=self.root):
                with patch("scripts.security.run_security") as run:
                    self.assertEqual(main(), 0)

        run.assert_called_once_with(self.root, workflows=False, secrets=True)

    def test_single_purpose_cli_options_are_mutually_exclusive(self) -> None:
        with patch.object(
            sys,
            "argv",
            ["security.py", "--secrets-only", "--workflows-only"],
        ):
            with self.assertRaises(SystemExit) as caught:
                main()
        self.assertEqual(caught.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
