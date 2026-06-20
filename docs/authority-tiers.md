# Authority Tiers and Conflict Rules

Every rule and every answer is labelled with exactly one authority tier. The tier tells the agent how much weight a statement carries.

## The tiers (ranked)

| Tier | Meaning | Weight |
|---|---|---|
| `legislation` | Acts (e.g. Property Occupations Act 2014, Property Law Act 2023) | Binding legal obligation |
| `regulation` | Regulations (e.g. Property Occupations Regulation 2014) | Binding legal obligation |
| `statutory_form` | Approved or prescribed form required in context (Form 6, Form 2, Form 8) | The form satisfies or evidences an obligation that the Act or Regulation creates. The form itself is not "the law". |
| `regulator_guidance` | OFT and ACCC guidance | Regulator interpretation and practical guidance. Persuasive, not law. |
| `industry_commentary` | REIQ, law-firm articles | Informative only |
| `internal_policy` | Agency house rules (private overlay) | Private business rule, not law |

## Important wording distinction

A statutory form is mandatory in its context, but the obligation comes from the legislation, not from the form. For example, Form 2 is the approved Seller Disclosure Statement under the Property Law Act 2023; the Act creates the disclosure obligation, and the form is the approved way to satisfy part of it. Say "the Act requires disclosure, given using the approved Form 2", not "the form is the law".

## Conflict resolution rules

These are enforced by the skill:

1. **Commentary vs law.** If industry commentary conflicts with legislation or regulation, legislation or regulation wins. Commentary is set aside.
2. **Guidance vs law.** If regulator guidance appears inconsistent with legislation, the skill flags the conflict and does **not** resolve it as legal advice. It surfaces both and recommends escalation to the OFT or a solicitor.
3. **Internal policy stricter than law.** If internal policy is stricter than the law, the statement is phrased "Blac policy requires X", never "the law requires X".
4. **Commentary alone is never mandatory.** A rule whose only sources are `industry_commentary` cannot use mandatory ("must", "required") language. Tier 5-only answers are advisory, and the skill says so.

## Practical effect on answers

When the skill answers, it groups statements by tier so the agent can see at a glance what is binding law versus guidance versus house rule. A high-stakes "must" with only a tier 4 or tier 5 source is downgraded to "guidance suggests" and flagged.
