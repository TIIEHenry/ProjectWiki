# Formats the checker reads

> English translation of [工具读取的写法](../formats.md). The Chinese page is authoritative: if the two differ, the Chinese page applies.

This page defines every fixed format the checker parses: where each one goes, how it is written, and which values it accepts. The page is copied together with the tool when `scripts/wiki/` is copied, so the templates and `AGENTS.md` in an adopting project carry only a summary, and this page governs the formats. For rule names, configuration fields, and the way the tool reports the problems it finds, see [Configuration and rules](reference.md).

The tool reads only these fixed lines. The rest of a page is treated as ordinary Markdown, and frontmatter is not required. On the rendered page each of these lines is an ordinary sentence that a person can read as it stands.

## General conventions

- Every keyword and every value has one Chinese form and one English form. The English forms are not case-sensitive. The colon can be full-width `：` or half-width `:`.
- The examples on this page use the English forms with ASCII punctuation. Chinese pages write the same lines with the Chinese forms and full-width punctuation; the [Chinese version of this page](../formats.md) shows them.
- Content in code blocks and inline code is not parsed, so a page that explains a format can show examples in backticks.
- People and agents are always written `human:<name>` or `agent:<name>`, wherever a checker, the author of a finding, an owner, or a signer is named. An agent may only write itself as `agent:`. The tool cannot tell who wrote a line, so in a project that has configured `remind`, when a staged change adds a `human:` name, the commit reminder asks the committer to confirm it with the user.
- A project can add synonyms for the statuses of plans, decision records, and inbox items in `status_values` of `docs/wiki.json`. Requirement statuses, review verdicts, and keywords cannot be configured.

## Keywords

| English | Chinese | Where it is written | Example |
|---|---|---|---|
| `Status` | `状态` | Plans, decision records, review READMEs, and inbox items: the first non-blank line below the level-one title. Requirements: the first non-blank line below the ID heading. Review findings: the first non-blank line below the finding heading | `Status: active. Scope: notes.` |
| `Owner` | `负责` | In the status line of a plan or a review README | `Owner: agent:kiro.` |
| `Reason` | `原因` | In the status line of a blocked plan | `Reason: waiting for the interface review of X.` |
| `Verified` | `核对` | On a knowledge page, below the level-one title and before the first level-two heading, at the start of a line | `Verified: agent:kiro, 2026-10-28; human:clarence, 2026-11-02.` |
| `Review by` | `复核期限` | In the same area as the verification line; it can follow that line or stand on a line of its own | `Review by: 2027-04-28.` |
| `manual` | `人工验证` | At the end of an acceptance item of a requirement, in parentheses | `(manual)` |
| `Acceptance check` | `验收核对` | In a requirements file, on the line after an acceptance item marked as manual verification, at the start of the line | `Acceptance check: PW-01.1, agent:codex, 2026-10-29.` |
| `Evidence` | `证据` | In a requirement entry, at the start of a line, followed by at least one link | `Evidence: [behavior tests](../tests/test_title.py).` |
| `Requirements` | `覆盖需求` | In a plan, at the start of a line | `Requirements: PW-11, PW-12.` |
| `Covers` | `覆盖问题` | In `plan-<topic>.md` of a review directory, at the start of a line | `Covers: r01-1, r02-3.` |
| `Author` | `作者` | In the section of a review finding, usually next to the observation | `(Author: agent:a, 2026-10-28)` |
| `Verification` | `核对` | In the section of a review finding, alone on a line (bold is allowed), immediately followed by the verification table | `**Verification**` |
| `Verdict` | `判定` | The header of the third column of a review verification table | The header cells read, in order: Round, Checker, Verdict, Basis |
| `Plan` | `方案` | In the section of a review finding, at the start of a line (bold is allowed) | `**Plan**` |

A `Requirements: PW-11` line in a design document and a `Scope: …` line at the top of a page are conventions for readers; the tool does not parse those two lines there. (Chinese pages write the design-document line as `对应需求：PW-11`.) A requirement ID counts as a reference wherever it appears in a current document.

## Status lines of plans, decision records, and inbox items

