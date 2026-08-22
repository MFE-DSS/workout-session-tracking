# First Deployment on OVH VPS — Step by Step

One-page guide. Assumes a fresh Ubuntu 22.04+ VPS with SSH
access and a DNS name already pointing at it. Total time: ~20
minutes.

> For subsequent updates, see [CHECKLISTS.md](CHECKLISTS.md)
> section 2. For backups and restore, see sections 3-5.

---

## 1. Server packages

```bash
sudo apt update && sudo apt install -y \
  python3.11 python3.11-venv \
  nginx certbot python3-certbot-nginx \
  sqlite3 apache2-utils
```

---

## 2. System user

```bash
sudo adduser --system --group --home /opt/workout-session-tracking workout
```

---

## 3. Clone + venv + deps

```bash
sudo -u workout bash -c '
  cd /opt/workout-session-tracking &&
  git clone https://github.com/mfe-dss/workout-session-tracking.git . &&
  python3.11 -m venv .venv &&
  .venv/bin/pip install -r requirements-lock.txt
'
```

---

## 4. Production environment file

```bash
sudo -u workout cp /opt/workout-session-tracking/.env.production.example \
  /opt/workout-session-tracking/.env.production

sudo -u workout vi /opt/workout-session-tracking/.env.production
# Fill in:
#   APP_SECRET_KEY   a real random string (e.g., python3 -c "import secrets; print(secrets.token_urlsafe(32))")
#   APP_BASE_URL     https://YOUR_DOMAIN
#   DATABASE_URL     sqlite:////opt/workout-session-tracking/var/app.db

sudo chmod 640 /opt/workout-session-tracking/.env.production
```

---

## 5. Persistent directories

```bash
sudo -u workout mkdir -p /opt/workout-session-tracking/var/backups
```

---

## 6. Database schema + seed

```bash
sudo -u workout bash -c '
  cd /opt/workout-session-tracking &&
  export $(grep -v "^#" .env.production | xargs) &&
  .venv/bin/python -m scripts.check_alembic_drift &&
  .venv/bin/alembic upgrade head &&
  .venv/bin/python -m scripts.seed_db
'
```

**Expected:**
- drift check: `Alembic drift check: OK (no diff).`
- alembic: `Running upgrade  -> ef67ec29e3e0, initial baseline`
- seed: `Reference catalog: seeded`

---

## 7. systemd — main app

The existing `deploy/workout.service` is written for
`/srv/workout`. Adapt it to `/opt/workout-session-tracking`:

```bash
sudo cp /opt/workout-session-tracking/deploy/workout.service /etc/systemd/system/workout.service
```

Edit `/etc/systemd/system/workout.service`:
- `User=workout`
- `Group=workout`
- `WorkingDirectory=/opt/workout-session-tracking`
- `EnvironmentFile=/opt/workout-session-tracking/.env.production`
- `ExecStart=/opt/workout-session-tracking/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --proxy-headers --forwarded-allow-ips="127.0.0.1"`
- `ReadWritePaths=/opt/workout-session-tracking/var`

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now workout
sudo systemctl status workout
```

**Expected:** `active (running)`.

Quick liveness check:
```bash
curl -sf http://127.0.0.1:8000/healthz
# → {"status":"ok"}
```

---

## 8. nginx + basic_auth

### 8.1 Create the password file

```bash
sudo htpasswd -c /etc/nginx/workout.htpasswd moi
```

### 8.2 Deploy the vhost

```bash
sudo cp /opt/workout-session-tracking/deploy/nginx.conf.example \
  /etc/nginx/sites-available/workout
