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
  .venv/bin/pip install -r requirements.txt &&
  cp .env.example .env
'
# then edit /srv/workout/.env with your real values:
sudo -u workout vi /srv/workout/.env
# set APP_SECRET_KEY, APP_BASE_URL, DATABASE_URL, BACKUP_DIR, BACKUP_RETENTION_DAYS
```
**Expected:** venv exists, requirements installed, `.env` is real.

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

Use every time you `git pull`:

```bash
sudo -u workout bash -c '
  cd /srv/workout &&
  git pull &&
  .venv/bin/pip install -r requirements.txt &&
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
