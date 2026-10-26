#!/usr/bin/env bash
# Runs INSIDE the pinned Playwright image (run.sh), cwd = clients/mobile, with
# node_modules on the named volume `auren-visual-contract-node-modules`.
#
# Why this exists: on that volume, under amd64 emulation, `npm ci` failed one pass in
# two — tar entries went missing, yet npm exited 0, and the export then found no
# `expo`. So: reuse an install that matches the lock exactly, VERIFY every install
# with `npm ls` instead of trusting npm's exit code, and retry from an emptied
# node_modules when the check fails.
set -euo pipefail

STAMP="node_modules/.auren-lock"

if [ -f "$STAMP" ] && cmp -s package-lock.json "$STAMP" && npm ls --depth=0 >/dev/null 2>&1; then
  echo "visual-contract: dependencies match package-lock.json — npm ci skipped"
  exit 0
fi

for attempt in 1 2 3; do
  # empty the volume's content (the mount point itself cannot be removed)
  find node_modules -mindepth 1 -maxdepth 1 -exec rm -rf {} +
  if npm ci --no-audit --no-fund && npm ls --depth=0 >/dev/null 2>&1; then
    cp package-lock.json "$STAMP"
    echo "visual-contract: dependencies installed and verified (attempt $attempt)"
    exit 0
  fi
  echo "visual-contract: install incomplete on attempt $attempt — retrying from an empty node_modules" >&2
done

echo "visual-contract: dependencies could not be installed after 3 attempts" >&2
exit 1
