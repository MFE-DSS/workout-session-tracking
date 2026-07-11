# Audit Report — Sx_DOGFOOD_01 Load Hint / Substitution Coherence

**Statut** : 🟢 AUDIT ONLY — pending human review (docs-only, aucun code)
**Date** : 2026-07-11
**Spec** : [`docs/strategy/Sx_DOGFOOD_01_LOAD_HINT_SUBSTITUTION_COHERENCE_SPEC.md`](strategy/Sx_DOGFOOD_01_LOAD_HINT_SUBSTITUTION_COHERENCE_SPEC.md)
**Méthode** : audit read-only du code (router, services, template, CSS, tests) — aucun fichier modifié.

---

## 0. Étape 0 — Brainstorming / sujets clivants

Les 12 sujets clivants du brief sont tranchés dans la spec §10. Synthèse : identité
de charge = `(exercise_code_snapshot, substitution_key)` ; prescrit et substitut =
historiques séparés ; **silence plutôt que faux poids** ; Option A (patch `last_time`)
comme build minimal, Option B (service central) future, Option D (transfert de
charge) rejetée V1.

---

## 1. Feedback dogfood (constat de départ)

Sur les cartes d'exercice, les poids/reps proposés deviennent **incohérents** quand
un exercice alternatif a été utilisé dans une séance précédente, ou quand
l'utilisateur choisit une alternative dans la séance courante. Une « dernière fois »
peut afficher la charge d'un **autre exercice** (celui du slot, pas celui exécuté).

---

## 2. Carte des producteurs de suggestion de charge

| # | Producteur | Fichier:ligne | Donnée | Identité | Sub-aware ? |
|---|---|---|---|---|---|
| 1 | `last_time_by_exercise_code` | `stats.py:118-157` | dict `code → {weights_str, reps_str, relative, has_data}` | `(template_slug, exercise_code_snapshot)` | ❌ **NON** (aucun filtre `substituted_name`) |
| 2a | `build_overload_input_for_exercise` | `overload_inputs.py:231-286` | `OverloadInput` | code + `current_is_substituted` | ✅ (silence si substitué) |
| 2b | `_history_signals_for_code` | `overload_inputs.py:96-191` | `HistoricalSetSignal` | code + `_matches_substitution_policy` | ✅ **V2 stricte** |
| 3 | `compute_overload_hint` | `overload_engine.py:255-306` | `OverloadHint` | — (engine pur) | ✅ (amont) |
| 4 | `explain_overload_hint` + `_build_overload_placeholder` | `overload_explainer.py:62` / `sessions.py:182-208` | placeholders `{weight, reps}` | — | ✅ (amont) |
| 5 | `compute_delta` / `format_delta` | `delta.py:38-114` | delta string | consomme `last_time.get(code)` | ❌ **NON** |
| 6 | `build_chip` | `briefing.py:86-104` | chip « dernière fois » | consomme `last_time.get(code)` | ❌ **NON** |
| 7 | `build_peek` | `briefing.py:107-146` | up-next overlay | consomme `last_time.get(code)` | ❌ **NON** (display_name OK via `substituted_name`, mais charge non-aware) |
| 8 | `compute_hints` (Sx_08) | `hints.py:32-87` | hints +10%/reps drop | consomme `last_time.get(code)` | ❌ **NON** |

**Producteurs sûrs** : la chaîne overload (2→4) filtre la substitution et devient
**silencieuse** si l'exercice courant est substitué (`overload_inputs.py:260-264`).

**Producteurs contaminés** : tout ce qui dérive de `last_time` (1, 5, 6, 7, 8).

---

## 3. Carte des consommateurs (router `sessions.py::session_detail`)

| Ligne (~) | Appel | Clé | Sub-aware ? |
|---|---|---|---|
| 244 | `last_time = last_time_by_exercise_code(db, session, now)` | fetch global | ❌ |
| 265-276 | `build_overload_input_for_exercise(...)` → hint → placeholder | interne (code + substitution) | ✅ |
| 333 | `compute_sb08_hints(se, last_time.get(se.exercise_code_snapshot))` | `exercise_code_snapshot` | ❌ |
| 354 | `prior = last_time.get(code)` (delta) | `exercise_code_snapshot` | ❌ |
| 361-365 | `compute_delta(curr, prior)` → `format_delta` | dérive de `prior` | ❌ |
| 423-426 | `build_chip(se.template_exercise, last_time.get(code), ...)` | `exercise_code_snapshot` | ❌ |
| 436-439 | `build_peek(next_se, last_time.get(next_code), ...)` | `next_se.exercise_code_snapshot` | ❌ |

---

## 4. Carte des identités

