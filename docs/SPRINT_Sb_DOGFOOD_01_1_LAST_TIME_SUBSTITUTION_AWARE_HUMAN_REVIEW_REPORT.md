# Human Review — Sb_DOGFOOD_01.1 last_time Substitution-Aware Source Fix

**Verdict** : ✅ **HUMAN REVIEW ACCEPTED**
**Date** : 2026-07-11
**Type** : revue humaine — docs-only (aucun code touché)
**Cycle** : Sx_DOGFOOD_01 Load Hint / Substitution Coherence
**Build report** : [`SPRINT_Sb_DOGFOOD_01_1_LAST_TIME_SUBSTITUTION_AWARE_REPORT.md`](SPRINT_Sb_DOGFOOD_01_1_LAST_TIME_SUBSTITUTION_AWARE_REPORT.md)

---

## 1. Décision

**Sb_DOGFOOD_01.1 est accepté.** `last_time_by_exercise_code` est désormais
**substitution-aware** : une charge précédente n'est affichée que si elle
appartient à l'exercice **réellement exécuté** pour le slot courant. Le bug
dogfood (charge d'un exercice alternatif affichée comme référence d'un autre) est
corrigé à la **source unique**, et les 5 surfaces consommatrices héritent
automatiquement de la garantie via un contrat de retour inchangé.

---

## 2. Preuve CI (run réel)

| Item | Valeur |
|---|---|
| **Commit** | `b5776fbec2da73b1d904d6cd700656aeeece7854` |
| **Run** | [`29160746462`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/29160746462) — ✅ **3/3 success** |
| `lint` | ✅ success |
| `pytest + QA scripts` | ✅ success |
| `SonarCloud` | ✅ success |
| **Tests** | ✅ **1896 passed** (2 warnings, 21:57) — +9 = tests S1→S5 |

---

## 3. Éléments acceptés (checklist)

| Élément | Statut |
|---|---|
| `last_time_by_exercise_code` substitution-aware | ✅ |
| Contrat de retour inchangé : `dict[str, dict]` | ✅ |
| Consommateurs inchangés : `last_time.get(se.exercise_code_snapshot)` | ✅ |
| Politique alignée avec overload — prescrit → historique prescrit | ✅ |
| Politique — substitué X → historique même X | ✅ |
| Politique — autre cas → absence | ✅ |
| Matrice S1→S5 couverte | ✅ |
| Règle : silence plutôt que faux poids | ✅ |
| Aucun modèle | ✅ |
| Aucune migration | ✅ |
| Aucun router | ✅ |
| Aucun overload | ✅ |
| Aucun template / CSS | ✅ |
| Aucun Body Intelligence | ✅ |
| Aucun JS | ✅ |
| Aucun `value=` | ✅ |

---

## 4. Matrice S1→S5 (avant / après)

| Scénario | Avant | Après |
|---|---|---|
| **S1** prescrit → prescrit | ✅ charge prescrite | ✅ inchangé |
| **S2** prescrit → substitué | ❌ charge du prescrit | ✅ **absent** (silence) |
| **S3** substitué → prescrit | ❌ charge de la substitution | ✅ **prescrit plus ancien** ou absent |
| **S4** substitué(X) → substitué(X) | ✅ charge X | ✅ inchangé |
| **S5** substitué(X) → substitué(Y) | ❌ charge X | ✅ **Y plus ancien** ou absent |

Couverte par 9 tests (`tests/test_last_time_substitution.py`), dont les cas subtils
S3/S5 (retourne l'occurrence compatible plus ancienne, jamais l'incompatible).

---

## 5. Implémentation acceptée

- `stats.py` : `_normalize_sub` (vide/whitespace → None) + `_matches_current_substitution`
  (politique identique à `overload_inputs._matches_substitution_policy`, **répliquée
  localement**, pas d'import cross-service) + filtre dans la boucle de
  `last_time_by_exercise_code`.
- `_summarise_prior` et le router **non modifiés**.
- Overload placeholders **inchangés** (déjà substitution-aware).

---

## 6. Note process

- **Full sweep local hang** (test préexistant qui bloque localement, in-process, sans
  rapport avec `stats.py`) — le garde-fou a correctement classé `SHARED_CODE`
  (`stats.py` importé ailleurs) et exigé le full sweep ; celui-ci a été lancé puis
  interrompu (hang). La **CI réelle** (job pytest, timeout 25 min) l'a exécuté →
  **1896 passed**, confirmant que le hang est un artefact **local**, pas le code.
- 449 tests ciblés locaux verts (surface last_time + tous les consommateurs) avant push.

---

## 7. Suite du cycle Sx_DOGFOOD_01

| Sprint | État après cette revue |
|---|---|
| **Sb_DOGFOOD_01.1** | ✅ **HUMAN REVIEW ACCEPTED** (2026-07-11) |
| **Sb_DOGFOOD_01.2** consumer propagation verification | 🟡 **READY TO BE PROPOSED, not opened** — vérifier explicitement que delta / hints Sx_08 / chip / peek deviennent silencieux en S2/S3/S5 (ils héritent déjà via `.1`) |
| **Sb_DOGFOOD_01.3** mobile placeholder | ⏸️ deferred |
| Body Intelligence | ⏸️ deferred |
| Deploy | ⏸️ deferred |
| Release tag | ⏸️ deferred |

---

## 8. Verdict

**Verdict :** ✅ **Sb_DOGFOOD_01.1 last_time Substitution-Aware — HUMAN REVIEW ACCEPTED.**

`last_time` applique désormais la même politique de substitution que l'overload :
prescrit↔prescrit, substitué↔même substitut, sinon **absence** (silence plutôt que
faux poids). Correctif à la source unique, contrat de retour inchangé, 5 surfaces
consommatrices intactes, matrice S1→S5 couverte (9 tests). Aucun router / overload /
modèle / migration / template / CSS / Body Intelligence touché. CI réelle verte 3/3
(1896 passed). `Sb_DOGFOOD_01.2` (vérif propagation consommateurs) prêt à être
proposé. Aucun code touché par cette revue.