The first non-blank line below the level-one title reads `Status: <value>.` and can go on to give the scope, the owner, and other notes. The tool reads only this line; it does not read roadmap checkboxes or step lists. A project that already records status in frontmatter can register the field name in the configuration: a page without a status line then takes its value from that field, and when both are written this line wins. See [Configuration and rules](reference.md#configuration).

```markdown
# Multi-line title support

Status: active. Scope: notes. Owner: agent:kiro.
```

| English | Chinese | Class | Meaning |
|---|---|---|---|
| `draft` | `草案` | draft | Not yet in effect |
| `active` | `执行中` | active | The work is in progress |
| `blocked` | `阻塞` | blocked | The work is paused and waiting for a condition |
| `current` | `当前有效` | current | The decision is in effect |
| `finished` | `已完成` | finished | The work has ended and can be archived |
| `superseded` | `被替代` | superseded | A replacement document exists |
| `retired` | `废止` | retired | No longer applies, and nothing replaces it |
| `open` | `待分诊` | open | The inbox item has no conclusion yet |

A project's own wording, for example `cancelled` or `adopted`, is mapped to the classes above in `status_values`: `{"cancelled": "finished", "adopted": "current"}`.

The owner is written in the status line as `Owner: human:<name>` or `Owner: agent:<name>`. It is required when several people or agents work at the same time.

A plan whose status is `blocked` continues the status line with `Reason: <what it is waiting for>.`, for example `Status: blocked. Reason: waiting for the interface review of X.` The reason must not be empty: it tells other people where the plan stopped and what will release it. With English punctuation the tool reads the reason to the end of the line, so write `Reason:` last. `current` is a status for decision records and is not written on a plan: a plan describes work that ends, so finished work is written `finished` and replaced work `superseded`.

## Verification line and review-by date

A knowledge page writes these below the level-one title and before the first level-two heading:

```markdown
# Handling a failed title validation

Verified: agent:kiro, 2026-10-28; human:clarence, 2026-11-02. Review by: 2027-04-28.
```

- Each check is one entry of the form `<checker>, YYYY-MM-DD`; separate several entries with `;`. When the page is checked again, append an entry at the end of the line and keep the old ones.
- The review-by date is an absolute date. Write it only on pages that go out of date, such as runbooks, external facts, and the results of an investigation. It must not be earlier than the latest check.
- Only lines that begin with `Verified:` or `Review by:` count. The two keywords are not parsed when a list item or a sentence merely mentions them.

## Requirement entries

```markdown
### PW-11 Remind at commit time to sync the documents

Status: implemented.

- PW-11.1 A commit that changes only code gets the docs-not-updated reminder.
- PW-11.2 The specification reads clearly. (manual)
  Acceptance check: PW-11.2, agent:codex, 2026-10-29.

Evidence: [behavior tests](../tests/test_wiki.py).
```

- Each requirement is a heading of level two to four that begins with the ID. The default ID is a prefix that starts with an upper-case letter, then a hyphen, then a number, for example `PW-11`. When existing IDs use another format, register it in `requirements.id_pattern` and leave the IDs as they are.
- The first non-blank line below the heading is the status; the values are in the table below.
- An acceptance item is a list item that begins with the requirement ID, a dot, and a number, for example `PW-11.1`. A test refers to the item when it writes this ID in its descriptive text.
- An item that no command can prove is marked `(manual)` at its end, and the next line reads `Acceptance check: <acceptance ID>, <checker>, YYYY-MM-DD.` An acceptance check is valid only on an item marked as manual verification: under any other item the tool gives a warning, and the line does not take the place of a test.
- When the status changes to `verified`, add a line that begins with `Evidence:` and links to the test or the verification record.
- A plan lists the IDs on a line that begins with `Requirements:`; maintenance work writes `Requirements: none (<reason>)`. When a requirement is cancelled, change its status to `retired` and keep the ID.

| English | Chinese | Meaning |
|---|---|---|
| `proposed` | `提出` | Under discussion; the boundary and the acceptance criteria are not settled |
| `accepted` | `已接受` | The project accepts this goal; it is not implemented yet |
| `implemented` | `已实现` | The implementation is complete |
| `verified` | `已验证` | A test or a check record serves as evidence |
| `retired` | `已废止` | No longer required; the ID is kept |

## Review findings

A review is one directory, by default `dev/reviews/<start date>-<topic>/`; the actual location follows the [project adaptation](workflow.md#shared-workflow-and-project-adaptation). The directory holds a `README.md` and one route file for each route. A fix that spans several findings is written in `plan-<topic>.md` in the same directory. The directory name begins with the start date because the same topic is reviewed more than once and the date identifies the latest review; the date is not changed afterwards.

Each finding is a level-two heading in a route file. The heading begins with the finding ID, which is the route number, a hyphen, and a sequence number, for example `## r01-1 A title containing only zero-width spaces passes validation`. The first non-blank line below the heading is a status line that gives the verdict:

| English | Chinese | Meaning |
|---|---|---|
| `pending` | `待核对` | Nobody has verified it yet |
| `confirmed` | `成立` | The finding holds and needs a plan |
| `narrowed` | `收窄` | Part of it holds; state which part does not |
| `rejected` | `不成立` | The finding does not hold |
| `known` | `已知` | A plan, a gap, or a decision already covers it; a link to that is required |
| `duplicate` | `重复` | It repeats another finding of this review; that finding's ID is required |

The section then contains, in order, the observation (with its author), a conjecture (optional), the verification table, the plan, and the sign-off. The verification table has one row for each round and four columns: round, checker, verdict, and basis. The checker must not be the author. When verification is finished, change the verdict at the top of the section to the verdict of the last round. The sign-off says `signed`, `signed (narrowed)`, or `not signed`, with the signer and the date; the tool does not parse the sign-off.

## Inbox items

One file for each item, at `dev/inbox/<type>/<topic>.md`, for example `dev/inbox/bug/combining-character-count.md`. The first non-blank line below the title is the status:

- A new item is written `Status: open.`, followed by its source.
- When the item has been handled, write where it went (which plan it became, which knowledge page it was written into, which item it duplicates, or why nothing will be done), change the status to `Status: finished.`, and archive it with `archive`. After that, `check-new` points out this history when a new item of the same name is created.

## How IDs are assigned

- **Requirement IDs** take the highest ID in use plus one, and an ID that has been used is never given to another requirement. When the configuration divides the requirements into groups, take the number within the group. Two branches that add requirements at the same time can take the same ID, and after the merge `check` reports `trace-duplicate-id`. The side that merges later then moves to the next free ID and, in the same change, updates the design documents, plans, and tests on its branch that refer to it. An ID that has already been merged into the main branch is not changed. A parallel branch that will live for a long time can reserve its ID first, by committing on its own an entry that has only the ID heading and `Status: proposed.`
- **Review route numbers** are assigned by the person who consolidates the review, in the route table of the review README. A route added midway is also registered before anyone starts writing it; the people working on the routes do not pick their own numbers. Finding sequence numbers are written in order by each route's reviewer in that route's own file, so they cannot collide with other routes.
- Plans, decision records, and inbox items are not numbered. They use file names that describe the topic, so that people do not compete for the same sequence number.
