# Operational checklists

Three short, concrete checklists for the V1 operator. Designed
to be tickable in a terminal without context-switching.

Each step says what command to run AND what to expect.

- [First deploy](#1-first-deploy)
- [Update](#2-update)
- [Backup verification](#3-backup-verification)
- [Restore](#4-restore)

---

## 1. First deploy

Prerequisites: a VPS with SSH access, a DNS name pointing at it,
Ubuntu/Debian recent enough for Python 3.11.

### 1.1 System + user

```bash
sudo adduser --system --group --home /srv/workout workout
sudo apt update && sudo apt install -y \
  python3.11 python3.11-venv nginx certbot python3-certbot-nginx sqlite3 apache2-utils
sudo mkdir -p /srv/workout && sudo chown workout:workout /srv/workout
```
**Expected:** `workout` user exists, base deps installed.

### 1.2 Clone + install

```bash
sudo -u workout bash -c '
  cd /srv/workout &&
  git clone <repo-url> . &&
  python3.11 -m venv .venv &&
  .venv/bin/pip install -r requirements-lock.txt &&
  cp .env.example .env
'
# then edit /srv/workout/.env with your real values:
sudo -u workout vi /srv/workout/.env
# set APP_SECRET_KEY, APP_BASE_URL, DATABASE_URL, BACKUP_DIR, BACKUP_RETENTION_DAYS
```
**Expected:** venv exists, requirements installed, `.env` is real.

> **Why the lock and not `requirements.txt`?** `requirements.txt` is the
> human-edited *source spec* and carries open ranges (`fastapi>=0.110`, …).
> `requirements-lock.txt` is what CI installs and what
> `scripts/deploy_prod.sh` installs. Installing the source spec by hand ships
> versions no test ever ran against. One install contract, every consumer.

### 1.3 Migrations + seed

```bash
sudo -u workout bash -c '
  cd /srv/workout &&
  .venv/bin/python -m scripts.check_alembic_drift &&
  .venv/bin/alembic upgrade head &&
  .venv/bin/python -m scripts.seed_db
'
```
**Expected:**
- drift check: `Alembic drift check: OK (no diff).`
- alembic: `Running upgrade  -> <rev>, initial baseline`
- seed: `Reference catalog: seeded`

### 1.4 systemd units

```bash
# Main app
sudo cp /srv/workout/deploy/workout.service /etc/systemd/system/
# Nightly backup
sudo cp /srv/workout/deploy/workout-backup.service /etc/systemd/system/
sudo cp /srv/workout/deploy/workout-backup.timer   /etc/systemd/system/
# Nightly verify
sudo cp /srv/workout/deploy/workout-backup-verify.service /etc/systemd/system/
sudo cp /srv/workout/deploy/workout-backup-verify.timer   /etc/systemd/system/

sudo systemctl daemon-reload
sudo systemctl enable --now workout
sudo systemctl enable --now workout-backup.timer
sudo systemctl enable --now workout-backup-verify.timer
```
**Expected:** `systemctl status workout` is `active (running)`,
both timers appear in `systemctl list-timers`.

### 1.5 nginx + HTTPS + basic_auth

```bash
sudo htpasswd -c /etc/nginx/workout.htpasswd moi
sudo cp /srv/workout/deploy/nginx.conf.example /etc/nginx/sites-available/workout
# edit /etc/nginx/sites-available/workout:
#   - replace workout.example.com with your domain
#   - add the auth_basic / auth_basic_user_file block
#     (see deploy/README.md section 5.2)
sudo ln -s /etc/nginx/sites-available/workout /etc/nginx/sites-enabled/workout
sudo nginx -t && sudo systemctl reload nginx
sudo certbot --nginx -d workout.example.com
```
**Expected:** `curl -sfL https://workout.example.com/healthz` returns
`{"status":"ok"}` without credentials.

### 1.6 Smoke test

```bash
# Public probe (no auth)
curl -sfL http://127.0.0.1:8000/healthz
# Strict probe (operator, shows backup state)
curl -sfL http://127.0.0.1:8000/healthz/strict | python -m json.tool
# Library renders
curl -sfL -u moi:<pwd> https://workout.example.com/library -o /dev/null
```
**Expected:**
- `/healthz` → `{"status":"ok"}`
- `/healthz/strict` → JSON with `"status":"ok"` or `"degraded"`
  (degraded is normal on first deploy because no backup exists
  yet; the `backup.present` field will be `false`).

### 1.6.1 First manual backup

Trigger the backup immediately instead of waiting for 03:30:

```bash
sudo systemctl start workout-backup.service
sudo -u workout BACKUP_DIR=/srv/workout/var/backups \
  /srv/workout/.venv/bin/python -m scripts.list_backups
```
**Expected:** `list_backups` prints one JSON and one CSV file.

### 1.7 Verify backup integrity

```bash
sudo systemctl start workout-backup-verify.service
sudo journalctl -u workout-backup-verify.service -n 20
```
**Expected:** journal shows
`verify_backup: [OK ] sessions-YYYYMMDD_HHMM.json ok (schema_version=1, exported=N, live=N)`.

Or run it by hand:
```bash
sudo -u workout /srv/workout/.venv/bin/python -m scripts.verify_backup
echo "exit=$?"
```
**Expected:** stdout starts with `verify_backup: [OK ] ...`, exit 0.

### 1.8 Done

You're live. Open the app in a browser, log one test session,
verify `/healthz/strict` still reports `"status":"ok"`.

---

## 2. Update

### 2.1 Automated (recommended)

```bash
sudo bash /srv/workout/scripts/deploy_prod.sh
```

The script handles: SQLite backup, git pull, pip install, drift
check, alembic migrate, seed, restart, and health verification.
It aborts on any error and prints rollback hints.

To deploy a specific branch:
```bash
sudo DEPLOY_BRANCH=release/v2 bash /srv/workout/scripts/deploy_prod.sh
```

**Expected:** green "Deploy successful" banner with commit SHA.

### 2.2 Manual (fallback)

Use if `scripts/deploy_prod.sh` is not available or needs debugging. **These
steps stand in for that script and must stay identical to it** — in particular
the install line, which reads the lock exactly as the script does. The manual
path is a wrapper of the canonical path, never a second procedure:

```bash
sudo -u workout bash -c '
  cd /srv/workout &&
  git pull &&
  .venv/bin/pip install -r requirements-lock.txt &&
  .venv/bin/python -m scripts.check_alembic_drift &&
  .venv/bin/alembic upgrade head &&
  .venv/bin/python -m scripts.seed_db
' && sudo systemctl restart workout
```
**Expected:** drift check OK, alembic upgrade lists any new
revisions, seed prints `unchanged` or `seeded`, service restarts.

Then verify:

```bash
curl -sfL http://127.0.0.1:8000/healthz
curl -sfL http://127.0.0.1:8000/healthz/strict | python -m json.tool
sudo -u workout /srv/workout/.venv/bin/python -m scripts.verify_backup
```
**Expected:** `/healthz/strict` returns `"status":"ok"`,
`verify_backup` exits 0.

---

## 3. Backup verification

### 3.1 Manual, on-demand

```bash
sudo -u workout /srv/workout/.venv/bin/python -m scripts.verify_backup
echo "exit=$?"
```
**Expected:**
- `[OK ] sessions-YYYYMMDD_HHMM.json ok (schema_version=1, exported=N, live=N)`
- exit 0

If it fails:
- `[FAIL] no JSON backup file found in ...` → the backup cron
  never ran. Check `workout-backup.timer`.
- `[FAIL] cannot parse JSON: ...` → file is corrupt. Check
  disk, delete, re-run `backup_sessions`.
- `[FAIL] schema_version is X, expected 1` → either the file
  was produced by an incompatible version, or `SCHEMA_VERSION`
  changed in the code. Compare `git log app/services/export_builder.py`.

### 3.2 Automated daily

`workout-backup-verify.timer` runs the verifier every night at
04:00 UTC, 30 min after the backup. Wire an alert on it:

```bash
# Last exit code of the oneshot
systemctl show workout-backup-verify.service --property=ExecMainStatus
```
Expect `ExecMainStatus=0`. Anything else is a failure to act on.

### 3.3 Signal in the app

`GET /export` (browser) shows the latest backup file name, size,
age, schema_version, and an **"Intégrité : OK / FAIL"** badge.
Any errors are listed inline.

`GET /healthz/strict` (curl) returns the same information as JSON
with a 200 / 503 status code — suitable for `curl --fail` in cron.

---

## 4. Restore

Full coverage in `deploy/README.md` section 8. Shortcut for the
operator in a hurry:

### 4.1 Rollback in place (recommended)

```bash
sudo systemctl stop workout
sudo cp /srv/workout/var/workout-2026-04-08.db /srv/workout/var/workout.db
sudo chown workout:workout /srv/workout/var/workout.db
sudo systemctl start workout
curl -sfL http://127.0.0.1:8000/healthz
```
**Expected:** `{"status":"ok"}`.

### 4.2 Fresh machine

Follow checklist **1. First deploy** on the new machine, then
copy the latest SQLite snapshot into `/srv/workout/var/workout.db`
BEFORE enabling `workout.service`. Run the drift check and
`alembic upgrade head` after the copy.

### 4.3 Ad-hoc analysis

Open `sessions-YYYYMMDD_HHMM.csv` in Excel / Numbers / Pandas.
This is a read-only view, not a restore.

---

## 5. Restore drill (periodic confidence check)

This is NOT an emergency procedure — it's a periodic drill you
run to prove your backups are actually restorable. Do it once
after the first deploy, then once a month, or whenever the
backup pipeline changes.

### 5.1 Prep: create a throwaway DB

```bash
export DRILL_DB="/tmp/workout-drill-$(date +%s).db"
export DATABASE_URL="sqlite:///${DRILL_DB}"
export BACKUP_DIR=/srv/workout/var/backups

# Apply the schema to the empty file
cd /srv/workout
.venv/bin/alembic upgrade head
```
**Expected:** `Running upgrade  -> <rev>, initial baseline`.
The drill DB is now empty with the right schema.

### 5.2 Restore the latest JSON backup

```bash
.venv/bin/python -m scripts.restore_latest_backup
```
**Expected:**
- stdout starts with `restore: source file = sessions-YYYYMMDD_HHMM.json`
- stdout ends with `restore: OK — restored N sessions, M exercises, P sets`
- stdout has a `verify:` line showing the first session's
  template name + started_at
- exit code 0

If it FAILS:
- `restore: FAIL — no JSON backup found` → the backup cron
  never ran. Fix `workout-backup.timer`.
- `restore: FAIL — cannot read JSON` → the file is corrupt.
  Run `python -m scripts.verify_backup` for the full diagnosis.
- `restore: FAIL — schema_version is X, expected 1` → the
  backup was produced by a different code version. Compare the
  git history of `app/services/export_builder.py`.
- `restore: FAIL — target DB is not empty` → you're pointing
  at the live DB instead of the drill DB. Double-check
  `$DATABASE_URL`.

### 5.3 Verify restored data

```bash
.venv/bin/python -m scripts.verify_backup
```
**Expected:** `[OK ]` with matching exported count and live count.

```bash
.venv/bin/python -c "
from app.database import SessionLocal
from sqlalchemy import select, func
from app.models.session import WorkoutSession
with SessionLocal() as db:
    n = db.execute(select(func.count(WorkoutSession.id))).scalar_one()
    print(f'{n} sessions in drill DB')
"
```
**Expected:** the same count that `restore_latest_backup` printed.

### 5.4 Spot-check one session

```bash
.venv/bin/python -c "
from app.database import SessionLocal
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.session import WorkoutSession, SessionExercise
with SessionLocal() as db:
    s = db.execute(
        select(WorkoutSession)
        .options(selectinload(WorkoutSession.session_exercises).selectinload(SessionExercise.set_logs))
        .limit(1)
    ).scalar_one()
    print(f'{s.template_name_snapshot} · started {s.started_at} · {len(s.session_exercises)} exercises')
    for se in s.session_exercises[:3]:
        work = [sl for sl in se.set_logs if sl.kind == \"work\" and sl.completed]
        print(f'  {se.exercise_code_snapshot} {se.exercise_name_snapshot}: {len(work)} work sets done')
"
```
**Expected:** readable output with real template names, exercise
codes, and set counts. If the output is empty or garbled, the
backup is structurally broken.

### 5.5 Cleanup

```bash
rm -f "${DRILL_DB}"
unset DRILL_DB DATABASE_URL BACKUP_DIR
```

### 5.6 Done

If 5.2 + 5.3 + 5.4 all show sensible data: **the backup is
proven restorable**. Log the date somewhere. Next drill in 30
days.
