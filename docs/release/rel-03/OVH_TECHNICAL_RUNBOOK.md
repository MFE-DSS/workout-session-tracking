# REL-03 OVH — technical preparation and operational boundary

Technical GO: `call_657199a80f2441d3b3bd3d450dfaaabf`, 15 November 2026. This code prepares an isolated QA service; it does not create or modify an OVH service, DNS/TLS, secret, image custody, APK or OTA. Canonical feature parent: `683e88313b0c2c5866f0594766213569628d1659` (BODY, NUT, library and builder). Schema: `program_builder_operations_01`.

## Independent chain

1. The manual `PREPARE_IMAGE` operation first checks the existing protected `qa-release` environment. No environment is created implicitly. Its image job requires a direct human review comment `APPROVE_QA_IMAGE <exact-source-sha>`, distinct from a release or merge decision. It builds from a clean Git archive, resolves and pins the Python base digest, records Dockerfile/context digests, amd64 config imageID and actual exported archive bytes/checksum. Only metadata is uploaded; local disposable bytes are removed. **This technical delivery has not executed that cloud image job.**
2. Producer payload `qa-image-build-payload/1.0.0` cannot contain its own future artifact ID. `acquire_image_receipt` independently fetches the run, exact attempt/job, artifact metadata and ZIP, recomputes its checksum and verifies source CI. It then adds the acquired artifact ID in `qa-image-build/1.0.0`. The artifact checksum, exported image checksum and Docker configuration imageID are different identities. A JSON copied into a candidate is insufficient.
3. Actual image custody is still operationally unprovisioned. `stage_image` and `restore_image` support private local AES-256-GCM streaming with existing private 32-byte keys, a 2GiB plaintext cap, no overwrite and no final unauthenticated plaintext. They do not upload or load Docker. Existing DB proof caps remain 128MiB/file and 256MiB total. A later separately approved private transport must preserve the **same** acquired image checksum/imageID; a rebuilt image needs its own receipt.
4. The release orchestrator requires a fresh pinned SSH observation before and after the HTTPS version/health reads. Public TLS must verify normally and the connected peer IP must equal the qualified host. Only `https://qa.spignos.com` is admitted by OVH v2; no proxy/CDN, port, sibling origin, redirect or v1 fallback. The future target file remains unprovisioned.
5. The administrator-owned collector observes only the fixed `auren-qa-rel03` resource and the QA nginx routing generation. Application labels or version responses cannot attest themselves. The service's actual imageID, single writer, nonroot UID, named volumes, binding, resources and loaded routing must match policy. A healthy container plus an unrelated HTTPS responder fails.

## Administrator installation — future authorized operation only

No command in this section has been run against OVH. First qualify a supported host OS and sufficient resources; the previously observed Ubuntu25.04 is outside support. Preserve existing nginx, services and personal databases. Never grant the audit user Docker group/socket or a shell.

Install the standalone checked-in `deploy/qa/observe_ovh.py` as root-owned `/usr/local/libexec/auren-qa-observe-v1` outside app checkout, with a qualified Python3.11+ interpreter. Configure `qa-audit` with forced command, `restrict`, no PTY/forwarding/agent forwarding; its narrowly scoped privilege may execute only this root-owned collector. The operator must review the actual sudo/SSH policy before activation. No generic sudo/python/docker command is allowed to that user.

Root-owned files under `/etc/auren-qa/` (all ancestors root-owned and not group/world writable):

