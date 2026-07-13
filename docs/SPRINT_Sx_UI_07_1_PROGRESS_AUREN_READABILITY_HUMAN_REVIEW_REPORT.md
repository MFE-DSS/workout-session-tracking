# Human Review — Sx_UI_07.1 Progress Surface Auren Readability

**Verdict** : ✅ **HUMAN REVIEW ACCEPTED**
**Date** : 2026-07-13
**Type** : revue humaine — docs-only (aucun code touché par cette revue)
**Cycle** : Sx_UI_07 (History & Progress)
**Build report** : [`SPRINT_Sx_UI_07_1_PROGRESS_AUREN_READABILITY_REPORT.md`](SPRINT_Sx_UI_07_1_PROGRESS_AUREN_READABILITY_REPORT.md)
**CI headroom report** : [`SPRINT_Sx_UI_07_1_CI_TIMEOUT_HEADROOM_REPORT.md`](SPRINT_Sx_UI_07_1_CI_TIMEOUT_HEADROOM_REPORT.md)

---

## 1. Décision

**Sx_UI_07.1 est accepté.** `/progress` gagne une **lecture Auren plus calme et
hiérarchisée** (lede plus utile, section « Rythme récent », titres timelines sobres,
note « Lecture indicative ») **sans changer une seule valeur ni un service** :
template-only, tous les blocs conservés. Le sprint est validé avec **deux SHAs** : le
**build fonctionnel `98d679d`** (template-only) et le **fix CI infra `01fb142`**
(`timeout-minutes: 35 → 45`, aucun gate retiré).

---

## 2. Preuve CI (run réel)

| Item | Valeur |
|---|---|
| **Build fonctionnel** | `98d679d` (template-only sur `/progress`) |
| **Fix CI infra** | `01fb142` (`ci.yml` timeout 35 → 45) |
| **Run final** | [`29242663710`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/29242663710) — ✅ **3/3 success** |
| `lint` | ✅ success |
| `pytest + QA scripts` | ✅ success (job 24:24, pytest 21:40 — sous les 45 min) |
| `SonarCloud` | ✅ success |
| Migration checks · Perf budget | ✅ success (job pytest) |
| **Tests** | ✅ **1978 passed** |

---

## 3. Éléments acceptés — build (checklist)

| Élément | Statut |
|---|---|
| Lede plus utile (« Lecture des séances terminées, de la régularité et des signaux récents ») | ✅ |
| Section « Rythme récent » ajoutée | ✅ |
| Weekly loop conservé en haut | ✅ |
| KPIs existants conservés | ✅ |
| « Par programme » conservé | ✅ |
| « Activité récente par exercice » conservé | ✅ |
| Timelines qualité / poids conservées | ✅ |
| Note finale reformulée « Lecture indicative » | ✅ |
| Aucun service KPI/timeline/weekly_loop modifié | ✅ |
| `pages.py` non modifié | ✅ |
| Home, session, BI, physique intacts | ✅ |
| Labels « sessions » conservés (périmètre respecté, `test_kpis.py` non modifié) | ✅ |
| Aucun calcul / JS / lien BI-physique / rebrand / nouveau score | ✅ |

---

## 4. Éléments acceptés — fix CI (checklist)

| Élément | Statut |
|---|---|
| `ci_infra` only : `ci.yml` timeout job pytest 35 → 45 | ✅ |
| pytest **inchangé** | ✅ |
| coverage **inchangé** | ✅ |
| QA scripts **inchangés** | ✅ |
| SonarCloud **inchangé** | ✅ |
| migration checks **inchangés** | ✅ |
| perf budget **inchangé** | ✅ |
| Aucun gate retiré | ✅ |

**Cause du fix** : le run `29239935779` sur `98d679d` avait été **cancelled par
timeout de job** (job 35:17 > 35 min, step pytest cancelled à 34:46) malgré **1978
passed** — pas un test rouge. Le patch `35 → 45` donne la marge ; run final vert 3/3
à 24:24.

---

## 5. Note produit — décision « sessions » vs « séances »

Un premier essai renommait « sessions » → « séances » (cohérence FR), mais 2
assertions textuelles préexistantes de `test_kpis.py` (**hors périmètre**) y sont
asservies. **Décision opérateur** : conserver « sessions » sur ces 2 labels pour
rester **strictement dans le périmètre** (`progress.html` seul, `test_kpis.py` non
modifié). Le reste de la microcopy (lede, « Rythme récent », titres timelines, note)
est appliqué. Alignement FR complet = futur sprint (toucherait aussi ces tests).

---

## 6. Note infra — timeout qui remonte (signalé pour la roadmap)

Le timeout du job pytest est passé `25 → 35` (Sb_DOGFOOD_01.3) puis `35 → 45`
(ici) : la suite grandit (~2 sprints ajoutent un run notablement plus lent). À terme,
une **optimisation dédiée** (parallélisation `pytest-xdist`, coverage plus léger)
serait plus saine qu'augmenter le timeout indéfiniment. **Deferred** — sprint dédié,
non urgent ; 45 min tient pour l'instant.

---

## 7. Suite

| Piste | État |
|---|---|
| **Sx_UI_07.2** History Surface Auren Readability | 🟡 **READY TO BE PROPOSED, not opened** |
| CI timeout 45 | ✅ **accepted as current baseline** |
| CI optimization / pytest-xdist | ⏸️ **deferred dedicated sprint** |
| Dogfooding terrain | 🗓️ **pending (en différé)** |
| Activation BI | ⏸️ **deferred until dogfood + explicit GO** |

---

## 8. Verdict

**Verdict :** ✅ **Sx_UI_07.1 Progress Surface Auren Readability — HUMAN REVIEW ACCEPTED.**

`/progress` gagne une lecture plus calme et hiérarchisée (lede utile, section « Rythme
récent », titres timelines sobres, note « Lecture indicative ») **sans changer une
valeur ni un service** — template-only, tous les blocs conservés, `pages.py` et les
services KPI/timeline/weekly_loop intacts ; Home, session, BI, physique intacts ;
labels « sessions » conservés (périmètre respecté). Le fix CI `01fb142` est
**infra-only** (timeout 35 → 45, aucun gate retiré). CI réelle verte 3/3 (1978
passed). Deux SHAs : build `98d679d` + fix CI `01fb142`. Aucun code touché par cette
revue. Next : **`Sx_UI_07.2`** History Surface Auren Readability.
