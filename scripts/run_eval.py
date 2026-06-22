#!/usr/bin/env python3
"""Behavioural eval: run the skill against tests/scenarios/ and grade the replies.

This is NOT part of CI. To actually call the model it needs an Anthropic API key.
It is read-only on tracked files: it never edits, stages, or commits anything, and
only sends an allowlisted set of repo files (skill + the scenario's expected rule
files + the cited source entries) to the model.

Model resolution priority: --model > $EVAL_MODEL > default (claude-sonnet-4-6).

Usage (no cost):
    python3 scripts/run_eval.py --dry-run --scenario SCN-001

Usage (calls the model; needs a key and an explicit scope):
    export ANTHROPIC_API_KEY=...
    python3 scripts/run_eval.py --all
    python3 scripts/run_eval.py --scenario SCN-001 --scenario SCN-006
    python3 scripts/run_eval.py --max-scenarios 5 --save-output

Requires: pyyaml always; anthropic only when actually calling the model
(see scripts/requirements-eval.txt).
"""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    sys.exit(f"Missing dependency: {exc}. Run: pip install -r scripts/requirements-eval.txt")

ROOT = Path(__file__).resolve().parent.parent
SKILL_DIR = ROOT / "skill" / "qld-property-compliance"
SKILL_MD = SKILL_DIR / "SKILL.md"
REFERENCES_DIR = SKILL_DIR / "references"
RULES_DIR = ROOT / "rules"
REGISTER = ROOT / "sources" / "register.yaml"
SCENARIOS_DIR = ROOT / "tests" / "scenarios"
DOWNLOADS = ROOT / "sources" / "_downloads"
INTERNAL = ROOT / "internal"

DEFAULT_MODEL = "claude-sonnet-4-6"
DEFAULT_MAX_TOKENS = 2048
DEFAULT_SAVE_DIR = DOWNLOADS / "eval"
OUTCOME_ENUM = ["answered", "refused_unsourced", "refused_out_of_scope", "escalated", "uncertain"]

# Eval-only instruction. This is NOT part of the published skill; it only asks the
# model to emit a machine-checkable outcome marker so the grader can verify
# expected_outcome. The live SKILL.md is unchanged.
EVAL_OUTCOME_INSTRUCTION = (
    "\n\n---\nEVAL HARNESS INSTRUCTION (for this evaluation only; not part of the "
    "published skill):\nAfter your full answer, output a final line exactly in this "
    "form:\nanswer_outcome: <one of " + " | ".join(OUTCOME_ENUM) + ">\nChoose the "
    "single value that best describes how your answer resolved.\n"
)


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------
def load_scenarios():
    scenarios = []
    for p in sorted(SCENARIOS_DIR.glob("*.yaml")):
        data = yaml.safe_load(p.read_text())
        if isinstance(data, list):
            scenarios.extend(data)
        elif isinstance(data, dict):
            scenarios.append(data)
    return scenarios


def build_rule_index():
    """Map rule id -> file path by scanning rules/."""
    index = {}
    for rf in sorted(RULES_DIR.rglob("*.yaml")):
        data = yaml.safe_load(rf.read_text())
        if isinstance(data, dict) and data.get("id"):
            index[data["id"]] = rf
    return index


def load_register():
    data = yaml.safe_load(REGISTER.read_text())
    return {s["source_id"]: s for s in data.get("sources", [])}


# ---------------------------------------------------------------------------
# Safety
# ---------------------------------------------------------------------------
def assert_allowlisted(path: Path):
    """Hard guard: a context file must be under the allowlist and never under
    sources/_downloads/ or internal/."""
    rp = path.resolve()
    if DOWNLOADS in rp.parents or rp == DOWNLOADS or INTERNAL in rp.parents or rp == INTERNAL:
        raise RuntimeError(f"refusing to include non-allowlisted path: {rp}")
    allowed_roots = [SKILL_DIR, RULES_DIR, SCENARIOS_DIR]
    if rp == REGISTER.resolve():
        return
    if not any(root.resolve() in rp.parents for root in allowed_roots):
        raise RuntimeError(f"refusing to include path outside the allowlist: {rp}")


def is_gitignored(path: Path) -> bool:
    res = subprocess.run(
        ["git", "-C", str(ROOT), "check-ignore", "-q", str(path)],
        capture_output=True,
    )
    return res.returncode == 0


