#!/usr/bin/env bash
# DA-GOV-01 — run the visual contract gate in the SAME pinned image as CI.
#
#   bash clients/mobile/visual-contract/run.sh test      # compare to the approved baselines
#   bash clients/mobile/visual-contract/run.sh approve   # OPERATOR ONLY: rewrite the baselines
#
# `approve` is the explicit operator action of docs/strategy/AUREN_VISUAL_CONTRACT.md §5:
# it rewrites the PNGs; the manifest must then be updated (sha256, approver, date)
# or tests/test_visual_contract_governance.py fails.
set -euo pipefail

IMAGE="mcr.microsoft.com/playwright:v1.63.0-noble@sha256:bc6ab0d6d44ff4826e4cb8c1e6d801e185bfc42bb0753f8e2a30efc70db054c7"
MODE="${1:-test}"
case "$MODE" in
  test) EXTRA="" ;;
  approve) EXTRA="--update-snapshots=all" ;;
  *) echo "usage: $0 test|approve" >&2; exit 2 ;;
esac

REPO="$(cd "$(dirname "$0")/../../.." && pwd)"
# node_modules lives in a named volume: Linux binaries never land in the macOS tree
docker run --rm --platform linux/amd64 \
  -v "$REPO":/work \
  -v auren-visual-contract-node-modules:/work/clients/mobile/node_modules \
  -w /work/clients/mobile \
  -e EXPO_PUBLIC_GALLERY=contract \
  "$IMAGE" \
  bash -c "npm ci --no-audit --no-fund \
    && npx expo export --platform web --output-dir dist-contract \
    && npx playwright test -c visual-contract/playwright.config.ts $EXTRA"
