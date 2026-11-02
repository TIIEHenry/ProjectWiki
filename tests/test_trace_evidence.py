"""Behaviour tests for requirement tracing and evidence visibility (PW-46)."""
import sys
import unittest

from test_wiki import ProjectFixture, wiki, SCRIPT


class RequirementsLocationTests(ProjectFixture):
    """PW-46.1: requirements files must live under a knowledge root."""

    def setUp(self):
        super().setUp()
        self.config["requirements"] = {"files": ["**/requirements.md"], "tests": ["tests/*"]}
        self.body = ("# Requirements\n\n### EX-01 First\n\n状态：已实现。\n\n"
                     "- EX-01.1 Does a thing.\n")
        self.write("docs/design.md", "# Design\n\n对应需求：EX-01。\n")
        self.save_config()

    def rules_for(self, report):
        return {(x["rule"], x.get("key")) for x in report["findings"]}

    def test_knowledge_root_requirements_do_not_warn(self):
        """PW-46.1"""
        self.write("docs/requirements.md", self.body)
        code, report = self.run_cli("check")
        self.assertNotIn("trace-requirements-location",
                         {x["rule"] for x in report["findings"]})

    def test_process_and_archive_roots_warn(self):
        """PW-46.1"""
        # A requirements file that sits under the process root (dev/plans/) and
        # one that sits under the archive root both get flagged.
        self.write("docs/requirements.md", self.body)
        self.write("dev/plans/requirements.md", self.body.replace("EX-01", "EX-02"))
        self.write("archive/requirements.md", self.body.replace("EX-01", "EX-03"))
        code, report = self.run_cli("check")
        flagged = {x["path"] for x in report["findings"] if x["rule"] == "trace-requirements-location"}
        self.assertEqual(flagged, {"dev/plans/requirements.md", "archive/requirements.md"})
        message = [x["message"] for x in report["findings"] if x["rule"] == "trace-requirements-location"][0]
        self.assertIn("move", message)
        self.assertNotIn("](", message, "the message names the command without linking its documentation")

    def test_legacy_requirements_file_still_warns(self):
        """PW-46.1"""
        # A file present before adoption is still reported, not grandfathered in.
        if not self.has_git():
            self.skipTest("git is required")
        self.write("dev/plans/requirements.md", self.body)
        self.git("init", "-q")
        self.git("add", "-A")
        self.git("-c", "user.name=t", "-c", "user.email=t@x.invalid",
                 "-c", "commit.gpgsign=false", "commit", "-qm", "base")
        self.config["adopted_at"] = self.git("rev-parse", "HEAD")
        self.save_config()
        code, report = self.run_cli("check")
        flagged = {x["path"] for x in report["findings"] if x["rule"] == "trace-requirements-location"}
        self.assertIn("dev/plans/requirements.md", flagged)

    def has_git(self):
        import shutil
        return bool(shutil.which("git"))


