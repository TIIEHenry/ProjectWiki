# Document model

> English translation of [文档模型](../../design/document-model.md). The Chinese page is authoritative: if the two differ, the Chinese page applies.

Requirements: PW-01, PW-02, PW-04, PW-05, PW-12, PW-14, PW-15, PW-16, PW-17, PW-18, PW-25, PW-26, PW-27, PW-47.

## Directories of an adopting project

The table below is the default layout. The actual paths of an existing project are determined as described in [Shared workflow and project adaptation](../../../scripts/wiki/en/workflow.md#shared-workflow-and-project-adaptation).

| Path | Responsibility |
|---|---|
| `AGENTS.md` | Global hard rules for agents and the routing of what to read by task |
| `docs/` | The requirements, principles, design, standards, operation and troubleshooting guides, reusable practices, and decision records currently in force, maintained in place |
| `dev/` | The development process: roadmap, plans, reviews, inbox items |
| `archive/` | Finished process material and documents that have lost their validity as a whole, keeping their original relative paths |
| `<module>/README.md` | Module entry: responsibilities, related contracts, how to verify |
| `<module>/docs/` | The design, decisions, maintenance guides, and reusable practices that belong to this module only; created when there is enough content |

The three root directories of the default layout sit side by side, and `archive/` can be created at the first archiving. A small module writes only a README and need not create a module `docs/`; the module table in the global documents links directly to the module entries, and no separate set of module mirror directories is created under `docs/`. The templates are in [`templates/en/project/`](../../../templates/en/README.md), and a complete example is [NoteBox](../../../demo-en/README.md).

## Responsibilities of pages

| Page | Content | How it is updated |
|---|---|---|
| Entry | The applicable rules, the conditions for reading, and the links to the targets | Updated when the routing changes |
| Current knowledge | Requirements, principles, structure, contracts, standards, operation and troubleshooting guides, and reusable practices | Continuously maintained in place |
| Decision record | The background, alternatives, conclusion, and consequences of an important choice | The original decision is kept; when the decision changes, the basis for replacing it is stated |
| Plan | The steps, progress, verification, and handoff of one piece of work | Updated along with that work |
| Roadmap | Direction, order, and the entries to milestones | Updated when the direction or the dependencies change |
| Optional status page | Links to current tasks, cross-module dependencies, and pending matters | Created, updated, or retired by the [coordination needs](../../../scripts/wiki/en/workflow.md#task-records-and-status-pages) |
| Inbox item | The observation, the request, the conjecture, the basis of verification, and the destination | Updated at triage and when handled; archived after it is handled and the destination is stated |
| Review | The scope and routes of one review, and each finding with its verification, plan, and sign-off | Appended to continuously while the review is in progress; the whole directory is archived when it ends |
| Archive | Finished processes or content retired as a whole | The source is kept, and overwriting history is avoided |

Current knowledge contains both project constraints and practical advice; the basis of a constraint is the requirement, principle, standard, design, or decision record that accepts it, see [Capturing experience](../../../scripts/wiki/en/workflow.md#capturing-experience).

Documents need not all adopt complex frontmatter. `docs/wiki.json` registers scopes, entries, roles, and budgets; the text uses titles, scopes, statuses, and sources that people can understand. Plans, decision records, and inbox items write their status in the first line under the title, for example `Status: active.`; from this the tool reminds about plans and inbox items that have not been updated for a long time or that are finished but not archived, and prevents entry pages from linking to superseded documents. The formats and the values are in [Formats the checker reads](../../../scripts/wiki/en/formats.md#status-lines-of-plans-decision-records-and-inbox-items), and why the first line of the text is used is in the [status line decision](../../decisions/status-line.md) (in Chinese). When several people or several agents work at the same time, the status line of a plan also names the owner, for example `Owner: agent:kiro.`, written in the same way as a checker; from this `remind` lists who is responsible for which work in progress. The progress of one piece of work is not written a second time in frontmatter, in roadmap checkboxes, or in another overview; duplicated progress in an existing overview is changed into links to the original records, see [Task records and status pages](../../../scripts/wiki/en/workflow.md#task-records-and-status-pages). An old repository that already records status in frontmatter can register the field name in the configuration; the tool reads this field from pages that have no status line, and checks whether the two agree when both are written, see the [status line decision](../../decisions/status-line.md) (in Chinese).

An execution suite and the documentation system share the existing development entry, and the actual sources of tasks, execution records, inbox items, verification, and archiving are stated by the [project binding](../../../scripts/wiki/en/workflow.md#sharing-the-development-entry-with-an-execution-suite); plans, task statuses, and slot records that serve different purposes can coexist and be linked, without copying the same fact.

## Current knowledge and target design

Confirming a requirement means that the project accepts the goal, not that the implementation is complete. A design page should state clearly whether it describes current behavior or a future solution; the limitations of the current implementation and the links to the matching work should be traceable.

When the tool checks configuration names, links, or fields, it proves only the part it checks. Whether a design is in effect and the result of the machine check are expressed separately, and one passing mark cannot replace the review of the whole document.

## Decisions and current design

An Architecture Decision Record (ADR) explains why a choice holds. The current requirements, principles, and design express what applies today, and cite ADRs where needed.

An ADR that affects only one module goes in the module's `docs/decisions/`; a cross-module ADR goes in the root `docs/decisions/`. The first version creates these directories on demand and uses descriptive file names, so that collaborators do not claim the same global sequence number.

An adopted ADR is not archived because its implementation is complete. After the whole decision is superseded or what it applies to is retired, it can be archived by the [lifecycle rules](lifecycle.md), keeping the replacement relationship.

ADRs and the current design must be consistent. When a decision changes, update in the same change the current documents that still describe the old conclusion; when a design change overturns an adopted decision, add a new ADR. The specific steps are in the [development workflow](../guides/workflow.md#updating-documents-when-a-decision-or-design-changes).

## Identity and paths

Ordinary Markdown links go on using paths that can be opened directly. The optional IDs in the configuration are used to check current identity and replacement relationships and do not require a special link syntax.

Texts currently in force must not have duplicate identities within one scope of application. Historical versions can keep the same logical ID and are told apart by the archive path and the source version; restoring a historical document does not require deleting the old evidence.

A summary describes the content. The conditions for reading are placed beside the navigation, so the same design page can be entered both from the feature development entry and from the fault maintenance entry.

## File naming

A file name is a navigation hint, not a complete identity. Stable knowledge uses descriptive names that sum up the topic; `draft`, `final`, `latest`, `done`, or a version number is not treated as the sole identity, and the status is written in the status line of the text. IDs that need stable references, such as requirement IDs and review finding IDs, are written in the text and are not reused.

Fixed entries use conventional names such as `README.md`, `AGENTS.md`, `CLAUDE.md`, `INDEX.md`, and `CHANGELOG.md`. After copying a placeholder template such as `templates/en/plan.md` or `templates/en/decision.md`, rename the file to the name of the specific topic.

The path of a new document must not contain spaces, `#`, `%`, or parentheses; these characters make archive links need escaping, and the tool cannot guarantee that a rewritten link still points to the same target. Markdown files in one directory that differ only in case are also treated as a conflict. Other matters of style (whether to use Chinese, ASCII, lowercase with hyphens, a length limit, or a date prefix) are decided by the adopting project itself; the tool only points out status words, version words, and template placeholder names in the check for new documents. Archiving, and a move that changes only the directory and not the file name, keep the original name and do not count as creating, so existing old file names do not get in the way of archiving and relocation.

Before creating a document, run `python3 scripts/wiki/wiki.py check-new <path> --root .`. It checks, by the complete original relative path, the current files and the history under the primary archive root, which under the default layout is `archive/<original relative path>`; other history roots have to be queried separately, and the scope is under [Configuration and rules](../../../scripts/wiki/en/reference.md#baseline-of-existing-problems). A hit in history is a hint and does not occupy the name permanently; archiving keeps the original file name and does not add a sequence number automatically.

## Changelog

`CHANGELOG.md` records, by version, the behavior changes that users can perceive and the things to note when upgrading. It is stable knowledge: sections are not rewritten after release, and only new versions are appended. Development steps, internal refactoring, and verification logs are not written into the changelog; they belong to plans and commit records.

A project with a release process can check at release time whether the changelog already has a section for the current version, and stop the release when it does not. A check of this kind is done by the project's own release script; the ProjectWiki tool does not check it.

## Requirement entries and tracing

In a requirement file each requirement is a heading that begins with an ID, the line under the heading gives the status, and the acceptance criteria are listed one by one, each with a sub-ID, written in a form that can be checked. The exact formats, the status values, and how IDs are assigned are in [Formats the checker reads](../../../scripts/wiki/en/formats.md#requirement-entries); when a project already has another ID format, keep the original IDs and register the format in the configuration, see [Configuration and rules](../../../scripts/wiki/en/reference.md#requirement-tracing). An ID is unique within one requirement scope. When a repository has several products that each number from `PRD-001`, register them as several groups in the configuration, each with its own requirement files, the documents that cite it, and the tests, and do not change the IDs for the sake of global uniqueness.

Acceptance criteria are proved by tests by default. Only an item that a command really cannot prove is marked "(manual)", and the person or agent who checks it writes one line of acceptance check record. This line is valid only for items marked for manual verification: if any item could replace a test with one line of check record, items for which a test can be written would also be let through with a single "checked". A verified requirement needs a line "Evidence:" that links to tests or to a verification record.

Downstream only cites the IDs and does not copy the text of the requirements: a test writes the acceptance ID in its descriptive text; when a design or a plan is needed, the related documents also cite the requirement ID. Whether a design and a plan are needed is judged by the [development workflow](../guides/workflow.md#starting-work); a lightweight change can keep only the requirement entry and the tests. The tool checks IDs cited wrongly and acceptance criteria without tests, and does not require a new document because a design reference is missing. The format of citations is in [Formats the checker reads](../../../scripts/wiki/en/formats.md#requirement-entries), and the trade-offs are in the [requirement traceability decision](../../decisions/requirement-traceability.md) (in Chinese).

A requirement that is confirmed but not yet implemented has the status "accepted" and is still stable knowledge. After implementation it is changed to "implemented", and once there is evidence, to "verified". When a requirement is canceled it is changed to "retired", and the ID is not deleted, so that the same ID does not point to something else later.

## Verification records and review-by dates

A knowledge page can write one line of verification record under the level-1 heading and before the first level-2 heading, and a page that goes out of date also writes a review-by date, for example `Verified: agent:kiro, 2026-10-28; human:clarence, 2026-11-02. Review by: 2027-04-28.`. The format is in [Formats the checker reads](../../../scripts/wiki/en/formats.md#verification-line-and-review-by-date).

A checker is always written as `human:<name>` or `agent:<name>`, and the checkers in a review's verification table, the authors of findings, owners, and signers use this form too. Three levels of trust can be told apart from this: no verification line means unverified; verified only by an agent; verified by a human. An agent must not write itself as `human:`. The tool cannot tell who wrote a line, so in a project that has configured `remind`, a commit that adds a `human:` name produces a `[user]` reminder asking the committer to confirm with the user; the rest is checked through review and the commit records.

A review-by date is an absolute date and is set only for pages that really go out of date, such as operations manuals, external facts, and investigation conclusions; it is renewed when the page is verified. After it passes, `remind` gives a reminder. The configuration can require certain paths to have a review-by date, or to have human verification. This format is borrowed from `verified` and `stale_after` of the Open Knowledge Format, and the trade-offs are in the [verification record and OKF decision](../../decisions/verification-line-and-okf.md) (in Chinese).

## Review records

One review is kept in one directory, by default at `dev/reviews/<start date>-<topic>/`; the actual location is determined by the [project adaptation](../../../scripts/wiki/en/workflow.md#shared-workflow-and-project-adaptation). The directory has one `README.md` that gives the scope, the baseline commit, how the routes are divided, the verification groups, and the summary of sign-offs; each route has one route file, for example `r01-input-boundary.md`. When there is only one route, the findings can be written directly in `README.md`. The template is in [`templates/en/review/`](../../../templates/en/review/README.md), and an example is the [title input review of the demo](../../../demo-en/dev/reviews/2026-10-28-title-input/README.md).

A directory name that begins with the start date is an exception to not writing dates in file names: the same topic is reviewed several times, with a new directory each time, and only the date makes it possible to find the most recent one. This date records only the day the review started; it is not changed afterwards and does not indicate progress.

How the routes are divided is decided by the reviewers: they can be divided by module, by topic, by one specific question, by a group of files, or by a class of defects, and the number of routes is not fixed. Route numbers are assigned by the person responsible for the summary, and a route added midway is also registered in the README before writing starts, so that reviewers working in parallel do not take the same route number.

Each finding is a level-2 heading in a route file, and the heading begins with the finding ID, for example `## r01-1 A title containing only zero-width spaces passes validation`. The ID is unique within the whole review and is used all the way from discovery, verification, plan, and sign-off to implementation. A finding section contains, in order, the verdict line, the observation, the conjecture, the verification table, the plan, and the sign-off; the formats and the verdict values are in [Formats the checker reads](../../../scripts/wiki/en/formats.md#review-findings). A few key points:

- The observation is the facts the author wrote down, including files and line numbers, commands and output. This part is not modified after verification starts.
- A second round of rechecking, or rechecking by another person or another model, appends a row to the verification table. The checker cannot be the author.
- A plan is written only for findings that are confirmed or narrowed. When one fix covers several findings and needs to be scheduled separately, it becomes `plan-<topic>.md` in the same directory.

What is verified is the finding itself, so the result of verification is written directly into the finding section and no separate verification file is created; the round, the model, and the date are written in the table and not in the file name. In this way the number of files of one review is roughly the number of routes plus one and does not multiply with the rounds and the participants.

## Cross-repository contracts

When a system consists of several repositories checked out side by side, a cross-repository contract (an interface, a version convention, a protocol) has its text only in the provider's repository. A consumer's repository writes how it uses the contract itself and links to the provider's page, without restating the conclusions and without copying the provider's README over as it is; one that has already been copied is changed into a short note that points to the canonical source. The same contract written once in each of several repositories will contradict itself sooner or later.

Cross-repository links are written as relative paths, and the target repository is registered in `repos` of the configuration. When the repository is checked out, the tool checks the target file and the anchor; when it is not, the report states how many links were not checked. Submodules need not be registered and are handled in the same way when not initialized. The links require the repositories to be checked out at the registered relative positions, and in a worktree nested under another directory these links cannot be resolved. The reasons and the alternatives are in the [decision on cross-repository links](../../decisions/cross-repo-links.md) (in Chinese), and the configuration is under [Configuration and rules](../../../scripts/wiki/en/reference.md#neighboring-repositories-and-submodules).

## Evidence and inbox items

A verification record states the code or configuration that was verified, the commands that were run, the results, and the known limitations. For the commands, the results, and the hashes of the files under test, use the output of `verify` and do not write them by hand; what was checked by hand is written after it. Records written afterwards are not part of the snapshot of the code under test.

An inbox item should keep observation and conjecture apart. Accepting something for investigation does not confirm the problem, and routing it to a plan does not mean the fix is done. An existing issue system can be reused; when an in-repository inbox is used, items are placed under `dev/inbox/` by type, one file per item, to avoid appending what everyone finds to one big file.

One file per item makes the inbox grow without end, so every item needs a way to end: after triage it is turned into a plan, written back into current knowledge, judged a duplicate, or decided not to be handled; the destination is written into the item, the status is changed to "finished", and then it is archived. It is archived rather than deleted because the reason for "not handling" will be asked about again later: when an item of the same name is created again, `check-new` points to the one in the archive. A project that has configured `remind` receives reminders about items long awaiting triage and items finished but not archived; the project template sets a directory file-count budget for the inbox by default, which does not depend on `remind`.
