## ADDED Requirements

### Requirement: Isolated read-only worker avoids persistent ORM bootstrap state
The worker SHALL install its admitted limits before application imports and SHALL isolate incidental ORM initialization from persistent/default database paths. The actual owned read capture SHALL keep its separate server-supplied SQLite URI, read-only transaction, owner filters and existing budgets.

#### Scenario: Read-only canonical source without a generated state directory
- **WHEN** the bounded Linux worker runs on a read-only checkout with no default var directory
- **THEN** incidental ORM imports do not attempt to create persistent state there
- **AND** the actual SQLite capture remains read-only and owner-bound

#### Scenario: Qualification target differs from deployment
- **WHEN** a tested runtime/image/source/mount profile differs from a future deployment profile
- **THEN** evidence identifies the exact tested candidate and retains operational HOLD until the deployment profile is separately qualified
- **AND** no QA activation or automatic budget relaxation follows
