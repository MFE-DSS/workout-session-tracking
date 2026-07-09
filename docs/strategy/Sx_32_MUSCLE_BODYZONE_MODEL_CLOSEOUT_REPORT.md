# Sx_32 — Muscle/BodyZone Model Refactor — CLOSEOUT REPORT

**Verdict** : ✅ **Sx_32 TECHNICALLY CLOSED / FOUNDATION CLOSED**
**Date** : 2026-07-09
**Type** : closeout — docs-only (aucun code touché)
**Cycle** : premier cycle de **refonte profonde des features/objets backend** (métier)
**Spec** : [`Sx_32_MUSCLE_BODYZONE_MODEL_SPEC.md`](Sx_32_MUSCLE_BODYZONE_MODEL_SPEC.md) (HUMAN REVIEW ACCEPTED, `47f3fac`)

---

## 1. Verdict

Sx_32 est **clôturé comme fondation métier complète + premier consommateur UI**.
Le cycle a remplacé la dette « substring-matching hardcodé » (`muscle_mapping.py`)
par une **chaîne relationnelle formelle** — `BodyZone` → `Muscle` →
`ExerciseMuscleMapping` → `body_map_descriptor` — **branchée pour la première fois
dans l'UI** (Focus Mode / Worked Area), le tout **sans régression historique**
(invariance `classify_exercise` prouvée **91/91**) et **sans migrer aucun
consommateur métier lourd** (scoring / coach / body intelligence).

La bascule des consommateurs métier vers le lookup DB reste un chantier
**explicitement différé** (`Sb_32.4`), review-gated, sous garde de non-régression.

---

## 2. Périmètre livré

1. **Vocabulaire `BodyZone` formel** — 11 zones en base, backfillées **par
   dérivation** des constantes existantes (jamais recopiées).
2. **Modèle `Muscle`** — préparé, **vide V1** (aucune anatomie inventée).
3. **Relation `ExerciseMuscleMapping`** — exercice → zone (primary/secondary),
   backfill 87 lignes depuis la baseline `.1`.
4. **Lookup DB optionnel + fallback substring** — `classify_exercise(name, *,
   exercise_code=None, db=None)`, name-only **byte-identique** à l'ancien.
5. **Descriptor JSON stable** — `build_body_map_descriptor(...) -> dict` (10 clés,
   `resolution_path` honnête, unknown → « À qualifier »).
6. **Premier consommateur UI SSR/no-JS** — Worked Area affiche la zone réellement
   résolue (primary + assistants réels).
7. **Invariance historique 91/91** — prouvée sur les deux chemins (name-only + db).
8. **Aucune migration des consommateurs lourds** (par conception).
9. **Aucun changement** scoring / coach / body intelligence.
10. **Base prête** pour `Sb_32.4` (bascule consommateurs) ou un futur cycle Body
    Intelligence.

---

## 3. Sous-sprints (SHA + CI)

| Sous-sprint | SHA build | Statut | CI (run) |
|---|---|---|---|
| Spec Sx_32 | `47f3fac` | ✅ SPEC ACCEPTED | docs-only |
| Sb_32.1 BodyZone + Muscle Foundation | `fa230fe` | ✅ ACCEPTED | [`28933861397`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/28933861397) 3/3 · 1813 passed |
| Sb_32.2 ExerciseMuscleMapping + lookup/fallback | `00450c7` | ✅ ACCEPTED | [`29001421131`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/29001421131) 3/3 (attempt 2) · 1827 passed |
| Sb_32.3 body_map_descriptor | `63a4e74` | ✅ ACCEPTED | [`29010584067`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/29010584067) 3/3 · 1843 passed |
| Sb_32.next.worked-area-descriptor-ui | `9dd28a1` + fix `8559e8b` | ✅ ACCEPTED | [`29029149976`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/29029149976) 3/3 · 1865 passed |
| Sb_OPS.scope-guard (outillage transverse) | `a43ce85` | ✅ ACCEPTED | [`29015557948`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/29015557948) 3/3 |

Migrations additive-only : `j1k6e2f3h54` (BodyZone/Muscle) · `k2l7f3g4i65`
(ExerciseMuscleMapping). Aucun DROP/RENAME/UPDATE/DELETE historique. Snapshot à jour.

---

## 4. Invariants historiques préservés

- `classify_exercise(name)` **byte-identique** à l'avant-Sx_32 (baseline figée
  `tests/fixtures/classify_exercise_baseline.json`, 91 exercices).
- **DB lookup ET name-only == baseline 91/91** (0 divergence, les deux chemins).
- Aucun consommateur métier muté : les 7 callers de `classify_exercise` intacts.
- Migrations **additive-only** ; `muscles` vide ; `muscle_code` NULL (rien inventé).
- Contrats Focus Mode (logging / rest timer / substitution / overload) intacts.

