# Source Verification Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Verify every pinpoint citation in the five v1 rule modules against the official source, and promote each rule's `verification_status` from `unverified`/`needs_review`/`partially_verified` to `verified` only where the exact provision is confirmed. Where a pinpoint cannot be confirmed, leave it flagged with an explicit blocker note. No new rules, no scope expansion.

**Architecture:** Verification is done by downloading the official legislation PDF into the gitignored `sources/_downloads/` directory and extracting its text locally (the legislation.qld.gov.au HTML site is a JavaScript SPA that does not return later sections to a fetcher). Each confirmed provision is recorded in an append-only `docs/verification-log.md` audit trail, then the corresponding rule YAML is updated and re-validated. The downloaded PDFs are never committed (content policy / Crown copyright).

**Tech Stack:** Bash + `curl`, Python 3 with `pdfminer.six` for PDF text extraction, the existing `scripts/validate_*.py` and `scripts/citation_coverage.py` validators, `WebFetch` as a secondary method for HTML-only sources (OFT/ACCC guidance).

**Decision rule used in every task (the verify-or-flag contract):**
- If the exact section number AND heading are confirmed in the official source → set `verification_status: verified`, set the precise `pinpoint`, set `verification_note: null`, and add a `quote` (≤25 words) only if the wording is decisive.
- If the provision is found but partly (e.g. number confirmed, scope unclear) → `verification_status: partially_verified` with a note stating exactly what is and is not confirmed.
- If it cannot be confirmed with available tooling → leave `needs_review`/`unverified`, and update `verification_note` to name the blocker (e.g. "PDF download blocked; manual check required").
- Never invent or promote an unconfirmed section number.

---

## File map

| File | Responsibility | Action |
|---|---|---|
| `scripts/fetch_source.sh` | Download an official source PDF into gitignored `sources/_downloads/` | Create |
| `docs/verification-log.md` | Append-only audit trail of every verification | Create |
| `sources/register.yaml` | Update `version_or_as_at`, `retrieved_date`, notes per source | Modify |
| `rules/form-6-appointment/*.yaml` | Promote/flag Form 6 rules | Modify |
| `rules/commission/*.yaml` | Promote/flag commission rules | Modify |
| `rules/marketing-and-price/*.yaml` | Promote/flag marketing rules | Modify |
| `rules/offers-and-negotiation/*.yaml` | Promote/flag offers rule | Modify |
| `rules/seller-disclosure/*.yaml` | Promote/flag disclosure rules | Modify |
| `CHANGELOG.md` | Record the verification pass | Modify |

**Already verified in the scaffold (re-confirm, do not redo from scratch):** POA 2014 s 102 "Appointment of agent"; PLA 2023 Pt 7 Div 4 s 99 "Seller must give buyer disclosure documents" and s 99(2) approved form.

---

## Task 1: Verification tooling and audit log

**Files:**
- Create: `scripts/fetch_source.sh`
- Create: `docs/verification-log.md`

- [ ] **Step 1: Confirm the PDF extraction library is available**

Run:
```bash
python3 -c "import pdfminer; print('pdfminer ok')" || pip install --user pdfminer.six
```
Expected: prints `pdfminer ok`, or installs it then succeeds.

- [ ] **Step 2: Create the download helper**

Create `scripts/fetch_source.sh`:
```bash
#!/usr/bin/env bash
# Download an official source PDF into the gitignored sources/_downloads/ dir.
# Usage: scripts/fetch_source.sh <url> <output-name.pdf>
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEST="$ROOT/sources/_downloads"
mkdir -p "$DEST"
URL="$1"; NAME="$2"
curl -fsSL "$URL" -o "$DEST/$NAME"
echo "Saved $DEST/$NAME ($(wc -c < "$DEST/$NAME") bytes)"
```

- [ ] **Step 3: Make it executable and confirm the download dir is gitignored**

Run:
```bash
chmod +x scripts/fetch_source.sh
git check-ignore sources/_downloads/test.pdf
```
Expected: `git check-ignore` prints `sources/_downloads/test.pdf` (it is ignored).

