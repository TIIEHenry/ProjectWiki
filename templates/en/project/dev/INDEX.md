# Development entry

- Direction and order: [roadmap](roadmap.md).
- [TODO: when there is actual work, link the active plans or tasks, and say which one to read first when taking over.]

Status and execution records are maintained by the task concerned. When there is no active work, say so directly; do not fill in conclusions such as passed or integrated in advance. Records that have ended can be archived to their original relative path under the root `archive/dev/`.

This entry does not create a status page in advance. When there is an independent coordination purpose, decide whether one is needed by "Task records and status pages" in `scripts/wiki/en/workflow.md`, and avoid duplicating task records. When an execution suite has been adopted, keep the necessary records and fixed entries as its actual reading contract requires, and check the readers at the same time before adjusting them.

## Project binding for an execution suite (fill in when one is used)

Fill this in as described under "Sharing the development entry with an execution suite" in `scripts/wiki/en/workflow.md`; delete this section when no suite is used. Reuse the actual sources and do not create empty files; for a role that does not exist, write `none` or `not used`.

| Role | Actual source and who maintains it |
|---|---|
| Task source | [TODO: the entry to plans, requirements, issues, or submitted tasks, and how a task is identified] |
| Execution and coordination records | [TODO: the entry to the suite's rules, and the sources and maintainers of the dispatch, status, conflict scope, slot, and recovery records] |
| Inbox source | [TODO: an existing inbox or issue system, or none] |
| Verification entry | `python3 scripts/wiki/wiki.py verify --root .`; [TODO: where the results are saved in the original task] |
| Archiving convention | [TODO: the end conditions, the archive location, and how it is confirmed that readers no longer depend on the original location] |
