# Title validation design

Requirements: NB-01.

Scope: the notes module. Status: current.

`normalize_title` is in [src/title.py](../src/title.py). The function first calls `strip()`, and then checks that the title is not empty and is within the limit of 60 code points. It uses no files, network, or global state.

The function is currently the only public entry. After catching `ValueError`, the caller is responsible for telling the user, and should not reimplement a separate truncation or count outside the module.

The reasons for counting code points and its limitations are in the [character counting decision](decisions/unicode-length.md). For the requirements, see the [module requirements](requirements.md); for verification, see the [tests](../tests/test_title.py).
