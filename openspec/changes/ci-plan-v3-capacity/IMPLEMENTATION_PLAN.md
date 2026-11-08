# CI capacity Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Complete the unchanged backend suite with measured runner headroom.

**Architecture:** Reuse file-level round-robin sharding. Keep the aggregator,
worker limit, security, coverage scope and protected check identities intact.

**Tech Stack:** Python, pytest, GitHub Actions, existing local bounded sweep.

**Spec:** [design.md](design.md), [authorization](BUILD_AUTHORIZATION.md).

## Global Constraints

- Start with five shards; six only if measured headroom is below 4096 MiB.
- Two effective workers; sole exclusion test_v1_acceptance.py unchanged.
- No app/SCI/mobile/SDK/API/migration/baseline/reuse or runner-class changes.
- CI_INFRA requires bounded full local and real PR/canonical CI.
- Stop if six remains insufficient; no invented success or threshold change.

## Review Focus

- Matrix drift: existing exact matrix comparison must reject missing/duplicate indexes.
- Coverage omission: existing aggregate derives expected count and rejects missing artifacts.
- Silent test exclusion: filesystem-anchored tests retain the exact singular exclusion.
- Worker drift: existing runner tests and actual logs must demonstrate two workers.
- Empty/missing resource series: real five/six-shard CI cannot be accepted without measurements.

### Task 1: Scale the existing topology and verify all consumers

**Files:**
- Modify: `scripts/ci_test_shards.py`, `.github/workflows/ci.yml`.
- Test: `tests/test_ci_shard_topology.py`.
- Document: this change and `docs/strategy/SPEC_REGISTRY.md` append only.

**Interfaces:**
- Consumes: `build_shards(shard_count=DEFAULT_SHARDS, root=None)`, CLI `--shard-count`.
- Produces: same signatures, default five; explicit matrix 1..5, derived reused-verdict message.

- [x] Update the existing minimum-capacity guard from three to five; add six to the existing arbitrary-count partition cases.
- [x] Run scope then that guard: expect `3 >= 5` failure before implementation.
- [x] Set DEFAULT_SHARDS=5, matrix [1,2,3,4,5], document incident; derive skipped-shard count via CLI.
- [x] Run topology/runner-stability/canonical-attestation tests; expect all pass, exact partition unchanged.
- [x] Run required Ruff/budget/spec/OpenSpec checks and bounded full local sweep; expect no failed batch.
- [x] Fresh whole-branch code review; correct Important findings with regressions.
- [ ] Commit/push/PR under standing authorization. Verify all tests, combined coverage, two workers and nonempty CI_RESOURCE samples with min available >=4096 MiB for every shard.
- [ ] If five fails capacity, change the same topology/guard to six, rerun affected checks and real new HEAD CI; stop if insufficient.
- [ ] Merge at guarded SHA only after all checks; verify canonical capacity/CI. Publish actual evidence; no CLOSED before canonical success.

### Delivery continuation

After the CI correction is integrated, synchronize the pushed PLAN closeout
branch with the current canonical without force-push; preserve both registry
append blocks. Verify its final HEAD and canonical, record Sonar, archive only
the authorized scopes and clean only integrated work without unique commits.

Self-review: spec sections map to Task 1 and continuation. No new subsystem or
interface required; historical SCI pins remain unchanged. Inline execution and
the design are already approved by the operator’s continuation instruction.