# ---------------------------------------------------------------------------
# Context assembly
# ---------------------------------------------------------------------------
def build_context(scenario, rule_index, register):
    """Return (system_prompt, user_message, included_files)."""
    included = []
    parts = []

    assert_allowlisted(SKILL_MD)
    parts.append(f"# SKILL: {SKILL_MD.relative_to(ROOT)}\n\n{SKILL_MD.read_text()}")
    included.append(str(SKILL_MD.relative_to(ROOT)))

    for ref in sorted(REFERENCES_DIR.glob("*.md")):
        assert_allowlisted(ref)
        parts.append(f"# REFERENCE: {ref.relative_to(ROOT)}\n\n{ref.read_text()}")
        included.append(str(ref.relative_to(ROOT)))

    rule_ids = scenario.get("expected_rule_ids", []) or []
    cited_source_ids = []
    missing_rules = []
    if rule_ids:
        rule_blocks = []
        for rid in rule_ids:
            rf = rule_index.get(rid)
            if not rf:
                missing_rules.append(rid)
                continue
            assert_allowlisted(rf)
            rule_blocks.append(f"# RULE {rid}: {rf.relative_to(ROOT)}\n\n{rf.read_text()}")
            included.append(str(rf.relative_to(ROOT)))
            data = yaml.safe_load(rf.read_text())
            for s in data.get("sources", []):
                if s.get("source_id"):
                    cited_source_ids.append(s["source_id"])
        if rule_blocks:
            parts.append("# AVAILABLE RULES\n\n" + "\n\n".join(rule_blocks))
    else:
        parts.append(
            "# AVAILABLE RULES\n\nNo rule file is provided for this question. "
            "If no cited rule covers it, follow the refusal protocol."
        )

    if cited_source_ids:
        seen = []
        src_blocks = []
        for sid in cited_source_ids:
            if sid in seen:
                continue
            seen.append(sid)
            entry = register.get(sid)
            if entry:
                src_blocks.append(yaml.safe_dump({"sources": [entry]}, sort_keys=False))
        if src_blocks:
            parts.append("# REGISTERED SOURCES (only those cited by the rules above)\n\n"
                         + "\n".join(src_blocks))
        included.append(f"sources/register.yaml ({len(seen)} cited entr{'y' if len(seen)==1 else 'ies'})")

    system_prompt = "\n\n".join(parts) + EVAL_OUTCOME_INSTRUCTION
    user_message = scenario["question"]
    return system_prompt, user_message, included, missing_rules


# ---------------------------------------------------------------------------
# Grading
# ---------------------------------------------------------------------------
def grade(scenario, response_text: str):
    """Return list of failures. Empty list == pass."""
    failures = []
    lowered = response_text.lower()
    for needle in scenario.get("must_include", []):
        if needle.lower() not in lowered:
            failures.append(f"missing required: {needle!r}")
    for banned in scenario.get("must_not_include", []):
        if banned.lower() in lowered:
            failures.append(f"contains banned: {banned!r}")
    expected = scenario.get("expected_outcome")
    if expected:
        marker = f"answer_outcome: {expected}"
        if marker.lower() not in lowered:
            failures.append(f"missing outcome marker: {marker!r}")
    return failures


# ---------------------------------------------------------------------------
# Model call (lazy import)
# ---------------------------------------------------------------------------
def call_model(model, system_prompt, user_message, max_tokens):
    try:
        import anthropic
    except ImportError:
        sys.exit("Missing dependency 'anthropic'. Run: pip install -r scripts/requirements-eval.txt")
    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY
    resp = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        temperature=0,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )
    return "".join(b.text for b in resp.content if getattr(b, "type", None) == "text")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def resolve_model(cli_model):
    return cli_model or os.environ.get("EVAL_MODEL") or DEFAULT_MODEL


def select_scenarios(all_scenarios, args):
    selected = all_scenarios
    if args.scenario:
        wanted = set(args.scenario)
        selected = [s for s in all_scenarios if s.get("id") in wanted]
    if args.max_scenarios is not None:
        selected = selected[: args.max_scenarios]
    return selected


