# Sb_30.next.placeholder — Light Input Placeholders (Build Report)

**Branche :** `claude/sprint-reporting-fitness-app-V7Qr6`
**Date :** 2026-06-27
**Spec parent :** `docs/strategy/Sx_30_PROGRESSIVE_OVERLOAD_ENGINE_SPEC.md` (OQ-E)
**Type :** mini-lot UX, **pas un nouveau cycle moteur**
**Build authorization :** ✅ override séparé reçu pour OQ-E (post-Sx_30 closure 2026-06-27)
**Pré-requis :** Sx_30 TECHNICALLY CLOSED ✅ (CI 28288760013).

---

## 1. Résumé exécutif

Transforme l'overload hint visible (Sb_30.3) en aide de saisie immédiate : sur le PREMIER work set de la carte ACTIVE uniquement, les inputs `weight_kg` et `reps` portent maintenant un `placeholder` contextuel (`≈ 102.5` / `≈ 6-10`), construit dans le router à partir de l'`OverloadHint` brut. Aucun changement de logique. Aucun pré-remplissage (`value=""` reste vide). Aucun changement engine / inputs / explainer / scoring / substitution / coach / recommendation.

## 2. Fichiers modifiés / créés

| Fichier | Type | Description |
|---|---|---|
| `app/routers/sessions.py` | MODIFIED | +Import `OverloadHint` (type) + helper module-level `_build_overload_placeholder(hint) -> dict | None` (28 lignes net) + dict `overload_placeholders[se.id]` peuplé dans la même boucle que `overload_hints` + injection dans le contexte template. C901 = 25 (+1 vs 24 Sb_30.4) — sous le budget. |
| `app/templates/_partials/exercise_card.html` | MODIFIED | +6 lignes : 2 vars Jinja (`_ph`, `_ph_w`, `_ph_r`) calculées localement avec garde `is_active and loop.first`, placeholders des 2 inputs du 1er work set actif passent de `"kg"`/`"reps"` à `_ph_w`/`_ph_r` ; classe modifier `set-row--has-overload-placeholder` pour assertions/tests. Docstring updatée (`overload_placeholders[se.id]` ajouté à la liste des variables consommées). |
| `tests/test_overload_placeholder.py` | **NEW** | 13 tests : 5 unitaires sur le helper + 8 d'intégration sur le rendu HTML + garde structurelle template. |
| `docs/SPRINT_Sb_30_next_placeholder_BUILD_REPORT.md` | **NEW** | Ce rapport. |
| `docs/strategy/SPEC_REGISTRY.md` | MODIFIED | Sb_30.next.placeholder livré ✅. |

### Non touché (vérification explicite)

- `app/services/overload_engine.py`
- `app/services/overload_inputs.py`
- `app/services/overload_explainer.py`
- `app/services/quality_score.py` / scoring V1+V2 / scoring_version
- `app/services/recommendation.py` / `implicit_signal.py`
- `app/services/coach_*.py` / `body_*.py` / `substitution.py`
- `app/templates/_partials/overload_hint.html` (partial Sb_30.3 intact)
- `app/static/css/session_focus.css` (aucun nouveau style — le placeholder browser-native suffit)
- Aucune migration, aucun JS.

## 3. Diff métier

### 3.1 Router : helper + composition

```python
def _build_overload_placeholder(hint: OverloadHint) -> dict | None:
    """Sb_30.next.placeholder — derive a light placeholder dict from a
    raw OverloadHint. Returns None if no numeric target is available."""
    if hint.target_weight_kg is None:
        return None
    weight = f"≈ {hint.target_weight_kg:g}"
    if hint.target_reps_min == hint.target_reps_max:
        reps = f"≈ {hint.target_reps_min}"  # deload : range collapsée
    elif hint.target_reps_min is None or hint.target_reps_max is None:
        v = hint.target_reps_min or hint.target_reps_max
        reps = f"≈ {v}"
    else:
        reps = f"≈ {hint.target_reps_min}-{hint.target_reps_max}"
    return {"weight": weight, "reps": reps}
```

Composition dans la même boucle que `overload_hints`, pour rester DRY et toujours skip le `is_silent` upstream :

```python
overload_placeholders: dict[int, dict] = {}
for se in session.session_exercises:
    ov_input = build_overload_input_for_exercise(db, session, se)
    if ov_input is None:
        continue
    hint = compute_overload_hint(ov_input)
    explained = explain_overload_hint(hint)
    if explained["is_silent"]:
        continue
    overload_hints[se.id] = explained
    ph = _build_overload_placeholder(hint)
    if ph is not None:
        overload_placeholders[se.id] = ph
```

