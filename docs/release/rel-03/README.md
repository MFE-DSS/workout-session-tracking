# REL03 — PREPARED / BLOCKED_EXTERNAL

This package prepares a controlled Android QA release. Code engineering/merge
approval does not authorize hosting, spend, cutover, cloud build or APK/OTA
publication. Target configuration remains UNPROVISIONED. No stable URL, APK,
OTA result, provider deployment or physical-device acceptance is claimed.

**CODE/PREPARATION GAP:** the repository currently has no producer/importer for
qa-continuity-proof Actions artifacts. The workflow consumes such an artifact but
cannot create the first one. Root must resolve and review this code gap before
claiming independent code readiness; hosting permission alone does not fix it.

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
and synthetic. Daily retention/export remains an operator responsibility; the
distinct pre-release backup/export below is an enforced publication gate. Never
upload secrets, passwords or production/personal data to this artifact.

## Required capture/export for each release

Historical cutover proof is insufficient after new journal/auth facts accumulate.
The same reviewed proof artifact must additionally contain release-backup.json,
release-backup.db and its .manifest.json, plus release-export.db and its
.manifest.json: the exact off-service export read back for verification. Both
whole DB copies are checked against their complete manifests and byte hashes,
and the export must equal this release's snapshot. Neither is compared to the
old cutover DB or today's mutable live DB.

The new record has schema_version qa-release-backup/1.0.0 and assurance
OPERATOR_ATTESTED, and contains these required bindings:

- release_id, candidate_sha256, source and target exactly match this candidate;
- preparation_run_id identifies a successful, completed first-attempt
  qa-release.yml workflow_dispatch at this exact source SHA;
- capture.started_at and capture.completed_at are observed timezone-aware times;
- off_service_export.completed and off_service are actual operator-attested true
  facts, with its private reference, completed_at and observed_at (readback check);
- files_sha256 pins all four exact DB/manifest files named above.

The gate independently reads GitHub preparation/current run times and all prior
qa-release deployments. Preparation creation must follow every prior QA deployment
creation, excluding the actual current deployment. Then the completed preparation run’s last update
(updated_at) ≤ capture start ≤ capture completion ≤ export completion ≤ export
observation ≤ current release dispatch creation. This sequence requires a new
preparation/capture/export after every prior release; no arbitrary TTL or daily
backup success is inferred. Missing/false/reversed/stale/differently bound facts
stop before env:set. Physical location and observation of off-service export are
explicitly OPERATOR_ATTESTED under the exact protected proof-hash review, while
SQLite/manifests/checksums and GitHub timestamps are mechanically verified.

Future authorized sequence (nothing here executes it):

1. At the exact approved source, dispatch operation PREPARE without a proof. Wait
   for its successful completion and retain its real run ID/times. This automated
   read-only job is required once per release, after the prior QA release; it adds
   one preparation job and GitHub reads, no build/deployment/spend. PREPARE currently
   builds a BUILD_APK candidate; this run anchors only source/time for all actions.
2. On a clean checkout of that same SHA, obtain the exact intended candidate hash
   before capture, using the already qualified historical/native proof directory:

   ```sh
   python -m tools.qa_delivery.pipeline prepare --candidate docs/release/rel-03/candidate.json --operation BUILD_APK --proof /private/qa-proof --output /private/build-candidate.json
   python -m tools.qa_delivery.pipeline prepare --candidate docs/release/rel-03/candidate.json --operation UPDATE --proof /private/qa-proof --output /private/update-candidate.json
   python -m tools.qa_delivery.pipeline prepare --candidate docs/release/rel-03/candidate.json --operation ROLLBACK --proof /private/qa-proof --output /private/rollback-candidate.json
   ```

   Run only the intended action. The output candidate_sha256 is independent of
   the proof hash. UPDATE/ROLLBACK reuse the real previous native receipt; their
   candidate/action need not equal the preliminary BUILD_APK preparation artifact.
3. Under the separate approved external operation, capture the entire current QA
   DB using `python -m tools.qa_delivery.database backup <private-current-db>
   <private-new-release-backup.db>`, recording actual start/completion. Export that
   DB plus manifest to the approved private off-service location, read it back as
   release-export.db plus its renamed manifest and record actual completion/check
   observations. Record observed facts/hashes in release-backup.json, bound to the
   intended action's candidate from step2 and real preparation run from step1.
4. Include these files with historical cutover/native proof in the private
   operator-controlled qa-continuity-proof artifact. **This step is currently a
   CODE/PREPARATION GAP:** no supported producer/importer exists in this repository.
   GitHub has no `gh run upload` command or manual Actions-artifact UI upload.
   The sequence cannot currently be completed end-to-end by this package. Root
   must review a supported private ingestion path (including any host/key/mode/source
   bindings) before code readiness; this fix does not invent a transport, public
   export route, new workflow or secret architecture. No upload is executed here.
5. Dispatch BUILD_APK, UPDATE or ROLLBACK at that same source with this proof_run_id.
   Current prepare independently regenerates the exact action candidate and hashes
   the entire proof, then the single protected deployment review acknowledges both
   hashes. A changed candidate/source requires re-preparation/capture; no circular
   proof hash is embedded in the capture record, and no extra human approval is
   imposed by the preliminary automated preparation.

## Fixed SDK actions after every gate

The CLI is pinned to EAS27.2.0, Node22.20.0 and existing ExpoSDK58. Account usage
is re-read: only the approved Free plan with remaining Android/total build quota
and no overage is admitted. Update/updater and bandwidth headroom are also checked;
no plan purchase/upgrade exists. Channel must be one unconditional qa→qa mapping;
unknown, partial or active rollouts for the exact candidate/installed runtime are
refused. A latest global group for another runtime does not block the first OTA
on a newly installed native runtime; an independent runtime-filtered query is
mandatory. No force-end rollout flag exists.

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
