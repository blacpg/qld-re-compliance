# Tenanted-Sale Compliance — Planning Scope

**Status: planned, not implemented.**

This is a planning document only. No skill, schema, module, rule, scenario, source-register, README, or validator changes have been made for it. It describes a future module and the boundary around it. Nothing here is verified law yet (see the verification note at the end).

## Why this module exists

Forms 9, 10 and 18a are **not** core Property Occupations Act 2014 sales forms. They are **Residential Tenancies and Rooming Accommodation Act 2008 (RTRA Act) / RTA tenancy forms**. They become relevant to a **sales** agent when the property being sold is **tenanted**: the sales campaign (inspections, marketing, access) has to comply with the tenant's rights and the entry/notice rules in tenancy law.

The trigger is narrow and specific: *"I'm selling a property that has a tenant in it."* This module covers the slice of tenancy law a selling agent must follow during a sales campaign. It is **not** a property-management module.

## In scope (future `tenanted-sale-compliance` module)

- Selling a tenanted property
- Tenant access for sales inspections
- **Form 9 — Entry notice**
- **Form 10 — Notice of lessor's intention to sell premises**
- **Form 18a — General Tenancy Agreement**
- Open homes and tenant consent
- Private inspections
- Marketing photos and access
- Pre-launch checks for occupied listings (what a sales agent must confirm before booking inspections or starting marketing)

## Out of scope

- Routine property management
- Rent reviews
- Bond handling
- Repairs and maintenance
- Lease renewals
- Tenancy terminations unrelated to a sale

## The boundary test

One question decides whether something belongs here:

> **Does this obligation arise *because* a sales campaign is being run on a tenanted property?**

- **Yes** → in scope (entry to show buyers, notice to the tenant about the sale, tenant rights during the campaign, photo/access limits, the intention-to-sell notice).
- **No** → out of scope; it is general property management and stays with the RTA.

## Laws and regulators by group

- **Core sales** — Property Occupations Act 2014 + Property Occupations Regulation 2014 (OFT); Property Law Act 2023 + Property Law Regulation 2024 (seller disclosure); Australian Consumer Law (Cth) for misleading conduct. Regulators: Office of Fair Trading; ACCC.
- **Tenanted-sale** — Residential Tenancies and Rooming Accommodation Act 2008 and its regulation. Regulator: Residential Tenancies Authority (RTA).

These stay in separate authority lanes. In the source register, the RTRA Act would be `legislation`, the RTA forms `statutory_form`, and RTA guidance `regulator_guidance`. A tenanted-sale answer cites RTA/RTRA sources, clearly labelled as tenancy law, so sales law (POA/PLA) and tenancy law are never blurred.

## Forms by group

**Core sales forms:**

| Form | Title | Handling |
|---|---|---|
| Form 6 | Residential agent appointment | Statutory form (covered) |
| Form 2 | Seller Disclosure Statement (PLA 2023) | Statutory form (covered) |
| Form 7 | Disclosure of beneficial interest | Sales gap (separate future add) |
| Form 8 | Disclosure to potential buyer | Sales gap (separate future add) |
| Contract of sale (REIQ) | — | Cite-only; copyright/paid; never committed |

**Tenanted-sale forms (RTA / RTRA Act):**

| Form | Title (to be verified) | Role in a sale |
|---|---|---|
| Form 18a | General Tenancy Agreement | The existing lease the agent inherits; sets the tenant's rights and fixed-term/periodic status |
| Form 10 | Notice of lessor's intention to sell premises | Lessor must notify the tenant of intent to sell; affects when/how marketing can begin |
| Form 9 | Entry notice | Mechanism and notice periods for entering to show the property to buyers/photographers |

## How the skill should route questions

Three lanes, with the tenanted-sale lane running **in parallel** with (not instead of) the sales lanes:

1. **Normal sale compliance** → `form-6-appointment`, `commission`, `marketing-and-price`, `offers-and-negotiation` (POA/PLA/ACL).
2. **Seller disclosure** → `seller-disclosure` (Form 2, PLA 2023).
3. **Tenanted-sale compliance** → `tenanted-sale-compliance` (RTRA Act / RTA forms), triggered when the question involves selling an occupied property.

A tenanted sale fires **both** the relevant sales module and the tenanted-sale module. Example: "can I run an open home this Saturday on a tenanted listing?" pulls marketing rules *and* the entry-notice / tenant-consent rules together. Pure property-management questions with **no sale** are out of scope and route to the RTA.

## Why this stays a sales tool, not a property-management repo

Occupied-property sales are a common, frequently-litigated source of selling-agent error (entry without proper notice, open homes without tenant consent, photographing an occupied home without permission). Scoping the module to the **sale-driven intersection** captures that high-value area without taking on the full RTA tenancy-management surface. It is the selling agent's "what do I owe the tenant while I sell this place" lane — nothing more.

## Verification note (mandatory before any build)

Every form title, form number, notice period, statutory section, and regulator source named in this document is **unverified** and must be confirmed against official sources — **rta.qld.gov.au** for RTA forms and guidance, and **legislation.qld.gov.au** for the Residential Tenancies and Rooming Accommodation Act 2008 — **before any rule is built or marked `verified`**. Only Form 18a (General Tenancy Agreement) has been confirmed against the RTA so far; Form 9 (Entry notice) and Form 10 (Notice of lessor's intention to sell premises) are stated identities pending verification. The repo's verify-or-flag rule applies in full: no guessed section, notice period, or form identity is published as verified.
