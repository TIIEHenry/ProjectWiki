"""Default page/line size warnings, duplicate entry files, and directory budget specificity.

Covers PW-44. Style follows tests/test_wiki.py: each test names its acceptance IDs in the
docstring and drives the tool through the JSON CLI on a temporary project.
"""

import json
import sys
import unittest

from test_wiki import ProjectFixture, wiki, SCRIPT


class SizeLimitTests(ProjectFixture):
    def findings_for(self, report, rule):
        return [item for item in report["findings"] if item["rule"] == rule]

    # --- D1 page-oversized / line-oversized ---

    def test_oversized_page_warns_with_default_limit(self):
        """PW-44.1"""
        self.write("docs/big.md", "# Big\n" + "x" * 100001 + "\n")
        self.write("docs/INDEX.md", "# Current\n\n[Work](../dev/INDEX.md)\n[Big](big.md)\n")
        code, report = self.run_cli("check")
        self.assertEqual(code, 0, report)
        hits = self.findings_for(report, "page-oversized")
        self.assertEqual([h["path"] for h in hits], ["docs/big.md"])
        self.assertEqual(hits[0]["severity"], "warning")

    def test_page_just_under_limit_is_silent(self):
        """PW-44.1"""
        self.write("docs/ok.md", "# Ok\n" + "x" * 50 + "\n")
        self.write("docs/INDEX.md", "# Current\n\n[Work](../dev/INDEX.md)\n[Ok](ok.md)\n")
        code, report = self.run_cli("check")
        self.assertEqual(code, 0, report)
        self.assertEqual(self.findings_for(report, "page-oversized"), [])

    def test_registered_max_chars_suppresses_page_oversized(self):
        """PW-44.2"""
        self.write("docs/big.md", "# Big\n" + "x" * 100001 + "\n")
        self.write("docs/INDEX.md", "# Current\n\n[Work](../dev/INDEX.md)\n[Big](big.md)\n")
        self.config["pages"].append({"path": "docs/big.md", "max_chars": 200000})
        self.save_config()
        code, report = self.run_cli("check")
        self.assertEqual(code, 0, report)
        # The page states its own size through max_chars, so the default rule stays quiet;
        # page-budget would fire only once the registered limit is exceeded.
        self.assertEqual(self.findings_for(report, "page-oversized"), [])
        self.assertEqual(self.findings_for(report, "page-budget"), [])

    def test_long_line_warns_once_with_count_and_line_number(self):
        """PW-44.3"""
        body = "# Lines\n" + "short\n" + ("y" * 10001) + "\n" + ("z" * 10005) + "\n"
        self.write("docs/lines.md", body)
        self.write("docs/INDEX.md", "# Current\n\n[Work](../dev/INDEX.md)\n[Lines](lines.md)\n")
        code, report = self.run_cli("check")
        self.assertEqual(code, 0, report)
        hits = self.findings_for(report, "line-oversized")
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0]["path"], "docs/lines.md")
        self.assertEqual(hits[0]["line"], 3)  # first offending line
        self.assertIn("10001", hits[0]["message"])  # characters of the first offender
        self.assertIn("2 line", hits[0]["message"])  # total offending lines in the document

    def test_custom_limits_are_honoured(self):
        """PW-44.4"""
        self.write("docs/mid.md", "# Mid\n" + "x" * 500 + "\n")
        self.write("docs/INDEX.md", "# Current\n\n[Work](../dev/INDEX.md)\n[Mid](mid.md)\n")
        self.config["size_limits"] = {"page_chars": 200, "line_chars": 100}
        self.save_config()
        code, report = self.run_cli("check")
        self.assertEqual(code, 0, report)
        self.assertEqual(len(self.findings_for(report, "page-oversized")), 1)
        self.assertEqual(len(self.findings_for(report, "line-oversized")), 1)

    def test_ignore_pattern_suppresses_both_rules(self):
        """PW-44.5"""
        self.write("docs/gen/export.md", "# Export\n" + "x" * 100001 + "\n")
        self.write("docs/INDEX.md", "# Current\n\n[Work](../dev/INDEX.md)\n[Export](gen/export.md)\n")
        self.config["size_limits"] = {"ignore": ["docs/gen/*"]}
        self.save_config()
        code, report = self.run_cli("check")
        self.assertEqual(code, 0, report)
        self.assertEqual(self.findings_for(report, "page-oversized"), [])
        self.assertEqual(self.findings_for(report, "line-oversized"), [])

    def test_archive_documents_do_not_report_size(self):
        """PW-44.6"""
        self.write("archive/old.md", "# Old\n" + "x" * 100001 + "\n")
        code, report = self.run_cli("check")
        self.assertEqual(code, 0, report)
        self.assertEqual(self.findings_for(report, "page-oversized"), [])
        self.assertEqual(self.findings_for(report, "line-oversized"), [])

    def test_oversized_pre_adoption_file_still_reports(self):
        """PW-44.7"""
        # adopted_at exempts legacy files from new-file rules, but an existing oversized page
        # is exactly what should become visible, so size rules still fire.
        self.initialize_index()
        self.write("docs/big.md", "# Big\n" + "x" * 100001 + "\n")
        self.write("docs/INDEX.md", "# Current\n\n[Work](../dev/INDEX.md)\n[Big](big.md)\n")
        self.git("add", ".")
        self.git("-c", "user.email=a@b.c", "-c", "user.name=t", "commit", "-q", "-m", "seed")
        head = self.git("rev-parse", "HEAD")
        self.config["adopted_at"] = head
        self.save_config()
        self.git("add", ".")
        self.git("-c", "user.email=a@b.c", "-c", "user.name=t", "commit", "-q", "-m", "adopt")
        code, report = self.run_cli("check")
        self.assertEqual(code, 0, report)
        self.assertEqual([h["path"] for h in self.findings_for(report, "page-oversized")], ["docs/big.md"])

    def test_size_limits_field_validation(self):
        """PW-44.8"""
        for bad in ({"page_chars": 0}, {"line_chars": -1}, {"page_chars": "big"},
                    {"unknown": 1}, {"ignore": "docs/*"}, {"ignore": [1]}):
            self.config["size_limits"] = bad
            self.save_config()
            code, report = self.run_cli("check")
            self.assertEqual((code, report["result"]), (2, "incomplete"), (bad, report))

    # --- D2 entry-duplicate ---

    def test_entry_duplicate_warns_when_agents_and_claude_match(self):
        """PW-44.9"""
        body = "# Rules\n\n" + ("Follow the documented checks. " * 20) + "\n"
        self.assertGreater(len(body.strip()), 200)
        self.write("AGENTS.md", body)
        self.write("CLAUDE.md", "\n" + body + "  \n")  # same after strip, extra surrounding whitespace
        self.config["entrypoints"].append("CLAUDE.md")
        self.save_config()
        code, report = self.run_cli("check")
        self.assertEqual(code, 0, report)
        hits = self.findings_for(report, "entry-duplicate")
        self.assertEqual([h["path"] for h in hits], ["CLAUDE.md"])
        self.assertIn("@AGENTS.md", hits[0]["message"])

    def test_entry_import_stub_is_not_a_duplicate(self):
        """PW-44.10"""
        body = "# Rules\n\n" + ("Follow the documented checks. " * 20) + "\n"
        self.write("AGENTS.md", body)
        self.write("CLAUDE.md", "@AGENTS.md\n")
        self.config["entrypoints"].append("CLAUDE.md")
        self.save_config()
        code, report = self.run_cli("check")
        self.assertEqual(code, 0, report)
        self.assertEqual(self.findings_for(report, "entry-duplicate"), [])

    def test_short_identical_entries_are_not_flagged(self):
        """PW-44.10"""
        self.write("AGENTS.md", "# Rules\n\nShort.\n")
        self.write("CLAUDE.md", "# Rules\n\nShort.\n")
        self.config["entrypoints"].append("CLAUDE.md")
        self.save_config()
        code, report = self.run_cli("check")
        self.assertEqual(code, 0, report)
        self.assertEqual(self.findings_for(report, "entry-duplicate"), [])

    def test_differing_entries_are_not_flagged(self):
        """PW-44.10"""
        self.write("AGENTS.md", "# Rules\n\n" + ("A " * 200) + "\n")
        self.write("CLAUDE.md", "# Rules\n\n" + ("B " * 200) + "\n")
        self.config["entrypoints"].append("CLAUDE.md")
        self.save_config()
        code, report = self.run_cli("check")
        self.assertEqual(code, 0, report)
        self.assertEqual(self.findings_for(report, "entry-duplicate"), [])

    # --- D3 directory budget: most specific pattern wins ---

    def test_most_specific_dir_budget_pattern_applies(self):
        """PW-44.11"""
        # dev/* (broad) and dev/plans (specific) both match dev/plans. The specific
        # budget of 2 governs, so three plans exceed it even though dev/* allows 5.
        self.config["dir_budgets"] = {"dev/*": 5, "dev/plans": 2}
        self.save_config()
        for n in range(3):
            self.write(f"dev/plans/plan-{n}.md", f"# Plan {n}\n状态：执行中。\n")
        code, report = self.run_cli("check")
        hits = [h for h in report["findings"] if h["rule"] == "dir-budget" and h["path"] == "dev/plans"]
        self.assertEqual(len(hits), 1, report)
        self.assertIn("budget 2", hits[0]["message"])
        self.assertIn("dev/plans", hits[0]["message"])

    def test_broad_budget_covers_other_dev_subdirectories(self):
        """PW-44.11"""
        self.config["dir_budgets"] = {"dev/*": 2, "dev/plans": 30}
        self.save_config()
        for n in range(3):
            self.write(f"dev/roadmap/item-{n}.md", f"# Item {n}\n")
        self.write("docs/INDEX.md", "# Current\n\n[Work](../dev/INDEX.md)\n"
                   + "".join(f"[r{n}](../dev/roadmap/item-{n}.md)\n" for n in range(3)))
        code, report = self.run_cli("check")
        hits = [h for h in report["findings"] if h["rule"] == "dir-budget" and h["path"] == "dev/roadmap"]
        self.assertEqual(len(hits), 1, report)
        self.assertIn("dev/*", hits[0]["message"])


if __name__ == "__main__":
    unittest.main()
