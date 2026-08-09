# SPRINT Sb_FULL_BODY_MORPHOTYPE_PRIORITY — Ajout catalogue contrôlé (RAPPORT)

**Base canonique :** `efc10c2` · **Branche :** `sb/full-body-morphotype-priority` · **Tier :** ISOLATED (**data catalogue + tests + docs ; 0 modèle, 0 migration**)
**Doc programme :** [`FULL_BODY_MORPHOTYPE_PRIORITY_PROGRAM.md`](strategy/FULL_BODY_MORPHOTYPE_PRIORITY_PROGRAM.md)
**Livré sous le protocole agentique** (`CLAUDE.md §4`) : `GO BUILD` → Phase 0 → **STOP + arbitrage** → autonome jusqu'à `PR GREEN / MERGE PENDING`.

## 1. Résumé du changement

Ajout d'**un nouveau programme catalogue** « **Full Body — Morphotype Priority** » (section `specialization`, slug `full-body-morphotype-priority-v1`) comme **ajout additif** à `data/reference_split.json`. Aucune refonte : cartes exercice, mode session, save→next, historique, prévu/réalisé, no-JS, SSR/mobile **inchangés**. 0 modèle, 0 migration, 0 nouvelle table, 0 champ ajouté.

## 2. Brainstorming / Options / Risques / Choix retenu (CLAUDE.md §3)

**Phase 0 (inspection) = STOP + arbitrage.** L'inspection (sous-agent + lectures) a révélé un **couplage architectural** : le catalogue est un **référentiel fermé** — l'ensemble des noms (prescrits ∪ substituts) est verrouillé aux **103 noms canoniques EKB** (snapshot opposable checké des deux côtés + QA CI). Les noms/substituts anglais spécifiés par la mission n'y sont **pas** → ajout « tel quel » **casserait la CI** (drift snapshot, closure EKB `exit 1`, compteurs gelés).

