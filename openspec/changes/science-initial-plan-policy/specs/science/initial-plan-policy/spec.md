## ADDED Requirements

### Requirement: Traceable initial policy

The producer MUST use reviewed, versioned dose, effort, selection, attribution and time policies from trusted references. It MUST NOT promote historical constants, template names or an APPROVED string into scientific authority. A selected priority MUST remain a preference.

#### Scenario: Sufficient Blueprint without admitted policy
- **WHEN** required inputs are present but a policy reference is absent or unapproved
- **THEN** the result is POLICY_UNAVAILABLE and no READY plan is fabricated.

### Requirement: Progressive inputs and honest applicability

The producer MUST separate contract-required inputs from optional anthropometry and personalisation. It MUST preserve UNKNOWN and WITHHELD, use the canonical input assessment and state its supported population/cadence explicitly.

#### Scenario: Missing weight and experience
- **WHEN** anthropometry and experience are unknown but required inputs are complete
- **THEN** it does not fabricate their values or require them to hide a missing policy; calibration and limitations remain explicit.

### Requirement: Canonical candidates and contextual compatibility

The producer MUST use reviewed canonical identities, explicit intent definitions and role/movement compatibility. It MUST NOT require equipment inventory or assume a full gym. Substitution MUST recheck the plan constraints.

#### Scenario: Unknown gym with exercise confirmations
- **WHEN** no inventory is declared but an exercise is confirmed available in the current context
- **THEN** it may use that sourced confirmation without inferring other equipment.

#### Scenario: Unconfirmed selected exercise
- **WHEN** a selected exercise has unknown compatibility
- **THEN** the plan remains REVIEW_REQUIRED rather than READY.

### Requirement: Supported duration and reproducible readiness

The producer MUST use the existing SCI-P02 v1 schemas and validator, explicit input fingerprint and frozen policy/catalogue versions. It MUST NOT invent numerical constants or elapsed-time bounds to produce READY. Individual response MUST remain NOT_ESTIMATED.

#### Scenario: Missing time basis
- **WHEN** the available sources do not support a duration upper bound
- **THEN** the response expresses TIME_UNCERTAIN and cannot be READY.

#### Scenario: First genuine ready fixture
- **WHEN** the actual producer passes admission tests with sufficient inputs, approved policies, complete exposure, feasible candidates and supported time within budget
- **THEN** a contract-valid READY fixture is generated from that producer with version, evidence and reproducibility metadata, without production activation.

### Requirement: Isolated delivery boundary

This change MUST preserve existing mobile layouts, visual contracts, shared backend models and served recommendation behavior. Implementation MUST follow operator review of this proposal. Proposal artifacts MUST NOT be represented as an implemented or served producer.

#### Scenario: Proposal awaiting build approval
- **WHEN** no separate GO BUILD is recorded
- **THEN** only the proposal, audit, design and test specification are delivered, with no runtime READY claim.
