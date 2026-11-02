from __future__ import annotations

import os
import shutil
import subprocess
import unittest

from test_wiki import ProjectFixture, wiki, SCRIPT


class PlanLifecycleCheckTests(ProjectFixture):
    """check-time rules on plan status lines: blocked needs a reason, plans may not be 'current'. PW-43."""

    def plan(self, name, body):
        self.write(f"dev/plans/{name}", body)

    def test_blocked_plan_without_reason_is_warned(self):
        """PW-43.4"""
        self.plan("waiting.md", "# Waiting\n\n状态：阻塞。\n")
        self.plan("waiting-reason.md", "# Waiting with reason\n\n状态：阻塞。原因：等待 X 的接口评审。\n")
        self.plan("working.md", "# Working\n\n状态：执行中。\n")
        code, report = self.run_cli("check")
        self.assertEqual(code, 0, report)
        flagged = [x["path"] for x in report["findings"] if x["rule"] == "plan-blocked-no-reason"]
        self.assertEqual(flagged, ["dev/plans/waiting.md"])

    def test_blocked_plan_with_empty_reason_is_warned(self):
        """PW-43.4"""
        self.plan("empty-reason.md", "# Empty reason\n\n状态：阻塞。原因：。\n")
        code, report = self.run_cli("check")
        flagged = [x["path"] for x in report["findings"] if x["rule"] == "plan-blocked-no-reason"]
        self.assertEqual(flagged, ["dev/plans/empty-reason.md"])

    def test_english_reason_keyword_is_accepted(self):
        """PW-43.4"""
        self.plan("waiting.md", "# Waiting\n\nStatus: blocked. Reason: waiting for the API review.\n")
        self.config["status_values"] = {"blocked": "blocked"}
        self.save_config()
        code, report = self.run_cli("check")
        self.assertNotIn("plan-blocked-no-reason", self.rules(report))

    def test_plan_using_current_status_is_warned(self):
        """PW-43.5"""
        self.plan("landed.md", "# Landed work\n\n状态：当前有效。\n")
        code, report = self.run_cli("check")
        flagged = [x["path"] for x in report["findings"] if x["rule"] == "plan-status-current"]
        self.assertEqual(flagged, ["dev/plans/landed.md"])

    def test_decision_using_current_status_is_not_a_plan_warning(self):
        """PW-43.5"""
        self.write("docs/decisions/count.md", "# Count\n\n状态：当前有效。\n")
        self.write("docs/INDEX.md", "# Current\n\n[Work](../dev/INDEX.md)\n[Count](decisions/count.md)\n")
        code, report = self.run_cli("check")
        self.assertNotIn("plan-status-current", self.rules(report))

    def test_frontmatter_current_mapped_by_status_values_is_warned(self):
        """PW-43.5"""
        self.config["status_frontmatter"] = "status"
        self.config["status_values"] = {"accepted": "current"}
        self.save_config()
        self.plan("mapped.md", "---\nstatus: accepted\n---\n\n# Mapped plan\n\nSteps.\n")
        code, report = self.run_cli("check")
        flagged = [x["path"] for x in report["findings"] if x["rule"] == "plan-status-current"]
        self.assertEqual(flagged, ["dev/plans/mapped.md"])


class PlanLifecycleLegacyTests(ProjectFixture):
    """Files that existed at adopted_at are exempt from the new plan rules. PW-43."""

    GIT_ENV = {"GIT_AUTHOR_NAME": "Wiki Test", "GIT_AUTHOR_EMAIL": "wiki@example.invalid",
               "GIT_COMMITTER_NAME": "Wiki Test", "GIT_COMMITTER_EMAIL": "wiki@example.invalid"}

    def setUp(self):
        super().setUp()
        if not shutil.which("git"):
            self.skipTest("git is required for adopted_at tests")

    def commit(self, message):
        self.git("add", "-A")
        subprocess.run(["git", "-C", str(self.root), "-c", "commit.gpgsign=false", "commit", "-q", "--no-verify", "-m", message],
                       check=True, env={**os.environ, **self.GIT_ENV}, capture_output=True)

    def test_legacy_plans_are_exempt_from_blocked_and_current_rules(self):
        """PW-43.4 PW-43.5"""
        self.write("dev/plans/old-blocked.md", "# Old blocked\n\n状态：阻塞。\n")
        self.write("dev/plans/old-current.md", "# Old current\n\n状态：当前有效。\n")
        self.git("init", "-q")
        self.commit("Old layout")
        adopted = self.git("rev-parse", "HEAD")
        self.config["adopted_at"] = adopted
        self.save_config()
        self.write("dev/plans/new-blocked.md", "# New blocked\n\n状态：阻塞。\n")
        self.write("dev/plans/new-current.md", "# New current\n\n状态：当前有效。\n")
        code, report = self.run_cli("check")
        blocked = [x["path"] for x in report["findings"] if x["rule"] == "plan-blocked-no-reason"]
        current = [x["path"] for x in report["findings"] if x["rule"] == "plan-status-current"]
        self.assertEqual(blocked, ["dev/plans/new-blocked.md"])
        self.assertEqual(current, ["dev/plans/new-current.md"])


