"""Behavior tests use temporary projects; no checked-out project is modified."""

from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "wiki" / "wiki.py"
SPEC = importlib.util.spec_from_file_location("project_wiki", SCRIPT)
wiki = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = wiki
SPEC.loader.exec_module(wiki)


class ProjectFixture(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.config = {
            "version": 1,
            "project_name": "Example",
            "roots": [
                {"path": "docs", "role": "knowledge"},
                {"path": "dev", "role": "process"},
                {"path": "archive", "role": "archive"},
            ],
            "entrypoints": ["README.md", "AGENTS.md", "docs/INDEX.md", "dev/INDEX.md"],
            "pages": [{"path": "AGENTS.md", "role": "entry", "max_chars": 1000}],
            "exclude": ["tmp/**"],
        }
        self.write("README.md", "# Example\n\n[Knowledge](docs/INDEX.md#current)\n")
        self.write("AGENTS.md", "# Rules\n\nUse the documented checks.\n")
        self.write("docs/INDEX.md", "# Current\n\n[Work](../dev/INDEX.md)\n")
        self.write("dev/INDEX.md", "# Work\n\nNo active task.\n")
        self.save_config()

    def write(self, path, content):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    def save_config(self):
        self.write("docs/wiki.json", json.dumps(self.config))

    def run_cli(self, command, *args):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), command, *args, "--root", str(self.root), "--json"],
            capture_output=True, text=True,
        )
        return result.returncode, json.loads(result.stdout)

    def git(self, *args, input=None):
        result = subprocess.run(["git", "-C", str(self.root), *args], input=input, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout.strip()

    def initialize_index(self):
        if not shutil.which("git"):
            self.skipTest("git is required for index snapshot tests")
        self.git("init", "-q")
        self.git("add", ".")

    def rules(self, report):
        return {item["rule"] for item in report["findings"]}


class WikiTests(ProjectFixture):
    def test_valid_project_does_not_require_archive_directory(self):
        """PW-01.2"""
        code, report = self.run_cli("check")
        self.assertEqual(code, 0, report)
        self.assertEqual(report["documents_checked"], 4)

    def test_project_without_archive_root_still_checks(self):
        """PW-01.2"""
        self.config["roots"] = [r for r in self.config["roots"] if r["role"] != "archive"]
        self.save_config()
        code, report = self.run_cli("check")
        self.assertEqual(code, 0, report)
        code, report = self.run_cli("check-new", "docs/new.md")
        self.assertEqual(code, 0, report)
        self.assertIsNone(report["history_match"])
        code, report = self.run_cli("archive", "docs/INDEX.md")
        self.assertEqual(code, 2)
        self.assertIn("No archive root is registered", report["findings"][0]["message"])
        self.initialize_index()
        code, report = self.run_cli("check", "--staged")
        self.assertEqual(code, 0, report)

    def test_no_root_fallback_and_exact_case(self):
        """PW-09.1"""
        self.write("docs/topic.md", "# Topic\n[Wrong relative](docs/INDEX.md)\n[Wrong case](index.md)\n")
        code, report = self.run_cli("check")
        self.assertEqual(code, 1)
        self.assertEqual(sum(x["rule"] == "broken-link" for x in report["findings"]), 2)

    def test_reference_links_images_and_code_blocks(self):
        """PW-09.1"""
        self.write("docs/topic.md", """# Topic
[explicit][intro]
[intro][]
[intro]
![image](diagram.svg)

[intro]: INDEX.md#current "Introduction"
`[ignore](missing.md)`
```markdown
[also ignore](missing.md)
```
""")
        self.write("docs/diagram.svg", "<svg/>")
        code, report = self.run_cli("check")
        self.assertEqual(code, 0, report)
        self.write("docs/topic.md", "# Topic\n[Missing][not-defined]\n")
        code, report = self.run_cli("check")
        self.assertEqual(code, 1)
        self.assertIn("missing-reference", self.rules(report))

    def test_atx_anchors_duplicates_unicode_and_explicit_anchor(self):
        """PW-09.2"""
        self.write("docs/topic.md", "# 运行方式\n## Same\n## Same\n## Same-1\n<a id=\"manual\"></a>\n")
        self.write("README.md", "# Example\n[A](docs/topic.md#运行方式)\n[B](docs/topic.md#same-1)\n[C](docs/topic.md#manual)\n[D](docs/topic.md#same-1-1)\n")
        code, report = self.run_cli("check")
        self.assertEqual(code, 0, report)
        self.write("README.md", "# Example\n[A](docs/topic.md#absent)\n")
        code, report = self.run_cli("check")
        self.assertEqual(code, 1)
        self.assertIn("broken-anchor", self.rules(report))

    def test_relative_root_directory_link(self):
        """PW-09.1"""
        self.write("docs/topic.md", "# Topic\n[Project](../)\n[Remote](//example.com/help)\n")
        code, report = self.run_cli("check")
        self.assertEqual(code, 0, report)

    def test_standalone_agent_imports_are_case_sensitive(self):
        """PW-03.3"""
        self.config["entrypoints"].append("CLAUDE.md")
        self.save_config()
        self.write("CLAUDE.md", "@AGENTS.MD\n")
        code, report = self.run_cli("check")
        self.assertEqual(code, 1)
        self.assertIn("broken-link", self.rules(report))
        self.write("CLAUDE.md", "@AGENTS.md\n")
        self.assertEqual(self.run_cli("check")[0], 0)

    def test_single_long_line_cannot_bypass_character_budget(self):
        """PW-03.2"""
        self.write("AGENTS.md", "# Rules\n" + "长" * 1001)
        code, report = self.run_cli("check")
        self.assertEqual(code, 1)
        self.assertIn("page-budget", self.rules(report))

    def test_unregistered_nested_docs_are_reported_and_exclusions_explicit(self):
        """PW-04.2"""
        self.write("client/docs/README.md", "# Client\n")
        self.write("tmp/notes/docs/README.md", "# Scratch\n")
        code, report = self.run_cli("check")
        self.assertEqual(code, 1)
        unregistered = [x["path"] for x in report["findings"] if x["rule"] == "unregistered-docs"]
        self.assertEqual(unregistered, ["client/docs"])

    def test_small_module_can_have_only_a_readme(self):
        """PW-04.1"""
        self.write("small/README.md", "# Small module\n\nOne responsibility.\n")
        self.config["modules"] = [{"name": "small", "path": "small", "entry": "small/README.md"}]
        self.save_config()
        code, report = self.run_cli("check")
        self.assertEqual(code, 0, report)
        self.assertEqual(report["documents_checked"], 5)

    def test_legacy_archive_does_not_make_primary_target_ambiguous(self):
        """PW-06.4"""
        self.config["roots"].append({"path": "dev/roadmap/archive", "role": "archive"})
        self.save_config()
        self.write("dev/roadmap/archive/old.md", "# Old plan\n")
        code, report = self.run_cli("check-new", "docs/new.md")
        self.assertEqual(code, 0, report)
        self.assertIn("legacy-history-unmatched", self.rules(report))
        self.assertEqual(report["history_match_scope"]["primary_root"], "archive")
        code, report = self.run_cli("archive", "docs/INDEX.md")
        self.assertEqual(code, 0, report)
        self.assertEqual(report["destination"], "archive/docs/INDEX.md")

    def test_historical_links_warn_and_same_identity_is_allowed(self):
        """PW-09.5"""
        self.write("archive/docs/old.md", "# Old\n[Gone](gone.md)\n")
        self.config["pages"] += [
            {"path": "docs/INDEX.md", "id": "doc-1"},
            {"path": "archive/docs/old.md", "id": "doc-1"},
        ]
        self.save_config()
        code, report = self.run_cli("check")
        self.assertEqual(code, 0, report)
        self.assertEqual(report["warnings"], 1)
        self.config["pages"].append({"path": "dev/INDEX.md", "id": "doc-1"})
        self.save_config()
        code, report = self.run_cli("check")
        self.assertEqual(code, 1)
        self.assertIn("duplicate-current-id", self.rules(report))

    def test_current_page_cannot_self_exempt_with_archive_role(self):
        """PW-09.5"""
        self.write("docs/hidden.md", "# Hidden\n[Broken](missing.md)\n")
        self.config["pages"] += [
            {"path": "docs/INDEX.md", "id": "doc-1"},
            {"path": "docs/hidden.md", "id": "doc-1", "role": "archive"},
        ]
        self.save_config()
        code, report = self.run_cli("check")
        self.assertEqual(code, 2)
        self.assertIn("archive requires", report["findings"][0]["message"])
        del self.config["pages"][-1]["role"]
        self.save_config()
        code, report = self.run_cli("check")
        self.assertEqual(code, 1)
        self.assertTrue({"duplicate-current-id", "broken-link"}.issubset(self.rules(report)))

    def test_relative_link_outside_root_fails_for_current_but_warns_for_history(self):
        """PW-09.5"""
        self.write("README.md", "# Example\n[Outside](../outside.md)\n")
        code, report = self.run_cli("check")
        self.assertEqual(code, 1)
        self.assertEqual(report["findings"][0]["severity"], "error")
        self.write("README.md", "# Example\n")
        self.write("archive/docs/old.md", "# Old\n[Outside](../../../outside.md)\n")
        code, report = self.run_cli("check")
        self.assertEqual(code, 0, report)
        self.assertEqual(report["findings"][0]["severity"], "warning")

    def test_new_path_history_is_advisory_and_uses_full_path(self):
        """PW-07.1"""
        self.write("archive/docs/new.md", "# Prior topic\n")
        code, report = self.run_cli("check-new", "docs/new.md")
        self.assertEqual(code, 0, report)
        self.assertIn("historical-path-match", self.rules(report))
        code, report = self.run_cli("check-new", "dev/new.md")
        self.assertEqual(code, 0)
        self.assertIsNone(report["history_match"])
        self.assertEqual(self.run_cli("check-new", "docs/INDEX.md")[0], 1)

    def test_new_path_naming_errors_and_warnings(self):
        """PW-26.2 PW-26.3"""
        code, report = self.run_cli("check-new", "docs/title input (v2).md")
        self.assertEqual(code, 1)
        self.assertIn("name-unsafe-character", self.rules(report))
        code, report = self.run_cli("check-new", "dev/plans/plan.md")
        self.assertEqual(code, 0)
        self.assertEqual({"name-template-placeholder"}, self.rules(report))
        code, report = self.run_cli("check-new", "docs/v2-api.md")
        self.assertEqual(code, 0)
        self.assertIn("name-status-or-version", self.rules(report))
        code, report = self.run_cli("check-new", "docs/requirements.md")
        self.assertEqual((code, self.rules(report)), (0, set()), "a recommended layout is not a template placeholder")

    def test_new_path_naming_imposes_no_house_style(self):
        """PW-26.4"""
        for path in ("docs/设计/标题校验.md", "docs/Design_Notes.md", "dev/reviews/2026-10-28-title-input/README.md",
                     "docs/TitleRules.md"):
            code, report = self.run_cli("check-new", path)
            self.assertEqual((code, self.rules(report)), (0, set()), path)

    def test_staged_archive_and_rename_keep_existing_names(self):
        """PW-26.5"""
        self.write("dev/plans/old plan.md", "# Old plan\n\n状态：已完成。\n")
        self.write("dev/notes (v1).md", "# Notes\n")
        self.initialize_index()
        self.git("-c", "user.name=Wiki Test", "-c", "user.email=wiki@example.invalid", "-c", "commit.gpgsign=false",
                 "commit", "-q", "--no-verify", "-m", "Legacy names")
        (self.root / "archive/dev/plans").mkdir(parents=True)
        self.git("mv", "dev/plans/old plan.md", "archive/dev/plans/old plan.md")
        self.git("mv", "dev/notes (v1).md", "dev/plans/notes (v1).md")
        code, report = self.run_cli("check", "--staged")
        self.assertEqual(code, 0, report)
        self.assertFalse({"name-unsafe-character", "name-status-or-version"} & self.rules(report))
        self.git("mv", "dev/plans/notes (v1).md", "dev/plans/renamed notes.md")
        self.write("dev/new idea.md", "# New idea\n")
        self.git("add", "dev/new idea.md")
        code, report = self.run_cli("check", "--staged")
        self.assertEqual(code, 1)
        self.assertEqual([x["path"] for x in report["findings"] if x["rule"] == "name-unsafe-character"],
                         ["dev/new idea.md", "dev/plans/renamed notes.md"], "new files and new names are still checked")

    def test_document_names_that_only_differ_by_case_fail(self):
        """PW-26.1"""
        self.write("docs/Plan.md", "# Plan\n")
        self.write("docs/plan.md", "# plan\n")
        code, report = self.run_cli("check")
        self.assertEqual(code, 1)
        self.assertIn("name-case-collision", self.rules(report))

    def test_staged_new_document_gets_naming_warning(self):
        """PW-26.2 PW-26.3"""
        self.write("docs/v2-api.md", "# Versioned API\n")
        self.initialize_index()
        code, report = self.run_cli("check", "--staged")
        self.assertEqual(code, 0, report)
        self.assertIn("name-status-or-version", self.rules(report))

    def test_history_match_requires_file_but_archive_collision_includes_directory(self):
        """PW-07.2"""
        self.write("archive/docs/new.md/extra.md", "# Historical child\n")
        code, report = self.run_cli("check-new", "docs/new.md")
        self.assertEqual(code, 0, report)
        self.assertIsNone(report["history_match"])
        self.write("docs/new.md", "# New\n")
        code, report = self.run_cli("archive", "docs/new.md")
        self.assertEqual(code, 1)
        self.assertIn("archive-collision", self.rules(report))
        self.initialize_index()
        code, report = self.run_cli("check", "--staged")
        self.assertEqual(code, 0, report)
        self.assertNotIn("historical-path-match", self.rules(report))

    def test_archive_preserves_name_previews_links_and_never_writes(self):
        """PW-06.1"""
        self.write("docs/plan.md", "# Plan\n[Code](../src/example.py)\n")
        self.write("src/example.py", "value = 1\n")
        self.write("README.md", "# Example\n[Plan](docs/plan.md#plan)\n")
        before = {p.relative_to(self.root).as_posix(): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        code, report = self.run_cli("archive", "docs/plan.md")
        self.assertEqual(code, 0, report)
        self.assertEqual(report["destination"], "archive/docs/plan.md")
        targets = {x["suggested_target"] for x in report["affected_links"]}
        self.assertEqual(targets, {"../../src/example.py", "archive/docs/plan.md#plan"})
        after = {p.relative_to(self.root).as_posix(): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(before, after)
        self.assertFalse(report["writes"])

    def test_archive_conflict_blocks_even_when_bytes_identical(self):
        """PW-06.2"""
        self.write("archive/docs/INDEX.md", (self.root / "docs/INDEX.md").read_text())
        code, report = self.run_cli("archive", "docs/INDEX.md")
        self.assertEqual(code, 1)
        self.assertIn("archive-collision", self.rules(report))

    def test_archive_reports_unresolved_outgoing_links(self):
        """PW-06.1"""
        self.write("docs/plan.md", "# Plan\n[External project](../../other/docs.md)\n[Missing](missing.md)\n")
        code, report = self.run_cli("archive", "docs/plan.md")
        self.assertEqual(code, 0, report)
        self.assertEqual(self.rules(report), {"archive-unresolved-link", "archive-unresolved-target"})
        self.assertEqual(report["affected_links"], [])
        self.assertFalse(report["writes"])

    def test_index_is_deterministic_and_check_is_read_only(self):
        """PW-09.7"""
        first = self.run_cli("index")
        second = self.run_cli("index")
        self.assertEqual(first, second)
        self.assertNotIn("updated", first[1])
        self.config["generated_index"] = "docs/wiki-index.json"
        self.save_config()
        # The index command has a plain exit status on successful comparison.
        encoded = json.dumps(first[1], ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        self.write("docs/wiki-index.json", encoded)
        result = subprocess.run([sys.executable, str(SCRIPT), "index", "--root", str(self.root), "--check"], capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.write("docs/new.md", "# New\n")
        code, report = self.run_cli("index", "--check")
        self.assertEqual(code, 1)
        self.assertIn("index-outdated", self.rules(report))

    def test_invalid_json_and_version_are_incomplete(self):
        """PW-09.4"""
        self.write("docs/wiki.json", "{bad}")
        code, report = self.run_cli("check")
        self.assertEqual(code, 2)
        self.assertEqual(report["result"], "incomplete")
        self.config["version"] = True
        self.save_config()
        self.assertEqual(self.run_cli("check")[0], 2)

    def test_doctor_warns_when_archive_root_is_not_ignored(self):
        """PW-08.2"""
        code, report = self.run_cli("doctor")
        self.assertIn("archive-default-search", self.rules(report))
        self.write(".ignore", "/archive/\n")
        self.assertNotIn("archive-default-search", self.rules(self.run_cli("doctor")[1]))

    def test_doctor_does_not_claim_hooks_verified(self):
        """PW-09.6"""
        self.write(".ignore", "/archive/\n")
        code, report = self.run_cli("doctor")
        self.assertEqual(code, 0)
        self.assertIn("unknown", report["hooks"])
        self.assertEqual(report["result"], "passed_with_warnings")

    def test_staged_rejects_worktree_only_repair(self):
        """PW-09.3"""
        self.write("README.md", "# Example\n[Broken](missing.md)\n")
        self.initialize_index()
        self.write("README.md", "# Example\n[Fixed](docs/INDEX.md)\n")
        self.assertEqual(self.run_cli("check")[0], 0)
        code, report = self.run_cli("check", "--staged")
        self.assertEqual(code, 1)
        self.assertIn("broken-link", self.rules(report))
        self.assertTrue(report["snapshot"].startswith("git-index-sha256:"))

    def test_staged_does_not_use_untracked_target_or_unstaged_config(self):
        """PW-09.3"""
        self.write("docs/topic.md", "# Topic\n[Target](missing.md)\n")
        self.initialize_index()
        self.write("docs/missing.md", "# Target\n")
        self.config["exclude"].append("docs/topic.md")
        self.save_config()
        self.assertEqual(self.run_cli("check")[0], 0)
        code, report = self.run_cli("check", "--staged")
        self.assertEqual(code, 1)
        self.assertIn("broken-link", self.rules(report))

    def test_staged_requires_git_and_index_configuration(self):
        """PW-09.4"""
        self.assertEqual(self.run_cli("check", "--staged")[0], 2)
        self.initialize_index()
        self.git("rm", "--cached", "docs/wiki.json")
        code, report = self.run_cli("check", "--staged")
        self.assertEqual(code, 2)
        self.assertEqual(report["result"], "incomplete")

    def test_staged_blob_reads_remain_frozen_after_index_changes(self):
        """PW-09.3"""
        self.initialize_index()
        snap = wiki.Snapshot(self.root, staged=True)
        original = (self.root / "README.md").read_bytes()
        self.write("README.md", "# Changed\n")
        self.git("add", "README.md")
        self.assertEqual(snap.read("README.md"), original)

    def test_staged_initial_project_reports_matching_history(self):
        """PW-07.3"""
        self.write("archive/docs/restored.md", "# Previous version\n")
        self.write("docs/restored.md", "# Restored current version\n")
        self.initialize_index()
        code, report = self.run_cli("check", "--staged")
        self.assertEqual(code, 0, report)
        self.assertEqual(report["head_baseline"], "unborn")
        matches = [x["path"] for x in report["findings"] if x["rule"] == "historical-path-match"]
        self.assertEqual(matches, ["docs/restored.md"])

    def test_staged_restore_compares_against_captured_head(self):
        """PW-07.3"""
        self.write("archive/docs/restored.md", "# Previous version\n")
        self.initialize_index()
        self.git("-c", "user.name=Wiki Test", "-c", "user.email=wiki@example.invalid", "commit", "-qm", "Fixture baseline")
        baseline = self.git("rev-parse", "HEAD")
        self.write("docs/restored.md", "# Restored current version\n")
        self.git("add", "docs/restored.md")
        snap = wiki.Snapshot(self.root, staged=True)
        self.git("-c", "user.name=Wiki Test", "-c", "user.email=wiki@example.invalid", "commit", "-qm", "Move HEAD after capture")
        findings = wiki.check(wiki.Wiki(snap))
        self.assertEqual(snap.head_oid, baseline)
        self.assertTrue(any(f.rule == "historical-path-match" and f.path == "docs/restored.md" for f in findings))

    def test_unmerged_index_fails_closed(self):
        """PW-09.4"""
        self.initialize_index()
        oid = self.git("hash-object", "-w", "--stdin", input="conflict\n")
        self.git("update-index", "--index-info", input=f"100644 {oid} 1\tconflict.md\n100644 {oid} 2\tconflict.md\n")
        code, report = self.run_cli("check", "--staged")
        self.assertEqual(code, 2)
        self.assertIn("Unmerged", report["findings"][0]["message"])


class RemindTests(ProjectFixture):
    """Commit-time reminders; each test builds a temporary Git history."""

    GIT_ENV = {"GIT_AUTHOR_NAME": "Wiki Test", "GIT_AUTHOR_EMAIL": "wiki@example.invalid",
               "GIT_COMMITTER_NAME": "Wiki Test", "GIT_COMMITTER_EMAIL": "wiki@example.invalid"}

    def setUp(self):
        super().setUp()
        if not shutil.which("git"):
            self.skipTest("git is required for reminder tests")
        self.config["modules"] = [{"name": "notes", "path": "notes", "entry": "notes/README.md", "docs": "notes/docs"}]
        self.config["remind"] = {
            "watch": [{"name": "notes", "code": ["notes/src/*"], "docs": ["notes/docs/*", "notes/README.md"]}],
            "threshold": {"commits": 3, "lines": 1000},
            "block_at": {"commits": 5},
            "ask_user": ["docs/requirements.md"],
        }
        self.save_config()
        self.write("notes/README.md", "# Notes\n\n[Design](docs/design.md)\n")
        self.write("notes/docs/design.md", "# Design\n\nSee [count decision](decisions/count.md).\n")
        self.write("notes/docs/decisions/count.md", "# Count decision\n\nStatus: current.\n")
        self.write("notes/src/title.py", "LIMIT = 60\n")
        self.git("init", "-q")
        self.commit("Initial project", all_files=True)

    def commit(self, message, all_files=False, verify=False):
        import os
        if all_files:
            self.git("add", "-A")
        args = ["git", "-C", str(self.root), "-c", "commit.gpgsign=false", "commit", "-q", "-m", message]
        if not verify:
            args.append("--no-verify")
        return subprocess.run(args, capture_output=True, text=True, env={**os.environ, **self.GIT_ENV})

    def change_code(self, number):
        self.write("notes/src/title.py", f"LIMIT = {60 + number}\n")
        self.git("add", "notes/src/title.py")

    def message(self, text):
        path = self.root / "MSG"
        path.write_text(text, encoding="utf-8")
        return str(path)

    def watch(self, report):
        return {item["name"]: item for item in report["watch_status"]}

    def test_staged_code_without_docs_reminds_without_blocking(self):
        """PW-11.1"""
        self.change_code(1)
        code, report = self.run_cli("remind", "--staged")
        self.assertEqual(code, 0, report)
        self.assertIn("docs-not-updated", self.rules(report))
        self.assertEqual(self.watch(report)["notes"]["commits"], 1)

    def test_staged_numstat_uses_the_captured_index_and_head(self):
        """PW-11.9"""
        self.change_code(1)
        captured = wiki.Snapshot(self.root, staged=True)
        self.write("notes/src/title.py", "LIMIT = 62\n")
        self.git("add", "notes/src/title.py")
        self.assertEqual(wiki.snapshot_numstat(captured), [("notes/src/title.py", 2)])

    def test_staged_numstat_handles_links_and_submodules_and_reads_only_changes(self):
        """PW-11.11"""
        (self.root / "notes/link.md").symlink_to("README.md")
        self.git("add", "notes/link.md")
        oid = self.git("rev-parse", "HEAD")
        self.git("update-index", "--add", "--cacheinfo", f"160000,{oid},vendor/sub")
        self.commit("Add a symlink and a submodule entry")
        self.change_code(1)
        (self.root / "notes/link.md").unlink()
        (self.root / "notes/link.md").symlink_to("docs/design.md")
        self.git("add", "notes/link.md")
        code, report = self.run_cli("remind", "--staged", "--message-file", self.message("Change\n"))
        self.assertEqual(code, 0, report)
        self.assertIn("docs-not-updated", self.rules(report))
        captured = wiki.Snapshot(self.root, staged=True)
        with mock.patch.object(wiki.Snapshot, "head_read", autospec=True, side_effect=wiki.Snapshot.head_read) as head_read:
            changes = wiki.snapshot_numstat(captured)
        self.assertEqual(changes, [("notes/link.md", 0), ("notes/src/title.py", 2)])
        self.assertEqual([call.args[1] for call in head_read.call_args_list], ["notes/src/title.py"],
                         "unchanged objects and non-regular entries are not read")

    def test_staged_docs_update_resets_count_and_silences_reminder(self):
        """PW-11.2"""
        for number in range(3):
            self.change_code(number + 1)
            self.commit(f"Change {number}")
        self.change_code(9)
        self.write("notes/docs/design.md", "# Design\n\nLimit changed. See [count decision](decisions/count.md).\n")
        self.git("add", "notes/docs/design.md")
        code, report = self.run_cli("remind", "--staged")
        self.assertEqual(code, 0, report)
        self.assertNotIn("docs-not-updated", self.rules(report))
        self.assertNotIn("docs-review-due", self.rules(report))
        self.assertEqual(self.watch(report)["notes"]["since"], "this commit")

    def test_history_count_reaches_threshold_and_docs_commit_resets_it(self):
        """PW-11.2"""
        for number in range(3):
            self.change_code(number + 1)
            self.commit(f"Change {number}")
        code, report = self.run_cli("remind")
        self.assertEqual(code, 0, report)
        self.assertIn("docs-review-due", self.rules(report))
        self.assertEqual(self.watch(report)["notes"]["commits"], 3)
        self.write("notes/README.md", "# Notes\n\nReviewed.\n\n[Design](docs/design.md)\n")
        self.git("add", "notes/README.md")
        self.commit("Update notes docs")
        code, report = self.run_cli("remind")
        self.assertEqual(self.watch(report)["notes"]["commits"], 0)
        self.assertNotIn("docs-review-due", self.rules(report))

    def test_review_trailer_resets_only_with_reason(self):
        """PW-11.2"""
        for number in range(3):
            self.change_code(number + 1)
            self.commit(f"Change {number}")
        self.commit("Refactor only\n\nDocs-Reviewed: notes")
        self.assertEqual(self.watch(self.run_cli("remind")[1])["notes"]["commits"], 3)
        self.change_code(7)
        self.commit("Rename variable\n\nDocs-Reviewed: notes no behavior change")
        self.assertEqual(self.watch(self.run_cli("remind")[1])["notes"]["commits"], 0)

    def test_block_at_fails_only_for_more_unreviewed_code(self):
        """PW-11.3"""
        for number in range(5):
            self.change_code(number + 1)
            self.commit(f"Change {number}")
        self.write("dev/INDEX.md", "# Work\n\nUnrelated note.\n")
        self.git("add", "dev/INDEX.md")
        code, report = self.run_cli("remind", "--staged")
        self.assertEqual(code, 0, report)
        self.git("reset", "-q", "dev/INDEX.md")
        self.change_code(9)
        code, report = self.run_cli("remind", "--staged", "--message-file", self.message("More code\n"))
        self.assertEqual(code, 1, report)
        self.assertIn("docs-review-overdue", self.rules(report))
        incomplete = self.message("More code\n\nDocs-Reviewed: notes\n")
        code, report = self.run_cli("remind", "--staged", "--message-file", incomplete)
        self.assertEqual(code, 1, report)
        self.assertIn("review-trailer-incomplete", self.rules(report))
        reviewed = self.message("More code\n\nDocs-Reviewed: notes read design, still accurate\n# comment line\n")
        code, report = self.run_cli("remind", "--staged", "--message-file", reviewed)
        self.assertEqual(code, 0, report)
        self.assertNotIn("docs-review-overdue", self.rules(report))

    def test_summary_mode_never_blocks(self):
        """PW-11.4"""
        for number in range(6):
            self.change_code(number + 1)
            self.commit(f"Change {number}")
        code, report = self.run_cli("remind")
        self.assertEqual(code, 0, report)
        overdue = [x for x in report["findings"] if x["rule"] == "docs-review-overdue"]
        self.assertEqual([x["severity"] for x in overdue], ["warning"])

    def test_decision_change_lists_unstaged_linking_documents_and_ask_user(self):
        """PW-11.5"""
        self.write("docs/requirements.md", "# Requirements\n\nTitles have at most 60 code points.\n")
        self.git("add", "docs/requirements.md")
        self.commit("Add requirements")
        self.write("notes/docs/decisions/count.md", "# Count decision\n\nStatus: superseded.\n")
        self.write("docs/requirements.md", "# Requirements\n\nTitles have at most 80 code points.\n")
        self.git("add", "notes/docs/decisions/count.md", "docs/requirements.md")
        code, report = self.run_cli("remind", "--staged")
        self.assertEqual(code, 0, report)
        sync = [x for x in report["findings"] if x["rule"] == "decision-sync"]
        self.assertEqual(len(sync), 1)
        self.assertIn("notes/docs/design.md", sync[0]["message"])
        self.assertIn("docs/requirements.md", [x["path"] for x in report["findings"] if x["rule"] == "ask-user"])

    def test_remind_without_configuration_or_git_is_incomplete(self):
        """PW-11.7"""
        del self.config["remind"]
        self.save_config()
        self.assertEqual(self.run_cli("remind")[0], 2)
        self.config["remind"] = {"watch": [{"name": "bad name", "code": ["x"], "docs": ["y"]}], "threshold": {"commits": 1}}
        self.save_config()
        self.assertEqual(self.run_cli("check")[0], 2)

    def install_hooks(self):
        tool_dir = self.root / "scripts" / "wiki"
        shutil.copytree(SCRIPT.parent, tool_dir, ignore=shutil.ignore_patterns("__pycache__"))
        self.config["exclude"].append("scripts/**")
        self.save_config()
        self.git("add", "-A")
        self.commit("Add wiki tool")
        self.git("config", "core.hooksPath", "scripts/wiki/hooks")

    def test_real_git_hooks_block_bad_docs_and_print_reminders(self):
        """PW-11.6"""
        self.install_hooks()
        code, report = self.run_cli("doctor")
        self.assertEqual(report["git_hooks"], {"pre-commit": "installed", "commit-msg": "installed"})
        self.write("docs/INDEX.md", "# Current\n\n[Missing](missing.md)\n")
        self.git("add", "docs/INDEX.md")
        result = self.commit("Break a link", verify=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("broken-link", result.stdout + result.stderr)
        self.git("checkout", "-q", "HEAD", "--", "docs/INDEX.md")
        self.change_code(3)
        result = self.commit("Change limit", verify=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("docs-not-updated", result.stdout + result.stderr)

    def test_doctor_reports_missing_hooks(self):
        """PW-09.6"""
        code, report = self.run_cli("doctor")
        self.assertEqual(report["git_hooks"]["pre-commit"], "missing")
        self.assertIn("hook-not-installed", self.rules(report))

    def test_finished_plan_still_in_dev_is_reminded(self):
        """PW-11.8"""
        self.write("dev/plans/done-work.md", "# Done work\n\n状态：已完成。范围：notes。\n")
        self.write("dev/plans/no-status.md", "# Something\n\nNo status here.\n")
        code, report = self.run_cli("remind")
        self.assertEqual(code, 0, report)
        by_rule = {x["rule"]: x["path"] for x in report["findings"]}
        self.assertEqual(by_rule.get("plan-finished-not-archived"), "dev/plans/done-work.md")
        self.assertEqual(by_rule.get("plan-no-status"), "dev/plans/no-status.md")

    def test_new_human_claims_are_shown_to_the_user(self):
        """PW-11.12"""
        self.write("docs/guide.md", "# Guide\n\n核对：human:alice，2026-10-01。\n\nFormat: `human:<名字>`.\n")
        self.git("add", "docs/guide.md")
        self.commit("Add guide")
        self.write("docs/guide.md", "# Guide\n\n核对：human:alice，2026-10-01。\n\nFormat: `human:<名字>` or human:<名字>.\n\n"
                   "```\n核对：human:example，2026-10-02。\n```\n")
        self.git("add", "docs/guide.md")
        code, report = self.run_cli("remind", "--staged")
        self.assertEqual(code, 0, report)
        self.assertNotIn("human-claim-added", self.rules(report), "existing lines, code and placeholders are not claims")
        self.write("docs/guide.md", "# Guide\n\n核对：human:alice，2026-10-01；human:bob，2026-10-30。\n\nFormat: `human:<名字>`.\n")
        self.write("dev/reviews/2026-10-30-x/r01-a.md", "# r01\n\n| 1 | human:carol | 成立 | read it |\n")
        self.git("add", "docs/guide.md", "dev/reviews/2026-10-30-x/r01-a.md")
        code, report = self.run_cli("remind", "--staged")
        claims = {x["path"]: x for x in report["findings"] if x["rule"] == "human-claim-added"}
        self.assertEqual(set(claims), {"docs/guide.md", "dev/reviews/2026-10-30-x/r01-a.md"})
        self.assertIn("human:alice, human:bob", claims["docs/guide.md"]["message"], "the changed line lists its names")
        self.assertTrue(claims["docs/guide.md"]["message"].startswith("[user]"))
        self.assertEqual(code, 0, "the reminder does not block the commit")

    def test_inbox_items_are_reminded_until_archived(self):
        """PW-11.13"""
        import os
        self.write("dev/inbox/README.md", "# Inbox\n\nOne file per item.\n")
        self.write("dev/inbox/bug/old.md", "# Old question\n\n状态：待分诊。来源：test。\n")
        self.git("add", "dev/inbox")
        old = {**os.environ, **self.GIT_ENV, "GIT_AUTHOR_DATE": "2020-01-01T00:00:00", "GIT_COMMITTER_DATE": "2020-01-01T00:00:00"}
        subprocess.run(["git", "-C", str(self.root), "-c", "commit.gpgsign=false", "commit", "-q", "--no-verify", "-m", "Old item"],
                       check=True, env=old, capture_output=True)
        self.write("dev/inbox/bug/new.md", "# New question\n\n状态：待分诊。\n")
        self.write("dev/inbox/request/done.md", "# Done request\n\n状态：已完成。去向：dev/plans/x.md。\n")
        self.write("dev/inbox/request/bare.md", "# No status\n\nJust text.\n")
        self.git("add", "dev/inbox")
        self.commit("More items")
        code, report = self.run_cli("remind")
        self.assertEqual(code, 0, report)
        found = {(x["rule"], x["path"]) for x in report["findings"] if x["rule"].startswith("inbox-")}
        self.assertEqual(found, {("inbox-stale", "dev/inbox/bug/old.md"),
                                 ("inbox-finished-not-archived", "dev/inbox/request/done.md"),
                                 ("inbox-no-status", "dev/inbox/request/bare.md")})

    def test_active_plan_without_recent_commit_is_stale(self):
        """PW-11.8"""
        import os
        self.write("dev/plans/old-work.md", "# Old work\n\n状态：执行中。\n")
        self.git("add", "dev/plans/old-work.md")
        old = {**os.environ, **self.GIT_ENV, "GIT_AUTHOR_DATE": "2020-01-01T00:00:00", "GIT_COMMITTER_DATE": "2020-01-01T00:00:00"}
        subprocess.run(["git", "-C", str(self.root), "-c", "commit.gpgsign=false", "commit", "-q", "--no-verify", "-m", "Old plan"],
                       check=True, env=old, capture_output=True)
        self.write("dev/plans/new-work.md", "# New work\n\n状态：执行中。\n")
        self.git("add", "dev/plans/new-work.md")
        self.commit("New plan")
        code, report = self.run_cli("remind")
        stale = [x["path"] for x in report["findings"] if x["rule"] == "plan-stale"]
        self.assertEqual(stale, ["dev/plans/old-work.md"])
        self.write("dev/plans/old-work.md", "# Old work\n\n状态：执行中。\n\nStep 2 started.\n")
        self.git("add", "dev/plans/old-work.md")
        code, report = self.run_cli("remind", "--staged")
        self.assertNotIn("plan-stale", self.rules(report))


class ReviewTests(ProjectFixture):
    DIR = "dev/reviews/2026-10-28-sample"

    def finding(self, finding_id, verdict, rows=(), extra="", author="A"):
        table = ""
        if rows:
            table = "**核对**\n\n| 轮次 | 核对人 | 判定 | 依据 |\n|---|---|---|---|\n" + "".join(
                f"| {i} | {who} | {v} | evidence |\n" for i, (who, v) in enumerate(rows, 1))
        return f"## {finding_id} Title\n\n状态：{verdict}。\n\n**观察**（作者：{author}，2026-10-28）\n\nFacts.\n\n{table}\n{extra}\n"

    def review(self, *routes, plans=()):
        self.write(f"{self.DIR}/README.md", "# Review\n\n状态：进行中。范围：x。\n")
        for name, body in routes:
            self.write(f"{self.DIR}/{name}.md", f"# {name}\n\n范围：x。\n\n{body}")
        for name, body in plans:
            self.write(f"{self.DIR}/{name}.md", body)
        return self.run_cli("check")

    def test_complete_review_passes(self):
        """PW-14.1"""
        body = (self.finding("r01-1", "成立", [("B", "成立")], "**方案**\n\nFix it.\n")
                + self.finding("r01-2", "不成立", [("B", "不成立")])
                + self.finding("r01-3", "重复", [("B", "重复")], "Same as r01-1.\n")
                + self.finding("r01-4", "已知", [("B", "已知")], "See [plan](../../INDEX.md).\n"))
        code, report = self.review(("r01-scope", body))
        self.assertEqual(code, 0, report)
        self.assertFalse([x for x in report["findings"] if x["rule"].startswith("review-")], report)

    def test_routes_are_free_form_and_ids_unique_across_files(self):
        """PW-14.1"""
        code, report = self.review(("r01-security", self.finding("r01-1", "成立", [("B", "成立")], "**方案**\n\nx\n")),
                                   ("r02-session-restore", self.finding("r01-1", "成立", [("A", "成立")], "**方案**\n\nx\n")))
        self.assertEqual(code, 1)
        self.assertIn("review-duplicate-id", self.rules(report))

    def test_missing_verdict_and_bad_references_fail(self):
        """PW-14.2"""
        body = ("## r01-1 No verdict\n\nJust text.\n"
                + self.finding("r01-2", "重复", [("B", "重复")], "No id here.\n")
                + self.finding("r01-3", "已知", [("B", "已知")], "No link.\n"))
        code, report = self.review(("r01-x", body))
        self.assertEqual(code, 1)
        self.assertTrue({"review-verdict-missing", "review-duplicate-target", "review-known-target"} <= self.rules(report))

    def test_warnings_for_unverified_self_checked_mismatched_and_planless(self):
        """PW-14.3"""
        body = (self.finding("r01-1", "待核对")
                + self.finding("r01-2", "成立", [("A", "成立")], "**方案**\n\nx\n")
                + self.finding("r01-3", "成立", [("B", "成立"), ("C", "收窄")], "**方案**\n\nx\n")
                + self.finding("r01-4", "收窄", [("B", "收窄")])
                + self.finding("r01-5", "成立"))
        code, report = self.review(("r01-x", body))
        self.assertEqual(code, 0, report)
        by_id = {}
        for item in report["findings"]:
            by_id.setdefault(item["key"], set()).add(item["rule"])
        self.assertEqual(by_id["r01-1"], {"review-unverified"})
        self.assertEqual(by_id["r01-2"], {"review-no-independent-check"})
        self.assertEqual(by_id["r01-3"], {"review-verdict-mismatch"})
        self.assertEqual(by_id["r01-4"], {"review-plan-missing"})
        self.assertEqual(by_id["r01-5"], {"review-check-missing", "review-plan-missing"})

    def test_shared_plan_covers_findings_and_unknown_ids_fail(self):
        """PW-14.4"""
        body = self.finding("r01-1", "成立", [("B", "成立")]) + self.finding("r02-1", "收窄", [("B", "收窄")])
        plan = "# Shared fix\n\n状态：草案。\n\n覆盖问题：r01-1、r02-1、r09-9\n"
        code, report = self.review(("r01-x", body), plans=[("plan-shared", plan)])
        self.assertEqual(code, 1)
        self.assertNotIn("review-plan-missing", self.rules(report))
        self.assertEqual([x["key"] for x in report["findings"] if x["rule"] == "review-plan-unknown-id"], ["r09-9"])

    def test_single_route_review_can_live_in_readme(self):
        """PW-14.5"""
        self.write(f"{self.DIR}/README.md", "# Review\n\n状态：进行中。\n\n" + self.finding("r01-1", "不成立", [("B", "不成立")]))
        code, report = self.run_cli("check")
        self.assertEqual(code, 0, report)

    def test_archived_review_is_not_rechecked(self):
        """PW-14.5"""
        self.write("archive/dev/reviews/old/README.md", "# Old\n\n状态：已完成。\n\n## r01-1 Old\n\nno verdict\n")
        self.config["reviews"] = ["dev/reviews/*/README.md", "archive/dev/reviews/*/README.md"]
        self.save_config()
        self.assertEqual(self.run_cli("check")[0], 0)

    def test_directory_budget_warns(self):
        """PW-15.1"""
        self.config["dir_budgets"] = {"dev/reviews/*": 2}
        self.save_config()
        code, report = self.review(("r01-a", ""), ("r02-b", ""))
        self.assertEqual(code, 0, report)
        self.assertIn("dir-budget", self.rules(report))

    def test_archive_preview_moves_whole_review_directory(self):
        """PW-06.3"""
        self.review(("r01-a", self.finding("r01-1", "不成立", [("B", "不成立")], "[Index](../../INDEX.md)\n")))
        self.write(f"{self.DIR}/notes.txt", "raw notes\n")
        self.write("dev/INDEX.md", f"# Work\n\n[Review](reviews/2026-10-28-sample/README.md)\n")
        code, report = self.run_cli("archive", self.DIR)
        self.assertEqual(code, 0, report)
        self.assertEqual(report["source_kind"], "directory")
        self.assertEqual(report["destination"], f"archive/{self.DIR}")
        self.assertEqual(len(report["documents_moved"]), 2)
        changes = {(x["path"], x["suggested_target"]) for x in report["affected_links"]}
        self.assertIn(("dev/INDEX.md", "../archive/dev/reviews/2026-10-28-sample/README.md"), changes)
        self.assertIn((f"{self.DIR}/r01-a.md", "../../../../dev/INDEX.md"), changes)
        self.assertFalse(any(x["path"] == f"{self.DIR}/README.md" for x in report["affected_links"]))
        self.assertIn("archive-non-markdown", self.rules(report))
        self.assertFalse((self.root / "archive" / self.DIR).exists())

    def test_archive_directory_collision_fails(self):
        """PW-06.2"""
        self.review(("r01-a", ""))
        self.write(f"archive/{self.DIR}/README.md", "# Previous\n\n状态：已完成。\n")
        code, report = self.run_cli("archive", self.DIR)
        self.assertEqual(code, 1)
        self.assertIn("archive-collision", self.rules(report))

    def test_finished_review_is_reminded_like_a_plan(self):
        """PW-11.8"""
        if not shutil.which("git"):
            self.skipTest("git required")
        self.write(f"{self.DIR}/README.md", "# Review\n\n状态：已完成。\n")
        self.git("init", "-q")
        self.config["remind"] = {"watch": [{"name": "x", "code": ["src/*"], "docs": ["docs/*"]}], "threshold": {"commits": 5}}
        self.save_config()
        code, report = self.run_cli("remind")
        self.assertEqual(code, 0, report)
        self.assertIn(f"{self.DIR}/README.md", [x["path"] for x in report["findings"] if x["rule"] == "plan-finished-not-archived"])


class TraceTests(ProjectFixture):
    REQS = ("# Requirements\n\n"
            "### EX-01 First\n\n状态：已验证。\n\n- EX-01.1 Does a thing.\n- EX-01.2 Reads well.（人工验证）\n  验收核对：EX-01.2，agent:test，2026-10-29。\n\n证据：[tests](../../tests/test_x.py)。\n\n"
            "### EX-02 Second\n\n状态：已接受。\n\n- EX-02.1 Will do a thing.\n")

    def setUp(self):
        super().setUp()
        self.config["requirements"] = {"files": ["docs/requirements/*.md"], "tests": ["tests/*"]}
        self.save_config()
        self.write("docs/requirements/main.md", self.REQS)
        self.write("docs/design.md", "# Design\n\n对应需求：EX-01、EX-02。\n")
        self.write("tests/test_x.py", '"""EX-01.1"""\n')

    def trace(self):
        code, report = self.run_cli("check")
        return code, report, {(x["rule"], x.get("key")) for x in report["findings"] if x["rule"].startswith("trace-")}

    def test_complete_trace_passes(self):
        """PW-16.3"""
        code, report, found = self.trace()
        self.assertEqual(code, 0, report)
        self.assertEqual(found, set())

    def test_unknown_references_fail_in_docs_and_tests(self):
        """PW-16.1"""
        self.write("docs/other.md", "# Other\n\nSee EX-09 and EX-01.7.\n")
        self.write("tests/test_y.py", "# EX-03.1\n")
        code, report, found = self.trace()
        self.assertEqual(code, 1)
        self.assertEqual({k for r, k in found if r == "trace-unknown-ref"}, {"EX-09", "EX-01.7", "EX-03.1"})

    def test_duplicate_id_and_missing_status_fail(self):
        """PW-16.2"""
        self.write("docs/requirements/more.md", "# More\n\n### EX-01 Again\n\n状态：提出。\n\n### EX-03 No status\n\nText.\n\n### EX-04 Odd\n\n状态：随便。\n")
        code, report, found = self.trace()
        self.assertEqual(code, 1)
        self.assertIn(("trace-duplicate-id", "EX-01"), found)
        self.assertTrue({("trace-status-missing", "EX-03"), ("trace-status-missing", "EX-04")} <= found)

    def test_missing_design_test_and_evidence_warn(self):
        """PW-16.3 PW-16.4 PW-16.5"""
        self.write("docs/design.md", "# Design\n\nNothing.\n")
        self.write("tests/test_x.py", "# no ids\n")
        self.write("docs/requirements/main.md", self.REQS.replace("证据：[tests](../../tests/test_x.py)。", "证据：见测试。"))
        code, report, found = self.trace()
        self.assertEqual(code, 0, report)
        self.assertTrue({("trace-no-design", "EX-01"), ("trace-no-design", "EX-02"),
                         ("trace-no-test", "EX-01"), ("trace-no-evidence", "EX-01")} <= found)
        no_test = [x for x in report["findings"] if x["rule"] == "trace-no-test"][0]["message"]
        self.assertIn("EX-01.1", no_test)
        self.assertNotIn("EX-01.2", no_test, "manual acceptance items need no test")

    def test_acceptance_check_only_replaces_tests_on_manual_items(self):
        """PW-16.4 PW-16.8"""
        self.write("tests/test_x.py", "# no ids\n")
        self.write("docs/requirements/main.md", self.REQS.replace(
            "- EX-01.1 Does a thing.\n", "- EX-01.1 Does a thing.\n  验收核对：EX-01.1，agent:test，2026-10-29。\n"))
        code, report, found = self.trace()
        self.assertEqual(code, 0, report)
        self.assertIn(("trace-check-not-manual", "EX-01"), found)
        no_test = [x for x in report["findings"] if x["rule"] == "trace-no-test"]
        self.assertTrue(no_test and "EX-01.1" in no_test[0]["message"], "a check record does not stand in for a test")
        self.write("tests/test_x.py", '"""EX-01.1"""\n')
        found = self.trace()[2]
        self.assertNotIn(("trace-no-test", "EX-01"), found)
        self.assertIn(("trace-check-not-manual", "EX-01"), found)

    def test_project_id_format_is_configurable(self):
        """PW-16.7"""
        self.config["requirements"]["id_pattern"] = r"(?:REQ-[A-Z]+-\d{3}|FR-\d+(?:\.\d+)*)"
        self.save_config()
        self.write("docs/requirements/main.md", "# Requirements\n\n"
                   "### REQ-AUTH-001 Sign in\n\n状态：已实现。\n\n- REQ-AUTH-001.1 Accepts a valid password.\n\n"
                   "### FR-1.2 Export\n\n状态：已实现。\n\n- FR-1.2.1 Writes CSV.\n")
        self.write("docs/design.md", "# Design\n\n对应需求：REQ-AUTH-001、FR-1.2。Uses UTF-8 and SHA-256.\n")
        self.write("tests/test_x.py", '"""REQ-AUTH-001.1 FR-1.2.1"""\n')
        code, report, found = self.trace()
        self.assertEqual((code, found), (0, set()), report)
        self.write("docs/other.md", "# Other\n\nSee REQ-AUTH-002 and FR-1.3.\n")
        code, report, found = self.trace()
        self.assertEqual(code, 1)
        self.assertEqual({k for r, k in found if r == "trace-unknown-ref"}, {"REQ-AUTH-002", "FR-1.3"})

    def test_invalid_id_pattern_is_incomplete(self):
        """PW-16.7"""
        for pattern in ("[", "", "X?", 7):
            self.config["requirements"]["id_pattern"] = pattern
            self.save_config()
            code, report = self.run_cli("check")
            self.assertEqual(code, 2, (pattern, report))
        del self.config["requirements"]["id_pattern"]
        self.config["requirements"]["id_format"] = "x"
        self.save_config()
        self.assertEqual(self.run_cli("check")[0], 2, "unknown requirements fields are reported")

    def test_process_documents_do_not_count_as_design(self):
        """PW-16.3"""
        self.write("docs/design.md", "# Design\n\nNothing.\n")
        self.write("dev/INDEX.md", "# Work\n\nWorking on EX-01 and EX-02.\n")
        found = self.trace()[2]
        self.assertIn(("trace-no-design", "EX-01"), found)

    def test_plans_must_name_requirements_unless_finished_or_in_reviews(self):
        """PW-16.6"""
        self.write("dev/plans/a.md", "# A\n\n状态：执行中。\n")
        self.write("dev/plans/b.md", "# B\n\n状态：执行中。\n\n覆盖需求：无（维护：升级依赖）。\n")
        self.write("dev/plans/c.md", "# C\n\n状态：已完成。\n")
        self.write("dev/reviews/2026-10-28-x/README.md", "# Review\n\n状态：进行中。\n")
        self.write("dev/reviews/2026-10-28-x/plan-fix.md", "# Fix\n\n状态：草案。\n\n覆盖问题：\n")
        found = self.trace()[2]
        self.assertEqual({k for r, k in found if r == "trace-plan-scope"}, {None})
        scoped = [x["path"] for x in self.run_cli("check")[1]["findings"] if x["rule"] == "trace-plan-scope"]
        self.assertEqual(scoped, ["dev/plans/a.md"])

    def test_disabled_without_configuration(self):
        """PW-16.1"""
        del self.config["requirements"]
        self.save_config()
        self.write("docs/other.md", "# Other\n\nSee EX-09.\n")
        self.assertEqual(self.run_cli("check")[0], 0)


class VerificationTests(ProjectFixture):
    def page(self, header, path="docs/guide.md"):
        self.write(path, f"# Guide\n\n{header}\n\n## Section\n\nBody.\n\n核对：not-parsed-here\n")

    def test_verification_line_parsing(self):
        """PW-17.1"""
        info = wiki.verification_header("# T\n\n状态：采用。\n核对：agent:kiro，2026-10-28；human:clarence，2026-11-02。复核期限：2027-04-28。\n\n## A\n\n核对：human:x，2020-01-01\n")
        self.assertEqual([(k, n, d.isoformat()) for k, n, d in info["entries"]],
                         [("agent", "kiro", "2026-10-28"), ("human", "clarence", "2026-11-02")])
        self.assertEqual(info["review_by"].isoformat(), "2027-04-28")
        self.assertEqual(info["problems"], [])
        separate = wiki.verification_header("# T\n核对：agent:a，2026-01-01。\n复核期限：2026-06-01。\n")
        self.assertEqual(separate["review_by"].isoformat(), "2026-06-01")
        prose = wiki.verification_header("# Rules\n\n- 核对后写 `核对：agent:<名字>，YYYY-MM-DD。` 和 `复核期限：YYYY-MM-DD。`。\n说明：复核期限：YYYY-MM-DD 只是示例。\n")
        self.assertEqual((prose["line"], prose["review_by"], prose["problems"]), (None, None, []))

    def test_bad_format_and_review_before_check_fail(self):
        """PW-17.2 PW-18.1"""
        for header, rule in [("核对：kiro，2026-10-28。", "verify-format"),
                             ("核对：robot:kiro，2026-10-28。", "verify-format"),
                             ("核对：agent:kiro，2026-13-40。", "verify-format"),
                             ("核对：agent:kiro。", "verify-format"),
                             ("核对：agent:kiro，2026-10-28。复核期限：下个月。", "verify-format"),
                             ("核对：agent:kiro，2026-10-28。复核期限：2026-10-01。", "verify-review-before-check")]:
            self.page(header)
            code, report = self.run_cli("check")
            self.assertEqual(code, 1, header)
            self.assertIn(rule, self.rules(report), header)
        self.page("核对：agent:kiro，2026-10-28。复核期限：2027-04-28。")
        self.assertEqual(self.run_cli("check")[0], 0)

    def test_due_and_future_dates_are_remind_only(self):
        """PW-17.3"""
        self.page("核对：agent:kiro，2020-01-01；agent:kiro，2999-01-01。复核期限：2999-02-01。")
        self.write("docs/old.md", "# Old\n\n核对：agent:kiro，2020-01-01。复核期限：2020-06-01。\n")
        code, report = self.run_cli("check")
        self.assertEqual(code, 0, report)
        self.assertFalse({"knowledge-review-due", "verify-date-future"} & self.rules(report))
        findings = wiki.review_due_findings(wiki.Wiki(wiki.Snapshot(self.root)))
        self.assertEqual({(f.rule, f.path) for f in findings},
                         {("knowledge-review-due", "docs/old.md"), ("verify-date-future", "docs/guide.md")})

    def test_required_review_by_and_human_paths_warn(self):
        """PW-17.4 PW-18.3"""
        self.config["verification"] = {"review_by_required": ["docs/guides/*"], "human_required": ["docs/guides/*"]}
        self.save_config()
        self.page("核对：agent:kiro，2026-10-28。", path="docs/guides/run.md")
        code, report = self.run_cli("check")
        self.assertEqual(code, 0, report)
        self.assertTrue({"review-by-missing", "verify-no-human"} <= self.rules(report))
        self.page("核对：agent:kiro，2026-10-28；human:clarence，2026-10-28。复核期限：2027-01-01。", path="docs/guides/run.md")
        self.assertFalse({"review-by-missing", "verify-no-human"} & self.rules(self.run_cli("check")[1]))
        self.config["verification"] = {"unknown": []}
        self.save_config()
        self.assertEqual(self.run_cli("check")[0], 2)

    def test_index_reports_trust_level(self):
        """PW-18.2"""
        self.page("核对：agent:kiro，2026-10-28。")
        self.write("docs/other.md", "# Other\n\n核对：agent:kiro，2026-10-28；human:clarence，2026-10-29。\n")
        data = wiki.index_data(wiki.Wiki(wiki.Snapshot(self.root)))
        trust = {p["path"]: p.get("trust") for p in data["pages"]}
        self.assertEqual(trust["docs/guide.md"], "agent-checked")
        self.assertEqual(trust["docs/other.md"], "human-checked")
        self.assertIsNone(trust["docs/INDEX.md"])

    def review(self, checker, human_required=False):
        if human_required:
            self.config["verification"] = {"human_required": ["dev/reviews/*"]}
            self.save_config()
        self.write("dev/reviews/2026-10-28-x/README.md", "# R\n\n状态：进行中。\n")
        self.write("dev/reviews/2026-10-28-x/r01-a.md",
                   "# r01\n\n## r01-1 T\n\n状态：不成立。\n\n**观察**（作者：agent:a，2026-10-28）\n\nx\n\n**核对**\n\n"
                   f"| 轮次 | 核对人 | 判定 | 依据 |\n|---|---|---|---|\n| 1 | {checker} | 不成立 | e |\n")
        return self.run_cli("check")

    def test_review_checker_prefix_must_be_human_or_agent(self):
        """PW-18.4"""
        code, report = self.review("robot:b")
        self.assertEqual(code, 1)
        self.assertIn("review-actor-format", self.rules(report))
        self.assertEqual(self.review("agent:b")[0], 0)
        self.assertEqual(self.review("审查者B")[0], 0, "unprefixed names stay allowed")

    def test_review_requiring_human_check_warns_without_one(self):
        """PW-18.3"""
        code, report = self.review("agent:b", human_required=True)
        self.assertEqual(code, 0, report)
        self.assertIn("review-no-human-check", self.rules(report))
        self.assertNotIn("review-no-human-check", self.rules(self.review("human:clarence", human_required=True)[1]))

    def export(self, out=None):
        out = out or Path(self.temp.name).parent / (Path(self.temp.name).name + "-okf")
        self.addCleanup(lambda: shutil.rmtree(out, ignore_errors=True))
        result = subprocess.run([sys.executable, str(SCRIPT), "export-okf", "--root", str(self.root), "--out", str(out), "--json"],
                                capture_output=True, text=True)
        return result.returncode, json.loads(result.stdout), out

    def test_export_writes_frontmatter_and_skips_process_and_archive(self):
        """PW-19.1 PW-19.2"""
        self.write("docs/decisions/a.md", "# Old decision\n\n状态：被替代。\n\nThe first paragraph.\n")
        self.write("docs/guide.md", "# Guide\n\n核对：human:clarence，2026-10-28。复核期限：2027-01-31。\n\nHow to run it.\n")
        self.write("archive/docs/gone.md", "# Gone\n")
        code, report, out = self.export()
        self.assertEqual(code, 0, report)
        self.assertFalse((out / "dev").exists())
        self.assertFalse((out / "archive").exists())
        decision = (out / "docs/decisions/a.md").read_text(encoding="utf-8")
        self.assertTrue(decision.startswith('---\ntype: "Decision"\ntitle: "Old decision"\n'))
        self.assertIn('status: "deprecated"', decision)
        self.assertIn('description: "The first paragraph."', decision)
        self.assertTrue(decision.endswith("# Old decision\n\n状态：被替代。\n\nThe first paragraph.\n"))
        guide = (out / "docs/guide.md").read_text(encoding="utf-8")
        self.assertIn('verified:\n  - by: "human:clarence"\n    at: "2026-10-28T00:00:00Z"', guide)
        self.assertIn('stale_after: "2027-01-31T00:00:00Z"', guide)
        self.assertNotIn("status:", guide)
        self.assertEqual((self.root / "docs/guide.md").read_text(encoding="utf-8")[:7], "# Guide", "source is unchanged")

    def test_export_refuses_unsafe_targets(self):
        """PW-19.3"""
        code, report, _ = self.export(self.root / "okf")
        self.assertEqual(code, 2)
        self.assertFalse((self.root / "okf").exists())
        busy = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: shutil.rmtree(busy, ignore_errors=True))
        (busy / "keep.txt").write_text("x")
        code, report, _ = self.export(busy)
        self.assertEqual(code, 2)
        self.assertEqual([p.name for p in busy.iterdir()], ["keep.txt"])

    def test_export_keeps_existing_frontmatter(self):
        """PW-19.4"""
        self.write("docs/fm.md", "---\ntype: Metric\n---\n# Metric\n")
        code, report, out = self.export()
        self.assertEqual(code, 0, report)
        self.assertEqual((out / "docs/fm.md").read_text(encoding="utf-8"), "---\ntype: Metric\n---\n# Metric\n")
        self.assertIn("okf-existing-frontmatter", self.rules(report))


class StatusAndBaselineTests(ProjectFixture):
    def test_status_line_parsing(self):
        """PW-12.1"""
        self.assertEqual(wiki.status_value("# Title\n\n状态：被替代。范围：x。\n"), "被替代")
        self.assertEqual(wiki.status_value("# Title\nStatus: Superseded. Scope: x\n"), "Superseded")
        self.assertIsNone(wiki.status_value("# Title\n\nSome text. 状态：采用。\n"))
        self.assertIsNone(wiki.status_value("```\n# Title\n状态：采用\n```\n"))

    def write_decisions(self, old_status="被替代"):
        self.write("docs/decisions/old.md", f"# Old decision\n\n状态：{old_status}。由 [new](new.md) 替代。\n")
        self.write("docs/decisions/new.md", "# New decision\n\n状态：采用。替代 [old](old.md)。\n")

    def test_entry_linking_replaced_document_fails_and_other_pages_warn(self):
        """PW-12.2"""
        self.write_decisions()
        self.write("docs/INDEX.md", "# Current\n\n[Work](../dev/INDEX.md)\n[Rule](decisions/old.md)\n")
        self.write("docs/design.md", "# Design\n\nWhy: [old](decisions/old.md).\n")
        code, report = self.run_cli("check")
        self.assertEqual(code, 1, report)
        hits = {(x["path"], x["severity"]) for x in report["findings"] if x["rule"] == "links-replaced-document"}
        self.assertEqual(hits, {("docs/INDEX.md", "error"), ("docs/design.md", "warning")})

    def test_decisions_may_reference_what_they_replace_and_archive_links_are_history(self):
        """PW-12.3"""
        self.write_decisions()
        self.write("archive/docs/decisions/older.md", "# Older\n\n状态：被替代。\n")
        self.write("docs/INDEX.md", "# Current\n\n[Work](../dev/INDEX.md)\n[History](../archive/docs/decisions/older.md)\n")
        code, report = self.run_cli("check")
        self.assertEqual(code, 0, report)
        self.assertNotIn("links-replaced-document", self.rules(report))

    def test_unknown_or_missing_status_warns_and_configured_value_is_accepted(self):
        """PW-12.4"""
        self.write("docs/decisions/a.md", "# A\n\n状态：评审中。\n")
        self.write("docs/decisions/b.md", "# B\n\nNo status.\n")
        code, report = self.run_cli("check")
        self.assertEqual(code, 0, report)
        self.assertTrue({"status-unknown", "status-missing"} <= self.rules(report))
        self.config["status_values"] = {"评审中": "draft"}
        self.save_config()
        self.assertNotIn("status-unknown", self.rules(self.run_cli("check")[1]))
        self.config["status_values"] = {"评审中": "nonsense"}
        self.save_config()
        self.assertEqual(self.run_cli("check")[0], 2)

    def test_baseline_accepts_known_problems_but_not_new_ones(self):
        """PW-13.1"""
        self.config["baseline"] = "docs/wiki-baseline.json"
        self.save_config()
        self.write("docs/old.md", "# Old\n\n[Gone](gone.md)\n")
        result = subprocess.run([sys.executable, str(SCRIPT), "baseline", "--root", str(self.root)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.write("docs/wiki-baseline.json", result.stdout)
        code, report = self.run_cli("check")
        self.assertEqual(code, 0, report)
        self.assertEqual(report["baseline_accepted"], 1)
        self.write("docs/old.md", "# Old\n\nIntro moved the link down.\n\n[Gone](gone.md)\n")
        self.assertEqual(self.run_cli("check")[0], 0, "line moves must not create a new fingerprint")
        self.write("docs/other.md", "# Other\n\n[Missing](missing.md)\n")
        code, report = self.run_cli("check")
        self.assertEqual(code, 1)
        self.assertEqual([x["path"] for x in report["findings"] if x["rule"] == "broken-link"], ["docs/other.md"])

    def test_fixed_baseline_entries_ask_to_shrink(self):
        """PW-13.2"""
        self.config["baseline"] = "docs/wiki-baseline.json"
        self.save_config()
        self.write("docs/wiki-baseline.json", json.dumps({"version": 1, "findings": ["broken-link|docs/old.md|gone.md"]}))
        code, report = self.run_cli("check")
        self.assertEqual(code, 0, report)
        self.assertIn("baseline-stale", self.rules(report))

    def test_staged_baseline_growth_is_flagged_for_the_user(self):
        """PW-13.3"""
        if not shutil.which("git"):
            self.skipTest("git required")
        import os
        self.config["baseline"] = "docs/wiki-baseline.json"
        self.save_config()
        self.write("docs/wiki-baseline.json", json.dumps({"version": 1, "findings": []}))
        self.git("init", "-q")
        self.git("add", "-A")
        env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@x.invalid", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@x.invalid"}
        subprocess.run(["git", "-C", str(self.root), "-c", "commit.gpgsign=false", "commit", "-q", "--no-verify", "-m", "base"], check=True, env=env)
        self.write("docs/new.md", "# New\n\n[Missing](missing.md)\n")
        self.write("docs/wiki-baseline.json", json.dumps({"version": 1, "findings": ["broken-link|docs/new.md|missing.md"]}))
        self.git("add", "-A")
        code, report = self.run_cli("check", "--staged")
        self.assertEqual(code, 0, report)
        grown = [x for x in report["findings"] if x["rule"] == "baseline-grown"]
        self.assertEqual(len(grown), 1)
        self.assertTrue(grown[0]["message"].startswith("[user]"))


class AutomationTests(ProjectFixture):
    PLAN = "# Done work\n\n状态：已完成。\n\n[需求](../../docs/INDEX.md#current)、[入口](../INDEX.md)\n"
    REQ = "# Req\n\n证据：[记录](../dev/plans/done.md#done-work)。示例 `[x](../dev/plans/done.md)` 不改。\r\n[ref]: ../dev/plans/done.md\n\nSee [ref].\n"

    def tree(self):
        return {p.relative_to(self.root).as_posix(): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}

    def preview(self, path):
        code, report = self.run_cli("archive", path)
        return code, report, report.get("plan_sha256")

    def test_archive_apply_moves_rewrites_only_listed_links_and_rechecks(self):
        """PW-20.1 PW-20.3 PW-20.5"""
        self.write("dev/plans/done.md", self.PLAN)
        self.write("docs/req.md", self.REQ)
        self.write("docs/INDEX.md", "# Current\n\n[Work](../dev/INDEX.md)\n[Req](req.md)\n")
        code, preview, plan = self.preview("dev/plans/done.md")
        self.assertEqual(code, 0, preview)
        self.assertEqual({x["direction"] for x in preview["affected_links"]}, {"incoming", "outgoing"})
        code, report = self.run_cli("archive", "dev/plans/done.md", "--apply", "--expect", plan)
        self.assertEqual(code, 0, report)
        self.assertFalse((self.root / "dev/plans/done.md").exists())
        self.assertEqual((self.root / "archive/dev/plans/done.md").read_text(),
                         self.PLAN.replace("../../docs/", "../../../docs/").replace("(../INDEX.md)", "(../../../dev/INDEX.md)"),
                         "two different links on one line are both rewritten")
        expected = self.REQ.replace("(../dev/plans/done.md#", "(../archive/dev/plans/done.md#").replace("]: ../dev/", "]: ../archive/dev/")
        self.assertEqual((self.root / "docs/req.md").read_bytes(), expected.encode())
        self.assertIn("`[x](../dev/plans/done.md)`", expected)
        self.assertEqual(report["after_check"], "passed")
        self.assertEqual(len(report["writes"]), 3)

    def test_copied_project_template_checks_and_verifies(self):
        """PW-10.2"""
        target = self.root / "copied"
        shutil.copytree(SCRIPT.parents[2] / "templates" / "project", target)
        shutil.copytree(SCRIPT.parent, target / "scripts" / "wiki", ignore=shutil.ignore_patterns("__pycache__"))
        for command in ("check", "verify"):
            result = subprocess.run([sys.executable, str(target / "scripts/wiki/wiki.py"), command, "--root", str(target)],
                                    capture_output=True, text=True, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
            self.assertEqual(result.returncode, 0, command + ": " + result.stdout + result.stderr)

    def test_archive_apply_refuses_and_writes_nothing(self):
        """PW-20.2"""
        self.write("dev/plans/done.md", self.PLAN)
        self.write("docs/req.md", self.REQ)
        _, _, plan = self.preview("dev/plans/done.md")
        before = self.tree()
        code, report = self.run_cli("archive", "dev/plans/done.md", "--apply", "--expect", "0" * 64)
        self.assertEqual((code, self.tree()), (1, before))
        self.assertIn("archive-plan-changed", self.rules(report))
        self.write("docs/req.md", self.REQ + "\n[Again](../dev/plans/done.md)\n")
        before = self.tree()
        code, report = self.run_cli("archive", "dev/plans/done.md", "--apply", "--expect", plan)
        self.assertEqual((code, self.tree()), (1, before), "a new incoming link changes the plan")
        self.write("docs/req.md", "# Req\n\n[Escaped](../dev/plans/do%6Ee.md)\n")
        code, preview, plan = self.preview("dev/plans/done.md")
        self.assertIn("archive-rewrite-manual", self.rules(preview))
        before = self.tree()
        code, report = self.run_cli("archive", "dev/plans/done.md", "--apply", "--expect", plan)
        self.assertEqual((code, self.tree()), (1, before))
        self.assertIn("archive-not-applied", self.rules(report))
        self.write("docs/req.md", "# Req\n")
        self.write("archive/dev/plans/done.md", "# Older\n")
        code, preview, plan = self.preview("dev/plans/done.md")
        before = self.tree()
        code, report = self.run_cli("archive", "dev/plans/done.md", "--apply", "--expect", plan)
        self.assertEqual((code, self.tree()), (1, before))
        self.assertIn("archive-collision", self.rules(report))
        self.assertEqual(self.run_cli("archive", "dev/plans/done.md", "--apply")[0], 2)

    def test_archive_apply_rolls_back_when_commit_fails(self):
        """PW-20.6"""
        self.write("dev/plans/done.md", self.PLAN)
        self.write("docs/req.md", self.REQ)
        _, _, plan = self.preview("dev/plans/done.md")
        before = self.tree()
        captured = wiki.Wiki(wiki.Snapshot(self.root), "docs/wiki.json")
        original_replace = wiki.os.replace
        failed = False

        def fail_once(source, target):
            nonlocal failed
            if not failed and Path(target) == self.root / "docs/req.md":
                failed = True
                raise OSError("simulated commit failure")
            return original_replace(source, target)

        with mock.patch.object(wiki.os, "replace", side_effect=fail_once):
            report = wiki.archive_apply(captured, "dev/plans/done.md", plan, None)
        self.assertTrue(failed)
        self.assertEqual(report["result"], "failed")
        self.assertIn("archive-apply-failed", self.rules(report))
        after = self.tree()
        self.assertEqual(set(after), set(before), (set(before) - set(after), set(after) - set(before)))
        self.assertEqual(after, before)

    def test_directory_plan_covers_every_moved_file(self):
        """PW-20.7"""
        self.config["exclude"] = ["tmp/**", "dev/reviews/r/raw/**"]
        self.save_config()
        self.write("dev/reviews/r/README.md", "# Review\n\n状态：已完成。\n\n![Shot](shot.png)\n")
        (self.root / "dev/reviews/r/shot.png").write_bytes(b"\x89PNG one")
        self.write("dev/reviews/r/raw/log.txt", "excluded but still moved\n")
        (self.root / "dev/reviews/r/empty").mkdir()
        code, preview, plan = self.preview("dev/reviews/r")
        self.assertEqual(code, 0, preview)
        self.assertEqual(preview["other_files_moved"], ["dev/reviews/r/raw/log.txt", "dev/reviews/r/shot.png"])
        for change in (lambda: (self.root / "dev/reviews/r/shot.png").write_bytes(b"\x89PNG two"),
                       lambda: self.write("dev/reviews/r/raw/log.txt", "edited\n"),
                       lambda: self.write("dev/reviews/r/late.txt", "added after preview\n"),
                       lambda: (self.root / "dev/reviews/r/empty").rmdir()):
            _, _, plan = self.preview("dev/reviews/r")
            change()
            before = self.tree()
            code, report = self.run_cli("archive", "dev/reviews/r", "--apply", "--expect", plan)
            self.assertEqual((code, self.tree()), (1, before), report)
            self.assertIn("archive-plan-changed", self.rules(report))
        _, _, plan = self.preview("dev/reviews/r")
        code, report = self.run_cli("archive", "dev/reviews/r", "--apply", "--expect", plan)
        self.assertEqual(code, 0, report)
        self.assertEqual((self.root / "archive/dev/reviews/r/shot.png").read_bytes(), b"\x89PNG two")
        self.assertTrue((self.root / "archive/dev/reviews/r/late.txt").is_file())

    def test_directory_plan_rejects_a_change_between_planning_and_moving(self):
        """PW-20.7"""
        self.write("dev/reviews/r/README.md", "# Review\n\n状态：已完成。\n")
        (self.root / "dev/reviews/r/shot.png").write_bytes(b"one")
        _, _, plan = self.preview("dev/reviews/r")
        captured = wiki.Wiki(wiki.Snapshot(self.root), "docs/wiki.json")
        original = wiki.archive_plan

        def plan_then_edit(*args):
            result = original(*args)
            (self.root / "dev/reviews/r/shot.png").write_bytes(b"two")
            return result

        with mock.patch.object(wiki, "archive_plan", side_effect=plan_then_edit):
            report = wiki.archive_apply(captured, "dev/reviews/r", plan, None)
        self.assertIn("archive-plan-changed", self.rules(report))
        self.assertTrue((self.root / "dev/reviews/r/README.md").is_file())
        self.assertFalse((self.root / "archive/dev/reviews").exists())

    def test_archive_preview_reports_blocked_destinations(self):
        """PW-06.5"""
        self.write("dev/plans/done.md", self.PLAN)
        (self.root / "archive/dev/plans/done.md").mkdir(parents=True)
        code, report = self.run_cli("archive", "dev/plans/done.md")
        self.assertEqual(code, 1, "an empty directory at the destination is a collision")
        self.assertIn("archive-collision", self.rules(report))
        shutil.rmtree(self.root / "archive")
        self.write("archive/dev", "a file where a directory is needed\n")
        code, report = self.run_cli("archive", "dev/plans/done.md")
        self.assertEqual(code, 1)
        self.assertIn("archive-collision", self.rules(report))

    def test_archive_summary_appends_to_first_table_or_refuses(self):
        """PW-20.4"""
        self.write("dev/plans/done.md", self.PLAN)
        _, _, plan = self.preview("dev/plans/done.md")
        before = self.tree()
        code, report = self.run_cli("archive", "dev/plans/done.md", "--apply", "--expect", plan, "--summary", "完成记录")
        self.assertEqual((code, self.tree()), (1, before))
        self.assertIn("archive-index-unavailable", self.rules(report))
        self.write("archive/INDEX.md", "# History\n\n| 记录 | 范围 |\n|---|---|\n| [Old](docs/old.md) | 旧 |\n\nText after.\n\n| Other | table |\n|---|---|\n")
        self.write("archive/docs/old.md", "# Old\n")
        _, _, plan = self.preview("dev/plans/done.md")
        code, report = self.run_cli("archive", "dev/plans/done.md", "--apply", "--expect", plan, "--summary", "完成 | 验证记录")
        self.assertEqual(code, 0, report)
        self.assertEqual((self.root / "archive/INDEX.md").read_text(),
                         "# History\n\n| 记录 | 范围 |\n|---|---|\n| [Old](docs/old.md) | 旧 |\n"
                         "| [Done work](dev/plans/done.md) | 完成 \\| 验证记录 |\n\nText after.\n\n| Other | table |\n|---|---|\n")

    def test_archive_directory_warns_for_entry_links_and_reports_failed_recheck(self):
        """PW-20.1 PW-20.5"""
        self.write("dev/reviews/r/README.md", "# Review\n\n状态：已完成。\n\n[Route](route.md)\n")
        self.write("dev/reviews/r/route.md", "# Route\n\n[Back](README.md)\n")
        self.write("dev/INDEX.md", "# Work\n\n[Review](reviews/r/README.md)\n")
        self.write("docs/broken.md", "# Broken\n\n[Missing](missing.md)\n")
        code, preview, plan = self.preview("dev/reviews/r")
        self.assertIn("archive-entry-link", self.rules(preview))
        code, report = self.run_cli("archive", "dev/reviews/r", "--apply", "--expect", plan)
        self.assertEqual(code, 1, "the unrelated broken link fails the check that runs after the move")
        self.assertEqual(report["after_check"], "failed")
        self.assertTrue((self.root / "archive/dev/reviews/r/route.md").is_file())
        self.assertFalse((self.root / "dev/reviews/r").exists())
        self.assertEqual((self.root / "archive/dev/reviews/r/route.md").read_text(), "# Route\n\n[Back](README.md)\n")
        self.assertEqual((self.root / "dev/INDEX.md").read_text(), "# Work\n\n[Review](../archive/dev/reviews/r/README.md)\n")

    def verify_config(self, **extra):
        python = sys.executable
        self.config["verify"] = {
            "commands": [
                {"name": "ok", "run": [python, "-c", "print('Ran 3 tests'); print(); print('OK')"]},
                {"name": "fail", "run": [python, "-c", "import sys; print('boom'); sys.exit(3)"], "cwd": "docs"},
                {"name": "slow", "run": [python, "-c", "import time; time.sleep(5)"], "timeout": 1},
                {"name": "argv", "run": [python, "-c", "import sys; print(sys.argv[1]); print('later')", "$HOME|x"],
                 "summary_lines": 1, "summary_from": "start"},
            ],
            "files": ["docs/INDEX.md"], **extra}
        self.save_config()

    def test_verify_records_commands_results_and_inputs(self):
        """PW-21.1 PW-21.2 PW-21.3 PW-21.4"""
        self.verify_config()
        code, report = self.run_cli("verify")
        self.assertEqual(code, 1)
        text = report["markdown"]
        prefix = wiki.digest((self.root / "docs/INDEX.md").read_bytes())[:12]
        config_prefix = wiki.digest((self.root / "docs/wiki.json").read_bytes())[:12]
        for expected in ["不是 Git 仓库", f"`{config_prefix}`", "`ok`：", "通过（退出码 0", "输出最后几行：`Ran 3 tests`；`OK`。",
                         "在 `docs` 下运行，失败（退出码 3", "1 秒后超时，已终止", "输出第一行：`$HOME|x`。", f"`docs/INDEX.md` `{prefix}`"]:
            self.assertIn(expected, text)
        self.assertEqual({x["key"] for x in report["findings"] if x["rule"] == "verify-command-failed"}, {"fail", "slow"})
        code, report = self.run_cli("verify", "ok")
        self.assertEqual(code, 0, report)
        self.assertIn("未运行：`fail`、`slow`、`argv`。", report["markdown"])
        if shutil.which("git"):
            self.git("init", "-q")
            self.git("add", "-A")
            self.git("-c", "user.name=t", "-c", "user.email=t@x.invalid", "-c", "commit.gpgsign=false", "commit", "-qm", "base")
            self.write("docs/new.md", "# New\n")
            head = self.git("rev-parse", "--short=12", "HEAD")
            report = self.run_cli("verify", "ok")[1]
            self.assertIn(f"HEAD `{head}`，相对 HEAD 有 1 个文件未提交", report["markdown"])

    def test_verify_invalid_configuration_runs_nothing(self):
        """PW-21.4"""
        python = sys.executable
        for bad in ({"name": "bad", "run": "echo hi"}, {"name": "bad", "run": [python, "-V"], "cwd": "../elsewhere"}):
            self.config["verify"] = {"commands": [{"name": "mark", "run": [python, "-c", "open('marker', 'w')"]}, bad]}
            self.save_config()
            code, report = self.run_cli("verify")
            self.assertEqual((code, report["result"]), (2, "incomplete"), bad)
            self.assertFalse((self.root / "marker").exists())

    def test_index_write_only_changes_file_when_needed(self):
        """PW-22.1"""
        self.config["generated_index"] = "docs/wiki-index.json"
        self.save_config()
        self.assertEqual(self.run_cli("index", "--check")[0], 1)
        code, report = self.run_cli("index", "--write")
        self.assertEqual((code, report["written"]), (0, True))
        target = self.root / "docs/wiki-index.json"
        stamp = target.stat().st_mtime_ns
        code, report = self.run_cli("index", "--write")
        self.assertEqual((code, report["written"], target.stat().st_mtime_ns), (0, False, stamp))
        result = subprocess.run([sys.executable, str(SCRIPT), "index", "--check", "--root", str(self.root)], capture_output=True)
        self.assertEqual(result.returncode, 0)

    def test_reconcile_reports_both_directions_and_empty_sides(self):
        """PW-23.1 PW-23.2"""
        self.write("docs/rules.md", "# Rules\n\n| `alpha-rule` | a |\n| `gone-rule` | g |\n")
        self.write("src/tool.py", 'Finding("alpha-rule")\nFinding(\n    "beta-rule")\n')
        entry = {"name": "rules", "docs": ["docs/rules.md"], "doc_pattern": r"^\| `([a-z-]+)`", "code": ["src/*.py"], "code_pattern": r'Finding\(\s*"([a-z-]+)"'}
        self.config["reconcile"] = [entry]
        self.save_config()
        code, report = self.run_cli("check")
        self.assertEqual(code, 1)
        found = {(x["rule"], x["key"]) for x in report["findings"] if x["rule"].startswith("reconcile")}
        self.assertEqual(found, {("reconcile-missing-in-doc", "rules:beta-rule"), ("reconcile-missing-in-code", "rules:gone-rule")})
        self.config["reconcile"] = [{**entry, "ignore": ["beta-rule", "gone-rule"]}]
        self.save_config()
        self.assertEqual(self.run_cli("check")[0], 0)
        self.config["reconcile"] = [{**entry, "code": ["lib/*.py"]}]
        self.save_config()
        self.assertIn("reconcile-empty", self.rules(self.run_cli("check")[1]))
        self.config["reconcile"] = [{**entry, "doc_pattern": "(unclosed"}]
        self.save_config()
        self.assertEqual(self.run_cli("check")[0], 2)

    def test_orphan_pages_and_assets_are_warned(self):
        """PW-24.1 PW-24.2 PW-24.3"""
        self.write("docs/lonely.md", "# Lonely\n\n![Shot](shot.png)\n")
        self.write("docs/shot.png", "png")
        self.write("docs/unused.html", "<p>prototype</p>")
        self.write("docs/wire/a.canvas.tsx", "export {}")
        self.write("docs/linked.md", "# Linked\n\n[Wireframes](wire/)\n")
        self.write("docs/.keep", "")
        self.write("archive/docs/old.md", "# Old\n\n[Unused](../../docs/unused.html)\n")
        self.write("dev/plans/note.md", "# Note\n\n状态：执行中。\n")
        self.write("docs/INDEX.md", "# Current\n\n[Work](../dev/INDEX.md)\n[Linked](linked.md)\n")
        code, report = self.run_cli("check")
        self.assertEqual(code, 0, report)
        found = {(x["rule"], x["path"]) for x in report["findings"] if x["rule"].startswith("orphan")}
        self.assertEqual(found, {("orphan-page", "docs/lonely.md"), ("orphan-asset", "docs/unused.html")},
                         "links from history do not count; a page's own assets and directory links do; config, dotfiles and dev/ are skipped")
        self.config["orphan_ignore"] = ["docs/lonely.md", "docs/*.html"]
        self.save_config()
        self.assertFalse(any(x["rule"].startswith("orphan") for x in self.run_cli("check")[1]["findings"]))

    def test_plan_owner_is_checked_and_listed(self):
        """PW-25.1 PW-25.2"""
        if not shutil.which("git"):
            self.skipTest("git required")
        self.write("dev/plans/a.md", "# A\n\n状态：执行中。范围：x。负责：agent:kiro。\n")
        self.write("dev/plans/b.md", "# B\n\n状态：阻塞。\n")
        self.write("dev/plans/c.md", "# C\n\n状态：已完成。负责：kiro。\n")
        self.config["remind"] = {"watch": [{"name": "src", "code": ["src/*"], "docs": ["docs/*"]}], "threshold": {"commits": 5}}
        self.save_config()
        code, report = self.run_cli("check")
        self.assertEqual(code, 1)
        self.assertEqual([(x["rule"], x["path"]) for x in report["findings"] if x["rule"] == "owner-format"], [("owner-format", "dev/plans/c.md")])
        self.write("dev/plans/c.md", "# C\n\n状态：已完成。Owner: human:clarence.\n")
        self.assertNotIn("owner-format", self.rules(self.run_cli("check")[1]))
        self.git("init", "-q")
        self.git("add", "-A")
        self.git("-c", "user.name=t", "-c", "user.email=t@x.invalid", "-c", "commit.gpgsign=false", "commit", "-qm", "base")
        report = self.run_cli("remind")[1]
        self.assertEqual(report["active_plans"], [{"path": "dev/plans/a.md", "status": "执行中", "owner": "agent:kiro"},
                                                  {"path": "dev/plans/b.md", "status": "阻塞", "owner": None}])

    def test_copied_files_only_link_to_what_is_copied(self):
        """PW-10.3"""
        repository = Path(__file__).resolve().parents[1]

        def local_targets(path):
            relative = path.relative_to(repository).as_posix()
            for link in wiki.markdown_links(path.read_text(encoding="utf-8"), relative):
                target, _, problem = wiki.resolve_link(relative, link.target)
                if target is not None or problem:
                    yield target or link.target

        tool = repository / "scripts" / "wiki"
        for path in sorted(tool.glob("*.md")):
            for target in local_targets(path):
                self.assertTrue(target.startswith("scripts/wiki/") and (repository / target).is_file(),
                                f"{path.name} links to {target}, which is not copied with the tool")
        groups = {"templates/review": repository / "templates" / "review", "templates/module": repository / "templates" / "module"}
        for prefix, directory in groups.items():
            for path in sorted(directory.rglob("*.md")):
                for target in local_targets(path):
                    self.assertTrue(target.startswith(prefix + "/"), f"{path} links outside its template group: {target}")
        for name in ("plan.md", "decision.md", "inbox-item.md", "requirements.md"):
            self.assertEqual(list(local_targets(repository / "templates" / name)), [], f"templates/{name} is copied alone")
        agents = (repository / "templates" / "project" / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("scripts/wiki/formats.md", agents)

    def test_formats_page_lists_exactly_the_keywords_the_tool_reads(self):
        """PW-10.4"""
        import re
        text = (SCRIPT.parent / "formats.md").read_text(encoding="utf-8")
        documented = set()
        in_table = False
        for line in text.splitlines():
            if line.startswith("| 中文 | English |"):
                in_table = True
                continue
            if not line.startswith("|"):
                in_table = False
            elif in_table:
                cells = [c.strip() for c in line.strip("|").split("|")]
                pair = tuple(re.fullmatch(r"`([^`]+)`", c).group(1) for c in cells[:2] if re.fullmatch(r"`([^`]+)`", c))
                if len(pair) == 2:
                    documented.add(pair)

        def pairs(values):
            by_class = {}
            for word, kind in values.items():
                by_class.setdefault(kind, []).append(word)
            for kind, words in by_class.items():
                self.assertEqual(len(words), 2, f"{kind} needs exactly one Chinese and one English word: {words}")
            return {tuple(sorted(words, key=lambda w: w.isascii())) for words in by_class.values()}

        code = set(wiki.KEYWORDS.values()) | pairs(wiki.DEFAULT_STATUS_VALUES) | pairs(wiki.VERDICTS) | pairs(wiki.REQUIREMENT_STATUSES)
        for zh, en in code:
            self.assertFalse(zh.isascii(), zh)
            self.assertTrue(en.isascii(), en)
        self.assertEqual(documented, code)

    def test_template_and_demo_budget_process_directories(self):
        """PW-15.3"""
        repository = Path(__file__).resolve().parents[1]
        for config in ("templates/project/docs/wiki.json", "demo/docs/wiki.json"):
            budgets = json.loads((repository / config).read_text(encoding="utf-8")).get("dir_budgets", {})
            self.assertTrue({"dev/plans", "dev/inbox/*", "dev/reviews/*"} <= set(budgets), config)

    def test_this_repository_documents_every_rule_name(self):
        """PW-23.3"""
        repository = Path(__file__).resolve().parents[1]
        project = wiki.Wiki(wiki.Snapshot(repository))
        self.assertTrue(project.reconcile, "docs/wiki.json registers the rule-name reconcile")
        self.assertEqual([f.message for f in wiki.reconcile_check(project)], [])


if __name__ == "__main__":
    unittest.main()