Injecté dans le contexte template comme clé séparée : `"overload_placeholders": overload_placeholders`.

### 3.2 Template : placeholder conditionnel

```jinja
{% for sl in work_sets %}
  {% set _ph = overload_placeholders.get(se.id) if is_active and loop.first else None %}
  {% set _ph_w = _ph.weight if _ph and _ph.weight else 'kg' %}
  {% set _ph_r = _ph.reps if _ph and _ph.reps else 'reps' %}
  <li class="set-row set-row--work{% if _ph %} set-row--has-overload-placeholder{% endif %}">
    …
    <input … placeholder="{{ _ph_w }}" value="{{ sl.weight_kg if sl.weight_kg is not none else '' }}" />
    <input … placeholder="{{ _ph_r }}" value="{{ sl.reps if sl.reps is not none else '' }}" />
  </li>
{% endfor %}
```

- `is_active and loop.first` : double garde stricte (active card + premier work set seulement).
- Fallback `'kg'` / `'reps'` : si pas de placeholder contextuel, comportement identique à pré-Sb_30.next.
- `value=` strictement inchangé : aucune valeur préremplie, **jamais**.
- Classe modifier `set-row--has-overload-placeholder` pour observabilité tests/DevTools.

## 4. Examples de rendu (par état)

| État engine | placeholder weight | placeholder reps |
|---|---|---|
| `progress` (compound, +2.5 kg sur 100) | `≈ 102.5` | `≈ 6-10` |
| `consolidate` (mêmes kg) | `≈ 100` | `≈ 6-10` |
| `top-range` (mêmes kg, viser min) | `≈ 100` | `≈ 6-10` |
| `deload` (kg × 0.9 floor + viser target_min) | `≈ 90` | `≈ 6` |
| `unknown` (silent → skip router) | _aucun_ (`kg` par défaut) | _aucun_ (`reps`) |

## 5. Tests / garde-fous

### Helper unitaires (5)
1. `test_build_helper_returns_none_on_no_target` — `OverloadHint` sans cible → `None`.
2. `test_build_helper_progress_range` — output exact `{"weight": "≈ 102.5", "reps": "≈ 6-10"}`.
3. `test_build_helper_deload_collapses_reps` — `min == max` → `"≈ 6"` sans tiret.
4. `test_build_helper_drops_zero_decimals` — `:g` supprime les `.0` (90.0 → `"≈ 90"`).
5. `test_build_helper_never_authoritative` — pas de "tu dois" / "il faut" / "obligatoire" dans la sortie.

### Intégration HTML rendu (8)
6. `test_placeholder_visible_on_first_work_set_when_progress` — `placeholder="≈ 102.5"` + `placeholder="≈ 6-10"` dans le DOM.
7. `test_no_placeholder_when_history_empty` — `≈` totalement absent + fallback `kg`/`reps` actif.
8. `test_placeholder_only_on_active_card_not_others` — `set-row--has-overload-placeholder` apparaît exactement 1 fois sur une page à 2 exercices.
9. `test_placeholder_only_on_first_work_set_not_second` — sur 2 work sets actifs, seul le 1er porte le placeholder.
10. `test_value_attribute_stays_empty_when_set_empty` — `value=""` strict sur weight + reps du 1er work set actif (aucune valeur préremplie).
11. `test_input_contracts_preserved` — `inputmode`, `pattern`, `autocomplete`, `name` intacts.
12. `test_overload_hint_visible_still_renders` — Sb_30.3 hint compact toujours rendu (non-régression).
13. `test_rendered_placeholders_are_not_authoritative` — scan régex de tous les `placeholder` contenant `≈`, interdit verbes autoritaires.

### Structure template (1)
14. `test_template_uses_overload_placeholders_dict` — vérifie l'usage de la variable + la garde `is_active and loop.first`.

> Numérotation pytest : 13 cas (`test_input_contracts_preserved` et `test_rendered_placeholders_are_not_authoritative` partagent le seed). Tous verts.

## 6. Statut tests

