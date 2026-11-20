---
name: adopt-projectwiki
description: >-
  Adopt ProjectWiki in a project the user names, or complete an adoption that is not finished.
  Survey the existing documents and workflow, merge the necessary entries and configuration,
  connect the checks and reminders, and verify the actual effect. For adoption tasks; not for
  everyday commits or automatic upgrades.
---

# Adopting ProjectWiki in a project

> English translation of [给项目接入 ProjectWiki](../../../skills/adopt-projectwiki/SKILL.md). The Chinese page is authoritative: if the two differ, the Chinese page applies.

This skill is provided by ProjectWiki, and what it operates on is the business project the user names. The goal is to make the existing documents support real development tasks and to put the necessary checks into effect; adopt features as the project needs them, and do not create one of every kind of document in the templates.

## Establish the target and the source

First locate the root directory of the target project and read its `AGENTS.md`, the related entries, and the state of the Git working tree and the staging area. All adoption changes, project configuration, and verification refer to the target project; keep the existing uncommitted and untracked content.

A first adoption needs a readable ProjectWiki source that contains `docs/guides/adoption.md`, `templates/`, and `scripts/wiki/` (the English versions are `docs/en/guides/adoption.md`, `templates/en/`, and `scripts/wiki/en/`). Locate and verify these files from the path the user provides or from a known workspace, and keep the source and the target apart: opening this skill from the source repository does not mean that the target is the source repository, and opening it from inside a project does not mean that the project contains the complete templates. The source is read-only; do not create a dependency in the target's documents through absolute paths on this machine.

Read the adoption steps needed this time from `docs/guides/adoption.md` in the source; the rules, the templates, and the tool are taken from the same source. When the source is unclear or material is missing, first complete the survey of the target and state what is missing; do not guess a repository address, fabricate templates, or report an unfinished adoption as finished. When only completing the configuration of an existing tool, you can use the complete tool package already in the target and the [configuration reference](../../reference.md); fetching the source again is not required.

## Decide what needs to be added

Choose one real feature change of the project and one maintenance task, and follow the entries to the requirements, the constraints, the code, and the way to verify. Fill in navigation and text for the parts that cannot be found, are duplicated, or are untrue; do not build empty directories first.

Check content and workflow separately. Valid text, numbering, directories, and status wording are kept and registered by preference; the documentation development workflow is migrated as described in [Shared workflow and project adaptation](../../workflow.md#shared-workflow-and-project-adaptation). Clean up, one by one, the old requirements that duplicate or conflict with the shared workflow, and update the original entry, the checkers, and the other readers at the same time; a necessary exception states its grounds as that section describes, and a rule is not kept because the old one is stricter. A staged check and a working-tree check have different inputs, and one of them must not be deleted merely because the names are similar. The rules that result are written back into the existing entry; do not add a workflow list that needs long-term maintenance.

Do not take the product requirements, development conventions, or demo business content of the source repository as facts about the target project. The necessary records and the boundaries of status are in the [development workflow rules](../../workflow.md); how to register existing history is in the [configuration reference](../../reference.md), where you look up `adopted_at`, `status_frontmatter`, or `baseline` specifically.

## Merge the minimum adoption content

- Compare with the source templates, add the missing entries, and merge the existing files; keep business, interface, and security constraints and valid content, and handle the requirements of the old documentation workflow as in the previous section. Check the references before moving a path, use the [tool commands](../../README.md#common-commands) when a migration is really needed, and do not tidy the whole repository in passing.
- A first adoption copies the complete `scripts/wiki/` tool package, including the documentation, the skills, and the hooks. When the target already has files of the same name, compare first and add the missing files as needed; report version differences or local modifications of an existing tool separately, and do not overwrite or upgrade it on the grounds of completing the adoption.
- In the target's `docs/wiki.json`, register the actual scope of the documents, the entries, the modules, and the existing numbering, and merge the existing configuration, thresholds, and test commands. Handle existing historical problems as the source guide describes; do not hide the new problems of this adoption by excluding whole directories, enlarging the baseline, or relaxing the gate. `adopted_at` can only point to an adoption commit that actually exists; when nothing has been committed yet, state it as an item still to be completed, and do not commit on your own in order to fill it in.
- Merge the target's `AGENTS.md` and its search ignore rules. Links to the detailed workflow go to the copied tool documentation, and the skills only provide entries that are read according to the task; do not claim that the host's native skill discovery has been installed.
- Register the project's existing tests, builds, and document checks in `verify`; set up the `remind` correspondences against the real code and documents. When old commits cause accumulated debt, actually review the related text; do not reset the count by raising thresholds at will or by writing review notes that are not true. State explicitly which scope could not be checked and is left for later.

## Connect the hooks and verify

First check the existing Git hooks and the configuration currently in effect, then connect as described in [Installing the Git hooks](../../README.md#installing-the-git-hooks). When there is already a hook manager or script, merge the wiki checks into it and keep the original checks that still apply and have a purpose of their own; an equivalent check runs only once, the checks of the old documentation workflow migrate together with the rules, and unrelated configuration is not overwritten. Configure only locally in the target project and stay within the scope of operations the user has given; do not modify global Git settings or host settings. When there is no Git repository, do not initialize one on your own in order to pass the gate; report only the checks that could be completed.

Run the `verify` registered in the target and keep its real output; use `doctor` to check which checks are enabled and what the tool cannot judge, and use `remind` to check the actual reminders. Commands and exit codes are in the [tool entry](../../README.md); read the configuration according to the [rule reference](../../reference.md).

Following the adoption acceptance of the source guide, check the real reading paths, the tracing between requirements and tests, the necessary modules, and the actual staged snapshot. When staged verification is needed but changing the target's staging area has not been permitted, verify the candidate content in an isolated copy or a temporary index and state that it is not the original staging area; do not stage or unstage the work of other tasks. Verify the hook behavior in a temporary Git repository: an ordinary code and test fix can be committed while the review threshold has not been reached, and a broken link that is still in the staging area cannot be masked by a fix in the working tree. Temporary experiments do not change the commit history of the target project.

When the configuration has not entered the index being checked, the hooks are not enabled, or the checks cover only part of the scope, list this truthfully; an exit code of zero cannot stand in for the complete adoption acceptance.

## Deliver the adoption result

Briefly state the target project, the source used, the actual changes, the input and scope of the verification, and the adoption items still unfinished. Do not create a plan, a status page, or an audit report for the sake of reporting; items that really need follow-up go into the project's existing to-do list. After adoption, the everyday syncing of documents uses [Sync documents and commit](../sync-docs-and-commit/SKILL.md).

A request to adopt is not in itself an authorization to commit or push. Continue to complete what the user has already authorized; do not carry out commits, pushes, or changes to other projects that have not been authorized.
