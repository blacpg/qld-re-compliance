# Install

How to install the **qld-property-compliance** skill so Claude can use it.

This is a Claude Code skill: a source-backed Queensland property-**sales** compliance
assistant. It answers only from the rule files in this repo and cites the exact
source; it refuses when no cited rule covers the question. It is **not legal advice**
(see [DISCLAIMER.md](DISCLAIMER.md)).

---

## Quick install (macOS / Linux)

The repo is public, so no authentication is needed.

### 1. Clone the repo

```bash
git clone https://github.com/blacpg/qld-re-compliance.git ~/qld-re-compliance
```

(Clone anywhere you like; if you change the location, change the `R=` line below.)

### 2. Install it as a Claude skill

This creates a self-contained skill folder whose entries symlink back to the repo,
so the repo stays the single source of truth and `git pull` updates the skill
automatically.

```bash
R=~/qld-re-compliance
S=~/.claude/skills/qld-property-compliance
mkdir -p "$S"
ln -sfn "$R/skill/qld-property-compliance/SKILL.md"   "$S/SKILL.md"
ln -sfn "$R/skill/qld-property-compliance/references" "$S/references"
ln -sfn "$R/rules"     "$S/rules"
ln -sfn "$R/sources"   "$S/sources"
ln -sfn "$R/modules"   "$S/modules"
ln -sfn "$R/docs"      "$S/docs"
ln -sfn "$R/DISCLAIMER.md" "$S/DISCLAIMER.md"
```

### 3. Use it

Restart Claude Code (skills are loaded at session start), then either:

- type `/` and choose **`qld-property-compliance`**, or
- just ask a Queensland property-sales question (e.g. *"Do I need a licensed
  auctioneer to run my auction?"* or *"How long must I hold a deposit?"*).

It will answer from the rules with citations, or refuse and route you on if no cited
rule covers the question.

### Updating

```bash
git -C ~/qld-re-compliance pull
```

The symlinks mean the skill picks up the new rules automatically — no re-install.

---

## Project-level install (one project only)

To make the skill available in a single project rather than for your whole user
account, point `S` at that project's `.claude/skills` directory instead:

```bash
S="/path/to/your/project/.claude/skills/qld-property-compliance"
```

then run the same `ln -sfn …` commands.

---

## Windows

Symlinks are awkward on native Windows. Either:

- run the steps above under **WSL**, or
- **copy** the folders instead of symlinking (`cp -r` equivalents) — but then you must
  re-copy after each `git pull` rather than the symlinks updating automatically.

---

## You do NOT need these just to use the skill

The following are only for maintainers who want to run the checks or the eval:

- **Validators** (no cost): `python3 -m pip install -r scripts/requirements.txt`, then
  run the five validators in [CONTRIBUTING.md](CONTRIBUTING.md).
- **Behavioural eval** (needs an Anthropic API key, real spend):
  `python3 -m pip install -r scripts/requirements-eval.txt`. See the runner header in
  `scripts/run_eval.py`. Use `--dry-run` for a free preview.

Using the skill itself requires none of the above — only the clone and the symlinks.

---

## Scope reminder

Queensland property **sales** only. Tenancies, property management, other states, tax
and finance are out of scope and will be refused. See [README.md](README.md) and
[docs/](docs/) for the governance model and what is covered.
