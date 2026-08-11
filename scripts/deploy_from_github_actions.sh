#!/usr/bin/env bash
# Wrapper invoked over SSH by .github/workflows/deploy-production.yml.
#
# Receives the exact git SHA validated by CI, checks it out under the
# application user, then chains into the existing deploy_prod.sh which
# already handles backup, migrations, service restart and health checks.
#
# Invocation (from GitHub Actions, via SSH as the `deploy` user):
#   sudo /srv/workout/scripts/deploy_from_github_actions.sh <SHA>
#
# The `deploy` user has a sudoers entry restricted to this exact script
# path (see docs/CICD_RUNBOOK.md §2). Nothing else on the VPS is
# executable via that sudo grant.
#
# Exit codes:
#   0 — deploy succeeded; service is live on the requested SHA
#   2 — missing SHA argument
#   1 — any underlying step failed (git fetch, checkout, deploy_prod.sh)

set -euo pipefail

SHA="${1:-}"
if [[ -z "$SHA" ]]; then
  echo "[deploy] FATAL: SHA required as first argument" >&2
  exit 2
fi

# Fail early if the SHA looks obviously wrong. We don't validate against
# remote here — that happens during the fetch + checkout steps below.
if [[ ! "$SHA" =~ ^[0-9a-f]{7,40}$ ]]; then
  echo "[deploy] FATAL: '$SHA' does not look like a git SHA" >&2
  exit 2
fi

# These two values match the real VPS layout. Override via env vars if
# your install differs. They're also exported so deploy_prod.sh, which
# accepts APP_DIR and APP_USER as env vars since Sb_16.1, picks them up.
APP_DIR="${APP_DIR:-/opt/workout-session-tracking}"
APP_USER="${APP_USER:-ubuntu}"
# The wrapper has just done git fetch + reset --hard <SHA>, so the repo
# is already at the target SHA. Tell deploy_prod.sh to skip its own pull
# step — it would otherwise try to reset to origin/${DEPLOY_BRANCH}, which
# may or may not exist on this clone and is redundant with our reset.
SKIP_GIT_PULL=1
export APP_DIR APP_USER SKIP_GIT_PULL

if [[ ! -d "$APP_DIR/.git" ]]; then
  echo "[deploy] FATAL: $APP_DIR is not a git checkout" >&2
  exit 1
fi

cd "$APP_DIR"

# Sb_OPS_DEPLOY_SAFETY_01 — capture the TRUE rollback target BEFORE moving the working tree.
# Previously deploy_prod.sh read `git rev-parse HEAD` on its own, but by then this wrapper had
# already run `git reset --hard $SHA`, so its "PRE_SHA" was the target SHA and the real previous
# SHA was lost. Rollback then depended on tag archaeology. Exported so deploy_prod.sh and the
# deploy-state writer record the genuine previous SHA.
HOST_PRE_SHA="$(sudo -u "$APP_USER" git rev-parse HEAD 2>/dev/null || echo 'unknown')"
export HOST_PRE_SHA

echo "[deploy] previous SHA: $HOST_PRE_SHA   <-- rollback target"
echo "[deploy] target   SHA: $SHA"
echo "[deploy] app dir     : $APP_DIR"
echo "[deploy] app user    : $APP_USER"

echo "[deploy] step 1/3 — git fetch origin"
sudo -u "$APP_USER" git fetch --prune --tags origin

echo "[deploy] step 2/3 — git reset --hard $SHA"
sudo -u "$APP_USER" git reset --hard "$SHA"

echo "[deploy] step 3/3 — running scripts/deploy_prod.sh (as root — needs systemctl)"
# deploy_prod.sh is designed to run as root: it uses sudo -u "$APP_USER"
# internally for git / pip / alembic, and calls systemctl restart directly
# (which requires root privileges). APP_DIR / APP_USER / SKIP_GIT_PULL are
# already exported above so the child process inherits them.
bash "$APP_DIR/scripts/deploy_prod.sh"

echo "[deploy] OK — $SHA is live on $APP_DIR"