- [ ] **Step 4: Create the audit log**

Create `docs/verification-log.md`:
```markdown
# Verification Log

Append-only record of pinpoint verifications. Each entry: date, source, provision checked, method, outcome, and the rule(s) updated.

| Date | Source | Provision checked | Method | Outcome | Rule(s) |
|---|---|---|---|---|---|
| 2026-06-20 | POA 2014 | s 102 Appointment of agent | WebFetch (official whole/html) | VERIFIED heading | RULE-FORM6-001 |
| 2026-06-20 | PLA 2023 | Pt 7 Div 4, s 99 + s 99(2) | WebFetch (official whole/html) | VERIFIED heading + quote | RULE-DISC-001 |
```

- [ ] **Step 5: Commit**

```bash
git add scripts/fetch_source.sh docs/verification-log.md
git commit -m "Add source-fetch helper and verification audit log"
```

---

## Task 2: Download the four Queensland source PDFs

**Files:** none committed (downloads are gitignored).

- [ ] **Step 1: Download POA 2014, PO Regulation 2014, PLA 2023, PL Regulation 2024**

Run:
```bash
scripts/fetch_source.sh "https://www.legislation.qld.gov.au/view/pdf/inforce/current/act-2014-022" poa-2014.pdf
scripts/fetch_source.sh "https://www.legislation.qld.gov.au/view/pdf/inforce/current/sl-2014-0251" po-reg-2014.pdf
scripts/fetch_source.sh "https://www.legislation.qld.gov.au/view/pdf/inforce/current/act-2023-027" pla-2023.pdf
scripts/fetch_source.sh "https://www.legislation.qld.gov.au/view/pdf/inforce/current/sl-2024-0211" pl-reg-2024.pdf
```
Expected: four "Saved ..." lines with non-trivial byte counts.

- [ ] **Step 2: If any download is blocked or tiny (HTML error page), record the blocker**

If a file is < 50 KB or not a PDF (`file sources/_downloads/poa-2014.pdf`), note it: the official "current" PDF URL may differ. Fall back to resolving the correct PDF link from the act landing page, or mark the affected downstream tasks as blocked in `docs/verification-log.md`. Do not proceed to verify a provision from a source you could not download.

- [ ] **Step 3: Extract each PDF to text for searching**

Run:
```bash
for f in poa-2014 po-reg-2014 pla-2023 pl-reg-2024; do
  python3 -c "from pdfminer.high_level import extract_text; open('sources/_downloads/$f.txt','w').write(extract_text('sources/_downloads/$f.pdf'))"
  echo "$f.txt $(wc -l < sources/_downloads/$f.txt) lines"
done
```
Expected: four `.txt` files with substantial line counts. (No commit; these are gitignored working files.)

---

## Task 3: Verify POA appointment validity → RULE-FORM6-002

**Files:**
- Modify: `rules/form-6-appointment/appointment-validity.yaml`
- Modify: `docs/verification-log.md`

- [ ] **Step 1: Find the general-requirements and ineffective provisions**

Run:
```bash
grep -niE "general|requirements for|appointment is ineffective|ineffective" sources/_downloads/poa-2014.txt | head -40
grep -niE "^\s*10[0-9]|^\s*11[0-9]" sources/_downloads/poa-2014.txt | head -60
```
Goal: confirm the actual section number and heading for (a) the general requirements an appointment must satisfy, and (b) the provision making a non-complying appointment ineffective. Commentary suggested s 104 and s 112(4); confirm or correct.

- [ ] **Step 2: Record the finding in `docs/verification-log.md`**

Append a row: date `2026-06-20`, source `POA 2014`, provision (the confirmed section + heading, or "could not confirm"), method `PDF extract`, outcome `VERIFIED`/`could not confirm`, rule `RULE-FORM6-002`.

- [ ] **Step 3: Update the rule per the decision rule**

