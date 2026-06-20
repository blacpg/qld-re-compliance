# Answer Format

Shape the answer to the `question_type`, but always keep the sourced structure.

## Standard structure

**Short answer.** One or two sentences, plain practical English for an agent.

**Why (sourced).** A short list. Each point tagged:
`[authority_tier] Source title pinpoint (rule_id)`.

**Verification.** Only if a cited rule is not `verified`. State the status and what the agent should confirm.

**Practical next step.** The concrete action from `agent_action`.

**Escalation.** Only if `human_escalation_required`. State the specific reason.

## Variations by question_type

- `rule_check` — standard structure.
- `document_review` — go field by field through the document against the rules; list gaps as "missing / non-compliant / OK", each cited.
- `agent_script` — lead with `agent_wording.safe_version`, then `avoid_saying`, each tied to the rule that makes the wording risky.
- `risk_assessment` — lead with `risk_level` and the consequence, then the sourced basis, then escalation.
- `checklist` — return the steps from `agent_action` / `requirement`, each cited.
- `refusal` — use the Refusal Protocol; no substantive answer.

## Banned phrases

Never output: "I think", "probably legal", "you should be fine", or any legal conclusion without a `rule_id` and `source_id`.

## Required elements in any substantive answer

`rule_id`, `source_id`, `authority_tier`, and a practical next step must all be present. The behavioural eval (`scripts/run_eval.py`) checks for these.
