# REL-03 OVH Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans inline, one fresh whole-branch review at the end.

**Goal:** Bind synthetic QA source/image/container/origin with independently acquired evidence.
**Architecture:** Strict OVH v2 alongside unchanged Render v1; private feature references and separate process environments. Fixed readonly host collector. Image bytes never uploaded under technical GO.
**Tech Stack:** Python stdlib/httpx, existing Docker/GitHub Actions and Expo config. No new dependencies.
**Spec:** OVH_EVIDENCE_AND_CONFIG.md and OVH_AMENDMENT_SCOPE_20261115.md in this change.

## Global Constraints

Only https://qa.spignos.com in explicit OVH profile. Image 2GiB cap distinct from DB proof caps. No product/UI/SCI/schema/SDK edits, remote changes, secrets creation, APK/OTA or deployment. Preserve all other worktrees. GOV-MERGE-01 covers scoped delivery after checks. Parent 683e88313b0c2c5866f0594766213569628d1659.

## Review Focus

Administrator-owned collector/policy must resist app-user self-attestation. TLS peer and loaded routing must bind actual container through observation interval. Artifact/run/attempt substitution must refuse. No config/key leaks via facade/version/filesystem links. PLAN/Render v1 unchanged.

### Task 1: Explicit synthetic feature configuration

**Files:** tools/qa_delivery/server.py, identity.py; tests/test_qa_delivery_server.py and test_qa_delivery_identity.py.
**Interfaces:** optional feature_config_file: strict qa-feature-config/1.0.0 with included_features and private signature references; QAConfig.feature_environment/feature_profiles. _child_environment backend-only; _facade_environment minimal. Public feature_profiles only when configured.
- [x] Write tests: private references, duplicates/unknown keys, distinct keys/identities, old PLAN, separate child environments, current version redaction.
- [x] check_scope then targeted pytest: expected RED missing interfaces; implement closed parser, distinct environments without startup DDL; rerun expected PASS.
- [x] Real synthetic family HTTP smoke with consent boundaries; no product modifications.

### Task 2: Image receipt and fixed observer

**Files:** tools/qa_delivery/image_receipts.py, ovh_observation.py, deploy/qa/observe_ovh.py; new tests.
**Interfaces:** acquire_image_receipt(reference, client, token) fetches actual GitHub run/attempt/job/artifact; observe_ovh(candidate, proof, client, ssh_runner) pins private SSH policy and fresh nonce observations before/after HTTPS. Fixed collector reads admin policy outside checkout, fixed Docker/nginx inspection only.
- [x] RED tests: forged/foreign/stale receipt, workflow/source mismatch, oversize; nonce/time/image/UID/writer/mount/routing/TLS mismatch.
- [x] Implement strict schemas and bounded subprocess/downloads; verify all refusal/positive cases PASS without external side effects.

### Task 3: Provider/target/pipeline

**Files:** releases.py, pipeline.py, clients/mobile/qa-delivery.config.js, .github/workflows/qa-release.yml; Python/Jest tests.
**Interfaces:** OVH target v2 provider OVH + feature_profiles + configuration_sha256; native target v2 explicit provider. v1 unchanged. observe_target dispatch preserves both existing freshness gates. PREPARE_IMAGE manually produces image provenance metadata from clean archive and resolved base digest; image private encrypted locally, no image upload in technical scope.
- [x] RED exact origin/version/provider and workflow operation tests; implement no implicit downgrade or protected-environment creation.
- [x] Run Python/Jest/TypeScript/workflow tests expected PASS; no EAS or actual image transfer.

### Task 4: Verified delivery

**Files:** deploy/qa/README.md, docs/release/rel-03, registry and existing change.
- [x] Document config, trust chain, installation commands and exact operational blockers.
- [x] Effective tier checks: bounded local full sweep if CI_INFRA, targeted/broad/mobile/OpenSpec/security. One independent whole-branch review; Important fixes RED→GREEN.
- [ ] Commit/push scoped PR; mandatory CI exact HEAD; guarded merge/canonical CI; docs closeout. Keep operational REL03 tasks open.

## Pre-flight and leases

Task1 feature profiles and Task2 evidence consumed by Task3: exact names above. No incompatible shared interfaces. Root owns only technical file list in approved scope; no competing product PR or shared UI lease. Commit after full review, no partial checkpoint labeled complete. Engineering approval does not authorize operational image upload or cloud execution.
