---
name: auren-sprint-from-spec
description: Use when the operator injects a short/vague product spec for AUREN and expects a full autonomous sprint under the delivery envelope — converts the concise spec into explicit acceptance criteria, implementation, tests, docs and a PR, without asking a series of clarifying questions.
---

# Sprint from a concise spec (AUREN)

The operator pastes a **short** spec and expects delivery, not interrogation. Absorb it, make its
implicit parts explicit, and run the standard delivery loop. Ask **nothing** that the repo can answer.

## Invocation shape

```
MISSION — GO BUILD <SPRINT_ID>
Use DELIVERY AUTONOMY ENVELOPE.
Canonical: <SHA or "latest canonical after previous closeout">
User spec:
<the concise spec>
```

## Interpretation rules (binding)

1. **Preserve product intent.** Never trade the operator's goal for implementation convenience.
2. **Convert vague terms into explicit acceptance criteria** and state them back in the sprint
   report. "Should feel fast", "make it smarter" ⇒ measurable, testable statements.
3. **Prefer additive implementation.** No architecture rewrite unless the spec demands it.
4. **Inspect the repo before coding.** Real code beats old reports; when a report and the code
   disagree, the code wins and you say so.
5. **Reuse** existing services, models, fixtures and QA. Do not re-implement what exists.
6. **Keep current UX / session / publication semantics** unless the spec explicitly changes them.
7. **On contradiction** between the spec and canonical closed architecture → **STOP with options**,
   never silently pick one.

## Loop

Preflight → classify scope (`DOCS` · `ISOLATED` · `SHARED_CODE` · `DB_WRITE` · `RUNTIME_FLOW`;
**when in doubt go one level up**) → smallest coherent design → targeted tests → sweep proportional
to risk → `check_scope` + ruff + budget + `check_spec_protocol` + relevant QA + targeted tests
(+ full sweep for shared code/data) → commit → push → PR → watch CI/Gitar/Sonar → fix in-scope
findings autonomously → repeat until **PR GREEN / MERGE PENDING**.

`check_scope` reporting `ISOLATED` is **not** a licence to skip the sweep when the change touches
shared data or runtime flow — that over-check has caught real regressions three times.

## Required output

Implementation · tests · `docs/SPRINT_<ID>_REPORT.md` · registry/roadmap update when applicable ·
PR body stating scope, files, tests, risks and non-regressions.

## Autonomy boundaries

**Do not stop for**: local lint/test fixes · in-scope CI red after authoritative diagnosis ·
in-scope Gitar/Sonar findings · re-running tests · adding regression tests · docs inside sprint scope.

**Always stop for**: merge · destructive cleanup · DB migration ambiguity · schema/lifecycle
contradiction · data-loss risk · secret/security · rewrite beyond sprint scope · `AGENTS.md` ·
dirty-worktree deletion · force-push or `--admin`.

**Never merge without an explicit `GO MERGE`** (or a standing one written into the sprint prompt —
see the `auren-standing-merge` skill). **Never clean up without `GO CLEANUP`** (or "cleanup included").

Finish with: `<SPRINT_ID> PR GREEN / MERGE PENDING`.
