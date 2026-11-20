# Decision: titles are counted by Unicode code points

Status: adopted. Scope: title validation.

## Background

The title limit needs a way of counting that is repeatable. "Character" can mean a byte, a Unicode code point, or a user-perceived character, and the three must not be mixed.

## Alternatives

- Counting UTF-8 bytes: simple to implement, but common Chinese characters and English letters take different numbers of bytes, so the same limit would give the two kinds of titles different length limits; therefore not adopted.
- Counting user-perceived characters: closer to what the screen shows, but it requires implementing Unicode grapheme boundaries or bringing in a dependency. The first version provides only a local function on the standard library, so it is not adopted for now.

## Decision

The first version counts Unicode code points by the length of the Python string. It does not depend on third-party packages, and common Chinese characters and English letters share the same limit.

## Consequences

Combining characters and some emoji may consist of several code points, so the count does not equal the number of characters seen on screen. This is a current limitation, and callers follow the same counting rule. If counting by user-perceived characters is needed later, the dependencies and compatibility should be evaluated, and then the current contract revised.

The current rule is in the [module requirements](../requirements.md); only the trade-offs and the reasons are kept here, and implementation progress is recorded by plans.
