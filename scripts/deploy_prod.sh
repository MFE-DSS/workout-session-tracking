#!/usr/bin/env bash
# deploy_prod.sh — Production deploy with safety checks.
#
# Automates: backup → pull → deps → migrate → seed → restart → verify.
# Aborts on any error. Never drops data.
#
# Usage (as root or with sudo):
#   sudo bash /srv/workout/scripts/deploy_prod.sh
#
# Or with a specific branch:
#   sudo DEPLOY_BRANCH=release/v2 bash /srv/workout/scripts/deploy_prod.sh
#
# Environment variables:
#   DEPLOY_BRANCH   — git branch to deploy (default: main)
#   APP_DIR         — application root (default: /srv/workout)
#   APP_USER        — system user owning the app + service (default: workout)
#   SERVICE_NAME    — systemd unit name (default: workout)
#   SKIP_BACKUP     — set to 1 to skip SQLite backup (not recommended)

set -euo pipefail

# ─── Configuration ────────────────────────────────────────────────
APP_DIR="${APP_DIR:-/srv/workout}"
APP_USER="${APP_USER:-workout}"
SERVICE_NAME="${SERVICE_NAME:-workout}"
DEPLOY_BRANCH="${DEPLOY_BRANCH:-main}"
SKIP_BACKUP="${SKIP_BACKUP:-0}"
SKIP_GIT_PULL="${SKIP_GIT_PULL:-0}"
VENV="${APP_DIR}/.venv"
PIP="${VENV}/bin/pip"
PYTHON="${VENV}/bin/python"
ALEMBIC="${VENV}/bin/alembic"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"

# ─── Helpers ──────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BOLD='\033[1m'
NC='\033[0m'

step()  { echo -e "\n${BOLD}▶ $1${NC}"; }
ok()    { echo -e "  ${GREEN}✓${NC} $1"; }
warn()  { echo -e "  ${YELLOW}⚠${NC} $1"; }
fail()  { echo -e "  ${RED}✗ $1${NC}"; }

die() {
    fail "$1"
    echo ""
    echo -e "${RED}${BOLD}Deploy FAILED at: $1${NC}"
    echo -e "Service state: $(systemctl is-active "${SERVICE_NAME}" 2>/dev/null || echo 'unknown')"
    echo ""
    echo "Rollback hints:"
    echo "  1. If migration failed:  sudo -u ${APP_USER} ${ALEMBIC} downgrade -1"
    echo "  2. If code is bad:       sudo -u ${APP_USER} bash -c 'cd ${APP_DIR} && git checkout HEAD~1'"
    echo "  3. Restart previous:     sudo systemctl restart ${SERVICE_NAME}"
    if [ -n "${SQLITE_BACKUP:-}" ] && [ -f "${SQLITE_BACKUP}" ]; then
        echo "  4. Restore SQLite:     sudo cp '${SQLITE_BACKUP}' '${APP_DIR}/var/workout.db'"
    fi
    exit 1
}

# ─── Preflight ────────────────────────────────────────────────────
step "Preflight checks"

[ -d "${APP_DIR}" ]          || die "APP_DIR not found: ${APP_DIR}"
[ -f "${PYTHON}" ]           || die "Python venv not found: ${PYTHON}"
[ -f "${APP_DIR}/.env" ]     || die ".env not found — first deploy not done?"

# Load DATABASE_URL to detect SQLite vs PostgreSQL
if [ -f "${APP_DIR}/.env" ]; then
    DB_URL="$(grep -i '^DATABASE_URL=' "${APP_DIR}/.env" | head -1 | cut -d= -f2- || echo "")"
fi
DB_URL="${DB_URL:-sqlite:///./var/workout.db}"

IS_SQLITE=0
if echo "${DB_URL}" | grep -qi '^sqlite'; then
    IS_SQLITE=1
    ok "Database: SQLite"
else
    ok "Database: PostgreSQL"
fi

ok "App dir: ${APP_DIR}"
ok "Branch: ${DEPLOY_BRANCH}"
ok "Service: ${SERVICE_NAME}"

# ─── Record pre-deploy state ─────────────────────────────────────
step "Recording pre-deploy state"

cd "${APP_DIR}"
# Sb_OPS_DEPLOY_SAFETY_01 — prefer the SHA captured by the CI wrapper BEFORE it reset the working
# tree. Reading HEAD here would return the TARGET (the wrapper already checked it out), which made
# the recorded "previous" SHA useless for rollback. Manual runs, which do their own pull further
# down, keep the legacy behaviour.
PRE_SHA="${HOST_PRE_SHA:-$(sudo -u "${APP_USER}" git rev-parse HEAD 2>/dev/null || echo 'unknown')}"
ok "Previous commit (rollback target): ${PRE_SHA:0:12}"

