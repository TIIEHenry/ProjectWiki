# Design principles of the documentation system

> English translation of [文档系统设计原则](../../principles/document-system.md). The Chinese page is authoritative: if the two differ, the Chinese page applies.

Requirements: PW-03, PW-13, PW-15, PW-16, PW-26.

## Keep stable knowledge and the development process apart

`docs/` describes the current goals, boundaries, rules, and design of the project. `dev/` organizes the development process and records plans, pending matters, execution, verification, and handoffs. Important decisions that remain in force are kept in the ADRs of the knowledge scope they belong to. `archive/` keeps finished processes and content that as a whole no longer has anything to apply to.

A requirement that has been confirmed but not yet implemented is still knowledge. Task progress cannot change the validity of the requirement itself; when the source code and a requirement disagree, record the gap and the basis for handling it in the matching plan or in `dev/inbox/`.

## Make it readable to people first

Stable knowledge is for the people who need to understand the project. The text uses complete explanations and states the object, the conditions, the behavior, and the reasons. The fields, IDs, and directories that agents can search are auxiliary structure and cannot replace the text.

A title states the topic, and a summary states the content. Navigation says when something needs to be read. Avoid writing commit records, phase numbers, internal abbreviations, and running status updates into knowledge summaries. The specific requirements are in the [writing standard](../standards/writing.md).

## Provide context layer by layer, by task

The project entry provides the global hard rules and task navigation; a module entry provides responsibilities and related contracts; topic pages provide the details; source code and tests are used to confirm behavior.

Before starting a change, a developer should be able to answer what the goal and the acceptance are, which constraints apply, where the implementation is, and how to verify. When information is lacking, read further in a targeted way. A cross-module contract should list the provider and the consumers, so that a local change can discover the related impact. When a contract crosses repositories, its text is written only in the provider's repository, and the consumers link to it without restating the conclusions.

The budget of an entry takes the character count, the navigation items, and the necessary constraints into account together. First check the reading paths with one feature change and one maintenance task, and then write a character limit that suits the project into the configuration; when the limit is exceeded, move details out first and keep the rules that must be directly visible. The number of items is reviewed by people, and the tool at present enforces only the character budget. Limiting only the number of lines would let long lines hide the actual reading burden.

Registers that keep growing, such as deferred gaps, issue lists, and history indexes, should be searched by ID or keyword, reading only the matching lines and not the whole page. The entry has to state which files are of this kind and which keywords to search them with.

The signs that an entry has stopped working are these: the session conventions are changed to say that it should not be read in full, or a long standard has to be read through every time work starts. There has been an index navigation of about 200KB that was forbidden to be read in full, and another project required a documentation standard of about 26KB to be read through every time. When these signs appear, turn the entry back into short navigation, and change the registers that grow so that they are looked up by ID.

## Key rules are directly visible

Rules that affect changes across the whole project and that cause errors when ignored are written directly in `AGENTS.md`. A detailed standard can explain the background, the exceptions, and the steps, but following the key rules must not depend on the agent opening further links. Control sizes, call order, and local implementation constraints go in module documents and are not piled into `AGENTS.md`.

Inlined rules and the detailed text are kept consistent. One rule change needs both places to be reviewed; the existence of a clause number or a link proves only a structural relationship, not that the meaning is the same.

## Authoritative text and controlled summaries

Each rule has only one designated authoritative text. `AGENTS.md` may restate the hard rules that directly cause errors when ignored, but every restatement links back to the authoritative text; templates and the reference project keep only the short summaries needed for carrying things out and do not copy the complete explanation. When the authoritative text is changed, check by links and keywords whether the controlled summaries, the templates, and the examples are still consistent. The tool can list the link relationships that need review but cannot replace checking the meaning.

