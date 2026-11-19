"""Text that only looks like a link, heading IDs, links the snapshot cannot verify, and
documents or directories that are symbolic links (PW-09.14 to PW-09.18, PW-12.8).

Rules that must agree in both modes run against the working tree and the Git index.
"""

from __future__ import annotations

import os
import subprocess
import sys
import unittest

from test_wiki import ProjectFixture, SCRIPT


BOTH_MODES = ((), ("--staged",))


class ReferenceLinkTests(ProjectFixture):
    def test_undefined_pair_is_plain_text_on_a_page_without_definitions(self):
        """PW-09.14"""
        self.write("docs/topic.md", "# Topic\n\nCell m[i][j] holds the sum.\n\n1. **[P0][Nit]** Rename it. [Missing][not-defined]\n")
        code, report = self.run_cli("check")
        self.assertEqual(code, 0, report)
        self.assertNotIn("missing-reference", self.rules(report))

    def test_undefined_pair_is_reported_on_a_page_that_defines_reference_links(self):
        """PW-09.14"""
        self.write("docs/topic.md", "# Topic\n\n[Index][index] and [Missing][not-defined].\n\n[index]: INDEX.md\n")
        code, report = self.run_cli("check")
        self.assertEqual(code, 1, report)
        missing = [(x["line"], x["message"]) for x in report["findings"] if x["rule"] == "missing-reference"]
        self.assertEqual(missing, [(3, "Undefined reference link: not-defined")])

    def test_footnote_labels_are_never_reference_links(self):
        """PW-09.14"""
        self.write("docs/topic.md", "# Topic\n\nSee the registry [^108^][^165^] and [the index][index][^2].\n\n"
                                    "[index]: INDEX.md\n[^2]: A note.\n")
        code, report = self.run_cli("check")
        self.assertEqual(code, 0, report)
        self.assertNotIn("missing-reference", self.rules(report))

    def test_inline_link_after_a_plain_bracket_is_still_checked(self):
        """PW-09.14"""
        self.write("docs/topic.md", "# Topic\n\n[a][b](missing.md)\n")
        code, report = self.run_cli("check")
        self.assertEqual(code, 1, report)
        self.assertEqual([x["key"] for x in report["findings"] if x["rule"] == "broken-link"], ["missing.md"])


class HeadingIdTests(ProjectFixture):
    def test_id_written_in_braces_after_a_heading_is_an_anchor(self):
        """PW-09.15"""
        self.write("docs/topic.md", "# Topic\n\n## G0-1 — Call chain {#g0-1}\n\n## Limits {: #caps .note}\n\n## Plain {braces}\n")
        self.write("README.md", "# Example\n[A](docs/topic.md#g0-1)\n[B](docs/topic.md#caps)\n"
                                "[C](docs/topic.md#g0-1--call-chain-g0-1)\n[D](docs/topic.md#plain-braces)\n")
        code, report = self.run_cli("check")
        self.assertEqual(code, 0, report)
        # A class is not an ID, and the heading text without its attribute block is not an anchor anywhere.
        self.write("README.md", "# Example\n[E](docs/topic.md#note)\n[F](docs/topic.md#limits)\n[G](docs/topic.md#braces)\n")
        code, report = self.run_cli("check")
        self.assertEqual(code, 1, report)
        self.assertEqual([x["line"] for x in report["findings"] if x["rule"] == "broken-anchor"], [2, 3, 4])


