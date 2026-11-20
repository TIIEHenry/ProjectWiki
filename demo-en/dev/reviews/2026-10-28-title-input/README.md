# Review: boundaries of title input and consistency of the documents

Status: active. Scope: `notes/src/title.py` and the requirements, design, and maintenance guide related to titles. Baseline commit: the example project has no commit history of its own; verification is against the contents of the working tree on 2026-10-28. Owner: agent:kiro.

This is a teaching example that shows how a two-route review writes findings, verification, plans, and sign-off in one set of files. The verdicts below were all obtained by actually running against the example source code.

## Scope and method

Two questions are answered: whether abnormal input can get around the contract of "not empty, 1–60 code points"; and whether what the documents describe matches the implementation. The source code and the documents are read without modification, and minimal reproductions are run under Python 3.10. Storage and a user interface are out of scope.

## Routes

| Route | Scope | Method | Reviewer | File |
|---|---|---|---|---|
| r01 | Input boundaries: whitespace, invisible characters, and the length limit | Construct inputs and run `normalize_title` | agent:reviewer-a | [r01-input-boundary](r01-input-boundary.md) |
| r02 | Whether the documents match the implementation | Compare the requirements, design, maintenance guide, and source code sentence by sentence | agent:reviewer-b | [r02-doc-consistency](r02-doc-consistency.md) |

## Verification groups

agent:reviewer-b verifies r01, and agent:reviewer-a verifies r02. A checker must not be the author of the finding. All verification in the example is done by agents, and there is no verification by a person.

## Summary and sign-off

| ID | Verdict | Plan | Sign-off |
|---|---|---|---|
| r01-1 | narrowed | in the section | pending |
| r01-2 | rejected | none | not signed |
| r02-1 | known | points to an existing record | not signed |
| r02-2 | duplicate | see r01-1 | not signed |

## Conclusions and where they go

After r01-1 is signed off, change the module requirements and add the test as the plan says, then mark this review `finished`, and archive the whole directory to `archive/dev/reviews/2026-10-28-title-input/`.
