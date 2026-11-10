## ADDED Requirements

### Requirement: Stable isolated QA service
The QA delivery runtime SHALL use an attested persistent HTTPS environment with bounded mobile-only exposure, assigned synthetic accounts and explicit deployment authorization. A temporary tunnel SHALL NOT satisfy stable target readiness.

#### Scenario: Provider or target is not approved
- **WHEN** hosting access, cost approval or a real target receipt is missing
- **THEN** independent preparation continues without provisioning or publishing
- **AND** readiness remains PREPARED or externally blocked rather than operational

### Requirement: Owned state survives QA relocation
A QA upgrade SHALL preserve account, device, subject and journal identities. A complete consistent QA backup SHALL be verified on an isolated replacement before cutover; colliding numeric IDs in an unrelated database SHALL NOT establish ownership.

#### Scenario: Replacement is incomplete or unrelated
- **WHEN** auth, subject, canonical facts, typed sidecars or source revisions do not match the controlled transfer
- **THEN** cutover and client distribution are refused without deleting, reassigning or reseeding historical state

### Requirement: Native and update releases have explicit identities
Every QA build and update SHALL produce a source-attested receipt linking native version, versionCode, signature, artifact checksum, runtime, update channel, JS revision and current compatible backend/science/schema references. Unknown or future values SHALL remain unverified.

#### Scenario: A compatible JS update is installed
- **WHEN** the installed client runs a published QA update
- **THEN** its current JS source/update ID are distinguished from native build identity
- **AND** a native configuration or dependency change requires a new APK rather than an OTA bypass

### Requirement: Publication requires separate approval
A merge SHALL NOT itself publish a backend, APK or OTA. The QA workflow SHALL verify the exact merged HEAD, mandatory CI, applicable visual acceptance, target/runtime compatibility and an actual controlled release gate before publication.

#### Scenario: A publish gate or native runtime is missing
- **WHEN** the environment is unprotected, approval is absent or the runtime is incompatible
- **THEN** publication fails closed while a nonpublishing preparation job remains usable

### Requirement: Installed update and rollback evidence
OTA support SHALL be claimed only after a real installed client downloads and runs a compatible controlled QA update and a known-good rollback without losing owned SQLite facts. HTTP, emulator and physical results SHALL remain distinct.

#### Scenario: Only the historical QA02 APK exists
- **WHEN** Expo Updates is disabled or the QA channel/runtime is absent in that binary
- **THEN** it is not advertised as OTA-capable
- **AND** a new native build and installed proof remain required
