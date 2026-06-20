#!/usr/bin/env python3
"""Detect rules whose source review is overdue.

A rule is overdue when next_review_due is in the past. Pass --today YYYY-MM-DD
to check against a fixed date (useful in CI snapshots); otherwise uses the
system date.

Exit codes: 0 = all current, 1 = one or more overdue.

Requires: pyyaml
"""
import argparse
import sys
from datetime import date
from pathlib import Path

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    sys.exit(f"Missing dependency: {exc}. Run: pip install pyyaml")

ROOT = Path(__file__).resolve().parent.parent
RULES_DIR = ROOT / "rules"


def parse_date(value: str) -> date:
    return date.fromisoformat(str(value))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--today", help="Override today's date (YYYY-MM-DD)")
    ap.add_argument("--warn-only", action="store_true", help="Report but exit 0")
    args = ap.parse_args()

    today = parse_date(args.today) if args.today else date.today()

    overdue = []
    for rf in sorted(RULES_DIR.rglob("*.yaml")):
        data = yaml.safe_load(rf.read_text())
        due = data.get("next_review_due")
        if due and parse_date(due) < today:
            overdue.append((data["id"], due, rf.name))

    if overdue:
        for rid, due, name in overdue:
            print(f"OVERDUE {rid} (due {due}) in {name}")
        print(f"\n{len(overdue)} rule(s) overdue for source review (as at {today}).")
        return 0 if args.warn_only else 1

    print(f"OK: no rules overdue for review (as at {today}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
