# Sprint Sb_CUSTOM_PROGRAM_EKB_03 — EKB Classifiability QA — BUILD

**Statut** : 🟢 **PATCH COMPLETE / REVIEW PENDING** (non commité, non poussé, CI non lancée)
**Type** : CODE BUILD — **QA script + branchement CI**, zéro migration, zéro `app/`, zéro `data/`
**Date** : 2026-07-21
**Specs** : `Sx_CUSTOM_PROGRAM_02` §9 (les 8 checks QA) + §14 (build EKB_03 = QA classifiability CI-able)
**Branche** : `sb/custom-program-ekb-03-classifiability-qa` (worktree dédié, base `64ab789` — origin canonique, head Alembic `n5o0i6j7l98` inchangé)
**Préflight** : ✅ GO PATCH validé (arbitrages : gaps + trous noirs = warnings à compteur figé, dérive = erreur, invariances = erreurs dures, étape CI additive)

---

## 0. Étape 0 — Brainstorming / Options / Risques / Choix retenu

| Décision | Options | Choix retenu |
|---|---|---|
| Sémantique des 52 gaps / 19 trous noirs | erreurs dures · warnings à compteur figé | **warnings à compteur figé** (arbitrage) — cohérent avec la livraison EKB_02 (gaps délibérés) ; la CI reste verte, mais toute **dérive** du compteur (covered régressé, gap/trou noir surnuméraire) devient **erreur** |
| Invariances (noms, unicité, non-médical, traçabilité, complétude covered, closure, alias) | souples · dures | **erreurs dures (exit 1)** — ce sont les contrats non négociables du track |
| Patron du script | classe · fonctions `check_*` → (errors, warnings) | **fonctions** (patron `catalog_qa.py`), signature uniforme `(ekb, snapshot)`, dispatch trivial |
| Rapport | markdown fichier · stdout SUMMARY/ERRORS/WARNINGS | **stdout** (SUMMARY + ERRORS + WARNINGS) — surface de diff minimale, CI-lisible |
| Branchement CI | job séparé · étape dans le job pytest+QA | **étape additive** `python -m scripts.ekb_classifiability_qa` à côté de `catalog_qa`/`machine_atlas_qa` |

Tension centrale tranchée (préflight) : la spec §9-1 dit « le gap de 52 doit tomber à 0 », mais EKB_02
a livré 52 gaps délibérés. Un check dur les rendrait rouges en permanence → **warnings à compteur
figé** résout la contradiction sans exiger de curation non ouverte.

## 1. Patch appliqué

| Fichier | Nature |
|---|---|
| `scripts/ekb_classifiability_qa.py` | **nouveau** (~300 l.) — les **8 checks §9** (couverture, closure substitutions, complétude, invariance des noms, unicité, cohérence de groupe, non-médical, traçabilité) + check alias, lecture seule, SUMMARY/ERRORS/WARNINGS, exit 1 si erreur. Compteurs figés `EXPECTED_TOTAL/COVERED/GAP/BLACKHOLES = 103/51/52/19` |
| `tests/test_ekb_classifiability_qa.py` | **nouveau** — **14 tests** (succès + 11 cassures contrôlées) |
| `.github/workflows/ci.yml` | **modifié** (+3 l.) — étape `EKB classifiability QA` dans le job pytest+QA, additive |

**Zéro `data/` (lecture seule) · zéro `app/` · aucune migration (head `n5o0i6j7l98`) · aucune correction de gap, aucune curation, aucun `variant_group` rempli.**

## 2. Sortie du script (état actuel)

```
=== EKB classifiability QA (Sb_CUSTOM_PROGRAM_EKB_03) ===
SUMMARY : 0 erreur(s), 4 warning(s) attendue(s)
--- WARNINGS (attendues, compteur figé) ---
  · [couverture] 52 gaps de curation (état EKB_02 délibéré, curation = build ultérieur)
  · [complétude] 19 gaps sans zone dérivable (curation différée)
  · [groupe] variant_group null partout (V1) — cohérence vacuously true
  · [traçabilité] 19 trous noirs (confidence=todo, curation différée)
OK : toutes les invariances tiennent (warnings attendues).
```
**exit 0** (aucune erreur, seules les 4 warnings à compteur figé attendues).

