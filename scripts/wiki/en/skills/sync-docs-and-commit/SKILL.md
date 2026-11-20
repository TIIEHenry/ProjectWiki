---
name: sync-docs-and-commit
description: >-
  In a project that has adopted ProjectWiki, sync the current project's documents with the actual
  changes, check the verification results, and sort out the scope of the commit. Use when the user
  asks to sync documents and commit, to close out with a commit, or to check documents before a
  commit; a commit is created only when this request or an existing authorization includes
  committing.
---

# Sync documents and commit

> English translation of [同步文档与提交](../../../skills/sync-docs-and-commit/SKILL.md). The Chinese page is authoritative: if the two differ, the Chinese page applies.

This skill is provided by ProjectWiki and distributed with `scripts/wiki/`, for an adopting project to sync its own documents, verify the current change, and close out with a commit.

Reading this skill, or its being selected automatically, creates no authorization to commit, push, or modify external systems; keep to the scope authorized for this task, and do not ask again about operations that have already been explicitly authorized.

## Confirm the scope and the project entries

First determine the root directory of the project this task is in, and read the project's `AGENTS.md` and the related entries; all later paths, configuration, the working tree, the staging area, and Git commits refer to this project. Identify the implementation, the tests, the necessary documents, and the unrelated changes of this task, and check them together with what was already staged; that files are under the same path cannot be taken as grounds for their belonging to the same task.

The documentation workflow follows [Shared workflow and project adaptation](../../workflow.md#shared-workflow-and-project-adaptation). When you meet a conflict such as an old rule that still forces a status update with every commit, or separate commits for the plan and the implementation, handle the gap in the adoption as that section describes, and then continue with the affected closing operations.

From the project entries, find the requirements, the current documents, the existing plans, and the verification entry that correspond to this change. Read only the content related to this work, and do not create other records by default file names.

Include only the changes within the scope authorized this time. When one file mixes in other work, select by diff the parts that belong to this task and check the final staged content; when they cannot be separated reliably, leave things as they are, state the specific conflict, and ask for the necessary clarification of scope. Do not commit, unstage, overwrite, or clean up other people's changes on your own. When there is already unrelated staged content, first determine a way to keep it and to commit only the content of this task; if that cannot be done, stop the commit, and the document check can still be completed.

## Sync according to impact

- When a change in behavior, interfaces, or rules makes the current text untrue, update the matching text and the necessary references in this change. When an internal refactoring, a test, or a fix brings the implementation back in line with the existing documents, the documents can be left unchanged after checking. The specific boundaries are under [syncing documents](../../workflow.md#updating-documents-when-a-decision-or-design-changes).
- Update the requirement entries affected this time and the plans and review records actually in use, with the statuses and formats the project has registered; do not treat an ADR as a progress plan. An ordinary fix does not get a plan, an ADR, or a design page made up for it, and status pages and roadmaps are not all updated merely because the files exist. The reasoning can be written in the commit message; see [Task records and status pages](../../workflow.md#task-records-and-status-pages).
- When a plan, an inbox item, or a review record really has to be ended or archived this time, check the end conditions and the references as described in [Lifecycle and archiving](../../workflow.md#lifecycle-and-archiving), and then handle it with the wiki tool.

The implementation, the tests, and the documents that must be synced this time together form one complete change; the plan is not forced to be committed separately first, and unrelated work is not merged into this commit.

## Verify and handle the reminders

From the current project's verification entry, choose the checks that match the scope of the impact, and in that project's root directory use the `verify` check names actually registered in its configuration; the commands are in the [tool entry](../../README.md#common-commands). When a verification record needs to be saved, use the actual output of `verify`, and state the input, the scope, the failures, and the items not checked; a passing working-tree check cannot stand in for a check of the staged content.

Commit reminders are handled as described in [Configuration and rules](../../reference.md#documentation-reminders-at-commit-time); a document change or a review trailer is not additionally required every time. Text known to be untrue is still updated in the same change; a single `[info]` alone needs no added record. An `[agent]` reminder of an accumulated review must be handled after actually checking. On meeting `[user]`, first check the user's existing authorization, and confirm with the user only when it is not covered.

## Commit as authorized and report

Stage the changes of this task only when committing has been authorized; check the final diff and pass the commit checks that apply to the project, and then create the commit. When the user asks only for the documents to be checked, completing the check is enough; do not commit because the name of the skill contains `commit`.

State the reason for the change and the necessary verification basis as the project's conventions require. When a commit hook fails, examine the output and the state of the repository, fix the problems within the scope of this task, and retry; do not skip the hooks, and do not assume that a commit was or was not created before the failure. Without authorization, do not push and do not rewrite existing commits.

At the end, check what the commit actually contains and the remaining state of the working tree, and briefly report the necessary document syncing, the actual scope and results of the verification, and the result of the commit or the reason for not committing. Keep other work; there is no need to create a separate closing report or to list one by one the kinds of documents that were not used.
