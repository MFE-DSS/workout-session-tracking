#!/usr/bin/env bash
# smoke_deploy.sh — minimal post-deploy validation.
#
# Run this ON THE VPS after completing the deploy procedure.
# Every check prints PASS or FAIL. The script exits 0 only if
# ALL checks pass.
#
# Usage:
#   sudo -u workout bash /opt/workout-session-tracking/scripts/smoke_deploy.sh
#
# Or with a custom base URL (defaults to http://127.0.0.1:8000):
#   BASE_URL=https://workout.example.com bash scripts/smoke_deploy.sh

set -euo pipefail

BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"
FAILS=0

check() {
    local label="$1"
    shift
    if "$@" >/dev/null 2>&1; then
        echo "  PASS  $label"
    else
        echo "  FAIL  $label"
        FAILS=$((FAILS + 1))
    fi
}

# Wait for the server to be ready (max 5 seconds).
echo "=== Waiting for server at ${BASE_URL} ==="
for i in 1 2 3 4 5; do
    if curl -sf "${BASE_URL}/healthz" >/dev/null 2>&1; then
        echo "  Server ready after ${i}s"
        break
    fi
    if [ "$i" -eq 5 ]; then
        echo "  FAIL  Server not reachable after 5s"
        exit 1
    fi
    sleep 1
done

echo ""
echo "=== Smoke deploy: ${BASE_URL} ==="
echo ""

# --- Offline backup refresh (runs first so /healthz/strict sees a
#     fresh JSON dump in /var/backups, otherwise it would return 503
#     "degraded — check backups" on a VPS where the systemd backup
#     timer has not produced a dump yet — Sb_16.5). ---

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"

# `python -m scripts.xxx` needs the CWD to be the repo root so
# the `scripts/` package is importable. Pipeline SSH invocations
# land in the remote home dir (e.g. /home/deploy), so we force cd.
cd "${REPO_DIR}"

check "backup_sessions.py runs successfully" \
    "${REPO_DIR}/.venv/bin/python" -m scripts.backup_sessions

check "verify_backup.py returns OK" \
    "${REPO_DIR}/.venv/bin/python" -m scripts.verify_backup

# --- Public routes (expect 200) ---

check "GET /healthz returns 200" \
    curl -sf "${BASE_URL}/healthz"

check "GET /healthz/strict returns 200" \
    curl -sf "${BASE_URL}/healthz/strict"

check "GET /welcome returns 200" \
    curl -sf "${BASE_URL}/welcome"

check "GET /login returns 200" \
    curl -sf "${BASE_URL}/login"

check "GET /register returns 200" \
    curl -sf "${BASE_URL}/register"

# --- Private routes (expect 303 redirect to /login) ---

check_auth_redirect() {
    local label="$1"
    local path="$2"
    local code
    code=$(curl -s -o /dev/null -w '%{http_code}' "${BASE_URL}${path}" 2>/dev/null || echo "000")
    if [ "$code" = "303" ]; then
        echo "  PASS  $label"
    else
        echo "  FAIL  $label (got $code, expected 303)"
        FAILS=$((FAILS + 1))
    fi
}

check_auth_redirect "GET / requires auth" "/"
check_auth_redirect "GET /library requires auth" "/library"
check_auth_redirect "GET /science requires auth" "/science"
check_auth_redirect "GET /history requires auth" "/history"
check_auth_redirect "GET /progress requires auth" "/progress"
check_auth_redirect "GET /export requires auth" "/export"
check_auth_redirect "GET /export/sessions.json requires auth" "/export/sessions.json"
check_auth_redirect "GET /export/sessions.csv requires auth" "/export/sessions.csv"

# --- Offline schema drift (unrelated to backups, kept at the end). ---

check "check_alembic_drift returns OK" \
    "${REPO_DIR}/.venv/bin/python" -m scripts.check_alembic_drift

echo ""
if [ "$FAILS" -eq 0 ]; then
    echo "=== ALL CHECKS PASSED ==="
    exit 0
else
    echo "=== ${FAILS} CHECK(S) FAILED ==="
    exit 1
fi
