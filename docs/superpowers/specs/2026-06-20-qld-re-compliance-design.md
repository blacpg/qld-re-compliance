# Queensland Real Estate Compliance Assistant — Design Spec

Date: 2026-06-20
Status: Approved design, pending implementation plan
Author: Antony Thompson (Blac Property Group) with Claude
Australian English throughout. No reproduction of Crown-copyright source text.

---

## 1. Purpose and non-goals

### Purpose
A source-backed compliance assistant for Queensland real estate agents, delivered as a Claude Code skill. It answers property-sales compliance questions **only** from structured rule files, and every answer cites the exact legislation, regulation, approved form, or regulator guidance it relies on.

### Core contract
- **No rule file, no answer.** If no rule covers the question, the skill refuses and points to the Office of Fair Trading (OFT) or a solicitor. It does not improvise law.
- **Verify or flag.** Every pinpoint citation (section, clause, form field) is verified against the official source at build time. If a pinpoint cannot be verified in-session, the rule ships as `verification_status: unverified` with a visible note. A guessed citation is never published.
- **Separate the layers.** Official law, regulator guidance, industry commentary, and internal agency policy are kept in distinct authority tiers and labelled on every answer.

### Non-goals (v1)
- Not legal advice, and not a substitute for OFT or a solicitor.
- Not residential tenancy / property management (sales only).
- Not other jurisdictions (QLD only, but `jurisdiction` is recorded everywhere so NSW/VIC can be added later without retrofit).
- No RAG server, no app. The skill loads rule files directly, the same way the user invokes other Claude Code skills.

### Honest limit
A skill cannot physically stop a model recalling law from memory. The design makes "no rule file, no answer" the hard default, forces a citation against every assertion, and polices the behaviour with eval scenarios. That is the realistic enforcement model.

---

## 2. Runtime behaviour (the answer loop)

`SKILL.md` enforces a fixed sequence:

1. **Classify question_type** before anything else (see §7). "Can I say this to a buyer?" needs a different answer shape to "Review this Form 6".
2. **Select module** (Form 6, commission, marketing/price, offers, disclosure).
3. **Load** only the matching rule file(s) from `rules/`.
4. **Answer strictly from loaded rules.** Every assertion maps to a `rule_id` and a `source_id`.
5. **Refuse when unsourced.** No matching rule => refusal protocol.
6. **Surface verification status.** If a rule is `unverified`, `partially_verified`, or `needs_review`, that is stated up front, not buried.
7. **Apply authority tier + conflict rules** (see §4).
8. **Escalate when required** (see `human_escalation_required`), with the specific reason, not a generic "see a solicitor".

---

## 3. Repository structure

```
qld-re-compliance/
├── README.md                      # credible, scoped, "not legal advice" near the top
├── DISCLAIMER.md                  # full disclaimer, linked everywhere
├── LICENSE                        # MIT for schema/scripts; content terms noted separately
├── CONTRIBUTING.md                # a rule may only cite an already-registered source
├── CHANGELOG.md
├── .gitignore                     # ignores internal/ overlay and any PII
│
├── skill/qld-property-compliance/
│   ├── SKILL.md                   # answer loop, refusal protocol, tier + conflict rules
│   └── references/
│       ├── refusal-protocol.md
│       ├── citation-style.md
│       ├── answer-format.md
│       ├── escalation-rules.md
│       └── glossary.md
│
├── sources/
│   └── register.yaml              # every source: id, type, tier, url, version, dates, licence
│
├── rules/
│   ├── form-6-appointment/
│   ├── commission/
│   ├── marketing-and-price/
│   ├── offers-and-negotiation/
│   └── seller-disclosure/
│
├── modules/
│   └── modules.yaml               # MVP module index + question_type taxonomy
│
├── schema/
│   ├── rule.schema.json
│   ├── source.schema.json
│   └── scenario.schema.json
│
├── tests/
│   ├── scenarios/                 # 20 compliance-question scenarios (YAML)
│   └── expected-answer-rules/     # must_include / must_not_include assertion sets
│
├── docs/
│   ├── source-ingestion-standard.md
│   ├── authority-tiers.md
│   ├── legal-and-copyright.md
│   ├── public-content-policy.md
│   ├── sources-to-obtain.md
│   └── review-cadence.md
│
├── internal.example/
│   └── internal-policy.example.yaml   # redacted template; real internal/ is gitignored
│
└── scripts/
    ├── validate_rules.py          # JSON Schema validation of every rule
    ├── validate_sources.py        # register integrity
    ├── check_stale_sources.py     # next_review_due / last_source_check overdue detection
    ├── citation_coverage.py       # every rule has >=1 registered source; tiers consistent
    └── run_eval.py                # OPTIONAL, needs API key: runs skill vs scenarios
```

