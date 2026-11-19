# REL-03 OPS-03 — runner source hygiene investigation

19 November 2026. Parent `8c8184b27cddbc2046c7758eb184069c43a08d7e`.

## Brainstorming / Options / Risks / Choice

Actual BUILD_APK run44332229836, attempts1/2, fails in `Acquire all gates then
publish only to fixed QA project/channel` with `qa_pipeline_source_dirty`.
The private-proof import and dependency installation succeed. The failure is
before GitHub release-gate collection and any EAS publishing command. MFE-DSS's
actual exact candidate/proof approval is preserved; it is not missing.
The attachment qa-prepared.json is preparation metadata, not a failure log.

Do not bypass the source-cleanliness check, hide files with new ignore rules,
reset the runner, or retry the same failed operation. Attempt2 would also be
ineligible under the existing fresh-dispatch rule; do not relax it.
Actual Mac Node22.20.0/npm10.9.3 and disposable Linux Node22/npm10 reproductions
remain clean after pip/npm/EAS installation and Python import. The precise
GitHub-only path is not yet proven. No speculative application fix is admitted.

Chosen diagnostic: on PREPARE only, reproduce release dependency setup on the
actual credential-free GitHub runner, checking and reporting Git path/status
metadata at each boundary. No file contents, secret references, provider writes,
EAS build/update, QA or personal-service mutation. Preserve the original guard.
The protected job also reports path/status metadata before calling that guard.
This is an in-scope REL-03 correction investigation, not a new product scope.

## Execution plan

- [x] Add behavioral tests executing the workflow's actual diagnostic shell in a
  real temporary Git checkout. Clean setup passes; modified tracked/untracked
  source fails at its boundary; no source deletion or automatic reset.
- [x] Add PREPARE-only Node22.20.0 and release dependency reproduction; no provider
  credentials in that job. Preserve required review, runtime and publishing rules.
- [ ] Run check_scope (CI_INFRA), local bounded sweep and mandatory checks; review,
  commit/push under the existing GO, then dispatch PREPARE only on the exact branch.
- [ ] Acquire the real runner path before implementing the smallest proven fix.
  Update this receipt with cause and RED/GREEN evidence; independent review and
  mandatory exact-HEAD CI before merge. No old CI substituted for new source.
- [ ] After canonical delivery, prepare a new exact candidate/proof operation.
  Actual human candidate review stays distinct; no inherited rerun approval.

## State

INVESTIGATING. No new APK, no installed-client acceptance, no application/native,
scientific, schema, visual, lock or QA backend modification.

## Diagnostic checkpoint validation

Three RED cases became GREEN; 135 targeted pipeline/diagnostic tests pass on
Python3.11. OpenSpec28/28, actionlint, Ruff new tests, budget259≤548, protocol
and staged-diff Gitleaks pass. A whole-directory Gitleaks scan flags the existing
Sonar issue identifier in docs/SONAR_AUDIT_01_REPORT.md:197; it is unchanged and
is a quoted issue key, not a newly exposed credential. No allowlist change.
Independent diagnostic review has no findings. The required local bounded full
sweep is still running: no global PASS or merge readiness claimed. This checkpoint
may be pushed solely to acquire credential-free PREPARE runner evidence. It is
not a corrected release candidate or a complete feature delivery.
