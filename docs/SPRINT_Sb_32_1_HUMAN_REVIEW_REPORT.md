# Human Review — Sb_32.1 BodyZone + Muscle Foundation

**Verdict** : ✅ **HUMAN REVIEW ACCEPTED**
**Date** : 2026-07-08
**Type** : revue humaine — docs-only (aucun code touché)
**Cycle** : Sx_32 Deep Feature/Object Refactor (backend métier) — **in progress**
**Build report** : [`SPRINT_Sb_32_1_REPORT.md`](SPRINT_Sb_32_1_REPORT.md)

---

## 1. Décision

**Sb_32.1 est accepté.** La première brique relationnelle de la refonte métier
Sx_32 (objets `BodyZone` / `Muscle`) est livrée, la CI réelle est verte, et
l'invariance historique — contrainte #1 du cycle — est prouvée à trois niveaux
(migration additive + roundtrip, test schéma pré/post table-par-table, baseline
de non-régression `classify_exercise`).

Aucun consommateur n'a été migré : c'est **exactement** le périmètre attendu
pour `.1` (poser les objets sans basculer le comportement).

---

## 2. Preuve CI (run réel)

| Item | Valeur |
|---|---|
| **Commit** | `fa230fe1ad9a6c558b8303cf191f7d7abc98f9c3` |
| **Run** | [`28933861397`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/28933861397) |
| **Jobs** | ✅ **3/3 success** |
| `lint (ruff budget + bandit + actionlint + shellcheck)` | ✅ success |
| `pytest + QA scripts` | ✅ success |
| `SonarCloud` | ✅ success (scanner Java 21) |
| **Tests** | ✅ **1813 passed** (2 warnings, 20:30) |
| Ruff budget | ✅ 542 ≤ 548 |
| Alembic drift | ✅ OK (no diff) |
| Schema snapshot | ✅ matches alembic head |
| Migration patterns | ✅ no dangerous pattern |
| Migration roundtrip | ✅ clean |
| Spec protocol | ✅ pass |

---

## 3. Éléments acceptés (checklist)

| # | Élément | Statut |
|---|---|---|
| 1 | Sb_32.1 accepted | ✅ |
| 2 | CI verte run `28933861397` | ✅ |
| 3 | 1813 passed | ✅ |
| 4 | 3/3 jobs success | ✅ |
| 5 | Modèles `BodyZone` / `Muscle` (foundation) | ✅ accepté |
| 6 | Migration additive-only (`j1k6e2f3h54`, down `7i0f5d1e2g43`) | ✅ accepté |
| 7 | Backfill des 11 zones actuelles (dérivé des constantes `muscle_mapping`) | ✅ accepté |
| 8 | Table `muscles` vide V1 — **sans invention anatomique** | ✅ accepté |
| 9 | Baseline `classify_exercise` (91 exercices) figée + testée | ✅ accepté |
| 10 | `classify_exercise` **inchangé** | ✅ confirmé |
| 11 | **Aucun consommateur migré** (coach / body intelligence / scoring) | ✅ confirmé |
| 12 | Invariance historique préservée (contrainte #1) | ✅ confirmé |
| 13 | Étape **Brainstorming / Options / Risques / Choix retenu** documentée | ✅ acceptée comme **règle permanente** |
| 14 | Sb_32.2 **READY TO BE PROPOSED, not opened** | ✅ |
| 15 | Sb_32.3 / .4 **BLOCKED** | ✅ |
| 16 | Autres axes Tier 1 (readiness agg, identité exercice, substitution first-class) restent **backlog** | ✅ |
| 17 | Release tag **différé** | ✅ |

---

## 4. Règle permanente confirmée

À partir de maintenant, **chaque prompt de build significatif doit inclure une
étape « Brainstorming / Options / Risques / Choix retenu »**, documentée dans le
sprint report. Sb_32.1 est le premier sprint à l'appliquer (voir §0 de son build
report : Option A backfill migration retenue vs B `seed.py` interdit vs C `code`
PK non conventionnel ; sous-décision `muscles` vide V1 pour ne rien inventer).

---

## 5. Périmètre NON fait (par conception)

- `classify_exercise` **non basculé** vers un lookup DB (reste substring-matching).
- `muscles` **vide** (aucun mapping muscle→zone inventé).
- Aucun `ExerciseMuscleMapping`, aucun `body_map_descriptor`, aucune UI, aucun
  consommateur touché.

Ces éléments sont le contenu explicite des sous-sprints suivants, **review-gated**.

---

## 6. Suite du cycle Sx_32

| Sprint | État après cette revue |
|---|---|
| **Sb_32.1** | ✅ **HUMAN REVIEW ACCEPTED** |
| **Sb_32.2** ExerciseMuscleMapping + `classify_exercise` lookup/fallback | 🟡 **READY TO BE PROPOSED, not opened** — doit prouver la non-régression (`classify` old == new) contre la baseline `.1` avant tout basculement |
| **Sb_32.3 / .4** | ⏸️ **BLOCKED** (séquentiels, review-gated) — `body_map_descriptor` → migration consommateurs |
| Autres axes Tier 1 | 📋 backlog (readiness agg, identité exercice, substitution first-class) |
| Release tag | ⏸️ différé |

**Prochaine action** : ouvrir `Sb_32.2 ExerciseMuscleMapping + classify_exercise
lookup/fallback` (spec-then-build) **sur override explicite opérateur**, sous
garde de la baseline de non-régression. **Non ouvert dans ce commit.**

---

## 7. Verdict

**Verdict :** ✅ **Sb_32.1 BodyZone + Muscle Foundation — HUMAN REVIEW ACCEPTED.**

Fondation relationnelle posée, invariance historique prouvée, comportement métier
inchangé, CI réelle verte 3/3. Le cycle Sx_32 est **in progress**. `Sb_32.2` est
**prêt à être proposé, non ouvert**. Aucun code touché par cette revue.
