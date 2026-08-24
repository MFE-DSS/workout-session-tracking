#!/usr/bin/env bash
# run_local_sweep.sh — LE full sweep LOCAL (Sb_OPS_LOCAL_SWEEP_MEMORY_01).
#
# POURQUOI CE SCRIPT EXISTE
# --------------------------
# `run_ci_pytest.sh` est la reproduction fidèle de la CI, et doit le rester.
# Mais lancée sur un poste de développement, elle a **fait tomber la machine de
# l'opérateur à répétition** : VS Code tué, conteneurs emportés, sweep jamais
# terminé. Ce n'est pas un garde-fou, c'est une panne.
#
# LA CAUSE, MESURÉE
# ------------------
# `run_ci_pytest.sh` plafonne déjà les workers sur la RAM physique, à raison de
# ~5 Go par worker. Sur une machine de 16 Go cela autorise 2 workers — et c'est
# précisément ce qui sature, parce que **le calcul suppose la machine dédiée au
# sweep**. Elle ne l'est jamais : VS Code, ses serveurs de langage et un
# navigateur en occupent déjà plusieurs gigaoctets.
#
# S'y ajoute une croissance MONOTONE : un même interpréteur qui enchaîne ~5 200
# tests accumule graphe applicatif importé, métadonnées SQLAlchemy, fixtures et
# traceur de couverture. Le pic n'est pas le coût d'un test, c'est le cumul de
# tous.
#
# CE QUE CE SCRIPT FAIT AUTREMENT
# --------------------------------
# 1. **Il découpe la suite en lots**, chacun exécuté dans un processus pytest
#    NEUF. Le pic mémoire redevient celui d'UN lot, pas de la suite entière, et
#    il est donc borné par construction plutôt que par une multiplication
#    optimiste.
# 2. **Pas de couverture par défaut.** `--cov` change le profil mémoire ET la
#    durée ; la couverture sert à Sonar, c'est-à-dire à la CI. En local on
#    cherche des régressions, pas un rapport. `--with-coverage` la réactive.
# 3. **Un chien de garde mémoire.** La RSS de l'arbre pytest est échantillonnée
#    pendant le lot ; au-delà du budget, on ARRÊTE avec un message clair plutôt
#    que de laisser l'OS choisir quel programme tuer.
# 4. **La mémoire DISPONIBLE est lue au démarrage**, pas la mémoire physique :
#    c'est la seule qui dit ce qu'on peut réellement prendre.
#
# Usage :
#   bash scripts/run_local_sweep.sh                 # tout, par lots
#   bash scripts/run_local_sweep.sh --with-coverage # profil CI, plus lourd
#   SWEEP_BATCH=20 bash scripts/run_local_sweep.sh  # lots plus gros
#   SWEEP_BUDGET_MB=3000 bash scripts/...           # budget explicite
#
# Le code de sortie est non nul dès qu'un lot échoue. Rien ici ne peut rendre
# un échec vert.

set -uo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.." || exit 2

# ── refus net sur CI ────────────────────────────────────────────────────────
# La CI a son script, mesuré sur le runner. Deux chemins qui prétendent tous
# deux être « le sweep » est exactement la divergence que
# `Sb_OPS_INSTALL_AUTHORITY_01` vient de fermer côté dépendances.
if [[ -n "${CI:-}" ]]; then
    echo "[local-sweep] REFUS : sur CI, la commande est scripts/run_ci_pytest.sh." >&2
    exit 2
fi