class CoverageTests(ProjectFixture):
    """PW-46.2 and PW-46.3: coverage summary and the all-manual warning."""

    def setUp(self):
        super().setUp()
        self.config["requirements"] = {"files": ["docs/requirements/*.md"], "tests": ["tests/*"]}
        self.save_config()
        self.write("docs/design.md", "# Design\n\n对应需求：EX-01、EX-02、EX-03。\n")

    def coverage(self):
        code, report = self.run_cli("check")
        groups = report.get("coverage", {}).get("requirements", [])
        by_name = {g["name"]: g for g in groups}
        return code, report, by_name

    def test_default_group_counts_tested_manual_and_untested(self):
        """PW-46.2"""
        self.write("docs/requirements/main.md",
                   "# Requirements\n\n"
                   "### EX-01 With tests\n\n状态：已实现。\n\n"
                   "- EX-01.1 Tested item.\n"
                   "- EX-01.2 Manual item.（人工验证）\n  验收核对：EX-01.2，agent:t，2026-10-29。\n"
                   "- EX-01.3 Untested item.\n\n"
                   "### EX-02 Accepted only\n\n状态：已接受。\n\n- EX-02.1 Planned.\n")
        self.write("tests/test_x.py", '"""EX-01.1"""\n')
        code, report, by_name = self.coverage()
        self.assertIn("default", by_name)
        default = by_name["default"]
        self.assertEqual(default["requirements"], 2)
        self.assertEqual(default["acceptance"], 4)
        self.assertEqual(default["tested"], 1)
        self.assertEqual(default["manual"], 1)
        self.assertEqual(default["untested"], 2)
        self.assertEqual(default["status"], {"已实现": 1, "已接受": 1})

    def test_text_output_has_a_summary_line(self):
        """PW-46.2"""
        self.write("docs/requirements/main.md",
                   "# Requirements\n\n### EX-01 One\n\n状态：已实现。\n\n- EX-01.1 Tested.\n")
        self.write("tests/test_x.py", '"""EX-01.1"""\n')
        result = __import__("subprocess").run(
            [sys.executable, str(SCRIPT), "check", "--root", str(self.root)],
            capture_output=True, text=True)
        self.assertIn("requirements[default]: 1 requirements, 1 acceptance items: "
                      "1 with tests, 0 manual only, 0 untested", result.stdout)

    def test_named_groups_each_get_their_own_coverage(self):
        """PW-46.2"""
        self.config["requirements"] = [
            {"name": "engine", "files": ["docs/requirements/engine.md"], "docs": ["docs/*"], "tests": ["tests/engine/*"]},
            {"name": "tui", "files": ["docs/requirements/tui.md"], "docs": ["docs/requirements/tui.md"], "tests": ["tests/tui/*"]},
        ]
        self.save_config()
        self.write("docs/design.md", "# Design\n\n对应需求：PRD-001。\n")
        self.write("docs/requirements/engine.md",
                   "# Engine\n\n### PRD-001 Run\n\n状态：已实现。\n\n- PRD-001.1 Runs.\n")
        self.write("docs/requirements/tui.md",
                   "# TUI\n\n[d](../design.md)\n\n### PRD-001 Show\n\n状态：已实现。\n\n- PRD-001.1 Shows.\n- PRD-001.2 Lists.\n")
        self.write("tests/engine/test_e.py", '"""PRD-001.1"""\n')
        code, report, by_name = self.coverage()
        self.assertEqual(by_name["engine"]["tested"], 1)
        self.assertEqual(by_name["engine"]["acceptance"], 1)
        self.assertEqual(by_name["tui"]["acceptance"], 2)
        self.assertEqual(by_name["tui"]["tested"], 0)
        self.assertEqual(by_name["tui"]["untested"], 2)

    def test_all_manual_implemented_requirement_warns(self):
        """PW-46.3"""
        self.write("docs/requirements/main.md",
                   "# Requirements\n\n### EX-01 All manual\n\n状态：已实现。\n\n"
                   "- EX-01.1 Manual one.（人工验证）\n  验收核对：EX-01.1，agent:t，2026-10-29。\n"
                   "- EX-01.2 Manual two.（人工验证）\n  验收核对：EX-01.2，agent:t，2026-10-29。\n")
        self.write("tests/test_x.py", "# none\n")
        code, report, by_name = self.coverage()
        rules = {(x["rule"], x.get("key")) for x in report["findings"]}
        self.assertIn(("trace-all-manual", "EX-01"), rules)

    def test_single_manual_item_does_not_warn(self):
        """PW-46.3"""
        # Fewer than 2 acceptance items: no all-manual warning.
        self.write("docs/requirements/main.md",
                   "# Requirements\n\n### EX-01 Lonely\n\n状态：已实现。\n\n"
                   "- EX-01.1 Manual one.（人工验证）\n  验收核对：EX-01.1，agent:t，2026-10-29。\n")
        self.write("tests/test_x.py", "# none\n")
        code, report, by_name = self.coverage()
        self.assertNotIn("trace-all-manual", {x["rule"] for x in report["findings"]})

    def test_one_tested_item_prevents_all_manual_warning(self):
        """PW-46.3"""
        self.write("docs/requirements/main.md",
                   "# Requirements\n\n### EX-01 Mixed\n\n状态：已实现。\n\n"
                   "- EX-01.1 Tested.\n"
                   "- EX-01.2 Manual.（人工验证）\n  验收核对：EX-01.2，agent:t,2026-10-29。\n")
        self.write("tests/test_x.py", '"""EX-01.1"""\n')
        code, report, by_name = self.coverage()
        self.assertNotIn("trace-all-manual", {x["rule"] for x in report["findings"]})


