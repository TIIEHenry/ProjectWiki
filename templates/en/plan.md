# Implementation plan: [TODO: the specific work]

Status: [TODO: draft, active, blocked, or finished; all the values are in `scripts/wiki/en/formats.md`]. Scope: [TODO]. Owner: [TODO: `human:<name>` or `agent:<name>`; required when several people or agents work at the same time]. [When blocked, write `Reason: <what it is waiting for>.` at the end of the same line, for example `Status: blocked. Reason: waiting for the interface review of X.` Do not use `current`: that is a status of decision records; a completed plan is `finished`, and a replaced one is `superseded`.]

Requirements: [TODO: requirement IDs, for example APP-01; for maintenance work write `none` and give the reason in parentheses].

## Goal and basis

[TODO: the goal, the acceptance, the entries to the existing requirements and design, and the constraints that apply. State explicitly when the target specification is not implemented yet.]

## Steps and remaining work

[TODO: steps, dependencies, blockers, and the next step. Implementation progress is maintained here, and the roadmap only refers to this plan. The status is written only on the one line at the top. Before ending, write where each unfinished step goes, and then archive the whole page.]

## Open questions and pending trade-offs

[TODO: scope, dependencies, or trade-offs that are not settled yet, and what basis is needed to decide them. Write an ADR for an important, lasting decision once it is confirmed.]

## Workspace and integration

[TODO: the modules involved, the baseline commit, the branch or workspace, and which changes have been integrated.]

## Verification

[TODO: paste the output of `python3 scripts/wiki/wiki.py verify --root .`; do not write command results and hashes by hand. Then add what was checked by hand and the known failures. When nothing was run, say so explicitly. For each known failure, state how to reproduce it and its exit condition.]

## Completion and handoff

[TODO: whether the acceptance is met, where the stable conclusions were written back, and where the remaining items go. When there is no new stable knowledge, no new knowledge page is needed.]

After the work has ended and the handoff is complete, preview with `wiki.py archive`, then add `--apply --expect <plan_sha256>` to archive the plan to the matching original path under `archive/dev/plans/`. Add a decision record when an important trade-off needs a lasting explanation.
