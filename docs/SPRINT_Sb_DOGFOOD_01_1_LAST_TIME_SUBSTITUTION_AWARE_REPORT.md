# Sprint Sb_DOGFOOD_01.1 — last_time Substitution-Aware Source Fix

**Statut** : 🟢 DELIVERED — pending GO commit + CI + human review
**Date** : 2026-07-11
**Cycle** : Sx_DOGFOOD_01 Load Hint / Substitution Coherence
**Spec / Audit** : [`Sx_DOGFOOD_01_..._SPEC.md`](strategy/Sx_DOGFOOD_01_LOAD_HINT_SUBSTITUTION_COHERENCE_SPEC.md) + [`..._AUDIT_REPORT.md`](SPRINT_Sx_DOGFOOD_01_LOAD_HINT_SUBSTITUTION_COHERENCE_AUDIT_REPORT.md)
**Précondition** : Sx_DOGFOOD_01 audit/spec committé (`89ee684`) ✅.

---

## 0. Rappel dogfood

Une suggestion de charge (« Référence précédente », « Dernière fois », delta,
hints, briefing) n'est fiable que si elle correspond à **l'exercice réellement
exécuté**. `last_time_by_exercise_code` s'indexait sur le **slot**
(`exercise_code_snapshot`) sans regarder la substitution → il pouvait afficher la
charge d'un **autre exercice** (ex. Leg Press comme « dernière fois » du prescrit).

---

## 1. Étape 0 — Brainstorming / Options / Risques / Choix retenu

### Choix
**Option A** — patch de la **source unique** `last_time_by_exercise_code` (stats.py).

| Option | Verdict |
|---|---|
| **A** — filtrer les candidats historiques selon la substitution du slot courant ; contrat de retour inchangé ; les 5 surfaces héritent | ✅ **RETENU** |
| B — service central `exercise_load_identity` | 🔵 future (trop large) |
| C — masquer toute référence si une substitution existe | ❌ trop pessimiste (perd S4) |
| D — transfert de charge inter-machine N1/N2/N3 | ❌ rejeté V1 |

### Politique d'identité de charge (répliquée de `overload_inputs._matches_substitution_policy`)
- normalisation : `substituted_name` vide/whitespace → `None`, sinon strippé ;
- courant **prescrit** (sub None) → n'accepte que l'historique **prescrit** ;
- courant **substitué X** → n'accepte que l'historique **même X** exact ;
- sinon → **skip**, on continue à scanner les sessions plus anciennes ;
- aucun historique aligné → **absence** dans `last_time` (silence).

### Risques / parades
| Risque | Parade |
|---|---|
| 5 consommateurs changent en même temps | Contrat de retour inchangé ; couvert par tests S1→S5 + non-régression (85 verts) |
| Politique divergente d'overload | **Répliquée à l'identique** (même logique que `_matches_substitution_policy`) |
| S3/S5 : renvoyer le mauvais historique | Le filtre **ne marque pas** `result[code]` sur un incompatible → l'occurrence compatible plus ancienne peut encore matcher (testé) |
| `stats.py` importé ailleurs | `check_scope` → **SHARED_CODE** → full sweep exécuté |

**Aucun import cross-service** : la politique est répliquée localement pour garder
`stats.py` autonome (pas de dépendance sur `overload_inputs`).

---

## 2. Politique appliquée (matrice S1→S5, avant / après)

| Scénario | Avant | Après |
|---|---|---|
| **S1** prescrit → prescrit | ✅ charge prescrite | ✅ inchangé (charge prescrite) |
| **S2** prescrit → substitué | ❌ charge du prescrit affichée | ✅ **absent** (silence) |
| **S3** substitué → prescrit | ❌ charge de la substitution | ✅ **prescrit plus ancien** si existe, sinon **absent** |
| **S4** substitué(X) → substitué(X) | ✅ charge X | ✅ inchangé (charge X) |
| **S5** substitué(X) → substitué(Y) | ❌ charge X affichée | ✅ **Y plus ancien** si existe, sinon **absent** |

---

## 3. Changements effectués

### `app/services/stats.py` (MODIFIÉ — source unique)

- Docstring mise à jour (identité = `(template_slug, code, substitution_key)`).
- `_normalize_sub(name)` : vide/whitespace → `None`, sinon strippé.
- `_matches_current_substitution(past_sub, current_sub)` : politique substitution
  (identique à `overload_inputs._matches_substitution_policy`).