class PlanIdleRemindTests(ProjectFixture):
    """remind reports draft and blocked plans left idle for too long. PW-43."""

    GIT_ENV = {"GIT_AUTHOR_NAME": "Wiki Test", "GIT_AUTHOR_EMAIL": "wiki@example.invalid",
               "GIT_COMMITTER_NAME": "Wiki Test", "GIT_COMMITTER_EMAIL": "wiki@example.invalid"}

    def setUp(self):
        super().setUp()
        if not shutil.which("git"):
            self.skipTest("git is required for reminder tests")
        self.config["remind"] = {
            "watch": [{"name": "docs", "code": ["docs/*"], "docs": ["docs/INDEX.md"]}],
            "threshold": {"commits": 3},
        }
        self.save_config()
        self.git("init", "-q")

    def commit_old(self, message):
        self.git("add", "-A")
        env = {**os.environ, **self.GIT_ENV,
               "GIT_AUTHOR_DATE": "2020-01-01T00:00:00", "GIT_COMMITTER_DATE": "2020-01-01T00:00:00"}
        subprocess.run(["git", "-C", str(self.root), "-c", "commit.gpgsign=false", "commit", "-q", "--no-verify", "-m", message],
                       check=True, env=env, capture_output=True)

    def commit_now(self, message):
        self.git("add", "-A")
        subprocess.run(["git", "-C", str(self.root), "-c", "commit.gpgsign=false", "commit", "-q", "--no-verify", "-m", message],
                       check=True, env={**os.environ, **self.GIT_ENV}, capture_output=True)

    def test_old_draft_and_blocked_plans_are_idle_but_fresh_ones_are_not(self):
        """PW-43.1"""
        self.write("dev/plans/old-draft.md", "# Old draft\n\n状态：草案。\n")
        self.write("dev/plans/old-blocked.md", "# Old blocked\n\n状态：阻塞。原因：等待评审。\n")
        self.commit_old("Old plans")
        self.write("dev/plans/new-draft.md", "# New draft\n\n状态：草案。\n")
        self.commit_now("New plan")
        code, report = self.run_cli("remind")
        self.assertEqual(code, 0, report)
        idle = sorted(x["path"] for x in report["findings"] if x["rule"] == "plan-idle")
        self.assertEqual(idle, ["dev/plans/old-blocked.md", "dev/plans/old-draft.md"])

    def test_active_plan_is_stale_not_idle(self):
        """PW-43.1"""
        self.write("dev/plans/old-active.md", "# Old active\n\n状态：执行中。\n")
        self.commit_old("Old active plan")
        code, report = self.run_cli("remind")
        rules = {(x["rule"], x["path"]) for x in report["findings"]}
        self.assertIn(("plan-stale", "dev/plans/old-active.md"), rules)
        self.assertNotIn("plan-idle", {r for r, _ in rules})

    def test_idle_limit_is_configurable(self):
        """PW-43.1 PW-43.2"""
        self.write("dev/plans/old-draft.md", "# Old draft\n\n状态：草案。\n")
        self.commit_old("Old draft plan")
        self.config["remind"]["plan_idle_days"] = 100000
        self.save_config()
        self.commit_now("Raise the idle limit")
        code, report = self.run_cli("remind")
        self.assertNotIn("plan-idle", self.rules(report))

    def test_idle_limit_rejects_non_positive_integer(self):
        """PW-43.2"""
        for bad in (0, -1, 1.5, "60"):
            self.config["remind"]["plan_idle_days"] = bad
            self.save_config()
            code, report = self.run_cli("remind")
            self.assertEqual(code, 2, bad)
            self.assertTrue(any("plan_idle_days" in x["message"] for x in report["findings"]), (bad, report))

    def test_idle_default_is_sixty_days(self):
        """PW-43.2"""
        self.assertNotIn("plan_idle_days", self.config.get("remind", {}))
        self.write("dev/plans/old-draft.md", "# Old draft\n\n状态：草案。\n")
        self.commit_old("Old draft plan")
        code, report = self.run_cli("remind")
        # The 2020 commit is far more than the default 60 days old.
        self.assertIn("dev/plans/old-draft.md", [x["path"] for x in report["findings"] if x["rule"] == "plan-idle"])

    def test_legacy_idle_plans_fold_into_the_summary(self):
        """PW-43.3"""
        self.write("dev/plans/old-draft.md", "# Old draft\n\n状态：草案。\n")
        self.commit_old("Old draft plan")
        adopted = self.git("rev-parse", "HEAD")
        self.config["adopted_at"] = adopted
        self.save_config()
        self.commit_now("Register adopted_at")
        code, report = self.run_cli("remind")
        rules = [x["rule"] for x in report["findings"]]
        self.assertNotIn("plan-idle", rules)
        self.assertEqual(rules.count("legacy-lifecycle"), 1, report)
        summary = next(x for x in report["findings"] if x["rule"] == "legacy-lifecycle")
        self.assertIn("plan-idle 1", summary["message"])
        code, report = self.run_cli("remind", "--all")
        self.assertIn("dev/plans/old-draft.md", [x["path"] for x in report["findings"] if x["rule"] == "plan-idle"])
        self.assertNotIn("legacy-lifecycle", self.rules(report))


