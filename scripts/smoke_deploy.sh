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

echo "=== Smoke deploy: ${BASE_URL} ==="
echo ""

# 1. Liveness probe
check "GET /healthz returns 200" \
    curl -sf "${BASE_URL}/healthz"

# 2. Strict health
check "GET /healthz/strict returns 200" \
    curl -sf "${BASE_URL}/healthz/strict"

# 3. Home page renders
check "GET / returns 200" \
    curl -sf "${BASE_URL}/"

# 4. Library page renders
check "GET /library returns 200" \
    curl -sf "${BASE_URL}/library"

# 5. Rules page renders
check "GET /rules returns 200" \
    curl -sf "${BASE_URL}/rules"

# 6. History page renders
check "GET /history returns 200" \
    curl -sf "${BASE_URL}/history"

# 7. Progress page renders
check "GET /progress returns 200" \
    curl -sf "${BASE_URL}/progress"

# 8. Export landing page renders
check "GET /export returns 200" \
    curl -sf "${BASE_URL}/export"

# 9. JSON export downloadable
check "GET /export/sessions.json returns 200" \
    curl -sf "${BASE_URL}/export/sessions.json"

# 10. CSV export downloadable
check "GET /export/sessions.csv returns 200" \
    curl -sf "${BASE_URL}/export/sessions.csv"

# 11. Create a session (POST /sessions with push-a)
LOCATION=$(curl -sf -o /dev/null -w '%{redirect_url}' \
    -d "template_slug=push-a" "${BASE_URL}/sessions" 2>/dev/null || true)
if [ -n "$LOCATION" ]; then
    echo "  PASS  POST /sessions creates and redirects to ${LOCATION}"
else
    echo "  FAIL  POST /sessions did not redirect"
    FAILS=$((FAILS + 1))
fi

# 12. Session detail renders (if we got a location)
if [ -n "$LOCATION" ]; then
    check "GET session detail returns 200" \
        curl -sf "${LOCATION}"
fi

# 13. Manual backup run
REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
check "backup_sessions.py runs successfully" \
    "${REPO_DIR}/.venv/bin/python" -m scripts.backup_sessions

# 14. Backup verify
check "verify_backup.py returns OK" \
    "${REPO_DIR}/.venv/bin/python" -m scripts.verify_backup

# 15. Alembic drift guard
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
