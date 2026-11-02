"""PW-41: remind reports ineffective hooks, staged checks skip uncommitted config,
and Docs-Reviewed with an unknown watch group warns.

Each test builds a temporary Git repository, so the whole module needs Git.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import unittest

from test_wiki import ProjectFixture, wiki, SCRIPT


class RemindHookFixture(ProjectFixture):
    GIT_ENV = {"GIT_AUTHOR_NAME": "Wiki Test", "GIT_AUTHOR_EMAIL": "wiki@example.invalid",
               "GIT_COMMITTER_NAME": "Wiki Test", "GIT_COMMITTER_EMAIL": "wiki@example.invalid"}

    def setUp(self):
        super().setUp()
        if not shutil.which("git"):
            self.skipTest("git is required for hook reminder tests")
        self.config["modules"] = [{"name": "notes", "path": "notes", "entry": "notes/README.md", "docs": "notes/docs"}]
        self.config["remind"] = {
            "watch": [{"name": "notes", "code": ["notes/src/*"], "docs": ["notes/docs/*", "notes/README.md"]}],
            "threshold": {"commits": 3, "lines": 1000},
            "block_at": {"commits": 5},
            "ask_user": ["docs/requirements.md"],
        }
        self.save_config()
        self.write("notes/README.md", "# Notes\n\n[Design](docs/design.md)\n")
        self.write("notes/docs/design.md", "# Design\n\nStable.\n")
        self.write("notes/src/title.py", "LIMIT = 60\n")
        self.git("init", "-q")

    def commit(self, message, all_files=False, verify=False):
        if all_files:
            self.git("add", "-A")
        args = ["git", "-C", str(self.root), "-c", "commit.gpgsign=false", "commit", "-q", "-m", message]
        if not verify:
            args.append("--no-verify")
        return subprocess.run(args, capture_output=True, text=True, env={**os.environ, **self.GIT_ENV})

    def message(self, text):
        path = self.root / "MSG"
        path.write_text(text, encoding="utf-8")
        return str(path)

    def install_tool_and_hooks(self, hooks_path="scripts/wiki/hooks"):
        """Copy the real tool into the repo and point core.hooksPath at the installed hooks."""
        tool_dir = self.root / "scripts" / "wiki"
        shutil.copytree(SCRIPT.parent, tool_dir, ignore=shutil.ignore_patterns("__pycache__"))
        self.config["exclude"].append("scripts/**")
        self.save_config()
        self.commit("Initial project", all_files=True)
        self.git("config", "core.hooksPath", hooks_path)


# --- A1: remind flags hooks that are not effective -------------------------------------

class HooksNotInstalledTests(RemindHookFixture):
    def test_remind_warns_when_hooks_missing(self):
        """PW-41.1"""
        self.commit("Initial project", all_files=True)
        code, report = self.run_cli("remind")
        self.assertEqual(code, 0, report)
        hooks = [f for f in report["findings"] if f["rule"] == "hooks-not-installed"]
        self.assertEqual({f["path"] for f in hooks}, {"pre-commit", "commit-msg"})
        for f in hooks:
            self.assertTrue(f["message"].startswith("[user]"), f)
            self.assertIn("core.hooksPath scripts/wiki/hooks", f["message"])

    def test_remind_silent_once_hooks_installed(self):
        """PW-41.1"""
        self.install_tool_and_hooks()
        code, report = self.run_cli("remind")
        self.assertEqual(code, 0, report)
        self.assertNotIn("hooks-not-installed", self.rules(report))

    def test_staged_remind_does_not_check_hooks(self):
        """PW-41.2"""
        self.commit("Initial project", all_files=True)
        self.write("notes/src/title.py", "LIMIT = 61\n")
        self.git("add", "notes/src/title.py")
        code, report = self.run_cli("remind", "--staged")
        self.assertEqual(code, 0, report)
        self.assertNotIn("hooks-not-installed", self.rules(report))

    def test_not_a_git_work_tree_yields_no_hook_findings(self):
        """PW-41.2"""
        # When the root is not a Git work tree, hook_status cannot classify anything, so the
        # hook check contributes nothing rather than inventing a missing-hook warning. (remind
        # itself reports incomplete without Git; this exercises the hook check in isolation.)
        shutil.rmtree(self.root / ".git")
        w = wiki.Wiki(wiki.Snapshot(self.root), "docs/wiki.json")
        self.assertNotIsInstance(wiki.hook_status(w), dict)
        self.assertEqual(wiki.hooks_not_installed_findings(w), [])

    def test_hook_warning_given_even_without_remind_config(self):
        """PW-41.2"""
        del self.config["remind"]
        self.save_config()
        self.commit("Initial project", all_files=True)
        code, report = self.run_cli("remind")
        self.assertEqual(code, 0, report)
        rules = self.rules(report)
        self.assertIn("remind-not-configured", rules)
        self.assertIn("hooks-not-installed", rules)

    def test_other_hooks_dir_calling_wiki_reads_as_installed(self):
        """PW-41.2"""
        # A project driving the tool through its own hooks directory: the hooks still call
        # wiki.py with the expected commands, so they read as installed and nothing warns.
        self.commit("Initial project", all_files=True)
        githooks = self.root / ".githooks"
        githooks.mkdir()
        for name, marker in (("pre-commit", "check --staged"), ("commit-msg", "remind --staged --message-file \"$1\"")):
            hook = githooks / name
            hook.write_text("#!/bin/sh\nexec python3 scripts/wiki/wiki.py " + marker + " --root .\n", encoding="utf-8")
            hook.chmod(0o755)
        self.git("config", "core.hooksPath", ".githooks")
        code, report = self.run_cli("remind")
        self.assertEqual(code, 0, report)
        self.assertNotIn("hooks-not-installed", self.rules(report))


# --- A2: staged checks skip an uncommitted configuration ---------------------------------

class ConfigNotCommittedTests(RemindHookFixture):
    def test_staged_check_skips_when_config_never_committed(self):
        """PW-41.3"""
        # Stage everything except docs/wiki.json: config is in neither the index nor HEAD.
        self.git("add", "notes", "README.md", "AGENTS.md", "docs/INDEX.md", "dev/INDEX.md")
        code, report = self.run_cli("check", "--staged")
        self.assertEqual(code, 0, report)
        self.assertEqual(report["result"], "not_checked")
        self.assertIn("config-not-committed", self.rules(report))
        self.assertTrue(report["coverage"]["not_checked"])

    def test_staged_remind_skips_when_config_never_committed(self):
        """PW-41.3"""
        self.git("add", "notes", "README.md", "AGENTS.md", "docs/INDEX.md", "dev/INDEX.md")
        code, report = self.run_cli("remind", "--staged")
        self.assertEqual(code, 0, report)
        self.assertEqual(report["result"], "not_checked")
        self.assertIn("config-not-committed", self.rules(report))

    def test_staged_check_runs_once_config_is_staged(self):
        """PW-41.4"""
        # Config newly added to the index (still no commit) goes through the normal check.
        self.write("docs/INDEX.md", "# Current\n\n[Missing](missing.md)\n")
        self.git("add", "-A")
        code, report = self.run_cli("check", "--staged")
        self.assertEqual(code, 1, report)
        self.assertNotIn("config-not-committed", self.rules(report))
        self.assertIn("broken-link", self.rules(report))

    def test_config_deleted_from_index_but_in_head_stays_incomplete(self):
        """PW-41.4"""
        self.commit("Initial project", all_files=True)
        # This commit removes the configuration from a project that had adopted it.
        self.git("rm", "-q", "--cached", "docs/wiki.json")
        code, report = self.run_cli("check", "--staged")
        self.assertEqual(code, 2, report)
        self.assertEqual(report["result"], "incomplete")
        self.assertNotIn("config-not-committed", {f["rule"] for f in report["findings"]})


# --- A3: Docs-Reviewed naming an unknown watch group warns -------------------------------

class ReviewTrailerUnknownGroupTests(RemindHookFixture):
    def setUp(self):
        super().setUp()
        self.commit("Initial project", all_files=True)

    def change_code(self, number):
        self.write("notes/src/title.py", f"LIMIT = {60 + number}\n")
        self.git("add", "notes/src/title.py")

    def test_unknown_group_name_warns_and_resets_nothing(self):
        """PW-41.5"""
        self.change_code(1)
        code, report = self.run_cli("remind", "--staged",
                                    "--message-file", self.message("Change\n\nDocs-Reviewed: wiki-adoption done\n"))
        self.assertEqual(code, 0, report)
        unknown = [f for f in report["findings"] if f["rule"] == "review-trailer-unknown-group"]
        self.assertEqual(len(unknown), 1, report)
        self.assertTrue(unknown[0]["message"].startswith("[agent]"))
        self.assertIn("wiki-adoption", unknown[0]["message"])
        self.assertIn("notes", unknown[0]["message"])
        # An unknown name does not reset the count, so the docs-not-updated reminder stays.
        self.assertIn("docs-not-updated", self.rules(report))

    def test_known_name_still_resets_without_warning(self):
        """PW-41.5"""
        self.change_code(1)
        code, report = self.run_cli("remind", "--staged",
                                    "--message-file", self.message("Change\n\nDocs-Reviewed: notes no behavior change\n"))
        self.assertEqual(code, 0, report)
        self.assertNotIn("review-trailer-unknown-group", self.rules(report))
        self.assertNotIn("docs-not-updated", self.rules(report))

    def test_mixed_names_warn_only_for_unknown_and_reset_known(self):
        """PW-41.5"""
        self.change_code(1)
        code, report = self.run_cli("remind", "--staged",
                                    "--message-file", self.message("Change\n\nDocs-Reviewed: notes,ghost reviewed\n"))
        self.assertEqual(code, 0, report)
        unknown = [f for f in report["findings"] if f["rule"] == "review-trailer-unknown-group"]
        self.assertEqual(len(unknown), 1, report)
        self.assertIn("ghost", unknown[0]["message"])
        self.assertNotIn("notes", unknown[0]["key"].split(","))
        # notes is a real group, so its count is reset and no reminder fires.
        self.assertNotIn("docs-not-updated", self.rules(report))

    def test_trailer_without_reason_keeps_incomplete_not_unknown(self):
        """PW-41.5"""
        # A trailer missing a reason is review-trailer-incomplete, unchanged by this change,
        # and does not also raise the unknown-group warning.
        self.change_code(1)
        code, report = self.run_cli("remind", "--staged",
                                    "--message-file", self.message("Change\n\nDocs-Reviewed: ghost\n"))
        self.assertEqual(code, 0, report)
        rules = self.rules(report)
        self.assertIn("review-trailer-incomplete", rules)
        self.assertNotIn("review-trailer-unknown-group", rules)


if __name__ == "__main__":
    unittest.main()
