# Sprint Sb_CUSTOM_PROGRAM_EKB_01 — Exercise Knowledge Base Foundation — BUILD

**Statut** : 🟢 **PATCH COMPLETE / REVIEW PENDING** (non commité, non poussé, CI non lancée)
**Type** : CODE BUILD — **audit + QA read-only** (spec 02 §14, premier build EKB) :
zéro migration, zéro `data/`, zéro `app/`, aucun EKB canonique créé
**Date** : 2026-07-19
**Specs** : `Sx_CUSTOM_PROGRAM_02` §3/§4/§9/§14 (référentiel de noms, invariance, QA, queue)
**Branche** : `sb/custom-program-ekb-01-foundation` (worktree dédié, base `e88865c` — origin canonique post-closeout PERSISTENCE_05, head Alembic `n5o0i6j7l98` inchangé)
**Préflight** : ✅ GO PATCH validé (arbitrage opérateur : snapshot dans `tests/fixtures/`, aucun `data/`)

---

## 0. Étape 0 — Brainstorming / Options / Risques / Choix retenu

| Décision | Options considérées | Choix retenu |
|---|---|---|
| Emplacement du snapshot | `data/` (patron reference data) · `tests/fixtures/` (patron `classify_exercise_baseline.json`) | **`tests/fixtures/ekb_names_snapshot.json`** (décision opérateur) — zéro toucher à `data/`, précédent exact de la baseline Sx_32 |
| Dépendances du script | importer `app.services.*` (patron `catalog_qa.py`) · stdlib pur | **stdlib pur** (json/pathlib/argparse) — évite structurellement le piège editable-install des worktrees (leçon PERSISTENCE_01) et garantit la lecture pure |
| Sémantique exit code | tout écart = erreur · gaps = rapport, invariances = erreurs | **gaps/orphelins = REPORTÉS (exit 0)**, invariances (unicité, clôtures, drift snapshot) = **erreurs (exit 1)** — les 52 gaps sont l'état connu qu'`EKB_02` doit fermer, pas un échec de l'audit |
| Vérification du snapshot | test-only · script + test | **les deux** : le script vérifie le snapshot committé à chaque run (drift → exit 1, CI-able), le test pinne en plus l'égalité live/fixture |
| Rapport de sortie | fichier markdown généré (patron `catalog_qa.py`) · stdout only | **stdout only** — la surface du diff reste exactement les 3 fichiers autorisés |
| Ordre du référentiel | ordre d'apparition · tri codepoint | **tri codepoint (`sorted()`)** — déterministe, identique à `jq unique`, stable pour la review |

Risque principal identifié : tier `ci_infra` mécanique (`scripts/**`) → full sweep local +
validation CI réelle impérative — assumé et exécuté.

## 1. Patch appliqué

| Fichier | Nature |
|---|---|
| `scripts/ekb_coverage_qa.py` | **nouveau** (~230 l.) — audit read-only : extraction déterministe du référentiel canonique (prescrits + substituts N1), couverture properties, orphelins, clôtures N1/bridges N3/baseline, vérification du snapshot committé, `--write-snapshot` (refuse `data/`), `--json`, exit 1 sur invariance cassée |
| `tests/fixtures/ekb_names_snapshot.json` | **nouveau** — snapshot opposable des **103 noms canoniques** byte-à-byte, tri codepoint, `source_version: 2026-04-21.v13`, zéro transformation |
| `tests/test_ekb_coverage.py` | **nouveau** — **13 tests**, listes exactes des 52 gaps et 2 orphelins embarquées |

**Aucun `app/`, aucun `data/`, aucune migration (head `n5o0i6j7l98`), aucun seed, aucune
table UserProgram*, aucun alias runtime, aucun `variant_key`/`variant_group` instancié.**

## 2. Chiffres mesurés (tous re-vérifiés sur l'arbre, pas hérités de la spec)

| Mesure | Valeur |
|---|---|
| Templates catalogue (`reference_split.json` v13) | **16** (sections core/utility/specialization/archived) |
| Slots d'exercices | **98** |
| Noms prescrits uniques | **65** |
| Substituts N1 distincts | **59** |
| Overlap prescrits∩substituts | **21** (65 + 59 − 21 = 103 ✓) |
| **Référentiel canonique** | **103 noms uniques** |
| Entrées `exercise_properties.json` (Sb_22a.v1.1) | **53** |
| Couverts | **51/103** |
| **Gaps properties** | **52** (liste nominative pinnée dans les tests) |
| **Properties orphelines** | **2** : `Incline DB Press 30°`, `Incline Dumbbell Press` |
| Noms cités par les bridges N3 | **12 — tous dans le référentiel** (clôture stricte OK) |
| Baseline classification Sx_32 | **91 entrées / 65 noms uniques, tous ⊆ référentiel** |

Découverte préflight confirmée : la spec (§3) annonçait le gap de 52 — exact — mais pas les
**2 orphelines** (anciennes graphies anglaises d'un développé incliné haltères, jamais
renommées). EKB_01 les **constate** ; leur sort (rattachement ou retrait) = décision
d'`EKB_02`, aucun renommage ici.

## 3. Mesuré / dérivé / inféré / non déductible

- **Mesuré** (fichiers existants) : les 103 noms, machines (25 slugs / 8 familles),
  53 properties (`pattern_motor`/`zone_primary`/`equipment_family`/`chain`), 11 zones,
  mappings Sx_32, bridges.
- **Dérivé déterministe** (ce build) : référentiel trié, couverture, gaps, orphelins,
  clôtures, snapshot.