class ExcludedLinkTests(ProjectFixture):
    def setUp(self):
        super().setUp()
        self.config["exclude"] += ["vendor/**", "**/build/**"]
        self.save_config()

    def test_link_into_an_excluded_path_the_snapshot_does_not_hold_is_counted(self):
        """PW-09.16"""
        self.write("docs/topic.md", "# Topic\n\n[Source](../vendor/lib/Api.java) and [report](../app/build/report.html).\n"
                                    "[Again](../vendor/lib/Other.java)\n")
        code, report = self.run_cli("check")
        self.assertEqual(code, 0, report)
        self.assertNotIn("broken-link", self.rules(report))
        counted = [{"path": "app/build", "links_unchecked": 1}, {"path": "vendor", "links_unchecked": 2}]
        self.assertEqual(report["coverage"]["excluded_links"], counted)
        text = subprocess.run([sys.executable, str(SCRIPT), "check", "--root", str(self.root)], capture_output=True, text=True).stdout
        self.assertIn("Links not checked: 2 into vendor, which is excluded and has no file in this snapshot", text)
        self.initialize_index()
        code, staged = self.run_cli("check", "--staged")
        self.assertEqual(code, 0, staged)
        self.assertEqual(staged["coverage"]["excluded_links"], counted)

    def test_missing_file_under_an_excluded_path_the_snapshot_holds_is_still_broken(self):
        """PW-09.16"""
        self.write("vendor/lib/Api.java", "class Api {}\n")
        self.write("docs/topic.md", "# Topic\n\n[Source](../vendor/lib/Api.java)\n[Gone](../vendor/lib/Gone.java)\n")
        self.initialize_index()
        for mode in BOTH_MODES:
            code, report = self.run_cli("check", *mode)
            self.assertEqual(code, 1, report)
            self.assertEqual([x["line"] for x in report["findings"] if x["rule"] == "broken-link"], [4])
            self.assertNotIn("excluded_links", report["coverage"])

    def test_ignored_local_checkout_gives_the_same_result_in_both_modes(self):
        """PW-09.16"""
        self.write(".gitignore", "vendor/\n")
        self.write("vendor/lib/Api.java", "class Api {}\n")
        self.write("docs/topic.md", "# Topic\n\n[Source](../vendor/lib/Api.java)\n")
        self.initialize_index()
        for mode in BOTH_MODES:
            code, report = self.run_cli("check", *mode)
            self.assertEqual(code, 0, report)
            self.assertEqual(report["coverage"]["excluded_links"], [{"path": "vendor", "links_unchecked": 1}])

    def test_ignored_target_that_is_not_excluded_stays_broken_and_says_why(self):
        """PW-09.16"""
        self.write(".gitignore", "local/\n")
        self.write("local/notes.txt", "scratch\n")
        self.write("docs/topic.md", "# Topic\n\n[Notes](../local/notes.txt)\n")
        self.initialize_index()
        code, report = self.run_cli("check")
        self.assertEqual(code, 1, report)
        broken = [x for x in report["findings"] if x["rule"] == "broken-link"]
        self.assertEqual(len(broken), 1, report)
        self.assertIn("Git ignores it", broken[0]["message"])
        code, staged = self.run_cli("check", "--staged")
        self.assertEqual(code, 1, staged)
        staged_broken = [x for x in staged["findings"] if x["rule"] == "broken-link"]
        # A staged check never reads the working tree; the baseline entry is the same either way.
        self.assertNotIn("Git ignores it", staged_broken[0]["message"])
        self.assertEqual(staged_broken[0]["key"], broken[0]["key"])


class GeneratedPageTests(ProjectFixture):
    def test_generated_page_may_list_replaced_documents(self):
        """PW-12.8"""
        self.write("docs/decisions/old.md", "# Old decision\n\n状态：被替代。\n")
        self.write("docs/catalog.md", "# Catalog\n\n[Old](decisions/old.md)\n")
        self.write("docs/design.md", "# Design\n\nWhy: [old](decisions/old.md).\n")
        self.config["pages"].append({"path": "docs/catalog.md", "role": "generated"})
        self.save_config()
        code, report = self.run_cli("check")
        self.assertEqual(code, 0, report)
        hits = [x["path"] for x in report["findings"] if x["rule"] == "links-replaced-document"]
        self.assertEqual(hits, ["docs/design.md"])


class UnreadableDocumentTests(ProjectFixture):
    def test_document_that_is_not_utf8_is_listed_and_the_check_finishes(self):
        """PW-09.17"""
        (self.root / "docs" / "latin.md").write_bytes(b"# Caf\xe9\n\n[Missing](missing.md)\n")
        self.write("docs/INDEX.md", "# Current\n\n[Work](../dev/INDEX.md) [Latin](latin.md) [Gone](gone.md)\n")
        self.initialize_index()
        for mode in BOTH_MODES:
            code, report = self.run_cli("check", *mode)
            self.assertEqual(code, 1, report)
            self.assertEqual(report["result"], "failed")
            found = sorted((x["rule"], x["path"], x["message"] if x["rule"] == "unreadable" else x["key"]) for x in report["findings"])
            # The page that cannot be read is named once; the rest of the project is still checked.
            self.assertEqual(found, [("broken-link", "docs/INDEX.md", "gone.md"),
                                     ("unreadable", "docs/latin.md", "File is not UTF-8: docs/latin.md")])
            self.assertEqual(report["documents_checked"], 4)


