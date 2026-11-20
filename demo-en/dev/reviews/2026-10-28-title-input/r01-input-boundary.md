# r01 Input boundaries

Scope: whitespace, invisible characters, and the length limit. Reviewer: agent:reviewer-a. Checker: agent:reviewer-b.

## r01-1 A title containing only zero-width spaces passes validation

Status: narrowed.

**Observation** (Author: agent:reviewer-a, 2026-10-28)

`normalize_title("\u200b")` returns `'\u200b'` and raises no exception. Line 5 of [`title.py`](../../../notes/src/title.py) removes whitespace with `str.strip()`; the zero-width space (U+200B) is not a Unicode whitespace character, so it is not removed; the non-empty check on line 6 then passes.

**Conjecture**

A caller may save an invisible title, which shows as an empty line in a list.

**Verification**

| Round | Checker | Verdict | Basis |
|---|---|---|---|
| 1 | agent:reviewer-b | narrowed | The reproduction is confirmed: `normalize_title("\u200b")` returns `'\u200b'`. But NB-01.2 of the [module requirements](../../../notes/docs/requirements.md) only requires rejecting "input that is all whitespace"; a zero-width space is not whitespace, and the existing behavior meets the contract. The part that holds is that the requirements do not say how invisible characters are handled; it is not an implementation defect |

**Plan**

Do not change the code. State in the module requirements: invisible characters such as the zero-width space are handled as ordinary code points and are not treated as whitespace; whether to reject a title containing only invisible characters is decided once there is evidence from callers. At the same time, add a test that locks in the current behavior.

**Sign-off**

Pending.

## r01-2 A title of more than 60 code points is truncated

Status: rejected.

**Observation** (Author: agent:reviewer-a, 2026-10-28)

The suspicion is that only the first 60 code points are kept when the length is over the limit.

**Verification**

| Round | Checker | Verdict | Basis |
|---|---|---|---|
| 1 | agent:reviewer-b | rejected | Lines 8–9 of [`title.py`](../../../notes/src/title.py) raise `ValueError("title is too long")` when there are more than 60 code points, without truncating; running `normalize_title("x" * 61)` gives the same exception. The test `test_rejects_excess_instead_of_truncating` covers this |
