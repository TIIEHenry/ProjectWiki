"""Reads of the Git index and of Git history that do not repeat work (PW-09.19, PW-11.15).

The faster paths must return exactly what the plain ones return and still report failures.
"""

from __future__ import annotations

import subprocess
import unittest
from unittest import mock

from test_remind_hooks import RemindHookFixture
from test_wiki import ProjectFixture, wiki


class StagedBlobReaderTests(ProjectFixture):
    def setUp(self):
        super().setUp()
        self.samples = {
            "docs/empty.md": b"",
            "docs/binary.bin": bytes(range(256)) * 3 + b"\x00tail without a newline",
            # Larger than a pipe buffer, so the content arrives in several reads.
            "docs/large.md": ("# Large\n\n" + "A line that fills the page.\n" * 10000).encode(),
        }
        for path, data in self.samples.items():
            (self.root / path).write_bytes(data)
        self.initialize_index()

    def snapshot(self):
        snapshot = wiki.Snapshot(self.root, staged=True)
        self.addCleanup(snapshot.close)
        return snapshot

    def test_batch_reader_returns_the_bytes_of_each_object(self):
        """PW-09.19"""
        snapshot = self.snapshot()
        for path in self.samples:
            oid = snapshot.entries[path][1]
            self.assertEqual(snapshot.read(path), wiki.run_git(self.root, "cat-file", "blob", oid), path)
        self.assertEqual(snapshot.read("docs/empty.md"), b"")
        self.assertGreater(len(snapshot.read("docs/large.md")), 256 * 1024)

    def test_staged_check_reads_every_document_through_one_git_process(self):
        """PW-09.19"""
        for number in range(30):
            self.write(f"docs/page-{number:02}.md", f"# Page {number}\n\n[Index](INDEX.md)\n")
        self.git("add", "-A")
        with mock.patch.object(wiki.subprocess, "Popen", wraps=subprocess.Popen) as popen:
            snapshot = wiki.Snapshot(self.root, staged=True)
            try:
                project = wiki.Wiki(snapshot, "docs/wiki.json")
                findings = wiki.check(project)
                documents = project.documents()
            finally:
                snapshot.close()
        commands = [call.args[0] if call.args else call.kwargs["args"] for call in popen.call_args_list]
        self.assertGreaterEqual(len(documents), 34)
        self.assertNotIn("unreadable", {finding.rule for finding in findings})
        self.assertEqual(len([command for command in commands if command[-2:] == ["cat-file", "--batch"]]), 1, commands)
        self.assertEqual([command for command in commands if "cat-file" in command and "blob" in command], [])

    def test_reader_that_stopped_is_replaced_and_the_read_succeeds(self):
        """PW-09.19"""
        snapshot = self.snapshot()
        snapshot.read("docs/large.md")
        stopped = snapshot._blob_reader
        stopped.kill()
        stopped.wait()
        oid = snapshot.entries["docs/binary.bin"][1]
        self.assertEqual(snapshot.read("docs/binary.bin"), wiki.run_git(self.root, "cat-file", "blob", oid))
        self.assertIsNone(snapshot._blob_reader)
        self.assertEqual(snapshot.read("docs/empty.md"), b"")
        self.assertIsNotNone(snapshot._blob_reader)
        self.assertIsNot(snapshot._blob_reader, stopped)

    def test_object_missing_from_the_repository_is_reported(self):
        """PW-09.19"""
        snapshot = self.snapshot()
        snapshot.entries["docs/lost.md"] = ("100644", "0" * len(snapshot.entries["docs/empty.md"][1]))
        with self.assertRaises(wiki.WikiError):
            snapshot.read("docs/lost.md")
        self.assertEqual(snapshot.read("docs/empty.md"), b"")


class HistoryScanTests(RemindHookFixture):
    LOG = ("log", "--numstat", "--format=%x1e%H%x1f%P%x1f%s")

    def setUp(self):
        super().setUp()
        self.commit("Initial project", all_files=True)

    def change_code(self, number):
        self.write("notes/src/title.py", f"LIMIT = {60 + number}\n")
        self.commit(f"Change limit {number}", all_files=True)

    def change_design(self, text):
        self.write("notes/docs/design.md", f"# Design\n\n{text}\n")
        self.commit("Update the design page", all_files=True)

    def project(self):
        return wiki.Wiki(wiki.Snapshot(self.root), "docs/wiki.json")

    def count_records(self):
        """Count the records a caller takes from git_records, not the ones Git could print."""
        taken = []
        real = wiki.git_records

        def records(root, *args):
            for record in real(root, *args):
                taken.append(record)
                yield record

        patcher = mock.patch.object(wiki, "git_records", records)
        patcher.start()
        self.addCleanup(patcher.stop)
        return taken

    def test_records_are_the_split_of_the_whole_output(self):
        """PW-11.15"""
        for number in range(1, 5):
            self.change_code(number)
        whole = wiki.git_text(self.root, *self.LOG).split("\x1e")[1:]
        self.assertEqual(len(whole), 5)
        self.assertEqual(list(wiki.git_records(self.root, *self.LOG)), whole)
        self.assertEqual(list(wiki.git_records(self.root, *self.LOG, "--", "no/such/path")), [])

    def test_stopping_early_is_not_an_error_but_a_failed_command_is(self):
        """PW-11.15"""
        self.change_code(1)
        records = wiki.git_records(self.root, *self.LOG)
        first = next(records)
        records.close()
        self.assertEqual(first, wiki.git_text(self.root, *self.LOG).split("\x1e")[1])
        with self.assertRaises(wiki.WikiError):
            list(wiki.git_records(self.root, "log", "--format=%x1e%H", "no-such-revision"))

    def test_watch_scan_stops_at_the_commit_that_updated_the_documents(self):
        """PW-11.15"""
        for number in range(1, 4):
            self.change_code(number)
        self.change_design("Titles are limited to 63 characters.")
        self.change_code(4)
        self.change_code(5)
        taken = self.count_records()
        status, _ = wiki.history_debt(self.project())
        self.assertEqual(status["notes"]["commits"], 2)
        self.assertEqual(status["notes"]["since"], self.git("rev-parse", "HEAD~2")[:12])
        # Two code commits and the commit that updated the documents; the four older ones are not read.
        self.assertEqual(len(taken), 3)

    def test_plan_age_scan_stops_at_the_first_substantial_commit(self):
        """PW-11.15"""
        for number in range(1, 4):
            self.change_design(f"Round {number} of the design.")
        taken = self.count_records()
        self.assertEqual(wiki.days_since_commit(self.project(), "notes/docs/design.md"), 0)
        self.assertEqual(len(taken), 1)


if __name__ == "__main__":
    unittest.main()
