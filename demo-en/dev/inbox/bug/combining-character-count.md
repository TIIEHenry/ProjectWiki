# Question about counting combining characters in titles

Status: open. Source: example input, not a real user report.

## Observation

Some combining sequences that display as one character contain several Unicode code points. The module currently counts code points.

## Conjecture

Callers may expect counting by user-perceived characters. There is no evidence from callers, so it cannot be judged a defect directly.

## Basis of verification and where it goes

Not verified yet. First compare with the [current counting decision](../../../notes/docs/decisions/unicode-length.md), and then investigate what callers expect; only after a change is confirmed to be needed does it enter the requirements or an implementation plan.
