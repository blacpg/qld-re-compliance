# Coverage gaps register

**Status: planning.** This file lists questions a Queensland property *sales* agent
would realistically ask that the skill currently **cannot answer from a cited rule**
(so it refuses). It is the backlog for new rules/modules.

**Important — this is not legal content.** Nothing here states the law. Each entry
is an *unanswered question* plus a *candidate source to verify*. Candidate sources
are starting points for the verify-or-flag process, not confirmed pinpoints. No rule
is built, and no pinpoint is relied on, until it is verified against the official
source and added under the normal gated PR flow (see `CONTRIBUTING.md`).

How these were found: live testing on 2026-06-22 (a real "switch two listings from
private treaty to auction" scenario) plus an audit of `modules/modules.yaml` against
the 9 built rules — several module `covers:` bullets have no backing rule file.

---

## Priority 1 — bread-and-butter, currently refused

### GAP-001 · Form 6 reappointment / variation when changing sale method
- **✅ BUILT — RULE-FORM6-003 (partially_verified), shipped in PR #3 on 2026-06-22.**
- **Owner flag: must be answerable.** Raised directly by Antony 2026-06-22.
- **Question the tool refuses today:** "I'm switching a property from private treaty
  to auction — do I need a new Form 6 or can I vary the existing appointment?"
- **Why it matters:** routine listing management; getting the appointment wrong can
  put commission recovery at risk (links RULE-FORM6-002, RULE-COMM-001).
- **Declared but unbuilt:** `modules.yaml` form-6-appointment → "Reappointment and withdrawal".
- **Candidate sources to verify:** Property Occupations Act 2014 (Qld) — reappointment
  provisions and the general-content/ineffectiveness sections already used (s 104,
  s 112(4)); Form 6 (SRC-FORM-6) reappointment fields; SRC-OFT-APPOINTMENT guidance.
- **Module:** form-6-appointment (new rule).

### GAP-002 · Cooling-off difference: auction vs private treaty
- **✅ BUILT — RULE-COOL-001 (verified), new `cooling-off` module, shipped in PR #3 on 2026-06-22.**
- **Question the tool refuses today:** "If I switch to auction, does the buyer still
  get a cooling-off period?"
- **Why it matters:** directly changes buyer rights on a private-treaty→auction switch;
  an agent must understand and not misstate it. High consequence.
- **Not a module yet.** Candidate new module: `cooling-off-and-warning`.
- **Candidate sources to verify:** Property Law Act 2023 (Qld) cooling-off / warning
  statement provisions and any auction treatment; POA 2014 auction provisions. Verify
  before asserting any period or any auction carve-out.

### GAP-003 · Sole/exclusive agency term limits
- **✅ BUILT — RULE-FORM6-004 (verified), shipped in PR #3 on 2026-06-22.**
- **Question the tool refuses today:** "How long can a sole agency appointment run for?"
- **Declared but unbuilt:** `modules.yaml` form-6-appointment → "Sole vs open appointment
  and term limits".
- **Candidate sources to verify:** POA 2014 appointment-term provisions; Form 6
  appointment-term fields; SRC-OFT-APPOINTMENT.
- **Module:** form-6-appointment (new rule).

---

## Priority 2 — common, in-scope, not yet covered

### GAP-004 · Auction conduct
- **Questions refused today:** "Do I need a licensed auctioneer?", "How is the reserve
  handled?", "Do bidders have to register?", "What counts as dummy bidding?"
- **Not a module yet.** Candidate new module: `auction-conduct`.
- **Candidate sources to verify:** POA 2014 auction provisions (incl. the s 214/s 216
  price-guide sections already used); auctioneer licensing provisions.

### GAP-005 · Seller disclosure — Form 2 contents and exemptions
- **Questions refused/incomplete today:** "What exactly must the Form 2 contain?",
  "Which sales are exempt from the disclosure scheme?"
- **Partial:** RULE-DISC-001 establishes the obligation but lists prescribed documents
  as *pinpoint pending* and notes exclusions exist without enumerating them.
- **Candidate sources to verify:** Property Law Act 2023 (Qld) Pt 7 div 4; Property Law
  Regulation 2024 (Qld) prescribed documents and exclusions (SRC-PL-REG-2024).

### GAP-006 · Commission — GST, expense recovery, sharing/referral
- **Questions refused/incomplete today:** "Is commission quoted including GST?", "Can I
  recover marketing expenses that weren't itemised in the Form 6?", "Can I share
  commission with / pay a referral fee to another agent?"
- **Declared but unbuilt:** `modules.yaml` commission → "Sharing and referral".
- **Candidate sources to verify:** POA 2014 s 104/s 105 (already used); Form 6 Part 7/8;
  GST treatment per the form wording; referral/sharing provisions.

### GAP-007 · Duty to present offers to the seller
- **Question refused today:** "Do I have to present every offer to my seller?"
- **Note:** RULE-OFFERS-001 covers *not misleading buyers* about offers, but says nothing
  about an agent's duty toward the *seller* to pass on offers.
- **Candidate sources to verify:** POA 2014 conduct provisions / OFT conduct guidance.

---

## Priority 3 — known scope gaps (also tracked elsewhere)

### GAP-008 · Form 7 — beneficial-interest disclosure
- Agent acquiring a beneficial interest / related-party purchase. Sales-side gap noted
  in `docs/HANDOVER.md` §12. Candidate sources: POA 2014; Form 7.

### GAP-009 · Form 8 — disclosure to a potential buyer
- **Declared but unbuilt:** `modules.yaml` seller-disclosure → "Form 8 buyer angle".
  Sales-side gap noted in HANDOVER §12. Candidate sources: POA 2014; Form 8.

### GAP-010 · Trust account / deposit handling
- "Where does the deposit go / how is it held?" In the original design, not built.
  Candidate sources: Agents Financial Administration Act 2014 (Qld) (NOT yet registered).

---

## Notes
- Tenanted-sale (RTA Forms 9/10/18a) is tracked separately in
  `docs/scope/tenanted-sale-compliance.md` and is out of v1 sales scope.
- Building any of these follows the gated flow: register the source → verify the
  pinpoint → write the rule with honest `verification_status` → add a test scenario →
  validators green → PR with green CI.