# ─── SQLite backup ────────────────────────────────────────────────
SQLITE_BACKUP=""
if [ "${IS_SQLITE}" -eq 1 ] && [ "${SKIP_BACKUP}" != "1" ]; then
    step "Backing up SQLite database"

    # Sb_OPS_DEPLOY_SAFETY_01 — FAIL CLOSED. The path used to be hardcoded to
    # `${APP_DIR}/var/workout.db`; when DATABASE_URL pointed elsewhere the file was "not found",
    # the script only WARNED, and the deploy migrated with NO backup. Resolve the real file and
    # abort on any failure — never run Alembic without a verified snapshot.
    SQLITE_PATH="$(sudo -u "${APP_USER}" "${PYTHON}" \
        "${APP_DIR}/scripts/resolve_sqlite_path.py" \
        --database-url "${DB_URL}" --app-dir "${APP_DIR}")" \
        || die "Could not resolve a SQLite file from DATABASE_URL — refusing to migrate without a backup"

    [ -n "${SQLITE_PATH}" ] \
        || die "Empty SQLite path resolved from DATABASE_URL — refusing to migrate without a backup"
    [ -e "${SQLITE_PATH}" ] \
        || die "SQLite database not found at ${SQLITE_PATH} — refusing to migrate without a backup"
    [ -f "${SQLITE_PATH}" ] \
        || die "SQLite path ${SQLITE_PATH} is not a regular file — refusing to migrate without a backup"

    SQLITE_BACKUP="${APP_DIR}/var/backups/workout_pre_deploy_${TIMESTAMP}.db"
    mkdir -p "${APP_DIR}/var/backups" \
        || die "Cannot create backup directory ${APP_DIR}/var/backups"
    chown "${APP_USER}" "${APP_DIR}/var/backups" 2>/dev/null || true

    # sqlite3 .backup is WAL-consistent; cp is the fallback when sqlite3 is absent.
    if command -v sqlite3 &>/dev/null; then
        sudo -u "${APP_USER}" sqlite3 "${SQLITE_PATH}" ".backup '${SQLITE_BACKUP}'" \
            || die "sqlite3 backup FAILED for ${SQLITE_PATH} — aborting before migrations"
    else
        sudo -u "${APP_USER}" cp "${SQLITE_PATH}" "${SQLITE_BACKUP}" \
            || die "cp backup FAILED for ${SQLITE_PATH} — aborting before migrations"
    fi

    [ -s "${SQLITE_BACKUP}" ] \
        || die "Backup ${SQLITE_BACKUP} is missing or empty — aborting before migrations"

    BACKUP_SIZE="$(du -h "${SQLITE_BACKUP}" | cut -f1)"
    ok "SQLite backup: ${SQLITE_BACKUP} (${BACKUP_SIZE})"
    ok "Source database: ${SQLITE_PATH}"
elif [ "${SKIP_BACKUP}" = "1" ]; then
    warn "SQLite backup SKIPPED (SKIP_BACKUP=1)"
fi

# ─── Pull latest code ────────────────────────────────────────────
# When the CI/CD wrapper invokes this script, it has already checked out
# the exact target SHA, so we skip the pull entirely. Operators running
# the script manually keep the legacy pull-from-DEPLOY_BRANCH behaviour.
if [ "${SKIP_GIT_PULL}" = "1" ]; then
    step "Pulling latest code (skipped — caller already placed repo at target SHA)"
    # Sb_OPS_DEPLOY_SAFETY_01 — read the ACTUAL checked-out SHA. It used to be copied from
    # PRE_SHA, which is now the genuine previous SHA, so copying would report the wrong target.
    POST_SHA="$(sudo -u "${APP_USER}" git rev-parse HEAD 2>/dev/null || echo 'unknown')"
    ok "Target SHA: ${POST_SHA:0:12} (previous: ${PRE_SHA:0:12})"
else
    step "Pulling latest code"

    sudo -u "${APP_USER}" bash -c "
        cd '${APP_DIR}' &&
        git fetch origin &&
        git reset --hard 'origin/${DEPLOY_BRANCH}'
    " || die "git pull failed"

    POST_SHA="$(sudo -u "${APP_USER}" git -C "${APP_DIR}" rev-parse HEAD)"
    if [ "${PRE_SHA}" = "${POST_SHA}" ]; then
        warn "No new commits (already at ${POST_SHA:0:12})"
    else
        ok "Updated: ${PRE_SHA:0:12} → ${POST_SHA:0:12}"
        # Show what changed
        sudo -u "${APP_USER}" git -C "${APP_DIR}" log --oneline "${PRE_SHA}..${POST_SHA}" 2>/dev/null | head -10 | while read -r line; do
            echo "    ${line}"
        done
    fi
fi

# ─── Install dependencies ────────────────────────────────────────
step "Installing dependencies"

sudo -u "${APP_USER}" "${PIP}" install --quiet --upgrade pip 2>/dev/null || true
sudo -u "${APP_USER}" "${PIP}" install --quiet -r "${APP_DIR}/requirements.txt" \
    || die "pip install failed"
ok "Dependencies installed"

