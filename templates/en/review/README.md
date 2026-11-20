# Review: [TODO: topic]

Status: active. Scope: [TODO: the code or documents under review]. Baseline commit: [TODO: the commit ID when the review starts]. Owner: [TODO: `human:<name>` or `agent:<name>`].

One review lives in one directory: `dev/reviews/<start date>-<topic>/`. The route files and the plans all go here, and the whole directory is archived when the review ends.

## Scope and method

[TODO: the questions to be answered, the way of reviewing (read-only reading, running tests, comparing with the documents, and so on), and what is outside the scope of this review.]

## Routes

The number of routes and the way of dividing them are decided as needed and do not have to match the modules. A scope can be a module, a topic, a question, a group of files, or a class of defects. Route numbers are assigned in this table by the person who consolidates the review; a route added later is also registered here first, with its number, the date it was added, and the reason, before its reviewer starts writing, so that two parallel routes cannot take the same number. When there is only one route, the findings can be written directly in this file, without a route file.

| Route | Scope | Method | Reviewer | File |
|---|---|---|---|---|
| r01 | [TODO] | [TODO] | [TODO] | [r01-TODO: short name of the scope](r01-TODO.md) |

## Verification groups

[TODO: who verifies which routes, for example "agent:reviewer-a covers r01–r03". A checker is written as `human:<name>` or `agent:<name>` and must not be the author of the finding. Delete this section when there are no groups.]

## Summary and sign-off

The verdict on each finding is written in the finding's own section; this table only summarizes. It is updated by the person who consolidates the review, and the reviewers of the routes do not change it.

| ID | Verdict | Plan | Sign-off |
|---|---|---|---|
| [TODO] | [confirmed / narrowed / rejected / known / duplicate] | [in the section / plan file / none] | [signed / signed (narrowed) / not signed / pending] |

## Conclusions and where they go

[TODO: which design, requirements, or decisions the conclusions that still hold were written back into; which findings were handed over to the roadmap or to the deferred gaps. When all the plans are complete, change the status to `finished` and archive the whole directory.]
