# Human Review — Sb_32.2 ExerciseMuscleMapping + classify_exercise lookup/fallback

**Verdict** : ✅ **HUMAN REVIEW ACCEPTED**
**Date** : 2026-07-09
**Type** : revue humaine — docs-only (aucun code touché)
**Cycle** : Sx_32 Deep Feature/Object Refactor (backend métier) — **in progress**
**Build report** : [`SPRINT_Sb_32_2_REPORT.md`](SPRINT_Sb_32_2_REPORT.md)

---

## 1. Décision

**Sb_32.2 est accepté.** La classification exercice→zone est désormais
**relationnelle** (`ExerciseMuscleMapping`) avec un chemin de lookup DB
**optionnel** et un fallback substring conservé. L'invariance historique —
contrainte #1 du cycle — est **prouvée 91/91** contre la baseline Sb_32.1, sur
les deux chemins (lookup DB **et** name-only). Aucun consommateur n'est migré :
c'est exactement le périmètre attendu pour `.2`.

---

## 2. Preuve CI (run réel)

| Item | Valeur |
|---|---|
| **Commit** | `00450c717168b0b2f14b1e453d0ec23c8f589e54` |
| **Run** | [`29001421131`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/29001421131) — **attempt 2** |
| **Jobs** | ✅ **3/3 success** |
| `lint (ruff budget + bandit + actionlint + shellcheck)` | ✅ success |
| `pytest + QA scripts` | ✅ success |
| `SonarCloud` | ✅ success |
| **Tests** | ✅ **1827 passed** (2 warnings, 20:45) |
| Ruff budget | ✅ 541 ≤ 548 |
| Alembic drift | ✅ OK (no diff) |
| Schema snapshot | ✅ matches alembic head |
| Migration patterns | ✅ no dangerous pattern |
| Migration roundtrip | ✅ clean |
| Spec protocol | ✅ pass |

---

## 3. Éléments acceptés (checklist)

| # | Élément | Statut |
|---|---|---|
| 1 | Sb_32.2 accepted | ✅ |
| 2 | CI verte run `29001421131` attempt 2 | ✅ |
| 3 | 1827 passed | ✅ |
| 4 | 3/3 jobs success | ✅ |
| 5 | Modèle `ExerciseMuscleMapping` | ✅ accepté |
| 6 | Migration additive-only `k2l7f3g4i65` (down `j1k6e2f3h54`) | ✅ accepté |
| 7 | Backfill **87 lignes** (65 primary + 22 secondary) | ✅ accepté |
| 8 | `exercise_code = name` comme identité stable V1 | ✅ accepté |
| 9 | Lookup DB **optionnel** | ✅ accepté |
| 10 | Fallback substring conservé | ✅ accepté |
| 11 | `classify_exercise(name)` **inchangé** en name-only | ✅ accepté |
| 12 | Équivalence **91/91** contre la baseline Sb_32.1 | ✅ accepté |
| 13 | **Aucun consommateur migré** (7 callers intacts) | ✅ confirmé |
| 14 | **Aucune UI / endpoint / JS / rebrand** | ✅ confirmé |
| 15 | Annulation SonarCloud attempt 1 = bruit infra, résolue par re-run | ✅ documentée |
| 16 | Sb_32.3 `body_map_descriptor` **READY TO BE PROPOSED, not opened** | ✅ |
| 17 | Sb_32.4 **BLOCKED** | ✅ |
| 18 | Release tag **différé** | ✅ |

---

## 4. Note CI — annulation SonarCloud (attempt 1), résolue

L'attempt 1 du run `29001421131` était rouge **uniquement** à cause du job
**SonarCloud `cancelled`** — pas `failure` : 0 step enregistré, 0 log
(`BlobNotFound` sur l'API logs), ~15 min alors que `timeout-minutes: 10`. Les
jobs `lint` et `pytest + QA scripts` étaient **déjà verts** à l'attempt 1
(1827 passed). `.github/` **n'est pas touché** par Sb_32.2. Diagnostic : **bruit
d'infrastructure côté SonarCloud** (annulation / timeout runner), sans lien avec
le code.

**Résolution** : re-run des jobs échoués seuls (`rerun-failed-jobs`), **sans
nouveau commit, sans `[skip ci]`, sans skip-checks**. Le SonarCloud a repassé
vert du premier coup à l'**attempt 2** → run global `success`. (Contrainte
annexe : DNS système local cassé pendant l'épisode, contourné par résolution
API par IP ; la CI côté GitHub n'a jamais été affectée.)

---

## 5. Périmètre NON fait (par conception)

- **Aucun consommateur migré** vers le lookup DB (les 7 callers appellent
  toujours `classify_exercise(name)`, name-only, inchangé).
- Lookup DB **non branché en prod** — il existe et est prouvé équivalent, mais
  personne ne le consomme encore.
- `muscles` toujours vide ; `muscle_code` NULL ; rôle `stabilizer` non peuplé
  (aucune anatomie inventée).
- Aucune UI (Worked Area), aucun `body_map_descriptor`.

Ces éléments sont le contenu explicite des sous-sprints suivants, **review-gated**.

---

## 6. Suite du cycle Sx_32

| Sprint | État après cette revue |
|---|---|
| **Sb_32.1** | ✅ HUMAN REVIEW ACCEPTED (2026-07-08) |
| **Sb_32.2** | ✅ **HUMAN REVIEW ACCEPTED** (2026-07-09) |
| **Sb_32.3** `body_map_descriptor` | 🟡 **READY TO BE PROPOSED, not opened** — contrat de service (agrégation zone→descripteur) consommable UI Worked Area + coach, s'appuyant sur `ExerciseMuscleMapping` |
| **Sb_32.4** | ⏸️ **BLOCKED** — migration consommateurs (coach/body_intel/scoring) vers lookup DB, prouvée non-régressive |
| Autres axes Tier 1 | 📋 backlog (readiness agg, identité exercice, substitution first-class) |
| Release tag | ⏸️ différé |

**Prochaine action** : ouvrir `Sb_32.3 body_map_descriptor` (contrat de service),
sur override explicite opérateur, review-gated. **Non ouvert dans ce commit.**

---

## 7. Verdict

**Verdict :** ✅ **Sb_32.2 ExerciseMuscleMapping + lookup/fallback — HUMAN REVIEW ACCEPTED.**

Relation exercice→zone posée et backfillée depuis la baseline Sb_32.1, chemin de
lookup DB optionnel avec fallback substring, invariance **prouvée 91/91** sur les
deux chemins, comportement métier inchangé, aucun consommateur migré, CI réelle
verte 3/3 (attempt 2). L'annulation SonarCloud de l'attempt 1 est documentée
comme bruit infra, résolue par re-run. Le cycle Sx_32 est **in progress**.
`Sb_32.3` est **prêt à être proposé, non ouvert**. Aucun code touché par cette revue.