In `rules/form-6-appointment/appointment-validity.yaml`:
- If confirmed: set `verification_status: verified`, set `verification_note: null`, set `sources[0].pinpoint` to the confirmed sections (e.g. `"s 104; s 112(4)"`), remove the "(unverified)" qualifiers, and optionally add a ≤25-word `quote`.
- If not confirmed: keep `verification_status: needs_review` and rewrite `verification_note` to state the blocker.

- [ ] **Step 4: Re-validate**

Run:
```bash
python3 scripts/validate_rules.py && python3 scripts/citation_coverage.py
```
Expected: both `OK`.

- [ ] **Step 5: Commit**

```bash
git add rules/form-6-appointment/appointment-validity.yaml docs/verification-log.md
git commit -m "Verify POA appointment validity pinpoints (RULE-FORM6-002)"
```

---

## Task 4: Verify POA recovery-of-reward restriction → RULE-COMM-001

**Files:**
- Modify: `rules/commission/commission-requires-appointment.yaml`
- Modify: `docs/verification-log.md`

- [ ] **Step 1: Find the recovery-of-reward provision**

Run:
```bash
grep -niE "recover|reward|entitled to|no proper authorisation|expense" sources/_downloads/poa-2014.txt | head -40
```
Goal: confirm the section that restricts an agent recovering a reward or expense (commission) without proper authorisation/appointment. Commentary suggested ~s 89; confirm or correct the number and heading.

- [ ] **Step 2: Record the finding** in `docs/verification-log.md` (rule `RULE-COMM-001`).

- [ ] **Step 3: Update the rule** in `rules/commission/commission-requires-appointment.yaml` per the decision rule. If confirmed, set `verification_status: verified` (s 102 is already confirmed; add the confirmed recovery section), set the precise `pinpoint`, and clear the "(unverified)" qualifier. If not confirmed, keep `partially_verified` and update the note.

- [ ] **Step 4: Re-validate**

Run: `python3 scripts/validate_rules.py && python3 scripts/citation_coverage.py`
Expected: both `OK`.

- [ ] **Step 5: Commit**

```bash
git add rules/commission/commission-requires-appointment.yaml docs/verification-log.md
git commit -m "Verify POA recovery-of-reward restriction (RULE-COMM-001)"
```

---

## Task 5: Verify POA commission provisions + Form 6 commission field → RULE-COMM-002

**Files:**
- Modify: `rules/commission/commission-must-be-agreed.yaml`
- Modify: `docs/verification-log.md`

- [ ] **Step 1: Find commission-expression / disclosure provisions**

Run:
```bash
grep -niE "commission|reward|amount|how.*expressed|stated" sources/_downloads/poa-2014.txt | head -40
grep -niE "commission|reward" sources/_downloads/po-reg-2014.txt | head -40
```
Goal: confirm whether the Act/Regulation prescribes how commission must be expressed or disclosed, and confirm that residential sales commission is not capped (a stated finding, not an assumption). Note the Form 6 commission part is verified separately in Task 11.

- [ ] **Step 2: Record the finding** (rule `RULE-COMM-002`).

- [ ] **Step 3: Update the rule** per the decision rule. Likely outcome: `partially_verified` (no statutory cap confirmed; precise expression rules tied to the Form, verified in Task 11). State exactly what was confirmed.

- [ ] **Step 4: Re-validate**

Run: `python3 scripts/validate_rules.py && python3 scripts/citation_coverage.py`
Expected: both `OK`.

- [ ] **Step 5: Commit**

```bash
git add rules/commission/commission-must-be-agreed.yaml docs/verification-log.md
git commit -m "Verify POA commission provisions (RULE-COMM-002)"
```

---

## Task 6: Verify POA false-representations provision → RULE-MKTG-001

**Files:**
- Modify: `rules/marketing-and-price/no-false-or-misleading-representations.yaml`
- Modify: `docs/verification-log.md`

- [ ] **Step 1: Find the false-representations section**

Run:
```bash
grep -niE "false|misleading|representation" sources/_downloads/poa-2014.txt | head -40
```
Goal: confirm the section number and heading for false representations about property (commentary said s 212 "False representations about property"). Confirm the maximum penalty wording if you will cite it.

