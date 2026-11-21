# REL-03 — SDK channel groups after the first real QA update

21 November 2026. Parent `6beba77afb4ea2ae5e4fa2efbdec0255a4030517`.
Correction within the existing REL03 build/OPS mandate and GOV-MERGE-01. No new
product, geometry, schema, credentials, deployment or publication authorization.

## Brainstorming / Options / Risques / Choix retenu

The approved UPDATE44901053814 succeeded. Actual installed update01a1fe9c-d75e-78cb-b38a-045af4a30421
runs JS6beba77 on native3bd, runtime8c3. The later **local read-only** rollback
preflight stops at `qa_eas_channel_or_rollout_refused`: pinned EAS27.2 channel:view
returns `updateGroups: [[AndroidUpdate]]`, without rollout fields. Previously the
channel was empty, so the incorrect flat fixture did not expose the defect.

Do not flatten and invent null rollout flags. Do not remove the rollout check.
Chosen repair: recognize the observed grouped SDK shape explicitly, require its
QA branch/platform/runtime identities and bind it to the independently acquired
exact-runtime GraphQL rollout witness. Keep the existing strict flat shape for
its already tested consumers. Missing/partial rollout evidence remains refused.
The publisher still reacquires exact-runtime rollout immediately before effects.
No change to the protected approval, backup, source, known-good or native guards.

## Plan, ownership and checks

Own tools/qa_delivery/pipeline.py, tests/test_qa_delivery_pipeline.py, this receipt
and the existing REL03 ledger. No mobile/shared-server lease. Preserve the installed
APK/update and the incomplete rollback PREPARE/backup proof; do not dispatch it
against stale code or claim a rollback occurred.

1. Add a sanitized witness of the actual nested response; demonstrate RED.
2. Bind parsing to the exact-runtime observation, with negative shape/branch/
   unknown/partial rollout tests and real acquisition probe before publication.
3. Run check_scope first; conservatively treat publisher changes as CI_INFRA:
   bounded local sweep, release broad tests, budget/spec/security and actual CI.
4. Independent review, exact HEAD protected checks, guarded merge and canonical CI.
5. Reconcile future release preparation to the resulting canonical/workflow source.
   The current approved OTA stays active. Any additional publication requires its
   own protected review; no rollback to the defective embedded JS is proposed.

## Evidence limits

The existing known-good receipt covers synthetic emulator smoke, not all pilot
flows or physical acceptance. A same-source republish would exercise the protected
rollback path, not recovery from a deliberately bad OTA. This correction does not
change that distinction. No native rebuild is needed for this publisher-only fix.

## Verification and independent review

The initial nested-response regression is RED on the prior interface. Full release
pipeline:168PASS. The fixture for native mismatch no longer simultaneously injects
an active rollout; each refusal is exercised independently. SDK flat, grouped
other-runtime and grouped installed-runtime cases traverse the real publish entry
for UPDATE and ROLLBACK. Partial GraphQL responses fail at both observations;
last-minute channel pause/remap fails before every provider mutation.

The live authenticated read-only query matches the captured SDK response's exact
branch and Android update/group/runtime; missing witness is refused. No external
write is performed by that probe. GitHub publication remains independently gated.

check_scope reports ISOLATED for the four-file leaf diff. Conservatively elevated
to publisher/CI_INFRA for verification: bounded local sweep completes459/459files,
all batches green, maximum1715MiB within1953MiB budget, no files skipped. Ruff
changed files,259≤548budget, protocol, strictOpenSpec28/28 and scoped Gitleaks pass. Bandit -ll on the changed
publisher passes; the unfiltered scan retains five LOW findings (B404/fourB603),
identical to the parent, zero MEDIUM/HIGH. No new local mobile sweep: mobile/native/lock/storage sources are unchanged;
mandatory remote mobile/visual checks still apply.

Independent review's two Important findings are fixed: reject data+errors rather
than treating unresolved nullable rollout fields as no rollout; bind branch and
update/group IDs and reacquire channel mapping immediately before effects. Re-read
finds no Critical/Important. Minor retained: legacy UUID regex permits36hyphens;
exact equality of independently acquired publication identities remains required.
No scientific, visual or operational permission derives from these checks.

The already installed known-good JS6beba77 remains attributed to that source.
A new tooling merge does not change its EAS gitCommitHash or qualify a rollback
candidate from another SHA. Future protected preparation must preserve that
binding; this change does not reinterpret a previous approval or republish group.
