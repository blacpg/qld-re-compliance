# Queensland Real Estate Compliance Assistant

A source-backed compliance assistant for Queensland real estate agents, delivered as a Claude skill. It answers Queensland property-sales compliance questions **only** from structured, cited rule files — and refuses when it has no source.

> **This is not legal advice.** It does not replace the Queensland Office of Fair Trading, the ACCC, or a solicitor. See [DISCLAIMER.md](DISCLAIMER.md).

## What it is

- Every answer cites the exact legislation, regulation, approved form, or regulator guidance it relies on.
- It never answers property law from memory. No cited rule, no answer.
- It separates **binding law** from **regulator guidance**, **industry commentary**, and **internal agency policy**, and labels every statement with its authority tier.
- Every citation is pinned to a version or date, and every pinpoint is verified against the official source before it is marked `verified`. Anything unverifiable is flagged, not guessed.

## What it is not

- Not legal advice and not a solicitor-client relationship.
- Not a guarantee the law is current — verify against the official source before relying on it.
- Not for residential tenancies, property management, or other states.

## Scope (v1)

**Queensland property sales only.** Five modules:

| Module | Covers |
|---|---|
| Form 6 appointment | Valid appointment, mandatory contents, commission disclosure |
| Commission | How it is expressed and agreed, no recovery without a valid appointment |
| Marketing and price | Auction / no-price marketing, misleading price representations |
| Offers and negotiation | Multiple offers, no dummy offers, safe agent wording |
| Seller disclosure | Form 2 under the Property Law Act 2023, timing, termination consequences |

## How it works

1. The skill classifies the question (rule check, document review, agent script, risk assessment, checklist, or refusal).
2. It loads the matching rule file(s) from `rules/`.
3. It answers only from those rules, citing each source and labelling its authority tier.
4. If no rule covers the question, it refuses and routes you to the OFT or a solicitor.

See the skill at [`skill/qld-property-compliance/SKILL.md`](skill/qld-property-compliance/SKILL.md).

## How sources are handled

The repo **cites and links** to official sources; it does not reproduce Crown-copyright legislation or regulator forms. Sources must be the official publisher (legislation.qld.gov.au, qld.gov.au / OFT, accc.gov.au). See [docs/public-content-policy.md](docs/public-content-policy.md) and [docs/legal-and-copyright.md](docs/legal-and-copyright.md).

## Repository layout

```
skill/      the Claude skill (SKILL.md + references)
sources/    the source register (citations + official links)
rules/      the compliance rules (YAML), one folder per module
modules/    the module + question-type index
schema/     JSON Schemas that validate rules, sources, scenarios
tests/      compliance-question scenarios + answer-behaviour assertions
scripts/    CI validators + an optional behavioural eval runner
docs/        ingestion standard, authority tiers, copyright, review cadence
internal.example/   redacted template of the private Blac overlay
```

## Safety

This is a public repo. No client data, no signed forms, no internal agency policy, no paid templates, no copied legislation. See [SECURITY.md](SECURITY.md) and [docs/pii-and-private-data.md](docs/pii-and-private-data.md).

## Contributing

A rule may only cite a source already registered in `sources/register.yaml`, and every pinpoint must be verified before it is marked `verified`. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Status

Early. Rules are being built and verified module by module. Treat any rule marked `unverified`, `partially_verified`, or `needs_review` as a prompt to check the source, not a settled answer.

## Maintainer

Blac Property Group. Not affiliated with the Queensland Office of Fair Trading, the ACCC, or the REIQ.

## Licence

Schema, scripts, and documentation: MIT (see [LICENSE](LICENSE)). Cited legal sources remain the copyright of their publishers and are linked, not reproduced.