`SessionExercise` (`models/session.py`) :
- `exercise_code_snapshot` (slot prescrit E1…E7) — clé de `last_time`.
- `exercise_name_snapshot` (nom prescrit).
- `substituted_name` (nullable — nom réellement exécuté si substitution) — **ignoré
  par `last_time`, utilisé par overload**.
- `actual_exercise_name(se)` = `substituted_name or exercise_name_snapshot`
  (`substitution.py:95`) — utilisé par overload/descriptor, **pas** par `last_time`.

---

## 5. Table des incohérences possibles

| Surface | Producteur | Scénarios impactés | Symptôme |
|---|---|---|---|
| Référence précédente (console active) | `last_time` | S2, S3, S5 | affiche la charge d'un exercice différent |
| Dernière fois (cartes non-actives) | `last_time` | S2, S3, S5 | idem |
| Delta | `compute_delta` (via `last_time`) | S2, S3, S5 | Δ inter-exercice (fausse progression/régression) |
| Hints Sx_08 | `compute_hints` (via `last_time`) | S2, S3, S5 | alerte +10% / reps drop sur inter-exercice |
| Chip / Peek briefing | `build_chip` / `build_peek` | S2, S3, S5 | « dernière fois » incomparable |
| Cible (placeholder) | overload | — | **déjà sûr** (silence si substitué) |

---

## 6. Analyse des 5 transitions

| Transition | `last_time` renvoie aujourd'hui | Attendu | Verdict |
|---|---|---|---|
| **S1** prescrit → prescrit | prescrit du slot | prescrit | ✅ correct |
| **S2** prescrit → substitué | prescrit du slot (alors que courant = alternative) | silence | ❌ faux |
| **S3** substitué → prescrit | dernière occ. (substituée) du slot | prescrit précédent (ou silence) | ❌ faux |
| **S4** substitué → **même** substitut | historique du même substitut | même substitut | ✅ correct |
| **S5** substitué → **autre** substitut | autre substitut | silence | ❌ faux |

**Décision** (spec §6) : aligner `last_time` sur la politique de substitution
d'`overload_inputs` — prescrit↔prescrit strict, substitué↔même `substituted_name`
strict, **silence** sinon.

---

## 7. Décision « silence plutôt que faux poids »

Confirmée. Une charge inter-exercice trompe l'utilisateur (fausse progression /
régression, faux hint de prudence). En l'absence d'historique **aligné**, toutes
les surfaces dérivées doivent devenir **silencieuses** (comme le fait déjà
overload), jamais afficher une valeur d'un autre exercice.

---

## 8. Proposition de split build

- **`Sb_DOGFOOD_01.1`** — `last_time` substitution-aware (source unique) + tests des
  5 scénarios + microcopy « pas de repère pour cette alternative ».
- **`Sb_DOGFOOD_01.2`** — propagation aux dérivés (delta, hints Sx_08, chip, peek) :
  cohérence automatique + silence vérifié en S2/S3/S5.
- **`Sb_DOGFOOD_01.3`** — mobile placeholder proportion (CSS-only) : format `102.5`,
  typo réduite mobile, évaluer unité séparée.

Review-gated, sur override séparé. Contrat immuable : **placeholders seulement,
jamais `value=`**.

---

## 9. Section mobile — placeholder proportion

- Unité **non séparée** : le placeholder = « kg »/« reps » (vide) ou valeur cible
  chiffrée (`_ph.weight`, ex. « ≈ 102.5 »).
- Media queries `@max-width: 380px` présentes ; pas de contrôle de proportion.
- V1 (`.3`, CSS-only) : format `102.5` (retirer `≈`), réduire la police du
  `::placeholder` sur mobile ; unité séparée = à évaluer (touche la structure de row).
- Tap target 44×44 conservé ; aucun JS.

---

## 10. Non-goals

Voir spec §11 : pas de migration/modèle/schema, pas de Body Intelligence, pas de
substitution graph, pas de recalcul historique, pas de transfert de charge (Option
D), pas de JS, pas de préremplissage, **pas de `value=`**.

---

## Verdict

**Verdict :** 🟢 **AUDIT COMPLET — READY FOR HUMAN DECISION.**

Asymétrie confirmée : `overload` est substitution-aware (silence si substitué),
`last_time_by_exercise_code` **ne l'est pas** et contamine 5 surfaces (Référence
précédente, Dernière fois, Delta, Hints Sx_08, Chip/Peek) dans les scénarios
S2/S3/S5 (mélange inter-exercice). Correctif minimal = **Option A** (aligner
`last_time` sur la politique de substitution d'overload), avec la règle « silence
plutôt que faux poids ». Split build `.1`/`.2`/`.3` + section mobile placeholder.
**Aucun code touché par cet audit.**
