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
remain clean after pip/npm/EAS installation and Python import. At that checkpoint the precise GitHub-only path was not yet proven.
The acquired cause and correction below supersede that investigation status.

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

SOURCE FIX UNDER VERIFICATION. No new APK, no installed-client acceptance, no application/native,
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

## Acquired root cause and bounded correction

The first credential-free GitHub PREPARE44504762716 succeeds after the same
Python/npm/EAS setup. Those installers are not the reproduced writer.
The original runner identifies ubuntu26/20261111.196, whose published software
inventory specifies GitHub CLI2.103.3. With that actual Linux CLI, the original
`gh_command` environment (PATH/GH_HOST/GH_TOKEN/GH_PROMPT_DISABLED, no HOME)
creates `.local/state/gh/device-id` relative to cwd. Reproduced using only a
synthetic invalid token and an HTTP401 read: no private credential is needed to
trigger the write. The CLI's telemetry/device-identity initialization is the
writer, not a mobile-source mutation. Local CLI2.87.3 did not reproduce it.

Primary references: [actual runner image inventory](https://github.com/actions/runner-images/blob/ubuntu26/20261111.196/images/ubuntu/Ubuntu2604-Readme.md),
[CLI device-state implementation](https://github.com/cli/cli/blob/v2.103.3/internal/telemetry/telemetry.go).
The exact failed runner did not expose its path; this root cause is reproduced
from its specified CLI and the exact wrapper envelope, rather than a recovered
post-mortem filesystem. Actual fixed GitHub proof-reader execution remains required.

Options: inheriting the operator HOME would place state outside source but also
admit ambient GitHub configuration/credentials; ignoring/deleting `.local` would
hide evidence without fixing the writer. Chosen: each CLI command receives an
exclusive0700 temporary HOME outside both checkout/cwd, retains the explicit
token-only environment, disables CLI telemetry, and removes only that private
state on success/failure. A temporary root inside source is refused. No API,
crypto, approval, fresh-dispatch, source cleanliness or immutable-readback gate
is relaxed. No user HOME/configuration/cache is changed.

Three new behavioral regression cases were RED against the old wrapper: success,
failure cleanup, and a temporary directory incorrectly located inside source.
The actual2.103.3 Linux CLI leaves source empty with the corrected envelope and
private HOME0700. A fourth workflow case verifies that CLI-state source pollution
is reported and refused. The PREPARE probe now exercises the actual wrapper with
only the built-in read token and public product-repository GET, before review.
No private-proof or Expo credential is exposed to PREPARE.

## Fix checkpoint verification

174 proof/pipeline/workflow tests PASS on Python3.11 after the three new wrapper
RED cases. Actual private immutable ciphertext readback still matches its pinned
SHA with the corrected wrapper; no value is printed and no generated source
state appears. Ruff changed files and actionlint PASS. A fresh independent
review of the fix and regressions has no Critical/Important/Minor findings.
The CI_INFRA full local sweep remains running; final GitHub CI and actual
credential-free runner proof-reader execution remain required before merge.