## 3. Les 8 checks (§9) et leur classe

| # | Check | Classe |
|---|---|---|
| 1 | Couverture (103 entrées, gaps == 52 figé) | ERREUR sur entrée manquante/hors-snapshot/dérive · WARNING sur les 52 gaps |
| 2 | Closure substitutions (N1 + bridges → entrée ou alias) | ERREUR si nom cité inconnu |
| 3 | Complétude (covered ont pattern+equipment) | ERREUR pour les 51 covered · WARNING gaps sans zone |
| 4 | Invariance des noms (== snapshot, canonical_name == clé) | ERREUR |
| 5 | Unicité (canonical_name + variant_key) | ERREUR |
| 6 | Cohérence de groupe (variant_group partage pattern+zone) | ERREUR (vacuously true en V1, null partout) · WARNING |
| 7 | Non-médical (lexique interdit absent) | ERREUR |
| 8 | Traçabilité (confidence/coverage/zone fermés, trous noirs == 19 figé) | ERREUR sur enum/dérive · WARNING sur les 19 trous noirs |

(+ check alias : chaque alias → entrée canonique existante, jamais lui-même une entrée.)

## 4. Tests et checks exécutés

| Suite / check | Résultat |
|---|---|
| Dédiés (`test_ekb_classifiability_qa.py`) | **14/14 premier coup** (2 succès + 12 cassures contrôlées : renommage, suppression, doublon variant_key, covered incomplet, gap surnuméraire, trou noir surnuméraire, alias cassé, alias promu en entrée, lexique médical, closure cassée, groupe incohérent) |
| Non-régression EKB_01+EKB_02 (`test_ekb_coverage` + `test_exercise_knowledge_base`) | **13 + 19 = 32/32** → total **46/46** |
| `ekb_classifiability_qa` / `ekb_coverage_qa` | exit 0 |
| ruff (2 fichiers py neufs) | clean |
| `check_ruff_budget` | **543 ≤ 548** |
| `check_spec_protocol` | PASS |
| **`check_scope`** | **CI_INFRA** (`scripts/**` + `.github/workflows/**`) — full sweep local requis + validation CI réelle impérative |
| **Full sweep local** | **2491 passed / 0 failed** (15:11) — 100 % vert pré-commit (aucun modèle/migration touché, garde-fou arbre-sale passant) |

## 5. Risques résiduels

Le compteur figé (52/19) devra être **mis à jour explicitement** par un futur build de curation
qui comblera des gaps (le check protège précisément contre une dérive **silencieuse**) · l'étape CI
est bloquante pour le job pytest+QA (attendu : c'est un gate) mais additive (n'affecte pas lint/
Sonar) · double emploi partiel avec les tests pytest — l'apport distinct est le **script exit-code
CI-able** (un test pytest ne bloque pas comme un script QA dédié) et la consolidation des 8 checks
en un artefact unique.

## 6. Confirmations de périmètre

✅ Zéro `data/` (lecture seule) · ✅ zéro `app/` · ✅ aucune migration (head `n5o0i6j7l98`) · ✅
aucun seed/API/UI/scoring/wizard · ✅ aucune correction de gap, aucune curation, aucun `variant_group`
rempli · ✅ `data/exercise_knowledge_base.json` **intouché**.

---

## Verdict

**Verdict :** 🟢 **Sb_CUSTOM_PROGRAM_EKB_03 — PATCH COMPLETE / REVIEW PENDING.**

Les 8 checks QA de la spec §9 sont consolidés en un script CI-able (`scripts/ekb_classifiability_qa.py`),
branché dans la CI, avec la doctrine tranchée : invariances = erreurs dures, gaps/trous noirs =
warnings à compteur figé (dérive = erreur). 14 dédiés + 32 non-régression verts, exit 0 sur l'EKB
actuel. `EKB_04` (seed DB optionnel) = **NOT OPENED** · `SCORING_01`, `WIZARD_*` = **NOT OPENED**.
