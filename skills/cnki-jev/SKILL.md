---
name: cnki-jev
description: Optional paid Jev-assisted CNKI title/abstract screening with per-condition proposals, budget accounting, and escalation to evidence-based LLM or human review. Use when the user chooses Jev screening or a shadow comparison.
---

# CNKI Jev 辅助筛选（可选，调用付费）

Requires cnki-screening and cnki-resume. The base bundle works without this skill.
Installation never enables calls. The helper uses Python 3.9+ standard library and
TypeSafe's official hosted API; it does not browse CNKI or read/upload full text.

## Before enabling

Read [configuration and workflow](references/usage.md). Preserve existing task
criteria and authorized scope. User authorization must cover paid calls, a budget,
and transmission of the task's titles/abstracts to TypeSafe. If these were already
specified, use them without asking again. Otherwise obtain only the missing choices.
The user configures TYPESAFE_API_KEY in their environment; never ask them to paste
it into a conversation, config file, task ledger or repository. Do not purchase
credits or create an account as an implicit setup step.

Start with the supplied disabled config. `shadow` and `assist` both incur fees;
`off` does not. State that the local USD budget is an estimate based on a configured
rate, not a provider-enforced billing cap; the call-count limit is enforced locally.
Keep the task and its adjacent `.jev.sqlite` together across retries/resumes.

## Screening

1. Freeze/import the actual result set with cnki-resume. Match `criteria` exactly
   and decompose all necessary inclusion conditions into atomic questions. Check
   coverage against the research question; do not silently drop/change conditions.
2. Run the helper for each eligible paper, reusing the same task and configuration.
   Only title and abstract are sent. Missing abstracts return to baseline review.
3. `shadow`: let the baseline LLM/human make an independent decision before comparing
   the saved Jev proposal. Do not use Jev's suggestion as the evaluation reference.
   `assist`: an inclusion proposal proceeds to source-evidence verification;
   exclusions and uncertain/complex/conflicting cases go to baseline LLM/human review.
   A high probability is not demonstrated accuracy. The supplied threshold is an
   uncalibrated starting value, not permission for automatic exclusion.
4. Read the actual source and save the final `include/exclude/uncertain` decision,
   criterion-linked reason and exact evidence using the existing `screen` command.
   Include the proposal provenance in that record (see reference). Never submit a
   proposal as a final screening record, fabricate a quote, or treat missing text
   as a failed criterion. Full-text reading, when needed, stays in the base workflow.
5. Report candidates, final decisions, unresolved reviews, actual route, request
   count and estimated usage/reserved budget separately. Export the usual workbook
   plus local Jev proposals if requested. Never upload private ledgers, abstracts,
   proposal files or credentials to GitHub as part of publishing the skill.

On API/configuration/budget failure, honor `on_failure`: baseline means the agent
continues ordinary screening; pause means preserve progress and stop that portion.
The helper routes work but does not itself invoke a second model. It never retries
an uncertain paid request automatically. See the reference for manual failed-call
retries and crash recovery. Do not reset/delete the sidecar to evade a budget.
