# ProjectWiki specification

> English translation of [ProjectWiki 规范](../INDEX.md). The Chinese page is authoritative: if the two differ, the Chinese page applies.

This is the specification of the documentation system itself: how an adopting project organizes its documents, and how it maintains and checks them. The business documents of the reference project are in [`demo-en/docs/`](../../demo-en/docs/INDEX.md).

| When to read | Document |
|---|---|
| Confirming the requirements the system has to meet and their acceptance criteria | [Requirements](../requirements/projectwiki.md) (in Chinese) |
| Deciding how documents are classified, referenced, and expanded | [Design principles](principles/document-system.md) |
| Looking up the responsibilities of the directories of this repository | [Directory and module structure](design/module-structure.md) |
| Judging the validity of current knowledge, process records, and history | [Document model](design/document-model.md) |
| Creating, moving, or archiving documents | [Lifecycle and archiving](design/lifecycle.md) |
| Running, adopting, or extending the checker | [Automation design](design/automation.md) |
| Arranging requirements, plans, ADRs, and reviews | [Development workflow](guides/workflow.md) |
| Understanding why plans and decisions write their status in the first line of the text | [Status line decision](../decisions/status-line.md) (in Chinese) |
| Understanding how requirement IDs run through design, plans, and tests | [Requirement traceability decision](../decisions/requirement-traceability.md) (in Chinese) |
| Understanding the trade-offs of verification records, review-by dates, and OKF export | [Verification record and OKF decision](../decisions/verification-line-and-okf.md) (in Chinese) |
| Understanding which steps are handed to the tool and which are still judged by people or agents | [Decision on automating mechanical steps](../decisions/automation-writes.md) (in Chinese) |
| Understanding how links to other repositories are written, registered, and checked | [Cross-repository links decision](../decisions/cross-repo-links.md) (in Chinese) |
| Creating or reviewing Chinese technical documents | [Writing standard](standards/writing.md) |
| Changing the code, templates, or examples of ProjectWiki | [Development standard](../standards/development.md) (in Chinese) |
| Adopting this system in an existing project | [Adoption guide](guides/adoption.md) |
| Creating new content from a template | [Template notes](../../templates/en/README.md) |
| Looking up how status lines, verification lines, requirement entries, and review findings are written, and how IDs are assigned | [Formats the checker reads](../../scripts/wiki/en/formats.md) |

The specification is edited in place, and old versions are kept by Git. What has not been done yet is in the [to-do list](../../TODO.md) (in Chinese), and version changes are in the [changelog](../../CHANGELOG.md) (in Chinese).