- **Inféré (curation, ère EKB_02 — RIEN ici)** : stability, fatigue_class, difficulté,
  latéralité, setup, durée de slot, overload_compatibility, confidence.
- **Non déductible** : muscles fins (table `Muscle` vide V1, OQ-EKB-C), tout claim
  médical (interdit spec §2).

## 4. Tests et checks exécutés

| Suite / check | Résultat |
|---|---|
| Dédiés (`test_ekb_coverage.py`) | **13/13 premier coup** (1 fix ruff I001 d'import, zéro fix logique) |
| Script (`python -m scripts.ekb_coverage_qa`) | exit 0, snapshot vérifié, invariances OK |
| Adjacents (catalogue ×2, atlas ×2, substitution ×2, mapping, bodyzone, body-intelligence) | **146/146** |
| ruff (2 fichiers py neufs) | clean |
| `check_ruff_budget` | **543 ≤ 548** |
| `check_spec_protocol` | PASS |
| `check_scope` | **CI_INFRA** (`scripts/**`, conforme au préflight) — full sweep local exécuté + validation CI réelle impérative au push |
| **Full sweep local** | **2384 passed / 0 failed** (timer pytest 16:34 ; mur ~4h — process descheduled sous contention machine de 3 sessions parallèles, aucun impact sur le verdict) — **100 % vert pré-commit**, y compris le garde-fou arbre-sale (aucun modèle/migration touché) |

Couverture des 13 tests : extraction live == snapshot · 103/65/59 exacts · 16 templates /
98 slots · unicité + tri + byte-exactitude · gaps == liste exacte des 52 · orphelins == les 2 ·
clôture N1 · clôture bridges (12 noms) · cohérence baseline (91 entrées / 65 noms,
zéro mapping inventé) · déterminisme (2 runs identiques) · non-mutation des 4 sources
(sha256 avant/après) · exit 0 + sortie lisible · refus d'écrire sous `data/`.

## 5. Risques résiduels

Le référentiel dépend de la version v13 du catalogue — toute évolution future du catalogue
fera **volontairement** échouer le script (drift détecté = comportement voulu, jamais un
ajustement silencieux) · les 2 orphelines restent non résolues (décision EKB_02) · le
script n'est pas encore branché à la CI comme gate dédié (candidat naturel d'`EKB_03`,
les 8 checks complets de la spec §9).

## 6. Confirmations de périmètre

✅ Aucun `app/` · ✅ aucun `data/` modifié (lecture pure, refus d'écriture codé et testé) ·
✅ aucune migration (head `n5o0i6j7l98`) · ✅ aucun seed · ✅ `session_builder`/UI/wizard/
scoring/publication intacts · ✅ tables UserProgram* intactes · ✅ aucun renommage, aucun
alias runtime, aucune invention anatomique · ✅ `variant_key`/`variant_group` non instanciés.

---

## Verdict

**Verdict :** 🟢 **Sb_CUSTOM_PROGRAM_EKB_01 — PATCH COMPLETE / REVIEW PENDING.**

Le référentiel des 103 noms canoniques est extrait, opposable (snapshot + drift-check) et
gardé par 13 tests ; l'état de couverture est mesuré au nom près (52 gaps, 2 orphelines,
clôtures N1/N3/baseline prouvées). `EKB_02` (JSON canonique 103 entrées) = **FIRST NEXT
EKB BUILD CANDIDATE / NOT OPENED** · `EKB_03`/`EKB_04`, `SCORING_01`, `WIZARD_*` = **NOT
OPENED / NOT AUTHORIZED**.

---

## Appendice post-merge (closeout 2026-07-20)

- **Commit build** : `282a47f` (6 fichiers, +689) sur `sb/custom-program-ekb-01-foundation`,
  base `e88865c`.
- **PR #28 MERGED** — merge **`6345f5a`** sur le canonique.
- **CI canonique `29726786735` sur `6345f5a` : 3/3 GREEN** (pytest+QA · lint · SonarCloud).
- **CI PR finale 4/4 GREEN** — les 3 jobs **+ le quality gate externe « SonarCloud Code
  Analysis »**, première PR de code du track à passer ce gate.
- **Incident #1 (externe, résolu par refresh sans force)** : au premier run, la CI de la PR
  était rouge sur `check_spec_protocol` / `test_spec_protocol` — cause racine **hors branche
  EKB** : `docs/SPRINT_Sb_ASSET_01_1_GOVERNANCE_SCAFFOLD_HUMAN_REVIEW_REPORT.md` (poussé sur
  le canonique par la session ASSET en commit 100 % docs, donc sans CI) n'avait aucun
  marqueur de verdict. Après correction opérateur côté ASSET, la branche EKB a été
  **rafraîchie par merge du canonique (sans `--force`)** → merge `3ee5ff3` ; les 6 fichiers
  EKB sont restés inchangés hors intégration canonique.
- **Incident #2 (défaut réel du test, fix minimal)** : le quality gate externe a ensuite
  signalé un bug MAJOR `python:S5863` sur `tests/test_ekb_coverage.py` — le test de
  déterminisme comparait `run_audit() == run_audit()` (mêmes expressions). Corrigé en liant
  les deux runs à `first`/`second` avant comparaison (**commit `2f39db6`**) — même intention
  (deux appels distincts doivent concorder), sémantique préservée, 13/13 toujours verts.
- **Head Alembic canonique inchangé : `n5o0i6j7l98`** — EKB_01 est bien un build
  audit-only, zéro schéma / zéro `data/` / zéro `app/`.
