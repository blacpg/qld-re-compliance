# Handover — QLD Real Estate Compliance Assistant

Last updated: 2026-06-21. Written so you (or anyone) can resume cold on another machine.

---

## 1. TL;DR — where things stand

- **Repo:** https://github.com/blacpg/qld-re-compliance — public, org `blacpg`, owner `bpg-ant`.
- **Branch:** `main` · **latest commit at handover:** `bff4f92` ("Implement behavioural eval runner (#2)").
- **Verification pass: complete.** 8 of 9 rules `verified`; 1 (`RULE-OFFERS-001`) intentionally `partially_verified`.
- **CI:** the `validate` workflow runs on every push/PR and is green.
- **One thing not done yet:** the **paid behavioural eval has never been run** (the SCN-005 smoke test is queued — see §10).
- **No new scope started:** Form 7/8, the tenanted-sale module, and broader coverage are documented as *planned, not built*.

## 2. What this is (and isn't)

A **source-backed Queensland property-SALES compliance assistant**, delivered as a Claude skill. Every answer is built only from structured rule files and cites the exact Act/regulation/approved form/regulator guidance behind it; it refuses when no cited rule covers the question. **Not legal advice.**

**v1 scope: Queensland property sales only.** Not tenancies/property management (except the planned tenanted-sale intersection), not other states.

## 3. Resume on a new machine

```bash
git clone https://github.com/blacpg/qld-re-compliance.git
cd qld-re-compliance
python3 -m pip install -r scripts/requirements.txt        # pyyaml + jsonschema (validators)
python3 -m pip install -r scripts/requirements-eval.txt   # anthropic (only if running the paid eval)
```

Then:
- **`gh` auth:** `gh auth login` with scopes `repo` **and** `workflow` (the latter is needed to push anything under `.github/`). Without it, pushes that touch the CI workflow are rejected.
- **`ANTHROPIC_API_KEY`:** environment-only, never in the repo. `export ANTHROPIC_API_KEY=...` when you want to run the eval.
- **`sources/_downloads/`** is gitignored and does not sync — it's local scratch (verification PDFs, eval transcripts). You don't need it on the other machine; the runner re-downloads as required.

## 4. Repo map

```
skill/qld-property-compliance/   SKILL.md (answer loop, refusal, tier+conflict rules) + references/
rules/<module>/*.yaml            the 9 compliance rules across 5 sales modules
sources/register.yaml            source register — cite-and-link only, no full text
modules/modules.yaml             module + question_type + answer_outcome taxonomy
schema/                          rule / source / scenario JSON Schemas
tests/scenarios/scenarios.yaml   20 scenarios (answered / refused / escalated / uncertain)
tests/expected-answer-rules/     how the inline assertions work
scripts/                         validators + run_eval.py + requirements*.txt
docs/                            policies, standards, specs, plans, this handover
docs/verification-log.md         append-only audit trail of every pinpoint verification
internal.example/                redacted template of the gitignored internal/ overlay
.github/workflows/validate.yml   CI
```

## 5. Operating model (the non-negotiables)

- **No rule file, no answer.** If no rule covers it → refuse, route to OFT/RTA/solicitor. No improvising.
- **Verify-or-flag.** Every pinpoint is checked against the official source. Unverifiable → `unverified`/`needs_review` with a note, never a guess.
- **Three independent rule fields:** `status` (active/draft/superseded/retired); `verification_status` (verified/partially_verified/unverified/needs_review); `risk_level` (high/medium/low).
- **Authority tiers:** legislation > regulation > statutory_form > regulator_guidance > industry_commentary > internal_policy. Commentary can never be the sole basis for a "must". Internal policy is phrased "Blac policy requires…", never "the law requires…".
- **question_type** (rule_check / document_review / agent_script / risk_assessment / checklist) is what the user asks; **answer_outcome** (answered / refused_unsourced / refused_out_of_scope / escalated / uncertain) is how it resolves. Any type can end in any outcome.
- **Review cadence:** 90 days default, 60 for seller-disclosure, plus event-triggered review on any official source change. Enforced by `check_stale_sources.py`.

