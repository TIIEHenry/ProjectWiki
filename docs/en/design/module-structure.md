# Directory and module structure

> English translation of [目录与模块结构](../../design/module-structure.md). The Chinese page is authoritative: if the two differ, the Chinese page applies.

This page describes the directories of the ProjectWiki repository itself. For the directory structure of an adopting project, see the [document model](document-model.md) and the [NoteBox reference project](../../../demo-en/README.md). When the directories change, update this page in place.

| Path | Responsibility |
|---|---|
| `README.md` | Introduction to the system and its entry, in English. The repository home page shows this one by default |
| `README.zh-CN.md` | The Chinese version of the same introduction. The two say the same thing; when one is changed, change the other at the same time |
| `AGENTS.md` | The rules that must be followed when developing this system, and the reading routes |
| `TODO.md` | What the system has not done yet |
| `CHANGELOG.md` | Changes that affect adopting projects |
| `docs/` | The specification of the system: requirements, principles, design, development workflow, writing and development standards, adoption guide, design trade-offs |
| [`docs/en/`](../INDEX.md) | The English translation of the specification, with directories matching `docs/`, without the requirements, the decisions, and the development standard. The Chinese page is authoritative; when a Chinese page is changed, change the matching English page as well |
| [`scripts/wiki/`](../../../scripts/wiki/en/README.md) | The copyable local documentation tool. `README.md` is the entry, `reference.md` registers the configuration and the rules, and `formats.md` is the authoritative text of the fixed forms the tool reads; the three are copied with the tool and link only to files in this directory |
| `scripts/wiki/en/` | The English translation of the tool documentation and the skills, copied together with the tool and likewise linking only to files inside `scripts/wiki/` |
| `tests/` | Counterexample and behavior tests of the documentation tool |
| `templates/` | The minimal templates used at adoption |
| `templates/en/` | The English templates, one for each Chinese template file, using the English keywords |
| `demo/` | The NoteBox reference project, independently configured and runnable, which demonstrates the complete structure after adoption |
| `demo-en/` | The English version of the NoteBox reference project, likewise independently configured and runnable, checked with `--root demo-en` |
| `tmp/` | Discussion drafts; not in Git and not part of the specification |

This repository has no `dev/` and no `archive/`: the development process of the system is not recorded in the way an adopting project records it; changes are written in commit messages and in `CHANGELOG.md`, and old versions are kept by Git.

## Organization of the specification

`docs/requirements/` states the problems the system is to solve and the acceptance requirements. `docs/principles/` states the constraints that must be kept when organizing knowledge. `docs/design/` explains the structure after adoption and the behavior of the tool. `docs/guides/` provides the steps for adoption and for everyday development. `docs/standards/` specifies the writing requirements and the development requirements of this repository. `docs/decisions/` records the important trade-offs in the design of the system.

## Boundary of the reference project

`demo/` and `demo-en/` are independent sample projects; each uses its own `docs/wiki.json` and is checked with `--root demo` and `--root demo-en`. The `docs/wiki.json` in the root directory registers only the specification documents of this repository, is used to check links and to reconcile the rule names in the tool documentation, and excludes `demo/`, `demo-en/`, `templates/`, and `tmp/`.

The module layout in the reference project does not restrict adopting projects. An existing repository can go on using `core/`, `packages/`, or another source layout, and only has to register the module entries and the documentation roots.

## Tool and templates

The checker reads the configuration of the target project, and all paths in the configuration are relative to the root directory of the target project. The templates provide structure and forms; after copying, the example goals, modules, and verification commands must be replaced.

The agents of other projects should choose the minimum set of content through the [adoption guide](../guides/adoption.md). Existing valid documents can be registered directly, without moving all the files first.
