#!/usr/bin/env bash
# run_ci_pytest.sh — THE canonical pytest+coverage invocation (Sb_OPS_CI_RUNNER_STABILITY_01).
#
# Single source of truth. The GitHub workflow calls this script; an operator
# reproducing CI locally calls the SAME script. "CI-identical" therefore has a
# machine-checkable meaning instead of being a claim someone has to remember.
#
# This exists because the claim drifted in practice: three local sweeps were
# reported as "CI-identical" while silently omitting `--cov`, which is exactly
# the flag that changes runtime and memory profile. A guard test now compares
# the workflow against this file, so the two cannot diverge again in silence.
#
# Usage:
#   bash scripts/run_ci_pytest.sh            # canonical worker policy
#   CI_PYTEST_WORKERS=2 bash scripts/...     # override worker count only
#
# The script forwards extra arguments to pytest, so a targeted local run can add
# `-k`, `-x`, or a path without editing this file — the canonical FLAGS stay put.
#
# Exit code is pytest's, unmodified. Nothing here may turn a real failure green.

set -uo pipefail

# Worker policy — BOUNDED, on measured evidence (Sb_OPS_CI_RUNNER_STABILITY_01, WS5).
#
# `-n auto` resolves to 4 workers on the hosted runner (4 CPU / 15 989 MB RAM),
# and the WS3 baseline showed that configuration exhausting the machine:
#
#   MemAvailable  14 773 MB → 40 MB      (monotonic decline across the run)
#   SwapFree       3 071 MB → 1 MB
#   Peak RSS      4 548 084 KB ≈ 4.34 GB
#   Disk free     88 744 → 88 173 MB     (never a constraint)
#
# That baseline passed with 40 MB of headroom. The three preceding runner
# shutdowns hit the same wall slightly harder — which is why they died late, at
# 95-96%, with no pytest failure and no timeout.
#
# Two workers halve the number of concurrent interpreters, each holding its own
# imported application graph and coverage tracer. Deliberately NOT one worker
# and NOT a job split: this is the smallest change that addresses the measured
# pressure, and the larger options stay available if evidence later demands them.
#
# The environment override remains so a future sprint can measure another value
# on real CI without editing this file.
CI_PYTEST_WORKERS="${CI_PYTEST_WORKERS:-2}"

# test_v1_acceptance.py exercises a local VSCode setup and is intentionally out
# of CI scope. Coverage is collected over `app/` (see pyproject [tool.coverage.run]);
# the XML report is what the SonarCloud sensor consumes.
CANONICAL_ARGS=(
    -n "${CI_PYTEST_WORKERS}"
    --dist worksteal
    --ignore=tests/test_v1_acceptance.py
    --cov=app
    --cov-report=xml
    --cov-report=term
    -q
)

echo "[ci-pytest] workers=${CI_PYTEST_WORKERS}"
echo "[ci-pytest] pytest ${CANONICAL_ARGS[*]} $*"

pytest "${CANONICAL_ARGS[@]}" "$@"
exit $?
