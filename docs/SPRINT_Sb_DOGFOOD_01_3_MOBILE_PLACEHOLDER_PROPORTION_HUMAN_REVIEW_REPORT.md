# Human Review — Sb_DOGFOOD_01.3 Mobile Placeholder Proportion

**Verdict** : ✅ **HUMAN REVIEW ACCEPTED**
**Date** : 2026-07-11
**Type** : revue humaine — docs-only (aucun code touché par cette revue)
**Cycle** : Sx_DOGFOOD_01 Load Hint / Substitution Coherence (dernier volet)
**Build report** : [`SPRINT_Sb_DOGFOOD_01_3_MOBILE_PLACEHOLDER_PROPORTION_REPORT.md`](SPRINT_Sb_DOGFOOD_01_3_MOBILE_PLACEHOLDER_PROPORTION_REPORT.md)

---

## 1. Décision

**Sb_DOGFOOD_01.3 est accepté.** Ce sprint **UI / présentation** rend les
placeholders cible chiffrés lisibles sur mobile étroit **sans préremplir les
champs et sans toucher la logique d'overload** : le formatter
`_build_overload_placeholder` est compacté (retrait du préfixe `≈`) et une règle
CSS mobile réduit la typo du `::placeholder` de la ligne d'overload — en
préservant le tap target (44 px) et l'anti-zoom iOS (16 px input). Le build
fonctionnel `e7dd1e1` était **valide** (1913 passed) ; il n'était bloqué que par
un **timeout de job CI** (25 min trop court pour une suite qui a grossi), corrigé
par le patch **infra-only** `3474b0c` (`timeout-minutes: 25 → 35`).

---

## 2. Preuve CI (run réel)

| Item | Valeur |
|---|---|
| **Build fonctionnel** | `e7dd1e158f0ab54f2ccaac22f768ef332da6a2d2` |
| **Fix CI infra** | `3474b0c3d43d8818d9ed9f55c337a935a9d62890` |
| **Run** | [`29169942718`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/29169942718) — ✅ **3/3 success** |
| `pytest + QA scripts` | ✅ success (job **25:46** — au-dessus des anciens 25 min, prouve le diagnostic) |
| `lint` | ✅ success |
| `SonarCloud` | ✅ success |
| **Tests** | ✅ **1913 passed** (2 warnings, 22:23) — +9 tests dogfood mobile placeholder |
| `Migration roundtrip check (Sb_26.2)` | ✅ **success** (le step qui était annulé au timeout) |

---

## 3. Éléments acceptés (checklist)

| Élément | Statut |
|---|---|
| Formatter compact : `≈ 102.5` → `102.5` | ✅ |
| Formatter compact : `≈ 6-10` → `6-10` (et `≈ 6` → `6`) | ✅ |
| CSS mobile `@media (max-width: 380px)` ciblant `::placeholder` des lignes overload | ✅ |
| Tap target 44 px préservé (`min-height` intact) | ✅ |
| Anti-zoom iOS 16 px préservé (`font-size` input intact) | ✅ |
| Aucun `value=` prérempli (input actif reste `value=""`) | ✅ |
| Aucun span unité (Option C différée) | ✅ |
| Aucun JS | ✅ |
| Aucun overload engine touché | ✅ |
| Aucun history identity touché | ✅ |
| Aucune substitution logic touchée | ✅ |
| Aucun modèle / migration / schema | ✅ |
| Aucun Body Intelligence | ✅ |
| HTML `exercise_card.html` non modifié (classe déjà existante) | ✅ |
| Aucune occurrence « Repère »/« repère » ajoutée | ✅ |
| Fix CI timeout accepté comme **infra-only**, nécessaire au full pytest + QA | ✅ |

---

## 4. Format retenu (rappel)

| Cas | Avant | Après |
|---|---|---|
| Progress (range) | `≈ 102.5` / `≈ 6-10` | `102.5` / `6-10` |
| Deload (min==max) | `≈ 90` / `≈ 6` | `90` / `6` |
| Une seule borne | `≈ 8` | `8` |
| Pas de cible | `None` | `None` (inchangé) |

L'unité **kg** reste portée par le label existant (contexte console) ; le
caractère « suggestion » reste porté par le placeholder grisé, jamais rempli.

---

## 5. Décisions (sujets clivants)