---

## 5. Preuve que la fondation est visible dans Focus Mode

La route `session_detail` calcule un descriptor par exercice et le passe au
partial `exercise_card.html`. Sur la **carte active**, le Worked Area affiche :
- **Principal** : label de zone réel (ex. Chest Press → *Pectoraux*) ;
- **Assistants** : labels secondaires réels (ex. *Triceps*) ;
- **Unknown** : « À qualifier » (aucune zone inventée) ;
- `resolution_path` (db_lookup / substring_fallback / unknown) en `data-*` discret ;
- note prudente **non médicale**.
Rendu **SSR strict / no-JS**. Vérifié par 14 tests (`test_worked_area_descriptor.py`).

---

## 6. Dette explicitement différée

| Élément | Statut |
|---|---|
| Bascule consommateurs métier (coach / body intelligence / scoring) vers lookup DB | ⏸️ **`Sb_32.4`** — deferred, review-gated |
| Peuplement fin du modèle `Muscle` (anatomie) | 📋 backlog (sources explicites requises) |
| Rôle `stabilizer` dans le mapping | 📋 backlog (non inventé) |
| Body Intelligence consumer migration | 📋 backlog controlled |
| Substitution first-class / exercise identity / readiness aggregation (axes Tier 1) | 📋 backlog |
| `exercise_code` = slug propre (vs nom d'exercice) | 📋 backlog (si le catalogue introduit un id stable) |

---

## 7. Pourquoi Sb_32.4 est différé

La bascule des consommateurs métier (scoring/coach/body intelligence) vers le
lookup DB est le sprint à **plus haut risque** du cycle : il change le chemin de
données de fonctionnalités analytiques en production. Le cycle a délibérément posé
**toute la fondation prouvée non-régressive** d'abord (modèles + mapping +
descriptor + 1er consommateur UI en lecture seule), de sorte que `Sb_32.4` puisse
être ouvert **plus tard, isolément**, avec la baseline `.1` comme garde-fou strict
(`classify old == new`). Rien ne force son ouverture immédiate : la valeur produit
(Worked Area lisible) est déjà livrée sans toucher au métier.

---

## 8. Risques restants

- `exercise_code = name` : robuste tant que le catalogue n'a pas de slug propre ;
  documenté comme dette.
- En prod, le Worked Area utilise `db_lookup` (DB migrée) ; en test, `substring_fallback`
  (DB `create_all` sans backfill) — les deux donnent les **mêmes zones** (invariance).
- Le lookup DB n'est **pas** encore la source des consommateurs métier : tant que
  `Sb_32.4` n'est pas fait, scoring/coach/body intelligence restent sur le substring.

---

## 9. Prochain choix recommandé

1. **Merge de la branche** (recommandé) — la fondation + UI sont acceptées et CI
   vertes ; la valeur est livrable.
2. Puis, sur override séparé : **`Sb_32.4`** (bascule consommateurs) **ou** un
   **cycle Body Intelligence** consommant le descriptor, selon priorité produit.

---

## 9bis. Non-goals (hors périmètre de ce closeout)

Ce closeout **n'ouvre ni ne réalise** :
- la **bascule des consommateurs métier** (scoring / coach / body intelligence)
  vers le lookup DB — c'est `Sb_32.4`, explicitement différé ;
- le **peuplement fin du modèle `Muscle`** (anatomie) — backlog, sources requises ;
- le rôle **`stabilizer`** dans le mapping — backlog (non inventé) ;
- un **slug d'exercice propre** (l'identité reste `exercise_code = name`) — backlog ;
- tout **release tag** ou merge automatique — décision opérateur ;
- toute modification de **code / modèle / migration / schéma** — closeout docs-only.

---

## 10. Merge readiness

**READY AFTER HUMAN REVIEW / operator decision.**

Tous les sous-sprints sont HUMAN REVIEW ACCEPTED avec CI réelle verte 3/3. Aucune
migration destructive, aucun consommateur métier muté, invariance prouvée. La
branche `claude/sprint-reporting-fitness-app-V7Qr6` est **mergeable** sous réserve
de la décision opérateur.

---

## Verdict

**Verdict :** ✅ **Sx_32 TECHNICALLY CLOSED / FOUNDATION CLOSED.**

La refonte Muscle/BodyZone a livré une fondation relationnelle formelle
(BodyZone → Muscle → ExerciseMuscleMapping → body_map_descriptor) branchée pour
la première fois dans l'UI (Worked Area SSR/no-JS), **sans régression historique
(91/91)** et **sans migration des consommateurs métier**. `Sb_32.4` (bascule
consommateurs) est **prêt à être proposé, différé**. Branche **merge-ready** sous
décision opérateur. Aucun code touché par ce closeout.
