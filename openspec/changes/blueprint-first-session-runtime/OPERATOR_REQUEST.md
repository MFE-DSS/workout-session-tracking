# AUREN — PLAN V3 FIRST REAL SESSION DELIVERY

## Mission

Continue the AUREN critical path from the latest verified canonical HEAD.

SCI stage2 V3 is merged and closed.

The next product objective is:

**An eligible authenticated user receives a scientifically admitted V3 plan, explicitly acknowledges uncertain time feasibility, creates one real owned session, and executes it through the native application.**

Use the existing preparation in:

`openspec/changes/blueprint-first-session-runtime/`

Do not produce another broad architectural audit.

## 1. Authorization and execution boundary

The existing PLAN preparation is docs-only and has no GO BUILD recorded.

Finalize and submit the exact OpenSpec implementation scope for approval, incorporating the decisions below.

Do not treat this prompt as authorization for unapproved schema migrations, runtime activation, visual baselines or deployment.

After the PLAN scope receives its required GO BUILD, execute autonomously:

implementation → targeted tests → integration tests → review → CI → fixes → PR → standing-GO merge → closeout.

Do not request routine merge approvals within an authorized scope.

## 2. Approved architectural direction

Use:

- server-owned Blueprint snapshot;
- canonical V3 scientific loader, producer and admitted validator;
- explicit version negotiation;
- durable evaluation;
- exact time acknowledgment;
- idempotent first-session creation;
- canonical WorkoutSession/SessionExercise/SetLog;
- typed execution binding;
- existing AUREN native session/navigation system.

Do not use mobile-generated science or legacy template instantiation as substitutes.

Preserve V1/V2 and historical replays.

## 3. Minimal persistent data model

Before schema implementation, examine every proposed new table.

For each table prove:

- which invariant requires persistence;
- why an existing canonical structure cannot support it;
- ownership and lifecycle;
- transaction boundaries;
- relation to deletion/retention policy;
- index and uniqueness constraints;
- rollback behavior.

Prefer the smallest additive schema that preserves the required invariants.

Do not remove idempotency, provenance or immutable scientific binding merely to reduce the table count.

## 4. First-plan runtime

Implement in dependency order:

A. Authenticated Blueprint acquisition and immutable source revision.

B. Server-owned snapshot with required data, missing fields, source provenance and consent applicability.

C. Explicit V3 contract negotiation, preserving pinned historical V1 files.

D. Actual published SCI loader + producer + admitted validator.

E. Persisted evaluation and revalidation when facts, context or authority change.

F. Exact time acknowledgment when `REQUIRES_TIME_ACK`.

G. Idempotent first-session command with durable recovery.

H. Atomic creation of a single owned WorkoutSession and its scientifically bound exercise/set records.

I. Native handoff into the actual session.

J. Start, pause, resume, set logging, finish and historical readback using the V3 execution profile.

No synthetic READY fixture in production.

No fabricated first-load kilograms, duration, fallback warmup, overload or exercise replacement.

## 5. Critical invariants

Prove with executable tests:

- two concurrent start requests produce at most one first session;
- lost HTTP response can be recovered without creating a second session;
- repeated request ID with altered body is rejected;
- cancellation before creation prevents delayed creation;
- another account cannot read or mutate the session;
- stale Blueprint invalidates new admission;
- withdrawn scientific authority prevents new work instructions;
- historical sessions remain readable;
- app restart retains journal integrity;
- typed machine/assistance/implement settings are never silently converted to total external kg;
- unknown metrics are omitted instead of becoming zero;
- historical success scoring and implicit adaptation do not execute on unqualified V3 sessions;
- incomplete or invalid scientific references fail closed.

Tests must exercise actual backend consumers and native integration, not only pure helpers.

## 6. Visual delivery

Preserve LOCKED MISSION and session composition.

New visual surfaces requiring design:

- acquisition of essential Blueprint facts;
- first-plan presentation;
- exact uncertainty acknowledgment;
- setting/observation capture where applicable;
- failure, incomplete, revoked and unknown states.

Reuse existing AUREN mark, tokens, primitives and BodyMap semantics.

Produce one consolidated review board and obtain operator acceptance before committing new visual geometry.

Do not open a new illustration pipeline.

## 7. Packaging and release

Verify real SCI source manifests, pins and effective runtime imports.

Do not rely on source files only available in a developer's workstation.

Ensure disabled-by-default runtime activation until all producer, DATA, visual and release conditions are satisfied.

Rollback must prevent new V3 session creation without destroying sessions already created.

Deployment needs separate authorization.

## 8. Completion

The sprint is not complete because a valid V3 DTO is returned.

It is complete only after a real, server-owned V3 session can be created and executed in a controlled authorized environment, with verified facts, persistence, recovery and historical readback.

Merge automatically under GOV-MERGE-01 when its mandatory conditions are satisfied.

Do not archive outstanding device or deployment gates as if completed.

## 9. Handoff

After the scoped deliverable, advance to the next approved critical-path preparation.

Return a concise receipt:
- delivered paths and functionality;
- canonical SHA;
- tests and CI;
- V3 runtime status;
- device/release status;
- exact remaining blockers.
