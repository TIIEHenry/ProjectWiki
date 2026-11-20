---
name: organize-docs
description: Organize the existing wiki documents within a given scope of a business project that has adopted ProjectWiki; decide what to keep, merge, move, or archive, and maintain the references and the unfinished items. For everyday document housekeeping; not for a first adoption or for changing the business implementation.
---

# Organizing existing wiki documents

> English translation of [整理存量 Wiki 文档](../../../skills/organize-docs/SKILL.md). The Chinese page is authoritative: if the two differ, the Chinese page applies.

In the current business project, organize the topic, directory, or batch the user names, keeping valid knowledge, historical sources, and unfinished work. This skill handles only wiki documents and the references to them.

The documentation workflow follows [Shared workflow and project adaptation](../../workflow.md#shared-workflow-and-project-adaptation); tell actual paths, necessary exceptions, and conflicts not yet migrated apart as that section describes.

## Establish the scope of this batch

- Read the project's `AGENTS.md`, the existing documentation entries, and the actual wiki configuration, and confirm the root of the business project, the knowledge and process documents, the history roots, and the boundary of this batch. When the information is already clear, use it directly; ask only when the project or the scope to be organized is substantially ambiguous.
- Look at the related uncommitted changes, and handle only the content you have been permitted to organize. When the source, the destination, or the references to be rewritten have parallel modifications that cannot be separated safely, pause the affected part and continue with the parts that can be handled independently; do not overwrite other people's work.
- Read [Lifecycle and archiving](../../workflow.md#lifecycle-and-archiving) and [Task records and status pages](../../workflow.md#task-records-and-status-pages) as needed. Look up commands in the [tool entry](../../README.md), configuration and rules by name in [Configuration and rules](../../reference.md), and fixed formats in the [formats page](../../formats.md).

## Decide where things go

First read through the candidate text and the related entries, and check the current responsibility, the scope of application, the references, the historical sources, and the remaining items. Prefer editing in place or adding navigation, and merging after that; move or archive only when the location is unsuitable or the lifecycle has ended.

- **Keep and revise:** Current requirements, interfaces, and design, and decision records (ADRs) that still constrain current behavior, stay where they are and are maintained within the knowledge scope they belong to. Age, length, or the lack of inbound links cannot alone be a reason to archive; knowledge that has no inbound link but is still valid should be given an entry.
- **Merge:** First determine the authoritative text, distinguish real duplicates from content that applies to different things, and keep each unique constraint, exception, source, and piece of evidence item by item. When it cannot be determined which conclusion is valid, keep the difference and raise an item to be checked; do not write a conflict up as a unified conclusion.
- **Move:** Relocate only when the present location does not match the actual responsibility; keeping the paths of knowledge pages stable is good for references. Do not re-sort the whole repository for the sake of tidy directories, and do not split out a status page for every module by default.
- **Archive:** Judge by the lifecycle rules, and first write reusable conclusions back into current knowledge. When a plan marked as finished still has unchecked steps, check where they go and what the status should be against existing decisions; those with nowhere to go stay where they are with the problem stated, and work must not be cancelled or checked off as done because of a request to organize. Waiting, blocked, and unfinished work cannot be made to disappear by archiving.
- A review directory is archived as a whole only after all its plans have been implemented or handed over; a superseded decision or an abandoned proposal keeps its reasons of the time, with the reason, the scope of application, and what replaces it stated.

When merging or retiring old text, keep the existing IDs of requirements, findings, and the like together with their traceability, and update the current entries to point to the authoritative text; historical evidence still points to the record of the time and cannot all be changed to the latest conclusion. When an old source needs to be kept, handle it by the archiving rules; do not simply delete unique content.

## Carry out the text and path changes

First complete the necessary revisions of the text and the handover of unfinished items, then preview the actual path operations; merging text is not itself something the tool does automatically.

1. Use the read-only preview of `archive` or `move` as described in the [archiving rules](../../reference.md#archiving-preview-first-then-apply) or the [moving rules](../../reference.md#moving-documents); do not move files by hand.
2. Check the actual source, the destination, the files moved (including non-Markdown files), and the lists of inbound and outbound link rewrites in the preview, and confirm that all of them are within the authorized scope of this batch. For a directory move, also check the accompanying assets and the untracked content.
3. The preview does not contain every reference. Check code comments, scripts, configuration, excluded directories, and known external consumers according to who actually reads them; when a fixed entry, or a basis for recovery or acceptance, is still being read, resolve the dependency before moving. For references with anchors and for external bookmarks, keep a redirect as needed and check it separately; do not assume that a redirect page passes the anchor on.
4. When there is no conflict and the scope has been authorized, use the `plan_sha256` returned by that preview and apply with `--apply --expect`; no additional confirmation is needed. When a change in the input invalidates the plan, preview again; do not write a hash by hand or reuse an old one.
5. For a conflict of source or destination identity, an existing target, a rewrite that has to be done by hand, or a modification that cannot be handled safely, stop only the related operation and state the obstacle; do not overwrite, and do not get around the conflict by renaming automatically. When applying fails, check the working tree and the result of the rollback against what the tool actually reports; do not assume a complete recovery.

Before creating new text or a redirect page, use `check-new` as described in the tool entry to check the complete path and the history. If a title or a section changes after a merge, check the old anchors; current entries point to the current text, and historical entries keep their historical meaning. Update the generated index only when a generated index that the project has configured is affected; do not edit generated results by hand.

## Check and deliver

- Examine the diff, and check that the valid knowledge, the unique content, the IDs, the historical sources, and the unfinished items of this batch all have a definite place to go, and that no reference has changed its meaning because of a merge or a move.
- Look at the `after_check` returned by the path operation; when the text is modified afterwards, run `check` again as needed. When a verification record or other registered checks are needed, first check the commands in the configuration, then run `verify` for the actual scope and use its real output in the record; the details are under [Verification record](../../reference.md#verification-record).
- Briefly state the actual input and scope of this batch, the results, the unfinished or blocked parts, the checks that were run, and their limitations. When only some of the checks passed, do not report that all passed; nor can document checks prove that a business conclusion or an implementation is correct.
- Do not create a report or a plan for each document; remaining work is written into the project's existing inbox location with its source kept. By default, do not stage, commit, or push.
