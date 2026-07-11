# Human Review — Sb_UI_06.3 Home Density Cleanup

**Verdict** : ✅ **HUMAN REVIEW ACCEPTED**
**Date** : 2026-07-11
**Type** : revue humaine — docs-only (aucun code touché)
**Cycle** : Sx_UI_06 Information Density / Dedup
**Build report** : [`SPRINT_Sb_UI_06_3_HOME_TEASER_KPI_CLEANUP_REPORT.md`](SPRINT_Sb_UI_06_3_HOME_TEASER_KPI_CLEANUP_REPORT.md)

---

## 1. Décision

**Sb_UI_06.3 est accepté.** La home est désormais un **cockpit de décision
unique** : un seul CTA (qui démarre la séance recommandée directement), plus de
bloc reco redondant, plus de teaser readiness vide, dernière séance compacte, KPI
réduits au signal décisionnel. Réponse directe au feedback dogfood sur la densité,
sans toucher au contrat de création de session ni au backend.

---

## 2. Preuve CI (run réel)

| Item | Valeur |
|---|---|
| **Commit** | `f5288a4374536d8d8d6c93b5684eb67bfd60f6df` |
| **Run** | [`29149281028`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/29149281028) — ✅ **3/3 success** |
| `lint` | ✅ success |
| `pytest + QA scripts` | ✅ success |
| `SonarCloud` | ✅ success |
| **Tests** | ✅ **1887 passed** (2 warnings, 19:41) |

---

## 3. Éléments acceptés (checklist)

| Élément | Statut |
|---|---|
| Home = cockpit de décision unique | ✅ |
| CTA hero démarre directement la séance recommandée si reco disponible | ✅ |
| Bloc « Prochaine séance suggérée » retiré de la home | ✅ |
| Détail reco + alternatives conservés dans le launcher | ✅ |
| Teaser readiness vide retiré | ✅ |
| Widget readiness unique conservé | ✅ |
| Dernière séance compacte : nom + date, sans Ressenti / Qualité | ✅ |
| KPI home réduit à « séances cette semaine » | ✅ |
| Score moyen / complétion 30j déplacés vers /progress | ✅ |
| Contrat `POST /sessions` intact | ✅ |
| SSR / no-JS intact | ✅ |
| Aucun Body Intelligence | ✅ |
| Aucun backend métier | ✅ |
| Aucun modèle / migration / schema | ✅ |

---

## 4. Avant / Après (home, pas de séance active)

| Surface | Avant | Après |
|---|---|---|
| CTA démarrage | hero « Démarrer une séance » (→ launcher) **+** bloc « Prochaine séance suggérée » | **1 CTA hero** qui lance la reco directement (form POST) |
| Readiness | teaser hero (« détail plus bas ») **+** widget complet | **widget unique** |
| Dernière séance | nom + date + Ressenti + Qualité | **nom + date** |
| KPI home | cette sem. + score moy. + complétion 30j | **cette sem.** + lien /progress |

---

## 5. Brainstorming clivant (rappel — report §0bis)

Les 10 sujets clivants ont été tranchés avant code (3 confirmés opérateur + 7
décidés selon Option A « Home = décision stricte ») : CTA hero démarre la reco
direct · bloc reco retiré de la home (gardé launcher) · teaser retiré · KPI réduits
à « cette sem. » · dernière compacte · disponibilité conservée · Body Intelligence
deferred · Option A template-only (contrat `POST /sessions` inchangé).

---

## 6. Cycle Sx_UI_06 — 3 surfaces principales dé-densifiées

| Sprint | État |
|---|---|
| **Sb_UI_06.1** Exercise Card | ✅ HUMAN REVIEW ACCEPTED (2026-07-10) |
| **Sb_UI_06.2** Worked Area | ✅ HUMAN REVIEW ACCEPTED (2026-07-11) |
| **Sb_UI_06.3** Home | ✅ **HUMAN REVIEW ACCEPTED** (2026-07-11) |

Les 3 surfaces principales (carte d'exercice · Worked Area · home) sont désormais
dé-densifiées ; chaque information vit à un seul endroit, au plus proche de l'action.

---

## 7. Suite

| Piste | État |
|---|---|
| **Dogfood Load Hint / Substitution Coherence** | 🟡 **READY TO BE PROPOSED, not opened** — investigation dogfood : cohérence entre la charge suggérée (overload hint / placeholder) et la substitution d'exercice (le hint suit-il le substitut choisi ?). |
| **Sb_UI_06.4** écrans secondaires (session done / coach report) | ⏸️ deferred |
| Body Intelligence | ⏸️ deferred |
| Deploy | ⏸️ deferred |
| Release tag | ⏸️ deferred |

---

## 8. Verdict

**Verdict :** ✅ **Sb_UI_06.3 Home Density Cleanup — HUMAN REVIEW ACCEPTED.**

Home = cockpit de décision unique : un CTA qui démarre la reco directement, plus de
bloc reco redondant, plus de teaser vide, dernière séance compacte, KPI réduits au
signal « cette semaine ». Contrat de création de session et reco launcher intacts ;
SSR/no-JS ; aucun backend / route / modèle / migration / Body Intelligence touché.
CI réelle verte 3/3 (1887 passed). Prochaine investigation proposée : Load Hint /
Substitution Coherence. Aucun code touché par cette revue.
