# PII and Private Data Policy

This repository is public. This document is the plain-English rule for what must never enter it.

## The one rule

If a file identifies a real person, a real property transaction, or a Blac internal practice, it does **not** belong in this public repo.

## Never commit

| Category | Examples |
|---|---|
| Client personal information | Vendor/buyer names, addresses, phone numbers, emails, ID |
| Transaction records | Contracts of sale, owner statements, settlement statements, commission invoices, trust records |
| Signed or completed forms | Any real Form 6 / Form 2 / Form 8 / appointment with party details |
| Private Blac policy | Internal scripts, house rules, commission rates, escalation contacts, agency procedures |
| Licensed or paid material | REIQ member templates, paid contract templates, paywalled content |
| Crown-copyright source text | Full text of Acts, Regulations, or OFT form PDFs (cite and link instead) |
| Credentials | API keys, tokens, passwords, `.env` files |

## Where private material goes instead

- **Private Blac policy** lives in the `internal/` directory, which is gitignored. The public repo ships only the redacted `internal.example/` template so the structure is visible without exposing the content.
- **Downloaded forms and legislation PDFs** (kept for your own reference while writing rules) go in `sources/_downloads/`, which is gitignored. Never commit them.

## Before every commit

- Confirm no file under `rules/`, `tests/`, or `sources/` contains a real name, address, or transaction.
- Confirm `git status` does not show anything from `internal/` or `sources/_downloads/`.
- If in doubt, leave it out.

See also: [SECURITY.md](../SECURITY.md) and [docs/public-content-policy.md](public-content-policy.md).
