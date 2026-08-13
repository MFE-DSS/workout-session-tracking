---
name: auren-standing-merge
description: Use when the operator has written STANDING GO MERGE into a sprint prompt — defines the exact gate checklist to verify before merging autonomously, the merge command form, and the closeout that must follow.
---

# Standing GO MERGE (AUREN)

A standing merge authorisation is **only** active when the operator wrote it **into the sprint
prompt**. It is never inferred from a green PR, from a previous sprint, or from a bare "GO".

## Gate — verify ALL, authoritatively, immediately before merging

Re-check right before the merge call (state drifts while CI runs):

1. **Head SHA** known and unchanged — `gh pr view <N> --json headRefOid`.
2. **Required checks green** — `gh pr checks <N>` (every row `pass`, including the **external**
   `SonarCloud Code Analysis` gate, which is distinct from the internal `SonarCloud` job).
3. **Sonar gate CLEAN** — `qualitygates/project_status?...&pullRequest=<N>` returns `status: OK`.
   A red gate is **never** an artifact: locate the exact finding with
   `sonar list issues --pull-request <N>` and fix the real cause. Route and traps:
   `auren-sonar-diagnosis`.
4. **0 unresolved review thread** — GraphQL `reviewThreads`, count `isResolved == false`.
5. **Mergeable** — `mergeStateStatus: CLEAN`, `mergeable: MERGEABLE`.
6. **No scope drift** — the diff still matches the sprint's declared perimeter.

If any check is not authentically satisfied, **do not merge** — diagnose and fix in scope, or STOP.

## Merge

```bash
gh pr merge <N> --repo MFE-DSS/workout-session-tracking \
  --merge --match-head-commit <HEAD_SHA>
```

**No squash. No `--admin`. No force.** Always pin the head commit.

## After the merge

1. **Canonical CI** — if the merge contains code, find the `push` run on the merge commit and
   verify it is genuinely green (3/3). It is the source of truth.
2. **Docs-only merge** — the push CI is legitimately skipped by `paths-ignore: docs/**`
   (`CLAUDE.md §2`). That is **not** a manual `[skip ci]`: **record the skip explicitly** in the
   closeout, and note the PR CI as the source of truth.
3. **Closeout** — post-merge appendix in the sprint report (merge SHA, CI run id, Sonar verdict,
   incidents resolved in scope), `SPEC_REGISTRY` status → MERGED, `ROADMAP` updated.
4. **Push the closeout** (docs-only) and verify the final canonical SHA.

## Cleanup

**Separate by default.** Only bundled when the operator writes `cleanup included`. Even then:
delete **only** the clean worktree/branch of the sprint just merged; never a dirty worktree, never
an unrelated one, never `AGENTS.md`, never a dependabot branch.