Option **B légère** retenue : formatter compact (retrait `≈`) **+** CSS mobile
`::placeholder`. Option A (CSS seul) insuffisante (« ≈ 102.5 » restait large) ;
Option C (span unité séparé) **différée** (changement de structure trop large
pour ce sprint) ; Option D (supprimer les placeholders) rejetée (régressif). `≈`
retiré plutôt que remplacé par `~` (bruit visuel évité). Breakpoint **380 px**
(existant, pas de nouveau seuil). Portée inchangée (ligne active de la carte
active). Tests sur string du formatter + regex CSS + rendu HTML (**zéro
screenshot**).

---

## 6. Note scope-guard (promotion manuelle acceptée)

`check_scope` a classé **ISOLATED**, mais l'opérateur a **promu manuellement en
SHARED_CODE** parce que `sessions.py` est un router principal monté dans
`main.py` via un import groupé (`from app.routers import (…)`) que le classifier
ne reconnaît pas (même angle mort que les templates). Des broad sweeps élargis
ont été exécutés (310 + 173 verts). C'est une **bonne décision de prudence**, pas
une anomalie bloquante : la CI réelle reste la source de vérité de non-régression
globale et est verte 3/3.

---

## 7. Fix CI timeout (infra-only, accepté)

| Item | Détail |
|---|---|
| Fichier | `.github/workflows/ci.yml` (job `pytest + QA scripts`) |
| Changement | `timeout-minutes: 25` → `35` (1 ligne, hunk unique) |
| Cause | La suite pytest (1913 tests) tourne à ~24-25 min sur runner GitHub ; le job dépassait 25 min et était annulé (reproductible) au step `Migration roundtrip check`. **Ni test rouge, ni bug applicatif, ni annulation infra aléatoire.** |
| Preuve | Après le fix, le job a pris **25:46** (au-dessus de l'ancien seuil) et est passé **success** → confirme le diagnostic. |
| Garde | 35 min ≪ un vrai hang : ne masque pas un blocage réel, donne juste la marge du sweep QA aval. |

---

## 8. Cycle Sx_DOGFOOD_01 — cohérent de bout en bout

| Sprint | État |
|---|---|
| Sx_DOGFOOD_01 (audit + spec) | ✅ committé |
| **Sb_DOGFOOD_01.1** (fix source `last_time`) | ✅ HUMAN REVIEW ACCEPTED |
| **Sb_DOGFOOD_01.2** (vérif consommateurs) | ✅ HUMAN REVIEW ACCEPTED |
| **Sb_DOGFOOD_01.3** (mobile placeholder) | ✅ **HUMAN REVIEW ACCEPTED** |

Le cycle est complet : **cohérence de charge ↔ substitution** (fix source +
propagation prouvée) **et** lisibilité mobile des placeholders cible. Le
`Sx_DOGFOOD_01 closeout` est prêt à être proposé.

---

## 9. Suite

| Piste | État |
|---|---|
| **Sx_DOGFOOD_01 closeout** | 🟡 **READY TO BE PROPOSED, not opened** |
| Dogfooding terrain | 🗓️ **planifié demain matin** (consignes §8 du build report) |
| Body Intelligence | ⏸️ deferred |
| Deploy | ⏸️ deferred |
| Release tag | ⏸️ deferred |
| Option C (unité séparée) | 💡 piste future, sprint UI dédié |

---

## 10. Verdict

**Verdict :** ✅ **Sb_DOGFOOD_01.3 Mobile Placeholder Proportion — HUMAN REVIEW ACCEPTED.**

Les placeholders cible chiffrés sont compactés (`102.5` / `6-10`, sans `≈`) et
leur typo est réduite sur mobile étroit via une règle `::placeholder` ciblée
`@media (max-width: 380px)`, sans toucher au tap target, à l'anti-zoom iOS, à la
structure HTML, ni au moindre `value=`. Présentation pure (formatter string +
CSS) ; aucun engine / historique / substitution / modèle / migration / JS / Body
Intelligence. Le build fonctionnel `e7dd1e1` (1913 passed) n'était bloqué que par
un timeout de job, corrigé infra-only (`3474b0c`). CI réelle verte 3/3. Le cycle
Sx_DOGFOOD_01 (audit → fix source → vérif → mobile placeholder) est cohérent de
bout en bout ; son closeout est prêt à être proposé. Aucun code touché par cette
revue.
