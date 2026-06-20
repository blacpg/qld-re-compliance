#!/usr/bin/env python3
"""Validate every rule YAML under rules/ against schema/rule.schema.json.

Requires: pyyaml, jsonschema
"""
import json
import sys
from pathlib import Path

try:
    import yaml
    from jsonschema import Draft202012Validator
except ImportError as exc:  # pragma: no cover
    sys.exit(f"Missing dependency: {exc}. Run: pip install pyyaml jsonschema")

ROOT = Path(__file__).resolve().parent.parent
RULES_DIR = ROOT / "rules"
SCHEMA = ROOT / "schema" / "rule.schema.json"


def main() -> int:
    schema = json.loads(SCHEMA.read_text())
    validator = Draft202012Validator(schema)
    rule_files = sorted(RULES_DIR.rglob("*.yaml"))
    if not rule_files:
        print("No rule files found under rules/.")
        return 0

    total_errors = 0
    seen_ids: dict[str, Path] = {}
    for rf in rule_files:
        # Normalise PyYAML date objects to ISO strings so they validate as JSON strings.
        data = json.loads(json.dumps(yaml.safe_load(rf.read_text()), default=str))
        errors = sorted(validator.iter_errors(data), key=lambda e: e.path)
        for e in errors:
            loc = "/".join(str(p) for p in e.path)
            print(f"ERROR {rf.relative_to(ROOT)} [{loc}]: {e.message}")
            total_errors += 1
        rid = data.get("id")
        if rid in seen_ids:
            print(f"ERROR: duplicate rule id {rid} in {rf.name} and {seen_ids[rid].name}")
            total_errors += 1
        elif rid:
            seen_ids[rid] = rf

    if total_errors:
        print(f"\n{total_errors} error(s) across {len(rule_files)} rule file(s).")
        return 1
    print(f"OK: {len(rule_files)} rule file(s) valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
