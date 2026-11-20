# Document maintenance and archiving

> English translation of [文档维护与归档](../../design/lifecycle.md). The Chinese page is authoritative: if the two differ, the Chinese page applies.

Requirements: PW-05, PW-06, PW-07, PW-08, PW-13, PW-20, PW-24, PW-42, PW-43.

## First judge whether a document still has a current responsibility

The archive directory mainly keeps finished material of the development process, by default at `archive/`; the actual path is determined as described in [Shared workflow and project adaptation](../../../scripts/wiki/en/workflow.md#shared-workflow-and-project-adaptation). Content in stable knowledge that is out of date in part is revised directly, and the revision history is kept by Git.

| Content | Usual handling |
|---|---|
| `module-structure.md`, current interfaces, requirements, principles, and practice guides still in force | Maintained in place; not archived because of one change or the completion of a task |
| ADRs still in force | Kept within the knowledge scope they belong to |
| Finished or canceled plans | Archived after the remaining items and the knowledge updates are checked |
| Inbox items that have been handled | State the destination in the item (a plan, current knowledge, the duplicated item, or the reason for not handling it), and archive after the status is changed to finished |
| Experiment reports and raw verification records | Can be archived when the work ends; reusable conclusions are organized into current knowledge |
| Status pages | Kept or retired by the [coordination needs](../../../scripts/wiki/en/workflow.md#task-records-and-status-pages); the historical log leaves the current overview |
| Documents specific to a deleted module | Archived as a whole after confirming that there is nothing else they apply to |
| Superseded decisions or solutions abandoned as a whole | Archived after the reason, the scope of application, and the replacement are recorded |

Content that is waiting, blocked, or still constraining current behavior is not archived automatically because it is old or over the size budget.

Knowledge pages and assets that no current document links to cannot be found by readers through navigation, and `check` gives a warning (`orphan-page`, `orphan-asset`). Choose one of three ways to handle it: link to it from the matching navigation or entry; merge the content into another page; or confirm that it no longer has a current responsibility and archive or delete it by the rules of this page. Assets such as screenshots and prototypes are usually deleted outright when nobody references them, and old versions are kept by Git.

The directory of one review is archived as a whole: after the status of the README is changed to "finished" and all the plans have been implemented or transferred out, archive the whole review directory with `archive`; under the default layout, `dev/reviews/<date>-<topic>/` moves to `archive/dev/reviews/<date>-<topic>/`. As long as one plan has not ended, leave the whole directory where it is and do not archive it in pieces. The relative links inside the directory move with the directory and remain valid.

## Ways of failing that have already occurred in real projects

All of the situations below actually occurred in adoption surveys. When you meet the same signs while handling documents, handle them by the right-hand column.

| Symptom | Consequence | Handling |
|---|---|---|
| A plan is entirely finished or already canceled but still stays in `dev/` marked "active" | The list of work in progress is distorted, and readers cannot tell what is still being done. One project once had more than two thousand such files | Archive a plan by the rules of this page when it ends. `remind` goes only by the status line: it reminds when the status is already finished and the plan still stays in `dev/`; when the status still says active, it cannot find it |
| The progress of one piece of work is written in the status page, in roadmap checkboxes, and in a plan overview at the same time | The three places give different conclusions. There has been a case where the status page said that no task was in progress, the plan overview marked another item as the current focus, and the roadmap file still marked it as in progress | Progress is maintained only in the original plan or task record; the roadmap only links to the original record, the status page references it by its [coordination responsibility](../../../scripts/wiki/en/workflow.md#task-records-and-status-pages), and no separate overview is created because the number of plans grows |
| The status line and the list of steps disagree: the status is already finished while there are unchecked steps, or all the steps are checked while the status is still active | "Finished" and the remaining work contradict each other, and readers cannot tell whether it can be archived | Make them agree before archiving. State the destination of every unchecked step: a separate plan, written back into current knowledge, or explicitly canceled. The tool recognizes only the status line and cannot find this kind of disagreement |
| After a whole directory is moved, relative links have one `../` level too many or too few | The links show no problem in an editor but are in fact broken | Do not move by hand. Preview with `archive` and then execute with `archive --apply`; the tool rewrites the affected links and runs `check` after executing |
| The same feature has a set of explanations in each of two places, and the content gradually diverges | Readers do not know which one to trust | Keep only one current text, and change the other place into a link, or archive it as a whole |
| The feature has landed, but the knowledge layer still keeps a "current state / implementation / roadmap" series, or review reports are placed in the architecture directory | The same feature has several sets of explanations, and the process of arriving at the solution is taken for current behavior | Keep one document that describes current behavior. The process chapters of the series and the review reports are archived when they end; constraints still in force are written back into that design |
| The root cause of a fault and the process of fixing it are placed in the system design directory | The log of the fix is taken for the current design | The root cause and the process go in `dev/` and are archived when finished; constraints still in force are written back into the design page, and reusable diagnostic methods are written back into the maintenance guide; the routing is under [Capturing experience](../../../scripts/wiki/en/workflow.md#capturing-experience) |
| A standard requires links or formats to be checked, but no tool does it | The standard says "links verified" while they are in fact broken | An item that a standard claims is checked by a tool needs a matching check, otherwise it must not be written as "checked" or "verified" |
| When adopting in an old repository, plans already implemented are all marked "current" in order to avoid hundreds of archive reminders | The plans never show as finished, and the archiving process never starts. Of the 960 plans of one project, not one was "finished" | Write the status truthfully. After `adopted_at` is registered, the archive reminders of old plans are merged into one, and they are archived in batches from the list of `remind --all` |
| The new rules take effect only in a subdirectory named after the tool, for example only the status lines in `dev/plans/wiki/` are checked | Plans of the same kind are split between two directories; the rules appear to be in effect but in fact govern only a few files | Leave the plans in their original directory, mark off what already exists with `adopted_at`, and the rules take effect for the files added afterwards |
| Every route, every round, every model, and every sign-off of a review gets a file of its own, all laid flat in one directory | One review has dozens of files, and the verification results of the same finding are scattered in several places | One dated directory per review, with verification written into the finding section and the round and the model written in the table |

## Checking history when creating

Before creating `dev/plans/example.md`, check the current location and the history at the same path under the primary archive root, which under the default layout is `archive/dev/plans/example.md`. The tool provides a read-only entry:

```bash
python3 scripts/wiki/wiki.py check-new dev/plans/example.md --root .
```

What is matched is the complete original relative path; it cannot be judged by a basename such as `README.md` alone. After finding history of the same origin, read its scope and conclusions, and then judge whether this is a restoration, a duplicate creation, or a new topic reusing the path.

The same name in history is in itself a hint. Only overwriting existing text, duplicating a current identity, overwriting an archive target, or making known old references quietly change their meaning requires stopping and resolving. The check for new documents cannot replace the final conflict check before an archive is written.

## Archiving a whole page

Archiving keeps the file name and the complete original relative directory under the primary archive root; an example under the default layout:

```text
dev/plans/example.md → archive/dev/plans/example.md
core/docs/retired-design.md → archive/core/docs/retired-design.md
```

Module documents are not reclassified into another set of mirror directories. When the target already exists, the conflict is reported explicitly; nothing is overwritten or numbered automatically, and an unfinished migration is not reported as a success.

Archiving takes two steps, preview first and then execute:

```bash
python3 scripts/wiki/wiki.py archive dev/plans/example.md --root .
python3 scripts/wiki/wiki.py archive dev/plans/example.md --root . --apply --expect <plan_sha256 given by the preview> --summary "one-line description"
```

Executing moves the file, rewrites the inbound and outbound links listed by the preview, and then runs `check`. The example above carries `--summary`, so a row is also added to the table of the history index; how the index is selected and the preconditions for writing are under [the archive command](../../../scripts/wiki/en/reference.md#archiving-preview-first-then-apply). Any change of input after the preview makes the plan hash no longer match, and the execution is refused. Files are only moved, not staged.

A complete historical record extracted from a live file has no original path of its own. If such a fragment needs to be kept later, it should go to `archive/<original parent directory>/<source file name>.history/<record identifier>.md`, with the source and the boundaries of the extraction recorded as well; the `.history` suffix keeps it from conflicting with `archive/<original parent directory>/<source file name>`, the target of archiving the whole page. The tool handles only whole pages or whole directories and does not cut out or append historical fragments automatically.

## Controlling the cost of link migration

Keeping the paths of current knowledge pages stable avoids most migrations. When a whole page really is moved, `archive --apply` rewrites the links to it in registered documents so that they go on pointing to the same content; references outside registered documents (code comments, excluded directories) have to be searched for separately.

- The navigation it belongs to links directly to the current text or to a suitable history entry. When a link in an entry page is rewritten into the archive, the tool warns, and a person decides whether to change it to link to the current text or to keep the link to history.
- Ordinary relative outbound links are resolved from the position before the move, and the path is then recomputed according to whether the target moves.
- Historical evidence keeps the version of its time and cannot all be changed to the latest documents.
- When there are external bookmarks or many inbound links, a short redirect note can be kept at the old path; in ordinary Markdown the reader then has to open the link in it.
- `old.md#section` does not locate the new text automatically through a short redirect page. Known inbound links with anchors have to be checked individually.
- While a redirect page holds the place, the old path cannot be silently reused for unrelated text. Check the references and the historical identity before reusing it.

A redirect page does not copy the old conclusions and is not included as another piece of current knowledge. The tool introduces no special resolver for ID links; it rewrites only the links it parses and does no string replacement across the repository. The actual coverage is under [Configuration and rules](../../../scripts/wiki/en/reference.md#archiving-preview-first-then-apply).

## Search and check scopes

`/archive/` in the root `.ignore` makes ordinary `rg` return fewer historical results by default, while the archive is still kept by Git. When the task needs it, you can read archived files directly, or widen the search explicitly:

```bash
rg --no-ignore 'keyword' archive/
```

GNU `grep`, `git grep`, and the search of other hosts may use different ignore rules, and the default scope should be set according to what each can do. This setting does not restrict access to history.

When adopting in an old repository, first register the actual history roots and then configure a transitional search scope; do not exclude every source directory named `archive` across the board. The full lifecycle and link checks are independent of the search ignore rules and still have to check the structure of history.
