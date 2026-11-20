# Development entry

| When to read | Record |
|---|---|
| Learning the direction and order of later work | [Roadmap](roadmap.md) |
| Evaluating whether titles should be limited to a single line | [Implementation plan](plans/multiline-title.md) |
| Submitting a problem that has not been verified yet | [Inbox](inbox/README.md) |
| Seeing how a review records findings, verification, and plans | [Title input review](reviews/2026-10-28-title-input/README.md) |

The finished first validation plan is in the [archive](../archive/dev/plans/initial-title-validation.md), and all historical records are in the [history index](../archive/INDEX.md). It cannot override the current requirements; whether history needs to be read depends on the task.

The plan and the module entry of this example are enough to continue the work, and there are no coordination matters that need a separate status page. When continuing, read the plan directly and check the current status, the changes in the source code, and the object verified; a status page is not created automatically because commits or modules are added. When a separate coordination view is needed, decide by "Task records and status pages" in `scripts/wiki/en/workflow.md`. This example has not adopted an execution suite; what follows only demonstrates the role binding of the existing records and does not prove that dispatch or recovery by a suite has been run.

## Example of a project binding

| Role | Actual source and responsibility in this example |
|---|---|
| Task source | The [multiline title plan](plans/multiline-title.md); the task is identified by its path; the acceptance criteria are in the requirements the plan cites |
| Execution and coordination records | No execution suite, concurrency slots, or separate recovery records; whoever continues the work maintains the steps and the verification record in the original plan |
| Inbox source | The [inbox](inbox/README.md); after triage, the original item links to the plan or states where else it went |
| Verification entry | Run `python3 scripts/wiki/wiki.py verify --root .` in the root directory of this example; the result is saved in the original plan |
| Archiving convention | After the plan is completed or canceled and the remaining items have somewhere to go, archive it to `archive/dev/plans/` by `scripts/wiki/en/workflow.md`; for the entry to history, see the top of this page |

If an execution suite is to reuse this example, it should find the original plan and the inbox from this table, and then declare the execution records it actually maintains; it does not copy the plan steps or the text of the requirements. Check how the suite reads and its end conditions by "Sharing the development entry with an execution suite" in `scripts/wiki/en/workflow.md`.
