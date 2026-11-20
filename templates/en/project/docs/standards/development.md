# Development standards

Scope: [TODO: where this applies]. Status: current.

## Changes and verification

[TODO: the actual requirements for coding, compatibility, testing, building, integration, and release.]

Before a change, be clear about the goal, the constraints that apply, the entry to the implementation, and the way to verify. A small fix can reuse an existing task or the commit record; a new feature or a change in behavior updates the requirement entry and the tests. When the boundary is clear, there is no significant risk or contract change, and no multi-step collaboration or handoff is needed, no separate design or plan is created. An existing design description that has become untrue must still be updated; a change to a contract, to data, or to a permission boundary requires reviewing the matching design. Do not judge risk by the number of commits or of changed lines.

Choose the verification commands according to the scope of the change. Commands and the directories they run in are registered only in the `verify` field of `docs/wiki.json`, and any command with a nonzero exit code is a failure; this page states which commands each kind of change requires to pass and does not copy the list of commands. The template registers only the document check `check`; add the project's own test and build commands at adoption. The single entry for running them is:

```bash
python3 scripts/wiki/wiki.py verify --root .
```

| Scope of the change | Condition for passing |
|---|---|
| [TODO: for example the source code of a module] | [TODO: the matching `verify` command exits with code 0] |
| Documents only | The matching `check` in the `verify` output passes |

A known failure states the failing test or command, how to reproduce it, and its exit condition. "It was already red before the change" cannot be a reason to leave it unhandled indefinitely; when it is not handled for now, register it in the matching plan or in `dev/inbox/`.

When leaving a placeholder implementation, an empty branch, or a `TODO`, state the reason, the behavior affected, and when and by which piece of work it will be cleaned up.

## Collaboration

Stage only the files related to the current work. Do not revert, clean up, or stage the uncommitted changes of other people or other agents in order to get a clean working tree.

When merging or rebasing, do a real three-way merge of the files that both sides have changed, and do not take one side wholesale by default.

## Documents and work records

Current knowledge is maintained in place, and the history of ordinary revisions is left to Git. Consider archiving only when a whole page no longer has a current responsibility; plans, tasks, and raw verification material can be archived when they end, and the conclusions that still hold stay in current knowledge.

The roadmap maintains direction, order, and milestones and refers to specific plans; a plan maintains implementation steps, acceptance, and task progress. Reasons that explain only this fix go in the commit message; what keeps constraining later changes goes in the design or the related code comments; a trade-off with a lasting, important effect whose alternatives need explaining gets a decision record. Do not copy the running log of execution a second time.

Changes that users can perceive are written in `CHANGELOG.md`, in sections by version. It is a stable record for users and contains only changes in behavior and notes for upgrading, not the development process.

A verification record states the source or change snapshot that can be retrieved, the commands, the results, and the known failures. Commands and results are generated through the single `verify` entry, and the list of commands is registered only in `verify` of `docs/wiki.json`. A record proves only what it verified and does not automatically stand for the current main branch.

## Writing

Write the object, the rules, the basis, and the scope of application directly. Distinguish facts, conjectures, and to-dos. Avoid empty evaluation, internal abbreviations, translationese, and conclusions of passing that were never run.
