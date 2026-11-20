# Wiki checker

> English translation of [Wiki 检查工具](../README.md). The Chinese page is authoritative: if the two differ, the Chinese page applies.

This script checks registered document entries, references, page length, and document identity. It reports each problem with its location, and at commit time it reminds you to bring the documents up to date. It does not judge whether the design or business conclusions in a page are correct.

It needs Python 3.10 or newer and no third-party packages. Checking staged content and commit reminders also need Git.

During adoption, copy the whole `scripts/wiki/` directory into the target repository. The pages below are copied with the tool:

| When to read | Page |
|---|---|
| Running commands, installing the hooks | This page |
| The user asks to adopt ProjectWiki in a named project, or to finish an incomplete adoption | [Adoption skill](skills/adopt-projectwiki/SKILL.md) |
| Writing a status line, a verification line, a requirement entry, a review finding, or an inbox item | [Formats the checker reads](formats.md) |
| Filling in `docs/wiki.json`, or looking up what a rule means and how severe it is | [Configuration and rules](reference.md). That page is a register: search it by rule name or field name and read only the section you hit, for example `rg -n 'trace-no-test' scripts/wiki/en/reference.md` |
| Following the development workflow (the order from requirement to verification, updating documents when a decision changes, where troubleshooting experience goes, who does what in a review, when to archive) | [Development workflow rules](workflow.md) |
| Checking named documents against the implementation for accuracy and omissions | [Document review skill](skills/review-docs/SKILL.md) |
| Tidying documents in a named scope that are duplicated, no longer true, or finished | [Document organizing skill](skills/organize-docs/SKILL.md) |
| Recording development experience, troubleshooting techniques, or confirmed conclusions | [Knowledge capture skill](skills/capture-knowledge/SKILL.md) |
| The user asks to sync the documents and commit, or to make a closing commit | [Sync-docs-and-commit skill](skills/sync-docs-and-commit/SKILL.md) |

## Common commands

Run from the project root:

```bash
python3 scripts/wiki/wiki.py check --root .
python3 scripts/wiki/wiki.py check --root . --json
python3 scripts/wiki/wiki.py check --root . --staged
python3 scripts/wiki/wiki.py check --root . --require-repos
python3 scripts/wiki/wiki.py check-new docs/design/new-topic.md --root .
python3 scripts/wiki/wiki.py archive dev/plans/finished-work.md --root .
python3 scripts/wiki/wiki.py archive dev/plans/finished-work.md --root . --apply --expect <plan_sha256> --summary "one-line summary"
python3 scripts/wiki/wiki.py move dev/decisions/engine.md docs/decisions/engine.md --root .
python3 scripts/wiki/wiki.py move dev/decisions/engine.md docs/decisions/engine.md --root . --apply --expect <plan_sha256>
python3 scripts/wiki/wiki.py index --root .
python3 scripts/wiki/wiki.py index --root . --write
python3 scripts/wiki/wiki.py verify --root .
python3 scripts/wiki/wiki.py doctor --root .
python3 scripts/wiki/wiki.py remind --root .
python3 scripts/wiki/wiki.py remind --root . --all
python3 scripts/wiki/wiki.py remind --root . --staged --message-file .git/COMMIT_EDITMSG
python3 scripts/wiki/wiki.py baseline --root . > docs/wiki-baseline.json
python3 scripts/wiki/wiki.py export-okf --root . --out /tmp/project-okf
```

| Command | What it does |
|---|---|
| `check` | Checks structure, links, status lines, requirement tracing, and review records. `--staged` reads only the Git index (and the HEAD of each registered neighboring repository). `--require-repos` requires that every registered neighboring repository can be read |
| `check-new` | Checks the path, the name, and the matching history before a document is created |
| `archive` | Previews archiving a page or a whole directory; add `--apply --expect` to carry it out |
| `move` | Previews moving a document or a whole directory to another registered location and rewriting the links; add `--apply --expect` to carry it out |
| `index` | Prints the machine-readable index; `--write` writes it to the generated index named in the configuration, and `--check` compares the two |
| `verify` | Runs the verification commands registered in the configuration and prints a verification record |
| `doctor` | Checks the configuration, the search ignore rules, and the Git hooks |
| `remind` | Summarizes overdue document reviews and the status of plans; `--staged` runs at commit time; `--all` lists, page by page, the lifecycle reminders of files that existed before adoption |
| `baseline` | Prints the fingerprints of the current errors, to serve as the baseline of an old repository |
| `export-okf` | Exports an Open Knowledge Format bundle |

Only `archive --apply`, `move --apply`, `index --write`, and `export-okf` write files, and `verify` runs the commands registered in the configuration; the other commands only read. The tool does not stage or commit, and the Git hooks do not change files.

## Installing the Git hooks

`hooks/pre-commit` and `hooks/pre-merge-commit` run `check --staged`, and `hooks/commit-msg` runs `remind --staged`. When a merge has no conflicts, Git creates the merge commit itself and runs only pre-merge-commit (since Git 2.24), not pre-commit, so both must be installed. When the project has no other hooks, run this once in every clone:

```bash
git config core.hooksPath scripts/wiki/hooks
```

When the project already uses a hook manager such as husky or pre-commit, do not override its configuration. Add the first command below to the existing pre-commit and pre-merge-commit hooks, and the second to the commit-msg hook:

```bash
python3 scripts/wiki/wiki.py check --staged --root .
python3 scripts/wiki/wiki.py remind --staged --message-file "$1" --root .
```

By default the hooks take the top level of the repository as the project root. Set `WIKI_ROOT` when the project root is a subdirectory, and `PYTHON` when the interpreter is not called `python3`. `doctor` checks whether the three hooks exist in the hook directory currently in effect, are executable, and call the matching commands. It cannot inspect other hook managers and cannot prevent `git commit --no-verify`, so the agent rules must state that hooks are not to be skipped.

Running `remind` (without `--staged`) in a Git working tree also lists the hooks that are not in effect and reminds you to install them in one of the two ways above. While the configuration (`docs/wiki.json`) has not been committed, `check --staged` and `remind --staged` only report the warning `config-not-committed`, run no checks, and exit with code 0, so the configuration and the hooks can go into the same adoption commit.

While the configuration has no `remind`, commit-msg prints the warning `remind-not-configured` and the commit succeeds. For the thresholds and exit codes once it is configured, see [Documentation reminders at commit time](reference.md#documentation-reminders-at-commit-time).

## Exit codes

- `0`: the checks that ran passed, possibly with warnings.
- `1`: a check found definite errors.
- `2`: the input, the configuration, or a command made it impossible to complete the verification; the result is reported as incomplete. Hooks must treat both `1` and `2` as failure.

## Tests

The behavior tests of the tool are in `tests/` of the ProjectWiki repository and are not copied with the tool. Run them from the root of the ProjectWiki repository:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v
```

The tests build sample projects and Git indexes in temporary directories; they do not initialize or commit in the current repository.
