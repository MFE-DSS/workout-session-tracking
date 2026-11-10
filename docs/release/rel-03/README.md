# REL03 — PREPARED / BLOCKED_EXTERNAL

This package prepares a controlled Android QA release. Code engineering/merge
approval does not authorize hosting, spend, cutover, cloud build or APK/OTA
publication. Target configuration remains UNPROVISIONED. No stable URL, APK,
OTA result, provider deployment or physical-device acceptance is claimed.

The product repository is **PUBLIC**. Proof transport is implemented as an
AES-256-GCM encrypted, flat ZIP plus a release asset in a separately configured
**PRIVATE** GitHub repository. `proof-store.json` remains **UNPROVISIONED**: no
private repository, key, token or upload is assumed or created by this change.
Only the public candidate/checksum metadata and submission receipt use product
Actions artifacts. Plain DB files and keys must never enter those artifacts.

## Manual release protocol

The sole distribution trigger is workflow_dispatch in qa-release.yml. It requires
an explicit exact source SHA matching the dispatch ref, and freezes a normalized
candidate in the immutable current-run qa-prepared-candidate artifact. Prepare
works without Expo/provider/publication secrets and emits NON_DISTRIBUTABLE. The
tracked candidate.json is a preparation template; null target/runtime/fingerprint
are real blockers. Git supplies native/JS source and the actual production storage
digest; a dispatch cannot assert clean source or a digest. For OTA the original
native identity comes from the independently reviewed previous native receipt.
The tracked candidate must contain that actual native identity for credential-free
workflow preparation; the decrypted previous receipt is checked again at publish.
Local preparation can derive it with --proof, but Actions prepare never reads DBs.

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

## Private encrypted proof transport (not provisioned by this preparation)

The allowlisted private staging directory contains:

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

The optional restored.db.manifest.json generated by the existing backup helper
is also accepted. No other filename, directory, symlink, nested path or compressed
ZIP entry is accepted. Per-file size is capped at128MiB and total plaintext at
256MiB; ciphertext has a bounded envelope allowance. Only the complete explicitly
named DB/proof set is packed. Authentication secrets, access configuration and
unrelated raw files are refused. Whole DB copies necessarily contain synthetic
auth rows; those bytes stay encrypted during transport, never in public artifacts.

No real backup is transferred or live writer stopped here. Missing/corrupt proof
fails before SDK installation or publishing. Daily retention/export remains an
operator responsibility. Encryption is a transport control, not a compliance
claim or scientific permission. Key management/recovery remains operator-owned.

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
4. Stage the complete allowlisted proof set in a private directory. After the
   separately approved creation/connection of the private proof repository, set
   proof-store.json to schema_version qa-proof-store/1.0.0, state CONFIGURED and
   its exact OWNER/REPO. A reviewed source change must carry this configuration;
   arbitrary repositories, product repo and URLs are refused. The tools read the
   actual repo API and require private=true and exact full_name before remote use.
   Use a random32-byte binary key outside source, mode0600, in an owner-private
   mode0700 directory. Key generation/escrow/rotation and protected-secret setup
   belong to the external decision, and are not executed by this preparation.

   Future operator-invoked commands (private paths must already be mode0700):

   ```sh
   python -m tools.qa_delivery.proofs pack --source /private/qa-proof --key /private/qa-keys/aes256.key --output /private/qa-staging/proof.aqp --receipt /private/qa-staging/staging.json
   python -m tools.qa_delivery.proofs upload --repository APPROVED_OWNER/APPROVED_PRIVATE_REPO --blob /private/qa-staging/proof.aqp --receipt /private/qa-staging/staging.json --output /private/qa-staging/upload.json
   ```

   Pack performs no network operation. Upload requires a separately authorized
   operator token with Contents:write on the dedicated private repository. It uses
   supported gh release create/upload, one unique prerelease tag at the actual
   private default-branch HEAD, no overwrite/clobber or automatic retry. API asset
   ID, name/state/size, available server digest and downloaded ciphertext checksum
   are checked. The upload receipt contains the immutable asset ID and actual
   cipher/proof hashes. A failure can leave a private release/asset; inspect it
   before another explicit invocation. No cleanup/delete command runs remotely.
5. Dispatch BUILD_APK, UPDATE or ROLLBACK at the same approved source with
   expected_proof_sha256, proof_asset_id and proof_cipher_sha256 copied from the
   local staging/readback receipts. Credential-free prepare freezes those fields
   as **DECLARED_NOT_VERIFIED / NON_DISTRIBUTABLE**, regenerates the candidate,
   and exposes both digests for one protected review. The operator compares the
   expected proof hash with the local staging receipt, then approves precisely
   `APPROVE_QA <candidate_sha256> <proof_sha256>`. No hash or boolean alone grants
   release authority. A changed candidate/source requires fresh preparation and
   capture; the capture record does not embed its own proof hash.
6. Only after that actual qa-release review does the release job obtain separate
   protected secrets QA_PROOF_READ_TOKEN (Contents:read on the private proof repo)
   and QA_PROOF_AES256_KEY_HEX (64 lowercase hex characters encoding the32-byte
   key). These are distinct from each other and from publication credentials.
   It reads actual private-repo and asset metadata, downloads by immutable asset
   ID, verifies cipher checksum, authenticates/decrypts into mode0700 RUNNER_TEMP
   staging with mode0600 files, and recomputes exact proof_digest equality to the
   approved expected hash. Wrong key/header/size/nonce/tag/cipher, archive abuse or
   mismatch creates no accepted output. Node receives the key only via binary
   stdin; it receives no credential environment and prints no secrets. The key
   file is deleted immediately after successful import; always-cleanup removes
   the private proof directory at job end. Private plaintext is never uploaded.
7. The actual pipeline publisher consumes that decrypted directory, verifies the
   real SQLite copies/manifests and all existing GitHub/Render/backup/EAS gates,
   and only then permits the existing QA-only SDK writes. Import success alone
   grants no release/scientific authority. No SDK is installed before import.

For controlled local import after authorization, the same real importer CLI is:

```sh
python -m tools.qa_delivery.proofs import --package /private/qa-staging/qa-prepared.json --key /private/qa-keys/aes256.key --output /private/qa-staging/imported-proof
```

The public candidate artifact includes expected digests/asset ID only. The private
operator staging receipt is the pre-approval anchor; the workflow cannot inspect
private proof bytes before approval, and labels that limit explicitly. There is
no public Actions proof artifact producer/download path or invented gh run upload.

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

After code/CI/review readiness, the **single external decision package** must
include a new dedicated private GitHub proof repository, its access/retention and
storage limits/cost, operator-only upload token, separate read-only workflow token,
and AES key custody/escrow/rotation plus protected qa-release secrets. None is
provisioned here. The initial setting remains UNPROVISIONED and blocks transport.
The same decision must approve a new dedicated Render service and
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

Primary contracts: [release assets](https://docs.github.com/en/rest/releases/assets),
[private releases](https://docs.github.com/en/rest/releases/releases),
[portable server](../../../deploy/qa/README.md),
[GitHub run approvals](https://docs.github.com/en/rest/actions/workflow-runs#get-the-review-history-for-a-workflow-run),
[GitHub environments](https://docs.github.com/en/rest/deployments/environments#get-an-environment),
[Render service](https://api-docs.render.com/reference/retrieve-service),
[Render deploy](https://api-docs.render.com/reference/retrieve-deploy),
[Render Docker secrets](https://render.com/docs/docker),
[Render blueprint](https://render.com/docs/blueprint-spec),
[EAS environments](https://docs.expo.dev/eas/environment-variables/).
