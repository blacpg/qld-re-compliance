#!/usr/bin/env python3
"""Validate every test scenario against schema/scenario.schema.json.

Scenario files under tests/scenarios/ may hold a single scenario (mapping) or a
list of scenarios.

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
SCENARIOS_DIR = ROOT / "tests" / "scenarios"
SCHEMA = ROOT / "schema" / "scenario.schema.json"


def main() -> int:
    schema = json.loads(SCHEMA.read_text())
    validator = Draft202012Validator(schema)
    files = sorted(SCENARIOS_DIR.glob("*.yaml"))
    if not files:
        print("No scenario files found.")
        return 0

    errors = 0
    seen = {}
    count = 0
    for f in files:
        raw = json.loads(json.dumps(yaml.safe_load(f.read_text()), default=str))
        scenarios = raw if isinstance(raw, list) else [raw]
        for s in scenarios:
            count += 1
            for e in sorted(validator.iter_errors(s), key=lambda e: e.path):
                loc = "/".join(str(p) for p in e.path)
                print(f"ERROR {f.name} [{s.get('id','?')}/{loc}]: {e.message}")
                errors += 1
            sid = s.get("id")
            if sid in seen:
                print(f"ERROR: duplicate scenario id {sid}")
                errors += 1
            elif sid:
                seen[sid] = f

    if errors:
        print(f"\n{errors} error(s) across {count} scenario(s).")
        return 1
    print(f"OK: {count} scenario(s) valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
