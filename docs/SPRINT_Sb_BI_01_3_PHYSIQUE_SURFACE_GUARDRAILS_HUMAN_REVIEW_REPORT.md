# Human Review — Sb_BI_01.3 Physique Surface Guardrails

**Verdict** : ✅ **HUMAN REVIEW ACCEPTED**
**Date** : 2026-07-11
**Type** : revue humaine — docs-only (aucun code touché par cette revue)
**Cycle** : Body Intelligence (reprise Sx_BI_01, Option B)
**Build report** : [`SPRINT_Sb_BI_01_3_PHYSIQUE_SURFACE_GUARDRAILS_REPORT.md`](SPRINT_Sb_BI_01_3_PHYSIQUE_SURFACE_GUARDRAILS_REPORT.md)

---

## 1. Décision

**Sb_BI_01.3 est accepté.** La surface live `/physique` est **encadrée** sans être
cassée : microcopy « lecture synthétique · score indicatif, non médical » qui
**relativise** le score A/B/C sans le renforcer ni le masquer, plus un lien vers
`/body/intelligence` **conditionnel au flag** (jamais un lien mort). Le score, le
grade, le radar et le service partagé `compute_physique_dashboard` restent
**inchangés** — leaderboard, user_profile, Home et internals Body Intelligence
**préservés**. Le flag reste **OFF en prod**. L'ordre validé en `.next` est respecté :
`/physique` encadré **avant** toute activation BI.

---

## 2. Preuve CI (run réel)

| Item | Valeur |
|---|---|
| **Commit build** | `fa7d63e98cc95ce6fa6689e446bdf4e0df49e363` |
| **Run** | [`29201970643`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/29201970643) — ✅ **3/3 success** |
| `lint` | ✅ success |
| `pytest + QA scripts` | ✅ success (22:57) |
| `SonarCloud` | ✅ success |
| Migration checks · Perf budget | ✅ success (job pytest) |
| **Tests** | ✅ **1944 passed** (+9 = tests dédiés Sb_BI_01.3) |

Premier coup, aucune annulation infra.

---

## 3. Éléments acceptés (checklist)

| Élément | Statut |
|---|---|
| Microcopy d'encadrement du score `/physique` | ✅ |
| « Lecture synthétique · Score indicatif, non médical. » | ✅ |
| Note « lecture par zones = surface principale quand BI activé » | ✅ |
| Lien « Voir la lecture par zones » **uniquement si flag ON** | ✅ |
| **Aucun lien mort** vers `/body/intelligence` si flag OFF | ✅ |
| Score conservé | ✅ |
| Grade conservé | ✅ |
| Radar conservé | ✅ |
| `compute_physique_dashboard` intact | ✅ |
| Leaderboard préservé | ✅ |
| user_profile préservé | ✅ |
| Home intacte | ✅ |
| Body Intelligence internals intacts | ✅ |
| Modèles / migrations / schema intacts | ✅ |
| Aucun JS · aucun nouveau score · aucun nouveau radar | ✅ |
| Aucun deploy | ✅ |

---

## 4. Comportement flag OFF / flag ON (validé)

| État | Comportement |
|---|---|
| **flag OFF** (défaut prod) | microcopy affichée ; **aucun lien** vers `/body/intelligence` |
| **flag ON** (test / futur prod) | microcopy **+** lien « Voir la lecture par zones » → `/body/intelligence` |

Flag lu **côté serveur** (`get_settings().body_intelligence_enabled`), passé au
template par `pages.py`. **Config prod inchangée** (flag reste OFF). Couvert par les
tests : OFF (client par défaut) et ON (client HTTP réel authentifié).

---

## 5. Service partagé préservé (point critique `.next`)

L'audit `.next` avait établi que `compute_physique_dashboard` alimente aussi
**leaderboard** et **user_profile**. Ce build **ne touche pas le service** :
- test sentinelle `test_muscle_scoring_not_modified_by_guardrails` (le marqueur
  `physique-guardrails` n'apparaît pas dans `muscle_scoring.py`) ;
- test sentinelle sur `leaderboard.py` et `user_profile.html`.

La dépréciation vise la **surface `/physique`** (microcopy), **jamais le service** —
conforme à la décision Option B prudente.

---

## 6. Tests (rappel)

9 tests dédiés (`test_bi01_physique_guardrails.py`) : rendu microcopy + score/grade/
radar conservés · flag OFF sans lien · flag ON avec lien (client HTTP réel) ·
non-régression (service + leaderboard + user_profile + Home + BI templates intacts)
· pas de JS · wording interdit. Broad sweep **301/288 passed** — 0 régression. CI
réelle **1944 passed**.

---

## 7. Note scope-guard (promotion manuelle acceptée)

`check_scope` a classé **ISOLATED** ; l'opérateur a **promu manuellement en
SHARED_CODE** parce que `pages.py` est une route montée dans l'app que le classifier
ne reconnaît pas comme partagée. **CI GitHub complète = source de vérité** → 3/3
verte. Bonne décision de prudence.

---

## 8. Flag & production

`body_intelligence_enabled` reste **OFF en prod** : le lien BI n'apparaît pas encore
en production. Le score `/physique` est désormais **encadré**, ce qui satisfait
l'ordre `.next` (encadrement AVANT activation). L'activation reste **deferred until
explicit GO**.

---

## 9. Suite

| Piste | État |
|---|---|
| **Sb_BI_01.activation** Controlled BI Flag Activation | 🟡 **READY TO BE PROPOSED, not opened** |
| Activation flag `body_intelligence_enabled` | ⏸️ **deferred until explicit GO** |
| Deploy | ⏸️ deferred |
| Release tag | ⏸️ deferred |
| Dogfooding terrain Sx_DOGFOOD_01 | 🗓️ **pending demain** |

---

## 10. Verdict

**Verdict :** ✅ **Sb_BI_01.3 Physique Surface Guardrails — HUMAN REVIEW ACCEPTED.**

`/physique` est **encadré** (microcopy « lecture synthétique · score indicatif, non
médical » + lien BI conditionnel au flag) sans que le score/grade/radar ni le service
partagé `compute_physique_dashboard` soient modifiés — leaderboard, user_profile,
Home et internals BI préservés (tests sentinelles). Flag OFF prod inchangé. CI réelle
verte 3/3 (1944 passed). L'ordre `.next` est satisfait : encadrement **avant**
activation. Aucun code touché par cette revue. Next proposed : **`Sb_BI_01.activation`**
(readiness de l'activation contrôlée du flag), ou dogfooding terrain, sur GO séparé.
