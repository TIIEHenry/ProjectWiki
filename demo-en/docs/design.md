# Project design

Requirements: NB-01.

Scope: NoteBox. Status: current.

Title validation is provided by the [notes module](../notes/README.md). The caller passes in a string, and the module returns the title with leading and trailing whitespace removed, or raises `ValueError`. The caller is responsible for presenting the error to the user.

There is currently no cross-module caller. When a storage module is added in the future, the consumer should be registered here, and the entry of the new module should point to the title contract; a copy of the title rules must not be made and maintained separately.

The implementation, the boundary conditions, and the entry to the tests are in the [module design](../notes/docs/design.md). The trade-offs of character counting are in the [Unicode counting decision](../notes/docs/decisions/unicode-length.md).
