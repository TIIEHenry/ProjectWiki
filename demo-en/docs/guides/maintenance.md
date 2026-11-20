# Handling title validation failures

Verified: agent:kiro, 2026-10-28; agent:sol, 2026-11-02; agent:opus, 2026-11-06. Review by: 2027-04-28.

Scope: the title module. Status: current.

## The title does not look empty, but the empty-title error is returned

First check whether the input consists only of spaces, tabs, or newlines: if `repr(value)` shows only whitespace characters and `value.strip() == ""`, this is the cause. The module calls `str.strip()` before validating, see the [implementation](../../notes/src/title.py). That an empty title must raise an error is specified by [requirement NB-01](../../notes/docs/requirements.md#nb-01-validate-the-title-before-saving); do not work around the problem by relaxing this rule. Known limitation: `str.strip()` does not remove the zero-width space (U+200B), so a title containing only zero-width spaces passes validation, see [input boundary review r01-1](../../dev/reviews/2026-10-28-title-input/r01-input-boundary.md#r01-1-a-title-containing-only-zero-width-spaces-passes-validation).

## Fewer than 60 characters on screen, but still over the limit

The number of characters displayed and the number of code points can differ. First keep the original input, and run `print(len(value.strip()), [f"U+{ord(c):04X}" for c in value.strip()])` on the actual value; judge by the number of code points, not by what the screen shows. `repr(value)` can show tabs, newlines, and zero-width characters (such as `\u200d`) but cannot show combining marks, so look at the code points one by one. Run the sample below in `demo-en/` to check the counts for combining characters and emoji:

```bash
python3 - <<'PYTHON'
import sys
sys.path.insert(0, "notes/src")
from title import normalize_title

for unit in ("e\u0301", "\U0001F469\u200d\U0001F4BB"):
    print(repr(unit), [f"U+{ord(c):04X}" for c in unit])
    for count in (60 // len(unit), 60 // len(unit) + 1):
        value = "  " + unit * count + "  "
        title = value.strip()
        try:
            result = normalize_title(value)
            assert result == title
            outcome = "accepted"
        except ValueError as error:
            outcome = str(error)
        print(len(title), outcome)
PYTHON
```

Expected: `e\u0301` is two code points, accepted at length 60 and returning `title is too long` at 62; `👩‍💻` is three code points, accepted at length 60 and returning the same error at 63. If the number of code points of the actual input after leading and trailing whitespace is removed exceeds 60, this is the cause; when the error is still raised although the number of code points is within the limit, go on to check the value the caller passes in and where the exception comes from.

Basis: [normalize_title](../../notes/src/title.py) calls `strip()` first and then `len()`; the [acceptance tests](../../notes/tests/test_title.py) cover the boundary and over-limit cases for ordinary characters, while combining characters and emoji have only the diagnostic sample above and are not in the tests. The threshold of 60 and counting by code points are the contract of [module requirement NB-01](../../notes/docs/requirements.md#nb-01-validate-the-title-before-saving); why code points are counted is in the [counting decision](../../notes/docs/decisions/unicode-length.md).

When you run into another problem of "what is displayed does not match the validation result", you can troubleshoot in the same order: first confirm the preprocessing and the unit of measurement by the contract, then look at the actual input, and construct boundary cases around the threshold. This order is inferred from the mechanism of this case and has not been verified on other interfaces; for an interface that measures by bytes or by graphemes (the text unit close to a user-perceived character), the result of `len()` does not apply. Truncating by what is displayed violates [Preserve the intent of the input](../principles/product.md#p-input-preserve-the-intent-of-the-input); computing a separate length in the caller violates the requirement in the [title validation design](../../notes/docs/design.md) and the [counting decision](../../notes/docs/decisions/unicode-length.md) that callers follow the same counting rule. Whether to change to counting by graphemes is in the [question about counting combining characters](../../dev/inbox/bug/combining-character-count.md), which awaits triage.

## Verifying a fix

Run the module tests from `demo-en/`; the command is in the [development standard](../standards/development.md). Add a case that reproduces the actual problem, and record the object verified and the result.