```

Edit `/etc/nginx/sites-available/workout`:
- Replace every `workout.example.com` with your real domain.
- Replace `/srv/workout` paths with `/opt/workout-session-tracking`
  where applicable (the `alias` for `/static/`).
- Make sure the `auth_basic` block is active (see
  `deploy/README.md` section 5.2 for the full reference vhost).

```bash
sudo ln -sf /etc/nginx/sites-available/workout /etc/nginx/sites-enabled/workout
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx
```

### 8.3 HTTPS via Certbot

```bash
sudo certbot --nginx -d YOUR_DOMAIN
```

**Expected:** Certbot modifies the vhost to add SSL directives
and a redirect from port 80 to 443. Test:

```bash
curl -sfL https://YOUR_DOMAIN/healthz
# → {"status":"ok"} (no auth required on /healthz)
```

---

## 9. Backup + verify timers

```bash
# Edit the service files to point at /opt/workout-session-tracking:
for f in workout-backup.service workout-backup.timer \
         workout-backup-verify.service workout-backup-verify.timer; do
  sudo cp /opt/workout-session-tracking/deploy/$f /etc/systemd/system/$f
done

# Edit each .service to adjust:
#   WorkingDirectory=/opt/workout-session-tracking
#   EnvironmentFile=/opt/workout-session-tracking/.env.production
#   ExecStart=/opt/workout-session-tracking/.venv/bin/python -m scripts.<name>
#   ReadWritePaths=/opt/workout-session-tracking/var

sudo systemctl daemon-reload
sudo systemctl enable --now workout-backup.timer
sudo systemctl enable --now workout-backup-verify.timer
sudo systemctl list-timers | grep workout
```

**Expected:** both timers listed.

Trigger the first backup + verify immediately:

```bash
sudo systemctl start workout-backup.service
sudo systemctl start workout-backup-verify.service
sudo journalctl -u workout-backup-verify.service -n 10
```

**Expected:** `verify_backup: [OK ] sessions-...json ok (...)`.

---

## 10. Smoke test

```bash
sudo -u workout bash /opt/workout-session-tracking/scripts/smoke_deploy.sh
```

**Expected:** every line is `PASS`, last line is `ALL CHECKS PASSED`.

If the app is behind basic_auth, run the smoke script on the
loopback (it defaults to `http://127.0.0.1:8000` which bypasses
nginx). For HTTPS-level testing:

```bash
BASE_URL=https://YOUR_DOMAIN \
  # Replace <user> + <password> with your real basic-auth credentials.
  curl -sf -u '<user>:<password>' https://YOUR_DOMAIN/healthz
```

---

## 11. Post-deploy verification

```bash
# Strict health (includes backup check)
curl -sf http://127.0.0.1:8000/healthz/strict | python3 -m json.tool

# Drift guard
sudo -u workout bash -c '
  cd /opt/workout-session-tracking &&
  export $(grep -v "^#" .env.production | xargs) &&
  .venv/bin/python -m scripts.check_alembic_drift
'

# List backups
sudo -u workout bash -c '
  cd /opt/workout-session-tracking &&
  export $(grep -v "^#" .env.production | xargs) &&
  .venv/bin/python -m scripts.list_backups
'
```

---

## 12. Rollback

If anything goes wrong after a `git pull` + restart:

```bash
sudo systemctl stop workout

# Option A: revert the code
sudo -u workout bash -c 'cd /opt/workout-session-tracking && git checkout <previous-tag>'

# Option B: restore the DB from a SQLite snapshot
sudo -u workout cp /opt/workout-session-tracking/var/app-YYYY-MM-DD.db \
  /opt/workout-session-tracking/var/app.db

sudo systemctl start workout
curl -sf http://127.0.0.1:8000/healthz
```

---

## 13. Summary

After completing steps 1-10, you have:

| What                          | Where                                          |
|-------------------------------|-------------------------------------------------|
| App process                   | systemd `workout.service`                      |
| Reverse proxy + HTTPS         | nginx + certbot                                |
| Access protection             | nginx basic_auth (public: /healthz, /static)   |
| SQLite DB                     | /opt/workout-session-tracking/var/app.db       |
| Nightly backup (03:30 UTC)    | workout-backup.timer                           |
| Nightly verify (04:00 UTC)    | workout-backup-verify.timer                    |
| Backup files                  | /opt/workout-session-tracking/var/backups/      |
| Smoke test                    | scripts/smoke_deploy.sh                        |
| Strict health signal          | GET /healthz/strict                            |

The app is live. Open it on your phone via HTTPS, log a session,
and the journey begins.