class BlockedReasonListingTests(ProjectFixture):
    """remind lists blocked plans with their reason. PW-43."""

    GIT_ENV = {"GIT_AUTHOR_NAME": "Wiki Test", "GIT_AUTHOR_EMAIL": "wiki@example.invalid",
               "GIT_COMMITTER_NAME": "Wiki Test", "GIT_COMMITTER_EMAIL": "wiki@example.invalid"}

    def setUp(self):
        super().setUp()
        if not shutil.which("git"):
            self.skipTest("git is required for reminder tests")
        self.config["remind"] = {
            "watch": [{"name": "docs", "code": ["docs/*"], "docs": ["docs/INDEX.md"]}],
            "threshold": {"commits": 3},
        }
        self.save_config()
        self.git("init", "-q")

    def test_blocked_plan_reason_is_listed(self):
        """PW-43.6"""
        self.write("dev/plans/with-reason.md", "# With reason\n\n状态：阻塞。原因：等待接口评审。\n")
        self.write("dev/plans/without-reason.md", "# Without reason\n\n状态：阻塞。\n")
        self.git("add", "-A")
        subprocess.run(["git", "-C", str(self.root), "-c", "commit.gpgsign=false", "commit", "-q", "--no-verify", "-m", "Plans"],
                       check=True, env={**os.environ, **self.GIT_ENV}, capture_output=True)
        code, report = self.run_cli("remind")
        plans = {x["path"]: x for x in report["active_plans"]}
        self.assertEqual(plans["dev/plans/with-reason.md"].get("reason"), "等待接口评审")
        self.assertIsNone(plans["dev/plans/without-reason.md"].get("reason"))


class ReasonKeywordTests(unittest.TestCase):
    """The 原因/Reason keyword is registered and parsed. PW-43."""

    def test_reason_keyword_is_in_the_table(self):
        """PW-43.4"""
        self.assertEqual(wiki.KEYWORDS["reason"], ("原因", "Reason"))

    def test_status_reason_reads_chinese_and_english(self):
        """PW-43.4"""
        self.assertEqual(wiki.status_reason("# T\n\n状态：阻塞。原因：等待接口评审。\n"), "等待接口评审")
        self.assertEqual(wiki.status_reason("# T\n\nStatus: blocked. Reason: waiting for review.\n"), "waiting for review")
        self.assertIsNone(wiki.status_reason("# T\n\n状态：阻塞。\n"))
        self.assertIsNone(wiki.status_reason("# T\n\n状态：阻塞。原因：。\n"))


if __name__ == "__main__":
    unittest.main()
