# Standard for Chinese technical documents

> English translation of [中文技术文档规范](../../standards/writing.md). The Chinese page is authoritative: if the two differ, the Chinese page applies.

## Scope

This standard applies to requirements, principles, design, guides, and explanations of decisions that need to be read over the long term. Execution records can be brief, but still have to distinguish facts, conjectures, and pending matters.

## Before writing

First make clear the problem the reader wants to solve, the scope of the document, and the existing authoritative text. Search current knowledge and the matching history, and confirm whether a new file is needed or an existing page should be revised.

Choose a title for the text that describes its content. The summary states the content in one or two sentences and does not record the development log. When to read it is written beside the link in the index or the navigation.

## Writing the text

- Use a concrete object as the subject, and describe the action, the conditions, and the result directly.
- When explaining the reasons for a design, give the problem, the constraints, and the trade-offs. Keep the necessary details and delete repeated conclusions.
- Use complete paragraphs. Parallel items suit a list, and comparisons suit a table; do not break every sentence into a paragraph of its own.
- Use the same name for the same concept. A necessary abbreviation should be explained at its first appearance, and names used inside the project should be replaced with expressions that outside readers can understand.
- Distinguish the specification from the present state. When a target capability has not been implemented yet, say so explicitly, and do not write a plan as behavior that already exists.
- Distinguish observation from conjecture. Give sources that can be rechecked, and for unverified judgments note the basis and the limitations.
- An operation guide states clearly the prerequisites, the steps, the expected results, and the way to verify. Example code should match the current implementation.
- A troubleshooting guide is organized by the symptoms the reader sees: the heading of each section is one symptom, and the text first says what to check first and then where the evidence is, without a system overview first. For an example, see the [fault maintenance guide](../../../demo-en/docs/guides/maintenance.md) of NoteBox. When there are many entries, a table with the three columns "symptom / check first / evidence" can be used.
- A cross-module contract states the provider and the consumers: which module defines it, which modules depend on it, and who has to be notified when it changes. When a contract crosses repositories, its text is written only in the provider's repository, and the consumers link to it without restating it (see [Cross-repository contracts](../design/document-model.md#cross-repository-contracts)).
- Internal names that recur in the project are collected in a glossary (for example `docs/glossary.md`), with a definition, a scope of application, and a link to the authoritative text for each. The text links to the glossary at first use and does not explain the name again in every page.

## Screenshots, prototypes, and wireframes

The text can reference assets in any format: screenshots, HTML prototypes, `.canvas.tsx` wireframes, exported JSON. An asset is placed beside the document that references it; a subdirectory is created only when the assets of one feature become numerous, and no fixed `assets/` structure is assumed in advance.

- State the purpose when referencing, for example "wireframe: layout of the bottom bar divider" or "competitor screenshot, for comparison only".
- Write out in words the conclusions drawn from the asset: sizes, order, states, interaction rules. Readers and agents may not be able to open or understand images and prototypes; the asset serves only as supporting evidence, and the text is what counts for the rules.
- While an asset still describes the current interface, it is maintained in place like the text; after the whole design is superseded, it is archived together with the text. Do not archive an old image for every revision; old versions are kept by Git.
- The checker verifies that asset links exist but does not read the content of assets.

## Common rewrites

| Problem | Unsuitable expression | Suggested expression |
|---|---|---|
| Empty lead-in | "It is worth noting that this solution can effectively empower the development process." | "The index provides entries to the source code and the tests, and developers can locate where to change from the module description." |
| Translationese | "Perform the execution of the loading of the configuration." | "Load the configuration." |
| Internal jargon | "This cut closes the loop; we wrap it up next round." | "This change adds timeout handling; the next task verifies the behavior after a retry fails." |
| Overstated effect | "Comprehensively solves all documentation consistency problems." | "Checks local links and the registered configuration fields; the semantics of the design still need review." |
| Progress summary without basis | "Phase 12 all green, phase 13 done." | Describe the current behavior in the knowledge page, and write the execution results into the matching task record. |
| Subjective description | "This is an elegant and powerful design." | State what duplicated content it reduces and the conditions for adopting it. |

Use a connective at the start of a sentence only when it really expresses a logical relationship. Delete summaries that add no information, preemptive rebuttals, and slogan-like sentences. Avoid copying foreign sentence patterns word for word; where necessary, break up long attributive phrases and adjust the word order.

## After writing

1. Read the whole text from the title to the end, and confirm that a developer who is not part of the current session can also understand it.
2. Check the terms, the links, the code examples, and the scope.
3. Check whether task logs, outdated examples, or unexplained internal abbreviations have slipped in.
4. Check whether every judgment has a clear object, conditions, and basis.
5. Run the documentation check, deal with the structure problems, and then review whether the rewriting has changed the original meaning.

Keyword search can help find suspicious expressions, but it cannot be used to assert that a text was written by AI, nor can all connectives be mechanically listed as errors. A style review goes by reading sentence by sentence.
