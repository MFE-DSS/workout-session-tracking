# Human Review — Sb_DOGFOOD_01.2 Consumer Propagation Verification

**Verdict** : ✅ **HUMAN REVIEW ACCEPTED**
**Date** : 2026-07-11
**Type** : revue humaine — docs-only (aucun code touché)
**Cycle** : Sx_DOGFOOD_01 Load Hint / Substitution Coherence
**Build report** : [`SPRINT_Sb_DOGFOOD_01_2_CONSUMER_PROPAGATION_VERIFICATION_REPORT.md`](SPRINT_Sb_DOGFOOD_01_2_CONSUMER_PROPAGATION_VERIFICATION_REPORT.md)

---

## 1. Décision

**Sb_DOGFOOD_01.2 est accepté.** Ce sprint **verification-only** prouve noir sur
blanc que les consommateurs de `last_time` (Référence précédente, delta, hints
Sx_08, chip/peek) héritent **automatiquement** du fix source `.1` : en S2/S3/S5 ils
tombent sur l'état vide existant (« Non disponible ») et n'affichent **jamais** la
charge d'un autre exercice ; en S1/S4 la référence comparable reste visible. **Aucun
code applicatif n'a été modifié** — les consommateurs géraient déjà l'absence de
`last_time`, et 8 tests le verrouillent.

---

## 2. Preuve CI (run réel)

| Item | Valeur |
|---|---|
| **Commit** | `306620e3e8e6f1bbf906393956acfc5e27ce4b14` |
| **Run** | [`29164774428`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/29164774428) — ✅ **3/3 success** |
| `lint` | ✅ success |
| `pytest + QA scripts` | ✅ success |
| `SonarCloud` | ✅ success |
| **Tests** | ✅ **1904 passed** (2 warnings, 18:44) — +8 = tests de propagation |

---

## 3. Éléments acceptés (checklist)

| Élément | Statut |
|---|---|
| Verification-only | ✅ |
| Aucun code applicatif modifié | ✅ |
| Delta silencieux quand `last_time` absent | ✅ |
| Hints Sx_08 silencieux quand `last_time` absent | ✅ |
| Console « Référence précédente » → « Non disponible » en S2/S3/S5 | ✅ |
| S3 → prescrit plus ancien visible, jamais substitution récente | ✅ |
| S1/S4 → références comparables toujours visibles | ✅ |
| Aucun patch consommateur requis | ✅ |
| Aucun modèle / migration / schema | ✅ |
| Aucun Body Intelligence | ✅ |
| Aucun JS / CSS / template applicatif | ✅ |

---

## 4. Propagation prouvée (matrice)

| Scénario | Silencieux | Visible |
|---|---|---|
| **S2** prescrit → substitué | Référence précédente (« Non disponible »), delta, hints | — |
| **S3** substitué → prescrit | la charge de la substitution (80) | le prescrit **plus ancien** (55) |
| **S5** substitué → autre substitut | la charge de l'autre substitut (90), Référence, delta, hints | — |
| **S1** prescrit → prescrit | — | référence (60) |
| **S4** substitué → même substitut | — | référence (80) |

Couvert par 8 tests (`tests/test_dogfood01_consumer_propagation.py`) : 2 unitaires
(delta None, hints []) + 5 HTML bout-en-bout (S1→S5) + 1 garde wording.

---

## 5. Décisions (sujets clivants)

Option **A** (tests seulement) retenue — le fix source `.1` propage seul. Option B
(patch consommateur) **non requise** (aucun test rouge). Microcopy « historique non
comparable » différée (réutilisation des états vides existants « Non disponible » /
« Aucune séance précédente »). `.2` clos comme **verification-only**.

---

## 6. Cycle Sx_DOGFOOD_01 — cohérent de bout en bout

| Sprint | État |
|---|---|
| Sx_DOGFOOD_01 (audit + spec) | ✅ committé |
| **Sb_DOGFOOD_01.1** (fix source `last_time`) | ✅ HUMAN REVIEW ACCEPTED |
| **Sb_DOGFOOD_01.2** (vérif consommateurs) | ✅ **HUMAN REVIEW ACCEPTED** |

Le bug dogfood (charge d'un exercice alternatif affichée pour un autre) est
**corrigé à la source et prouvé sur toutes les surfaces consommatrices**.

---

## 7. Suite

| Piste | État |
|---|---|
| **Sb_DOGFOOD_01.3** mobile placeholder proportion (CSS-only : format `102.5`, typo réduite) | 🟡 **READY TO BE PROPOSED, not opened** |
| Body Intelligence | ⏸️ deferred |
| Deploy | ⏸️ deferred |
| Release tag | ⏸️ deferred |

---

## 8. Verdict

**Verdict :** ✅ **Sb_DOGFOOD_01.2 Consumer Propagation Verification — HUMAN REVIEW ACCEPTED.**

Verification-only : les 5 surfaces consommatrices de `last_time` héritent du fix
`.1` sans aucun patch applicatif — en S2/S3/S5 elles restent silencieuses (état
vide existant), en S1/S4 la référence comparable reste visible, en S3 c'est le
prescrit plus ancien qui apparaît. 8 tests le prouvent ; CI réelle verte 3/3 (1904
passed). Le cycle Sx_DOGFOOD_01 (audit → fix source → vérif) est cohérent de bout
en bout. `Sb_DOGFOOD_01.3` (mobile placeholder) prêt à être proposé. Aucun code
touché par cette revue.
