#!/usr/bin/env python3
"""Validate sources/register.yaml against schema/source.schema.json.

Requires: pyyaml, jsonschema
    pip install pyyaml jsonschema
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
REGISTER = ROOT / "sources" / "register.yaml"
SCHEMA = ROOT / "schema" / "source.schema.json"


def main() -> int:
    schema = json.loads(SCHEMA.read_text())
    # Normalise PyYAML date objects to ISO strings so they validate as JSON strings.
    data = json.loads(json.dumps(yaml.safe_load(REGISTER.read_text()), default=str))
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(data), key=lambda e: e.path)
    if errors:
        for e in errors:
            loc = "/".join(str(p) for p in e.path)
            print(f"ERROR [{loc}]: {e.message}")
        print(f"\n{len(errors)} error(s) in {REGISTER.relative_to(ROOT)}")
        return 1

    ids = [s["source_id"] for s in data["sources"]]
    dupes = {i for i in ids if ids.count(i) > 1}
    if dupes:
        print(f"ERROR: duplicate source_id(s): {', '.join(sorted(dupes))}")
        return 1

    print(f"OK: {len(ids)} source(s) valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