# Taille de lot par défaut — MESURÉE, pas devinée.
#
# Premier essai à 12 fichiers : pics observés de 724 à 2896 Mo selon le lot.
# Le coût dépend donc des FICHIERS autant que de leur nombre — certains
# montent un client HTTP et une base par test. Le lot 20 a dépassé le budget
# et le chien de garde a arrêté le sweep, ce qui est le comportement voulu
# mais pas une façon de travailler.
#
# CE QUE LA MESURE PAR FICHIER A APPRIS, et qui change le raisonnement :
#
#   tests/test_training_preferences.py   1346 Mo   à lui seul
#   tests/test_training_state.py          697 Mo
#   tests/test_ui06_dedup.py              334 Mo
#   les trois EN LOT                     2157 Mo
#
# La somme individuelle (2377) est proche du lot (2157) : **la mémoire n'est
# pas rendue d'un fichier à l'autre dans un même processus**. La croissance est
# cumulative, et le PLANCHER du pic n'est donc pas la taille du lot mais le
# fichier le plus lourd — 1,3 Go à lui seul.
#
# Conséquence : réduire le lot aide, mais avec un rendement décroissant
# (6 → 2326 Mo, 3 → 2157 Mo). Quatre est le compromis mesuré ; descendre plus
# bas multiplie les démarrages sans gagner grand-chose.
SWEEP_BATCH="${SWEEP_BATCH:-4}"
WITH_COVERAGE=0
PYTEST_EXTRA=()
for arg in "$@"; do
    case "${arg}" in
        --with-coverage) WITH_COVERAGE=1 ;;
        *) PYTEST_EXTRA+=("${arg}") ;;
    esac
done

if ! [[ "${SWEEP_BATCH}" =~ ^[0-9]+$ ]] || [[ "${SWEEP_BATCH}" -lt 1 ]]; then
    echo "[local-sweep] REFUS : SWEEP_BATCH='${SWEEP_BATCH}' n'est pas un entier positif." >&2
    exit 2
fi

# ── budget mémoire : ce qui est DISPONIBLE, pas ce qui est installé ─────────
if [[ "$(uname -s)" == "Darwin" ]]; then
    _page="$(sysctl -n hw.pagesize 2>/dev/null || echo 16384)"
    _free_pages="$(vm_stat | awk '/Pages free/ {gsub("\\.","",$3); print $3}')"
    _inactive="$(vm_stat | awk '/Pages inactive/ {gsub("\\.","",$3); print $3}')"
    _avail_mb=$(( (_free_pages + _inactive) * _page / 1048576 ))
else
    _avail_mb="$(awk '/MemAvailable/ {print int($2/1024)}' /proc/meminfo 2>/dev/null || echo 0)"
fi

# On ne prend jamais tout le disponible — mais le plancher doit rester
# ATTEIGNABLE. Mesuré : le fichier de test le plus lourd coûte 1,3 Go à lui
# seul, donc aucun découpage ne descend en dessous. Un budget de 800 Mo
# arrêterait le sweep sur le premier lot venu et rendrait l'outil inutile,
# c'est-à-dire reproduirait le défaut qu'il corrige sous une autre forme.
#
# 60 % du disponible, plancher 1 600 Mo, plafond 4 Go.
_default_budget=$(( _avail_mb * 6 / 10 ))
[[ "${_default_budget}" -gt 4000 ]] && _default_budget=4000
[[ "${_default_budget}" -lt 1600 ]] && _default_budget=1600
SWEEP_BUDGET_MB="${SWEEP_BUDGET_MB:-${_default_budget}}"

# ⚠ PAS DE `mapfile` : macOS livre bash 3.2, où il n'existe pas. Le script
# doit tourner sur le poste où le problème se pose, pas sur une version de
# bash qu'on souhaiterait y trouver.
FILES=()
while IFS= read -r _f; do
    FILES+=("${_f}")
done < <(find tests -maxdepth 1 -name 'test_*.py' \
              ! -name 'test_v1_acceptance.py' | sort)
TOTAL_FILES="${#FILES[@]}"
if [[ "${TOTAL_FILES}" -eq 0 ]]; then
    echo "[local-sweep] REFUS : aucun fichier de test trouvé." >&2
    exit 2
fi

echo "[local-sweep] ${TOTAL_FILES} fichiers · lots de ${SWEEP_BATCH}"
echo "[local-sweep] mémoire disponible ${_avail_mb} Mo · budget par lot ${SWEEP_BUDGET_MB} Mo"
echo "[local-sweep] couverture : $( ((WITH_COVERAGE)) && echo activée || echo DÉSACTIVÉE )"

