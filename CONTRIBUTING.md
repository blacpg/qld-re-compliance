# Contributing

Thanks for helping keep this accurate. The whole value of the project is that every answer is sourced and verified. These rules are strict on purpose.

## The golden rules

1. **A rule may only cite a source registered in `sources/register.yaml`.** No registered source, no rule.
2. **Verify every pinpoint against the official source before marking it `verified`.** If you cannot verify it, mark the rule `unverified` (or `partially_verified`) with a non-empty `verification_note`. Never guess a section number or form field.
3. **Cite the official publisher only** (legislation.qld.gov.au, qld.gov.au / OFT, accc.gov.au). Third-party summaries are `industry_commentary` at most and can never be the sole basis for a mandatory rule.
4. **Never commit** client data, signed forms, paid templates, internal Blac policy, or full source text. See [SECURITY.md](SECURITY.md) and [docs/public-content-policy.md](docs/public-content-policy.md).

## Adding a rule

1. Register the source in `sources/register.yaml` (see [docs/source-ingestion-standard.md](docs/source-ingestion-standard.md)).
2. Add the rule YAML under `rules/<module>/`, following `schema/rule.schema.json`.
3. Set `verification_status` honestly and add a `verification_note` if it is not `verified`.
4. Set `last_source_check` and `next_review_due` (see [docs/review-cadence.md](docs/review-cadence.md)).
5. Add or update a test scenario in `tests/scenarios/`.
6. Run the validators (below). They must pass.

## Validation

```
python3 scripts/validate_sources.py
python3 scripts/validate_rules.py
python3 scripts/citation_coverage.py
python3 scripts/check_stale_sources.py
```

The behavioural eval (`scripts/run_eval.py`) needs an API key and is run on demand, not in CI.

## Authority tiers

Read [docs/authority-tiers.md](docs/authority-tiers.md). Get the tier right — it controls how strongly the rule can be stated.
