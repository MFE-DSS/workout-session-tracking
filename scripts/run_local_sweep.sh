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

# ── `Sb_OPS_LOCAL_SWEEP_ADAPTIVE_BATCH_01` — LE LOT S'ADAPTE, LE SWEEP ABOUTIT.
#
# CE QUI A ÉTÉ MESURÉ, sur quatre tranches consécutives :
#
#   TRAIN 1-C   115/139 lots  · arrêt à 1866 Mo pour 1852 de budget
#   TRAIN 1-D   140/140 lots  · abouti
#   TRAIN 1-E   113/140 lots  · arrêt à 1932 Mo pour 1772
#   POST_CONV   117/140 lots  · arrêt à 1936 Mo pour 1841
#
# Trois arrêts sur quatre, TOUS sans un seul test rouge. À chaque fois la même
# manœuvre à la main : lire le conseil imprimé, relancer avec un lot plus
# petit, ou finir la queue avec un runner improvisé. Le garde-fou protégeait
# la machine et laissait le travail inachevé.
#
# LA CAUSE N'EST PAS LE CODE TESTÉ. Le budget vaut 60 % de la mémoire
# DISPONIBLE au démarrage — 2397 Mo une semaine, 1772 la suivante, selon ce
# que l'éditeur et ses serveurs de langage occupent. Le pic d'un lot, lui, ne
# dépend pas de ce budget. Sur une machine chargée, la taille de lot par
# défaut devient donc inatteignable quoi que fasse le dépôt.
#
# CE QUE FAIT L'ADAPTATION : au lieu d'abandonner, le sweep HALVE le lot et
# REJOUE les mêmes fichiers. Le conseil qu'il imprimait, il l'applique.
#
# ⚠ IL RÉTRÉCIT, IL NE REGROSSIT JAMAIS. La pression mémoire d'un poste est
# monotone sur la durée d'un sweep : l'éditeur ne rend pas ce qu'il a pris.
# Regrossir rouvrirait l'arrêt qu'on vient de payer, et ferait osciller la
# taille de lot autour du seuil — plus de démarrages, pas moins d'arrêts.
#
# L'ABANDON SUBSISTE POUR LE SEUL CAS OÙ IL VEUT DIRE QUELQUE CHOSE : un lot
# d'UN fichier au-dessus du budget. Là, le coût vient de ce fichier, et aucun
# découpage n'y changera rien.
adaptations=0
i=0
while [[ "${i}" -lt "${TOTAL_FILES}" ]]; do
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
            kill -TERM "${pid}" 2>/dev/null
            wait "${pid}" 2>/dev/null

            # Le lot est toujours NOMMÉ : le coût dépend des fichiers autant
            # que de leur nombre, et un message qui dit seulement « réduire »
            # laisse chercher à l'aveugle.
            echo "" >&2
            echo "[local-sweep] lot ${batch_no} à ${rss_mb} Mo, budget ${SWEEP_BUDGET_MB} Mo." >&2
            echo "[local-sweep] fichiers du lot : ${batch[*]}" >&2

            # Le plancher n'est PAS la taille du lot : mesuré, un seul fichier
            # de cette suite coûte 1,3 Go. À un fichier, le découpage n'a plus
            # rien à donner — c'est le fichier qu'il faut alléger.
            if [[ "${SWEEP_BATCH}" -le 1 ]]; then
                echo "[local-sweep] ARRÊT : lot déjà à 1 fichier. Le coût vient de CE" >&2
                echo "[local-sweep] fichier, pas du découpage. Le sweep s'arrête LUI-MÊME" >&2
                echo "[local-sweep] plutôt que de laisser l'OS choisir quel programme tuer." >&2
                echo "[local-sweep] SWEEP_BUDGET_MB=... pour l'admettre délibérément." >&2
                exit 3
            fi

            SWEEP_BATCH=$(( SWEEP_BATCH / 2 ))
            adaptations=$((adaptations + 1))
            batch_no=$((batch_no - 1))
            echo "[local-sweep] ADAPTATION ${adaptations} : lot ramené à ${SWEEP_BATCH}," >&2
            echo "[local-sweep] les mêmes fichiers sont rejoués. Aucun test n'est sauté." >&2
            continue 2
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
    # Le total de lots n'est plus connu d'avance : il dépend des adaptations.
    # Afficher une progression en FICHIERS reste exact quoi qu'il arrive.
    i=$(( i + SWEEP_BATCH ))
    printf '[local-sweep] lot %3d · %s · pic %4d Mo · %d/%d fichiers\n' \
        "${batch_no}" "${status}" "${batch_peak}" \
        "$(( i < TOTAL_FILES ? i : TOTAL_FILES ))" "${TOTAL_FILES}"
done

echo "[local-sweep] pic mémoire observé : ${peak_mb} Mo (budget ${SWEEP_BUDGET_MB} Mo)"
if [[ "${adaptations}" -gt 0 ]]; then
    echo "[local-sweep] ${adaptations} adaptation(s) : lot final ${SWEEP_BATCH}."
    echo "[local-sweep] Aucun fichier sauté — les lots réduits ont été rejoués."
fi
if [[ "${#failed_batches[@]}" -gt 0 ]]; then
    # ⚠ « LOTS EN ÉCHEC : 4 » se lit « quatre lots » alors que la ligne
    # imprime les NUMÉROS. Je l'ai moi-même mal lu une fois, et j'ai failli
    # rapporter un défaut inexistant. Le libellé le dit maintenant.
    echo "[local-sweep] NUMÉROS DES LOTS EN ÉCHEC : ${failed_batches[*]}" >&2
    exit 1
fi
echo "[local-sweep] tous les lots sont verts."
exit 0
