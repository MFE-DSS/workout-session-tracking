# REL03 — PREPARED / BLOCKED_EXTERNAL

This package prepares a controlled Android QA release. Code engineering/merge
approval does not authorize hosting, spend, cutover, cloud build or APK/OTA
publication. Target configuration remains UNPROVISIONED. No stable URL, APK,
OTA result, provider deployment or physical-device acceptance is claimed.

## Manual release protocol

The sole distribution trigger is workflow_dispatch in qa-release.yml. It requires
an explicit exact source SHA matching the dispatch ref, and freezes a normalized
candidate in the immutable current-run qa-prepared-candidate artifact. Prepare
works without Expo/provider/publication secrets and emits NON_DISTRIBUTABLE. The
tracked candidate.json is a preparation template; null target/runtime/fingerprint
are real blockers. Git supplies native/JS source and the actual production storage
digest; a dispatch cannot assert clean source or a digest. For OTA the original
native identity comes from the independently reviewed previous native receipt.

After future authorized provisioning, the controlled release request must record
the actual attested target and actual SDK58 Android fingerprint/runtime in the
candidate template, matching the tracked mobile target config and versionCode.
These facts require a reviewed source change. A native build always requires a
new tracked app/versionCode relative to the previous observed receipt; silent
increment and reuse are refused. The orchestrator recomputes Expo config and the
real SDK fingerprint before publication; a caller's hash alone grants nothing.
This is intentionally not an automatic bootstrap from an unprovisioned target.

Before scheduling the fixed qa-release environment job, prepare reads the existing
GitHub environment and refuses absent/direct-human-reviewer protection. It never
creates or edits protection, secrets, reviewers or environments. The environment
review URL links the frozen candidate artifact. The **single protected candidate
deployment review**, with comment `APPROVE_QA <candidate_sha256> <proof_sha256>`,
reviews source, current canonical, target and exact private proof checksum together.
It is the applicable human release authorization, not a re-interpretation of GO
BUILD/MERGE or a fabricated PR review. Existing environment self-review policy is
respected; no stricter policy is silently created. Team-only reviewers are not yet
qualified and fail closed. Re-runs require a fresh dispatch/review.

The publishing entrypoint independently fetches actual workflow run/review history,
current environment/reviewers, cleared pending deployments and a real deployment
whose latest status log URL belongs to that run and whose SHA/environment match.
The candidate/proof hashes must still match. Current canonical must equal the
prepared snapshot, clean source must be its ancestor, and every effective branch
check plus the standing four-check floor must succeed on that exact SHA. CheckRun
app IDs and real Actions run URLs are checked; duplicate/unknown/missing runs fail.
If managed GITHUB_TOKEN cannot read branch protection (403), publication stops.
An operator-provisioned read-only QA_RELEASE_AUDIT_TOKEN with the required
Administration:read/Actions:read/Checks:read/Deployments:read and Contents:read
may be needed; no fake fallback policy exists and no credential is requested here.

Render is read through documented service/deploy GET APIs: dedicated repository,
branch, non-suspended single instance, private disk, auto-deploy off, actual live
deploy commit and URL must match the approved target. Real TLS GET health/version
must match the pinned source, environment, schema, bundle and current authority
state/generation/publication. Redirects/errors/unknowns stop release. WITHDRAWN
can be transport healthy; this grants no scientific readiness.

## Private proof artifact (not supplied by this preparation)

A future operator-controlled qa-continuity-proof artifact must be accessible in
this private repository by numeric proof_run_id. Both jobs download the same
artifact and hash its complete file set. It contains:

- backup.db with its exact backup.db.manifest.json, verified by the whole-DB
  verifier, plus a restored.db copy with identical schema/table/continuity digests;
- previous-native.json: the actual prior native receipt and artifact checksum;
  OTA also requires real EAS build ID/source/runtime/package/version readback;
- cutover.json: schema_version qa-cutover/1.0.0, assurance OPERATOR_ATTESTED,
  exact target, backup_reference, continuity_reference, files_sha256 entries for
  all three DB/manifest files, provider.service_id/deploy_id/branch, and version
  containing the complete **current** independently captured /__qa_version result;