`internal/` (real Blac policy) is gitignored. `internal.example/` ships a redacted template so the slot is visible to anyone who clones the public repo.

---

## 4. Authority tiers and conflict rules

### Tiers (ranked, labelled on every rule and every answer)
1. **legislation** — Acts. Binding legal obligation.
2. **regulation** — Regulations. Binding legal obligation.
3. **statutory_form** — approved or prescribed form required in context. The form satisfies or evidences an obligation that the Act/Regulation creates; the form itself is not "the law".
4. **regulator_guidance** — OFT, ACCC. Regulator interpretation / practical guidance. Persuasive, not law.
5. **industry_commentary** — REIQ, law-firm articles. Informative only.
6. **internal_policy** — agency house rules. Private overlay.

### Conflict resolution rules (encoded in SKILL.md and authority-tiers.md)
- If industry commentary conflicts with legislation or regulation, **legislation/regulation wins**.
- If regulator guidance appears inconsistent with legislation, **flag the conflict and do not resolve it as legal advice**. Surface both and recommend escalation.
- If internal policy is stricter than the law, say **"Blac policy requires X"**, never "the law requires X".
- Commentary (tier 5) can **never** be the sole basis for a "you must" answer. Tier 5-only => advisory, and the skill says so.

---

## 5. Rule schema (YAML)

Reconciliation note: `status`, `verification_status`, and `risk_level` are three independent fields. A rule can be `active` + `verified` + `risk_level: high`.

- `status` (lifecycle): `active | draft | superseded | retired`
- `verification_status` (sourcing quality): `verified | partially_verified | unverified | needs_review`
- `risk_level` (consequence if the agent gets it wrong): `high | medium | low`

```yaml
id: RULE-FORM6-001
title: Form 6 appointment required before acting
jurisdiction: QLD
module: form-6-appointment
question_types:
  - rule_check
  - checklist

status: active
verification_status: verified
verification_note: null         # required (non-empty) when verification_status != verified
risk_level: high
authority_tier: legislation

applies_when:
  - A property agent is appointed to sell residential property in Queensland.

does_not_apply_when:
  - The question relates to property management or residential tenancy advice.
  - The question relates to another jurisdiction.

requirement: "Plain-English practical rule the agent acts on."
detail: "Longer explanation, still source-backed."

sources:
  - source_id: SRC-POA-2014
    pinpoint: "s 102"
    source_role: primary        # primary | supporting
    quote: null                 # optional, <=25 words, only if wording is decisive

agent_action:
  - "Check the appointment is complete before marketing or performing services."
  - "Confirm dates, commission, expenses and signatures are all completed."

agent_wording:
  safe_version: null
  avoid_saying: []

exceptions: []
penalty: null                   # cited only if the Act/Regulation specifies one

human_escalation_required: false
escalation_reason: []           # e.g. commission recovery, contract termination, disclosure defect, trust account, OFT complaint risk

related_rules:
  - RULE-FORM6-002

last_source_check: 2026-06-20
next_review_due: 2026-09-20
tags:
  - appointment
  - form-6
```

### Schema enforcement
- `verification_status != verified` requires a non-empty `verification_note`.
- Every `source_id` in `sources` must exist in `sources/register.yaml`.
- A rule whose only sources are tier `industry_commentary` cannot use mandatory language in `requirement` (lint check).

---

## 6. Source register and ingestion standard

### The gate
A rule may only cite a `source_id` that already exists in `sources/register.yaml`. No registered source, no rule.

### Register entry fields
`source_id`, `title`, `jurisdiction`, `type` (act / regulation / statutory_form / regulator_guidance / industry_commentary / internal_policy / case), `authority_tier`, `publisher`, `official_url`, `version_or_as_at` (every cite pinned to a date/version), `retrieved_date`, `licence`, `pinpoint_style`, `notes`.

### Rules
- Source must be the **official publisher** (legislation.qld.gov.au, oft.qld.gov.au, accc.gov.au), never a third-party summary.
- Excerpts capped at 25 words, only where a rule turns on exact wording.
- `version_or_as_at` is mandatory so stale law is never presented as current.

---

## 7. Modules and question_type classifier

### question_type (first-level classifier, before module selection)
`rule_check | document_review | agent_script | risk_assessment | checklist | refusal`

### MVP modules (v1, QLD property sales only)
| Module | Covers |
|---|---|
| `form-6-appointment` | Valid appointment, mandatory fields, commission disclosure on the form, sole vs open, term, reappointment, withdrawal |
| `commission` | How commission may be expressed, written agreement, disclosure, sharing/referral, no recovery without a valid appointment |
| `marketing-and-price` | Auction/no-price marketing, "offers over", price guides, misleading price representations (POA + ACCC) |
| `offers-and-negotiation` | Multiple offers, no duty to disclose other offers' terms, no dummy/fictitious offers, misleading conduct |
| `seller-disclosure` | Property Law Act 2023 scheme, Form 2 contents, when disclosure is due, Form 8 buyer angle, termination consequences |

