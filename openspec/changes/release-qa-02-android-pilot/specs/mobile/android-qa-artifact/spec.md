## ADDED Requirements

### Requirement: Attested isolated Android QA artifact
The runtime SHALL provide an internal APK containing its actual native dependency graph, SHALL preserve the notifications consumer, and SHALL use an explicit isolated synthetic QA target rather than the public pilot profile.

#### Scenario: Native module and source are attested
- **WHEN** the QA APK is built
- **THEN** its build receipt records exact source/lock/config/native graph, EAS ID/artifact, package/version/signing fingerprint and QA backend identity
- **AND** successful compilation alone does not assert successful device launch

#### Scenario: Invalid target fails before build
- **WHEN** QA configuration names the public pilot backend or an unattested target, gallery, or missing revision
- **THEN** configuration fails without silently selecting pilot, production or a fixture

### Requirement: Evidence levels remain distinct
The acceptance record SHALL distinguish PASS, FAIL and UNAVAILABLE per flow, and HTTP, emulator and physical-device evidence SHALL remain separate.

#### Scenario: Physical Android absent
- **WHEN** no authorized physical Android is connected
- **THEN** physical installation and pilot acceptance remain UNAVAILABLE even if an emulator launches
- **AND** independent artifact and backend preparation continues

### Requirement: Assigned synthetic remote access
The temporary QA gateway SHALL admit only assigned synthetic registration/login identities, SHALL reject nonempty registration emails before upstream persistence, and SHALL bound request and upstream durations without rewriting command facts.

#### Scenario: An unassigned account or email is submitted
- **WHEN** a visitor submits an unassigned identity or nonempty email to registration
- **THEN** the request is rejected before the canonical account writer
- **AND** no production/shared backend or secret embedded in the APK is used

#### Scenario: The upstream is unavailable or redirects elsewhere
- **WHEN** the upstream fails, exceeds the total deadline or redirects to another target
- **THEN** the gateway reports a transport failure without forwarding the client to another host or inventing a scientific decision
