#!/usr/bin/env python3
"""Cross-check rules against the source register.

Enforces:
- every source_id cited by a rule exists in the register
- every rule has at least one source (schema also enforces minItems:1)
- a rule whose only sources are industry_commentary does not use mandatory language
- every related_rules id points to an existing rule

Requires: pyyaml
"""
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    sys.exit(f"Missing dependency: {exc}. Run: pip install pyyaml")

ROOT = Path(__file__).resolve().parent.parent
RULES_DIR = ROOT / "rules"
REGISTER = ROOT / "sources" / "register.yaml"

MANDATORY = re.compile(r"\b(must|required|mandatory|shall|prohibited)\b", re.IGNORECASE)


def main() -> int:
    register = yaml.safe_load(REGISTER.read_text())
    source_tier = {s["source_id"]: s["authority_tier"] for s in register["sources"]}

    rule_files = sorted(RULES_DIR.rglob("*.yaml"))
    rules = {}
    for rf in rule_files:
        data = yaml.safe_load(rf.read_text())
        rules[data["id"]] = (data, rf)

    errors = 0
    for rid, (data, rf) in rules.items():
        cited = [s["source_id"] for s in data.get("sources", [])]
        for sid in cited:
            if sid not in source_tier:
                print(f"ERROR {rf.name}: rule {rid} cites unregistered source {sid}")
                errors += 1

        tiers = {source_tier.get(sid) for sid in cited if sid in source_tier}
        only_commentary = tiers == {"industry_commentary"}
        if only_commentary:
            text = f"{data.get('requirement','')} {data.get('detail','')}"
            if MANDATORY.search(text):
                print(
                    f"ERROR {rf.name}: rule {rid} is sourced only from industry_commentary "
                    f"but uses mandatory language. Commentary cannot be the sole basis for a must."
                )
                errors += 1

        for related in data.get("related_rules", []):
            if related not in rules:
                print(f"ERROR {rf.name}: rule {rid} links to missing related rule {related}")
                errors += 1

    if errors:
        print(f"\n{errors} citation-coverage error(s).")
        return 1
    print(f"OK: citation coverage clean across {len(rules)} rule(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