- `last_time_by_exercise_code` : construit `current_sub_by_code` (substitution
  normalisée par slot de la session courante) ; dans la boucle, **skip** les
  `prior` dont le code n'est pas dans la session courante ou dont la substitution
  ne matche pas la politique — en continuant à scanner pour une occurrence
  compatible plus ancienne. **Format de retour inchangé** (`dict[str, dict]`).
- `_summarise_prior` **non modifié**. Router **non modifié**.

---

## 4. Tests

### `tests/test_last_time_substitution.py` (NOUVEAU, 9 tests) — matrice S1→S5
S1 prescrit→prescrit · S2 prescrit→substitué (absent) · S3 récent substitué +
ancien prescrit → prescrit ; S3 seulement substitué → absent · S4 même substitut ·
S4 tolérance whitespace · S5 autre substitut seul → absent ; S5 ancien matchant →
retourné · contrat de retour inchangé.

### Non-régression
- `test_last_time.py` (prescrit→prescrit, exclusion, scoping, completed-only) : verts
  (tous S1, non affectés).
- `test_session_focus_logging_console`, `test_briefing_surface`,
  `test_overload_hint_render`, `test_ui06_dedup` : verts.
- **85 passed** sur le lot ciblé last_time + consommateurs.

### Checks
| check | résultat |
|---|---|
| `check_scope` | **SHARED_CODE** (stats.py importé ailleurs) → full sweep exécuté |
| `check_ruff_budget` | ✅ 543 ≤ 548 (mes annotations en `X \| None` ; 3 warnings préexistants non touchés) |
| `check_spec_protocol` | ✅ |
| Full sweep local (shared_code) | voir §Verdict (CI réelle fait foi si hang local) |

---

## 5. Invariants préservés

- **Contrat de retour `last_time` inchangé** (`dict[str, dict]` keyé par code) →
  les consommateurs (`last_time.get(se.exercise_code_snapshot)`) intacts.
- **Aucun** changement router / overload (inputs/engine/explainer) / body_map_descriptor
  / substitution graph / modèle / migration / schema / session creation / `value=`
  / JS / template / CSS / Body Intelligence.
- **Overload placeholders inchangés** (déjà substitution-aware).
- Silence plutôt que faux poids : aucune charge inter-exercice.

---

## 6. Fichiers modifiés (whitelist)

| Fichier | État |
|---|---|
| `app/services/stats.py` | MODIFIÉ (source unique) |
| `tests/test_last_time_substitution.py` | NOUVEAU (9 tests S1→S5) |
| `docs/SPRINT_Sb_DOGFOOD_01_1_LAST_TIME_SUBSTITUTION_AWARE_REPORT.md` | NOUVEAU |
| `docs/strategy/SPEC_REGISTRY.md` · `ROADMAP_AND_NEXT_STEPS.md` | MODIFIÉS |

Aucun modèle / migration / schema / router / overload / template / CSS touché.
Aucun artefact.

---

## 7. Limites

- Les surfaces dérivées (delta, hints Sx_08, chip, peek) héritent **automatiquement**
  de la cohérence via `last_time`, mais leur **vérification explicite de silence en
  S2/S3/S5** est le périmètre de `Sb_DOGFOOD_01.2`.
- La microcopy d'absence reste les états existants (« Non disponible » / « Aucune
  séance précédente ») — aucun nouveau bloc bavard ajouté (règle du brief).

---

## 8. Next step

- **`Sb_DOGFOOD_01.2`** — vérification/propagation consommateurs (delta, hints,
  chip, peek deviennent silencieux en S2/S3/S5), **ou**
- **`Sb_DOGFOOD_01.3`** — mobile placeholder proportion (CSS-only).

---

## Verdict

**Verdict :** 🟢 **Sb_DOGFOOD_01.1 livré — `last_time` substitution-aware, silence plutôt que faux poids, contrat inchangé — pending GO commit + CI + human review.**

`last_time_by_exercise_code` applique désormais la **même politique de substitution
que l'overload** : une charge précédente n'est affichée que si elle appartient à
l'exercice réellement exécuté (prescrit↔prescrit, substitué↔même substitut), sinon
**absence**. Les 5 scénarios S1→S5 sont couverts (9 tests), le contrat de retour est
inchangé (5 surfaces héritent), aucun router/overload/modèle/migration touché. Le
garde-fou a classé `shared_code` → full sweep exécuté. Prêt pour GO commit.
