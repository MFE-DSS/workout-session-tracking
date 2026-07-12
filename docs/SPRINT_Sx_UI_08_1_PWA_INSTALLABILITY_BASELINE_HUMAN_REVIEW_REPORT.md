# Human Review — Sx_UI_08.1 PWA Installability Baseline

**Verdict** : ✅ **HUMAN REVIEW ACCEPTED**
**Date** : 2026-07-11
**Type** : revue humaine — docs-only (aucun code touché par cette revue)
**Cycle** : Sx_UI_08 (Portability / Installability)
**Build report** : [`SPRINT_Sx_UI_08_1_PWA_INSTALLABILITY_BASELINE_REPORT.md`](SPRINT_Sx_UI_08_1_PWA_INSTALLABILITY_BASELINE_REPORT.md)

---

## 1. Décision

**Sx_UI_08.1 est accepté.** Le manifest PWA est **resserré** (`id`/`lang`/`dir`
ajoutés ; name/short_name/couleurs `#0f1115` **inchangés**) et `base.html` gagne
`apple-mobile-web-app-title="SPIGNOS"` (cohérent avec le `<title>` existant, **pas un
rebrand**). **Aucun** service worker / offline / cache / SPA / JS / nouvelle icône /
nouvelle couleur / changement métier ; session, Body Intelligence, physique,
`pages.py`, services, modèles, migrations, deploy, nginx **intacts** ; no-JS fallback
préservé. Compatible avec le dogfooding séance de demain (aucune surface séance
touchée).

---

## 2. Preuve CI (run réel)

| Item | Valeur |
|---|---|
| **Commit build** | `d2519a4` |
| **Run** | [`29209091349`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/29209091349) — ✅ **3/3 success** |
| `lint` | ✅ success |
| `pytest + QA scripts` | ✅ success (23:07) |
| `SonarCloud` | ✅ success |
| Migration checks · Perf budget | ✅ success (job pytest) |
| **Tests** | ✅ **1958 passed** (+14 = tests dédiés Sx_UI_08.1) |

Premier coup, aucune annulation infra.

---

## 3. Éléments acceptés (checklist)

| Élément | Statut |
|---|---|
| Manifest resserré (`id`/`lang`/`dir` ajoutés) | ✅ |
| name/short_name/couleurs `#0f1115` **inchangés** | ✅ |
| `apple-mobile-web-app-title="SPIGNOS"` (pas un rebrand) | ✅ |
| Assets existants seulement (`favicon.svg`) | ✅ |
| **Pas d'apple-touch-icon** (aucun PNG) | ✅ |
| **Aucun** service worker / offline / cache / SPA / JS | ✅ |
| theme-color inchangé | ✅ |
| Session / BI / physique / pages.py / services / models / migrations intacts | ✅ |
| deploy / nginx / config prod intacts | ✅ |
| no-JS fallback préservé | ✅ |
| Compatible dogfooding séance demain | ✅ |

---

## 4. Note scope-guard (promotion manuelle acceptée)

`check_scope` a classé **ISOLATED** ; l'opérateur a **promu manuellement en
SHARED_CODE** parce que `base.html` est le layout partagé par ~toutes les pages SSR —
un changement de `<head>` touche potentiellement tout rendu. Broad sweep large
exécuté (**733 passed**) + **CI GitHub complète = source de vérité** → 3/3 verte.
Bonne décision de prudence.

---

## 5. Limite actée (→ Sx_UI_08.2)

Les pages auth publiques (`welcome` / `login` / `register`) ont un `<head>`
**standalone** qui n'hérite pas de `base.html` : elles ne portent donc pas encore le
manifest resserré ni `apple-mobile-web-app-title`. **Hors périmètre de `.1`** — cette
limite est le point de départ de **`Sx_UI_08.2`** (alignement des heads auth publics).

---

## 6. Tests (rappel)

14 tests dédiés (`test_pwa_installability.py`) : manifest JSON valide + clés
d'installabilité + display standalone + start_url résout + icons = asset existant ;
base.html référence manifest + theme-color + viewport + apple-mobile-web-app-title +
rendu réel ; non-goals (aucun SW / script PWA / fichier SW). Broad sweep **733
passed** — 0 régression. CI réelle **1958 passed**.

---

## 7. Suite

| Piste | État |
|---|---|
| **Sx_UI_08.2** Public Auth Heads Alignment (aligner welcome/login/register) | 🟡 **READY TO BE PROPOSED** — précondition `.1` ACCEPTED désormais satisfaite |
| Sx_UI_08.3 service worker / offline séance | 🟡 futur (spec, après dogfood) |

---

## 8. Verdict

**Verdict :** ✅ **Sx_UI_08.1 PWA Installability Baseline — HUMAN REVIEW ACCEPTED.**

Manifest resserré + `apple-mobile-web-app-title` sur `base.html`, sans service
worker/offline/JS/nouvelle couleur/changement métier ; toutes les surfaces sensibles
(séance, BI, physique) et l'infra (services, modèles, migrations, deploy, nginx)
**intactes** ; no-JS préservé. CI réelle verte 3/3 (1958 passed). Aucun code touché
par cette revue. Next : **`Sx_UI_08.2`** (alignement des heads auth publics), dont la
précondition est maintenant satisfaite.
