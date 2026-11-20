# Copyable templates

> English translation of [可复制模板](../README.md). The Chinese page is authoritative: if the two differ, the Chinese page applies.

First copy the files in `project/` into the target repository, replace every `[TODO: …]`, delete what does not apply, and then fill in `docs/wiki.json`. The `verify` of the template configuration registers only the document check, so `verify` can run as soon as `scripts/wiki/` has been copied; add the project's own test and build commands as described in the [adoption guide](../../docs/en/guides/adoption.md#11-register-verification-commands-and-reconciliation). The template configuration contains no `remind`, because the correspondence between code and documents can only be filled in for the target project; add it as described in the [adoption guide](../../docs/en/guides/adoption.md#8-set-up-documentation-sync-reminders), and install the Git hooks. Copy `module/` next to real modules as needed, and register the module paths in the configuration. The archive root `archive/` can be created at the first archive.

For a first adoption, or to complete an unfinished one, the [adoption skill](../../scripts/wiki/en/skills/adopt-projectwiki/SKILL.md) can be used on the target project the user names. Open it from the source repository the first time; once the complete `scripts/wiki/` has been copied, it can be opened locally in the target project, and the source repository still provides the templates and the complete adoption guide, to be read as needed.

When copying the complete `scripts/wiki/`, keep the whole `skills/` and the whole `en/`, which holds the English tool pages and skills. The `AGENTS.md` of the project template points to the adoption, review, organizing, knowledge capture, and sync-and-commit skills with a short task table; they are read only when needed, their text is not copied, and no step that every task must do is added. The host's native ways of discovering skills are in the [adoption guide](../../docs/en/guides/adoption.md#4-write-the-key-entries).

The project and module overview templates each have a "Maintenance and practices" section for reusable diagnostic methods and practices; the rules are under [Capturing experience](../../scripts/wiki/en/workflow.md#capturing-experience).

When an execution suite is used, fill in the optional binding section in the development entry of the project template, and the root `AGENTS.md` reads the actual task source through that entry; the responsibilities and the way to verify are under [Sharing the development entry](../../scripts/wiki/en/workflow.md#sharing-the-development-entry-with-an-execution-suite). When none is used, delete the section, and do not create empty task, queue, or slot records.

A small project can maintain requirements, principles, and design in the three sections of `docs/overview.md`. Split the page when the content grows; do not create empty documents in order to pass the checks. When an old project adopts, check its existing requirements as described in the [workflow cleanup step](../../docs/en/guides/adoption.md#1-read-projectwiki-and-survey-the-target-project), and then merge the templates. After adoption the [shared workflow](../../scripts/wiki/en/workflow.md#shared-workflow-and-project-adaptation) applies by default; keeping valid content and paths does not mean keeping the old workflow, and project exceptions are adapted as the shared workflow describes.

| Template | When to use it |
|---|---|
| [Minimum project set](project/README.md) | First adoption |
| [Minimum module set](module/README.md) | A module needs a knowledge entry of its own |
| [Requirements](requirements.md) | Writing requirements with IDs, statuses, and testable acceptance criteria |
| [Implementation plan](plan.md) | The work needs steps, acceptance, or a handoff across sessions |
| [Decision record](decision.md) | An important trade-off needs a lasting explanation |
| [Inbox item](inbox-item.md) | Recording a problem or suggestion that has yet to be triaged |
| [Review entry](review/README.md) and [route file](review/route.md) | One review: findings, verification, plans, and sign-offs are all written in these two kinds of file |

The status on the first line of `plan.md`, `decision.md`, and `inbox-item.md` must keep the format `Status: <value>.`; the checker relies on it to tell whether a plan has ended, a decision has been superseded, or an inbox item has been handled. The available values are under [Formats the checker reads](../../scripts/wiki/en/formats.md#status-lines-of-plans-decision-records-and-inbox-items). Templates that are copied into an adopting project mention `scripts/wiki/en/formats.md` only in plain text and do not link to ProjectWiki's own `docs/`, because those files do not exist in an adopting project. `plan.md`, `decision.md`, and `inbox-item.md` are copied as needed; an ordinary local fix can keep its goal, basis, and verification result in an existing task or in the commit record. A light change in behavior can also maintain only the requirement entry and the tests; whether to add a design, a plan, or an ADR is judged by the [extent of the impact](../../docs/en/guides/workflow.md#starting-work).

For a review, copy `review/README.md` to `dev/reviews/<start date>-<topic>/README.md` and copy one `review/route.md` for each route. Only when a fix spans several findings and needs to be scheduled on its own, create `plan-<topic>.md` from `plan.md` in the same directory and add a line `Covers: r01-1, r02-3.`

Write the text starting with the object, the rules, and the basis, and distinguish current facts, goals, and guesses. When writing verification results, fill in the real commands and what was verified; the blanks of a template cannot serve as evidence. After copying a placeholder template, rename it to a specific topic; file names, type directories, and budgets can be adjusted, and the text should be understandable to someone who did not take part in the project's discussions. The complete rules for naming and for the check of new documents are in ProjectWiki's [document model](../../docs/en/design/document-model.md#file-naming).

A complete example that runs is [NoteBox](../../demo-en/README.md). The tool and the adoption steps are in ProjectWiki's [adoption guide](../../docs/en/guides/adoption.md).
