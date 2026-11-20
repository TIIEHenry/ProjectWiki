# r02 Consistency between documents and implementation

Scope: the module requirements, the module design, the fault maintenance guide, and the source code. Reviewer: agent:reviewer-b. Checker: agent:reviewer-a.

## r02-1 A title of fewer than 60 characters on screen can also be judged too long

Status: known.

**Observation** (Author: agent:reviewer-b, 2026-10-28)

`len("e\u0301")` is 2: a letter with an accent is one character on screen but two when counted by code points. The maintenance guide and the requirements both describe the limit in code points.

**Verification**

| Round | Checker | Verdict | Basis |
|---|---|---|---|
| 1 | agent:reviewer-a | known | This is the limitation stated in the [character counting decision](../../../notes/docs/decisions/unicode-length.md), and an [inbox item](../../inbox/bug/combining-character-count.md) is tracking whether callers need counting by user-perceived characters. Not reopened |

## r02-2 The maintenance guide does not mention titles containing only invisible characters

Status: duplicate.

**Observation** (Author: agent:reviewer-b, 2026-10-28)

The [fault maintenance guide](../../../docs/guides/maintenance.md) discusses only overlong titles and combining characters, and does not say that a title made up of zero-width spaces is accepted.

**Verification**

| Round | Checker | Verdict | Basis |
|---|---|---|---|
| 1 | agent:reviewer-a | duplicate | The underlying problem is the same as r01-1. After the plan of r01-1 has changed the module requirements, the maintenance guide is brought in line; it is not handled separately |
