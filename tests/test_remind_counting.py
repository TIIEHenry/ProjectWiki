
from __future__ import annotations

import os
import subprocess
import sys
import unittest
import threading
import time
from unittest import mock
from pathlib import Path

from test_wiki import ProjectFixture, wiki, SCRIPT


class RemindCountingTests(ProjectFixture):
    """PW-42: adoption commits and mechanical changes do not clear remind counts.

    Each test builds its own temporary Git history. The config file is committed in a
    separate, later commit so the test controls which commit counts as the adoption
    commit (B1: the first commit that adds docs/wiki.json).
    """

    GIT_ENV = {"GIT_AUTHOR_NAME": "Wiki Test", "GIT_AUTHOR_EMAIL": "wiki@example.invalid",
               "GIT_COMMITTER_NAME": "Wiki Test", "GIT_COMMITTER_EMAIL": "wiki@example.invalid"}

    def setUp(self):
        super().setUp()
        self.config["remind"] = {
            "watch": [{"name": "notes", "code": ["notes/src/*"], "docs": ["notes/docs/*", "notes/README.md"]}],
            "threshold": {"commits": 3, "lines": 1000},
            "block_at": {"commits": 30},
            "plan_stale_days": 14,
        }
        self.save_config()
        self.write("notes/README.md", "# Notes\n\n[Design](docs/design.md)\n")
        self.write("notes/docs/design.md", "# Design\n\nThe limit is sixty. See [count](decisions/count.md).\n")
        self.write("notes/docs/decisions/count.md", "# Count\n\n状态：当前有效。\n")
        self.write("notes/src/title.py", "LIMIT = 60\n")
        self.git("init", "-q")

    # -- helpers -----------------------------------------------------------

    def commit(self, message, date=None):
        env = {**os.environ, **self.GIT_ENV}
        if date:
            env["GIT_AUTHOR_DATE"] = env["GIT_COMMITTER_DATE"] = date
        subprocess.run(["git", "-C", str(self.root), "-c", "commit.gpgsign=false", "commit", "-q",
                        "--no-verify", "-m", message], check=True, capture_output=True, env=env)
        return self.git("rev-parse", "HEAD")

    def add(self, *paths):
        self.git("add", *paths)

    def change_code(self, number):
        self.write("notes/src/title.py", f"LIMIT = {60 + number}\n")
        self.add("notes/src/title.py")

    def watch(self, report):
        return {item["name"]: item for item in report["watch_status"]}

    def adopt(self, message="Adopt wiki"):
        """Commit the project with the config file; its SHA is the adoption commit.

        Everything present so far (the notes tree and the config) is committed in one
        commit, matching a real adoption: an existing project adds docs/wiki.json.
        """
        self.add(".")
        return self.commit(message)

    def message_file(self, text):
        path = self.root / "MSG"
        path.write_text(text, encoding="utf-8")
        return str(path)

    def test_context_order_and_mechanical_fields(self):
        """PW-42.6, PW-42.8, PW-42.11: classify ordered text in context."""
        compare = wiki.text_is_substantial
        for field in ("date", "created", "updated", "phase"):
            with self.subTest(field=field):
                self.assertTrue(compare(f"# Guide\n{field}: old\n", f"# Guide\n{field}: new\n", False))
                self.assertFalse(compare(f"---\n{field}: old\n---\n# Guide\n", f"---\n{field}: new\n---\n# Guide\n", True))
        self.assertFalse(compare("---\nstatus: old\n---\n", "---\nstatus: new\n---\n", True))
        for prefix in ("Status:", "状态："):
            self.assertFalse(compare(f"# Plan\n{prefix} active\n", f"# Plan\n{prefix} blocked\n", False))
            self.assertTrue(compare(f"# Plan\n{prefix} active\n", f"# Plan\n{prefix} blocked\n", True))
        self.assertTrue(compare("# Guide\nFirst\nSecond\n", "# Guide\nSecond\nFirst\n", False))
        self.assertFalse(compare("# Guide\n[Text](old)\n", "# Guide\n[Text](new)\n", False))
        self.assertTrue(compare("---\ndate: old\n", "---\ndate: new\n", False))

    def test_link_parser_and_frontmatter_context(self):
        """PW-42.5, PW-42.6: only supported targets and top-level fields are mechanical."""
        compare = wiki.text_is_substantial
        pairs = [
            (r"literal \[x](old)", r"literal \[x](new)", True),
            ("[x](https://example/a(v1)/read)", "[x](https://example/v2/read)", False),
            (r"[x](a\(b\))", r"[x](c\(d\))", False),
            ('[x](old "visible title")', '[x](new "visible title")', False),
            ('[x](old "first")', '[x](old "second")', True),
            ("---\ndescription: |\n  status: old\n---\n", "---\ndescription: |\n  status: new\n---\n", True),
            ("---\nupdated: |\n  old\n---\n", "---\nupdated: |\n  new\n---\n", False),
        ]
        for before, after, expected in pairs:
            with self.subTest(before=before, after=after):
                self.assertEqual(compare(before, after, False), expected)

    def test_merge_does_not_recount_branch_changes_to_same_file(self):
        """PW-42.16: combined branch edits count once; integration edits count too."""
        self.write("notes/src/title.py", "a\nb\nc\nd\ne\nf\ng\n")
        self.adopt()
        self.git("checkout", "-qb", "side")
        self.write("notes/src/title.py", "a\nb\nc\nd\ne\nf\nSIDE\n")
        self.add("notes/src/title.py")
        self.commit("Side edit")
        self.git("checkout", "-q", "master")
        self.write("notes/src/title.py", "MAIN\nb\nc\nd\ne\nf\ng\n")
        self.add("notes/src/title.py")
        self.commit("Main edit")
        self.git("merge", "--no-ff", "--no-commit", "side")
        self.commit("Merge branches")
        self.assertEqual(self.watch(self.run_cli("remind")[1])["notes"]["commits"], 2)
        self.git("checkout", "-qb", "other")
        self.write("other", "branch\n")
        self.add("other")
        self.commit("Other branch")
        self.git("checkout", "-q", "master")
        self.write("main-marker", "main\n")
        self.add("main-marker")
        self.commit("Main marker")
        self.git("merge", "--no-ff", "--no-commit", "other")
        self.write("notes/src/title.py", "INTEGRATION\nb\nc\nd\ne\nf\nSIDE\n")
        self.add("notes/src/title.py")
        staged = self.watch(self.run_cli("remind", "--staged")[1])["notes"]["commits"]
        self.commit("Integration edit")
        self.assertEqual(self.watch(self.run_cli("remind")[1])["notes"]["commits"], staged)

    def test_merge_mechanical_edit_keeps_full_document_context(self):
        """PW-42.16: branch prose and integration metadata do not create a review."""
        self.write("notes/docs/design.md", "---\nupdated: old\n---\n# Design\n\nbase\n\n[x](old)\n")
        self.adopt()
        self.git("checkout", "-qb", "side")
        self.write("notes/docs/design.md", "---\nupdated: old\n---\n# Design\n\nside prose\n\n[x](old)\n")
        self.add("notes/docs/design.md")
        self.commit("Side prose")
        self.git("checkout", "-q", "master")
        self.write("main-marker", "main\n")
        self.add("main-marker")
        self.commit("Main marker")
        self.git("merge", "--no-ff", "--no-commit", "side")
        self.write("notes/docs/design.md", "---\nupdated: new\n---\n# Design\n\nside prose\n\n[x](new)\n")
        self.add("notes/docs/design.md")
        commit = self.commit("Merge with metadata update")
        parents = self.git("show", "-s", "--format=%P", commit).split()
        _, objects = wiki.merge_integration_changes(self.root, commit, len(parents), {"notes/docs/design.md"})
        blobs = wiki.merge_blob_contents(self.root, objects, {"notes/docs/design.md"})
        self.assertFalse(wiki.merge_document_substantial([blobs.get(oid, b"") for oid in objects["notes/docs/design.md"][1]], False))

    def test_merge_binary_and_special_mode_count_without_lines(self):
        """PW-42.16: integration binary and symlink changes count without text lines."""
        self.write("notes/src/blob.bin", "original\0data")
        self.adopt()
        self.git("checkout", "-qb", "side")
        self.write("side-marker", "side\n")
        self.add("side-marker")
        self.commit("Side marker")
        self.git("checkout", "-q", "master")
        self.write("main-marker", "main\n")
        self.add("main-marker")
        self.commit("Main marker")
        self.git("merge", "--no-ff", "--no-commit", "side")
        (self.root / "notes/src/blob.bin").write_bytes(b"changed\0binary")
        (self.root / "notes/src/title.py").unlink()
        (self.root / "notes/src/title.py").symlink_to("blob.bin")
        self.add("notes/src")
        staged = self.watch(self.run_cli("remind", "--staged")[1])["notes"]
        self.commit("Integrate binary and symlink")
        history = self.watch(self.run_cli("remind")[1])["notes"]
        self.assertEqual((history["commits"], history["lines"]), (staged["commits"], staged["lines"]))

    def test_merge_duplicate_lines_do_not_create_integration_change(self):
        """PW-42.16: repeated lines inherited from both parents do not count again."""
        self.write("notes/docs/design.md", "A\nA\n")
        self.adopt()
        self.git("checkout", "-qb", "side")
        self.write("notes/docs/design.md", "A\nB\n")
        self.add("notes/docs/design.md")
        self.commit("Side")
        self.git("checkout", "-q", "master")
        self.write("notes/docs/design.md", "B\nA\n")
        self.add("notes/docs/design.md")
        self.commit("Main")
        subprocess.run(["git", "-C", str(self.root), "merge", "--no-ff", "--no-commit", "side"],
                       env={**os.environ, **self.GIT_ENV}, capture_output=True, check=False)
        self.write("notes/docs/design.md", "B\nB\n")
        self.add("notes/docs/design.md")
        commit = self.commit("Merge duplicate lines")
        changes, _ = wiki.merge_integration_changes(self.root, commit, 2, {"notes/docs/design.md"})
        self.assertEqual(changes, [])

    def test_merge_batches_watched_documents(self):
        """PW-42.14, PW-42.16: one patch and one blob batch for many merge documents."""
        for i in range(25):
            self.write(f"notes/docs/many-{i}.md", f"before {i}\n")
        self.adopt()
        self.git("checkout", "-qb", "side")
        self.write("side-marker", "side\n")
        self.add("side-marker")
        self.commit("Side marker")
        self.git("checkout", "-q", "master")
        self.write("main-marker", "main\n")
        self.add("main-marker")
        self.commit("Main marker")
        self.git("merge", "--no-ff", "--no-commit", "side")
        for i in range(25):
            self.write(f"notes/docs/many-{i}.md", f"after {i}\n")
        self.add("notes/docs")
        commit = self.commit("Merge document updates")
        paths = {f"notes/docs/many-{i}.md" for i in range(25)}
        original = wiki.subprocess.run
        calls = []
        def counting(args, *a, **kw):
            calls.append(args)
            return original(args, *a, **kw)
        with mock.patch.object(wiki.subprocess, "run", side_effect=counting):
            changes, objects = wiki.merge_integration_changes(self.root, commit, 2, paths)
            wiki.merge_blob_contents(self.root, objects, {p for p, _ in changes})
        self.assertEqual(len(changes), 25)
        self.assertEqual(sum("diff-tree" in call for call in calls), 1)
        self.assertEqual(sum("cat-file" in call for call in calls), 1)

    def test_nested_root_history_uses_project_relative_paths(self):
        """PW-42.8, PW-42.10: nested history uses project-relative paths."""
        self.adopt()
        self.change_code(1)
        self.commit("Drift")
        new = "# Design\n\nThe limit is now eighty.\n"
        self.write("notes/docs/design.md", new)
        self.add("notes/docs/design.md")
        root = self.root / "notes"
        self.commit("Document behavior")
        commit = self.git("rev-parse", "HEAD")
        self.assertEqual(wiki.substantial_paths_in_commit(root, commit, {"docs/design.md"}, False), {"docs/design.md"})

    def test_code_and_status_example_reset_staged_and_history(self):
        """PW-42.8, PW-42.9: code and non-status prose remain substantial."""
        self.adopt()
        for number, (old, new) in enumerate((("# Design\n\n```text\nStatus: pending\n```\n", "# Design\n\n```text\nStatus: accepted\n```\n"),
                         ("# Design\n\nDescription.\nStatus: pending\n", "# Design\n\nDescription.\nStatus: accepted\n"),
                         ("# Design\n\n```python\nif ready:\n    run()\n```\n", "# Design\n\n```python\nif ready:\nrun()\n```\n"),
                         ("# Design\n\n```text\n[x](old)\n```\n", "# Design\n\n```text\n[x](new)\n```\n"),
                         ("# Design\n\nUse `[x](old)`.\n", "# Design\n\nUse `[x](new)`.\n"))):
            with self.subTest(old=old):
                self.write("notes/docs/design.md", old)
                self.add("notes/docs/design.md")
                self.commit("Establish example")
                self.change_code(number + 1)
                self.commit("Drift")
                self.write("notes/docs/design.md", new)
                self.add("notes/docs/design.md")
                _, staged = self.run_cli("remind", "--staged")
                self.assertEqual(self.watch(staged)["notes"]["since"], "this commit")
                self.commit("Update example")
                _, history = self.run_cli("remind")
                self.assertEqual(self.watch(history)["notes"]["commits"], 0)

    def test_reordered_body_resets_staged_and_history(self):
        """PW-42.8, PW-42.9: changing step order is substantial."""
        self.write("notes/docs/design.md", "# Design\n\nFirst.\nSecond.\n")
        self.adopt()
        self.change_code(1)
        self.commit("Drift")
        self.write("notes/docs/design.md", "# Design\n\nSecond.\nFirst.\n")
        self.add("notes/docs/design.md")
        _, staged = self.run_cli("remind", "--staged")
        self.assertEqual(self.watch(staged)["notes"]["since"], "this commit")
        self.commit("Reorder steps")
        _, history = self.run_cli("remind")
        self.assertEqual(self.watch(history)["notes"]["commits"], 0)

    def test_stale_history_prefetch_scope_and_concurrency(self):
        """PW-42.10, PW-42.15: only eligible plans and inbox items are prefetched."""
        for i in range(10):
            self.write(f"dev/plans/work-{i}.md", "# Work\n\n状态：执行中。\n")
        self.write("dev/plans/done.md", "# Done\n\n状态：已完成。\n")
        self.write("dev/inbox/task/open.md", "# Task\n\n状态：待分诊。\n")
        self.write("dev/inbox/task/README.md", "# Inbox\n\n状态：待分诊。\n")
        self.adopt()
        snapshot = wiki.Snapshot(self.root)
        instance = wiki.Wiki(snapshot)
        lock = threading.Lock()
        active = peak = 0
        seen = []
        def fake_days(_wiki, path):
            nonlocal active, peak
            with lock:
                seen.append(path)
                active += 1
                peak = max(peak, active)
            try:
                time.sleep(.03)
                return 100
            finally:
                with lock:
                    active -= 1
        with mock.patch.object(wiki, "days_since_commit", side_effect=fake_days):
            wiki.remind_report(instance)
        self.assertGreater(peak, 1)
        self.assertLessEqual(peak, 8)
        self.assertEqual(set(seen), {f"dev/plans/work-{i}.md" for i in range(10)} | {"dev/inbox/task/open.md"})
        self.assertEqual(len(seen), 11)

    # -- B1: adoption commit ----------------------------------------------

    def test_adoption_commit_touching_docs_does_not_reset(self):
        """PW-42.1"""
        # Pre-adoption drift: two code commits with no config yet.
        self.write("notes/other.py", "x = 1\n")
        self.add("notes/README.md", "notes/docs/design.md", "notes/docs/decisions/count.md", "notes/src/title.py", "notes/other.py")
        self.commit("Project before adoption")
        self.change_code(1)
        self.commit("Drift 1")
        self.change_code(2)
        self.commit("Drift 2")
        # Adoption commit also edits a watched doc (as real adoption commits do).
        self.write("notes/docs/design.md", "# Design\n\nThe limit is sixty. Adopted. See [count](decisions/count.md).\n")
        self.add("docs/wiki.json", "notes/docs/design.md")
        self.commit("Adopt wiki and touch docs")
        code, report = self.run_cli("remind")
        self.assertEqual(code, 0, report)
        # The adoption commit's doc edit must not reset; pre-adoption drift is still counted.
        self.assertEqual(self.watch(report)["notes"]["commits"], 2)

    def test_docs_reviewed_trailer_on_adoption_commit_resets(self):
        """PW-42.2"""
        self.change_code(1)
        self.commit("Drift before adoption")
        self.write("notes/docs/design.md", "# Design\n\nThe limit is sixty. Adopted.\n")
        self.add("docs/wiki.json", "notes/docs/design.md")
        self.commit("Adopt wiki\n\nDocs-Reviewed: notes adoption review done")
        code, report = self.run_cli("remind")
        self.assertEqual(self.watch(report)["notes"]["commits"], 0, report)
        self.assertNotEqual(self.watch(report)["notes"]["since"], None)

    def test_adopted_at_commit_is_also_an_adoption_commit(self):
        """PW-42.3"""
        self.add(".")
        first = self.commit("Initial import touching docs")
        self.change_code(1)
        self.commit("Drift")
        self.config["adopted_at"] = first
        self.save_config()
        self.add("docs/wiki.json")
        self.commit("Register adopted_at")
        code, report = self.run_cli("remind")
        # The adopted_at commit edited docs but must not reset; one drift commit counts.
        self.assertEqual(self.watch(report)["notes"]["commits"], 1, report)

    def test_no_adoption_commit_when_config_never_committed(self):
        """PW-42.4"""
        # The config file is never committed, so there is no adoption commit.
        self.add("notes")
        self.commit("Code only, no config committed")
        self.change_code(1)
        self.write("notes/docs/design.md", "# Design\n\nThe limit is sixty-one now.\n")
        self.add("notes/src/title.py", "notes/docs/design.md")
        self.commit("Change code and docs")
        code, report = self.run_cli("remind")
        # The doc edit is substantial and resets; behaviour is unchanged from before.
        self.assertEqual(self.watch(report)["notes"]["commits"], 0, report)

    # -- B2: mechanical vs substantial changes ----------------------------

    def test_link_only_change_does_not_reset(self):
        """PW-42.5"""
        self.adopt()
        self.change_code(1)
        self.change_code(2)  # overwrite; still one staged file
        self.commit("Drift")
        self.change_code(3)
        self.commit("More drift")
        # Change only a Markdown link target, keeping the link text.
        self.write("notes/docs/design.md", "# Design\n\nThe limit is sixty. See [count](decisions/counter.md).\n")
        self.add("notes/docs/design.md")
        self.commit("Repoint a link")
        code, report = self.run_cli("remind")
        self.assertEqual(self.watch(report)["notes"]["commits"], 2, report)

    def test_frontmatter_updated_bulk_change_does_not_reset(self):
        """PW-42.6"""
        self.write("notes/docs/design.md", "---\nupdated: 2026-01-01\n---\n# Design\n\nThe limit is sixty.\n")
        self.adopt()
        self.change_code(1)
        self.commit("Drift")
        # Bulk rewrite of the 'updated' frontmatter field only.
        self.write("notes/docs/design.md", "---\nupdated: 2026-10-28\n---\n# Design\n\nThe limit is sixty.\n")
        self.add("notes/docs/design.md")
        self.commit("Bump updated date")
        code, report = self.run_cli("remind")
        self.assertEqual(self.watch(report)["notes"]["commits"], 1, report)

    def test_pure_rename_does_not_reset(self):
        """PW-42.7"""
        self.adopt()
        self.change_code(1)
        self.commit("Drift")
        # Move a watched doc without changing content (still inside watch.docs).
        self.git("mv", "notes/docs/design.md", "notes/docs/design-v2.md")
        self.commit("Rename the design page")
        code, report = self.run_cli("remind")
        self.assertEqual(self.watch(report)["notes"]["commits"], 1, report)

    def test_real_prose_change_resets(self):
        """PW-42.8"""
        self.adopt()
        self.change_code(1)
        self.commit("Drift")
        self.write("notes/docs/design.md", "# Design\n\nThe limit is now eighty.\n")
        self.add("notes/docs/design.md")
        self.commit("Update the documented limit")
        code, report = self.run_cli("remind")
        self.assertEqual(self.watch(report)["notes"]["commits"], 0, report)

    # -- B2 staged mode ----------------------------------------------------

    def test_staged_link_only_change_does_not_reset(self):
        """PW-42.9"""
        self.adopt()
        self.change_code(1)
        self.commit("Drift")
        self.change_code(2)
        self.write("notes/docs/design.md", "# Design\n\nThe limit is sixty. See [count](decisions/counter.md).\n")
        self.add("notes/docs/design.md")
        code, report = self.run_cli("remind", "--staged")
        self.assertEqual(code, 0, report)
        # Link-only doc edit does not silence the reminder or reset the count.
        self.assertIn("docs-not-updated", {f["rule"] for f in report["findings"]})
        self.assertNotEqual(self.watch(report)["notes"]["since"], "this commit")

    def test_staged_real_change_resets(self):
        """PW-42.9"""
        self.adopt()
        self.change_code(1)
        self.commit("Drift")
        self.change_code(2)
        self.write("notes/docs/design.md", "# Design\n\nThe limit is a hundred now.\n")
        self.add("notes/docs/design.md")
        code, report = self.run_cli("remind", "--staged")
        self.assertEqual(code, 0, report)
        self.assertNotIn("docs-not-updated", {f["rule"] for f in report["findings"]})
        self.assertEqual(self.watch(report)["notes"]["since"], "this commit")

    def test_staged_pure_moves_do_not_clear_debt_across_watch_boundaries(self):
        """PW-42.7, PW-42.9: both snapshots classify pure moves alike."""
        self.adopt()
        self.change_code(1)
        self.commit("Drift")
        self.git("mv", "notes/docs/design.md", "notes/docs/design-v2.md")
        self.change_code(2)
        staged = self.watch(self.run_cli("remind", "--staged")[1])["notes"]
        self.assertEqual(staged["commits"], 2)
        self.commit("Move and change code")
        self.assertEqual(self.watch(self.run_cli("remind")[1])["notes"]["commits"], 2)
        self.git("mv", "notes/docs/design-v2.md", "notes/design-outside.md")
        self.assertEqual(self.watch(self.run_cli("remind", "--staged")[1])["notes"]["commits"], 2)
        self.commit("Move outside watch")
        self.assertEqual(self.watch(self.run_cli("remind")[1])["notes"]["commits"], 2)
        self.git("mv", "notes/design-outside.md", "notes/docs/design-v3.md")
        self.assertEqual(self.watch(self.run_cli("remind", "--staged")[1])["notes"]["commits"], 2)
        self.commit("Move into watch")
        self.assertEqual(self.watch(self.run_cli("remind")[1])["notes"]["commits"], 2)

    def test_staged_move_with_mechanical_edits_and_mode_change(self):
        """PW-42.7, PW-42.9: mechanical move across watch boundaries preserves debt."""
        self.write("notes/docs/design.md", "---\nupdated: 2020-01-01\n---\n# Design\n状态：当前有效。\nStable explanation one.\nStable explanation two.\nStable explanation three.\nStable explanation four.\nSee [count](old.md).\n")
        self.adopt()
        self.change_code(1)
        self.commit("Drift")
        self.git("mv", "notes/docs/design.md", "notes/docs/moved.md")
        self.write("notes/docs/moved.md", "---\nupdated: 2026-01-01\n---\n# Design\n状态：已完成。\nStable explanation one.\nStable explanation two.\nStable explanation three.\nStable explanation four.\nSee [count](new.md).\n")
        os.chmod(self.root / "notes/docs/moved.md", 0o755)
        self.add("notes/docs/moved.md")
        self.assertEqual(self.watch(self.run_cli("remind", "--staged")[1])["notes"]["commits"], 1)
        self.commit("Move and edit mechanics")
        self.assertEqual(self.watch(self.run_cli("remind")[1])["notes"]["commits"], 1)
        self.git("mv", "notes/docs/moved.md", "notes/outside.md")
        self.write("notes/outside.md", "---\nupdated: 2026-02-01\n---\n# Design\n状态：当前有效。\nStable explanation one.\nStable explanation two.\nStable explanation three.\nStable explanation four.\nSee [count](other.md).\n")
        self.add("notes/outside.md")
        self.assertEqual(self.watch(self.run_cli("remind", "--staged")[1])["notes"]["commits"], 1)
        self.commit("Move outside and edit mechanics")
        self.assertEqual(self.watch(self.run_cli("remind")[1])["notes"]["commits"], 1)

    def test_staged_duplicate_moves_pair_once_and_keep_prose_order(self):
        """PW-42.7, PW-42.9: equal content pairs once; reordered prose is substantial."""
        self.write("notes/docs/a.md", "first\nsecond\n")
        self.write("notes/docs/b.md", "first\nsecond\n")
        self.adopt()
        self.git("rm", "notes/docs/a.md", "notes/docs/b.md")
        self.write("notes/docs/c.md", "first\nsecond\n")
        self.write("notes/docs/d.md", "second\nfirst\n")
        self.add("notes/docs/c.md", "notes/docs/d.md")
        snap = wiki.Snapshot(self.root, staged=True)
        changed = wiki.staged_substantial_paths(snap, {"notes/docs/a.md", "notes/docs/b.md", "notes/docs/c.md", "notes/docs/d.md"}, False)
        self.assertEqual(changed, {"notes/docs/b.md", "notes/docs/d.md"})

    def test_short_mechanical_move_and_reordered_move_match_history(self):
        """PW-42.7, PW-42.9: short moves and reordered prose agree before/after commit."""
        self.write("notes/docs/design.md", "[a](old.md)\n")
        self.adopt()
        self.change_code(1)
        self.commit("Drift")
        self.git("mv", "notes/docs/design.md", "notes/outside.md")
        self.write("notes/outside.md", "[a](a-completely-different-target.md)\n")
        self.add("notes/outside.md")
        self.assertEqual(self.watch(self.run_cli("remind", "--staged")[1])["notes"]["commits"], 1)
        self.commit("Move short page with mechanical edit")
        self.assertEqual(self.watch(self.run_cli("remind")[1])["notes"]["commits"], 1)
        self.write("notes/docs/ordered.md", "first\nsecond\n")
        self.add("notes/docs/ordered.md")
        self.commit("Add prose")
        self.change_code(2)
        self.commit("More drift")
        self.git("mv", "notes/docs/ordered.md", "notes/docs/reordered.md")
        self.write("notes/docs/reordered.md", "second\nfirst\n")
        self.add("notes/docs/reordered.md")
        self.assertEqual(self.watch(self.run_cli("remind", "--staged")[1])["notes"]["commits"], 0)
        self.commit("Move and reorder prose")
        self.assertEqual(self.watch(self.run_cli("remind")[1])["notes"]["commits"], 0)

    def test_history_batches_only_needed_blobs_and_skips_empty_candidates(self):
        """PW-42.14: many documents require one batch, not one process per blob."""
        from unittest.mock import patch
        for i in range(30):
            self.write(f"notes/docs/batch-{i}.md", f"before {i}\n")
        self.adopt()
        for i in range(30):
            self.write(f"notes/docs/batch-{i}.md", f"after {i}\n")
        self.write("notes/src/title.py", "unrelated business blob\n")
        self.add("notes/docs", "notes/src/title.py")
        commit = self.commit("Many documents")
        paths = {f"notes/docs/batch-{i}.md" for i in range(30)}
        original = wiki.subprocess.run
        batch_inputs = []
        def counting(args, *a, **kw):
            if "cat-file" in args:
                batch_inputs.append(kw.get("input", b""))
            return original(args, *a, **kw)
        with patch.object(wiki.subprocess, "run", side_effect=counting):
            self.assertEqual(wiki.substantial_paths_in_commit(self.root, commit, paths, False), paths)
            self.assertEqual(len(batch_inputs), 1)
            self.assertNotIn(self.git("rev-parse", "HEAD:notes/src/title.py").encode(), batch_inputs[0])
            self.assertEqual(wiki.substantial_paths_in_commit(self.root, commit, set(), False), set())
            self.assertEqual(len(batch_inputs), 1)
        self.git("mv", "notes/docs/batch-0.md", "notes/docs/moved.md")
        move = self.commit("Move without edits")
        batch_inputs.clear()
        with patch.object(wiki.subprocess, "run", side_effect=counting):
            self.assertEqual(wiki.substantial_paths_in_commit(self.root, move, {"notes/docs/batch-0.md", "notes/docs/moved.md"}, False), set())
            self.assertEqual(batch_inputs, [])

    def test_staged_copy_is_not_a_move_and_snapshot_is_immutable(self):
        """PW-42.9: a copy resets, and later index changes do not alter a snapshot."""
        self.adopt()
        self.change_code(1)
        self.commit("Drift")
        self.write("notes/docs/copy.md", (self.root / "notes/docs/design.md").read_text())
        self.add("notes/docs/copy.md")
        snap = wiki.Snapshot(self.root, staged=True)
        self.git("mv", "notes/docs/design.md", "notes/docs/moved.md")
        self.assertEqual(wiki.staged_substantial_paths(snap, {"notes/docs/copy.md"}, False), {"notes/docs/copy.md"})

    def test_adoption_history_cached_per_wiki_including_empty(self):
        """PW-42.13: each configuration snapshot queries adoption history once."""
        from unittest.mock import patch
        self.add("notes")
        self.commit("Before adoption")
        first = wiki.Wiki(wiki.Snapshot(self.root))
        second = wiki.Wiki(wiki.Snapshot(self.root))
        original = wiki.git_text
        queries = []
        def counting(root, *args):
            if "--diff-filter=A" in args:
                queries.append(args)
            return original(root, *args)
        with patch.object(wiki, "git_text", side_effect=counting):
            for _ in range(642):
                self.assertIsNone(wiki.days_since_commit(first, "dev/plans/missing.md"))
            self.assertEqual(len(queries), 1)
            wiki.adoption_commits(second)
            self.assertEqual(len(queries), 2)
            self.add("docs/wiki.json")
            commit = self.commit("Adopt")
            third = wiki.Wiki(wiki.Snapshot(self.root))
            self.assertEqual(wiki.adoption_commits(third), {commit})
            self.assertEqual(wiki.adoption_commits(first), set())
            self.assertEqual(len(queries), 3)

    # -- B3: plan-stale skips adoption and mechanical commits --------------

    def test_plan_stale_skips_adoption_commit(self):
        """PW-42.10"""
        old = "2020-01-01T00:00:00"
        self.write("dev/plans/work.md", "# Work\n\n状态：执行中。\n")
        self.add("dev/plans/work.md", "notes")
        self.commit("Create plan long ago", date=old)
        # Adoption commit touches the plan (as an import would) but recently.
        self.write("dev/plans/work.md", "---\nupdated: 2026-10-28\n---\n# Work\n\n状态：执行中。\n")
        self.add("docs/wiki.json", "dev/plans/work.md")
        self.commit("Adopt wiki and bump the plan")
        code, report = self.run_cli("remind")
        rules = {f["rule"] for f in report["findings"]}
        # The plan's last substantial change is the old creation, so it reads as stale
        # despite the recent adoption/frontmatter commit.
        self.assertIn("plan-stale", rules, report)

    def test_plan_stale_status_line_change_counts_as_recent(self):
        """PW-42.11"""
        old = "2020-01-01T00:00:00"
        self.write("dev/plans/work.md", "# Work\n\n状态：执行中。\n")
        self.add("dev/plans/work.md", "notes")
        self.commit("Create plan long ago", date=old)
        self.adopt()
        # Reconfirming the status line is substantial for plan staleness (B3).
        self.write("dev/plans/work.md", "# Work\n\n状态：阻塞。原因：等待接口。\n")
        self.add("dev/plans/work.md")
        self.commit("Mark the plan blocked")
        code, report = self.run_cli("remind")
        rules = {f["rule"] for f in report["findings"]}
        self.assertNotIn("plan-stale", rules, report)

    def test_shared_judgment_status_line_parameter(self):
        """PW-42.12"""
        # One shared classifier; the 状态 line differs only by the parameter.
        self.assertFalse(wiki.text_is_substantial("# 计划\n状态：执行中。", "# 计划\n状态：阻塞。", status_line_substantial=False))
        self.assertTrue(wiki.text_is_substantial("# 计划\n状态：执行中。", "# 计划\n状态：阻塞。", status_line_substantial=True))
        self.assertTrue(wiki.text_is_substantial("old prose", "new prose", status_line_substantial=False))
        self.assertTrue(wiki.text_is_substantial("old prose", "new prose", status_line_substantial=True))


if __name__ == "__main__":
    unittest.main()
