# Adopting ProjectWiki

> English translation of [接入 ProjectWiki](../../guides/adoption.md). The Chinese page is authoritative: if the two differ, the Chinese page applies.

Requirements: PW-10, PW-27.

This guide is for the developers and agents of an adopting project. The goal is to build the minimum documentation system that can support real development tasks.

When the user asks to adopt ProjectWiki in a given project, or to complete an unfinished adoption, an agent can use the [adoption skill](../../../scripts/wiki/en/skills/adopt-projectwiki/SKILL.md). For a first adoption, open it from the ProjectWiki source repository; in a project that has already copied the tool, open it from the local `scripts/wiki/en/skills/adopt-projectwiki/SKILL.md`. This does not mean that the host has installed the skill natively. What the skill writes to is the target project the user names; the source repository only provides the templates, the tool, and this guide. The location of the source repository comes from a path the user gives or from a source already located in the workspace; when it is missing, pause only the steps that depend on the templates or on the complete guide, and do not construct a path yourself. Adoption does not include automatic upgrades, or commits, pushes, global configuration, or execution-suite operations that have not been authorized.

## 1. Read ProjectWiki and survey the target project

First read the [design principles](../principles/document-system.md), the [directories of an adopting project](../design/document-model.md#directories-of-an-adopting-project), the [development workflow](workflow.md), and the [reference project](../../../demo-en/README.md).

Once in the target repository, examine the existing `AGENTS.md`, README, modules, documents, development records, and history directories. Find the pages that are currently authoritative, the duplicated explanations, and the old material that still has a use, and deal with the existing content and the existing workflow separately. After adoption, the documentation development workflow takes the ProjectWiki shared workflow as its baseline; complete the migration of the rules as described in [Shared workflow and project adaptation](../../../scripts/wiki/en/workflow.md#shared-workflow-and-project-adaptation).

Existing valid text, requirement IDs, and historical records are registered by preference and are not rewritten in bulk in order to pass the checks. Keeping content and paths does not mean keeping the old workflow. For each requirement that by default has to be carried out with every task or every commit, check what problem it solves, when it is triggered, and whether it duplicates or conflicts with the shared workflow; revise the original rule entry and its readers according to the shared workflow, and do not apply the two sets of requirements on top of each other by default. A project exception that is really necessary is written in the original entry by the adaptation rules of the shared workflow. Do not require a plan, a status page, and a board all to record the same progress.

Existing checkers are likewise checked by their actual coverage, the input snapshot they read, and their failure conditions. When two checks are confirmed to be equivalent, keep only one; a working-tree check and a staged check read different content and cannot be treated as duplicates merely because the rule names are similar. Write the cleaned-up rules directly back into the original entry of the target project, and do not create a separate workflow list that needs long-term maintenance.

When the project has already adopted an execution suite, first check which agents or programs read the status, the queues, the boards, and the evidence, tell coordination summaries apart from execution protocol records as described in [Task records and status pages](../../../scripts/wiki/en/workflow.md#task-records-and-status-pages), and only then decide whether to merge, split, or retire them; existing fixed entries and mappings must not be deleted because their names are similar.

Do not copy ProjectWiki's own product requirements as the requirements of the target project. The document structure can be reused, but the business content has to be written from the actual situation of the target project.

When an execution suite and ProjectWiki are used together, register the actual sources and responsibilities as described in [Sharing the development entry](../../../scripts/wiki/en/workflow.md#sharing-the-development-entry-with-an-execution-suite), and then migrate the readers by the suite's own adoption instructions. First keep the mappings that work, for example the plans in `dev/roadmap/active/`, the inbox queue in `dev/progress/`, and the occupancy records in `dev/parallel/active/`; these paths are examples from existing projects, not directories that every project must create. A lightweight project can also reuse requirements, existing plans, or submitted tasks directly, without creating phases, status pages, or decision records for the adoption. Use the tasks chosen in step 2 to check in practice whether the two workflows connect.

## 2. Establish two real reading paths first

Choose one feature change and one maintenance problem, and identify the requirements, principles, design, code, and tests they need. Test the directories and the templates with these two tasks first, and avoid creating a large number of empty pages at once.

Each path should make the goal, the constraints, the entry to the implementation, and the way to verify clear to the reader. Add a counterexample: when a local configuration change affects another module, can the related contract be found?

## 3. Build the minimum structure

With [`templates/en/project/`](../../../templates/en/project/README.md) as a reference, create the root `docs/`, `dev/`, and `archive/` as the target project needs. The existing module layout stays unchanged, and the knowledge of a single module stays close to its source code.

A new, small project can use the merged pages of the templates. When the content grows, split it by requirements, principles, design, and standards. Existing valid documents can be registered directly and need not be renamed or moved first.

**Where old directories go.** Old repositories often have a number of directories that have no directly matching place in the model. There are only three criteria: what still describes current behavior goes in `docs/`; what records process and goes out of date goes in `dev/`; what has lost its validity as a whole goes in `archive/`. Directories under `docs/` are parsed as current knowledge, so templates and process material should not stay in `docs/`. Common old directories are handled by the table below; what cannot be sorted out in one pass is registered as transitional (see the transition table further down) and done in batches.

| Old directory | Suggested destination |
|---|---|
| `docs/systems`, `docs/architecture`, `docs/reference` | All current knowledge; they belong to `docs/`. Keep them, registered by module or left in the root `docs/`; they need not be moved |
| `docs/modules` | This is a mirror directory of the modules. The global module table links directly to the entry of each module; merge the content of the mirror into the `docs/` of the matching module and then delete the mirror. When it cannot all be merged in one pass, register the mirror as transitional first and migrate module by module |
| `docs/templates` | Templates are not current knowledge. Put them in `templates/` or inside the matching module, and do not leave them under `docs/`, which is parsed as current knowledge |
| `dev/progress`, `dev/roadmap`, `dev/reports`, `dev/iterations` | All process material; they belong to `dev/`. Registers that keep growing are searched by ID or keyword, reading only the matching lines, and are archived once the whole page has lost its validity |
| Agent operation manuals, playbooks, skills, runtimes (for example the batches of pages under `dev/loop/`) | Put them in directories of their own under `dev/`, not in `docs/`. When a tool or skill generates into `docs/` by its default path, change the default path in its configuration; when it cannot be changed, state in `AGENTS.md` that the output is moved into `dev/` after it is generated |

Read the [template notes](../../../templates/en/README.md) before using the templates. When copying a single file, check whether the target already exists, merge the valid content, and check and clean up the workflow rules as in step 1; do not overwrite the original file with the whole template.

**The transition table of an old repository.** When there are already many documents, with several on the same topic, and they cannot all be sorted out at once, first build a "table of current authorities", for example `docs/current-sources.md`. It has one row for each topic and three columns: the topic, the currently authoritative document, and the old documents that should no longer be consulted. When agents and new members meet several documents on the same topic, they read only the authority column. After that, each time an old document is archived, delete the matching cell of the table, and when every topic has only one text left, delete the whole table as well. This table is only for the transition and must not become a second navigation that is maintained in the long term.

The transition table answers only "which one to read on the same topic"; it has only these three columns and carries nothing else. When reading an old document reveals a correction of behavior in it ("actually the present practice is X"), write the correction back into the currently authoritative text, and do not pile corrections into the cells of the transition table; otherwise the table swells into an errata list (there has been a `current-sources.md` of 15KB and more than thirty rows whose cells were full of behavior corrections) while the real text is not updated. The table handles navigation only, and the whole table is deleted once every topic has converged on one text.

**Retirement notice.** When an old standard has been replaced by new rules but external links or bookmarks still point to it, do not leave an empty file, and do not delete it and break the links; rewrite it as a retirement notice: one sentence that says what this page no longer specifies and where to read instead, followed by a list of the old rules that should no longer be followed. For example:

```markdown
# Title validation standard (retired)

This page no longer specifies the length and character validation of titles; read docs/design/title.md instead.

Do not follow these old rules any more:
- Do not validate by the old "at most 20 characters in a title"; the length limit is in the new page.
- Do not cite the regular expression in this page; it does not match the current implementation.
```

A retirement notice does not copy the new conclusions and only points the way; once it is confirmed that there are no external references, the whole page can be archived by the lifecycle rules.

**Check where AI tools write their output.** Some agent skills write plans or reports to their own default paths, for example `docs/<tool name>/plans/`. At adoption, search `docs/` for directories generated by tools and move the content to `dev/`; for tools whose configuration can be changed, change the default path, and for those that cannot, state in `AGENTS.md` that the output is moved away after it is generated.

**Changelog.** When the project already has a `CHANGELOG.md`, keep it, and register it in `docs/INDEX.md` as the record of the changes visible to users. For a project with a release process, it is advisable to check in the release script whether the current version has been written into the changelog, and to stop the release when it has not.

**Register the adoption starting point.** When an old repository has hundreds of plans without a status line, old pages that nobody links to, or directories whose file counts have long exceeded the budget, do not confine the new rules to a dedicated subdirectory such as `dev/plans/wiki/`, and do not give finished plans a different status that triggers no reminder. After the adoption commit is made, write `"adopted_at": "<adoption commit>"` in `docs/wiki.json`: the files that existed then are not reported for a missing status line or as orphan pages, and are not counted toward directory budgets; new files are checked as usual; the archive reminders of old plans are merged into one that gives the count. After that, handle a few at a time from the list that `remind --all` prints. The scope is under [Adoption starting point](../../../scripts/wiki/en/reference.md#adoption-starting-point).

**A status field in existing frontmatter.** When plans and decision records already write their status in frontmatter, do not add a status line to each page as well; that would give one piece of work two statuses, which drift apart when nobody compares them. Register the field name in `docs/wiki.json` (`status_frontmatter`), and map the values the project has used to status classes in `status_values`; newly written pages use a status line. For old pages that have both, the tool warns when the classes differ. The fields are under [Configuration and rules](../../../scripts/wiki/en/reference.md#configuration).

**Decisions that still constrain behavior.** If existing decisions are kept in `dev/decisions/`, move the decisions that still constrain current behavior to the `docs/decisions/` of the knowledge scope they belong to. If one of them stipulates that future decisions are also written in `dev/`, replace that convention with a new decision; the conclusion that knowledge and action are kept apart can be retained. File names state the topic and do not continue a global sequence number.

**Module list.** Check the module tables in `AGENTS.md` and in the documents against the build entry. A handwritten table misses modules that already take part in the build. This reconciliation still has to be done by hand; the tool does not read build files at present.

**Case of include paths.** The include paths in files such as `CLAUDE.md` must match the case of the real file names. A case-sensitive system does not resolve `AGENTS.MD` to `AGENTS.md`.

## 4. Write the key entries

`AGENTS.md` states directly the purpose of the project, the hard rules that apply, the default search scope, and the verification command, and declares the shared workflow baseline as the project template does. Keep the business constraints of the project; workflow duplication or conflict is migrated as in step 1, and the old workflow must not be followed first by default just because the old entry is still there. Detailed reasons can be linked out, but following the key rules must not depend on opening further links.

Keep the skill task table in `AGENTS.md` as the project template has it: document review, document organization, knowledge capture, completing an adoption, and syncing documents and committing each have one on-demand entry, and the paths are all under `scripts/wiki/en/skills/`. These skills operate on the current adopting project; they need not be run with every task or commit, and they do not mean that the host has discovered the skills natively. The complete task navigation is in the [tool entry](../../../scripts/wiki/en/README.md). When a host skill list or native invocation is needed, register the entries separately in the way the host supports, still pointing to the single authoritative text of each skill.

The root README introduces the project and its entries to people. `docs/INDEX.md` says, by task, when to read which document. A module README describes the responsibilities, the related contracts, and where the source code and the tests are.

Use the [writing standard](../standards/writing.md) when creating stable knowledge: state the object and the conditions clearly, explain the terms, and remove AI boilerplate, translationese, and development logs. Read the whole text once, and then run the structure check.

## 5. Connect the local checks

Copy the whole `scripts/wiki/` to a suitable place in the target repository, and register your own `docs/wiki.json`. The `README.md`, `reference.md`, `formats.md`, `workflow.md`, and `skills/` in the directory (and their English versions under `en/`) are copied along with it: the agents of the target project look up the commands, the rules, the fixed forms, and the closing steps in them, and need not open the ProjectWiki source repository again. The `SKILL.md` in each skill directory under `skills/` is the single authoritative text of that skill; it is provided by ProjectWiki so that an adopting project can handle the task in question with its own entries, configuration, and working tree; the templates and the project entries only point the way and keep no second copy. The paths in the configuration are relative to the project root given by `--root`.

The configuration lists at least the knowledge root, the process root, the archive root, and the entries, and registers the modules by the actual structure. The copied `scripts/wiki/` is the documentation of the tool; write `scripts/wiki/**` in `exclude`, otherwise `check` reports that these Markdown files are not registered. A small module can register only its README; fill in the `docs` of the module when it has a documentation directory of its own. The check of the root project should exclude independent examples or subprojects, which are then checked separately. The checker should not depend on the ignore scope used for searching.

```bash
python3 scripts/wiki/wiki.py check --root .
python3 scripts/wiki/wiki.py doctor --root .
```

You can also check the target project from the ProjectWiki tool directory first, without copying the script right away:

```bash
python3 /path/to/ProjectWiki/scripts/wiki/wiki.py check --root /path/to/target-project
```

Here `/path/to/` is a placeholder in the command example; replace it with the actual path when running the command, and do not write absolute paths of your machine into the links in the text of the target project.

## 6. Set up default search and the check for new documents

Merge `/archive/` into the existing `.ignore` of the target repository. The archive stays under Git. When adopting an old layout, register the actual nested history directories with the `archive` role, and add exact search ignore rules for these directories.

New archives use the registered root `archive/` by default; when another name is used, name the primary target with `archive_root` in the configuration. Old history roots still take part in classification and checks, but the tool does not infer how an old layout corresponds to the original paths, so they have to be searched separately by topic.

Before creating a document, run the following command, replacing the path with the file to be created:

```bash
python3 scripts/wiki/wiki.py check-new docs/design/new-topic.md --root .
```

The check matches the complete original relative path under the primary target. When it hits history it returns a warning and the exit code is still `0`; read the historical content and then judge whether this is a restoration, a continuation, or a new topic. It fails when the current target already exists. The check does not permanently ban necessary standard file names. The staged check also examines the documents added relative to the captured HEAD and points out the matching history in the same index snapshot.

## 7. Connect the commit checks

First make the working-tree check pass. In a Git repository, after staging the configuration, the text, and the related files, check the actual staged snapshot:

```bash
python3 scripts/wiki/wiki.py check --root . --staged
```

When the project has no other hooks, copy `scripts/wiki/hooks/` and run `git config core.hooksPath scripts/wiki/hooks` once in each clone. When there is already a hook tool, add `check --staged` to the existing pre-commit and pre-merge-commit, and `remind --staged --message-file "$1"` to the existing commit-msg, and do not overwrite the original configuration. pre-merge-commit covers merges that have no conflicts and for which Git creates the merge commit directly; such merges do not run pre-commit. Scripts being present in the repository does not mean that the current working copy has enabled them; run `doctor` and look at the result of `git_hooks`. When the configuration has no `remind` yet, commit-msg prints the warning `remind-not-configured` and the commit succeeds; thresholds and blocking take effect only after `remind` is written in step 8, see [Documentation reminders at commit time](../../../scripts/wiki/en/reference.md#documentation-reminders-at-commit-time).

Exit code `0` means that this check found no errors, though there may still be warnings; `1` means that errors were found; `2` means that the input or the execution conditions are incomplete. A hook must treat both `1` and `2` as failure. Without a Git repository only the working-tree check can be run, and it cannot be used to report that the commit gate has passed.

Verify a counterexample with a temporary Git repository: a link is still wrong in the staging area and already fixed in the working tree, and the commit check should still fail. Do not cover up the content actually being committed with an unstaged fix.

When archiving later, first judge eligibility by the [lifecycle rules](../design/lifecycle.md); the tool does not check whether a plan is finished or whether a decision has lost its validity. Then run `python3 scripts/wiki/wiki.py archive <original relative path> --root .` to preview the conflicts and the links to be rewritten, and after confirming, add `--apply --expect <plan_sha256>` to execute. When the history index selected by the configuration already exists and contains a table, you can add `--summary "<one-line description>"` to register the entry at the same time; the selection rules are under [the archive command](../../../scripts/wiki/en/reference.md#archiving-preview-first-then-apply).

## 8. Set up documentation sync reminders

Add `remind` to `docs/wiki.json`, register each group of code paths and the documents that describe it as one `watch`, and then set the reminder thresholds; the requirement, principle, and decision files that need the user's confirmation are written in `ask_user`. The fields are described under [Configuration and rules](../../../scripts/wiki/en/reference.md#documentation-reminders-at-commit-time). By default you can start with a reminder at 10 commits or 300 lines and blocking at 30 commits, and adjust by the actual frequency of reminders.

At adoption, `remind` also counts the code commits made before the adoption, so some groups may already be over the blocking line. Do not raise `block_at` permanently for this one-off historical debt. Check documents against code group by group: documents that need changing are changed in the adoption commit, which resets the count of that group; for those that really need no change after checking, write `Docs-Reviewed: <group name>,<group name> checked group by group at adoption; the documents match the code` in the last paragraph of the adoption commit message, which resets the count as well. Groups that cannot be checked in time are left out of `watch` for now and added after checking; do not write a reason that has not been checked just to reset the count.

The reminders work for every agent host and rely on three places:

1. The Git `commit-msg` hook runs `remind --staged` at every commit, and the reminders appear in the output of the commit command.
2. The `AGENTS.md` of the target project states: run `python3 scripts/wiki/wiki.py remind --root .` when starting a task; the `[info]` notice of a single code change does not require a review record, a review is required only when the accumulated amount reaches the reminder threshold, and further accumulation is blocked only when it reaches the blocking threshold; when a document is known to describe things wrongly, it is still updated in the current change. How to handle them and the thresholds are under [Documentation reminders at commit time](../../../scripts/wiki/en/reference.md#documentation-reminders-at-commit-time). Reminders of the `[user]` kind are reported to the user; the hooks must not be skipped with `--no-verify`.
3. Optional: when the host supports a session-start hook, have it run the same `remind` command and inject the summary into the context. For example, Kiro can create a hook triggered by `SessionStart` whose command is that command; hosts such as Claude Code are configured by their own documentation. This step only makes the reminders appear earlier, and without it the first two still work.

Verify with a temporary repository: below the accumulation threshold, an ordinary fix that changes only code and tests shows `docs-not-updated` and can be committed without a review trailer; once the reminder threshold is reached, a review is required; once the accumulated amount reaches the blocking threshold, a commit that goes on changing code fails, and it passes after the matching documents are updated or really reviewed. The thresholds and the form of the review record are under [Documentation reminders at commit time](../../../scripts/wiki/en/reference.md#documentation-reminders-at-commit-time).

## 9. Number the requirements and connect the tracing checks

Organize the confirmed requirements of the target project by the [requirements template](../../../templates/en/requirements.md): each has a heading with an ID, a status line, and acceptance criteria with sub-IDs. When there is already a PRD or a requirements list, keep the original IDs and add only the statuses and the acceptance sub-IDs; when the IDs are not in a format like `APP-01`, register your own format in `requirements.id_pattern`, and do not change the IDs in order to pass the checks. Then add `requirements` to `docs/wiki.json` and register where the requirement files and the test files are. When a repository has several products that number independently, for example when the engine and the client both start from `PRD-001`, do not turn tracing off and do not renumber: write `requirements` as an array of groups, each registering its own requirement files, the documents that cite it, and the tests; the form is under [Requirement tracing](../../../scripts/wiki/en/reference.md#requirement-tracing).

The first run on an old project may report a large number of `trace-no-test`. Deal first with errors such as `trace-unknown-ref`; the errors that cannot all be dealt with can be recorded in the baseline of existing problems; warnings do not make the check fail and do not enter the baseline, so after adoption you can check the test coverage one by one and add the real acceptance IDs. Judge whether a design or a plan is needed by the [development workflow](workflow.md#starting-work); a lightweight change can use only the requirement entry and test tracing, and the tool does not require a new page because a design reference is missing. When an existing design still describes the behavior in question, keep it accurate, and do not write IDs into it in bulk to make up the references.

## 10. Optional: verification records and OKF export

For pages that go out of date, such as operations manuals, external facts, and investigation conclusions, write `Verified: agent:<name>, YYYY-MM-DD. Review by: YYYY-MM-DD.` under the title, and then register these paths in `verification.review_by_required` of `docs/wiki.json`. Paths that need a human gatekeeper are registered in `verification.human_required`. The format is under [Document model](../design/document-model.md#verification-records-and-review-by-dates).

When project knowledge has to be provided to tools that support the Open Knowledge Format, run `python3 scripts/wiki/wiki.py export-okf --root . --out <an empty directory outside the project>`. The export does not change how things are written in the repository; the directory and the rules are under [Configuration and rules](../../../scripts/wiki/en/reference.md#exporting-okf).

## 11. Register verification commands and reconciliation

Register the tests and checks that the target project must run in `verify` of `docs/wiki.json`, with each command written as an argument array and, where necessary, the working directory and the environment variables. After that, the verification record of a plan is generated with `python3 scripts/wiki/wiki.py verify --root .`, and agents no longer write command results and hashes by hand. `AGENTS.md` and the development standard write only this one command, and the list of commands is maintained in one place only, the configuration. The fields are under [Configuration and rules](../../../scripts/wiki/en/reference.md#verification-record).

When the documents contain a list that corresponds one to one with the code, such as rule names, configuration items, or environment variables, you can register `reconcile` so that `check` compares the lists on the two sides. Try it on one list first and see whether the false positives can be excluded with a small number of `ignore` entries; when there are more exclusions than items in the list itself, the list is not suited to reconciliation by regular expression. The fields are under [Configuration and rules](../../../scripts/wiki/en/reference.md#reconciling-documents-with-code).

## 12. Link to other repositories

When the system consists of several repositories checked out side by side (for example, when the build brings in a neighboring repository with `includeBuild('../OtherRepo')`), state the agreed checkout layout in the quick start of each repository, and then do the following:

1. Write cross-repository links as relative paths, not as absolute paths of your machine and not as inline code. Register the target repository in `repos` of `docs/wiki.json`; the form is under [Neighboring repositories and submodules](../../../scripts/wiki/en/reference.md#neighboring-repositories-and-submodules). When the target repository is checked out, `check` verifies the target file and the anchor; when it is not, there is only a warning, so it also passes when continuous integration checks out only one repository.
2. Submodules need not be registered. When one is not initialized, the links that point to it likewise only warn.
3. A cross-repository contract has its text only in the provider's repository, and the consumers link to it; the rules are under [Cross-repository contracts](../design/document-model.md#cross-repository-contracts). A README copied into another repository is changed into a short note that points to the canonical source.
4. After the links are written, first run `check --require-repos` once on a machine that has all the repositories checked out; a broken link for which `check` shows "Written as" has one `../` too few or too many.
5. In a worktree nested under another directory these links cannot be resolved, and the tool counts them as not checked out. A layout that places worktrees side by side, such as AIService, is not affected.

The reasons are in the [decision on cross-repository links](../../decisions/cross-repo-links.md) (in Chinese).

## 13. Adoption acceptance

- A new member can find the requirements, principles, design, source code, and tests from the entries.
- After the project template and the complete `scripts/wiki/` are copied to a temporary project, the agent entry can find the skill for syncing documents and committing, and all the local links of the skill can be opened, without going back to the source repository to read other files. When native discovery by the host is needed, verify it separately, and do not take the on-demand entries in `AGENTS.md` to mean that native discovery is in effect.
- An agent can find the related cross-module constraints during a local change.
- An ordinary query gets current documents first, and history can still be searched on demand.
- Current knowledge can be maintained in place, and finished plans can be archived by their original paths.
- The check for new documents, the check of the real staged snapshot, and the checks of independent modules have actual run results.
- A commit that changes only code shows the documentation reminder, and `doctor` shows that the three Git hooks are installed.
- An ordinary fix that does not change a contract described in the documents and does not reach the accumulated review threshold passes the hooks when only code and tests are committed, without updating a status page, adding a plan, or adding a review trailer.
- The documentation development workflow has been migrated to the shared baseline; the per-task and per-commit requirements of the old workflow have been checked one by one, duplicates and conflicts have been resolved by revising the original entry and its readers together, and the necessary exceptions conform to [Shared workflow and project adaptation](../../../scripts/wiki/en/workflow.md#shared-workflow-and-project-adaptation).
- When an execution suite is used as well, the project binding in the development entry can be found from the root `AGENTS.md`; the actual consumers follow the binding to the conventions for tasks, execution records, inbox items, verification, and archiving, and there is no other set of default paths that is still enforced. When only the documents were checked and the suite was not run, record this limitation explicitly.
- At least one requirement can be traced from its ID to a test, work that needs a design or a plan can also be traced to the matching documents, and `check` has no `trace-unknown-ref` errors.
- Writing problems and structure problems are reviewed separately, and a passing script is not taken to mean that the content is entirely correct.

After acceptance, write the valid rules of this adoption back into the knowledge of the target project; an existing plan keeps its verification record and the remaining items, and work without a plan records the basis and the verification results in the commit. When upgrading the tool later, review the changes in configuration and rules, to avoid silently changing the strength of the gate.
