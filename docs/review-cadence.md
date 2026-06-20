# Review Cadence

Every rule carries `last_source_check` and `next_review_due`. `check_stale_sources.py` fails CI (or warns) when a rule is overdue.

## Default cadence

`next_review_due = last_source_check + 90 days`.

## Higher-frequency areas

| Area | Cadence | Reason |
|---|---|---|
| `seller-disclosure` | 60 days | The Queensland seller disclosure scheme under the Property Law Act 2023 commenced on 1 August 2025. It is still new and likely to keep generating OFT guidance and practice updates, so it carries extra caution. |
| Everything else | 90 days | Standard review window. |

## What a review involves

1. Re-open the official source at the `official_url` in the register.
2. Confirm the pinpoint (section/clause/form field) still says what the rule claims.
3. Confirm the provision has not been amended, superseded, or repealed.
4. Update `version_or_as_at`, `retrieved_date`, `last_source_check`, and `next_review_due`.
5. If the source changed, update the rule and, if needed, change `verification_status` or `status`.

## On commencement or amendment

When an Act or Regulation amendment commences, treat affected rules as `needs_review` immediately, regardless of the scheduled date.