- [ ] **Step 2: Record the finding** (rule `RULE-MKTG-001`).

- [ ] **Step 3: Update the rule.** If confirmed, set the POA source `pinpoint` to the confirmed `"s 212"` (or corrected number), drop the "(reported as ...)" qualifier. Note: this rule also cites the ACL, verified in Task 7, so its overall `verification_status` becomes `verified` only once BOTH the POA and ACL pinpoints are confirmed; otherwise `partially_verified` with a note naming the outstanding one.

- [ ] **Step 4: Re-validate**

Run: `python3 scripts/validate_rules.py && python3 scripts/citation_coverage.py`
Expected: both `OK`.

- [ ] **Step 5: Commit**

```bash
git add rules/marketing-and-price/no-false-or-misleading-representations.yaml docs/verification-log.md
git commit -m "Verify POA false-representations pinpoint (RULE-MKTG-001)"
```

---

## Task 7: Verify ACL s 18 and s 30 → RULE-MKTG-001 and RULE-OFFERS-001

**Files:**
- Modify: `rules/marketing-and-price/no-false-or-misleading-representations.yaml`
- Modify: `rules/offers-and-negotiation/multiple-offers.yaml`
- Modify: `sources/register.yaml`
- Modify: `docs/verification-log.md`

- [ ] **Step 1: Confirm the ACL provisions on the Commonwealth register**

Use WebFetch on the official Federal Register of Legislation (the ACL is Schedule 2 of the Competition and Consumer Act 2010 (Cth)):
```
WebFetch https://www.legislation.gov.au/C2004A00109/latest/text
prompt: "In the Australian Consumer Law (Schedule 2), confirm the exact section number and heading for (a) misleading or deceptive conduct, and (b) false or misleading representations about the sale of land. Quote the headings verbatim."
```
If the page does not return the schedule text, download its PDF via `scripts/fetch_source.sh` into `sources/_downloads/` and extract as in Task 2.
Expected to confirm: s 18 (misleading or deceptive conduct) and s 30 (false or misleading representations etc about sale of land). Correct if different.

- [ ] **Step 2: Record the finding** (rules `RULE-MKTG-001`, `RULE-OFFERS-001`) and update the `SRC-ACL` register note + `retrieved_date`.

- [ ] **Step 3: Update both rules.** Set the ACL `pinpoint` to the confirmed `"s 18; s 30"`, drop the "(pinpoints unverified in-session)" qualifier. Recompute each rule's `verification_status`: `verified` if all of its cited statutory pinpoints are now confirmed, else `partially_verified` with a precise note.

- [ ] **Step 4: Re-validate**

Run: `python3 scripts/validate_sources.py && python3 scripts/validate_rules.py && python3 scripts/citation_coverage.py`
Expected: all `OK`.

- [ ] **Step 5: Commit**

```bash
git add rules/marketing-and-price/no-false-or-misleading-representations.yaml rules/offers-and-negotiation/multiple-offers.yaml sources/register.yaml docs/verification-log.md
git commit -m "Verify ACL s 18 / s 30 pinpoints (RULE-MKTG-001, RULE-OFFERS-001)"
```

---

## Task 8: Resolve the auction price-guide question → RULE-MKTG-002

**Files:**
- Modify: `rules/marketing-and-price/auction-and-no-price-marketing.yaml`
- Modify: `docs/verification-log.md`

- [ ] **Step 1: Look for any statutory no-price-guide-at-auction rule**

Run:
```bash
grep -niE "auction|price guide|guide price|advertise.*price" sources/_downloads/poa-2014.txt | head -40
grep -niE "auction|price" sources/_downloads/po-reg-2014.txt | head -40
```
Then WebFetch the OFT property-advertising page (already partly checked) to re-confirm its exact wording on auction/offers-over.
Goal: determine whether a blanket "no price guide once a property is going to auction" rule actually exists in QLD law, or whether the only real constraint is the misleading-conduct prohibition.

- [ ] **Step 2: Record the finding.** Expected likely outcome based on the scaffold check: no blanket statutory ban found; the operative constraint is misleading conduct (RULE-MKTG-001). State this explicitly in the log.