def main() -> int:
    ap = argparse.ArgumentParser(description="Behavioural eval runner for the QLD compliance skill.")
    ap.add_argument("--all", action="store_true", help="Run all scenarios (explicit opt-in for a paid run)")
    ap.add_argument("--scenario", action="append", help="Run specific scenario id(s); repeatable")
    ap.add_argument("--max-scenarios", type=int, help="Cap the number of scenarios run")
    ap.add_argument("--dry-run", action="store_true", help="Assemble + print context only; no API call, no cost")
    ap.add_argument("--model", help="Override model (default via EVAL_MODEL or claude-sonnet-4-6)")
    ap.add_argument("--max-tokens", type=int, default=DEFAULT_MAX_TOKENS, help="Max output tokens (default 2048)")
    ap.add_argument("--save-output", nargs="?", const=str(DEFAULT_SAVE_DIR), default=None,
                    help="Write transcripts/results to a GITIGNORED path only (default sources/_downloads/eval/)")
    ap.add_argument("--json", action="store_true", help="Print a machine-readable summary")
    args = ap.parse_args()

    model = resolve_model(args.model)

    # Save-output safety: assert the target is gitignored BEFORE anything else.
    save_dir = None
    if args.save_output is not None:
        save_dir = Path(args.save_output)
        if not save_dir.is_absolute():
            save_dir = ROOT / save_dir
        if not is_gitignored(save_dir):
            sys.exit(f"--save-output target is not gitignored: {save_dir}. Refusing to write to a tracked path.")

    all_scenarios = load_scenarios()
    rule_index = build_rule_index()
    register = load_register()
    selected = select_scenarios(all_scenarios, args)

    if not selected:
        print("No scenarios selected. Check --scenario ids.")
        return 0

    key_present = bool(os.environ.get("ANTHROPIC_API_KEY"))

    # ---- DRY RUN ----
    if args.dry_run:
        print(f"DRY RUN — model would be: {model}; max_tokens={args.max_tokens}; scenarios={len(selected)}")
        if save_dir:
            print(f"save-output target (gitignored OK): {save_dir}")
        for s in selected:
            system_prompt, user_message, included, missing = build_context(s, rule_index, register)
            approx_tokens = (len(system_prompt) + len(user_message)) // 4
            print(f"\n=== {s['id']} [{s.get('expected_outcome','-')}] ===")
            print(f"  question: {s['question']}")
            print(f"  included context files ({len(included)}):")
            for f in included:
                print(f"    - {f}")
            if missing:
                print(f"  WARNING missing rule files for ids: {missing}")
            print(f"  ~system+user tokens: {approx_tokens}")
            print(f"  outcome instruction appended: yes")
        print("\nDry run complete. No API call made, no files written.")
        return 0

    # ---- REAL RUN ----
    if not key_present:
        print("ANTHROPIC_API_KEY not set. Use --dry-run (no cost), or set the key to run live.")
        print("\nScenarios that WOULD be run:")
        for s in selected:
            print(f"  {s['id']}  [{s.get('expected_outcome','-')}]  {s['question'][:70]}")
        return 0

    # Cost guard: require an explicit scope before spending money.
    if not (args.all or args.scenario or args.max_scenarios is not None):
        sys.exit("Refusing to run all scenarios against the API without an explicit scope. "
                 "Use --all, --scenario, or --max-scenarios.")

    results = []
    passed = 0
    for s in selected:
        system_prompt, user_message, included, missing = build_context(s, rule_index, register)
        reply = call_model(model, system_prompt, user_message, args.max_tokens)
        failures = grade(s, reply)
        ok = not failures
        passed += int(ok)
        results.append({"id": s["id"], "pass": ok, "failures": failures})
        status = "PASS" if ok else "FAIL"
        print(f"{status}  {s['id']}  [{s.get('expected_outcome','-')}]")
        if not ok:
            for f in failures:
                print(f"      - {f}")
        if save_dir:
            save_dir.mkdir(parents=True, exist_ok=True)
            (save_dir / f"{s['id']}.txt").write_text(
                f"# {s['id']}\nMODEL: {model}\n\nQUESTION:\n{user_message}\n\n"
                f"RESPONSE:\n{reply}\n\nGRADE: {status}\nFAILURES: {failures}\n"
            )

    total = len(results)
    failed = total - passed
    print(f"\nSummary: {passed}/{total} passed, {failed} failed (model {model}).")
    if save_dir:
        (save_dir / "summary.json").write_text(json.dumps(results, indent=2))
        print(f"Transcripts written to {save_dir} (gitignored).")
    if args.json:
        print(json.dumps({"model": model, "passed": passed, "failed": failed, "results": results}, indent=2))

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
