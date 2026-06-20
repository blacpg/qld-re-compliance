# Answer Format

Shape the answer to the `question_type`, but always keep the sourced structure.

## Standard structure

**Short answer.** One or two sentences, plain practical English for an agent.

**Why (sourced).** A short list. Each point tagged:
`[authority_tier] Source title pinpoint (rule_id)`.

**Verification.** Only if a cited rule is not `verified`. State the status and what the agent should confirm.

**Practical next step.** The concrete action from `agent_action`.

**Escalation.** Only if `human_escalation_required`. State the specific reason.

## Variations by question_type (what the user asked for)

- `rule_check` — standard structure.
- `document_review` — go field by field through the document against the rules; list gaps as "missing / non-compliant / OK", each cited.
- `agent_script` — lead with `agent_wording.safe_version`, then `avoid_saying`, each tied to the rule that makes the wording risky.
- `risk_assessment` — lead with `risk_level` and the consequence, then the sourced basis, then escalation.
- `checklist` — return the steps from `agent_action` / `requirement`, each cited.

## answer_outcome (how it resolves)

Refusal is an outcome, not a question type. Every answer resolves to one of:

- `answered` — sourced answer from a matching, sufficiently verified rule.
- `refused_unsourced` — no cited rule covered it; use the Refusal Protocol.
- `refused_out_of_scope` — outside QLD property sales; refuse and route.
- `escalated` — answered but flagged for human escalation, with the reason.
- `uncertain` — a matching rule exists but is `unverified` / `needs_review`; say so plainly and do not present it as settled.

Any question_type can end in any outcome. A `document_review` can be `answered`, `uncertain`, `escalated`, or refused.

## Banned phrases

Never output: "I think", "probably legal", "you should be fine", or any legal conclusion without a `rule_id` and `source_id`.

## Required elements in any substantive answer

`rule_id`, `source_id`, `authority_tier`, and a practical next step must all be present. The behavioural eval (`scripts/run_eval.py`) checks for these.
