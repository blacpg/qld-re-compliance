# Security and Data Handling

This is a **public** repository. Treat everything committed here as readable by anyone, forever, including in git history after deletion.

## Never commit any of the following

- **Client data** of any kind: names, addresses, contact details, contracts, owner statements, settlement statements, trust records, ID documents.
- **Signed or completed forms**: any completed Form 6, Form 2, Form 8, contract of sale, or appointment with real party details.
- **Contracts and templates** that are paid, licensed, or member-only (for example REIQ member templates).
- **Private Blac policy**: internal scripts, commission rates, escalation contacts, agency procedures, risk-appetite notes. These live in the gitignored `internal/` overlay only.
- **Full text of Crown-copyright legislation or regulator forms.** Cite and link to the official source instead (see `docs/public-content-policy.md`).
- **Credentials**: API keys, tokens, passwords, `.env` files.

## What belongs here

- Your own structured compliance rules (the `rules/` YAML files).
- The source register (`sources/register.yaml`) of citations and official links.
- Schemas, scripts, documentation, the skill, and redacted example templates.

## If sensitive data is committed by mistake

1. Do not just delete the file in a new commit. It stays in history.
2. Treat any exposed credential as compromised and rotate it immediately.
3. Remove it from history (for example `git filter-repo`) and force-push, or, if the repo is young, delete and recreate it.
4. If client personal information was exposed, follow the Blac data-breach process and consider notification obligations under the Privacy Act.

## Reporting

Found something sensitive in this repo, or a security issue with the skill? Open a private report to the maintainer rather than a public issue.

See also: [docs/pii-and-private-data.md](docs/pii-and-private-data.md) and [docs/public-content-policy.md](docs/public-content-policy.md).
