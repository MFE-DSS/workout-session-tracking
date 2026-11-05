# MOB-03 DATA COMPLETION Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:executing-plans ; native autonomous execution requested, one final independent review.

**Goal:** Complete independently executable body-data/account/first-plan consumer work in PR353 without opening UI, destructive deletion or runtime science.
**Architecture:** Existing AuthSession/transport and canonical BodyMeasurement read remain authorities. A headless pagination consumer invalidates personal state across identities/consent/errors. Real SQLite metadata integration proves deletion recovery and owner retirement. Scientific runtime ports stay absent.
**Tech Stack:** Existing Expo/TypeScript/Jest, Python/FastAPI/Pydantic; no dependency or backend migration.
**Spec:** Existing account-onboarding-native proposal/design; operator MOB-03 DATA COMPLETION mandate5Nov2026.

## Global Constraints

Approved entry/forms/preferences/no inventory unchanged. No body UI, endpoint, measurement write, User.weight_kg write/date synthesis, destructive migration, production deletion or synthetic READY serving. One existing PR353; no merge until COMPLETE change gates pass. Canonicalbf847c7 incorporated, scientific producer1.0 remains NOT_SERVED/non-admitted.

## Brainstorming / Options / Risques / Choix retenu

Adding a body screen or activating deletion/science would cross explicit boundaries. Only extending isolated mocks would miss recovery/navigation/data lifetime risks. Retained: headless consumer using real SDK/transport, durable SQLite lifecycle integration, bounded pure refactor and test-only first-plan ports. Server deletion is design/fixtures only; unresolved policy table excludes previously accepted technical choices.

## Review Focus

1. Late page/owner response cannot restore private state after identity or consent change.
2. Duplicate/repeated cursor cannot create a fabricated chronology or endless paging.
3. An unverified refusal or401/404 never proves an authoritative deletion outcome.
4. Restart/concurrent claims cannot replay mutations or reopen a retired owner's journal.
5. Consent/version/owner/fingerprint failure cannot preserve a previously available recommendation.

## Task1 — weight consumer and canonical refactor

Files: api/weightHistoryResource.ts + integration tests; body_profile.py; existing weight backend tests.
Interfaces: WeightHistoryResource(auth,client).state/.refresh()/.loadNext(); values only confirmed, no persistence, identity-generation and request sequence guards. Existing WeightHistoryClient and GET remain read-only unchanged.
- [ ] RED real AuthSession+transport consent/revoked/empty/pagination/invalid cursor/network/expiry/owner/latest-response cases.
- [ ] Implement headless state/pagination with no UI and no prefetch; pending/error states clear readable private data, duplicate pages fail closed.
- [ ] Refactor weight_history_page into UTC/date, quality and row helpers, no output change. Characterize complete JSON against edge cases, then run canonical/HTTP body tests.

## Task2 — durable deletion integration and producer preparation

Files: accountDeletion.ts/tests, ownershipStore.ts factory, real SQLite integration tests; docs/MOB03_DELETION_PRODUCER_DESIGN.md and isolated synthetic test receipts.
Interfaces: createOwnershipBook(db) reuses the existing actual book initializer; AccountDeletionClient remains producer=null by default. Unauthenticated terminal rejection becomes unknown rather than an authoritative refusal.
- [ ] RED unverified refusal and real SQLite lost-response/reopen/pending/concurrent/cross-owner retirement tests.
- [ ] Complete bounded orchestration/factory seams, prove owner7 retired persists across restart while owner8 stays accessible; no actual purge/producer.
- [ ] Specify server idempotency/CAS/reauth/revocation/authoritative status and post-revocation receipt recovery; no route/table implementation. Concise policy-only decision table tied to existing inventory/graph.

## Task3 — first-plan runtime-boundary checks and delivery

Files: firstPlan integration test only; canonical real blocked producer fixtures and existing SYNTHETIC_TEST_ONLY_NOT_SERVED protocol fixture, no production adapter.
- [ ] Exercise real AuthSession/createTransport/client for READY protocol only, insufficiency, NOT_SERVED, stale version, wrong owner/fingerprint, unknown equipment,403consent and late account responses.
- [ ] check_scope then targeted+broad consumer/backend checks, full mobile/TypeScript, Ruff/budget/spec/OpenSpec; fresh review, one Important fix pass.
- [ ] Publish in existing353, actual final CI/Sonar; compact receipt of new code/tests, exact blockers and COMPLETE MOB03 status. No merge/deploy/archive while global mandatory gates remain open.