# ─── Alembic drift check ─────────────────────────────────────────
step "Checking schema drift"

sudo -u "${APP_USER}" bash -c "
    cd '${APP_DIR}' && '${PYTHON}' -m scripts.check_alembic_drift
" || die "Schema drift detected — fix before deploying"
ok "No schema drift"

# ─── Run migrations ──────────────────────────────────────────────
step "Running database migrations"

MIGRATION_OUTPUT="$(sudo -u "${APP_USER}" bash -c "
    cd '${APP_DIR}' && '${ALEMBIC}' upgrade head 2>&1
")" || {
    # Surface the captured stderr+stdout before dying so the GH Actions
    # log shows the actual sqlite/alembic error message. Without this
    # block the error is hidden inside a variable and never printed.
    echo "─── alembic upgrade output (last 80 lines) ───"
    echo "${MIGRATION_OUTPUT}" | tail -80
    echo "─── end alembic output ───"
    die "Alembic migration failed"
}

if echo "${MIGRATION_OUTPUT}" | grep -q "Running upgrade"; then
    echo "${MIGRATION_OUTPUT}" | grep "Running upgrade" | while read -r line; do
        ok "${line}"
    done
else
    ok "Database already at head"
fi

# ─── Seed catalog ────────────────────────────────────────────────
step "Seeding reference catalog"

sudo -u "${APP_USER}" bash -c "
    cd '${APP_DIR}' && '${PYTHON}' -m scripts.seed_db
" || die "Seed failed"
ok "Catalog seeded"

# ─── Verify DB connectivity ──────────────────────────────────────
step "Verifying database connectivity"

sudo -u "${APP_USER}" bash -c "
    cd '${APP_DIR}' && '${PYTHON}' -c '
from app.database import SessionLocal
from sqlalchemy import text
with SessionLocal() as db:
    db.execute(text(\"SELECT 1\"))
    print(\"DB connection OK\")
'
" || die "Database connectivity check failed"
ok "Database is reachable"

# ─── Restart service ──────────────────────────────────────────────
step "Restarting service"

systemctl restart "${SERVICE_NAME}" \
    || die "systemctl restart failed"

# Wait for service to become active
for i in 1 2 3 4 5; do
    if systemctl is-active --quiet "${SERVICE_NAME}"; then
        ok "Service active after ${i}s"
        break
    fi
    if [ "$i" -eq 5 ]; then
        # Show last logs for diagnosis
        journalctl -u "${SERVICE_NAME}" -n 20 --no-pager
        die "Service failed to start within 5s"
    fi
    sleep 1
done

# ─── Health check ─────────────────────────────────────────────────
step "Verifying health endpoint"

HEALTH_OK=0
for i in 1 2 3 4 5; do
    HTTP_CODE="$(curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8000/healthz 2>/dev/null || echo "000")"
    if [ "${HTTP_CODE}" = "200" ]; then
        HEALTH_OK=1
        ok "/healthz returned 200 after ${i}s"
        break
    fi
    sleep 1
done

if [ "${HEALTH_OK}" -eq 0 ]; then
    journalctl -u "${SERVICE_NAME}" -n 20 --no-pager
    die "/healthz not responding (last HTTP code: ${HTTP_CODE})"
fi

# ─── Strict health check (informational) ─────────────────────────
STRICT_CODE="$(curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8000/healthz/strict 2>/dev/null || echo "000")"
if [ "${STRICT_CODE}" = "200" ]; then
    ok "/healthz/strict returned 200 (fully healthy)"
else
    warn "/healthz/strict returned ${STRICT_CODE} (degraded — check backups)"
fi

# ─── Record deploy state (Sb_26.3) ───────────────────────────────
# Best-effort: writes var/deploy_state.json so /healthz/strict and
# scripts/prod_state_report.py can report the live SHA. Never fails
# the deploy if the writer hiccups.
step "Recording deploy state (Sb_26.3)"
sudo -u "${APP_USER}" "${PYTHON}" "${APP_DIR}/scripts/write_deploy_state.py" \
    --sha "${POST_SHA}" \
    --previous-sha "${PRE_SHA}" \
    --service "${SERVICE_NAME}" \
    --app-dir "${APP_DIR}" \
    --health "${HTTP_CODE:-unknown}" \
    --out "${APP_DIR}/var/deploy_state.json" \
    || warn "write_deploy_state.py failed — continuing (observability only)"

# ─── Summary ──────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}${BOLD}═══ Deploy successful ═══${NC}"
echo "  Commit:  ${POST_SHA:0:12}"
echo "  Branch:  ${DEPLOY_BRANCH}"
echo "  Service: $(systemctl is-active "${SERVICE_NAME}")"
if [ -n "${SQLITE_BACKUP}" ] && [ -f "${SQLITE_BACKUP}" ]; then
    echo "  Backup:  ${SQLITE_BACKUP}"
fi
echo "  Time:    $(date -Iseconds)"
echo ""