- [ ] **Step 3: Update the rule.** If no ban is found, change the rule so it does NOT assert one: keep `verification_status` honest (`partially_verified` if the offers-over/OFT guidance is confirmed and the misleading-conduct basis is verified via Task 7; `needs_review` otherwise). Make the `requirement`/`detail` rely on the misleading-conduct principle, not a fictional auction ban.

- [ ] **Step 4: Re-validate**

Run: `python3 scripts/validate_rules.py && python3 scripts/citation_coverage.py`
Expected: both `OK`.

- [ ] **Step 5: Commit**

```bash
git add rules/marketing-and-price/auction-and-no-price-marketing.yaml docs/verification-log.md
git commit -m "Resolve auction price-guide basis (RULE-MKTG-002)"
```

---

## Task 9: Confirm the multiple-offers basis → RULE-OFFERS-001

**Files:**
- Modify: `rules/offers-and-negotiation/multiple-offers.yaml`
- Modify: `docs/verification-log.md`

- [ ] **Step 1: Confirm there is no positive statutory duty to disclose competing offers' terms**

Run:
```bash
grep -niE "disclose|other offer|competing|inform the buyer" sources/_downloads/poa-2014.txt | head -40
```
Goal: confirm the *absence* of a disclosure duty (so it can be stated as "no obligation found", not as a cited permission), and confirm the misleading-conduct basis is already verified via Tasks 6 and 7.

- [ ] **Step 2: Record the finding** (rule `RULE-OFFERS-001`).

- [ ] **Step 3: Update the rule.** Set `verification_status: verified` for the misleading-conduct constraint once Tasks 6 and 7 are done; keep the "no positive duty to disclose" worded as an absence-of-found-obligation in `verification_note`, since absence is not a citable provision.

- [ ] **Step 4: Re-validate**

Run: `python3 scripts/validate_rules.py && python3 scripts/citation_coverage.py`
Expected: both `OK`.

- [ ] **Step 5: Commit**

```bash
git add rules/offers-and-negotiation/multiple-offers.yaml docs/verification-log.md
git commit -m "Confirm multiple-offers basis (RULE-OFFERS-001)"
```

---

## Task 10: Verify PLA seller-disclosure application and exclusions → RULE-DISC-001

**Files:**
- Modify: `rules/seller-disclosure/disclosure-statement-required.yaml`
- Modify: `docs/verification-log.md`

- [ ] **Step 1: Confirm s 99 wording and find the application/exclusion provisions**

Run:
```bash
grep -niE "disclosure statement|approved form|before a contract|signed by the buyer" sources/_downloads/pla-2023.txt | head -30
grep -niE "does not apply|exclud|application of|this division applies" sources/_downloads/pla-2023.txt | head -40
```
Goal: re-confirm s 99 / s 99(2) (already verified) and identify the section(s) setting out which sales the scheme applies to and the exclusions (so SCN-011 "does it apply to my sale?" has a real basis to flag against).

- [ ] **Step 2: Record the finding** (rule `RULE-DISC-001`). s 99 is already `verified`; add the confirmed application/exclusion section reference to the rule's `exceptions`/`does_not_apply_when` with a pinpoint.

- [ ] **Step 3: Update the rule** to cite the confirmed application/exclusion section. Keep `verification_status: verified` (s 99 confirmed); if the exclusions could not be pinned, add a `verification_note` scoping exactly that gap rather than downgrading the whole rule.

- [ ] **Step 4: Re-validate**

Run: `python3 scripts/validate_rules.py && python3 scripts/citation_coverage.py`
Expected: both `OK`.

- [ ] **Step 5: Commit**

```bash
git add rules/seller-disclosure/disclosure-statement-required.yaml docs/verification-log.md
git commit -m "Verify PLA seller-disclosure application/exclusions (RULE-DISC-001)"
```

---

## Task 11: Verify PL Regulation 2024 prescribed documents → RULE-DISC-001

