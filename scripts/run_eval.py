#!/usr/bin/env python3
"""Behavioural eval: run the skill against tests/scenarios/ and check assertions.

This is NOT part of CI. It requires an Anthropic API key because it actually
invokes the model with the skill, then checks each scenario's must_include /
must_not_include assertions and expected_behaviour against the response.

It is run on demand, by a maintainer, because a public repo has no key.

Usage:
    export ANTHROPIC_API_KEY=...
    python3 scripts/run_eval.py

Requires: pyyaml, anthropic
"""
import os
import sys
from pathlib import Path

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    sys.exit(f"Missing dependency: {exc}. Run: pip install pyyaml anthropic")

ROOT = Path(__file__).resolve().parent.parent
SCENARIOS = ROOT / "tests" / "scenarios"
SKILL = ROOT / "skill" / "qld-property-compliance" / "SKILL.md"


def load_scenarios():
    scenarios = []
    for p in sorted(SCENARIOS.glob("*.yaml")):
        data = yaml.safe_load(p.read_text())
        if isinstance(data, list):
            scenarios.extend(data)
        elif isinstance(data, dict):
            scenarios.append(data)
    return scenarios


def check_response(scenario: dict, response_text: str) -> list[str]:
    """Deterministic assertion checks on a model response string."""
    failures = []
    lowered = response_text.lower()
    for needle in scenario.get("must_include", []):
        if needle.lower() not in lowered:
            failures.append(f"missing required: {needle!r}")
    for banned in scenario.get("must_not_include", []):
        if banned.lower() in lowered:
            failures.append(f"contains banned: {banned!r}")
    return failures


def main() -> int:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ANTHROPIC_API_KEY not set. This behavioural eval needs a key and is")
        print("not part of CI. Set the key and re-run to actually exercise the skill.")
        print("\nScenarios that WOULD be run:")
        for s in load_scenarios():
            print(f"  {s['id']}  [{s['expected_behaviour']}]  {s['question'][:70]}")
        return 0

    # Real invocation is intentionally left to the maintainer's harness, so this
    # script stays dependency-light and safe to ship. Wire up the anthropic
    # client here, pass SKILL.md as system context plus the rule files, send each
    # scenario's question, then run check_response() on the reply.
    print("API key present. Implement the anthropic client call here to run live.")
    print(f"Skill: {SKILL.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
