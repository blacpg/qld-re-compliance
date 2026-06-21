# Plan — Behavioural eval runner (`scripts/run_eval.py`)

**Status: approved, implemented via PR (touches `scripts/`).**

**Goal:** Turn the `run_eval.py` stub into a working behavioural eval that calls the Anthropic API with the skill + the scenario's expected rule context, grades the reply against the existing `must_include` / `must_not_include` assertions **and** an `expected_outcome` marker, and exits non-zero on any failure. Read-only, cost-guarded, governed by PR + CI.

**Non-goals:** no new forms, modules, rules, scenarios, Form 7/8, or tenanted-sale work. No retrieval/routing eval (separate, later). No live-skill change. The runner stays out of CI (no key in CI).

## 1. API call
- **Model resolution priority:** CLI `--model` > env `EVAL_MODEL` > default **`claude-sonnet-4-6`**.
- **Env var:** `ANTHROPIC_API_KEY` required to actually call; absent → dry-run/list only.
- **`temperature: 0`**, **`max_tokens: 1024`** (overridable via `--max-tokens`).
- **Cost guard:** refuses to call the API unless one of `--all`, `--scenario`, or `--max-scenarios` is given.
- **Dependency:** `anthropic` imported lazily (only when calling); lives in `scripts/requirements-eval.txt`, separate from CI's `requirements.txt`.

## 2. Context (allowlist)
System prompt per scenario = `SKILL.md` + all `references/*.md` + the rule file(s) named by `expected_rule_ids` + only the register entries those rules cite + an **eval-only outcome instruction** (see §4). User message = the scenario `question`.
Never included: `sources/_downloads/`, `internal/`, anything outside `{skill/, rules/, sources/register.yaml, tests/scenarios/}`.

## 3. Rule selection
Preselect rule files by `expected_rule_ids` (tests answer behaviour, not retrieval). Empty `expected_rule_ids` → no rule files → forces the refusal path. Routing/retrieval is a separate future eval.

## 4. Grading
- `must_include` (all present) AND `must_not_include` (none present), case-insensitive — via the existing `check_response()`.
- **`expected_outcome` check (new):** the eval system prompt asks the model to end with a line `answer_outcome: <enum>`; if the scenario has `expected_outcome`, the grader requires `answer_outcome: <expected_outcome>` in the reply. This is an **eval-prompt construct only** — the published `SKILL.md` is NOT changed. If real runs show the skill should emit outcomes natively, that's a separate decision.
- Output: per-scenario PASS/FAIL with missing-required and forbidden-found lists; totals; **exit 1 if any fail**.

## 5. Safety
Read-only on tracked files; never edits/stages/commits. Sends only allowlisted files. `--save-output` writes only to a gitignored path (default `sources/_downloads/eval/`); the runner asserts the target is gitignored via `git check-ignore` at startup and aborts if not. Without `--save-output`, nothing is written.

## 6. CLI
`--all`, `--scenario SCN-xxx` (repeatable), `--max-scenarios N`, `--dry-run`, `--model NAME`, `--max-tokens N`, `--save-output [PATH]` (gitignored only), `--json`.

## 7. Governance
Touches `scripts/` → PR + green CI. Eval runner stays out of CI; CI only confirms the deterministic validators still pass with the new file present.

## File changes
- `scripts/run_eval.py` — implement runner.
- `scripts/requirements-eval.txt` — new (`pyyaml`, `anthropic`).
- `docs/superpowers/plans/2026-06-21-behavioural-eval-runner.md` — this plan.
- No rule / form / module / source-register / skill changes.

## Pre-PR testing (no API cost)
1. Deterministic validators all pass.
2. `--dry-run --scenario SCN-001` (answered) prints the right allowlisted files + the outcome instruction.
3. `--dry-run --scenario SCN-012` (refusal) prints no rule files.
4. Dry-run includes only allowlisted files; changes no tracked files.
5. `--save-output` to a non-gitignored path aborts (testable in dry-run via the startup assertion).
