# Development standard

Scope: NoteBox. Status: current.

Before a change, make clear the goal, the constraints that apply, where the implementation is, and how to verify. An ordinary local fix can write the basis and the result in the original task or the commit record; new behavior updates the matching requirements and tests. When the boundary is clear, there is no significant risk or contract change, and no multi-step collaboration or handoff is needed, no separate design or plan is created; contract changes such as title counting or the order of validation still require the relevant design to be updated. Do not judge risk by the number of commits or of changed lines.

This project uses Python 3.10+ and the standard library. The external behavior of the title module is specified by the [module requirements](../../notes/docs/requirements.md), and tests cannot change the contract on their own.

The verification commands are registered only in `verify` of [`docs/wiki.json`](../wiki.json); at present they are the unit tests of `notes/tests`. Run in the project root:

```sh
python3 scripts/wiki/wiki.py verify --root .
```

The verification record of a plan uses its output directly: the output states the Git HEAD, the number of uncommitted files, the hashes of the files under test, and the result of each command. What was checked by hand and the known limitations are written after it. Adding the evidence file itself does not change the source code that was verified.

The [roadmap](../../dev/roadmap.md) records direction and order; an implementation plan records the steps and the acceptance of one piece of work, and specific work is found from the [development entry](../../dev/INDEX.md). A reason that explains only this fix goes in the commit message; what goes on constraining later changes goes in the design or in the relevant code comments; a trade-off with important long-term impact whose alternatives need explaining gets an ADR. Task progress is maintained only in the matching task or plan; the roadmap references it and does not copy the execution log.

The text uses direct, specific English. Distinguish facts, conjectures, and to-dos; do not write an expectation as a result that has already been verified.
