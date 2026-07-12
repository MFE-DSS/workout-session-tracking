# Human Review — Sb_BI_01.2 Zone Drill Detail

**Verdict** : ✅ **HUMAN REVIEW ACCEPTED**
**Date** : 2026-07-11
**Type** : revue humaine — docs-only (aucun code touché par cette revue)
**Cycle** : Body Intelligence (reprise Sx_BI_01, Option A)
**Build report** : [`SPRINT_Sb_BI_01_2_ZONE_DRILL_DETAIL_REPORT.md`](SPRINT_Sb_BI_01_2_ZONE_DRILL_DETAIL_REPORT.md)

---

## 1. Décision

**Sb_BI_01.2 est accepté.** Chaque Zone Intelligence Card gagne un **drill inline
`<details>` no-JS** qui explique la card en montrant les **exercices principaux** de
la zone (noms réutilisés de `ZoneScore.top_exercises`), avec un état vide sobre
« Détail insuffisant ». Disclosure **natif SSR** — zéro JS, no-JS fallback préservé,
mobile-first. **Aucun** volume par exercice (différé), score, grade, radar, nouvelle
route ni nouvelle couleur ; `/physique`, Home, `muscle_scoring.py`, modèles et flag
restent inchangés — la surface reste **invisible en prod** (flag OFF).

---

## 2. Preuve CI (run réel)

| Item | Valeur |
|---|---|
| **Commit build** | `31bb62af94117707610d11ee9c3ddbe5bd2cde13` |
| **Run** | [`29194461683`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/29194461683) — ✅ **3/3 success** |
| `lint` | ✅ success |
| `pytest + QA scripts` | ✅ success (22:06) |
| `SonarCloud` | ✅ success |
| Migration checks · Perf budget | ✅ success (job pytest) |
| **Tests** | ✅ **1935 passed** (+10 = tests dédiés Sb_BI_01.2) |

Premier coup, aucune annulation infra.

---

## 3. Éléments acceptés (checklist)

| Élément | Statut |
|---|---|
| Drill inline `<details>` natif dans chaque zone card | ✅ |
| `<summary>Détail zone</summary>` | ✅ |
| Exercices principaux via `ZoneScore.top_exercises` | ✅ |
| Noms d'exercices seulement | ✅ |
| Pas de volume par exercice en V1 | ✅ |
| État vide « Détail insuffisant » | ✅ |
| **Zéro JS** · no-JS fallback préservé · mobile-first | ✅ |
| Aucune nouvelle route | ✅ |
| Aucun nouveau score · aucun grade A/B/C · aucun radar | ✅ |
| `/physique` intact | ✅ |
| Home intacte | ✅ |
| `muscle_scoring.py` intact | ✅ |
| Modèles / migrations / schema intacts | ✅ |
| Auren Terminal sans nouvelle couleur | ✅ |
| Flag `body_intelligence_enabled` conservé **OFF prod** | ✅ |
| Aucun deploy | ✅ |

---

## 4. Choix `<details>` inline (accepté)

`<details>`/`<summary>` est le **disclosure widget natif** du HTML : repli/dépli
**sans JS**, no-JS fallback intact (contenu accessible JS désactivé), mobile-first,
sans nouvelle route. Le drill « explique la card » sans devenir un dashboard —
conforme à la règle Sx_TRANSFORM_01 (approfondir la traçabilité, pas l'intelligence
apparente).

---

## 5. Données réutilisées & non affichées

- **Affiché** : `ZoneScore.top_exercises` (≤ 3 noms, déjà calculés par fréquence ;
  router `[:2]`→`[:3]`).
- **Non affiché (différé)** : **volume par exercice** (nécessiterait un recalcul de
  l'historique par exercice → future spec/build) ; zones secondaires ; historique
  90 j ; score/grade/radar (invariant du cycle).

---

## 6. Tests (rappel)

10 tests dédiés (`test_bi01_zone_drill_detail.py`) : flag (404 off, drill on),
`<details>`/`<summary>` natif + top exercices + **aucun JS**, absence de
score/radar dans la section, état vide « Détail insuffisant », non-goals
(`/physique`/Home non touchés, router sans `.score`/grade), wording interdit. Test
`.1` intact (**12/12**). Broad sweep **305 passed** — 0 régression. CI réelle
**1935 passed**.

---

## 7. Note scope-guard (promotion manuelle acceptée)

`check_scope` a classé **ISOLATED** ; l'opérateur a **promu manuellement en
SHARED_CODE** parce que `body_intelligence.py` est un router monté dans `main.py`
via un import groupé que le classifier ne reconnaît pas (angle mort connu). Broad
sweep élargi + **CI GitHub complète = source de vérité** → 3/3 verte. Bonne décision
de prudence.

---

## 8. Flag & production

Le flag **`body_intelligence_enabled` reste OFF en prod** : la surface
`/body/intelligence` (cards + drill) reste **invisible** en production. Activation
**deferred until explicit GO**. Aucune config prod modifiée, aucun deploy.

---

## 9. Suite

| Piste | État |
|---|---|
| Activation `body_intelligence_enabled` (rendre `/body/intelligence` visible en prod) | ⏸️ **deferred until explicit GO** |
| **Sb_BI_01.next** décision score `/physique` (garder / encadrer / déprécier) | 🟡 **READY TO BE PROPOSED, not opened** |
| Volume par exercice dans le drill | 🟡 **future spec/build, not opened** |
| Dogfooding terrain Sx_DOGFOOD_01 | 🗓️ **pending** |
| Deploy | ⏸️ deferred |
| Release tag | ⏸️ deferred |

---

## 10. Verdict

**Verdict :** ✅ **Sb_BI_01.2 Zone Drill Detail — HUMAN REVIEW ACCEPTED.**

Le drill inline `<details>` no-JS explique chaque zone card via ses exercices
principaux (noms, réutilisés de `ZoneScore.top_exercises`), avec un état vide sobre.
Disclosure natif SSR — zéro JS, no-JS fallback préservé, mobile-first ; aucun volume
par exercice (différé), score, grade, radar, nouvelle route ni nouvelle couleur ;
`/physique`, Home, `muscle_scoring.py`, modèles et flag **inchangés** (OFF prod →
surface invisible). CI réelle verte 3/3 (1935 passed). Aucun code touché par cette
revue. Next proposed : activation contrôlée du flag, ou `Sb_BI_01.next` (décision
score `/physique`), sur GO séparé.
