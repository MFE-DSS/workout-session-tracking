# Portable synthetic QA server — REL-03 preparation

PREPARED only. No hosting, spend, cutover, QA02 process change or publication is
authorized by these artifacts. One instance, one canonical worker, private
persistent SQLite volume; no scaling or automatic deployment. Framework unchanged. QA-only httpx/httpcore/certifi are pinned in the Dockerfile;
the canonical application dependency lock is unchanged.

Build only after code/CI approval, using a **tracked Git archive of the exact
approved SHA** locally, never the ambient checkout (which may contain private
files). The managed Render alternative uses only its trusted tracked Git checkout
at the approved deploy commit, with the explicit COPY closure and Dockerfile-specific
ignore file; Render root secret filenames must remain qa-config.json, qa-access.json
and qa-auth-secret, outside all COPY sources. Pass that same SHA as `--build-arg SOURCE_SHA=<approved SHA>` to
`docker build -f deploy/qa/Dockerfile -`. Startup compares configured source with
the immutable image marker; checkout validation compares Git HEAD. A clean,
merged source remains a separate release preflight requirement. No image build
has been executed in this preparation environment.

The image builds and verifies the real inventory2 science bundle, then makes it
read only. Runtime uses the exact deployed source SHA. The bootstrap initially serves only
maintenance; it never creates a DB, secret, application config or canonical server.
After explicit private activation and restart, the parent supervises a
canonical API on fixed loopback 8140 and a bounded public mobile facade on PORT
(default 8080). Either child exiting stops both; SIGTERM drains and stops them.
Canonical lifespan is explicitly **off**: no startup create_all, seed or migration.
Never run the canonical server directly as the public entrypoint.

Provide an absolute-path configuration file, mounted privately at
`/etc/secrets/qa-config.json`, containing exactly:

```json
{
  "data_scope": "SYNTHETIC_ONLY",
  "db_path": "/var/lib/qa/qa.db",
  "bundle_root": "/opt/science",
  "environment_id": "qa-rel03-isolated",
  "source_sha": "<exact 40 lowercase hex deployed Git SHA>",
  "access_file": "/etc/secrets/qa-access.json",
  "secret_file": "/etc/secrets/qa-auth-secret"
}
```

`access.json` has `signup_users` and `login_users` lists of explicitly assigned
`qa02-` synthetic names; every signup must be allowed to log in. Auth secret is
an existing dedicated QA secret (minimum 32 characters), never a production
value. Both referenced files must be owner-only readable (0600); owned volume
must be writable by UID10001. Never include their contents in Git, logs or APK.
Configuration is an operator assertion of synthetic scope, not a data classifier.
Inherited BODY/SMTP/SENTRY/PERF/SQL logging features are rejected; child env is
constructed from scratch and uses an empty cwd so no ambient `.env` is loaded.

Validate without starting anything:

```sh
python -m tools.qa_delivery.server --config /etc/secrets/qa-config.json --validate-only
```

`/__qa_health` verifies the whole DB schema/integrity/FKs, real bundle and upstream
transport. `/__qa_version` reads current SCI generation/state on every request.
Full DB row digests and SCI execution occur only at startup and health/version;
ordinary mobile calls check admitted schema cheaply, then rely on the canonical
V3 consumer's fresh authority guards. No generation is cached as current.
WITHDRAWN/DISABLED remains transport healthy; no scientific READY is fabricated.
Neither endpoint exposes owner, token, secret, path or approval ref. All canonical
forwarding remains closed to non-mobile paths, unassigned auth and real email.
QA02 byte/size/deadline/redirect/rate/concurrency guards are reused unchanged.
Private child output is suppressed; public failures are deliberately redacted.
A failed health response is not a proof of current scientific permission.

## Complete SQLite backup and restore in a new copy

No legacy JSON export/restore: every table, ID, refresh hash and PLAN fact is
preserved by SQLite online backup. Exact admitted head is
`plan_v3_20261107_01`, plus exact canonical schema snapshot, integrity and FKs.
Unknown schemas require a separately authorized compatibility change.

