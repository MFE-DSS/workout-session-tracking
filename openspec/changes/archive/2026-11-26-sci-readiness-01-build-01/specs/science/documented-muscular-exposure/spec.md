## ADDED Requirements

### Requirement: Separate admission and build authority
The reader SHALL remain non-served until explicit SCI admission, distinct GO BUILD and applicable qualification gates. Preparation MUST NOT be interpreted as implementation authorization.

#### Scenario: Conditional operator wording supplied
- **WHEN** a mandate offers a formula to transmit if admission is confirmed
- **THEN** no operator act or build authorization is inferred

### Requirement: Honest bounded temporal coverage
The reader SHALL separate requested window, inspected subset and attested coverage. UNKNOWN MUST NOT become zero, absence, exhaustive total or global latest.

#### Scenario: Old candidate prefix misses recent facts
- **WHEN** an ID-ordered scan truncates before recent rows in the requested window
- **THEN** the response is partial or unknown with limits and no false empty or latest claim

### Requirement: Effective authority and coherent source capture
Facts SHALL use owned current state, exact applicable roles, revisions and time provenance in a coherent capture. The projection MUST NOT repair writers or use current catalogue fallback for unproven V3 authority.

#### Scenario: Captured V3 catalogue unavailable
- **WHEN** effective bundle version and digests cannot be established
- **THEN** affected associations remain UNKNOWN without E1 position or fuzzy identity fallback

### Requirement: Resource bounds and isolation
The proposed runtime SHALL enforce bounded reads, input structure, memory, duration and output before service. Unsupported controls MUST fail closed.

#### Scenario: Worker cannot enforce qualified limits
- **WHEN** profile or OS capability is missing or resources cannot yield a safe result
- **THEN** the route remains unavailable and no unlimited fallback runs

### Requirement: Descriptive consumption only
Only the explicitly admitted reader SHALL consume the SCI projection. Allocation, recovery, historical timestamps and LOCKED/native surfaces MUST remain unchanged.

#### Scenario: Served SCI importer outside permitted consumer
- **WHEN** another product module imports the SCI layer
- **THEN** the preserved architectural guard rejects the consumption