| Option | Verdict |
|---|---|
| **A** — mapper sur les **noms EKB existants** (préservant l'intention), re-baseline des compteurs dérivés | ✅ **RETENU (opérateur)** — 0 expansion EKB, 0 modèle, 0 migration ; blast radius minimal |
| **B** — garder les noms anglais en **étendant l'EKB** (curation + snapshot + compteurs de couverture) | ✗ touche le référentiel partagé, adjacent à la curation EKB différée, proche d'une « refonte » interdite |
| **C** — documenter sans ajouter au catalogue runtime | ✗ programme non lançable |

**Risques traités** :
1. **Classification `unknown`** (test CI-bloquant #9) → chaque nom EKB choisi classe vers la zone d'intention (`classify_exercise`, match mots-clés). Ex. « Reverse **fly** machine » (delt_post) plutôt que « …pec deck inversé » (classerait `pecs`). *Testé.*
2. **Drift snapshot / closure EKB** → tous les noms (prescrits + substituts) ∈ 103 → union canonique **inchangée (103)** ; QA « invariances tiennent ». *Vérifié par `ekb_coverage_qa` + `ekb_classifiability_qa`.*
3. **Casse d'un template existant** → écriture par codegen déterministe (round-trip `json.dump` **fidèle à l'octet près**) ; diff = version + 1 template. *Testé (staples inchangés).*
4. **Compteurs gelés** → re-baseline **additif** (templates 16→17, slots 98→106, prescrits 65→68, substituts 59→66) — valeurs dérivées, pas des données historiques.

## 3. Fichiers modifiés (5 + docs)

| Fichier | Changement |
|---|---|
| `data/reference_split.json` | version `v13→v14` + **1 template** (8 exercices, noms EKB, substituts N1) ; existant intact |
| `tests/fixtures/ekb_names_snapshot.json` | `source_version` `v13→v14` (noms/count **inchangés**) |
| `tests/test_ekb_coverage.py` | compteurs dérivés re-baselinés (prescrits 68, substituts 66, templates 17, slots 106) |
| `tests/test_catalog_integrity_cleanup.py` | slug ajouté au set attendu (16→17) |
| `tests/test_full_body_morphotype_priority.py` (**neuf**) | 8 tests dédiés |
| docs | doc programme + ce rapport + registry + roadmap |
| **models / migrations / templates HTML / services / session_builder** | **aucun** |

## 4. Programme ajouté — exercices & sets

E1 Développé incliné haltères 30° (3×6-10) · E2 Rowing chest-supported (3×8-12) · E3 Hack Squat machine (2×6-10) · E4 Romanian Deadlift barre (2×6-10) · E5 Élévations latérales câble (4×12-20) · E6 Reverse fly machine (3×12-20) · E7 Relevés mollets debout machine (4×8-12) · E8 Mollets assis machine (3×12-20). Zones : pecs/upper_back/quads/posterior/delt_lat/delt_post/calves/calves. (détail + repos/intentions dans la doc programme.)

## 5. Substitutions

**N1 (intégrées `substitutes`)** par exercice (équivalents stricts, noms EKB — préservent l'intention ; jamais dips par défaut sur E1). **N2/N3 documentés** dans la doc programme (le modèle `substitutes` est un N1 curaté plat ; N2/N3 dérivés = moteur `substitution.py` existant, **inchangé**).

## 6-7. Tests lancés & résultat

- **Test dédié** `tests/test_full_body_morphotype_priority.py` — **8 passés** (présence catalogue · ordre E1-E8 · sets/reps · zones d'intention · substituts curatés · **session créée + page rendue** via le pipeline existant · **8 cartes** · additif/staples inchangés).
- **EKB/catalogue** (`ekb_coverage` · `catalog_integrity` + `_cleanup` · `ekb_classifiability_qa` · `exercise_knowledge_base` · `user_program_exercise_catalog`) — **77 passés** après re-baseline.
- **QA scripts** `ekb_coverage_qa` + `ekb_classifiability_qa` — **« toutes les invariances tiennent »**.
- **Broad sweep** (session_builder/flow/management · library · catalog · muscle_mapping · generator) — **115 passés** (0 régression).
- check_scope **ISOLATED** · `ruff` clean · budget **543 ≤ 548** · spec PASS.

## 8. Non-régressions vérifiées

Templates existants (push/pull/legs/liss/short/catch-up/upper-lower) **non modifiés** (slugs + shapes intacts) · générateur déterministe **inchangé** (nouveau slug hors `_SPLIT_CYCLES`) · référentiel EKB **103 inchangé** (pas de drift) · substitution N1/N2/N3 **inchangée** · cartes/mode session/save→next **inchangés**.

## 9. Points non faits volontairement

- **Pas d'expansion EKB** (Option B rejetée) → les noms sont les noms EKB existants, pas les noms anglais crafted.
- **N2/N3 documentés, non ajoutés** au catalogue (pas de nouveau moteur).
- **Repos/intent/zones en `notes`/doc** (pas de colonne ajoutée, pas de migration).
- **Pas de logique spéciale « Martin »** en code : programme catalogue générique, données perso restent dans la doc/blueprint.

## Prochaines étapes éventuelles

- Si l'on veut les noms anglais crafted ⇒ build séparé d'**expansion EKB** (sur GO).
- Intégration future au pipeline `Sx_MORPHO_PROGRAM` (slot intent / générateur) — hors ce sprint.

## Verdict

**Verdict :** ✅ **Sb_FULL_BODY_MORPHOTYPE_PRIORITY — MERGED + CANONICAL CI GREEN.** Programme catalogue **additif** livré (8 exercices, section specialization), lançable via le **pipeline session existant**, **0 modèle/migration/refonte**, référentiel fermé préservé (mapping noms EKB, Option A opérateur), non-régressions vérifiées.

---

## Appendice post-merge (closeout)

- **Merge** : PR **#62 MERGED** 2026-08-09, build `22e1f27` + fix Gitar E6 `dfcb7f2`, merge commit **`3e0dcf1`** via `--merge --match-head-commit dfcb7f2` — **sans squash, sans `--admin`** (gate `CLEAN`, 0 thread). `GO BUILD` → **STOP+arbitrage (Option A)** → PATCH Gitar → `GO MERGE`.
- **CI canonique** : run **`31326910791`** 3/3 GREEN sur `3e0dcf1` (lint · pytest+QA · SonarCloud) ; **coverage main 91.3 %** (data/tests, 0 code prod).
- **Finding Gitar E6 (résolu in-scope)** : le substitut « Rear delt fly machine (pec deck inversé) » contient « pec deck » → `classify_exercise` le classait en `pecs` avant `delt_post`. Comme un nom substitué remonte au scoring (`actual_exercise_name → classify_exercise`), un swap aurait attribué le volume aux pectoraux au lieu des delts postérieurs. Substituts E6 remappés en noms EKB classant `delt_post` (Face pull câble/corde, Écarté arrière) ; clôture 103 préservée, compteurs inchangés.
- **Cleanup** : branche `sb/full-body-morphotype-priority` (locale + remote) + worktree `workout-session-tracking-morphotype-program` supprimés au closeout (GO cleanup inclus).
- **Points non faits (volontaire)** : pas d'expansion EKB (noms EKB existants) ; N2/N3 documentées non ajoutées ; pas de logique « Martin » en code.
