# Candidate plan: evaluating single-line titles

Status: proposed. Scope: the notes module. Not yet approved as a current requirement.

Requirements: NB-02 (proposed).

## Goal and points to confirm

Evaluate whether internal newlines in a title should be rejected. The current [module requirements](../../notes/docs/requirements.md) allow internal newlines, and this plan cannot be taken as a contract in effect.

## Implementation steps

1. Confirm the calling scenarios, and distinguish internal newlines from leading and trailing whitespace.
2. If the decision is to change the behavior, first make compatibility clear, and revise the requirements and the design.
3. Change the implementation, add boundary cases for newlines, and run the module tests.

## Acceptance and records

The plan becomes active only after the scope of the new behavior and its compatibility are clear. The object verified, the commands, the results, and the known failures are recorded in this plan; at present there is no implementation or verification conclusion.

If it only continues an existing trade-off, no new ADR is created; if it brings in an important, lasting compatibility trade-off, record a decision then. The roadmap only refers to this plan and does not repeat these steps.
