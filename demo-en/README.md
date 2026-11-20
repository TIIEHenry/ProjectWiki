# NoteBox example project

> 中文版：ProjectWiki 仓库里的 `demo/`。

NoteBox provides title validation for notes. The example contains a small runnable module, and the relationships among requirements, principles, design, development records, and the archive. It serves to demonstrate the documentation system and provides no persistence or network service.

- To look up current knowledge: start from the [knowledge entry](docs/INDEX.md).
- To change the title rules: start from the [title module](notes/README.md).
- To continue work: start from the [development entry](dev/INDEX.md).
- When adopting in another project, first read the ProjectWiki adoption guide; this example directory can be copied on its own.

Run the tests under `demo-en/`:

```sh
python3 -m unittest discover -s notes/tests -v
```

The documentation tool is provided by ProjectWiki. When copying this example on its own, copy `scripts/wiki/` to the root directory as well, and then run `python3 scripts/wiki/wiki.py verify --root .`; in the ProjectWiki repository, run `python3 scripts/wiki/wiki.py verify --root demo-en` from the repository root.

For a first adoption in another project, or to complete an unfinished adoption, you can use the adoption skill provided by ProjectWiki: the first time, open it from `scripts/wiki/en/skills/adopt-projectwiki/SKILL.md` in the source repository; after the tool has been copied in full, open it locally from the target project. The source repository provides the templates and the complete adoption guide, and what is written to is the target project the user names; opening the skill by path does not mean that the host has installed it natively.

The complete `scripts/wiki/en/skills/` also provides the skills for document review, document organization, knowledge capture, and syncing documents and committing. Agents read them by the task table in `AGENTS.md` and operate on the current project; the example keeps no separate copy of the text, and does not require them to be invoked for every task or commit. Native skill discovery by the host has to be registered and verified separately.

The documentation development workflow of the example follows `scripts/wiki/en/workflow.md` by default, and the business constraints of the project stay in `AGENTS.md` and in the module knowledge; adaptation of the shared workflow is handled by its section "Shared workflow and project adaptation".

The example repository keeps `docs/`, `dev/`, and `archive/` side by side. `notes/docs/` keeps the module knowledge. Finished plans are in `archive/dev/plans/`; the current title rules are maintained in place, and the revision history is left to Git.

These example files do not require every change to create a set like them. An ordinary fix to title validation can change only the code and the tests and explain the basis in the commit message; new behavior with a clear boundary and no significant contract or risk change is traced with a requirement entry and tests. Add the relevant design when a contract or a significant risk changes, create a plan for multi-step collaboration or a handoff, and write a decision record for an important trade-off that needs a lasting explanation.