- `observer-policy.json`: exact policy fields validated by `validate_policy` in `ovh_observation.py`; resource `auren-qa-rel03`, origin exact, qualified public peer IP, UID10001, bridge, `unless-stopped`, at most2GiB RAM/2CPU/256pids. Actual approved limits must match exactly. Data volume `auren-qa-rel03-data` RW at `/var/lib/qa`; config volume `auren-qa-rel03-config` RO at `/etc/secrets`; only `127.0.0.1:8088 → 8080/tcp`. Four exact feature profiles. No production/bind/Docker mounts.
- `activation-proof.json`: exact container_id, image_id, started_at and configuration_sha256 recorded by the qualified administrator after the explicitly approved activation. It binds the immutable readonly private configuration to this actual container generation. Not an app-produced assertion.
- `routing-loaded.json`: whole `nginx -T` configuration digest, actual master `{pid,start_ticks}`, exact child generation list and closed QA vhost text specified in `verify_loaded_routing`. The administrator records these **after successful loading**. The collector rejects changed config, PID reuse, reload/worker generation changes or an alternate upstream. A reload or worker replacement requires renewed administrator qualification; automatic inference of loaded config from files alone is forbidden.

The collector also requires the exact existing Dockerfile bootstrap entrypoint and config/activation arguments; a facade-only or other command override is refused. The container requires read-only rootfs, all capabilities dropped, no new privileges/devices/host PID or IPC namespace, a64MiB noexec/nosuid `/tmp` tmpfs, and a bounded local healthcheck. The actual image needs the approved source; a Docker label is insufficient. App secrets stay in the private readonly config volume, mode0600/owner10001 inside a0700 directory. Observer output excludes Env, secrets, DB rows and volume contents; private routing/activation records are not published.

## Configuration

The old `qa-config.json` retains PLAN-only behavior when `feature_config_file` is absent. The optional reference must identify an absolute private0600 JSON file in a private0700 parent with no symlink component:

```json
{
  "schema_version": "qa-feature-config/1.0.0",
  "included_features": ["BODY", "NUT", "LIBRARY", "BUILDER"],
  "signatures": {
    "NUT": {"identity": "qa-rel03-nut", "signing_key_file": "/etc/secrets/nut.key"},
    "LIBRARY": {"identity": "qa-rel03-library", "signing_key_file": "/etc/secrets/library.key"},
    "BUILDER": {"identity": "qa-rel03-builder", "signing_key_file": "/etc/secrets/builder.key"}
  }
}
```

These are path/identity examples, not provisioned secrets or current target facts. Keys must already exist, be distinct/stable, at least32characters, private and owned by the service UID. No automatic key generation/rotation. Duplicate/unknown keys, missing references, shared identities/keys and builder without library refuse. BODY enables only `BODY_ASSESSMENT_ENABLED`; no body intelligence or capture-quality flag. NUT and BODY consent remain independent. SMTP/Sentry/performance/SQL logging are absent from rebuilt process environments. Backend flags never enter the facade environment.

OVH target attestation v2 adds `provider: OVH`, `configuration_sha256` and exact `feature_profiles` to the existing target fields. Its deployment reference is `ovh:auren-qa-rel03/sha256:<actual-imageID-hex>`. Native target v2 uses the corresponding camelCase fields and exact origin. It does not change product/SCI contract versions or establish a runtime fingerprint. Render v1 is preserved.

Private cutover proof `provider` has exactly `kind`, `image_reference`, `ssh`, `policy`. `image_reference`: run_id, attempt, artifact_id, source_sha. `ssh`: qualified IP host, user `qa-audit`, port22, known_hosts_sha256. Private runtime paths come from `AUREN_QA_OVH_IDENTITY_FILE` and `AUREN_QA_OVH_KNOWN_HOSTS_FILE`, never proof-controlled arbitrary commands. CI materializes the existing protected `QA_OVH_AUDIT_KEY`/`QA_OVH_KNOWN_HOSTS` references only for OVH. Missing credentials remain a refusal, not an instruction to create secrets.

## Release remains NOT_READY

Remaining operational decisions: supported-host qualification, readonly collector/audit account and loaded routing receipt installation, distinct synthetic service/volumes/state, private image/proof custody, ownership continuity versus explicit new QA identity, existing protected release environment, real DNS/TLS and backup/export recovery. No identity reuse into a new unrelated database. Then consolidate merged features and actual API/SCI/schema/native fingerprint/signing facts; separately authorize image transfer/deployment and EAS candidate. Installed smoke/upgrade/OTA/rollback and physical tester acceptance remain open. No APK per feature merge.