COV_ARGS=()
((WITH_COVERAGE)) && COV_ARGS=(--cov=app --cov-report=term --cov-append)

peak_mb=0
failed_batches=()
batch_no=0

for ((i = 0; i < TOTAL_FILES; i += SWEEP_BATCH)); do
    batch_no=$((batch_no + 1))
    batch=("${FILES[@]:i:SWEEP_BATCH}")

    # ── chien de garde : échantillonne la RSS de l'arbre pytest ─────────────
    # ⚠ `"${arr[@]}"` sur un tableau VIDE est une variable non liée en
    # bash 3.2 sous `set -u` — la forme `${arr[@]+…}` est la seule portable.
    pytest -q -p no:cacheprovider \
           ${COV_ARGS[@]+"${COV_ARGS[@]}"} \
           ${PYTEST_EXTRA[@]+"${PYTEST_EXTRA[@]}"} \
           "${batch[@]}" &
    pid=$!

    batch_peak=0
    while kill -0 "${pid}" 2>/dev/null; do
        rss_kb="$(ps -o rss= -g "$(ps -o pgid= -p ${pid} | tr -d ' ')" 2>/dev/null \
                  | awk '{s+=$1} END {print s+0}')"
        rss_mb=$(( rss_kb / 1024 ))
        [[ "${rss_mb}" -gt "${batch_peak}" ]] && batch_peak="${rss_mb}"
        if [[ "${rss_mb}" -gt "${SWEEP_BUDGET_MB}" ]]; then
            echo "" >&2
            echo "[local-sweep] ARRÊT : lot ${batch_no} à ${rss_mb} Mo, budget ${SWEEP_BUDGET_MB} Mo." >&2
            echo "[local-sweep] Le sweep s'arrête LUI-MÊME plutôt que de laisser l'OS" >&2
            echo "[local-sweep] choisir quel programme tuer." >&2
            # Nommer les fichiers : le coût dépend d'EUX autant que de leur
            # nombre, et « réduire SWEEP_BATCH » sans dire lesquels laisse
            # chercher à l'aveugle.
            echo "[local-sweep] fichiers du lot : ${batch[*]}" >&2
            echo "[local-sweep] relancer avec SWEEP_BATCH=$(( SWEEP_BATCH > 1 ? SWEEP_BATCH / 2 : 1 ))" >&2
            # Le plancher n'est PAS la taille du lot : mesuré, un seul fichier
            # de cette suite coûte 1,3 Go. Si le lot vaut déjà 1, c'est ce
            # fichier qu'il faut alléger, pas le découpage.
            if [[ "${SWEEP_BATCH}" -le 1 ]]; then
                echo "[local-sweep] lot déjà à 1 fichier : le coût vient de CE fichier," >&2
                echo "[local-sweep] pas du découpage. SWEEP_BUDGET_MB=... pour l'admettre." >&2
            fi
            kill -TERM "${pid}" 2>/dev/null
            wait "${pid}" 2>/dev/null
            exit 3
        fi
        sleep 1
    done
    wait "${pid}"
    rc=$?

    [[ "${batch_peak}" -gt "${peak_mb}" ]] && peak_mb="${batch_peak}"
    status="ok"
    if [[ "${rc}" -ne 0 ]]; then
        status="ÉCHEC(${rc})"
        failed_batches+=("${batch_no}")
    fi
    printf '[local-sweep] lot %2d/%d · %s · pic %4d Mo\n' \
        "${batch_no}" "$(( (TOTAL_FILES + SWEEP_BATCH - 1) / SWEEP_BATCH ))" \
        "${status}" "${batch_peak}"
done

echo "[local-sweep] pic mémoire observé : ${peak_mb} Mo (budget ${SWEEP_BUDGET_MB} Mo)"
if [[ "${#failed_batches[@]}" -gt 0 ]]; then
    echo "[local-sweep] LOTS EN ÉCHEC : ${failed_batches[*]}" >&2
    exit 1
fi
echo "[local-sweep] tous les lots sont verts."
exit 0