## 6. Rule verification status (8/9 verified)

| Rule | Status | Verified basis |
|---|---|---|
| RULE-FORM6-001 | verified | POA 2014 s 102 "Appointment" |
| RULE-FORM6-002 | verified | POA s 104 "General content of appointment"; s 112(4) ineffective |
| RULE-COMM-001 | verified | POA s 89 "Restriction on recovery of reward or expense—no proper authorisation etc." |
| RULE-COMM-002 | verified | POA s 104/s 105 + Form 6 V1 (May 2024) Part 7/8 |
| RULE-MKTG-001 | verified | POA s 212 "False representations about property"; ACL s 18 + s 30 |
| RULE-MKTG-002 | verified | POA s 216(2)(c) / s 214(2)(c); PO Reg 2014 reg 10 |
| RULE-DISC-001 | verified | PLA 2023 s 99 (Pt 7 Div 4) |
| RULE-DISC-002 | verified | PLA 2023 s 104 (buyer termination) |
| RULE-OFFERS-001 | **partially_verified (intentional)** | Mandatory "don't mislead" verified (POA s 212; ACL s 18/s 30); the "no positive duty to disclose other offers" point is an absence-of-obligation with no citable source — nothing further to verify |

Full audit trail: `docs/verification-log.md`.

## 7. Governance, branch protection, push policy

- `main` is protected: **PR + green `validate` CI required**; force-push/deletion blocked; conversation resolution required.
- **`enforce_admins` is OFF** (deliberate owner escape hatch). The push policy in `CONTRIBUTING.md` compensates:
  - **Admins may direct-push only** low-risk docs/planning changes (e.g. `docs/` notes, typo fixes, this handover).
  - **PR + green CI required (even for admins)** for: `skill/`, `rules/`, `sources/register.yaml`, `schema/`, `modules/`, `tests/scenarios/`, `scripts/`, `.github/workflows/`, `README.md`, `LICENSE`, `CONTRIBUTING.md`, and any public-content/privacy/safety/verification policy file.
- PR flow used so far: branch → change → validators + safety sweep → PR → green CI → squash-merge → delete branch.

## 8. CI

`.github/workflows/validate.yml` runs on push + PR: installs `scripts/requirements.txt`, then runs `validate_sources`, `validate_rules`, `validate_scenarios`, `citation_coverage`, and `check_stale_sources --warn-only`. The behavioural eval (`run_eval.py`) is **not** in CI (no API key in CI).

## 9. Running the validators (no cost, do this first on any machine)

```bash
python3 scripts/validate_sources.py
python3 scripts/validate_rules.py
python3 scripts/validate_scenarios.py
python3 scripts/citation_coverage.py
python3 scripts/check_stale_sources.py --today YYYY-MM-DD
```
All should print `OK`. (Pass `--today` to check staleness against a fixed date.)

## 10. Running the behavioural eval (`scripts/run_eval.py`)

- **Dry-run (no key, no cost):** `python3 scripts/run_eval.py --dry-run --scenario SCN-001` — assembles + prints the allowlisted context.
- **Paid run (needs key + explicit scope):** model = `--model` > `$EVAL_MODEL` > default `claude-sonnet-4-6`; `temperature 0`, `max_tokens 1024`. Grades each scenario on `must_include`/`must_not_include` + an `answer_outcome:` marker (the marker is requested by an **eval-only** prompt instruction; the live SKILL.md is unchanged). Exit 1 on any failure.
- **Context per scenario is allowlisted:** SKILL.md + references + the rule files named by `expected_rule_ids` + only the cited register entries. `sources/_downloads/` and `internal/` can never be included. Refusal scenarios get no rule files (forces refusal).
- **`--save-output`** writes only to gitignored `sources/_downloads/eval/` (asserted via `git check-ignore`).

