---
name: auren-sonar-diagnosis
description: Use when a SonarCloud gate is red, a Sonar finding must be located, or a Sonar issue needs adjudicating — defines the ordered diagnosis route (gate → authenticated CLI → metrics fallback → source confirmation), the pagination trap, and the false-positive vs accepted rule.
---

# Sonar diagnosis route (AUREN)

**The remote SonarCloud Quality Gate is the merge authority.** The `sonar` CLI is a *diagnostic
aid* — it locates and explains findings. It never decides whether a PR may merge. A local CLI
result that disagrees with the PR gate does not override the gate; it means you have not yet
found the real cause.

## Route — in this order, stop as soon as you have the exact issue

### 1. Authoritative gate result

```bash
sonar api GET '/api/qualitygates/project_status?projectKey=MFE-DSS_workout-session-tracking&pullRequest=<N>'
```

Tells you **which conditions** failed and by how much. It does **not** tell you which line.
Never change code from this alone — see the hard rules below.

### 2. Authenticated issue retrieval — the exact finding

```bash
sonar auth status    # must print [✓ Connected]; if not, STOP and fix auth, do not fall back to guessing
sonar list issues --project MFE-DSS_workout-session-tracking --pull-request <N> --format json
```

This returns rule id, severity, component and line **in one call**. It is the normal route.

**Project-wide queries paginate and truncate silently.** `--page-size` caps at 500 and the CLI
warns about nothing:

```bash
sonar list issues --project MFE-DSS_workout-session-tracking --format json --page-size 500 --page 1
sonar list issues --project MFE-DSS_workout-session-tracking --format json --page-size 500 --page 2
# … then dedupe on .key and check paging.total matches what you collected
```

### 3. Metrics fallback — only when step 2 is unavailable

Use when the CLI is unauthenticated or the endpoint is unreachable:

```bash
sonar api GET '/api/measures/component_tree?...&metricKeys=new_major_violations,new_critical_violations&qualifiers=FIL'
```

Two traps that cost real CI cycles before this route was written down:

- **`qualifiers=FIL` does not return test files.** A module tree that looks clean while the gate
  is red means the finding is in `tests/` — query the test path directly with
  `api/measures/component?component=<key>%3Atests%2F<file>.py`.
- **Severity weights: MAJOR = 15, CRITICAL = 10.** A single MAJOR breaks
  `new_code_smells_severity > 14` on its own. Use the arithmetic to infer *how many* findings you
  are looking for before you go hunting.

### 4. Source confirmation — always, before touching anything

Read the flagged line and its `textRange` offsets. Confirm the finding describes what the code
actually does. Sonar reports offsets, not intent: `bullets[:4]` and `bullets[4]` occupy similar
ranges and mean entirely different things.

## Hard rules

- **Never change code from an aggregate severity number alone.** Locate the exact issue first.
  Guessing from the gate delta has cost this repo three CI cycles in one sprint.
- **Distinguish an API/network failure from an analysis failure.** `403`/`404`/timeout on the
  Sonar API means *you cannot see the result* — it does **not** mean the analysis passed or
  failed. Say which one you observed.
- **Pre-scan `app/` AND `tests/` before pushing** for the rules that recur here. Scanning only
  the modules is the gap that let `S9073` through on PR #82.

  ```python
  import ast, pathlib
  for f in CHANGED_FILES:                       # every touched .py, tests included
      tree = ast.parse(pathlib.Path(f).read_text(encoding="utf-8"))
      print(f, "S9073:", [n.lineno for n in ast.walk(tree)
            if isinstance(n, ast.Assert) and isinstance(n.test, ast.BoolOp)])
  ```

  Recurring here: `python:S9073` (composite assertion, tests), `python:S5863` / `python:S1764`
  (identical operands), `python:S1192` (literal duplicated 3+ times), `python:S5778`.

## Adjudicating a finding

`FALSE POSITIVE` and `ACCEPTED` are not interchangeable:

- **FALSE POSITIVE** — the analyzer is *wrong about the code*. Use for engine mistakes: a slice
  read as an index access, a Jinja `{# … #}` comment parsed as live markup.
- **ACCEPTED** — the analyzer is *right* and the project chooses to keep the construct anyway.
  Use for contract-required constructs, with the reason.

Never mark an analyzer mistake as ACCEPTED — it records the tool as correct and hides the defect
in its engine. Always attach a technical justification naming the evidence.

```bash
sonar api POST '/api/issues/do_transition' --data '{"issue":"<KEY>","transition":"falsepositive"}'
sonar api POST '/api/issues/add_comment'   --data '{"issue":"<KEY>","text":"<why, with evidence>"}'
```

Adjudication is **never** bulk work and never a way to green a gate. One issue, one proof.

## Imported findings are not Sonar's to fix

Rules prefixed `external_ruff:` / `external_bandit:` are ingested verbatim from
`ruff-report.json` / `bandit-report.json` (`sonar-project.properties`). They carry no Sonar rule
engine behind them.

- Changing a Sonar Quality Profile **cannot** fix or silence them.
- They are not eligible for Sonar-native automated remediation.
- The fix belongs to the originating analyzer's own configuration — `pyproject.toml`
  (`[tool.ruff.lint]`, `[tool.bandit]`) and `.ruff-budget.json`.

A `noqa` silences ruff but **not** bandit, and Sonar ingests both reports. Suppressing one leaves
the other's copy open in Sonar.
