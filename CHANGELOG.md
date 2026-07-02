# Changelog

All notable changes to this project are recorded here. Dates are in YYYY-MM-DD.

## [Unreleased]

### Added
- RULE-FORM6-005 (form-6-appointment, partially_verified): a Form 6 must be signed and dated by both the client and the agent and a copy given to the client (POA 2014 s 109), separate from the s 104 content requirement whose breach is ineffective under s 112(4). Closes GAP-011 (the "agent signed a draft, not-finalised Form 6" scenario). Adds test scenarios SCN-038/SCN-039.
- Supporting industry_commentary sources SRC-REALWORKS-HELP and SRC-REIQ-FORM6, cited (supporting only, never the basis for a mandatory limb) in RULE-FORM6-005 to explain that in Realworks finalising a form removes the "DRAFT" watermark and precedes signing — so a signed-yet-watermarked copy is anomalous.
- Initial repository scaffold: skill, schemas, source register, docs, scripts, and safety files.
- First five module rule files: Form 6, commission, marketing and price, offers and negotiation, seller disclosure.
- Source register with the core Queensland and Commonwealth sources.
- CI validators (schema, source integrity, citation coverage, stale-source detection) and an optional behavioural eval runner.
- Design spec at `docs/superpowers/specs/2026-06-20-qld-re-compliance-design.md`.

### Notes
- Rules marked `unverified` or `needs_review` are pending pinpoint verification against the official source and must not be relied on until verified.
