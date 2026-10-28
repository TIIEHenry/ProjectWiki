"""Behavior tests use temporary projects; no checked-out project is modified."""

from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
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
        code, report = self.run_cli("check")
        self.assertEqual(code, 0, report)
        self.assertEqual(report["documents_checked"], 4)

    def test_no_root_fallback_and_exact_case(self):
        self.write("docs/topic.md", "# Topic\n[Wrong relative](docs/INDEX.md)\n[Wrong case](index.md)\n")
        code, report = self.run_cli("check")
        self.assertEqual(code, 1)
        self.assertEqual(sum(x["rule"] == "broken-link" for x in report["findings"]), 2)

    def test_reference_links_images_and_code_blocks(self):
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
        self.write("docs/topic.md", "# 运行方式\n## Same\n## Same\n## Same-1\n<a id=\"manual\"></a>\n")
        self.write("README.md", "# Example\n[A](docs/topic.md#运行方式)\n[B](docs/topic.md#same-1)\n[C](docs/topic.md#manual)\n[D](docs/topic.md#same-1-1)\n")
        code, report = self.run_cli("check")
        self.assertEqual(code, 0, report)
        self.write("README.md", "# Example\n[A](docs/topic.md#absent)\n")
        code, report = self.run_cli("check")
        self.assertEqual(code, 1)
        self.assertIn("broken-anchor", self.rules(report))

    def test_relative_root_directory_link(self):
        self.write("docs/topic.md", "# Topic\n[Project](../)\n[Remote](//example.com/help)\n")
        code, report = self.run_cli("check")
        self.assertEqual(code, 0, report)

    def test_standalone_agent_imports_are_case_sensitive(self):
        self.config["entrypoints"].append("CLAUDE.md")
        self.save_config()
        self.write("CLAUDE.md", "@AGENTS.MD\n")
        code, report = self.run_cli("check")
        self.assertEqual(code, 1)
        self.assertIn("broken-link", self.rules(report))
        self.write("CLAUDE.md", "@AGENTS.md\n")
        self.assertEqual(self.run_cli("check")[0], 0)

    def test_single_long_line_cannot_bypass_character_budget(self):
        self.write("AGENTS.md", "# Rules\n" + "长" * 1001)
        code, report = self.run_cli("check")
        self.assertEqual(code, 1)
        self.assertIn("page-budget", self.rules(report))

    def test_unregistered_nested_docs_are_reported_and_exclusions_explicit(self):
        self.write("client/docs/README.md", "# Client\n")
        self.write("tmp/notes/docs/README.md", "# Scratch\n")
        code, report = self.run_cli("check")
        self.assertEqual(code, 1)
        unregistered = [x["path"] for x in report["findings"] if x["rule"] == "unregistered-docs"]
        self.assertEqual(unregistered, ["client/docs"])

    def test_small_module_can_have_only_a_readme(self):
        self.write("small/README.md", "# Small module\n\nOne responsibility.\n")
        self.config["modules"] = [{"name": "small", "path": "small", "entry": "small/README.md"}]
        self.save_config()
        code, report = self.run_cli("check")
        self.assertEqual(code, 0, report)
        self.assertEqual(report["documents_checked"], 5)

    def test_legacy_archive_does_not_make_primary_target_ambiguous(self):
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
        self.write("archive/docs/new.md", "# Prior topic\n")
        code, report = self.run_cli("check-new", "docs/new.md")
        self.assertEqual(code, 0, report)
        self.assertIn("historical-path-match", self.rules(report))
        code, report = self.run_cli("check-new", "dev/new.md")
        self.assertEqual(code, 0)
        self.assertIsNone(report["history_match"])
        self.assertEqual(self.run_cli("check-new", "docs/INDEX.md")[0], 1)

    def test_history_match_requires_file_but_archive_collision_includes_directory(self):
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
        self.write("archive/docs/INDEX.md", (self.root / "docs/INDEX.md").read_text())
        code, report = self.run_cli("archive", "docs/INDEX.md")
        self.assertEqual(code, 1)
        self.assertIn("archive-collision", self.rules(report))

    def test_archive_reports_unresolved_outgoing_links(self):
        self.write("docs/plan.md", "# Plan\n[External project](../../other/docs.md)\n[Missing](missing.md)\n")
        code, report = self.run_cli("archive", "docs/plan.md")
        self.assertEqual(code, 0, report)
        self.assertEqual(self.rules(report), {"archive-unresolved-link", "archive-unresolved-target"})
        self.assertEqual(report["affected_links"], [])
        self.assertFalse(report["writes"])

    def test_index_is_deterministic_and_check_is_read_only(self):
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
        self.write("docs/wiki.json", "{bad}")
        code, report = self.run_cli("check")
        self.assertEqual(code, 2)
        self.assertEqual(report["result"], "incomplete")
        self.config["version"] = True
        self.save_config()
        self.assertEqual(self.run_cli("check")[0], 2)

    def test_doctor_does_not_claim_hooks_verified(self):
        self.write(".ignore", "/archive/\n")
        code, report = self.run_cli("doctor")
        self.assertEqual(code, 0)
        self.assertIn("unknown", report["hooks"])
        self.assertEqual(report["result"], "passed_with_warnings")

    def test_staged_rejects_worktree_only_repair(self):
        self.write("README.md", "# Example\n[Broken](missing.md)\n")
        self.initialize_index()
        self.write("README.md", "# Example\n[Fixed](docs/INDEX.md)\n")
        self.assertEqual(self.run_cli("check")[0], 0)
        code, report = self.run_cli("check", "--staged")
        self.assertEqual(code, 1)
        self.assertIn("broken-link", self.rules(report))
        self.assertTrue(report["snapshot"].startswith("git-index-sha256:"))

    def test_staged_does_not_use_untracked_target_or_unstaged_config(self):
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
        self.assertEqual(self.run_cli("check", "--staged")[0], 2)
        self.initialize_index()
        self.git("rm", "--cached", "docs/wiki.json")
        code, report = self.run_cli("check", "--staged")
        self.assertEqual(code, 2)
        self.assertEqual(report["result"], "incomplete")

    def test_staged_blob_reads_remain_frozen_after_index_changes(self):
        self.initialize_index()
        snap = wiki.Snapshot(self.root, staged=True)
        original = (self.root / "README.md").read_bytes()
        self.write("README.md", "# Changed\n")
        self.git("add", "README.md")
        self.assertEqual(snap.read("README.md"), original)

    def test_staged_initial_project_reports_matching_history(self):
        self.write("archive/docs/restored.md", "# Previous version\n")
        self.write("docs/restored.md", "# Restored current version\n")
        self.initialize_index()
        code, report = self.run_cli("check", "--staged")
        self.assertEqual(code, 0, report)
        self.assertEqual(report["head_baseline"], "unborn")
        matches = [x["path"] for x in report["findings"] if x["rule"] == "historical-path-match"]
        self.assertEqual(matches, ["docs/restored.md"])

    def test_staged_restore_compares_against_captured_head(self):
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
        self.write("notes/docs/decisions/count.md", "# Count decision\n\nStatus: adopted.\n")
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
        self.change_code(1)
        code, report = self.run_cli("remind", "--staged")
        self.assertEqual(code, 0, report)
        self.assertIn("docs-not-updated", self.rules(report))
        self.assertEqual(self.watch(report)["notes"]["commits"], 1)

    def test_staged_docs_update_resets_count_and_silences_reminder(self):
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
        for number in range(3):
            self.change_code(number + 1)
            self.commit(f"Change {number}")
        self.commit("Refactor only\n\nDocs-Reviewed: notes")
        self.assertEqual(self.watch(self.run_cli("remind")[1])["notes"]["commits"], 3)
        self.change_code(7)
        self.commit("Rename variable\n\nDocs-Reviewed: notes no behavior change")
        self.assertEqual(self.watch(self.run_cli("remind")[1])["notes"]["commits"], 0)

    def test_block_at_fails_only_for_more_unreviewed_code(self):
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
        for number in range(6):
            self.change_code(number + 1)
            self.commit(f"Change {number}")
        code, report = self.run_cli("remind")
        self.assertEqual(code, 0, report)
        overdue = [x for x in report["findings"] if x["rule"] == "docs-review-overdue"]
        self.assertEqual([x["severity"] for x in overdue], ["warning"])

    def test_decision_change_lists_unstaged_linking_documents_and_ask_user(self):
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
        code, report = self.run_cli("doctor")
        self.assertEqual(report["git_hooks"]["pre-commit"], "missing")
        self.assertIn("hook-not-installed", self.rules(report))


if __name__ == "__main__":
    unittest.main()
