# ProjectWiki

**English** · [中文](README.zh-CN.md)

ProjectWiki is a documentation system that lives in a project's code repository and is shared by its developers and coding agents. It includes rules for organizing documents, steps for adopting them, templates to copy, and a checker that depends only on the Python standard library.

It is meant for the situations in which people and agents depend on a project's documents: a new team member learning the project, an agent locating the code to change, a developer maintaining interfaces and design, a collaborator picking up unfinished work, and a maintainer tracing why a decision was made. The project can be a single-module tool or a repository that combines several build systems.

English introduction, 2 min 46 s.

https://github.com/user-attachments/assets/2fd09db3-88b2-48fd-bfba-666e4d086294

Chinese introduction, 2 min 46 s.

https://github.com/user-attachments/assets/df0ff5c5-ed0a-4155-8e2e-a23cac87e7be

## Layout after adoption

After adoption, a project keeps three kinds of material apart: what is true now, the records of work in progress, and history.

| Path | What it holds |
|---|---|
| `AGENTS.md` | Hard rules for the whole project, and a table that routes each kind of task to the pages to read |
| `docs/` | Current knowledge: requirements, principles, design, standards, guides, and decision records. Edited in place |
| `dev/` | The development process: roadmap, plans, reviews, and inbox items |
| `archive/` | Finished process material and whole documents that no longer apply, kept at their original relative paths |
| `<module>/README.md`, `<module>/docs/` | A module's entry page and the knowledge that belongs only to that module, kept next to its source |

`docs/`, `dev/`, and `archive/` sit side by side at the root. The [NoteBox reference project](demo-en/README.md) shows the complete layout. This repository is the documentation system itself and does not work like an adopting project: it has no `dev/` or `archive/`, and its root holds the specification, the templates, the checker, and the tests.

## The rules in brief

- Current knowledge, process records, and history are kept apart. A requirement that is confirmed but not yet implemented is still knowledge, and the progress of a task does not change what the requirement says.
- Context is supplied in layers, by task. The project entry gives the hard rules and a reading route, a module entry gives the module's responsibility and contracts, topic pages give the details, and source and tests settle what the code actually does. A project sets a character budget for its entry pages, and the checker fails a page that exceeds its budget.
- Each topic has one authoritative page. Other pages link to it instead of restating it. A project-wide rule that causes errors when ignored is also written directly in `AGENTS.md`, so that following it does not depend on an agent opening a link.
- Current knowledge is edited in place, and Git keeps the revisions. A document is archived only when the work it records has ended or the document as a whole has stopped applying.
- The number of documents is kept down. New content goes into a section of an existing file unless it has its own lifecycle or several people need to write it at the same time. A kind of record that takes one file per item, such as the inbox, must also define how each item is closed.
- Process scales with impact. An ordinary fix can change only code and tests and give its reasoning in the commit message. Design notes, plans, and decision records are added when there is a significant trade-off, a contract change across modules, a data migration, or a handoff.

The reasoning behind these rules is in the [design principles](docs/en/principles/document-system.md).

## The checker

`scripts/wiki/wiki.py` is a single Python file. It runs on Python 3.10 or newer without third-party packages; checking staged content and commit reminders also need Git. A project registers its document roots, entry pages, modules, and page budgets in `docs/wiki.json`, and the checker works from that configuration.

- `check` verifies that registered entry pages exist, that local links and anchors resolve, that pages stay within their budgets, and that status lines, requirement entries, and review records follow the formats it reads. When a project registers its requirements, `check` also counts the acceptance items that a test refers to by ID and warns about items of implemented requirements that have neither a test nor a manual-verification mark.
- The Git hooks run `check` on the staged snapshot. At commit time, `remind` points out code that has changed while the documents registered for it have not. The reminder relies only on Git, so it appears with any agent tool and with a manual `git commit`.
- `archive` and `move` show a preview first, then apply the change and rewrite the affected links.
- `baseline` records the problems an old repository already has, so that only new problems fail.

The checker does not judge whether the design or business conclusions in a page are correct. A run that cannot complete its checks is reported as incomplete, not as passed. The checker writes files only when a command asks for it (`archive --apply`, `move --apply`, `index --write`, `export-okf`), and `verify` runs the commands the project has registered. It does not stage or commit, and the Git hooks do not change files.

An adopting project copies the whole `scripts/wiki/` directory. Besides the checker, it carries the Git hooks, the pages that document commands, rules, and formats, and skills that guide an agent through tasks such as adoption and reviewing documents against the implementation.

## Try it

From the root of this repository, run the checker on the reference project:

```bash
python3 scripts/wiki/wiki.py check --root demo-en
```

The output begins with `check: passed (0 errors, 0 warnings)`.

## Adopt it in a project

Adoption starts small. Choose one feature change and one maintenance task in the project, and build only the pages those two tasks need. Documents that are still valid are registered where they are; they do not have to be moved or rewritten first. The steps are in the [adoption guide](docs/en/guides/adoption.md). A coding agent can carry them out by following the [adoption skill](scripts/wiki/en/skills/adopt-projectwiki/SKILL.md): tell it where this repository is and which project to adopt.

## Language

ProjectWiki is written in Chinese, and the Chinese pages are the authoritative text. The parts needed to understand and adopt it also have English versions:

| Chinese | English |
|---|---|
| The specification under `docs/` | [`docs/en/`](docs/en/INDEX.md): the design principles, the design pages, the adoption guide, the development workflow, and the writing standard |
| The tool pages and agent skills under `scripts/wiki/` | [`scripts/wiki/en/`](scripts/wiki/en/README.md), copied into an adopting project together with the checker |
| The templates under `templates/` | [`templates/en/`](templates/en/README.md), written with the English keywords |
| The NoteBox reference project in `demo/` | [`demo-en/`](demo-en/README.md) |

The requirements, the decision records, the changelog, the to-do list, and the conventions for developing ProjectWiki itself exist only in Chinese. Where an English page and its Chinese page differ, the Chinese page applies.

The checker reads documents in either language: every keyword and status value has a Chinese form and an English form, for example `状态：执行中。` and `Status: active.`, and both are listed in the [format reference](scripts/wiki/en/formats.md). It reports its findings in English, but the examples inside them use the Chinese forms, and the record that `verify` writes is in Chinese.

## Where to start

| If you want to | Read |
|---|---|
| Understand the reasoning behind the rules | [Design principles](docs/en/principles/document-system.md) |
| Adopt ProjectWiki in a project | [Adoption guide](docs/en/guides/adoption.md), [adoption skill](scripts/wiki/en/skills/adopt-projectwiki/SKILL.md) |
| See a complete example | [NoteBox reference project](demo-en/README.md) |
| Learn what goes into decision records, plans, roadmaps, and reviews | [Development workflow](docs/en/guides/workflow.md) |
| Write or review a document | [Writing standard for Chinese technical documents](docs/en/standards/writing.md) |
| Run the checker or look up a rule | [Checker commands](scripts/wiki/en/README.md), [configuration and rules](scripts/wiki/en/reference.md), [formats the checker reads](scripts/wiki/en/formats.md) |
| Find any page of the specification | [Specification index](docs/en/INDEX.md) |
| Change ProjectWiki itself | [Development conventions](AGENTS.md), [to-do list](TODO.md), [changelog](CHANGELOG.md), all in Chinese |