**PENDING — approved one-scenario smoke test (not yet completed):**
```bash
cd ~/qld-re-compliance
export ANTHROPIC_API_KEY=sk-ant-<real-key>
python3 scripts/run_eval.py --scenario SCN-005 --save-output
```
SCN-005 (auction price guide) must contain `RULE-MKTG-001` + `misleading`, avoid "probably legal"/"you should be fine", and end with `answer_outcome: answered`. Only after this looks right should `--all` be considered (≈20 short calls, real spend).

## 11. Key findings / gotchas worth remembering

- **legislation.gov.au is a JS SPA.** For the Commonwealth ACL, the HTML page returns only the ToC to a fetcher — use the official **EPUB/volume document** (that's how ACL s 18/s 30 operative text was obtained; **Compilation No. 164, 27 May 2026**, Schedule 2).
- **legislation.qld.gov.au:** use `view/pdf/inforce/current/<id>` to get the full PDF, or `view/whole/html/inforce/current/<id>` (large acts truncate). The view/html landing page alone returns almost nothing.
- **OFT forms** live on **publications.qld.gov.au** (e.g. Form 6 V1, effective 1 May 2024).
- **PLA 2023 reprint drift:** the current reprint is **as at 28 April 2026** (not the 1 Aug 2025 commencement). s 99 wording was confirmed unchanged across both; the register is pinned to 28 Apr 2026.
- **The auction price-guide ban is REAL law**, not an industry myth — POA s 216/s 214 + PO Reg reg 10 (the OFT advertising *page* alone did not state it; the Act/Regulation do). This was caught by verifying against the Act, not the guidance page.
- **REIQ contract of sale** is member/paid, copyright — cite-and-link only, never commit.
- **Form numbering is split across four systems:** OFT Property Occupations (sales: 6/6A/7/8), OFT auction/motor-dealer (9/10 — NOT property), Property Law Act 2023, and RTA tenancy (18a, 9 entry notice, 10 intention-to-sell).

## 12. Forms map (confirmed via official sources)

**Core sales (POA/PLA):** Form 6 (appointment) ✓ covered · Form 2 (seller disclosure) ✓ covered · Form 7 (beneficial-interest disclosure) — gap · Form 8 (disclosure to potential buyer) — gap · REIQ contract (cite-only).
**Tenanted-sale (RTA / RTRA Act) — planned, not built:** Form 18a (general tenancy agreement) · Form 10 (lessor's intention to sell) · Form 9 (entry notice).
**Out of scope:** OFT Forms 9/10 (chattel/motor dealer) · general property management.

## 13. Open follow-ups / planned-not-built

1. **Paid behavioural eval not yet run** — start with SCN-005 (§10), then `--all`.
2. **`tenanted-sale-compliance` module** — scoped in `docs/scope/tenanted-sale-compliance.md` (Status: planned). Covers tenancy rules that constrain a sale of an occupied property. RTA/RTRA form identities (esp. Form 9/10) still need verifying against rta.qld.gov.au before any rule is built.
3. **Form 7 and Form 8** — in-scope sales gaps, not built.
4. **Eval runner enhancements (optional):** a retrieval/routing eval (send all rules, check it picks the right one), and `--json` summaries for trend tracking.
5. **Optional:** tag a baseline release (e.g. `v0.1`) for a clean reference point.

## 14. Safety reminders (public repo)

Never commit: client data, signed/completed forms, the REIQ contract or any paid/member template, private Blac policy (lives in gitignored `internal/`), full Crown-copyright legislation or OFT form files, or API keys. Downloads stay in gitignored `sources/_downloads/`. Excerpts in rules are capped at ~25 words. See `SECURITY.md`, `docs/pii-and-private-data.md`, `docs/public-content-policy.md`.

## 15. Recommended next steps, in order

1. On the work machine: clone, install deps, run the validators (§9) — confirm green.
2. Run the **SCN-005 paid smoke test** (§10); read the transcript; sanity-check the skill answers as the verified rule intends.
3. If good, run `--all` and review failures (assertion wording vs skill behaviour).
4. Then pick a build: **Form 7/8** (small, in-scope) or **brainstorm the tenanted-sale module** (larger, needs RTA verification) — each via the gated PR + verify-or-flag flow.
