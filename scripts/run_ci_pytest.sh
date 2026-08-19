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

# ---------------------------------------------------------------------------
# Sb_OPS_LOCAL_SWEEP_CEILING_01 — deux garde-fous MÉCANIQUES.
#
# Ils existent parce que la version en prose a échoué deux fois, différemment.
#
# 1. `auto` est REFUSÉ. Le workflow a déjà fixé `CI_PYTEST_WORKERS` à la chaîne
#    littérale `auto` : la variable était alors *définie*, le `:-2` ci-dessus ne
#    jouait jamais, et un « run de mitigation » est passé au vert sans exécuter
#    la mitigation. Rien ne le signalait à part une ligne de journal. Une valeur
#    non numérique doit arrêter le script, pas se propager à pytest.
#
# 2. En LOCAL, le nombre de workers est plafonné par la RAM réelle. La suite
#    consomme ~4,4 Mo par test et environ 16,6 Go au total ; `-n auto` sur un
#    poste de développement lance un worker par cœur, part en swap, et emporte
#    tout ce qui tourne à côté — conteneurs compris. C'est arrivé, sur le poste
#    de l'opérateur, trois fois de suite. Un sweep parallèle local saturé
#    produit en plus de FAUX échecs, qui passent tous en série : on se met alors
#    à chercher un défaut produit dans du bruit mémoire.
#
#    Sur CI (`CI=true`), la politique reste celle mesurée sur le runner et
#    n'est pas touchée : c'est là que le chiffre a été validé.
# ---------------------------------------------------------------------------
if ! [[ "${CI_PYTEST_WORKERS}" =~ ^[0-9]+$ ]]; then
    # Le message ne cite PAS l'argument interdit littéralement : une garde
    # préexistante (`test_the_canonical_runner_script_never_uses_auto`) scanne
    # les lignes EXÉCUTABLES de ce script et n'accepte le littéral que dans un
    # commentaire. Elle a raison — un `echo` est exécutable — et la première
    # version de ce garde-fou l'a fait rougir sur la CI.
    echo "[ci-pytest] REFUS : CI_PYTEST_WORKERS='${CI_PYTEST_WORKERS}' n'est pas un entier." >&2
    echo "[ci-pytest] La valeur speciale d'xdist est interdite ici : elle a deja rendu" >&2
    echo "[ci-pytest] une mitigation invisible, et elle sature un poste de developpement." >&2
    exit 2
fi

if [[ -z "${CI:-}" ]]; then
    # Poste local : plafonner sur la RAM physique, ~5 Go par worker.
    if [[ "$(uname -s)" == "Darwin" ]]; then
        _mem_bytes="$(sysctl -n hw.memsize 2>/dev/null || echo 0)"
    else
        _mem_bytes="$(( $(getconf _PHYS_PAGES 2>/dev/null || echo 0) * \
                        $(getconf PAGE_SIZE 2>/dev/null || echo 0) ))"
    fi
    _max_workers="$(( _mem_bytes / 5000000000 ))"
    [[ "${_max_workers}" -lt 1 ]] && _max_workers=1
    if [[ "${CI_PYTEST_WORKERS}" -gt "${_max_workers}" ]]; then
        echo "[ci-pytest] local : ${CI_PYTEST_WORKERS} workers ramenés à ${_max_workers}" >&2
        echo "[ci-pytest] (RAM physique $(( _mem_bytes / 1073741824 )) Go, ~5 Go par worker)" >&2
        CI_PYTEST_WORKERS="${_max_workers}"
    fi
fi

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
