"""PW-48: watch patterns that match no file, and documents that were never committed."""

from __future__ import annotations

import os
import subprocess

from test_wiki import ProjectFixture


NOTES = {"name": "notes", "code": ["notes/src/*"], "docs": ["notes/docs/*", "notes/README.md"]}
TOOLS = {"name": "tools", "code": ["tools/src/*"], "docs": ["tools/docs/*"]}


class WatchDriftTests(ProjectFixture):
    GIT_ENV = {"GIT_AUTHOR_NAME": "Wiki Test", "GIT_AUTHOR_EMAIL": "wiki@example.invalid",
               "GIT_COMMITTER_NAME": "Wiki Test", "GIT_COMMITTER_EMAIL": "wiki@example.invalid"}

    def setUp(self):
        super().setUp()
        self.write("notes/README.md", "# Notes\n\n[Design](docs/design.md)\n")
        self.write("notes/docs/design.md", "# Design\n\nThe limit is sixty.\n")
        self.write("notes/src/title.py", "LIMIT = 60\n")
        self.set_watch(NOTES)

    def set_watch(self, *groups):
        self.config["remind"] = {"watch": list(groups), "threshold": {"commits": 3, "lines": 1000}}
        self.save_config()

    def dead(self):
        _, report = self.run_cli("check")
        found = [f for f in report["findings"] if f["rule"] == "watch-path-dead"]
        self.assertEqual({(f["severity"], f["path"]) for f in found} - {("warning", "docs/wiki.json")}, set())
        return sorted(f["key"] for f in found)

    def commit(self, message, *paths):
        self.git("add", *(paths or (".",)))
        subprocess.run(["git", "-C", str(self.root), "-c", "commit.gpgsign=false", "commit", "-q",
                        "--no-verify", "-m", message], check=True, capture_output=True,
                       env={**os.environ, **self.GIT_ENV})
        return self.git("rev-parse", "HEAD")

    def remind(self, *args):
        _, report = self.run_cli("remind", *args)
        watch = {item["name"]: item for item in report["watch_status"]}
        return watch, [(f["rule"], f["path"]) for f in report["findings"]]

    def tools_history(self):
        """Adopt, then change the tools code three times while tools has no document."""
        self.set_watch(NOTES, TOOLS)
        self.write("tools/src/run.py", "STEP = 0\n")
        self.git("init", "-q")
        self.commit("Adopt wiki")
        for step in (1, 2, 3):
            self.write("tools/src/run.py", f"STEP = {step}\n")
            self.commit(f"Change tools {step}")

    def test_dead_document_patterns_are_reported(self):
        """PW-48.1"""
        self.assertEqual(self.dead(), [])
        self.set_watch({**NOTES, "docs": NOTES["docs"] + ["notes/guide.md", "notes/manual/*"]})
        self.assertEqual(self.dead(), ["notes:docs:notes/guide.md", "notes:docs:notes/manual/*"])

    def test_code_wildcards_count_only_when_no_code_pattern_matches(self):
        """PW-48.2"""
        self.set_watch({**NOTES, "code": ["notes/src/*.py", "notes/src/*.kt", "notes/native/*.cc"]})
        self.assertEqual(self.dead(), [])
        self.set_watch({**NOTES, "code": ["notes/src/*.py", "notes/src/build.gradle"]})
        self.assertEqual(self.dead(), ["notes:code:notes/src/build.gradle"])
        self.set_watch({**NOTES, "code": ["notes/native/*.cc", "notes/native/*.h"]})
        self.assertEqual(self.dead(), ["notes:code:notes/native/*.cc", "notes:code:notes/native/*.h"])

    def test_uncommitted_documents_owe_nothing(self):
        """PW-48.3"""
        self.tools_history()
        watch, found = self.remind()
        self.assertEqual((watch["tools"]["commits"], watch["tools"]["since"]), (3, None))
        self.assertIn(("docs-review-due", "tools"), found)
        self.write("tools/docs/guide.md", "# Guide\n\nRun the tool.\n")
        watch, found = self.remind()
        self.assertEqual(watch["tools"], {"name": "tools", "commits": 0, "lines": 0, "since": "uncommitted docs"})
        self.assertIn(("docs-uncommitted", "tools"), found)
        self.assertNotIn(("docs-review-due", "tools"), found)
        self.assertIsNone(watch["notes"]["since"])
        self.assertNotIn(("docs-uncommitted", "notes"), found)

    def test_committing_the_documents_starts_the_count(self):
        """PW-48.4"""
        self.tools_history()
        self.write("tools/docs/guide.md", "# Guide\n\nRun the tool.\n")
        watch, found = self.remind("--staged")
        self.assertEqual((watch["tools"]["commits"], watch["tools"]["since"]), (3, None))
        self.assertNotIn(("docs-uncommitted", "tools"), found)
        self.git("add", "tools/docs/guide.md")
        watch, found = self.remind("--staged")
        self.assertEqual(watch["tools"], {"name": "tools", "commits": 0, "lines": 0, "since": "this commit"})
        self.assertNotIn(("docs-uncommitted", "tools"), found)
        commit = self.commit("Document the tool", "tools/docs/guide.md")
        watch, found = self.remind()
        self.assertEqual(watch["tools"], {"name": "tools", "commits": 0, "lines": 0, "since": commit[:12]})
        self.assertNotIn(("docs-uncommitted", "tools"), found)
        self.write("tools/src/run.py", "STEP = 4\n")
        self.commit("Change tools 4")
        self.assertEqual(self.remind()[0]["tools"]["commits"], 1)