class VerifyKindTests(ProjectFixture):
    """PW-46.4 and PW-46.5: verify.commands kind and code_tests_registered."""

    def commands(self, *, with_test):
        python = sys.executable
        cmds = [{"name": "check", "kind": "check", "run": [python, "-c", "print('ok')"]}]
        if with_test:
            cmds.append({"name": "tests", "kind": "test", "run": [python, "-c", "print('Ran 1 test'); print('OK')"]})
        return cmds

    def test_valid_kind_field_is_accepted(self):
        """PW-46.4"""
        self.config["verify"] = {"commands": self.commands(with_test=True)}
        self.save_config()
        code, report = self.run_cli("verify")
        self.assertEqual(code, 0, report)
        kinds = {c["name"]: c.get("kind") for c in report["commands"]}
        self.assertEqual(kinds, {"check": "check", "tests": "test"})

    def test_invalid_kind_is_reported_incomplete(self):
        """PW-46.4"""
        python = sys.executable
        self.config["verify"] = {"commands": [
            {"name": "mark", "kind": "lint", "run": [python, "-c", "open('marker','w')"]}]}
        self.save_config()
        code, report = self.run_cli("verify")
        self.assertEqual((code, report["result"]), (2, "incomplete"))
        self.assertFalse((self.root / "marker").exists(), "no command runs when the config is invalid")

    def test_no_test_command_marks_record_and_flag(self):
        """PW-46.5"""
        self.config["verify"] = {"commands": self.commands(with_test=False)}
        self.save_config()
        code, report = self.run_cli("verify")
        self.assertEqual(code, 0, report)
        self.assertFalse(report["code_tests_registered"])
        self.assertIn("未登记代码测试", report["markdown"])

    def test_registered_test_command_sets_flag_true(self):
        """PW-46.5"""
        self.config["verify"] = {"commands": self.commands(with_test=True)}
        self.save_config()
        code, report = self.run_cli("verify")
        self.assertEqual(code, 0, report)
        self.assertTrue(report["code_tests_registered"])
        self.assertNotIn("未登记代码测试", report["markdown"])

    def test_flag_follows_the_commands_actually_run(self):
        """PW-46.5"""
        # Running only the check command, the record cannot claim to prove code.
        self.config["verify"] = {"commands": self.commands(with_test=True)}
        self.save_config()
        code, report = self.run_cli("verify", "check")
        self.assertEqual(code, 0, report)
        self.assertFalse(report["code_tests_registered"])
        self.assertIn("未登记代码测试", report["markdown"])

    def test_command_without_kind_still_runs(self):
        """PW-46.4"""
        python = sys.executable
        self.config["verify"] = {"commands": [
            {"name": "plain", "run": [python, "-c", "print('Ran 1 test'); print('OK')"]}]}
        self.save_config()
        code, report = self.run_cli("verify")
        self.assertEqual(code, 0, report)
        self.assertNotIn("kind", report["commands"][0])
        self.assertFalse(report["code_tests_registered"])


if __name__ == "__main__":
    unittest.main()
