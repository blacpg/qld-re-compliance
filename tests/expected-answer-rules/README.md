# Expected Answer Rules

The behavioural assertions that police how the skill answers live inline in each scenario under `tests/scenarios/` as `must_include` and `must_not_include`.

- `must_include` — substrings the answer must contain (e.g. the `rule_id`, the cited pinpoint like `s 99`, the escalation reason).
- `must_not_include` — banned phrases that signal an unsourced or hedge answer (e.g. "I think", "probably legal", "you should be fine").

`scripts/run_eval.py` runs the skill against each scenario and checks these assertions. It needs an Anthropic API key and is run on demand, not in CI (a public repo has no key).

As the rule set grows, shared assertion sets (for example "every substantive answer must contain a rule_id and a source_id") can be factored out into files here and referenced from scenarios. For now they are kept inline for readability.
