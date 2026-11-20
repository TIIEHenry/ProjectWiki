---
name: review-docs
description: >-
  In a business project that has adopted ProjectWiki, check the documents on a given topic against
  the code, the tests, and the configuration, and find what is outdated, contradictory, missing, or
  duplicated as an authority. Use for a documentation health check, a consistency check, or a
  formal documentation review; read-only by default with feedback in the conversation, and fixes
  under existing authorization.
---

# Checking project documents

> English translation of [核对项目文档](../../../skills/review-docs/SKILL.md). The Chinese page is authoritative: if the two differ, the Chinese page applies.

Work on the current business project. First read the project's `AGENTS.md` and the related entries, and determine the topic, the related documents, and the scope of the implementation; do not treat the ProjectWiki source repository that the skill comes from as the object of the review, and do not require going back to the source to read the rules.

The documentation workflow follows [Shared workflow and project adaptation](../../workflow.md#shared-workflow-and-project-adaptation); when checking the project's rules, judge exceptions and conflicts not yet migrated as that section describes.

## Establish the scope and the basis

Start from the page, module, or question the user names, and follow the related references and keywords to the authoritative text, the requirements, the design, the decisions, and the matching implementation. By default check only this scope; do not scan the whole repository or create an audit report because of a "documentation health check".

First identify the responsibility and the tense of each piece of material: requirements can describe goals not yet implemented, design can record accepted constraints, code and configuration describe the current implementation, and tests and run records prove only the conditions they actually cover. Archived material serves to explain history and cannot be taken directly as a current rule.

Check the project's existing authorizations, requirement statuses, and decisions, and avoid deciding mechanically who is right by how new something is or by its file type. When the implementation differs from the documents, first judge whether the implementation has deviated, the goal is not yet implemented, the text is outdated, or the evidence is insufficient; requirements or design must not be changed only because the code differs.

## Check item by item

- Against the behavior, interfaces, configuration defaults, limitations, and examples in the documents, locate the related code, tests, and configuration; check whether callers and providers follow the same convention.
- Look for current descriptions that contradict each other, for missing conditions of application, and for cases where the same rule is maintained independently in several places. A repeated reference is not a duplicate authority; a deliberately kept difference between the goal and the current state is not a contradiction either.
- For each finding, record the source path and line number so that it can be checked again, the specific difference, the effect on readers or on behavior, and which place is proposed to be changed and why. When sources conflict or a decision is lacking, state the point to be confirmed; do not write a conjecture up as a confirmed problem.

By default, list the findings in the conversation by impact, and state the scope actually read, the evidence, and the items not checked. When nothing is found, say only that no problem was found within that scope; do not claim that the whole project is consistent.

## Formal review and fixes

When the user explicitly asks for a formal review, organize the records by the [review rules](../../workflow.md#reviews); fill in the fields of a finding as described under [Review findings](../../formats.md#review-findings). Formal verification must be done by a person or agent who is not the author; the author reading the text again does not count as independent verification, and a sign-off cannot be filled in on someone else's behalf. When independent verification cannot be arranged, keep the pending status and report the limitation.

When the user has authorized fixes, update the authoritative text and the affected references within the authorized scope, without asking for confirmation again. Where a goal or a decision changes, proceed by the [rules for syncing documents](../../workflow.md#updating-documents-when-a-decision-or-design-changes); for a product decision that there is no authorization to change, only report the difference and a recommendation.

Keep unrelated uncommitted changes; by default, do not change source code, create commits, or push. When an existing request authorizes related operations, keep to its scope.

## Verification and feedback

Structural checks can only verify tool rules such as links and formats and cannot replace the semantic checking above. A read-only check does not force tests to be added or a full verification to be run; when a real test is needed, run only the related checks within the authorized scope, and consider side effects such as builds and generated files. When documents are modified, choose the matching checks from the current project's verification entry; the commands are in the [tool entry](../../README.md#common-commands). When a verification record needs to be saved, use the actual output of `verify`.

Distinguish static reading, tests actually executed, and manual checks. Do not call behavior verified when no test was run, and do not fabricate requirement evidence or a human sign-off. Report the findings, the places fixed, the actual input and scope of the checks, the results, and the remaining limitations; no separate report is needed.
