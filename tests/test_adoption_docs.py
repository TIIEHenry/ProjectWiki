"""Adoption documentation: the copied workflow rules behave correctly in a target project.

Covers PW-47 and PW-10. The copied workflow and skills must retain resolvable local
references without the ProjectWiki source checkout.
"""
import re
import shutil
import unittest

from test_wiki import ProjectFixture, wiki, SCRIPT


WIKI_DIR = SCRIPT.parent  # scripts/wiki/ in the ProjectWiki repository
ADOPTION = SCRIPT.parents[2] / "docs" / "guides" / "adoption.md"  # docs/guides/adoption.md


class AdoptionWorkflowTests(ProjectFixture):
    def copy_tool(self):
        """Copy the whole scripts/wiki/ directory into the target project, as adoption does."""
        target = self.root / "scripts" / "wiki"
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(
            WIKI_DIR, target,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
        )
        # Register the module entry and its reference pages, as a target project does.
        self.config["modules"] = [
            {"name": "wiki", "path": "scripts/wiki", "entry": "scripts/wiki/README.md"}
        ]
        self.config["pages"] = self.config.get("pages", []) + [
            {"path": "scripts/wiki/README.md", "role": "entry", "max_chars": 6000},
            {"path": "scripts/wiki/reference.md", "role": "reference"},
            {"path": "scripts/wiki/formats.md", "role": "reference"},
            {"path": "scripts/wiki/workflow.md", "role": "reference"},
        ]
        self.config["pages"].extend(
            {"path": path.relative_to(self.root).as_posix(), "role": "reference"}
            for path in sorted((target / "skills").rglob("*.md"))
        )
        self.save_config()
        return target

    def test_workflow_doc_is_copied_with_the_tool(self):
        """PW-47.1"""
        target = self.copy_tool()
        self.assertTrue((target / "workflow.md").is_file())

    def test_copied_tool_checks_clean_without_broken_links(self):
        """PW-47.3, PW-10.7, PW-10.9, PW-10.11: copied skills retain local links."""
        target = self.copy_tool()
        for name in ("sync-docs-and-commit", "adopt-projectwiki", "review-docs", "organize-docs", "capture-knowledge"):
            self.assertTrue((target / "skills" / name / "SKILL.md").is_file())
            demo_entry = SCRIPT.parents[2] / "demo" / "AGENTS.md"
            self.assertIn(f"scripts/wiki/skills/{name}/SKILL.md", demo_entry.read_text(encoding="utf-8"))
        self.assertFalse((self.root / "dev" / "loop").exists())
        code, report = self.run_cli("check")
        self.assertEqual(code, 0, report)
        broken = [
            f for f in report["findings"]
            if f["rule"] in {"broken-link", "broken-anchor"} and f["path"].startswith("scripts/wiki/")
        ]
        self.assertEqual(broken, [], broken)

    def test_workflow_doc_links_only_inside_scripts_wiki(self):
        """PW-47.2"""
        text = (WIKI_DIR / "workflow.md").read_text(encoding="utf-8")
        # No relative link may climb out of scripts/wiki/ (that is how a link to docs/ is written).
        for target in re.findall(r"\]\(([^)]+)\)", text):
            self.assertFalse(
                target.startswith("../") or "/docs/" in target,
                f"workflow.md must not link outside scripts/wiki/: {target}",
            )
        # And it must not reference the knowledge root at all.
        self.assertNotIn("](../", text)

    def test_adoption_guide_maps_legacy_directories(self):
        """PW-47.4"""
        text = ADOPTION.read_text(encoding="utf-8")
        # The guide lists common legacy directories and where they should go.
        for name in ("docs/systems", "docs/architecture", "docs/modules", "docs/templates", "dev/progress"):
            self.assertIn(name, text, f"adoption guide should mention {name}")
        # And it gives the knowledge / process / archive decision rule.
        self.assertTrue("当前行为" in text and "失效" in text,
                        "adoption guide should explain the docs/dev/archive decision")

    def test_adoption_guide_constrains_the_transition_table(self):
        """PW-47.5"""
        text = ADOPTION.read_text(encoding="utf-8")
        # The transition table answers only "which single page to read", in three columns,
        # and corrections are written back into the authoritative page, not into the table.
        self.assertIn("current-sources", text)
        self.assertTrue("写回" in text, "adoption guide should say corrections go back to the current page")

    def test_adoption_guide_describes_retirement_notices(self):
        """PW-47.6"""
        text = ADOPTION.read_text(encoding="utf-8")
        self.assertTrue("停用说明" in text, "adoption guide should describe retirement notices")
        self.assertTrue("不再" in text and "改读" in text,
                        "retirement notice form should be '本文不再规定 X，改读 Y'")


if __name__ == "__main__":
    unittest.main()
