"""Freshness checks must fail visibly and keep security separate from holds."""

import datetime as dt
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import freshness

NOW = dt.datetime(2026, 10, 7, tzinfo=dt.UTC)


class FreshnessTests(unittest.TestCase):
    def test_stable_eligibility_preserves_breaking_boundaries(self):
        self.assertEqual(
            freshness.eligible(["1.2.0", "1.3.0", "2.0.0", "1.4.0-rc.1"], "1"), "1.3.0"
        )
        self.assertEqual(freshness.prefix_for("0.9.1"), "0.9")
        self.assertEqual(freshness.prefix_for("3.12.15", True), "3.12")

    def test_hold_requires_owner_reason_version_and_future_review(self):
        row = {"id": "npm:react", "selected": "19.0.0", "status": "update-available"}
        hold = {
            "selected": "19.0.0",
            "reason": "Expo SDK compatibility",
            "owner": "mobile maintainer",
            "review_on": "2026-10-20",
        }
        freshness.apply_hold(row, {"npm:react": hold}, NOW.date())
        self.assertEqual(row["status"], "held")
        for change in (
            {"review_on": "2026-10-07"},
            {"selected": "18.0.0"},
            {"owner": ""},
        ):
            with self.assertRaises(freshness.CheckError):
                freshness.apply_hold(row, {"npm:react": {**hold, **change}}, NOW.date())

    def sample(self, root):
        (root / "mise.toml").write_text('[tools]\nnode = "24.0.0"\n')
        (root / "package.json").write_text(
            json.dumps({"dependencies": {"is-number": "7.0.0"}})
        )
        (root / "package-lock.json").write_text(
            json.dumps(
                {
                    "lockfileVersion": 3,
                    "packages": {"node_modules/is-number": {"version": "7.0.0"}},
                }
            )
        )

    def response(self, command, root, **kwargs):
        if command[0] == "mise":
            return [{"version": v} for v in ["24.0.0", "24.1.0", "25.0.0"]]
        if command[1] == "audit":
            return {
                "vulnerabilities": {},
                "metadata": {"vulnerabilities": {"total": 0}},
            }
        if command[3] == "version":
            return ["7.0.0", "7.1.0"] if "^" in command[2] else "7.0.0"
        return {
            "dist-tags": {"latest": "8.0.0"},
            "time": {"7.1.0": "2026-09-01T00:00:00Z"},
        }

    def test_inventory_detects_pins_even_when_exact_requests_do_not_move(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            self.sample(root)
            with patch.object(freshness, "query", self.response):
                report = freshness.inventory(root, NOW)
            self.assertEqual(report["exit_code"], 1)
            self.assertEqual(report["dependencies"][0]["current_eligible"], "24.1.0")
            self.assertEqual(report["dependencies"][1]["current_eligible"], "7.1.0")
            self.assertEqual(report["dependencies"][1]["latest"], "8.0.0")
            self.assertEqual(report["checked_at"], NOW.isoformat())

    def test_security_is_not_suppressed_by_compatibility_hold(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            self.sample(root)
            holds = {
                name: {
                    "selected": selected,
                    "reason": "SDK coupling",
                    "owner": "maintainer",
                    "review_on": "2026-10-20",
                }
                for name, selected in [
                    ("mise:node", "24.0.0"),
                    ("npm:is-number", "7.0.0"),
                ]
            }
            (root / "dependency-freshness.json").write_text(
                json.dumps({"holds": holds})
            )

            def vulnerable(command, root, **kwargs):
                if command[1] == "audit":
                    return {
                        "vulnerabilities": {"is-number": {"severity": "high"}},
                        "metadata": {"vulnerabilities": {"total": 1}},
                    }
                return self.response(command, root, **kwargs)

            with patch.object(freshness, "query", vulnerable):
                report = freshness.inventory(root, NOW)
            self.assertEqual(report["exit_code"], 1)
            self.assertTrue(
                all(row["status"] == "held" for row in report["dependencies"])
            )
            self.assertEqual(report["security"]["total"], 1)

    def test_current_compatible_sample_passes_without_following_new_major(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "mise.toml").write_text('[tools]\nnode = "24.1.0"\n')
            with patch.object(freshness, "query", self.response):
                report = freshness.inventory(root, NOW)
            self.assertEqual(report["exit_code"], 0)
            self.assertIn("advisories separately", report["result"])
            self.assertEqual(report["dependencies"][0]["latest"], "25.0.0")

    def test_network_error_and_unsupported_lock_do_not_pass(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            self.sample(root)
            with patch.object(
                freshness,
                "query",
                side_effect=freshness.CheckError("network unavailable"),
            ):
                self.assertEqual(freshness.inventory(root, NOW)["exit_code"], 2)
            (root / "package-lock.json").unlink()
            with patch.object(freshness, "query", self.response):
                report = freshness.inventory(root, NOW)
            self.assertEqual(report["exit_code"], 2)
            self.assertIn("unsupported", report["errors"][0])

    def test_constraints_and_nested_manifests_cannot_hide_missing_coverage(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "mise.toml").write_text('[tools]\nnode = "24.1.0"\n')
            (root / "dependency-freshness.json").write_text(
                json.dumps(
                    {
                        "tool_constraints": {
                            "mise:node": {
                                "prefix": "24",
                                "reason": "Runtime support",
                                "owner": "maintainer",
                                "review_on": "2026-10-07",
                            }
                        }
                    }
                )
            )
            with patch.object(freshness, "query", self.response):
                self.assertEqual(freshness.inventory(root, NOW)["exit_code"], 2)
            (root / "dependency-freshness.json").unlink()
            (root / "apps").mkdir()
            (root / "apps/package.json").write_text("{}")
            with patch.object(freshness, "query", self.response):
                report = freshness.inventory(root, NOW)
            self.assertEqual(report["exit_code"], 2)
            self.assertIn("nested", report["errors"][0])

    def test_native_aube_inventory_and_security_keep_the_chosen_lockfile(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            self.sample(root)
            (root / "package-lock.json").unlink()
            (root / "pnpm-lock.yaml").write_text("lockfileVersion: 9.0\n")

            def native(command, root, **kwargs):
                if command[:2] == ["aube", "list"]:
                    self.assertIn("--lockfile-only", command)
                    return [{"dependencies": {"is-number": {"version": "7.0.0"}}}]
                if command[:2] == ["aube", "audit"]:
                    self.assertEqual(command[-2:], ["--audit-level", "info"])
                    return {
                        "advisories": {"123": {"severity": "high"}},
                        "metadata": {
                            "vulnerabilities": {
                                "info": 0,
                                "low": 0,
                                "moderate": 0,
                                "high": 1,
                                "critical": 0,
                            }
                        },
                    }
                return self.response(command, root, **kwargs)

            with patch.object(freshness, "query", native):
                report = freshness.inventory(root, NOW)
            self.assertEqual(report["exit_code"], 1)
            self.assertEqual(report["security"]["total"], 1)
            self.assertEqual(report["application_adapter"], "aube list/audit")
            self.assertFalse((root / "package-lock.json").exists())
            self.assertEqual(
                (root / "pnpm-lock.yaml").read_text(), "lockfileVersion: 9.0\n"
            )

    def test_native_audit_requests_info_even_when_project_filters_high(self):
        for severity in ("info", "low", "moderate"):
            with (
                self.subTest(severity=severity),
                tempfile.TemporaryDirectory() as folder,
            ):
                root = Path(folder)
                (root / "aube-workspace.yaml").write_text("audit:\n  level: high\n")

                def audit(command, root, severity=severity, **kwargs):
                    counts = dict.fromkeys(
                        ("info", "low", "moderate", "high", "critical"), 0
                    )
                    counts[severity] = 1
                    return {
                        "advisories": {"123": {"severity": severity}}
                        if command[-2:] == ["--audit-level", "info"]
                        else {},
                        "metadata": {"vulnerabilities": counts},
                    }

                with patch.object(freshness, "query", audit):
                    result = freshness.security(root, True, True)
                self.assertEqual(result["total"], 1)
                self.assertEqual(result["npm"]["123"]["severity"], severity)

    def test_incomplete_audit_report_is_not_a_clean_security_result(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            self.sample(root)

            def broken(command, root, **kwargs):
                return (
                    {}
                    if command[1] == "audit"
                    else self.response(command, root, **kwargs)
                )

            with patch.object(freshness, "query", broken):
                self.assertEqual(freshness.inventory(root, NOW)["exit_code"], 2)

    def test_all_unsupported_manifests_fail_at_root_and_nested(self):
        for name in (
            "pyproject.toml",
            "requirements.txt",
            "Cargo.toml",
            "go.mod",
            "pom.xml",
            "build.gradle",
            "build.gradle.kts",
        ):
            for nested in (False, True):
                with (
                    self.subTest(name=name, nested=nested),
                    tempfile.TemporaryDirectory() as folder,
                ):
                    root = Path(folder)
                    (root / "mise.toml").write_text("[tools]\n")
                    directory = root / "apps" if nested else root
                    directory.mkdir(exist_ok=True)
                    (directory / name).write_text("")
                    with patch.object(freshness, "query", self.response):
                        report = freshness.inventory(root, NOW)
                    self.assertEqual(report["exit_code"], 2)
                    self.assertTrue(any(name in error for error in report["errors"]))

    def test_hold_on_incomplete_dependency_returns_json_report(self):
        for failure in ("git-spec", "missing-lock-entry"):
            with self.subTest(failure=failure), tempfile.TemporaryDirectory() as folder:
                root = Path(folder)
                self.sample(root)
                if failure == "git-spec":
                    (root / "package.json").write_text(
                        json.dumps(
                            {"dependencies": {"is-number": "github:example/package"}}
                        )
                    )
                else:
                    (root / "package-lock.json").write_text(
                        json.dumps({"lockfileVersion": 3, "packages": {}})
                    )
                (root / "dependency-freshness.json").write_text(
                    json.dumps(
                        {
                            "holds": {
                                "npm:is-number": {
                                    "selected": "7.0.0",
                                    "reason": "Compatibility",
                                    "owner": "maintainer",
                                    "review_on": "2026-10-20",
                                }
                            }
                        }
                    )
                )
                with patch.object(freshness, "query", self.response):
                    report = freshness.inventory(root, NOW)
                self.assertEqual(report["exit_code"], 2)
                self.assertIn("incomplete", json.dumps(report))
                self.assertEqual(report["dependencies"][-1]["status"], "incomplete")


if __name__ == "__main__":
    unittest.main()
