# Source Ingestion Standard

No rule may cite a source that is not first registered in `sources/register.yaml`. This document defines how a source is registered.

## The gate

1. A source must be the **official publisher**:
   - Queensland legislation: legislation.qld.gov.au
   - OFT guidance and forms: qld.gov.au / Office of Fair Trading
   - ACCC guidance: accc.gov.au
   Third-party summaries, blogs, and law-firm articles may be registered only as `industry_commentary` and may never be the sole basis for a mandatory rule.

2. Every register entry must record:

   | Field | Purpose |
   |---|---|
   | `source_id` | Stable ID, e.g. `SRC-POA-2014` |
   | `title` | Full title of the source |
   | `jurisdiction` | `QLD` or `CTH` |
   | `type` | act / regulation / statutory_form / regulator_guidance / industry_commentary / internal_policy / case |
   | `authority_tier` | The tier (see authority-tiers.md) |
   | `publisher` | The official publisher |
   | `official_url` | Stable link to the official source |
   | `version_or_as_at` | The version or "as at" date the rule was checked against |
   | `retrieved_date` | When it was last retrieved |
   | `licence` | Copyright / licence terms |
   | `pinpoint_style` | How to reference a provision, e.g. "s 102", "sch 1 pt 2" |
   | `notes` | Anything relevant (e.g. commencement date) |

## Verification requirement

Before a rule that cites a source is marked `verification_status: verified`, the cited pinpoint (section, clause, form field) must be checked against the live official source. If it cannot be verified, the rule is marked `unverified` (or `partially_verified`) with a non-empty `verification_note`. A guessed pinpoint is never published as verified.

## Quotation limit

Excerpts are capped at 25 words and used only where a rule turns on the exact wording. See `docs/public-content-policy.md`.

## Currency

`version_or_as_at` is mandatory so a stale provision is never presented as current. Review cadence is in `docs/review-cadence.md`.