For the development workflow rules that the tool cannot enforce (the order from requirement to verification, which documents to update when a decision changes, the division of labor in reviews, when to archive), the authoritative text is `scripts/wiki/workflow.md`, which is copied with the tool. An adopting project follows this shared workflow by default; `AGENTS.md` links to it and does not copy these workflow rules into itself wholesale. The migration of an existing workflow and the necessary adaptation are under [Shared workflow and project adaptation](../../../scripts/wiki/en/workflow.md#shared-workflow-and-project-adaptation). `docs/guides/workflow.md` and `docs/design/lifecycle.md` are the complete texts for the people who develop ProjectWiki, with reasons and background; `workflow.md` is the condensed, executable version for adopting projects.

## One current text, several navigation entries

For one topic, within one scope of application and one version, one current text is designated. The development entry, the maintenance entry, and the module entries can link to it from different tasks and need not each write the explanation again.

Knowledge internal to a module goes in the module's `docs/`, and cross-module relationships go in the global design. The global module table points directly to the module entries, which avoids copying the lists of module topics by hand.

## Long-term knowledge is maintained in place

Requirements, principles, `module-structure.md`, and the current interface contracts are continuously updated in place, and the revision history is kept by Git. An ordinary content update does not trigger archiving of the whole page.

Archiving applies to finished work material, or to documents that as a whole no longer carry a current responsibility. A file of the same name in the archive does not prevent a standard document from being created, but the relationship between the two has to be checked and made clear.

A file name serves only as a navigation hint. The specific conventions for naming rules, placeholder templates, status words, and archive conflicts are in the [document model](../design/document-model.md#file-naming); do not turn file names into another status system with global numbers, status words, version numbers, or complex frontmatter. Whether to use a date prefix is up to the project, but a date may only denote a point in time that no longer changes, such as the date a review started, and a file must not be renamed as progress is made.

## Search scope and access rights are separate

Everyday search focuses on current knowledge by default, which reduces interference from the full text of history. An agent can widen the scope to the archive when the task needs it.

Search ignore rules, the index of current knowledge, and the full check have different scopes. Lifecycle and migration checks still have to cover history; excluding something from search must not hide structural problems in the archive.

## Automation keeps clear boundaries

Checking, generating, and moving are different operations. A report must state the input snapshot, the items actually checked, and the parts not covered. That one configuration check has passed cannot be used to claim that the whole contract has been verified.

Put directory locations, budgets, and rules in a common configuration, so that scripts do not each use a different scope. When adopting in an existing project, existing problems can be registered, but new problems must not be hidden by comparing total numbers of warnings.

## Rules differ in strength and leave projects room to adjust

Adopting projects differ in size, language, and existing documents. Directories and formats cannot require all existing content to be rewritten, so the rules of the tool come in three tiers. Adapting the configuration serves to express the actual structure of the project and does not mean that the original development workflow takes precedence over the shared workflow; workflow migration and exceptions follow [Shared workflow and project adaptation](../../../scripts/wiki/en/workflow.md#shared-workflow-and-project-adaptation).

| Tier | What it includes | Whether it can be adjusted |
|---|---|---|
| Invariants | Violating them would distort the tool's conclusions or lose content: an incomplete check cannot be reported as passed; the staged check reads only the captured Git index, plus the HEAD commit that each registered neighboring repository had when the check started; archiving and creating do not overwrite existing files; the local links and anchors of current documents must be valid; requirement IDs, review finding IDs, and current document identities are not duplicated within one scope | Fixed as errors. When an old repository adopts, existing problems can only be accepted temporarily through the baseline of existing problems, and new problems fail as usual |
| Default conventions | Directory locations, status values, the requirement ID format, file naming, page budgets, reminder thresholds, the structure of review files | The tool provides defaults, and a project adjusts them in `docs/wiki.json` to its own structure |
| Rules that need human judgment | Writing style, when to write a decision record, which capabilities to enable at adoption | Judged by the conditions in the shared workflow and the standards, with no machine check; a rule must not be ignored because the tool does not check it |

Among the default conventions, the verdict words and the finding ID format of reviews cannot be configured yet. Setting `reviews` to an empty list turns the review checks off, but turning the checks off does not exempt a project from the review requirements of the shared workflow; when another format really has to be kept, complete the adaptation by the shared workflow, and do not switch the checks off merely because there is already a review process.

Some errors come from limitations of the tool itself rather than from requirements on the documents. For example, the path of a new document cannot contain spaces because archiving cannot yet rewrite such links safely; once the tool can handle them, rules of this kind should be lowered to default conventions.

Three points are observed when adjusting default conventions:

- Existing content is registered by preference and is not rewritten in order to pass the checks. For existing requirement IDs, directories, and file names, register their format and location in the configuration, and do not rename in bulk. For requirements made only of new files (status lines, entries, directory budgets), mark off what already exists with the registered adoption commit, and do not confine the new rules to a dedicated subdirectory. The existing workflow is migrated separately by the shared baseline, and two workflows must not be applied on top of each other because content is kept; the adoption steps are in the [adoption guide](../guides/adoption.md#1-read-projectwiki-and-survey-the-target-project).
- Relaxations have to be visible. An adjustment is written in the configuration, with the reason stated in the commit message, so that reviewers can see which default conventions have been changed.
- Add a configuration item only when a real project finds that a default convention does not fit, and do not add switches in advance for hypothetical projects. A new check goes live as a warning first and is raised to an error after real projects have confirmed that its false positives are acceptable.

## Keep the number of documents down

When something can be written as a section of an existing file, do not create a new file. Only two cases get a document of their own: the content has a lifecycle of its own and needs to be scheduled, updated, and archived separately; or several people need to write at the same time and would conflict with one another if it were kept together.

If a new file is created for every step, the number of files multiplies with the rounds, the participants, and the models. The development directory of one project studied as a reference accumulated more than four thousand documents, two thousand of which were review, audit, and sign-off drafts; one review with 80 findings used 43 files. The round, the model, and the date of each verification should be written in the text and not in the file name; the start date in the name of a review directory only marks which review this is, and no files are added as the rounds go on. A directory can be given a file-count budget in the configuration, and when it is exceeded the checker reminds you to merge or archive; the project template sets default budgets for the plan, inbox, and review directories.

A way of registering with one file per item, such as the inbox, must also specify how each item ends. If only how to create is specified and not how to end, the number of files can only grow.

## The workflow expands with impact

An ordinary fix can reuse the commit or an existing work record. For new features and behavior changes, the documents needed are also judged by impact: when the boundary is clear, no multi-step collaboration or handoff is needed, and there is no significant risk or contract change, a requirement entry and tests are enough to complete the tracing. When there are important trade-offs, cross-module contract changes, data migration, or collaborative handoffs, add the matching design, plan, and decision. When existing knowledge describes things wrongly, it still has to be updated.

Reducing the number of files does not exempt anyone from the applicable rules and verification. Nor can increasing the number of files replace actual analysis. The division of labor among ADRs, plans, and the roadmap is in the [development workflow](../guides/workflow.md).

The signs that the workflow is too heavy are these: even an ordinary fix has to rewrite several progress pages every time; a review rebuilds the whole set of reports in every round; the reasons for fixes all become separate ADRs; document review records use the same sentence over and over without adding any conclusion from checking. When these signs appear, examine the trigger conditions, the duplicate records, and the ways of ending one by one, and cut the workflow down by impact.

Feedback from an adoption survey provided these figures: measured at the adoption commit `28b95a4c0a` of UniverseAgent (2026-10-30), the process records under `dev/` made up 84% of all Markdown lines; of the 6,510 commits from 2026-08-01 to 2026-09-27, 76% changed the same status page. These numbers come from the survey feedback and are limited to that repository and that sample period; they do not serve as a budget or as an automatic threshold for other projects. When judging the burden, also check whether these records produce useful conclusions.

For a documentation requirement that applies to every commit, the cost has to be multiplied by the commit frequency. Even when each time takes very little, it can take up a great deal of effort when commits are frequent. Before adding a requirement of this kind, state what problems it can find and why it has to be carried out every time; sync checks that need not be handled every time are triggered by the accumulated amount, and the exact boundaries are under [Documentation reminders at commit time](../../../scripts/wiki/en/reference.md#documentation-reminders-at-commit-time).