**Files:**
- Modify: `rules/seller-disclosure/disclosure-statement-required.yaml`
- Modify: `sources/register.yaml`
- Modify: `docs/verification-log.md`

- [ ] **Step 1: Find the prescribed documents/certificates**

Run:
```bash
grep -niE "prescribed|certificate|disclosure|document" sources/_downloads/pl-reg-2024.txt | head -50
```
Goal: confirm the regulation provision that prescribes the documents/certificates a seller must give with the Form 2.

- [ ] **Step 2: Record the finding** and set `SRC-PL-REG-2024` `pinpoint_style`/note + `retrieved_date` in the register.

- [ ] **Step 3: Update the rule's** `SRC-PL-REG-2024` source entry with the confirmed pinpoint, replacing "(pinpoint pending verification)".

- [ ] **Step 4: Re-validate**

Run: `python3 scripts/validate_sources.py && python3 scripts/validate_rules.py && python3 scripts/citation_coverage.py`
Expected: all `OK`.

- [ ] **Step 5: Commit**

```bash
git add rules/seller-disclosure/disclosure-statement-required.yaml sources/register.yaml docs/verification-log.md
git commit -m "Verify PL Regulation 2024 prescribed documents (RULE-DISC-001)"
```

---

## Task 12: Verify PLA termination provision → RULE-DISC-002

**Files:**
- Modify: `rules/seller-disclosure/termination-for-non-disclosure.yaml`
- Modify: `docs/verification-log.md`

- [ ] **Step 1: Find the buyer-termination provision**

Run:
```bash
grep -niE "terminate|termination|before settlement|right to terminate|material" sources/_downloads/pla-2023.txt | head -40
```
Goal: confirm the section that gives the buyer a right to terminate before settlement for non-disclosure or a material inaccuracy/omission, and confirm whether termination is the only remedy (no compensation). Commentary suggested ~s 104.

- [ ] **Step 2: Record the finding** (rule `RULE-DISC-002`).

- [ ] **Step 3: Update the rule.** If confirmed, set `verification_status: verified`, set the precise `pinpoint`, `verification_note: null`, and add a ≤25-word `quote` only if the termination wording is decisive. If not, keep `needs_review` with a precise blocker note.

- [ ] **Step 4: Re-validate**

Run: `python3 scripts/validate_rules.py && python3 scripts/citation_coverage.py`
Expected: both `OK`.

- [ ] **Step 5: Commit**

```bash
git add rules/seller-disclosure/termination-for-non-disclosure.yaml docs/verification-log.md
git commit -m "Verify PLA termination-for-non-disclosure provision (RULE-DISC-002)"
```

---

## Task 13: Verify the official forms (Form 6, Form 2) → RULE-FORM6-002, RULE-COMM-002, RULE-DISC-001

**Files:**
- Modify: `rules/form-6-appointment/appointment-validity.yaml`
- Modify: `rules/commission/commission-must-be-agreed.yaml`
- Modify: `sources/register.yaml`
- Modify: `docs/verification-log.md`

- [ ] **Step 1: Retrieve the official forms for field-level reference (gitignored)**

From the OFT appointment page and the PLA 2023 forms dataset, download the current Form 6 and Form 2 PDFs into `sources/_downloads/` using `scripts/fetch_source.sh`. If the direct PDF URL is not known, WebFetch the OFT/publications page to resolve the current download link first. These are Crown-copyright forms: they are reference-only and must never be committed.

- [ ] **Step 2: Confirm the field structure you actually cite**

Confirm the Form 6 part/section where commission and term are recorded (cited by RULE-COMM-002 and RULE-FORM6-002), and confirm the Form 2 "effective from 1 August 2025" version marker (cited by RULE-DISC-001). Record exact part/section references.

- [ ] **Step 3: Record the finding** and update `SRC-FORM-6` / `SRC-FORM-2` register notes + `retrieved_date`.

- [ ] **Step 4: Update the rules'** form `pinpoint`s (e.g. the Form 6 commission part) to the confirmed references, replacing the "pending verification" qualifiers. Recompute each rule's `verification_status`.