class SymlinkTests(ProjectFixture):
    # The project sits one level down so that links can point outside it.
    ROOT_SUBDIR = "project"

    def link(self, path, target):
        full = self.root / path
        full.parent.mkdir(parents=True, exist_ok=True)
        try:
            os.symlink(target, full)
        except (OSError, NotImplementedError):
            self.skipTest("symbolic links are not available")

    def outside(self, path, content):
        target = self.parent / "elsewhere" / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    def plans(self):
        # The linked plan would fail owner-format if it were read; it must not be.
        self.outside("plan.md", "# Shared plan\n\n状态：执行中。负责：someone\n")
        self.link("dev/plans/display-sync.md", "../../../elsewhere/plan.md")
        self.link("dev/plans/gap-closure.md", "../../../elsewhere/plan.md")
        self.write("dev/plans/send-path.md", "# Send path\n\n状态：执行中。负责：agent:dev\n")
        self.write("dev/INDEX.md", "# Work\n\n[Display](plans/display-sync.md#scope) [Gap](plans/gap-closure.md) [Send](plans/send-path.md)\n")

    def test_each_symlinked_document_is_listed_once_and_the_check_finishes(self):
        """PW-09.17"""
        self.plans()
        self.initialize_index()
        reasons = {(): "File resolves outside the selected root", ("--staged",): "Unsupported index file mode 120000"}
        for mode in BOTH_MODES:
            code, report = self.run_cli("check", *mode)
            self.assertEqual(code, 1, report)
            self.assertEqual(report["result"], "failed")
            unreadable = [x for x in report["findings"] if x["rule"] == "unreadable"]
            self.assertEqual([x["path"] for x in unreadable], ["dev/plans/display-sync.md", "dev/plans/gap-closure.md"])
            for item in unreadable:
                self.assertEqual(item["severity"], "error")
                # The baseline entry is the message as it was before the advice was added.
                self.assertEqual(item["key"], f"{reasons[mode]}: {item['path']}")
                self.assertTrue(item["message"].startswith(item["key"] + ". The path is a symbolic link"), item)
                self.assertIn("exclude", item["message"])
            # No other rule judges a page it cannot read: no status, owner or orphan finding.
            self.assertEqual([x["rule"] for x in report["findings"] if x["path"].startswith("dev/plans/")], ["unreadable", "unreadable"])
            self.assertEqual(report["documents_checked"], 5)
            # A link to such a page resolves; only the anchor it names cannot be looked up.
            linking = [x for x in report["findings"] if x["path"] == "dev/INDEX.md"]
            self.assertEqual([(x["rule"], x["key"]) for x in linking], [("unreadable-target", "plans/display-sync.md#scope")])
            self.assertIn("The path is a symbolic link", linking[0]["message"])
            self.assertEqual(report["errors"], 3)

    def test_excluding_a_symlinked_document_ends_its_finding(self):
        """PW-09.17"""
        self.plans()
        self.config["exclude"] += ["dev/plans/display-sync.md", "dev/plans/gap-closure.md"]
        self.save_config()
        self.initialize_index()
        for mode in BOTH_MODES:
            code, report = self.run_cli("check", *mode)
            self.assertEqual(code, 0, report)
            self.assertEqual(self.rules(report) & {"unreadable", "unreadable-target", "broken-link", "broken-anchor"}, set())
            # Links to an excluded link are counted, with or without an anchor.
            self.assertEqual(report["coverage"]["excluded_links"], [{"path": "dev/plans/display-sync.md", "links_unchecked": 1},
                                                                    {"path": "dev/plans/gap-closure.md", "links_unchecked": 1}])

    def test_archived_symlinked_document_only_warns(self):
        """PW-09.17"""
        self.outside("old.md", "# Old\n")
        self.link("archive/dev/plans/old-work.md", "../../../../elsewhere/old.md")
        code, report = self.run_cli("check")
        self.assertEqual(code, 0, report)
        self.assertEqual([(x["path"], x["severity"]) for x in report["findings"] if x["rule"] == "unreadable"],
                         [("archive/dev/plans/old-work.md", "warning")])

    def test_unreadable_requirements_file_keeps_the_check_incomplete(self):
        """PW-09.17"""
        self.config["requirements"] = {"files": ["docs/requirements/*.md"]}
        self.save_config()
        self.outside("requirements.md", "# Requirements\n\n## PW-01 First\n\n状态：提出。\n")
        self.link("docs/requirements/shared.md", "../../../elsewhere/requirements.md")
        code, report = self.run_cli("check")
        self.assertEqual(code, 2, report)
        self.assertEqual(report["result"], "incomplete")
        self.assertIn("docs/requirements/shared.md", report["findings"][0]["message"])
        self.assertIn("symbolic link", report["findings"][0]["message"])

    def test_unreadable_file_in_a_review_keeps_the_check_incomplete(self):
        """PW-09.17"""
        # A review is judged as a whole, so a missing part cannot be reported as one finding.
        self.outside("r01.md", "# r01\n\n## r01-1 Finding\n\nText.\n")
        self.write("dev/reviews/2026-11-02-engine/README.md", "# Engine review\n\n状态：执行中。\n\n[r01](r01-first.md)\n")
        self.link("dev/reviews/2026-11-02-engine/r01-first.md", "../../../../elsewhere/r01.md")
        self.write("dev/INDEX.md", "# Work\n\n[Review](reviews/2026-11-02-engine/README.md)\n")
        code, report = self.run_cli("check")
        self.assertEqual(code, 2, report)
        self.assertEqual(report["result"], "incomplete")
        self.assertIn("dev/reviews/2026-11-02-engine/r01-first.md", report["findings"][0]["message"])
        self.assertIn("symbolic link", report["findings"][0]["message"])

    def test_links_behind_a_symlinked_directory_say_so_and_can_be_excluded(self):
        """PW-09.18"""
        self.outside("docs/api.md", "# API\n")
        self.link("shared", "../elsewhere")
        self.write("docs/topic.md", "# Topic\n\n[API](../shared/docs/api.md)\n")
        self.initialize_index()
        for mode in BOTH_MODES:
            code, report = self.run_cli("check", *mode)
            self.assertEqual(code, 1, report)
            broken = [x for x in report["findings"] if x["rule"] == "broken-link"]
            self.assertEqual([(x["path"], x["key"]) for x in broken], [("docs/topic.md", "../shared/docs/api.md")])
            self.assertIn("lies behind the symbolic link shared", broken[0]["message"])
            self.assertIn("shared/** under exclude", broken[0]["message"])
        self.config["exclude"].append("shared/**")
        self.save_config()
        self.git("add", "docs/wiki.json")
        for mode in BOTH_MODES:
            code, report = self.run_cli("check", *mode)
            self.assertEqual(code, 0, report)
            self.assertNotIn("broken-link", self.rules(report))
            self.assertEqual(report["coverage"]["excluded_links"], [{"path": "shared", "links_unchecked": 1}])

    def test_required_path_behind_a_symlink_says_so(self):
        """PW-09.18"""
        self.outside("README.md", "# Shared\n")
        self.link("shared", "../elsewhere")
        self.config["modules"] = [{"name": "shared", "path": "shared", "entry": "shared/README.md"}]
        self.save_config()
        self.initialize_index()
        for mode in BOTH_MODES:
            code, report = self.run_cli("check", *mode)
            self.assertEqual(code, 1, report)
            missing = [x for x in report["findings"] if x["rule"] == "missing-entry"]
            self.assertEqual([(x["path"], x["key"]) for x in missing], [("shared/README.md", "Required path is missing from this snapshot")])
            self.assertIn("lies behind the symbolic link shared", missing[0]["message"])


if __name__ == "__main__":
    unittest.main()