- its old_writer_stopped, single_writer_opened and
  uid10001_volume_and_private_files_qualified fields describe actual operator
  observations from the approved cutover/qualification. Mere true values or
  arbitrary reference strings have no authority without the protected review of
  this exact artifact. Historical copies are never compared to today's mutable
  live journal after later writes; create a fresh release proof for current SCI;
- rollback additionally supplies known-good-update.json, the actual verified
  prior QA update receipt, with original native and JS source/group/update IDs.
  Runtime/branch/platform/Git/update ID are read back via the real SDK CLI.

No proof artifact is created, backup transferred or live writer stopped here.
Missing/corrupt proof fails before any publishing command. All copies are private
and synthetic; retention/off-service export is an operator responsibility. Never
upload secrets, passwords or production/personal data to this artifact.

## Fixed SDK actions after every gate

The CLI is pinned to EAS27.2.0, Node22.20.0 and existing ExpoSDK58. Account usage
is re-read: only the approved Free plan with remaining Android/total build quota
and no overage is admitted. Update/updater and bandwidth headroom are also checked;
no plan purchase/upgrade exists. Channel must be one unconditional qa→qa mapping;
unknown, partial or active rollouts are refused. No force-end rollout flag exists.

For build/update, only EXPO_PUBLIC_QA_NATIVE_SHA, EXPO_PUBLIC_QA_JS_SHA and
EXPO_PUBLIC_API_URL are synchronized to project-scoped preview variables. A
read-only GraphQL query using the installed CLI schema first rejects account-shared
or preview+other-environment bindings: CLI env:set would otherwise preserve those
links. Mutation responses must confirm exact public values and preview-only scope.
Thus cloud builders receive the same metadata rather than losing local process.env.
Existing QA02/pilot profiles remain unchanged. A partial env sync failure stops
without automatic retry; the operator reviews that state before a fresh dispatch.

Build uses the sole qa-continuous-android profile, Android, frozen credentials,
wait, JSON and non-interactive flags. Update uses Android/channelqa/environmentpreview.
Rollback republishes only the independently verified known-good QA group, Android,
destination-channelqa; embedded rollback is not implemented or claimed. No
production channel, generic shell command or arbitrary provider mutation exists.
Final policy/approval/source gates are re-acquired immediately before first writes.

A successful command returns SUBMITTED_NOT_DISTRIBUTABLE plus actual allowlisted
EAS response observations. It never invents BUILT/VERIFIED from success booleans.
Actual artifact checksum/signature/certificate/native build source/URL/runtime,
upgrade without uninstall, installed-client native/JS identity, download/launch,
persistence and rollback observations still gate later distributable receipts.

## Single external decision still pending

After code/CI/review readiness, approve only a new dedicated Render service and
region (Frankfurt proposed), Hobby base0USD +0.5c-512mb7USD/month +1GiB disk0.25USD:
**7.25USD/month before taxes/variables**. Bandwidth5GiB included then0.15USD/GiB,
extra pipeline minutes can cost more. A pipeline-minutes limit is not a global
invoice cap. Qualify actual memory/latency, disk UID10001 and managed secret modes;
no root/chown bypass or paid auto-upgrade. Authorize controlled QA02 freeze/drain,
complete private backup/restore/identity verification, one writer and explicit
activation/restart only after those gates. No personal device or production system.

Then approve one included Android build against the freshly re-read Free account
quota (snapshot2026-11-10T12:23:46Z:5/15Android used,10remaining; not a promise),
followed by controlled QA emulator update/rollback. Hosting/credentials/config and
all external writes remain pending. Physical acceptance remains UNAVAILABLE.

Primary contracts: [portable server](../../../deploy/qa/README.md),
[GitHub run approvals](https://docs.github.com/en/rest/actions/workflow-runs#get-the-review-history-for-a-workflow-run),
[GitHub environments](https://docs.github.com/en/rest/deployments/environments#get-an-environment),
[Render service](https://api-docs.render.com/reference/retrieve-service),
[Render deploy](https://api-docs.render.com/reference/retrieve-deploy),
[Render Docker secrets](https://render.com/docs/docker),
[Render blueprint](https://render.com/docs/blueprint-spec),
[EAS environments](https://docs.expo.dev/eas/environment-variables/).
