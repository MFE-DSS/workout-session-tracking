# REL-03 OPS-03 — public QA qualified

18 November 2026. Parent `c6190a19c20c916b75761c5104ef162cb7f5e301`.
**Public synthetic HTTP QA: QUALIFIED. Android candidate: not built or installed.**
The operational mandate authorizes the scoped DNS check, QA certificate/vhost,
reload, restricted observation and public tests. It does not authorize an APK/OTA.

## Actual identity

Both OVH authoritative nameservers and public resolvers 1.1.1.1/8.8.8.8 return
`qa.spignos.com A 51.91.79.44`, no AAAA. No DNS record was changed by the agent.
Origin: **https://qa.spignos.com**. Existing production and staging ACME accounts
were reused; no new account or paid host. QA-only certificate acquisition and a
real renewal dry-run passed. Leaf SHA256:
`b6b6b9e91df5f5e6c5944948950541879a77b92d582e64fe0e6d3f9641c9514e`,
SAN/CN `qa.spignos.com`, Let's Encrypt YE2, expires 16 February 2027 13:17:20 UTC.
CA, hostname, actual socket peer and exact version body were checked together.
HTTP port80 serves only ACME; root404. Renewal scheduling/reload at the next
actual certificate renewal is not claimed proven by the dry-run alone.

The QA vhost is `/etc/nginx/sites-enabled/zz-auren-qa-rel03.conf`, SHA256
`4fb3c6efa3d21f7f3062691d0108a8df2998261f154c15b5c3507683d1cf7dc2`.
Loaded nginx configuration SHA256:
`1087c00762cbb7bf630ae28e5ae36833d4ed68cd6729c2668732e49d9b754ed3`.
Master PID1254/start_ticks876; workers834125–834128/start_ticks14560833.
Configuration validation, reload and stable process-generation observation passed.
The root-owned routing proof pins the actual private container address172.23.0.2;
an address, worker or container change requires fresh routing evidence.

Backend source **`b8fc63ffadba35028af9e1c92c2e48892f9fe403`**, image
**`sha256:5ee90ab09696c4312cbe2a99654d5d2368d26f2050839858cca0ec801128334e`**,
container `b81e1442c58a1f5f9a9ca4ec108246c7816a619fe7ace4add974b4e2be5f5f34`,
StartedAt2026-11-18T13:41:51.854023463Z. Image run44188461111 was independently
reacquired from GitHub; no image rebuild/reinstall or database initialization.
Configuration SHA256:
`24f9b58aed1455d5183c809fc65aa1250c395b23451a4c156a925686f84eec94`.
Two restricted SSH observations bracketed public HTTPS with fresh nonces. The
operational binding explicitly says it is **not an Android candidate**; release
must acquire new candidate-bound observations, not reuse this receipt as permission.

API `first-session-runtime/3.0.0`, inventory`plan-calibration-inventory/2.0.0`,
schema **program_builder_operations_01**,46tables,2synthetic accounts.
BODY`body-measurements/1.0.0`, NUT`nutrition-manual/1.0.0`,
Library`owned-library/1.0.0`, Builder`program-builder/1.0.0`.
SCI ACTIVE/generation1; packaging
`22b066a0fb363b1bd435323269bad8a7fa47e4149f18b91e4b039e89d8352dfc`.
Published SCI pins remain unchanged:

- registry `602ff0d32ebc625b4c9474660b5b36ee9983c4c598f16ae9b1269e67e5cea50f`;
- binding `9ef301da08ec3614c7e2a4fbbb95a2384f1c870bca84b6b69eeb4e20a1897389`;
- bundle `78b3e5d99fe05093d6141678fd40f16e744b88d3d87405f14b0f8be357724d94`;
- effective `10e92afb04cd1b14036f5c21e4b3f755a7ac58eddd2cb369be99a355de05b5b9`.

## Public tests and preservation

11 fresh durable synthetic mutation intentions, zero automatic mutation retry;
none of the prior19POST intentions was replayed. PASS:

- A/B authentication, no-store, foreign/missing404 equivalence;
- existing Builder programme/receipt → Library composition → fresh owned session2,
  same identity in Today/execution, entered18kg/9reps, completion and exact history;
  Legacy equipment/load context UNKNOWN, no external-total-mass conversion;
- BODY ownerB:71.2→71.1 synthetic, original/2versions, right side unknown,
  withdrawal, minimal nonnumeric erasure view, all-version erasure and exact receipt;
  ownerA's withdrawn consent is not regranted;
- NUT optional energy, correction1000→1100, zero protein distinct from missing
  carbohydrate/fat, declared completeness, target isolation; no artificial target;
- sampled public `/`, `/docs`, `/redoc`, `/openapi.json`, `/admin`, `/.env`,
  `/files`, `/api/mobile/v1/admin` all404; version/health exact and no-store.

UNAVAILABLE: new installed native/physical client, actual packet loss/SQLite fault
in this HTTP campaign. Prior OPS02 real QA-only stop/restart and persisted Bearer/
session evidence is retained with unchanged container/StartedAt; not repeated
without need. This does not prove V3 seven-calibration native flow or security
exhaustiveness. Initial smoke stopped before business writes on duplicated
`no-store` headers; the private probe now compares exact semantic directives,
rejecting conflicting directives. Gateway code unchanged. An SSL diagnostic used
a positional API correction; no TLS verification bypass.

Postflight: same boot,8personal container identities/images/env/mounts/ports,
7services active and Tailscale unchanged; all10existing route/certificate profiles
unchanged. Effective nginx bytes excluding the single QA section are identical.
Personal web checkout/unit hashes preserved. Old broken workout backup timer is
not repaired or declared healthy by this scope.

New current-state backup/export after public writes: three separately encrypted
snapshot/manifest/anchor files, authenticated Mac readback and disposable restore
PASS;46tables, FK/integrity/digests and original ownership anchor verified.
Continuity digest
`39f82c3a8dc61722ed7cd5ef6d765f54fb5d2f50338ba3a61e88adf2470cca8e`.
No encryption key persisted on host, restored copy promoted or old backup removed.
This operational snapshot is **not yet the candidate-bound release-backup proof**.

## Rollback and remaining gate

Authorized contingency stops only `auren-qa-rel03.service`; preserve both QA
volumes, keys and existing encrypted backups. For QA routing rollback, validate
the exact owned file before removal/replacement, `nginx -t` then authorized reload;
the retained pre-TLS QA-only HTTP vhost is a reference. Never restore an old
database/image as writer without a compatible recovery decision. Existing personal
vhosts/services remain intact. No destructive rollback or app downgrade claimed.

Private evidence: `~/auren-review/rel03-ops02-20261116/ops03-20261118/`.
Raw DB, intentions, observer access and keys remain private. Current qualification
is point-in-time evidence, not permanent availability. REL03 remains active for
installed-client/update/rollback/device gates. DATA, physical and production
acceptance are not inferred from synthetic tests. Muscle availability NOT_SERVED.
