# Title validation requirements

Scope: the notes module. Status: current.

Each requirement begins with its ID, the first line below it is the status, and the acceptance criteria are listed one by one, each with a sub-ID. Tests write the acceptance ID in their descriptive text, and design pages cite the requirement with "Requirements:".

### NB-01 Validate the title before saving

Status: verified.

The input is a Python string, and the output is the string with leading and trailing whitespace removed.

- NB-01.1 After leading and trailing whitespace is removed, the rest of the content stays unchanged, including internal newlines.
- NB-01.2 Empty input or input that is all whitespace raises `ValueError("title is empty")`.
- NB-01.3 Exactly 60 Unicode code points are accepted.
- NB-01.4 More than 60 code points raise `ValueError("title is too long")`, without truncation.

Evidence: [acceptance tests](../tests/test_title.py), run `python3 -m unittest discover -s notes/tests -v`.

### NB-02 Titles allow only one line

Status: proposed.

Whether to reject internal newlines has not been decided; for the evaluation work, see the [roadmap](../../dev/roadmap.md). Until this entry becomes accepted, NB-01.1 remains in effect and internal newlines are kept.

For the global principle, see [P-INPUT](../../docs/principles/product.md#p-input-preserve-the-intent-of-the-input).
