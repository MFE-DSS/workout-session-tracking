# Human Review — Sb_UI_06.1 Exercise Card De-densification

**Verdict** : ✅ **HUMAN REVIEW ACCEPTED**
**Date** : 2026-07-10
**Type** : revue humaine — docs-only (aucun code touché)
**Cycle** : Sx_UI_06 Information Density / Dedup
**Build report** : [`SPRINT_Sb_UI_06_1_REPORT.md`](SPRINT_Sb_UI_06_1_REPORT.md)

---

## 1. Décision

**Sb_UI_06.1 est accepté.** La carte d'exercice en séance est dé-densifiée : la
charge de la dernière séance et la cible ne sont plus affichées à plusieurs
endroits sur la carte active. Chaque information vit désormais à **un seul
endroit, le plus proche de l'action** — sans aucune perte d'information (les
cartes non-actives conservent « Dernière fois »), et sans toucher au métier ni
au contrat de saisie. C'est la réponse directe au point d'attention opérateur
(surcharge informationnelle).

---

## 2. Preuve CI (run réel)

| Item | Valeur |
|---|---|
| **Commit** | `2ea53db5e87f24ce5ea87027ad011888c915a73c` |
| **Run** | [`29080671534`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/29080671534) — ✅ **3/3 success** |
| `lint (ruff budget + bandit + actionlint + shellcheck)` | ✅ success |
| `pytest + QA scripts` | ✅ success |
| `SonarCloud` | ✅ success |
| **Tests** | ✅ **1873 passed** (2 warnings, 21:26) |

---

## 3. Éléments acceptés (checklist)

| Élément | Statut |
|---|---|
| **D1** — « Dernière fois » supprimé **uniquement sur la carte active** | ✅ |
| Cartes non-actives — « Dernière fois » **conservé → aucune perte d'information** | ✅ |
| **D2** — la cible / set_scheme ne vit plus que dans le **placeholder des cases** | ✅ |
| Row console « Cible » retirée | ✅ |
| Row console « Référence précédente » conservée | ✅ |
| Contrat de logging intact (`set_*_weight_kg/_reps`, form, dérivation serveur) | ✅ |
| No-JS / SSR intact | ✅ |
| Aucun changement métier | ✅ |
| Aucun modèle / migration / schema | ✅ |
| Aucun Sx_32 backend | ✅ |
| Aucun Body Intelligence | ✅ |
| Aucun scoring / coach / substitution / readiness | ✅ |

---

## 4. Avant / Après (carte active)

| Donnée | Avant | Après |
|---|---|---|
| Charge dernière séance | recap · chip · bloc « Dernière fois » · console « Référence précédente » | **console « Référence précédente »** uniquement (carte active) |
| Cible / objectif | scheme en tête · console « Cible » · placeholder case | **placeholder de la case** uniquement |

Cartes **non-actives** : « Dernière fois » conservé (zéro perte d'info).

---

## 5. Note process (capturée)

- **Full sweep local non concluant** : un test **préexistant hang** localement
  (bloque indéfiniment, ~10h observées, sans rapport avec ce changement ; aucun
  enfant subprocess). Il n'apparaît **pas en CI** (job pytest `timeout-minutes: 25`,
  passe systématiquement). La CI réelle a exécuté le full sweep → **1873 passed**,
  confirmant que le hang est un artefact **local** (machine), pas le code.
- **2 régressions attrapées avant commit** : deux tests Worked Area cherchaient
  le fallback en **minuscule** « à qualifier » — string qui provenait en réalité
  de la row « Cible » console retirée par D2. Le fallback Worked Area réel est
  « **À** qualifier » (majuscule). Assertions rendues case-insensitive sur la
  vraie surface (fix de fragilité, intention préservée). Leçon : les tests qui
  asservissent une string via une surface **voisine** cassent quand cette surface
  bouge — préférer asserter sur la surface propre.

---

## 6. Suite du cycle Sx_UI_06

| Sprint | État après cette revue |
|---|---|
| **Sb_UI_06.1** Exercise Card | ✅ **HUMAN REVIEW ACCEPTED** (2026-07-10) |
| **Sb_UI_06.2** Worked Area (chip zone R3 + « à qualifier » R5) | 🟡 **READY TO BE PROPOSED, not opened** |
| **Sb_UI_06.3** Home (teaser readiness R4 + KPI R6) | ⏸️ deferred |
| **Sb_UI_06.4** écrans secondaires | ⏸️ deferred |
| Body Intelligence | ⏸️ deferred |
| Deploy | ⏸️ deferred |
| Release tag | ⏸️ deferred |

---

## 7. Verdict

**Verdict :** ✅ **Sb_UI_06.1 Exercise Card De-densification — HUMAN REVIEW ACCEPTED.**

La carte d'exercice n'affiche plus la charge précédente 3-4× ni la cible 3× :
chaque information à un seul endroit, au plus près de l'action, sans perte d'info
(cartes non-actives préservées) et sans toucher au logging ni au métier. CI réelle
verte 3/3 (1873 passed). `Sb_UI_06.2` (Worked Area) prêt à être proposé. Aucun code
touché par cette revue.
