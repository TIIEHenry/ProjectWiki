# Configuration and rules of the wiki checker

> English translation of [Wiki 检查工具的配置与规则](../reference.md). The Chinese page is authoritative: if the two differ, the Chinese page applies.

This page lists the configuration fields, the meaning and severity of every rule, and the detailed behavior of each command. It is a register and grows as rules are added: search it by rule name or field name and read only the section you hit, for example `rg -n 'trace-no-test' scripts/wiki/en/reference.md`; do not load the whole page. Common commands and installation steps are in the [tool entry](README.md); the fixed formats, such as status lines, verification lines, and requirement entries, are in [Formats the checker reads](formats.md).

## Command options

`--root` selects the project root; by default the configuration is `docs/wiki.json` under that directory. `--config` names another configuration path, relative to the root. Every path in the configuration is relative to the project root.

`--json` prints a structured report; `baseline`, and `index` without options, print JSON to standard output anyway. When the configuration declares `generated_index`, `index --check` compares that file with the current index result, and reports `index-outdated` and fails when the file is missing or differs. `index --write` writes the result to the file; when the content has not changed it leaves the file alone, and `written` in the report says whether the file was changed. The same input produces the same index, and no run date is added.

Only `archive --apply`, `index --write`, and `export-okf` write files, and `verify` runs the commands registered in the configuration; the other commands only read.

## Configuration

A minimal configuration contains `version`, `roots`, and `entrypoints`:

```json
{
  "version": 1,
  "project_name": "Example",
  "roots": [
    {"path": "docs", "role": "knowledge"},
    {"path": "dev", "role": "process"},
    {"path": "archive", "role": "archive"}
  ],
  "entrypoints": ["README.md", "AGENTS.md", "docs/INDEX.md", "dev/INDEX.md"],
  "modules": [
    {"name": "notes", "path": "notes", "entry": "notes/README.md", "docs": "notes/docs"}
  ],
  "pages": [
    {"path": "AGENTS.md", "role": "entry", "max_chars": 8000}
  ],
  "exclude": ["tmp/**", "**/__pycache__/**"]
}
```

`modules`, `pages`, and `exclude` can be omitted. The 8000 in the example is a demonstration value and should be adjusted to the project's actual tasks. A complete example is `demo-en/docs/wiki.json` of the NoteBox reference project in the ProjectWiki repository (`demo/docs/wiki.json` is the Chinese original).

All fields:

| Field | Meaning | Described in |
|---|---|---|
| `version` | Configuration version, currently `1` | |
| `project_name` | Display name of the project | |
| `roots` | Document roots and their roles: knowledge, process, archive | This section |
| `archive_root` | Optional. The main archive target; it must be a registered directory with the archive role | End of [Baseline of existing problems](#baseline-of-existing-problems) |
| `modules` | Module name, source root, and entry, with an optional module `docs` | This section |
| `entrypoints` | Entry files that must exist | This section |
| `pages` | Page role, character budget, ID, or scope | This section |
| `exclude` | Directory or file patterns that the current project does not check | This section |
| `orphan_ignore` | Optional. Paths that are not checked for having an entry | [Checks and their limits](#checks-and-their-limits) |
| `status_values` | Optional. The project's own status values and their classes | This section |
| `repos` | Optional. Registers the neighboring repositories that links point into | [Neighboring repositories and submodules](#neighboring-repositories-and-submodules) |
| `status_frontmatter` | Optional. For a project that already has frontmatter, the name of the status field, for example `"status"` | This section |
| `adopted_at` | Optional. The commit at adoption; files that existed then are not subject to the rules that apply only to new files | [Adoption starting point](#adoption-starting-point) |
| `requirements` | Optional. Where the requirements files and the test files are; an array of groups when there are several ID spaces | [Requirement tracing](#requirement-tracing) |
| `verification` | Optional. Paths that require a review-by date or a human check | [Verification records and review-by dates](#verification-records-and-review-by-dates) |
| `reconcile` | Optional. Reconciles lists of names between documents and code | [Reconciling documents with code](#reconciling-documents-with-code) |
| `reviews` | Optional. Where the entry READMEs of reviews are | [Review records](#review-records) |
| `dir_budgets` | Optional. Maps directory patterns to a maximum number of files | [File-count budgets for directories](#file-count-budgets-for-directories) |
| `size_limits` | Optional. The default length limits for pages and lines, and the patterns to ignore | [Page size](#page-size) |
| `baseline` | Optional. Path of the JSON baseline of existing problems | [Baseline of existing problems](#baseline-of-existing-problems) |
| `generated_index` | Optional. Path of the generated JSON index | [Command options](#command-options) |
| `archive_index` | Optional. The history index to which `archive --apply --summary` appends a record | [Archiving: preview first, then apply](#archiving-preview-first-then-apply) |
| `verify` | Optional. Verification commands and the files whose hashes are recorded | [Verification record](#verification-record) |
| `remind` | Optional. Documentation reminders at commit time | [Documentation reminders at commit time](#documentation-reminders-at-commit-time) |

The configuration is parsed as complete JSON. A misspelled field at the top level, or in `verification`, `requirements`, `verify` (including each command), `reconcile`, or `remind` (including `watch` entries, `threshold`, and `block_at`), is reported as incomplete; the tool does not fall back to a default.

- `roots` registers the knowledge, process, and history directories. The history directory can be created at the first archive; the other registered directories and the required entries must exist.
- `modules` registers each module's path and entry. A small module can have only a README and omit the `docs` field; register `docs` once the module has a documentation directory. The tool finds `docs/` directories that are neither registered nor explicitly excluded, so a separate front end or a module in another language needs registering too.
- `pages` gives particular files a role and a character budget. The optional `id` and `scope` are used to check identity conflicts between current documents. When scope is omitted, a page inside a module belongs to the module and any other page to the project; historical versions can keep the same logical ID. The exemption for history is decided by the path under a registered history root: a current file cannot lower its level of checking merely by setting its page role to `archive`.
- `exclude` controls the scope of the checks. It and `.ignore`, which serves everyday searching, are two sets of rules with different purposes. Do not use the check exclusions to exclude the whole history directory, or links into history can no longer be verified.
- When a link points to a path in `exclude`, what matters is whether that path has any file in the snapshot being checked. If it has, the target is checked for existence as usual. If it has none (a directory checked out only on this machine, build output, an excluded symbolic link), the target cannot be verified: no broken link is reported, `coverage.excluded_links` in the report gives the number of unchecked links for each path, and the text output shows a `Links not checked` line. Working-tree checks and staged checks give the same result on this point.
- A working-tree check automatically skips untracked files and directories that Git ignores, such as Gradle's `build/` and `.gradle/`; such directories need not be written into `exclude` as well. Tracked files are not affected by ignore rules. A link to an ignored untracked file is treated as a missing target, because other clones do not have the file; the message of a working-tree check says that the file exists only on this machine. To keep such a link on purpose, write its directory into `exclude`, and it is counted as in the previous item. When the project root is not inside a Git working tree, when there is no Git, or when the project root itself is ignored, the tool reads all files and `coverage.git_ignored` in the report says `not-applied`; when files were skipped it says `git-ignored-skipped`, and for a staged check it says `index`.
- The checks do not enter directories that are symbolic links and do not read symbolic links that point outside the project root. A staged check reads no symbolic link at all, because the index holds only the link itself. When a document is itself a symbolic link, one `unreadable` is reported for each such document and the other documents are checked as usual. When a link target or a registered required path lies behind a symbolic-link directory, the `broken-link` or `missing-entry` message names the symbolic link. There are two remedies. If the content is maintained elsewhere, write the symbolic link into `exclude` (its own path for a document, `path/**` for a directory); links to it and to what lies behind it are then counted in `coverage.excluded_links` by the rule above. If the content belongs to this repository, replace the link with an ordinary file.

Document text does not require frontmatter, and operations guides are free to use checkboxes.

Plans and decision records write their status on the first line below the level-one title. Status values fall into the classes draft, active, blocked, current, finished, superseded, retired, and open; the format and the default values are under [status lines](formats.md#status-lines-of-plans-decision-records-and-inbox-items). A project adds its own status values with `status_values`, for example `"status_values": {"reviewing": "draft"}`. By default plans are `dev/plans/*` together with `dev/reviews/*/README.md` and `dev/reviews/*/plan-*.md` of review directories, decision records are `docs/decisions/*` and `*/docs/decisions/*`, and inbox items are `dev/inbox/*/*.md`; these can be changed with `remind.plans`, `remind.decisions`, and `remind.inbox`.

- When an entry page links to a document whose status is superseded or retired, the error `links-replaced-document` is reported; when another current page does so, it is only a warning. Decision records citing one another do not count, documents in archive directories are treated as history, and pages with the role `generated` (for example an index page produced by a tool) get no reminder.
- A plan or decision record without a status line gets the warning `status-missing`; a status value that is not recognized gets the warning `status-unknown`.
- A plan whose status is `blocked` but whose status line gives no reason gets the warning `plan-blocked-no-reason`. A blocked plan must say what it is waiting for; the format is under [Reason](formats.md#status-lines-of-plans-decision-records-and-inbox-items): `Status: blocked. Reason: waiting for the interface review of X.` Old files from before the adoption starting point are not reported, as with `plan-no-status`.
- A plan whose status is `current` gets the warning `plan-status-current`. `current` is a status for decision records, and a plan describes work that ends: write finished work as `finished` and replaced work as `superseded`. When the work has landed and the page still describes current behavior, write the lasting content back into `docs/` and then archive the plan. A frontmatter value that `status_values` maps to current is reported too. Old files from before the adoption starting point are not reported.
- A project that already records status in frontmatter can register the field name, for example `"status_frontmatter": "status"`. After that, a page without a status line takes its status from this field. When both are written the status line wins, and the warning `status-mismatch` is given if the classes differ; a field value that is not recognized also gets the warning `status-unknown`. The field value and the status line share the `status_values` mapping, for example `{"accepted": "current", "in_progress": "active"}`. The tool reads only this one top-level frontmatter field and no other. Without the registration the tool does not read frontmatter.
- The status line of a plan can name an owner. If one is written without the `human:` or `agent:` prefix, the error `owner-format` is reported. `remind` lists the active and blocked plans with their owners, which shows who is changing what when several agents work at the same time; for blocked plans it lists the reason as well.

### Requirement tracing

With `"requirements": {"files": ["docs/requirements/*.md"], "tests": ["tests/*"]}` configured, `check` reads requirement entries from the files that match `files`; the format is under [Requirement entries](formats.md#requirement-entries). `tests` defaults to `tests/*` and `*/tests/*`, and any file that matches is scanned for IDs. Without `requirements` in the configuration this group of checks is not run.

By default a requirement ID matches the regular expression `[A-Z][A-Z0-9]*-\d+`. When existing requirements use other IDs, give their format in `id_pattern`: for example `"id_pattern": "REQ-[A-Z]+-\\d{3}"` matches `REQ-AUTH-001`, and `"FR-\\d+(?:\\.\\d+)*"` matches `FR-1.2`. An acceptance ID is always the requirement ID followed by `.` and a number, for example `REQ-AUTH-001.1` or `FR-1.2.1`. An invalid expression, or one that can match the empty string, is reported as incomplete.

When one repository has several sets of requirements, each numbered on its own, for example an engine and a terminal client that both start from `PRD-001`, write `requirements` as an array with one ID space for each group:

```json
"requirements": [
  {"name": "engine", "files": ["docs/product/requirements.md"], "docs": ["docs/*", "core/*"], "tests": ["core/src/test/*"]},
  {"name": "tui", "files": ["tui/docs/product/requirements.md"], "docs": ["tui/*"], "tests": ["tui/test/*"]}
]
```

Each group must have a unique `name` and can have its own `id_pattern`. Duplicate IDs are checked only within a group. `docs` lists the documents whose references belong to the group; the group's own requirements files always count, and when `docs` is omitted all documents count. Tests are scanned only by the group's own `tests`, so state where each group's tests are: the default `*/tests/*` would count the other groups' tests as well. A requirements file that matches the `files` of two groups is reported as incomplete. A project that needs no groups keeps writing a single object.

| Rule | Severity | Meaning |
|---|---|---|
| `trace-unknown-ref` | Error | A current document or a test refers to a requirement ID or acceptance ID that does not exist |
| `trace-duplicate-id` | Error | The same requirement ID is defined twice |
| `trace-status-missing` | Error | A requirement has no recognizable status line below it |
| `trace-acceptance-id` | Error | The prefix of an acceptance sub-ID does not match the requirement it is under |
| `trace-no-acceptance` | Warning | A requirement in the accepted status or later has no acceptance items |
| `trace-no-test` | Warning | An implemented or verified requirement has an acceptance item that is not marked `(manual)` and that no test refers to |
| `trace-manual-evidence` | Warning | An acceptance item is marked `(manual)` but has no matching `Acceptance check: <ID>, agent:<name>, YYYY-MM-DD.` record |
| `trace-check-not-manual` | Warning | An acceptance check record is written under an acceptance item that is not marked `(manual)`; the record cannot take the place of a test |
| `trace-no-evidence` | Warning | A verified requirement has no `Evidence:` line with a link |
| `trace-plan-scope` | Warning | A plan that has not ended has no `Requirements:` line; maintenance work writes `Requirements: none (<reason>)`. Plans in review directories are not checked |
| `trace-requirements-location` | Warning | The root that holds a requirements file has the process or archive role; requirements are current knowledge until they are retired and belong under a knowledge root |
| `trace-all-manual` | Warning | An implemented or verified requirement with at least 2 acceptance items has only manual verification for all of them, and no test refers to any |

The prefix of an ID is the part of a defined ID before its first digit (the prefix of `PW-11` is `PW-`). Only text with the same prefix is taken as a reference, so `UTF-8` and `SHA-256` are not reported by mistake. Every reference that exists in documents and process records is checked for an existing ID. The tool does not require every requirement to have a design reference or a plan: a light change can keep only the requirement entry and the tests, and no exemption field is needed. Whether a design and a plan are needed is judged by the impact of the change. The tool only confirms that the ID is referred to; it does not judge whether the test really covers the acceptance criterion.

Requirements are current knowledge until they are retired. When a file matched by `requirements.files` is under a root whose role is process or archive, `check` reports `trace-requirements-location` and advises moving the file under a knowledge root with the `move` command. Requirements files that were already in a process or archive root before the adoption starting point are reported as well.

`coverage.requirements` of `check --json` gives the distribution of evidence for each requirements group (the group is named `default` when there are no groups): `requirements` is the number of requirements, `acceptance` the number of acceptance items, `tested` the number of acceptance items that at least one test refers to, `manual` the number that have only manual verification and no test, `untested` the number that have neither, and `status` the number of requirements in each status. The text output adds a line to the summary, for example `requirements[default]: 13 requirements, 55 acceptance items: 40 with tests, 3 manual only, 12 untested`. When a requirement is implemented or verified, has at least 2 acceptance items, and all of them have only manual verification and no test, `check` reports `trace-all-manual`: manual verification is only for items that no command can prove, so write tests first for those that can be tested and mark the rest as manual.

### Verification records and review-by dates

A knowledge page can carry a verification line and a review-by date below the level-one title and before the first level-two heading; the format is under [Verification line and review-by date](formats.md#verification-line-and-review-by-date).

| Rule | Command | Severity | Meaning |
|---|---|---|---|
| `verify-format` | check | Error | A verification entry is not "a checker with the `human:` or `agent:` prefix, YYYY-MM-DD"; or the review-by date is not a valid date |
| `verify-review-before-check` | check | Error | The review-by date is earlier than the most recent check |
| `review-by-missing` | check | Warning | The path matches `verification.review_by_required` but the page has no review-by date |
| `verify-no-human` | check | Warning | The path matches `verification.human_required` and the verification line has no `human:` checker |
| `review-actor-format` | check | Error | A checker in a review verification table is written with a prefix that is not `human:` or `agent:` |
| `review-no-human-check` | check | Warning | The path of a review finding requires a human check, and the verification table has no `human:` checker |
| `knowledge-review-due` | remind | Warning | The review-by date has been reached |
| `verify-date-future` | remind | Warning | A verification date is later than today |

Example configuration: `"verification": {"review_by_required": ["docs/guides/*"], "human_required": ["docs/requirements/*", "dev/reviews/*"]}`. `check` only checks that the `human:` prefix is written correctly and cannot confirm that a person really wrote it. When a staged change adds a `human:` name, `remind --staged` gives the `[user]` reminder `human-claim-added`; see [Documentation reminders at commit time](#documentation-reminders-at-commit-time). For pages that have a verification line, `index` outputs `trust` (`agent-checked` or `human-checked`), `verified`, and `review_by`.

### Exporting OKF

```bash
python3 scripts/wiki/wiki.py export-okf --root . --out /tmp/project-okf
```

This copies the current knowledge documents to `--out`, keeping their relative paths, and adds Open Knowledge Format v0.2 frontmatter at the top of each: `type` (inferred from the directory, for example Decision, Requirements, Guide, Design), `title`, `description`, `status` (stable for current, draft for draft, deprecated for superseded or retired; synonymous statuses that the project configures in `status_values` are treated by their class), `verified`, `stale_after`, and `okf_source`, which records the original path.

The target directory must be outside the project root, and must be empty or not exist; otherwise no file is written and 2 is returned. Process directories (`dev/`) and archive directories are not exported, non-Markdown files are not copied, and links to documents that are not exported are left as they are. A document that already has frontmatter is copied unchanged and reported as `okf-existing-frontmatter`. A file named `index.md` or `log.md` is reported as `okf-reserved-name`: OKF treats these two names as the index page and the log, and other tools will read the files that way after the export.

### Reconciling documents with code

For content that can be listed as a set, such as rule names, configuration items, and command arguments, `check` can compare the two lists, the one in the documents and the one in the code:

```json
"reconcile": [
  {
    "name": "rules",
    "docs": ["scripts/wiki/README.md", "scripts/wiki/reference.md"],
    "doc_pattern": "`([a-z][a-z0-9]*(?:-[a-z0-9]+)+)`",
    "code": ["scripts/wiki/wiki.py"],
    "code_pattern": "Finding\\(\\s*\"([a-z][a-z0-9]*(?:-[a-z0-9]+)+)\"",
    "ignore": ["check-new", "working-tree"]
  }
]
```

`docs` and `code` are path patterns. `doc_pattern` and `code_pattern` are Python regular expressions, matched over the whole file in multiline mode; with one capture group the text of the group is taken, and with none the whole match. Names in `ignore` are compared on neither side; they exclude words in the documents that happen to fit the format but do not belong to the list. The configuration above is the one the ProjectWiki repository uses to check its own rules: every hyphenated name written in backticks in the tool documentation is reconciled with the rule names reported in `wiki.py`, so rule names without a hyphen (for example `unreadable`) are outside the reconciliation.

| Rule | Severity | Meaning |
|---|---|---|
| `reconcile-missing-in-doc` | Error | A name appears in the code but not in the documents |
| `reconcile-missing-in-code` | Error | A name is written in the documents but is no longer in the code |
| `reconcile-empty` | Error | One side matched no file or no name, usually because a path or a regular expression is wrong |

The regular expressions only match text and do not understand the structure of code: commented-out code and the same word inside a string are counted too. It is best to give the list a fixed format, for example always the first column of a table, so that the regular expression can be stricter.

### Review records

`reviews` configures the patterns that match review entries; the default is `["dev/reviews/*/README.md"]`. The patterns identify existing files and cannot be used directly as the path of a new one; where a new review goes is decided as described under [project adaptation](workflow.md#shared-workflow-and-project-adaptation). The directory of each matched README counts as one review: every Markdown file in the directory other than `plan-*.md` is a route file, and findings can also be written directly in the README itself. The format is under [Review findings](formats.md#review-findings).

The tool treats a level-two heading that begins with a finding ID (for example `## r01-1 …`) as one finding, and reads the status on the first line below it and the `Verification` table:

| Rule | Severity | Meaning |
|---|---|---|
| `review-duplicate-id` | Error | The same ID appears twice in this review |
| `review-verdict-missing` | Error | A finding has no recognizable verdict line below it (pending, confirmed, narrowed, rejected, known, duplicate) |
| `review-duplicate-target` | Error | A finding is judged a duplicate without naming another ID that exists in this review |
| `review-known-target` | Error | A finding is judged known without a link to the existing plan, gap, or decision |
| `review-plan-unknown-id` | Error | The `Covers:` line of a `plan-*.md` lists an ID that does not exist |
| `review-unverified` | Warning | The finding is still pending |
| `review-check-missing` | Warning | There is a verdict, but the verification table has no data row |
| `review-no-independent-check` | Warning | The checker in every row of the verification table is the author (recognized by `Author: <name>`) |
| `review-verdict-mismatch` | Warning | The status line and the last row of the verification table give different verdicts |
| `review-plan-missing` | Warning | A confirmed or narrowed finding has neither a `Plan` section nor a `plan-*.md` that covers it |
| `review-plan-scope` | Warning | A `plan-*.md` has no `Covers:` line |

Reviews in archive directories are no longer checked. The tool does not judge whether a verdict is correct or whether its basis is sufficient.

### File-count budgets for directories

`dir_budgets` maps directory patterns to a maximum number of files, for example `{"dev/*": 50, "dev/plans": 30, "dev/inbox/*": 30, "dev/reviews/*": 20}`. When the registered Markdown files placed directly in a directory exceed the limit, the warning `dir-budget` is reported, as a reminder to merge content into sections or to archive what has ended. Without the configuration nothing is checked. The configurations of the project template and of the reference project register the four entries above by default; among them `dev/*` gives the other subdirectories of `dev/` (such as roadmap, reports, and iterations) a fallback budget.

A directory can match several patterns at once. The most specific pattern then decides: the one with the longest pattern string applies, and the directory is reported once, against that limit only. For example, `dev/plans` matches both `dev/*` and `dev/plans` and is counted against the limit of the longer `dev/plans`.

### Baseline of existing problems

An old repository often reports a great many errors at once when it adopts the tool. After configuring `"baseline": "docs/wiki-baseline.json"`:

```bash
python3 scripts/wiki/wiki.py baseline --root . > docs/wiki-baseline.json
```

`baseline` prints the fingerprints of all current errors to standard output, and the operator writes them to the file. A fingerprint consists of the rule, the file, and the link target, without a line number, so inserting text into the same file does not turn an old problem into a new one.

After that, `check` no longer fails for errors that are in the baseline, and `baseline_accepted` in the report says how many were let through; errors that are not in the baseline fail as usual. When a problem in the baseline has been fixed, `baseline-stale` is reported with advice to regenerate the baseline, so that the baseline only shrinks and never grows. When a staged check finds that the committed baseline has more entries than HEAD, it reports `baseline-grown` at the `[user]` level: a new problem should be fixed, and putting one into the baseline needs the user's confirmation.

When an old repository adopts the tool, nested history directories that are still in use can stay registered with the `archive` role; they still take part in classification, history checks, and the hints about ignore rules. New archives go by default into the registered root `archive/`; if the main directory has another name, state it explicitly with the optional `archive_root`. When there is no root `archive/` and only one history root is registered, that root is used. When several other history roots coexist, the main target must be stated explicitly; the tool does not guess.

When no directory with the `archive` role is registered, `check`, `check --staged`, and `check-new` run as usual but without history matching, and `history_match` is `null`; `archive` and `archive --summary` cannot determine a destination, report `input-unavailable`, and return `incomplete`.

History matching for a new document checks only the complete original path under the main target and does not infer how old layouts correspond. When other history roots exist, `check-new` and the staged check of newly added pages say explicitly that those directories still need to be searched.

### Adoption starting point

The baseline records only the errors of `check`. There are other rules that, on an old repository, would require rewriting hundreds or thousands of old documents: adding a status line to every plan, finding an entry for every old page, squeezing more than a thousand plans into a directory budget. Previously a project could only confine the new rules to a dedicated subdirectory, or give finished work a different status that triggers no reminder.

Configuring `"adopted_at": "<commit>"` registers the commit at adoption; it can be a commit ID, a tag, or a branch name. The tool resolves it to a commit ID and writes it into `coverage.adopted_at` of the report. Files that already exist in that commit count, by path, as existing files, and the following rules are relaxed for them:

| Rule | For existing files |
|---|---|
| `status-missing`, `plan-no-status`, `plan-blocked-no-reason`, `plan-status-current` | Not reported |
| `orphan-page`, `orphan-asset` | Not reported |
| `dir-budget` | Not counted; only documents added after adoption are counted |
| `trace-plan-scope` | Not reported |
| Format rules for review records | Not checked; a duplicate finding ID is still reported as `review-duplicate-id` |
| `plan-finished-not-archived`, `plan-stale`, `plan-idle`, `inbox-finished-not-archived`, `inbox-stale`, `inbox-no-status` | Merged into one `legacy-lifecycle` warning that gives the count for each rule; `remind --all` lists the files one by one |

The remaining rules, such as links, anchors, page budgets, status values, and `status-mismatch`, are checked on existing files as usual, and their errors can still be recorded in the baseline. An existing file that is renamed or moved to another directory is judged by its new path and is no longer an existing file. When `adopted_at` is not a commit in the current repository, when there is no Git, or when a shallow clone lacks the commit, incomplete is reported.

## Page size

Registers, status histories, and inbox lists that keep growing will, if their size is not limited, swell to several megabytes in a single page, with hundreds of thousands of characters crammed into a single line. A keyword search that hits such a line amounts to reading the whole page in. `check` warns about every non-archived document against two default limits, without `max_chars` having to be registered page by page:

- When the number of characters exceeds `page_chars` and the page has no `max_chars` of its own registered in `pages`, the warning is `page-oversized`. A page with a registered `max_chars` is judged by [`page-budget`](#checks-and-their-limits) and is not reported twice. The remedy is to keep only the open entries in the register and to archive the closed ones as a whole page; when the length is really needed, register a `max_chars` for the page in `pages`.
- When any line exceeds `line_chars`, `line-oversized` is reported once for each document; the message gives the line number and the character count of the first overlong line, and how many lines of the document are overlong. The remedy is to write one record on each line and not to cram a whole table into one line.

Both rules are reported as usual for old files from before the adoption starting point (`adopted_at`): large existing files are exactly what needs to be seen.

The defaults are adjusted with `size_limits`; all three fields can be omitted:

```json
"size_limits": {"page_chars": 100000, "line_chars": 10000, "ignore": ["docs/generated/*"]}
```

- `page_chars` (default 100000) and `line_chars` (default 10000) must be positive integers.
- `ignore` is an array of path patterns; neither rule is reported for a path that matches. It is for generated files or exports that really need to be kept whole.

Both rules read only the text that `check` has already loaded and read no additional files.

There is one more warning, for two entry files with the same content: when `AGENTS.md` and `CLAUDE.md` both exist in the same directory, are identical character for character once leading and trailing whitespace is removed, and are longer than 200 characters, `entry-duplicate` is reported, with the advice to keep one and turn the other into an import that contains the single line `@AGENTS.md`. The letter case of the import path is checked by `broken-link` along with the rest.

| Rule | Meaning |
|---|---|
| `page-oversized` | A non-archived page with no registered `max_chars` exceeds `size_limits.page_chars` |
| `line-oversized` | A document has a line that exceeds `size_limits.line_chars` |
| `entry-duplicate` | `AGENTS.md` and `CLAUDE.md` in the same directory are identical character for character |

### Neighboring repositories and submodules

When a system consists of several repositories checked out side by side, documents link into other repositories. Such links are written as relative paths, and the target repositories are registered in the configuration:

```json
"repos": [
  {"name": "FlymeAIEngine", "path": "../FlymeAIEngine"},
  {"name": "AgenticUILibrary", "path": "../../Agents/AgenticUILibrary"}
]
```

`name` is a unique name made of letters, digits, `.`, `_`, and `-`, and is used only in reports. `path` is relative to the project root and must be outside it, and the paths of two entries must not be the same or contain one another. A malformed entry is reported as incomplete. The reasons and the alternatives are in `docs/decisions/cross-repo-links.md` of the ProjectWiki repository (in Chinese).

After a relative link in a current document is resolved:

| Where the target is | What happens |
|---|---|
| Inside the project root, in a submodule that is not initialized | No error; counted among the unchecked links of that submodule |
| In a registered repository that is checked out | The file or directory is checked for existence (case-sensitively), and so is the anchor; errors are reported as `broken-link` and `broken-anchor`, with the same severity as links inside the repository |
| In a registered repository that is not checked out | No error; counted among the unchecked links of that repository |
| Outside the project root and in no registered repository | `unsupported-link`; the message gives a corrected form that opens, or, when there is none, advises registering the repository |

**What counts as checked out.** The directory of the registered repository exists and is not empty. A submodule counts only when it has its own `.git` in the working tree. A staged check does not read the files of submodules, because the index records only their commit, so in a staged check every submodule counts as not checked out.

Each repository or submodule that is not checked out gets one `repo-not-checked-out` warning that gives the number of unchecked links. `coverage.repos` in the report lists, for each registered repository, its path, its state (`checked-out`, `not-checked-out`, `no-git-head`), how it was read, the HEAD commit that was read, and the number of links; when there are submodules, `coverage.submodules` lists whether each one is checked out. By default this does not fail the check, because continuous integration usually checks out one repository only. `check --require-repos` requires that every registered repository, and every submodule that links point into, can be read; when one cannot, it reports incomplete with exit code 2. It suits an integration environment in which all the repositories are checked out.

**How targets are read.** A working-tree check reads the working tree of the target repository and serves as feedback while editing. `check --staged` reads the HEAD commit that the target repository has when the check starts, and the report names this commit, so the result can be reproduced; when the directory exists but has no HEAD commit, the state is `no-git-head` and the repository is treated as not checked out. Only the files that are linked to are read, and the whole repository is not traversed; symbolic links that point outside the repository are not followed and are treated as missing targets.

**What is not done.** Orphan-page detection, requirement tracing, and the link rewriting of archiving look only at this repository. `archive` does not rewrite links in neighboring repositories. Reminding the consumers when a provider changes a contract, and reading the target repository's own configuration to decide whether the target has been superseded, are not done yet.

## Checks and their limits

Currently supported:

- Required entries, module entries, registered directories, and unregistered `docs/` directories.
- Common inline links, reference-style links, and image paths. A relative path is resolved only from the location of the current document and does not fall back to the repository root. A footnote definition `[^name]: …` does not count as a reference-style link definition, and links in the footnote text are checked as usual. Two adjacent pairs of square brackets, `[a][b]`, are treated as a reference-style link only when the page defines reference-style links; in a page without any definition they are ordinary text, such as the subscript `m[i][j]` or adjacent labels, and a name that begins with `^` is always a footnote.
- The letter case of paths, ATX heading anchors, the suffixes of repeated headings, a `{#id}` written at the end of a heading, and explicit HTML `id` or `name` anchors.
- `@<relative path>` imports on a line of their own in `AGENTS.md` and `CLAUDE.md`. Other host syntaxes are not covered.
- The total number of characters of a page, including long lines, tables, and code blocks.
- Duplicate IDs of current documents within the same scope.

Link examples in code blocks and inline code are not taken as actual references. References to source code and tests are checked for the existence of the path; the current version does not verify source symbols. Markdown anchors follow the heading rule fixed in the tool, which has tests for repeated headings, Chinese headings, and explicit anchors; support for every renderer extension is not promised.

Broken links, missing anchors, exceeded budgets, and identity conflicts in current documents fail the check. When a relative local link escapes the selected project root, a current document gets an error and a historical document a warning. An absolute path on the local machine gets a portability hint; a required import that cannot be verified fails. Broken links in historical documents are kept as warnings, because old source code or old contracts may no longer be in the current version.

| Rule | Meaning |
|---|---|
| `missing-entry` | A required entry, module entry, or registered directory does not exist. When the path lies behind a symbolic-link directory, the message names the symbolic link; this explanation is not part of the baseline fingerprint |
| `required-excluded` | A required path is excluded by `exclude` |
| `unregistered-docs` | A `docs/` directory was found that is neither registered nor excluded |
| `unregistered-markdown` | Warning: there are Markdown files in no registered root, module, page, or entry, and `check` does not read them. `coverage.unregistered_markdown` in the report gives the count and the first 20 paths. Register the directory they are in, or exclude them |
| `broken-link` | The link target does not exist, or its letter case differs. When writing one more or one fewer `../` would open the target, the message gives the corrected link; when the target lies behind a symbolic-link directory, or exists only on this machine (ignored by Git), the message gives the cause and the remedy. None of these hints is part of the baseline fingerprint |
| `broken-anchor` | The target file does not have this anchor |
| `missing-reference` | The page defines reference-style links, but a name used in `[text][name]` is not defined. A page without any definition is not reported |
| `unsupported-link` | An absolute path on the local machine, a path that begins with `/`, or a relative path that leaves the project root and is in no registered repository. The message likewise gives a corrected form that opens, or advises registering the repository |
| `repo-not-checked-out` | Warning: a registered neighboring repository or an uninitialized submodule cannot be read, and the links into it were not checked. The message gives the number of links |
| `unsupported-import` | An `@` import in `AGENTS.md` or `CLAUDE.md` is not a local path |
| `unreadable-target` | A link has an anchor and its target exists but cannot be read, for example because it is not UTF-8 or is a symbolic link; for a symbolic link the message gives the remedy |
| `page-budget` | A page exceeds its registered character budget |
| `duplicate-current-id` | Two current documents in the same scope register the same ID |
| `name-case-collision` | Markdown file names in the same directory differ only in letter case |
| `watch-path-dead` | Warning: a pattern in `remind.watch` matches no file; the path has moved or is misspelled. Document patterns are always reported. Code patterns are often listed in groups by file type, and a type that has no files for the time being does not count: a path without wildcards is reported when it does not exist, and a pattern with wildcards is reported only when none of the code patterns of its group matches anything. Change the pattern to the present path, or delete it |

Unless stated otherwise, these are errors on current documents and are lowered to warnings on archived documents. When a document itself cannot be read (it is a symbolic link, or it is not UTF-8), one `unreadable` is reported for each such document, the other documents are checked as usual, and the rules that need the text no longer judge this document. When the unreadable file is a requirements file or a file in a review directory, the check reports incomplete, because requirements and reviews have to be verified as a whole.

Two more warnings serve to find files that pile up without anyone being able to find them:

| Rule | Meaning |
|---|---|
| `orphan-page` | A current knowledge document is not linked from any current document. Entry pages, module entries, and documents in process directories (`dev/`) are not checked; being linked only from archived documents does not count as having an entry |
| `orphan-asset` | A non-Markdown file (a screenshot, prototype, wireframe, and so on) in a knowledge directory or a module documentation directory is not linked from any current document. A link to the directory it is in counts as a reference too; configuration files, the generated index, baseline files, and files whose names begin with `.` are not checked |

Paths that really need no entry are registered in `orphan_ignore`, for example `"orphan_ignore": ["docs/assets/fonts/*"]`.

The tool does not check whether external URLs can be reached, does not judge the business meaning of a reference, does not verify arbitrary executable scripts or business contracts, and does not describe passing the formal checks as the knowledge being entirely correct.

## Staged checks

`check --staged` first reads the paths, file modes, and object IDs in the Git index, and then reads the configuration, the text, and the link targets by the captured object IDs. Unstaged fixes and new files in the working tree do not take part in this check, and changes to the index that happen afterwards do not replace the input already captured.

The tool also captures HEAD as the baseline for comparing newly added paths. When there is no first commit, the baseline is empty and the report says `unborn`. For documents that are new in this index, `archive/<complete original path>` is looked up in the same index snapshot; a hit gives the warning `historical-path-match` and does not block restoring or creating a document because of the same name. When other history directories are registered as well, a separate `legacy-history-unmatched` is a reminder that those directories were not compared by path. What is compared is the addition of paths: the tool does not infer whether the topics of the texts are the same, and it does not automatically treat a rename as a new knowledge identity.

When the configuration file is neither in the index nor in HEAD (including a repository that has no first commit yet), the project has not committed its adoption, and there is no committed baseline to compare against. `check --staged` and `remind --staged` then run no checks and report the warning `config-not-committed`; `result` is `not_checked`, `coverage.not_checked` states that nothing was checked, the exit code is 0, and the commit completes as usual. An adoption script can therefore commit the configuration and the hooks together in one commit. When the configuration is in HEAD but deleted in the index (this commit would remove the adoption), `incomplete` and exit code 2 are still reported; when the configuration is in the index (including one added in this commit), the normal checks run.

When neighboring repositories are registered (`repos`), a staged check also reads the HEAD commit those repositories have when the check starts, and not their working trees; see [Neighboring repositories and submodules](#neighboring-repositories-and-submodules).

Once the configuration has been committed, the command returns `incomplete` and a nonzero exit code when there is no Git repository, when there are unmerged index entries, when the configuration is not staged, or when a required input cannot be read. It does not fall back to checking the working tree. Documents inside submodules and other unsupported file modes do not pass as verified either: for a symbolic link the index holds only the link itself, the staged check does not read what it points to, and when the link is a document `unreadable` is reported.

The report contains the input snapshot, the tool version, the configuration hash, the directories covered, and the items not checked. A staged snapshot is identified by the SHA-256 of the index listing; this is not a Git commit or tree ID. A working-tree check is marked `working-tree`; it serves as feedback while editing and does not claim that the working tree is an atomic snapshot.

## Creating and archiving

`check-new` checks whether the target already exists and reports `current-path-occupied` when it does; it then looks for a file at `archive/<complete original path>` and gives the hint `historical-path-match` on a hit. A parent directory of the same name does not count as a document of the same name. A same-named file in history lets the creator decide between restoring it, continuing it, and starting a new topic; a name is not banned for good merely because a standard document name once appeared in history.

The creation check also deals with the file name itself. A path containing a space, `#`, `%`, or parentheses is reported as the error `name-unsafe-character`, because the link rewriting of archiving cannot safely preserve such forms. The three template placeholder names `plan.md`, `decision.md`, and `inbox-item.md` are reported as the warning `name-template-placeholder` (`requirements.md` is the recommended file name and is not a placeholder). Status and version words such as `draft`, `final`, `latest`, `done`, `completed`, or `v2` are reported as the warning `name-status-or-version`. The warnings are produced only for `check-new` and for newly added staged documents; existing documents do not get repeated warnings over style advice. A staged check does not treat two kinds of path as new names: paths under the archive root, and moves in which the content and the file name stay the same and only the directory changes. So archiving or moving an old document with a space in its name is not blocked; a rename to a new file name is checked as usual. The tool does not enforce a policy on ASCII, lowercase, hyphens, Chinese, or length.

### Archiving: preview first, then apply

`archive <path>` without options only previews and writes no file. The path can be one complete Markdown document or a whole directory (for example one review). The preview gives:

- The destination `<main archive root>/<original relative path>`, which keeps the file name and the directory structure; the main archive root is chosen according to the [configuration](#baseline-of-existing-problems) and is `archive/` in the default layout.
- The documents to be moved, the hash of the source content `source_sha256`, and the hash of the whole operation plan `plan_sha256`. When a directory is archived, `other_files_moved` lists all the non-Markdown files that move with the directory, including files excluded by `exclude` and untracked files; the plan hash covers the path, type, permission bits, and content of every item in the directory, and empty directories count too.
- The links to be rewritten: inbound links from other documents to the moved documents, and outbound links from the moved documents to the outside. Links between files inside the directory move with the directory, need no change, and are not listed.

After confirming the preview, apply it:

```bash
python3 scripts/wiki/wiki.py archive dev/plans/finished-work.md --root . --apply --expect <plan_sha256> --summary "one-line description"
```

`--apply` computes the plan again and proceeds only when the hash equals `--expect`: it moves the file or directory and rewrites every link target listed in the preview, leaving the other bytes of the files unchanged. The content of the moved document has not changed, so the rewritten links still point to the same content as before. When `--summary` is given, a row "title link | description" is appended to the end of the first table of the history index named by `archive_index`; when that is not configured, `<main archive root>/INDEX.md` is used, which is `archive/INDEX.md` in the default layout. The index must already exist and contain a Markdown table; the tool does not create an index. When `--summary` is omitted, no index record is appended.

After applying, `check` is run once on the working tree automatically, and `after_check` in the report is its result; 1 is returned when the check has errors. Files are only moved, not staged: before committing, stage the deletion and the new path together. Before applying, the rewritten content is written to temporary files inside the repository, and when this preparation phase fails the source files are not moved; when the commit phase fails, the tool tries to roll back in reverse order and lists in the report the cause of the failure or of an incomplete rollback. When the process is killed, temporary files or an intermediate state may still be left behind, and the working tree has to be checked against the report.

The following cases are refused, and no file is written:

| Rule | Severity | Meaning |
|---|---|---|
| `archive-unsafe-path` | Error | The source, the destination, or a path to be rewritten contains a symbolic link or leaves the project root |
| `archive-after-check-failed` | Error | The files have been written, but the check after applying could not be run; the report keeps the completed writes |
| `archive-collision` | Error | The destination already exists (including an empty directory), or some parent path of the destination is a file; nothing is overwritten even when the bytes are identical |
| `archive-plan-changed` | Error | The plan hash differs from `--expect`, a file to be rewritten changed after it was read, or files in the archived directory were added, deleted, or modified; preview again |
| `archive-index-unavailable` | Error | `--summary` was given, but the history index does not exist, has no table, or the description is not a single line |
| `archive-not-applied` | Error | The plan contains errors or `archive-rewrite-manual`, so it was not applied |
| `archive-rewrite-manual` | Warning | A link is written in a way that cannot be rewritten mechanically (escaped characters, percent-encoding, links that cannot be told apart on the same line) and has to be changed by hand; with this item present, `--apply` refuses |
| `archive-prepare-failed` | Error | Preparing the temporary rewritten files failed; the move has not started |
| `archive-apply-failed` | Error | The commit phase failed; the tool has attempted a rollback |
| `archive-rollback-failed` | Error | The rollback did not complete; check the working tree against the report and fix it by hand |

The preview and the apply step also report the following, which do not block applying:

| Rule | Meaning |
|---|---|
| `archive-entry-link` | A link in a current entry page would be rewritten to point into the archive; when a current document exists, link to the current document instead |
| `archive-unresolved-link` | An outbound link of the moved document could not be resolved to begin with and is left as it is |
| `archive-unresolved-target` | The target of an outbound link no longer exists, and no new path is given |
| `archive-non-markdown` | The directory has non-Markdown files that move with it, and the links in them are not checked; the full list is in `other_files_moved` |

When any level of the source, the destination, or a path to be rewritten contains a symbolic link, the operation is refused; this is checked before both the preview and the apply step. The relocation uses an atomic move that does not overwrite the target; where the system does not support that, an ordinary file can be moved by means of a hard link, and a directory, or a move across file systems, that cannot be moved safely fails. A rollback undoes only the steps completed in this run, does not overwrite the files of other writers it comes across, and reports the unfinished rollback and the operations already written. The tool has no global lock, and the checks cannot prevent other processes from replacing paths at will after the check; avoid concurrent modification while it runs.

The tool does not judge whether a topic has been retired, does not add redirect pages, and cannot find references outside the registered documents (for example code comments, or files in excluded directories). Cutting historical fragments out of live files, and batch migration, are not implemented for now.

## Moving documents

`move <source> <destination>` moves a current document that is in the wrong place, or a whole directory, to another registered location and rewrites the affected links. It shares one relocation core with `archive`: the same preview, plan hash, rewriting of inbound and outbound links, collision detection, rollback, and one run of `check` after applying. The difference is that you name the destination, which can be any registered location and not the point under the archive root that corresponds to the original path; `archive` also registers a row in the history index, and `move` does not.

Without options it only previews and writes no file:

```bash
python3 scripts/wiki/wiki.py move dev/decisions/engine.md docs/decisions/engine.md --root .
```

The preview lists the files to be moved, `source_sha256`, the hash of the whole plan `plan_sha256`, and the links to be rewritten (inbound links from other documents to the moved files, and outbound links in the moved files). Links between files inside a directory move with the directory and need no change. The rewriting follows the same rules as `archive`, so a link that cannot be rewritten mechanically is reported as `archive-rewrite-manual`, outbound links that cannot be resolved as `archive-unresolved-link` and `archive-unresolved-target`, a destination conflict as `archive-collision`, and non-Markdown files in a directory as `archive-non-markdown`.

After confirming, apply:

```bash
python3 scripts/wiki/wiki.py move dev/decisions/engine.md docs/decisions/engine.md --root . --apply --expect <plan_sha256>
```

`--apply` requires the hash to equal `--expect` and refuses when the destination already exists (including an empty directory), neither overwriting it nor numbering automatically. It then moves the files, rewrites the links, runs `check` once, and reports the result in `after_check`; on failure it rolls back in the same way as `archive`. Files are only moved, not staged. `move` has no `--summary`.

When the destination file name is the same as the source file name and only the directory changes, the naming check for new documents is not made. When the file name changes, the destination path is checked by the rules for new documents, and a path containing a space, `#`, `%`, or parentheses is reported as the error `name-unsafe-character`.

`move` refuses in the following cases:

| Rule | Severity | Meaning |
|---|---|---|
| `move-destination-outside` | Error | The destination is not inside the project root, or is under no registered root (knowledge, process, archive) and no module documentation directory |
| `move-source-protected` | Error | The source is the configuration file, the baseline file, the generated index file, or the history index, or the directory contains a protected path, and cannot be moved; `archive` refuses likewise |
| `move-invalid` | Error | The source does not exist, the source and the destination are the same, or the destination is inside the source directory |
| `move-use-archive` | Error | The destination is in the archive root; use `archive`, which also registers the history index. Moving something out of the archive (restoring it) uses `move` |

If a move turns a document linked from an entry page into an orphan, or makes `generated_index` out of date, the `check` after applying reports it. When `generated_index` covers the moved files, run `index --write` after the move to regenerate it.

### Generated index and `doctor`

`index` outputs the complete machine-readable index of current and historical pages, and each record is marked with a `role`. When generating navigation for current knowledge or a default retrieval set, the caller should filter out the historical roles. `check-new`, `archive`, `index`, `doctor`, and `verify` use the working tree; `check --staged` and `remind --staged` use the staged snapshot, and the output states this difference explicitly. The line counts of `remind --staged` are computed from the captured index and HEAD content and may differ slightly from a live `git diff --numstat` for binary files or unusual line endings.

`doctor` checks the configuration, the explicit root-level ignore rules for history, and the three ProjectWiki hooks (pre-commit, pre-merge-commit, commit-msg) in the current Git hooks directory; other hook managers and build tasks are reported as `unknown`, with a `hook-coverage` note. When `.ignore` does not exclude a registered history root, `archive-default-search` is reported; when a hook is missing or does not call the matching command, `hook-not-installed`; and when the configuration has no `remind`, `remind-not-configured`. The `remind` command gives this last warning in the same situation, with exit code 0. Plain `rg` honors `.ignore`; arbitrary `grep`, `git grep`, or explicit file reads are not covered by this rule. The ignoring here is noise reduction by default, not an access restriction.

## Documentation reminders at commit time

`remind` reminds developers and agents to check the documents after the code changes. It does not depend on any agent host: its data comes only from the Git history, the staging area, and the commit message, and it is triggered by Git hooks, so the same reminders appear at commit time whether you use Kiro, Claude Code, Codex, Cursor, or a manual `git commit`.

Add `remind` to the configuration:

```json
"remind": {
  "watch": [
    {"name": "notes", "code": ["notes/src/*"], "docs": ["notes/docs/*", "notes/README.md"]}
  ],
  "threshold": {"commits": 10, "lines": 300},
  "block_at": {"commits": 30},
  "ask_user": ["docs/requirements.md", "docs/principles/*", "notes/docs/decisions/*"]
}
```

- `watch`: groups of code paths and the documents that go with them. Patterns use `fnmatch` syntax, and `*` can cross directories. A project whose rules, templates, and examples have to stay in sync can register one more watch group, for example with `docs/design/*` and `docs/principles/*` as the code, and `templates/*`, `demo/*`, and the entry summaries as the documents. When a pattern matches no file, `check` gives `watch-path-dead`; see [Checks and their limits](#checks-and-their-limits).
- `threshold`: when the accumulated number of commits or of changed lines since these documents were last updated or reviewed reaches either value, the documents have to be checked. After checking, update the text, or reset the count with a review trailer that gives a reason; this reminder itself does not block the commit.
- `block_at`: optional. Once the accumulated amount reaches this value, a new commit that keeps changing the code without updating or reviewing the documents fails. Without it there are only ever reminders.
- `ask_user`: when these files are changed, the agent is reminded to confirm with the user first, unless the user has already asked for the change.
- `decisions`: optional. Where the decision records are; the default is `docs/decisions/*` and `*/docs/decisions/*`.
- `plans`, `inbox`: optional. Where the plans and the inbox items are; see [Lifecycle reminders for plans and inbox items](#lifecycle-reminders-for-plans-and-inbox-items).
- `plan_stale_days`: optional. After how many days without a commit an active plan or an untriaged inbox item gets a reminder; the default is 14.
- `plan_idle_days`: optional. After how many days without a substantive change a plan whose status is draft or blocked gets a reminder; the default is 60. Draft and blocked do not end the work, so a longer period is used, to avoid frequent interruptions over work that is shelved for ordinary reasons.

The count starts from the most recent commit that meets either of two conditions: it made a substantive change to the documents of the group (see [What counts as a substantive change](#what-counts-as-a-substantive-change) below), or its commit message carries the line `Docs-Reviewed: <name> <reason>` (a Git trailer, written in the last paragraph of the commit message). When the documents really were reviewed and need no change, use this line to reset the count. A trailer without a reason does not reset it. Several names can be separated with commas.

The adoption commit is an exception. The commit that first adds the configuration file (`docs/wiki.json`, or the configuration named on the command line) to the repository counts as the adoption commit; the earliest one is taken (`git log --diff-filter=A`). When `adopted_at` is configured, the commit it points to counts as an adoption commit too. An adoption commit often touches the documents of nearly every group and brings in the existing code all at once, so its document changes do not reset a group and its code changes are not added to the accumulated amount; a group is reset only when `Docs-Reviewed` in the commit message names it. The scan continues back to earlier commits, and the debt accumulated before adoption counts as usual. When the configuration has never been committed there is no adoption commit, and the behavior is the same as before.

When documents have been written but never committed, the history has no commit to start counting from. `remind` does not charge the code changes in the scanned range to this group: the accumulated amount is 0, `since` for the group in `watch_status` of the report says `uncommitted docs`, and the `[info]` hint `docs-uncommitted` is given; once the documents are committed, counting starts from that commit. Three conditions decide this: the group has no starting point within the scanned range, no file in HEAD matches its `docs`, and the working tree has one. `remind --staged` looks only at the index and does not give this hint: when the documents are in this commit they are treated as changed documents, and when they are not staged yet the count covers the whole scanned range as before.

The history traversal includes the commits of every branch. A merge commit is judged by Git's combined diff: only lines marked as added in the columns of all parents, or as deleted in all of them, count as text changes made by the merge. Content inherited or combined from the parents is neither counted again nor allowed to reset anything at the merge commit, and the parent commits are still traversed as usual. Whether a document change is substantive still has to be judged on the complete content, and the staleness days of plans and inbox items use the same merge criterion. A merge change to a binary file or a special file type counts toward the number of commits, with zero lines. The origin of duplicated content may not be determinable from the commit objects; this rule does not infer the intent behind a manual conflict resolution.

#### What counts as a substantive change

To judge whether the change to a document in a commit is "substantive", the changed paths and contents are read from the commit objects, and only files that match the `docs` of a group that has not been reset yet are judged. To pair moves, the Markdown files added and deleted in the same commit are read as well; the content of files of other types is not read, and they count as a pure move only when the content is identical. The objects needed are read in batches for each commit, without starting Git for each file. `remind --staged` compares the captured HEAD with the index, and history and staging use the same rule: a deletion and an addition whose content is the same, or differs only in links, mechanical fields, and the status line, are paired as a pure move and do not reset the count. Identical content is paired first and mechanical changes after that, and when content is duplicated the pairing is one to one in path order. While the original file is still there, a newly added copy still counts as an addition. A move across the boundary of a watch group is judged in the same way.

Not substantive (the group is not reset):

- Only the targets of Markdown inline links that the tool recognizes changed, while the link text and the visible headings did not; escaped ordinary text, and link syntax in code blocks and inline code, are judged as ordinary content.
- Only the values of the top-level frontmatter keys `updated`, `created`, `date`, `status`, and `phase` changed, including multi-line values; multi-line content of other fields is judged as body text.
- Only the `Status:` or `状态：` status line changed (the keywords and values are under [status lines](formats.md#status-lines-of-plans-decision-records-and-inbox-items); both the English and the Chinese forms count).
- A pure rename or move: the content is the same once the differences above are ignored.

Substantive (the group is reset): everything else, including additions, deletions, changes to the body text, and changes to the order of the body text. Only the named fields inside frontmatter that opens on the first line and has a closing delimiter are treated as mechanical fields; a change to an ordinary field of the same name in the body is substantive; and `Status:` or `状态：` text in code blocks and other positions is not a status line either. When the project root is in a subdirectory of the Git repository, both history paths and staged paths are judged relative to the project root. Changes to the `Verified:` and `Review by:` lines (`核对：` and `复核期限：` in Chinese) are substantive, because those lines are a statement of verification.

How to run it:

| Command | Purpose | Exit code |
|---|---|---|
| `remind` | At the start of a session, summarizes the accumulated amount of each group and reminds about Git hooks that are not in effect | Reminders only, exit code 0; 2 when there is no Git |
| `remind --staged --message-file <file>` | At commit time, checks the staged changes and the pending commit message | 1 when `block_at` is exceeded and this commit keeps changing code without a review; otherwise 0 |

When the configuration has no `remind`, both commands report the warning `remind-not-configured` with exit code 0. The commit-msg hook likewise ends with exit code 0, and the commit completes. Without Git, `remind` reports incomplete with exit code 2; `remind --staged` likewise returns 2 when it cannot read the index.

When the project is a Git working tree, `remind` (without `--staged`) also checks the ProjectWiki hooks in the hooks directory currently in effect. When pre-commit, pre-merge-commit, or commit-msg is missing, is not executable, or does not call the matching command, it gives the `[user]` warning `hooks-not-installed`, which states which hook is missing and the consequence (without pre-merge-commit, a merge without conflicts goes unchecked) and gives two ways to install: `git config core.hooksPath scripts/wiki/hooks`, or adding `check --staged` (pre-commit and pre-merge-commit) and `remind --staged --message-file "$1"` (commit-msg) to the existing hooks (see [Installing the Git hooks](README.md#installing-the-git-hooks)). Because changing `git config` should be the user's decision, this is a `[user]` reminder, and an agent must not make the change on its own. It reuses the judgment of `doctor`: when the project is not a Git working tree, or the hooks directory cannot be recognized as ProjectWiki hooks, the reminder is not given, to avoid false reports about other hook managers. `remind --staged` (that is, when it runs inside a hook) does not check the hooks. The exit code is still 0.

Staged mode captures the object listings of the index and of HEAD at startup, and the files and line counts of this change are computed from those listings: the content of a path whose object IDs are the same on both sides is not read; symbolic links, submodules, and binary files count as changed paths but add no lines. Line counts are computed with Python's `difflib`, are used only for the threshold reminders, and may differ slightly from `git diff --numstat`.

At commit time the following are reported:

- `docs-not-updated`: this commit changes code, the matching documents are not changed, and there is no review trailer. This is an `[info]` notice; below the accumulated threshold it does not require a review, a document change, or a trailer.
- `docs-review-due` / `docs-review-overdue`: the accumulated amount has reached the reminder value or the blocking value, and an `[agent]` reminder asks for a review; the commit is blocked only when `block_at` is reached and this commit keeps changing code without a review.
- `decision-sync`: this commit changes a decision record; the current documents that link to it but are not changed in this commit are listed. Documents that have no link and restate the conclusion directly cannot be listed and still have to be found by keyword search.
- `ask-user`: this commit changes a file in `ask_user`.
- `review-trailer-incomplete`: `Docs-Reviewed` in the commit message gives no reason, so the count is not reset.
- `review-trailer-unknown-group`: `Docs-Reviewed` gives a reason, but the name is not the `name` of any `remind.watch` entry. The configured group names are listed, with a note that this name resets no count. When one line gives several names separated by commas, only the ones that do not exist get the warning, and the ones that exist reset their counts as usual.
- `human-claim-added`: a Markdown file staged in this commit adds a line that contains `human:<name>`, for example a verification line, a verification table, an owner, or a sign-off. An agent must not write itself as `human:`, and the tool cannot tell who wrote the line, so this is a `[user]` reminder: confirm that the person named really did this, or else change it to `agent:`. Format examples in code blocks and inline code do not count.
- `remind-not-configured`: the configuration has no `remind`. Reminders are not enabled, the command exits with code 0, and the commit goes on to complete.

Reminders that need handling begin with `[agent]` or `[user]`: the former are handled by the agent as the message says, and the latter have to be passed on to the user. `[info]` does not have to be cleared and does not require a review trailer. When a code change is known to make the behavior, interfaces, or rules described in the documents untrue, the text must still be updated in the same change and must not wait for the accumulated threshold. `remind-not-configured` only states that reminders are not enabled. The tool does not judge whether the content of the documents agrees with the code.

### Lifecycle reminders for plans and inbox items

`remind` also checks the plan pages under `dev/` and the READMEs of review directories (by default the paths `dev/plans/*`, `dev/reviews/*/README.md`, and `dev/reviews/*/plan-*.md`, which `remind.plans` can change). The status is read from the status line in the text; the format is under [status lines](formats.md#status-lines-of-plans-decision-records-and-inbox-items):

- `plan-stale`: the status is `active`, but no substantive change has been made to the file for more than `remind.plan_stale_days` (14 days by default). The days are counted from the last substantive change, skipping the adoption commit and commits that change only links or mechanical fields, so an adoption import or a commit that changes frontmatter in bulk does not reset the days of a plan. Unlike the counting for watch groups, a change to the `Status:` line counts as substantive here: confirming the status again is an update to the plan. At most 30 commits back are examined; when there is no substantive change within those 30, the days are counted from the oldest commit in the window (a plan buried under that many mechanical commits is at least that old, and reporting it as stale is safer than missing it). `inbox-stale` uses the same algorithm. For the plans and inbox items whose days have to be computed, at most 8 files are read concurrently; each file is still scanned independently over its latest 30 commits, and the limit of the history scan for watch groups remains 2000 commits.
- `plan-idle`: the status is `draft` or `blocked`, but there has been no substantive change for more than `remind.plan_idle_days` (60 days by default). The reminder asks for a decision: start the work, cancel it, or state what is still being waited for.
- `plan-finished-not-archived`: the status is already `finished` and the file is still in `dev/`; the project's synonymous values, such as "cancelled", should be mapped to `finished` in `status_values`.
- `plan-no-status`: a plan page has no recognizable status line.

Inbox items are `dev/inbox/*/*.md` by default (`dev/inbox/README.md` and the `README.md` of each type directory do not count), which `remind.inbox` can change:

- `inbox-stale`: the status is still `open`, and no commit has changed the item for more than `remind.plan_stale_days` days.
- `inbox-finished-not-archived`: the status is already `finished` and the file is still in `dev/`. State where it went, then archive it.
- `inbox-no-status`: there is no recognizable status line.
- `legacy-lifecycle`: when `adopted_at` is configured, plans and inbox items that existed before adoption are not reminded about one by one; the items above are merged into this one, which gives the count for each rule, and `remind --all` lists the files one by one. See [Adoption starting point](#adoption-starting-point).

These are all reminders and do not block a commit.

The steps for installing the hooks are in the [tool entry](README.md#installing-the-git-hooks).

## Verification record

The "Verification" section of a plan does not hold command results written by hand; it is generated with `verify`. First register in the configuration the verification commands and the files whose hashes are to be recorded:

```json
"verify": {
  "commands": [
    {"name": "tests", "run": ["python3", "-m", "unittest", "discover", "-s", "tests"], "env": {"PYTHONDONTWRITEBYTECODE": "1"}},
    {"name": "check", "run": ["python3", "scripts/wiki/wiki.py", "check", "--root", "."], "summary_lines": 1, "summary_from": "start"},
    {"name": "demo-tests", "run": ["python3", "-m", "unittest", "discover", "-s", "notes/tests"], "cwd": "demo"}
  ],
  "files": ["scripts/wiki/wiki.py", "tests/test_wiki.py"]
}
```

- `run`: an array of arguments, executed directly and not through a shell, so pipes, redirections, and wildcards have no effect. A pipe swallows the exit code of the command before it, which is one of the reasons for not using a shell.
- `cwd`: the directory to run in, relative to the project root; the default is the project root, and it cannot leave the project root.
- `env`: additional environment variables.
- `timeout`: seconds, 900 by default; after the timeout the command is terminated and recorded as failed.
- `summary_lines`: how many lines of the output to record, 2 by default.
- `summary_from`: `end` (the default) records the last lines, which suits test frameworks; `start` records the first lines, which suits commands that put their conclusion on the first line, such as `wiki.py check`.
- `kind`: optional, one of `test`, `check`, or `build`, stating which kind of verification the command belongs to; any other value is a configuration error. A command without `kind` runs the same way as before.

The output of `verify` has the boolean field `code_tests_registered`: it is true when any of the commands that were run has the `kind` `test`. Otherwise it is false, and the record contains the line "未登记代码测试：本记录只证明所登记的检查命令，不证明代码" (no code tests are registered: this record proves only the registered check commands, not the code), as a reminder that the record does not prove that the tests of the code itself were run.

`verify` runs all the commands in order, and `verify tests check` runs only the ones listed. The output is a piece of Markdown that states the run date, the Git HEAD, the number of uncommitted files, the sha256 prefixes of the configuration file and the registered files, and for each command its directory, exit code, duration, and output summary; when only some of the commands are run, the ones not run are listed. Put it unchanged into the "Verification" section of the plan, and then add what was checked by hand.

When any command fails or times out, 1 is returned and `verify-command-failed` is reported. When a registered file is modified during the run, `verify-files-changed` is reported, and the hashes in the record are the state before the run; when `files` matches no file, `verify-files-unmatched` is reported. When the configuration is invalid, 2 is returned and no command is run.

`verify` runs the commands written in the repository's configuration, with the same level of trust as running the project's own test scripts. Before running `verify` in someone else's repository, look at which commands are registered there.

## Exit codes

The meaning of the exit codes is in the [tool entry](README.md#exit-codes). When the input, the configuration, or a command cannot complete the verification, `input-unavailable` is reported and 2 is returned.
