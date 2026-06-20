#!/usr/bin/env python3
"""Detect rules whose source review is overdue or whose review window is too long.

Two checks:
1. Overdue: next_review_due is in the past.
2. Cadence: the window (next_review_due - last_source_check) must not exceed the
   module's maximum. seller-disclosure = 60 days (the scheme is new and volatile);
   everything else = 90 days.

Plus a reminder: rules with event_triggered_review (default true) must also be
reviewed BEFORE next_review_due whenever an official source changes (a
legislative amendment, a new or updated OFT page, a new approved form version,
or a relevant court decision). A script cannot detect those events, so it prints
a standing reminder.

Pass --today YYYY-MM-DD to check against a fixed date. --warn-only exits 0.

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

CADENCE_DAYS = {"seller-disclosure": 60}
DEFAULT_CADENCE_DAYS = 90


def parse_date(value: str) -> date:
    return date.fromisoformat(str(value))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--today", help="Override today's date (YYYY-MM-DD)")
    ap.add_argument("--warn-only", action="store_true", help="Report but exit 0")
    args = ap.parse_args()

    today = parse_date(args.today) if args.today else date.today()

    overdue = []
    window_too_long = []
    event_triggered = 0

    for rf in sorted(RULES_DIR.rglob("*.yaml")):
        data = yaml.safe_load(rf.read_text())
        module = data.get("module", "")
        cadence = CADENCE_DAYS.get(module, DEFAULT_CADENCE_DAYS)

        last = data.get("last_source_check")
        due = data.get("next_review_due")
        if due and parse_date(due) < today:
            overdue.append((data["id"], due, rf.name))
        if last and due:
            window = (parse_date(due) - parse_date(last)).days
            if window > cadence:
                window_too_long.append((data["id"], window, cadence, module, rf.name))

        # default true when omitted
        if data.get("event_triggered_review", True):
            event_triggered += 1

    problems = 0
    for rid, due, name in overdue:
        print(f"OVERDUE {rid} (due {due}) in {name}")
        problems += 1
    for rid, window, cadence, module, name in window_too_long:
        print(f"CADENCE {rid}: review window {window}d exceeds {cadence}d max for module '{module}' ({name})")
        problems += 1

    print(
        f"\nReminder: {event_triggered} rule(s) are event_triggered_review=true and must be "
        f"reviewed before their due date if an official source changes (amendment, new OFT "
        f"guidance, new form version, relevant court decision)."
    )

    if problems:
        print(f"{problems} review problem(s) (as at {today}).")
        return 0 if args.warn_only else 1

    print(f"OK: all rules within cadence and current (as at {today}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