```sh
python -m tools.qa_delivery.database backup /private/source.db /private/new-backup.db
python -m tools.qa_delivery.database verify /private/new-backup.db
python -m tools.qa_delivery.database restore /private/new-backup.db /private/new-restored.db
```

Restore requires the matching private manifest and verifies its complete file
checksum and every table digest before copying, including logical tampering
that SQLite integrity checks alone cannot detect. Keep the sidecar with backups.
The destination and its `.manifest.json` must not exist. Snapshot and sidecar
are 0600 and published with exclusive same-filesystem links after verification;
ordinary failures/interruptions clean owned partial files. The DB publication is
atomic; a process/host crash may leave the already-published sidecar without its
DB, which is incomplete and must not be used. No source mutation or in-place
restore, retention purge, seed or migration is performed. The manifest records
schema, all table counts/digests, continuity and complete file checksum without
row values. Capture returns failure if the source changes across verification
and backup; retry under a controlled writer freeze for cutover. A snapshot does
not prove that a writer has stopped, synthetic status or release authorization.

Before any authorized cutover: close all old forwarding including auth/GET,
drain and stop the old writer, capture and export privately off-service, restore
into a fresh isolated volume, validate all identities/refresh/PLAN and current
SCI authority, then open exactly one writer. Never reactivate an old snapshot
as writer after target use. Keep exact source/bundle/release receipt separately.
Daily backups and pre-release exports are operator obligations; no scheduler,
provider snapshot, RPO/RTO success or active target is invented here. Benchmark
memory/latency and rehearse restart/restore before approving a hosting size.


## First managed start and explicit activation

`render.yaml` is an unapproved proposal: new service name must be checked for
collision, Frankfurt region requires operator acceptance, one 0.5c-512mb instance,
1GiB private disk, auto-deploy off. SOURCE_SHA is the exact approved public Git SHA;
Render translates this environment variable to the Docker ARG. Confirm deploy
commit.id and current /__qa_version source_sha agree. No image has been built here.
There is no seed/migration/pre-deploy command or provider/account creation script.

With no /var/lib/qa/activation.json, only GET /__qa_liveness is 200 with
`{"alive":true,"data_ready":false}`. Every other method/path is 503 Retry-After30.
The same liveness response in active mode remains only a process signal; strong
health/version still attest their dependencies. Render uses liveness for maintenance
SSH availability; release readiness always requires health/version independently.
No file browser or automatic activation on DB presence exists.

Before transfer, qualify the real disk as UID10001, including creating SQLite WAL
sidecars, and owner-only readability of actual Render-managed secret references.
Those permissions are **unqualified** here. No root/chown/chmod workaround for a
managed mount is implemented. If managed secret modes cannot satisfy Task1, an
explicitly authorized private0600 copy owned by UID10001 must be qualified before
activation; never relax the validator. Runtime image home has private .ssh0700;
no key is added by this package.

Only the future approved cutover may write a private0600 activation marker owned
by the runtime user, containing exactly schema_version `qa-activation/1.0.0`, the
exact source_sha and config_sha256 (SHA256 of the complete config file bytes).
The config must itself be owner-private. Startup validates these bindings, then
runs full Task1 config/DB/bundle/science validation and confirms DB/directory write
access before exec of the fixed Task1 supervisor. Existing DB presence alone is
insufficient. A marker arriving while maintenance runs does nothing until an
explicit restart of the same image. A malformed marker fails startup closed.

The first hosting/cutover/secret transfer and first build/update remain the single
external decision described in [the release package](../../docs/release/rel-03/README.md).
Base proposal is USD7.25/month before taxes/variable bandwidth/build minutes;
there is no hard global invoice cap or automatic paid upgrade. The measured EAS
Free snapshot10Android remaining at2026-11-10T12:23:46Z must be re-read before use.