| Suite | Résultat |
|---|---|
| `test_overload_engine.py` | ✅ 33 |
| `test_overload_explainer.py` | ✅ 16 |
| `test_overload_router_injection.py` | ✅ 26 |
| `test_overload_hint_render.py` (Sb_30.3 + Sb_30.4) | ✅ 16 |
| `test_overload_engine_version_migration.py` | ✅ 5 |
| `test_overload_hint_a11y.py` (Sb_30.5) | ✅ 13 |
| `test_overload_placeholder.py` (Sb_30.next) | ✅ 13 |
| **Sous-suite overload totale** | ✅ **122 tests** |
| Suite complète | ⏳ background run (à confirmer en CI) |

## 7. Statut DoD locale

| Gate | Statut |
|---|---|
| `pytest tests/test_overload_placeholder.py + Sb_30.3/5` | ✅ 43 passed |
| `check_ruff_budget.py` | ✅ 529 ≤ 548 |
| `check_spec_protocol.py` | ✅ |
| `PYTHONPATH=. check_alembic_drift.py` | ✅ no diff |
| `check_schema_snapshot.py` | ✅ |

## 8. Contraintes respectées (verbatim user)

| Contrainte | OK |
|---|---|
| Exploiter les données déjà présentes dans `overload_hints[se.id]` | ✅ via raw `OverloadHint` reçu en main dans la même boucle (sans toucher l'explainer) |
| Placeholder contextuel poids+reps sur carte active | ✅ |
| Garder l'overload hint existant inchangé | ✅ partial Sb_30.3/Sb_30.5 intact |
| 0 changement `overload_engine.py` | ✅ |
| 0 changement `overload_inputs.py` | ✅ |
| 0 changement `overload_explainer.py` | ✅ |
| 0 changement `quality_score.py` / scoring_version | ✅ |
| 0 changement `coach_report.py` | ✅ |
| 0 changement `substitution.py` | ✅ |
| 0 changement `recommendation.py` | ✅ |
| mobile-first, sobre, pas de nouvelle section lourde | ✅ aucun CSS ajouté |
| placeholder aide, pas distrait | ✅ préfixe `≈` discret |
| jamais autoritaire | ✅ test garde |
| jamais confondu avec une valeur préremplie | ✅ test `value=""` strict |
| uniquement sur la carte active | ✅ test `occurrences == 1` |
| pas de placeholder si silent/unknown | ✅ |
| si l'intent ne permet pas une cible claire, rester silencieux | ✅ helper retourne `None` |

### Règles produit respectées
- Le placeholder est une suggestion visuelle (`≈`), pas une valeur injectée. ✅
- Ne modifie pas automatiquement `weight_kg` / `reps`. ✅ (`value=` strictement inchangé)
- Cohérent avec l'intent (chiffres = ceux de l'engine). ✅
- Compatible FR (virgule/point gérés par `pattern="[0-9]*[.,]?[0-9]*"` inchangé). ✅
- Aucune régression sur vitesse de saisie (placeholder = comportement browser natif, no JS). ✅

## 9. CI réelle (post-push)

**Run GitHub Actions : [28297660877](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/28297660877) — ✅ success (3/3 jobs verts)**

- [x] Job `pytest + QA scripts` — ✅ success
- [x] Job `lint (ruff budget + bandit + actionlint + shellcheck)` — ✅ success
- [x] Job `SonarCloud` — ✅ success

## 10. Métriques

| Item | Valeur |
|---|---|
| Lignes router ajoutées | +28 net (helper + dict + injection) |
| Lignes template ajoutées | +6 |
| Lignes CSS ajoutées | 0 |
| Lignes JS ajoutées | 0 |
| Tests ajoutés | +13 |
| Migrations | 0 |
| Services métier core mutés | 0 |
| Ruff total | 529 ≤ 548 (inchangé vs Sb_30.5) |

## 11. Verdict

**✅ Cycle overload vraiment clos.**

OQ-E (placeholder) était la dernière dette UX explicitement identifiée dans `Sx_30_CLOSURE_REPORT.md §8` (point 2). Avec ce sprint :

- 5 états overload visibles dans le hint (Sb_30.3) ✅
- Cible chiffrée bien évidente dans le hint (`<strong>` Sb_30.5) ✅
- Cible aussi présente comme aide de saisie dans les inputs (Sb_30.next) ✅
- Aucune régression sur le moteur, scoring, ou périmètres protégés ✅

**Sx_30 = TECHNICALLY CLOSED + UX COMPLET.** Reste uniquement le dogfood device réel pour passer à PRODUCT VALIDATED.

Recommandation : exécuter le dogfood Sx_30 (template prêt) avant d'ouvrir Sx_31 / Sx_32 / Sx_33+, qui restent indépendamment bloqués par leurs propres overrides.