---

## 8. Testing strategy

Two layers, with an explicit boundary.

### Deterministic validators (run in CI on every commit)
- `validate_rules.py` / `validate_sources.py` — JSON Schema conformance.
- `citation_coverage.py` — every rule has >=1 registered source; tier/language consistency.
- `check_stale_sources.py` — fails or warns when `next_review_due` is past or `last_source_check` is older than the cadence.

### Behavioural eval (run on demand, needs an API key)
- `run_eval.py` executes the skill against `tests/scenarios/` and checks per-scenario assertions:
  - `must_include`: `rule_id`, `source_id`, `authority_tier`, `practical_next_step`.
  - `must_not_include`: unsourced legal conclusion, "I think", "probably legal", "you should be fine".
- Not part of CI, because a public repo has no key. Documented as a manual/periodic gate.

### Scenario coverage (first 20)
- ~3 refuse cases (out of scope: tenancy, another state, tax advice).
- ~2 uncertain cases (genuinely unsettled points) proving the tool flags rather than asserts.
- The rest direct sourced answers, each with `expected_rule_ids` and `expected_source_ids`.

---

## 9. Public vs private (two-layer architecture)

### Public layer (the repo everyone sees)
Source register, schemas, general rules, public checklists, public skill, disclaimer, content policy.

### Private Blac overlay (`internal/`, gitignored)
Blac process, stricter house rules, internal scripts, preferred wording, escalation contacts, form review checklist, agency risk appetite. Example record:

```yaml
id: BLAC-POLICY-MULTIPLE-OFFERS-001
jurisdiction: QLD
linked_public_rules:
  - RULE-OFFERS-001
policy: "All multiple-offer situations must be confirmed in writing before the seller signs."
reason: "House standard to reduce dispute risk."
owner: "Antony"
```

The skill loads the overlay if present, and any overlay-derived statement is phrased as "Blac policy requires...", never "the law requires...".

---

## 10. Legal, copyright, and content policy

### Risks and mitigations
| Risk | Mitigation |
|---|---|
| Crown copyright in QLD legislation | Cite + link to legislation.qld.gov.au; no full-text mirroring; <=25-word excerpts |
| OFT forms (Form 6/2/8) are Govt copyright | Never commit the form files; link to the OFT download page |
| Construed as legal advice / unqualified practice | Prominent DISCLAIMER, scope limits, "verify against source" |
| A wrong rule misleads an agent | verification_status flags, review dates, refuse-when-unsourced |
| Client PII leaking in | Gitignore internal/; no real client data; example overlay redacted |
| Stale law presented as current | Every cite pinned to version_or_as_at; review cadence enforced |

### Public content policy (`docs/public-content-policy.md`, hard rules)
No paid templates. No REIQ member-only content. No contract templates unless clearly licensed. No client files. No internal agency procedures in public. No copied full legislation. Cite and link only.

### Sources: obtain / link / avoid
- **Link & cite (never commit):** Property Occupations Act 2014, Property Occupations Regulation 2014, Property Law Act 2023 + Property Law Regulation 2024, OFT guidance pages, ACCC false-or-misleading-representations guidance.
- **Download for own reference only (don't commit):** the actual Form 6 and Form 2 from OFT, to write accurate field-level rules.
- **Avoid entirely:** paywalled REIQ content, law-firm article text (link only), third-party PDFs of the legislation.

---

## 11. Review cadence (`docs/review-cadence.md`)

- Default: `next_review_due` = `last_source_check` + 90 days.
- **Seller disclosure** reviewed more often (60-day cadence): the QLD seller disclosure scheme commenced 1 August 2025 and is likely to keep generating guidance updates, so it carries extra caution.
- `check_stale_sources.py` enforces the cadence in CI.

---

## 12. Build order (the five v1 rule files)

In each, every pinpoint is verified against the official source before it is marked `verified`; anything unverifiable in-session ships as `unverified` with a note.

1. `form-6-appointment` — appointment required before acting, mandatory contents, commission disclosure.
2. `commission` — expression, written agreement, no recovery without valid appointment.
3. `marketing-and-price` — auction/no-price marketing, misleading price representations.
4. `offers-and-negotiation` — multiple offers, no dummy offers, safe agent wording.
5. `seller-disclosure` — Form 2 under PLA 2023, timing, termination consequences.

---

## 13. README intent

Credible but unambiguous: what it is, what it is not (not legal advice), how it works (sourced, cited, refuses when unsourced), v1 scope (QLD property sales only), the authority-tier model, how to invoke the skill, how to contribute a rule, licence, maintainer. Disclaimer near the top, not the footer.
