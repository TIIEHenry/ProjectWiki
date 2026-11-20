# Inbox

Both people and agents can record problems, documentation improvements, or points to confirm. Items go into subdirectories by type; this example shows `bug/` and `request/`, and creating all the empty directories in advance is not required. The names of the categories can be adjusted to the project.

One file for each item, with a short name that is unlikely to collide. The text gives the observation, the conjecture, the source, the basis of verification, and where the item goes. Accepting an item for investigation does not mean it is confirmed, and turning it into a task does not mean it is fixed. The authority to close an item follows the project's collaboration conventions.

For an item that has been handled, write where it went (the plan it became, the knowledge it was written back into, the item it duplicates, or the reason for doing nothing), change the status to `finished`, then preview with `python3 scripts/wiki/wiki.py archive <path> --root .` and add `--apply --expect <plan_sha256>` to archive it. Items that stay `open` for a long time get a reminder from `remind`.

The [question about counting combining characters](bug/combining-character-count.md) in this example is still to be verified and cannot be cited as an established defect.
