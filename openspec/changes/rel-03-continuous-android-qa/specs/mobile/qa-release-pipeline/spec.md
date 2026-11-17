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

#### Scenario: The operator explicitly works alone
- **WHEN** the operator designates MFE-DSS as the sole human QA reviewer and configures self-review as permitted
- **THEN** image preparation still requires one actual direct-human environment approval for the exact run and source SHA
- **AND** image self-review is permitted only for the designated sole direct reviewer MFE-DSS (User/id156458952), never for another reviewer or an expanded User/Team list
- **AND** the image guard honors the explicit boolean self-review policy, refuses an absent or malformed policy, and forbids self-review when that policy is true
- **AND** an agent does not approve on the human's behalf, and no merge authorization substitutes for the run-bound approval

### Requirement: Installed update and rollback evidence
OTA support SHALL be claimed only after a real installed client downloads and runs a compatible controlled QA update and a known-good rollback without losing owned SQLite facts. HTTP, emulator and physical results SHALL remain distinct.

#### Scenario: Only the historical QA02 APK exists
- **WHEN** Expo Updates is disabled or the QA channel/runtime is absent in that binary
- **THEN** it is not advertised as OTA-capable
- **AND** a new native build and installed proof remain required

### Requirement: Independent provider and image observation
The OVH QA path SHALL bind a backend image receipt independently acquired from an allowlisted GitHub workflow/run/source to an authenticated fresh fixed-command host observation of the actual running image. Candidate documents, application version responses and OCI source labels MUST NOT alone establish image provenance. Existing Render verification SHALL remain strict.

#### Scenario: Image or host observation cannot be independently acquired
- **WHEN** the workflow/artifact/source/image binding, pinned host identity, nonce or bounded observation freshness cannot be verified
- **THEN** publication is refused before an external build or update command
- **AND** preparation remains non-distributable without weakening the existing database-proof limits

### Requirement: Explicit synthetic feature configuration
The QA supervisor SHALL supply only explicitly admitted synthetic feature settings through private references and separate backend/facade environments. Advertised BODY, Nutrition, Library and Builder contracts SHALL require their applicable configuration and retain independent data-consent and runtime authority gates.

#### Scenario: Extended feature configuration is missing or contaminated
- **WHEN** a candidate promises a feature without its private configuration, or ambient production/sensitive values contaminate either child environment
- **THEN** extended service activation is refused without inheriting secrets or granting consent
- **AND** legacy PLAN-only configuration and minimal post-withdrawal erasure semantics are preserved

### Requirement: Explicit private custody and fresh initialization
Image custody SHALL preserve the independently built archive through authenticated encryption, durable single-upload intent and downloaded-byte verification in the configured private store. Fresh QA initialization SHALL run only on explicitly approved new state, using canonical migrations and reference seeds without granting consent or fabricating performed facts.

#### Scenario: Upload response or initialization outcome is uncertain
- **WHEN** an upload response is lost or initialization leaves partial state
- **THEN** automatic mutation replay is refused and the original intent/state is preserved for inspection
- **AND** a failed image job is not accepted solely from reconciled metadata

### Requirement: Shared host isolation is observed
The OVH observer SHALL acquire the actual dedicated internal network, sole container attachment and bounded host filter. Startup SHALL install isolation before the QA service, and routing SHALL preserve existing host listener groups while binding QA TLS to the qualified public IP.

#### Scenario: Network, filter or loaded routing changes
- **WHEN** an extra attachment, unapproved network option, reordered filter hook or changed nginx generation is observed
- **THEN** qualification is refused until actual administrator requalification
- **AND** no global firewall policy, foreign service or historical database is automatically replaced
