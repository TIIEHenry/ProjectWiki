# Title module

This module removes leading and trailing whitespace from a title, validates its length, and returns a title the caller can save. It does not save data.

| When to read | Text |
|---|---|
| Changing behavior, boundaries, or error handling | [Requirements](docs/requirements.md) |
| Changing responsibilities or the way characters are counted | [Design](docs/design.md) |
| Confirming the current implementation | [normalize_title](src/title.py) |
| Reproducing a boundary or verifying a change | [Tests](tests/test_title.py) |
| Troubleshooting an empty-title error, or an error on a title that seems to be within the limit | [Title maintenance guide](../docs/guides/maintenance.md) |

For the global constraints, see the [product and design principles](../docs/principles/product.md). A title over the limit must raise an error; silent truncation is not allowed.
