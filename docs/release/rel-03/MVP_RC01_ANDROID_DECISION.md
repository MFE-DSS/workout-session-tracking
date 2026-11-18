# MVP-RC-01 — Android candidate decision package

18 November 2026. **GO CANDIDATE REQUIRED; no new APK or OTA published.**
Public synthetic QA is [qualified](OPS03_PUBLIC_QUALIFICATION_20261118.md).
This scoped source change promotes that actual target into the existing Android
profile. After guarded merge, PREPARE will freeze the exact clean canonical SHA;
the final approval request must link that immutable candidate and private-proof
checksum. Approval of this document's engineering merge grants no release.

## Candidate identity and permitted operation

- Features already merged: PLAN/calibration, owned execution/journal, Today,
  Progress, BODY-01, manual NUT-01, MOB-06 and MOB-07. No UI geometry changes.
- One Android internal APK using `qa-continuous-android`, EAS project
  `c7243bfc-29b3-4486-aafe-e69b9c904bbe`, preview environment, channel`qa`→branch`qa`.
  Actual channel readback: unpaused, branch mapping qa, no update groups.
  No production channel/Store or OTA operation is requested by this build decision.
- `dev.auren.releaseqa02`, AUREN QA, **0.0.2 / versionCode3**; scheme
  `auren-releaseqa02`; fingerprint runtime policy. Actual SDK Android fingerprint
  **`8c3af5dabc725e61d226a83fea20d90d94fdae6d`**, runtimeVersion equal to that hash;
  publisher recomputes on exact source before build. SDK58.0.17/RN0.88.0/
  expo-updates58.0.21, lock preserved. `ExpoTopicSubscriptionModule` retained.
- Exact HTTPS target`https://qa.spignos.com`, environment`qa-rel03-rc01-20261117`.
  Backend source`b8fc63ffadba35028af9e1c92c2e48892f9fe403`, exact image/config/API/
  SCI generation1 and published pins in the linked operational receipt.
  Server`program_builder_operations_01`; local`first-session-local/3.0.0` plus
  actual storage-source digest computed by PREPARE. No schema/SCI changes here.
- Current EAS default signing credentials were read without requesting the key:
  certificate SHA256
  `12b13109a2a41e2e2c0e97578364793e659a7548da4ce210d0dbd2f912f4bc75`,
  matching QA02. Same QA package + higher code + same certificate make this an
  **intended in-place QA upgrade**, not a separate install or a proven upgrade.
  Actual compiled signature/upgrade and on-disk SQLite require installed testing.
  This package remains distinct from a future production identifier.

## Resources, permissions and limitations

Actual EAS27.2.0 read-only usage: Free plan,5/15Android builds used and5/30total,
zero overage required by the publishing guard. The proposed build consumes one
included build; quota/plan are checked again before submission. No paid-plan
upgrade, new host, optional add-on or unlimited spend is requested.

Expo introspection (not compiled APK proof) reports INTERNET, VIBRATE,
SYSTEM_ALERT_WINDOW and legacy READ/WRITE_EXTERNAL_STORAGE capped at API32.
Remote notifications plugin remains disabled. `allowBackup=true` with SecureStore
backup/data-extraction rules is inherited; it does not prove all SQLite copies
are excluded. Binary merged-manifest inspection must record the final permissions,
backup rules, non-debuggable status and default cleartext prohibition. No permission
is silently removed merely to improve this report. No photo/scan/media provider,
new native module or framework upgrade is introduced.

Fresh npm audit on the unchanged lock reports **71 affected package entries:
64 high /7 moderate /0 critical** (including propagated tool dependencies), not
71 independent vulnerabilities. Root advisories involve node-forge, picomatch,
zod, glob and minimatch. node-forge is pulled by Expo CLI/code-signing tools;
zod by Expo CLI. This is not a global innocuity claim or permission to apply
npm's proposed framework downgrades. The actual premerge Android production export passed: its Hermes source-map has
1,569 sources and contains none of node-forge/picomatch/zod/glob/minimatch. This
narrows packaged-JavaScript reachability only; CLI/code-signing-tool exposure and
native binary inspection remain separate. No global innocuity claim follows.

Sonar remains advisory and its genuine results must be attached to the final source
receipt. Dependency/security findings remain reportable; synthetic QA is not a
global security, privacy, scientific-safety or Store compliance certification.

**Permitted DATA scope: synthetic test facts and assigned synthetic accounts only.**
The API origin rejects arbitrary real-email signup; BODY/NUT have distinct consent
contracts. A real person's weights, nutrition, photos or sensitive facts remain
outside this decision without applicable controller policy. Synthetic test values
are not exercise instructions. Muscle-group availability is NOT_SERVED.

## Execution and rollback

Run credential-free PREPARE on the clean exact canonical SHA, capture/export the
new candidate-bound recovery snapshot after that run, stage the complete encrypted
proof, then dispatch `qa-release` BUILD_APK with its immutable references. Dispatch
only creates the reviewable pending operation: the release job waits at the existing
protected environment before EAS can run. The single distinct candidate GO is the
human review there. Reviewer MFE-DSS uses the exact
`APPROVE_QA <candidate hash> <proof hash>` comment; automation never approves itself
or edits protections/secrets. If the candidate/proof/source changes, reacquire and
review the new exact package. No EAS build runs before this approval.
Historical continuity proof and a new post-PREPARE off-service export are distinct.
Candidate-bound restricted observation is reacquired at publish; the operational
receipt alone never authorizes distribution.

Install first QA02 then upgrade when its preserved APK is available; check signature
and persistence before declaring upgrade PASS. Actual ConnectedApp smoke covers
login/token restore, Builder→Library→Today same session, logging/recovery/history,
Progress/BODY/NUT, offline→force-kill→SQLite recovery, A/B and Back/IME/safe areas/
large text. Emulator and physical results are separate; absent physical evidence
stays UNAVAILABLE. EAS ID, exact embedded source, artifact SHA256 and certificate
must come from the actual resulting APK/build, never prefilled as success.

Contingency: halt distribution and QA update publication, retain embedded bundle
and receipts; preserve SQLite before any install/downgrade. Do not assume old QA02
can serve as a functional fallback: its tunnel is temporary and it does not support
this runtime/channel by assumption. Stop only QA server if required; preserve data
and personal services. A compatible known-good new APK or verified QA update is
needed for a functional client rollback. No OTA/rollback is claimed tested yet.
