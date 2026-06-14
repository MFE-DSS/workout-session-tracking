#!/usr/bin/env bash
# Sb_26.4 — regenerate requirements-lock.txt from requirements.txt.
#
# Run this after every change to requirements.txt:
#   bash scripts/regen_lockfile.sh
#   git add requirements-lock.txt
#
# The lockfile is NOT yet used by deploy_prod.sh (would need explicit
# validation — see docs/SECURITY_BASELINE.md §5). It is consumed only
# by the CI freshness check in `.github/workflows/ci.yml`.

set -euo pipefail

cd "$(dirname "$0")/.."

if ! command -v pip-compile &>/dev/null; then
    echo "[regen_lockfile] pip-tools missing — installing"
    pip install --quiet pip-tools
fi

pip-compile \
    --strip-extras \
    --quiet \
    --output-file=requirements-lock.txt \
    requirements.txt

echo "[regen_lockfile] requirements-lock.txt regenerated ($(wc -l < requirements-lock.txt) lines)"