- [ ] **Step 5: Re-validate**

Run: `python3 scripts/validate_sources.py && python3 scripts/validate_rules.py && python3 scripts/citation_coverage.py`
Expected: all `OK`.

- [ ] **Step 6: Confirm no form PDF got staged**

Run: `git status --porcelain | grep -i downloads || echo "clean: no downloads staged"`
Expected: `clean: no downloads staged`.

- [ ] **Step 7: Commit**

```bash
git add rules/form-6-appointment/appointment-validity.yaml rules/commission/commission-must-be-agreed.yaml sources/register.yaml docs/verification-log.md
git commit -m "Verify Form 6 / Form 2 field references"
```

---

## Task 14: Confirm OFT and ACCC guidance URLs → register + supporting cites

**Files:**
- Modify: `sources/register.yaml`
- Modify: `docs/verification-log.md`

- [ ] **Step 1: Confirm the guidance pages resolve and re-read their key statements**

WebFetch `SRC-OFT-APPOINTMENT`, `SRC-OFT-ADVERTISING`, and `SRC-ACCC-RE` `official_url`s. Confirm each loads (HTTP 200) and that the statement the register relies on is still present. The ACCC landing URL in particular was marked "to be confirmed".

- [ ] **Step 2: Record the finding** and update each register entry's `retrieved_date` and `official_url` (correct the ACCC URL if it 404s or redirects).

- [ ] **Step 3: Re-validate**

Run: `python3 scripts/validate_sources.py`
Expected: `OK`.

- [ ] **Step 4: Commit**

```bash
git add sources/register.yaml docs/verification-log.md
git commit -m "Confirm OFT and ACCC guidance URLs"
```

---

## Task 15: Final validation pass and changelog

**Files:**
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Run the full validator suite**

Run:
```bash
python3 scripts/validate_sources.py && \
python3 scripts/validate_rules.py && \
python3 scripts/validate_scenarios.py && \
python3 scripts/citation_coverage.py && \
python3 scripts/check_stale_sources.py --today 2026-06-20
```
Expected: every script prints `OK` (stale-source also prints the event-trigger reminder).

- [ ] **Step 2: Tally verification status**

Run:
```bash
grep -rh "verification_status:" rules/ | sort | uniq -c
```
Record the counts (how many `verified` vs `partially_verified` vs `needs_review`) in the CHANGELOG and confirm none are silently left as `unverified` without a `verification_note`.

- [ ] **Step 3: Update `CHANGELOG.md`**

Move the verified rules out of the "pending verification" note and add a line summarising the verification pass and the date, listing any rules that remain flagged and why.

- [ ] **Step 4: Confirm no gitignored downloads were committed**

Run: `git ls-files | grep -i "_downloads\|\.pdf" || echo "clean: no PDFs or downloads tracked"`
Expected: `clean: no PDFs or downloads tracked`.

- [ ] **Step 5: Commit**

```bash
git add CHANGELOG.md
git commit -m "Complete v1 source verification pass"
```

---

## Self-review notes

- **Spec coverage:** every flagged item from the scaffold maps to a task — POA validity (T3), POA recovery (T4), POA commission (T5), POA false reps (T6), ACL s18/s30 (T7), auction guide (T8), multiple offers (T9), PLA application/exclusions (T10), PL Reg prescribed docs (T11), PLA termination (T12), forms (T13), OFT/ACCC URLs (T14). The two already-verified anchors (POA s 102, PLA s 99) are re-confirmed within T3/T10 rather than re-derived.
- **No new scope:** no task adds a rule that did not exist in the scaffold; tasks only verify and promote/flag. Rule expansion is explicitly a later plan.
- **Verify-or-flag preserved:** every task's Step 3 applies the same decision rule and forbids promoting an unconfirmed section number.
- **Audit trail:** every verification writes a `docs/verification-log.md` row before the rule is changed.
- **Copyright safety:** all PDFs land in gitignored `sources/_downloads/`; Tasks 13 and 15 explicitly assert nothing under `_downloads/` or any `.pdf` is committed.
