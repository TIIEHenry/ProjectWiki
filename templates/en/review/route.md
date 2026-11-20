# [TODO: route number] [TODO: scope]

Scope: [TODO]. Reviewer: [TODO]. Baseline commit: [TODO].

Each finding is a level-two heading that begins with the finding ID. The ID is unique within the whole review and does not change from discovery through sign-off and implementation. Verification results are written directly into the section of the finding, and no separate verification file is created; a second round and a check by a different person each append a row to the verification table.

## r01-1 [TODO: the finding in one sentence]

Status: pending.

**Observation** (Author: [TODO: `human:<name>` or `agent:<name>`], [TODO: date])

[TODO: facts that can be reproduced: files and line numbers, commands and output, commit IDs. This paragraph is not changed once verification has started.]

**Conjecture**

[TODO: possible causes and the extent of the impact. Delete this paragraph when there is none.]

**Verification**

| Round | Checker | Verdict | Basis |
|---|---|---|---|
| 1 | [TODO: `human:<name>` or `agent:<name>`, not the author] | [confirmed / narrowed / rejected / known / duplicate] | [TODO: the files and line numbers opened, the commands run, and the commit ID at the time of verification] |

About the verdicts: narrowed has to say clearly which part does not hold; known has to link to the existing plan, gap, or decision; duplicate has to give the ID it repeats. When verification is finished, change the status at the top of the section to the verdict of the last round.

**Plan**

[TODO: write this only for a confirmed or narrowed finding. When a fix spans several findings and needs to be scheduled on its own, write one line that links to `plan-<topic>.md` in the same directory, and list the IDs in that plan with `Covers:`.]

**Sign-off**

[TODO: signed / signed (narrowed) / not signed, with the signer and the date.]
