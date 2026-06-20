# Public Content Policy

Hard rules for what may be committed to this public repository. These are not guidelines. A pull request that breaks any of them must be rejected.

## Do not commit

- **No paid templates.**
- **No REIQ member-only content.**
- **No contract templates** unless clearly and openly licensed for redistribution.
- **No client files** of any kind (see [pii-and-private-data.md](pii-and-private-data.md)).
- **No internal agency procedures** in public (they belong in the gitignored `internal/` overlay).
- **No copied full legislation.** Do not mirror the text of Acts or Regulations.
- **No regulator form files** (Form 6, Form 2, Form 8 PDFs are Government copyright).

## Cite and link only

The repository links to official sources rather than reproducing them:

- Queensland legislation: <https://www.legislation.qld.gov.au> is the official source for the Property Occupations Act 2014, the Property Occupations Regulation 2014, the Property Law Act 2023, and the Property Law Regulation 2024. Link to these; do not mirror them.
- Office of Fair Trading guidance and forms: <https://www.qld.gov.au/law/fair-trading> and the OFT forms pages. Link to the download page; do not host the form.
- ACCC guidance: <https://www.accc.gov.au>. Link to the relevant guidance page.

## Limited quotation

Short excerpts (25 words or fewer) are permitted only where a rule turns on the exact wording of a provision, and only with a pinpoint citation and link to the official source. This is intended to fall within fair-dealing limits. When in doubt, paraphrase in your own words and cite the section instead.

## Every source must be official

A rule may only cite a source registered in `sources/register.yaml`, and that source must be the official publisher (legislation.qld.gov.au, qld.gov.au / OFT, accc.gov.au), never a third-party summary or blog.
