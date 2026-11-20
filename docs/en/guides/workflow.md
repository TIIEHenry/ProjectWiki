# Development workflow

> English translation of [开发流程](../../guides/workflow.md). The Chinese page is authoritative: if the two differ, the Chinese page applies.

This page explains the development steps of an adopting project, and how the roadmap, plans, decisions, and the knowledge text work together. Adopting the shared workflow, adapting paths, and project exceptions are under [Shared workflow and project adaptation](../../../scripts/wiki/en/workflow.md#shared-workflow-and-project-adaptation); for a complete example, see the [NoteBox reference project](../../../demo-en/README.md).

An Architecture Decision Record (ADR) states the basis of an important choice; a plan is the execution plan of one piece of work; the roadmap is the overall route of the project.

## Responsibilities of files

| File | The question it answers | What it should not repeat |
|---|---|---|
| roadmap | What to do next, and what the order and the dependencies are | Does not copy the steps of plans or the execution log |
| plan | How this work is completed, accepted, and handed off | Does not copy the full text of requirements and design |
| ADR | Why this important choice was made among several options | Does not serve as a to-do list or a progress board |
| Current knowledge | What the requirements, principles, design, and standards that apply today are | Does not pile up development logs |

The roadmap is by default a single `dev/roadmap.md`. One piece of work that needs a plan uses one `dev/plans/<topic>.md`, where the steps, the progress, the blockers, and the verification are updated. A status page is a coordination view used on demand: first reduce duplicate records and the number of updates, and then judge whether it needs to be kept or split; the exact conditions for creating, updating, and retiring it are under [Task records and status pages](../../../scripts/wiki/en/workflow.md#task-records-and-status-pages).

## Starting work

First find the target requirement or the maintenance goal, and check the applicable rules, the current design, and the scope of impact. Before creating a plan, check the existing plans and the matching history.

New features and behavior changes proceed by "confirm the requirement → implement and test → verify", with design and plans added according to the scope of impact:

1. Add or modify an entry in the requirement file and write acceptance criteria that can be checked, with the status "proposed". A new ID is taken as described in [How IDs are assigned](../../../scripts/wiki/en/formats.md#how-ids-are-assigned), and when parallel branches collide on an ID, the side that merges later changes its ID. The requirement, the implementation, the tests, and the affected current documents are kept in correspondence within the same change.
2. Once the boundary of the requirement and the acceptance criteria are clear, change the status to "accepted". When changes in structure, interfaces, dependencies, or compatibility need to be explained, write the approach in the relevant design page and cite the requirement ID.
3. During implementation, the tests write the acceptance IDs in their descriptive text; when it is done, the status of the requirement is changed to "implemented".
4. After running the tests or completing the manual check, add the "Evidence:" link to the requirement entry; an acceptance item marked "(manual)" also gets `Acceptance check: <acceptance ID>, agent:<name>, YYYY-MM-DD.`, and then the status is changed to "verified". For an acceptance item for which a test can be written, write the test and do not replace it with a check record.

The forms of requirement entries are in [Forms the tool reads](../../../scripts/wiki/en/formats.md#requirement-entries), and why tracing is done this way is in the [document model](../design/document-model.md#requirement-entries-and-tracing). `check` reports citations of IDs that do not exist and acceptance criteria that no test cites, and does not require a new design page because a design reference is missing.

A change whose boundary is clear, that has no significant risk or contract change, and that needs no multi-step collaboration or handoff can complete the tracing with only the requirement entry and tests, without a separate design or plan. When the description in an existing design becomes wrong because of the change, it still has to be updated at once. When multi-step collaboration, risk boundaries, handoffs, or long-running work are involved, create a plan; the plan cites the requirement IDs, and each step states which acceptance criteria it satisfies. Do not judge risk mechanically by the number of commits or of changed lines.

A local fix does not change existing requirements and needs no new requirement entry; citing the relevant IDs in the commit or in an existing plan is enough. When the fix reveals a gap in the requirement itself, go back to step 1.

A local fix can cite an existing task or commit record, keeping the basis of the change and the verification results.

A plan contains at least the goal, the related knowledge, the implementation steps, the acceptance, the open questions, and the verification record. The first line under the title gives the status, for example `Status: active.`; when several people or several agents work at the same time, the owner is written in the same line, for example `Status: active. Owner: agent:kiro.`, and before starting a piece of work, run `remind` first to see which plans are already active, who is responsible for them, and whether their scope overlaps with your own; after the status becomes finished or canceled, archive it by the completion process. The format is in the [status line decision](../../decisions/status-line.md) (in Chinese). Progress is maintained only in this plan, and the roadmap references it through a link.

Work navigation in current knowledge links by preference to long-lived entries such as `dev/INDEX.md` or the roadmap, which reduces link rewriting when plans are archived. When a specific gap has to be tracked or verification evidence has to be cited, a plan can be linked directly, with the purpose stated; at archiving, fix these in a targeted way by the reference relationships.

## Important trade-offs and ADRs

The reasons for a change are kept according to their use, which avoids writing every fix up as a decision:

| Use of the reason | Where it is kept |
|---|---|
| Explains only the cause and the approach of this fix | The commit message; when an existing task needs a handoff, it can be recorded in the task |
| Will go on constraining later changes | The current design page; when only a local implementation is involved, it can be written in the relevant code comments |
| Explains a choice with important long-term impact, and why the other options were not adopted | ADR |

Create an ADR when a choice will go on affecting structure, interfaces, dependencies, or compatibility, and there are alternatives that need explaining. Trade-offs not yet settled can first be noted in the plan.

An ADR uses four parts: background, alternatives, decision, and consequences. A record that affects only a module goes in the module's `docs/decisions/`, and a cross-module record goes in the root `docs/decisions/`. Use descriptive file names, and avoid depending on global sequence numbers.

An ADR is not a fixed formality before every task starts. An adopted decision may stay in force for a long time and is not archived because the matching plan is finished. The current design page keeps the conclusions now in force and links to the ADR when the trade-offs need explaining.

## Updating documents when a decision or design changes

Readers and agents work by the current requirements, principles, and design, and an ADR only explains the reasons. So when a decision or a design changes, update in the same change all the current documents that still describe the old conclusion. Do not change only the ADR, change only the code, or leave the syncing for later.

| What happened | What to do in the same change |
|---|---|
| A new ADR is adopted | Revise the affected requirements, principles, design, and module entries by the new conclusion; change the items in `AGENTS.md` that restate the rule along with them; design pages that need to explain the reasons link to this ADR |
| An ADR is superseded | The new ADR states which one it supersedes and why; the old ADR only has its status changed to "superseded" with a link to the new ADR, and the reasons of the time are not rewritten; links in current documents that point to the old ADR are changed to point to the new one |
| An ADR is retired with no replacement | The status of the old ADR is changed to "retired" with the reason stated; current documents delete the content that depends on this decision, or rewrite it as the present practice |
| The design changes and overturns the conclusion of an adopted ADR | Add a new ADR that supersedes it, and then handle it as in the row above. The design page and the ADR must not both be marked current while their content contradicts each other |
| The design changes but involves no adopted decision | Revising the design page in place is enough; no new ADR is needed |
| The behavior of the code changes an interface or a rule described in the documents | Commit the matching changes to the requirements, the design, or the module README together with the code |

Finished plans and archived files record the situation at the time and are not rewritten to follow new decisions. Once no current document references a superseded ADR any more, it can be archived by the [lifecycle rules](../design/lifecycle.md).

**Finding the affected documents.** Looking up links alone misses the places that restate the conclusion directly. The two methods have to be used together:

1. Look up the current documents that link to this ADR. You can use `rg -l '<ADR file name>'`; ordinary `rg` does not search `archive/` by default, so it yields exactly the current documents. You can also run `python3 scripts/wiki/wiki.py archive <ADR path> --root .` and use its read-only preview to list all the inbound links, without really archiving.
2. Search the current documents by the keywords of this decision, to find the places that have no link but write the old conclusion directly, especially `AGENTS.md`, the requirement pages, and the module READMEs.

Take `demo-en/` as an example: looking up links finds the 4 current documents that cite the [character counting decision](../../../demo-en/notes/docs/decisions/unicode-length.md); but `demo-en/AGENTS.md`, `demo-en/docs/requirements.md`, and `demo-en/notes/docs/requirements.md` write "counted by Unicode code points" directly without linking this ADR, and can be found only by searching for the keyword "code point". If the counting rule changes, all 7 places have to be updated in the same change.

The checker can only confirm that links exist and paths are valid; it cannot judge whether the content of the documents agrees with the new conclusion. This step requires the committer to read through the scope of the change, and it also has to be checked at review.

**Reminders at commit time.** In a project that has configured `remind`, every commit is checked by the Git hooks:
- when code is changed and the matching documents are not, an informational notice is given; below the accumulation threshold, changing documents or adding a review note for this notice is not required;
- when a decision record is changed, the documents that still link to it but were not changed this time are listed;
- when a requirement, principle, or decision configured in `ask_user` changes, a reminder says to confirm with the user first;
- when the accumulated amount of a group of code reaches the reminder threshold, a review of the matching documents is required; after the blocking threshold is reached, a commit that goes on changing code without a review fails.

After the review, update the documents according to the result, or state in the commit message the reason why no change is needed; the exact form and the counting rules are under [Configuration and rules](../../../scripts/wiki/en/reference.md#documentation-reminders-at-commit-time). When a change in an interface, behavior, or rule is already known to make a document wrong, update it at once, without waiting for the accumulation threshold. Why the reminders hang on commits is in the [automation design](../design/automation.md#reminders-hang-on-git-commits).

**Periodic review of knowledge pages.** For a knowledge page with a review-by date, `remind` gives a reminder after the date passes. After checking it again against the code and the sources, append a record to the verification line and write a new review-by date; when the path requires human verification, ask a person to check it, and do not have an agent fill in `human:` on their behalf.

## Reviews

The everyday checking of documents for given pages or topics can be reported directly in the session; a formal review needs findings recorded continuously, independent verification, and sign-off. The boundary between the two is under [the review rules](../../../scripts/wiki/en/workflow.md#reviews); do not create a whole set of review material just because a checking skill was run once.

A review is used to find problems systematically; it can be started by a person, and it can also be carried out by several agents in parallel. The file structure is in the [document model](../design/document-model.md#review-records).

1. **Prepare.** Determine the location of the review by the [project adaptation](../../../scripts/wiki/en/workflow.md#shared-workflow-and-project-adaptation) and create the review README, by default at `dev/reviews/<start date>-<topic>/README.md`. State the question to be answered, the scope, the baseline commit, and how the routes are divided. The number of routes and the way of dividing are decided as needed. The person responsible for the summary assigns a route number to each route in the route table; a route added midway also has its number registered first, and only then does the reviewer start writing.
2. **Discover.** Each route writes only its own route file, with one section for each finding and the status "pending". When different routes find the same problem, the one found later is judged "duplicate" at verification.
3. **Verify.** A person or agent who is not the author opens the code and documents in question and judges the findings one by one. The checker is written as `human:<name>` or `agent:<name>`, appends a row to the verification table of the finding section, and then changes the status line to the verdict. When the verdict is known, link to the existing plan, gap, or decision, and do not handle it again. The verification groups are written in the README; the routes each group is responsible for do not overlap, so parallel writing does not conflict.
4. **Plan.** Write plans for the confirmed and narrowed findings, in the finding sections. A fix that spans several findings gets a `plan-<topic>.md`.
5. **Sign off.** The result of the sign-off is written in the finding section and in the summary table of the README. The summary table is updated only by the person responsible for the summary.
6. **Implement.** After sign-off, the plan is the execution plan; a separately created `plan-*.md` has its status changed to "active". No board that records the progress a second time is created; the conflict scopes and slot registrations that an execution suite needs are kept for their [execution protocol purpose](../../../scripts/wiki/en/workflow.md#task-records-and-status-pages).
7. **Finish.** Conclusions still in force are written back into the design, the requirements, or the decisions, the status of the README is changed to "finished", and then `python3 scripts/wiki/wiki.py archive <actual review directory> --root .` previews the archiving of the whole directory; after confirming, add `--apply --expect <plan_sha256>` to execute.

A later review of the same topic creates a new dated directory and links to the previous review in its README. Do not append it to the old directory.

## Implementation and verification

Work that has a plan proceeds by the plan, and the completion of steps and the acceptance results update only the plan. When the design changes, update the knowledge in place; when a milestone changes, adjust only the matching entry in the roadmap. A reader's checklist in an operation guide is different from project progress, and a violation cannot be determined from the checkbox syntax alone.

Status is written only in the status line at the beginning of the plan. When the status line and the list of steps disagree, make them agree before archiving: when the status is already finished but there are still unchecked steps, give each remaining step a destination; when all the steps are done but it is still marked active, change it to finished and archive it.

At a handoff, state clearly what is done and what remains, the snapshot of the source code or configuration, the verification commands and results, the known failures, and which changes have been integrated. For the snapshot and the command results, use the output of `python3 scripts/wiki/wiki.py verify --root .` and do not write them by hand. The person taking over checks the relevant differences and then decides the scope of re-verification.

## Capturing experience

Diagnostic methods found during troubleshooting, operations that prove useful again and again, and lessons from failures that hold under certain conditions are part of current knowledge; write them back into an existing guide or the maintenance section of a module, and do not leave them in chat logs, task logs, or a separate experience library. No experience directory is created, because experience pages piled up by event or date have no way of ending and would grow with the rounds as review drafts do; when troubleshooting, readers look for an entry by symptom, not by date.

What is written back is divided into facts, constraints, and advice, because a summary written back by an agent is easily read as a rule by the next agent. A fact comes with evidence; the basis of a constraint is that there is a rule text that accepts it (a requirement, principle, standard, design, or decision record), and a guide only links to it and does not write it again; the rest is advice that readers weigh by the conditions, and raising it to a constraint goes through the existing requirement and decision processes. The selection criteria, the destination table, the elements of the text, and the self-check questions are under [the rules for capturing experience](../../../scripts/wiki/en/workflow.md#capturing-experience), and the steps are in the [knowledge capture skill](../../../scripts/wiki/en/skills/capture-knowledge/SKILL.md). The [title maintenance guide](../../../demo-en/docs/guides/maintenance.md) is an example of keeping diagnostic methods, their basis, and their limits by symptom.

## Completion and archiving

When finishing or canceling work, check the acceptance and where the remaining items go; write the new or changed stable knowledge back into `docs/`. When no knowledge has changed, do not add empty documents.

Archive finished plans and their attached evidence, keeping the original relative paths: first run `archive <path>` to preview, and then execute with `archive <path> --apply --expect <plan_sha256> --summary "<one-line description>"`; the tool rewrites the links and adds a row to the history index. How the index is selected and the preconditions for writing are under [the archive command](../../../scripts/wiki/en/reference.md#archiving-preview-first-then-apply). The roadmap updates only the matching link. Requirements, principles, design, and ADRs still in force stay in place; the specific rules are in [Lifecycle and archiving](../design/lifecycle.md).

Inbox items in `dev/inbox/` also have to end after triage: state in the item which plan it was turned into, which piece of knowledge it was written back into, which item it duplicates, or why it is not handled, change the status to "finished", and then archive it with the same `archive` command.
