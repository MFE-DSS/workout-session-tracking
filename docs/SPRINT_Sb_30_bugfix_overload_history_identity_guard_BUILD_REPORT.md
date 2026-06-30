# Sb_30.bugfix.history-identity-guard — Overload History Identity Fix (Build Report)

**Branche :** `claude/sprint-reporting-fitness-app-V7Qr6`
**Date :** 2026-06-30
**Type :** **BUGFIX critique** sur Sx_30 post-closure (dogfood réel)
**Pré-requis :** Sx_30 TECHNICALLY CLOSED + dogfood en cours
**Surface impactée :** `app/services/overload_inputs.py` (couche I/O Sx_30)

---

## 1. Résumé exécutif

Bug critique remonté en dogfood Sx_30 : sur "Élévations latérales câble épaules", l'overload hint proposait *"Consolider la charge actuelle"* autour de **57 kg** alors que "Dernière fois" affichait **5 kg** (ratio ×10). Cause racine confirmée : `_history_signals_for_code` filtrait uniquement par `user_id + status + exercise_code_snapshot`, agrégeant des `SessionExercise` venant de **templates différents** partageant le même code (ex. `E2`). Le fix aligne l'identité historique overload sur celle de `last_time_by_exercise_code` (`template_slug_snapshot + exercise_code_snapshot`) et introduit une politique de substitution V1 conservatrice + un garde-fou d'écart aberrant.

**Aucune modification** de `overload_engine.py`, `overload_explainer.py`, `scoring`, `substitution.py`, `recommendation.py`, `body_intelligence*`. Aucune migration. Aucun JS.

## 2. Cause racine confirmée

### 2.1 Données VPS (dogfood réel)

| Session | Template | Code | Exercice | Sub | First weight |
|---|---|---|---|---|---|
| 27, 41, 43, 46, 56 | `push-a` / `catch-up-shoulders` | E5 / E2 | Élévations latérales câble | (None) | **5.0 kg** ✅ |
| 58 | `pull-b` | E2 | Rowing câble assis prise neutre | Rowing câble assis prise serrée | **57.0 kg** |
| 33 | `push-a` | E1 | Incline Smith Press | (None) | **57.5 kg** |
| 38 | `catch-up-back-width` | E1 | Tirage poulie haute | (None) | **57.0 kg** |

### 2.2 Chemin du bug

1. **`last_time_by_exercise_code`** (`stats.py:118`) filtre proprement par
   `template_slug_snapshot == current.template_slug_snapshot` → "Dernière fois" lit le bon 5 kg.
2. **`_history_signals_for_code`** (`overload_inputs.py:89` avant fix) ne filtrait que par `user_id + status + exercise_code_snapshot`. Sur une séance `catch-up-shoulders E2` (5 kg), il agrégeait aussi `pull-b E2` (57 kg sub) et `push-a E2` (Chest Press, 30/42.5 kg).
3. **Substitution** : la séance 58 (`pull-b E2`) a `substituted_name = "Rowing câble assis prise serrée"`. Le builder lisait `first_set.weight_kg = 57.0` sans distinguer prescrit/substitué.
4. **Pipeline** : `compute_overload_hint` reçoit une cohorte 57/47/40 kg → trigger `consolidate` à 57 kg → l'UI affiche "Consolider la charge actuelle" + placeholder `≈ 57`.

### 2.3 Pourquoi les deux surfaces divergeaient

`last_time` partageait l'identité `(template_slug, code)` → 5 kg correct. `_history_signals_for_code` partageait l'identité `(code)` seule → contamination inter-template. Les deux surfaces n'avaient pas le même filtre.

## 3. Fichiers modifiés

| Fichier | Type | Description |
|---|---|---|
| `app/services/overload_inputs.py` | MODIFIED | +85 lignes nettes. Signature `_history_signals_for_code` étendue (`template_slug_snapshot`, `current_is_substituted`, `current_substituted_name`). Nouveau helper `_matches_substitution_policy`. Nouveau helper `_history_weight_is_plausible` + constante `_IMPLAUSIBLE_WEIGHT_RATIO = 3.0`. `build_overload_input_for_exercise` enrichi : early-return `None` si séance courante substituée, propagation `template_slug` + politique. |
| `tests/test_overload_history_identity_guard.py` | **NEW** | 11 tests : collision inter-template (2), alignement `last_time` (1), prescrit vs substitut passé (1), substitut courant silent V1 (2), changement d'alternative (1), garde-fou aberrant (2), non-régression cas normal (2). |
| `docs/SPRINT_Sb_30_bugfix_overload_history_identity_guard_BUILD_REPORT.md` | **NEW** | Ce rapport. |
| `docs/strategy/SPEC_REGISTRY.md` | MODIFIED | Entrée bugfix ajoutée. |

### Non modifiés (vérification explicite)
- `app/services/overload_engine.py` (composer Sb_30.1, `BODY_INTELLIGENCE_VERSION` sans rapport, mais sentinelle ici = `OVERLOAD_ENGINE_VERSION = 1` préservée)
- `app/services/overload_explainer.py`
- `app/services/quality_score.py`, `implicit_signal.py`, `confidence.py`, `coach_report.py`, `substitution.py`, `recommendation.py`, `body_intelligence*`
- `app/routers/sessions.py`, `app/routers/body_intelligence.py`, etc.
- Tous les templates, CSS, JS
- Aucune migration

## 4. Règles d'identité historique retenues (V2)

```
historical (template_slug_snapshot, exercise_code_snapshot, substitution_policy)
```

| Critère | Avant (bug) | Après (fix) |
|---|---|---|
| `user_id` | ✅ | ✅ |
| `status == completed` | ✅ | ✅ |
| `id != current_session.id` | ✅ | ✅ |
| `template_slug_snapshot == current.template_slug_snapshot` | ❌ | ✅ **(nouveau)** |
| `exercise_code_snapshot == current.exercise_code_snapshot` | ✅ | ✅ |
| Politique substitution | ❌ | ✅ **(nouveau, cf. §5)** |

Si `current_session.template_slug_snapshot` est vide / falsy → `build_overload_input_for_exercise` retourne `None` (sans identité de template, pas de garantie anti-collision).

## 5. Politique substitution V1

| Cas | Avant (bug) | Après (fix V1) |
|---|---|---|
| Courant **prescrit** (`substituted_name is None`) | Consommait tous les historiques (prescrit + substitut mixés) | Consomme **uniquement** les rows passées avec `substituted_name IS NULL` |
| Courant **substitué** (`substituted_name = "Variante X"`) | Recevait mécaniquement la cible du prescrit | **Retourne `None`** → hint silent → aucune cible chiffrée affichée |

**Justification du V1 conservateur sur substitut courant** : la régression inverse (laisser passer la cible du prescrit sur un substitut) est plus dangereuse que de masquer le hint. Un sprint futur pourra raffiner avec un match strict sur `substituted_name` exact (le code de `_matches_substitution_policy` le supporte déjà — il suffira d'enlever l'early-return du builder).

## 6. Garde-fou d'écart aberrant

Constante :
```python
_IMPLAUSIBLE_WEIGHT_RATIO = 3.0  # max/min des poids non-nuls dans la fenêtre
```

Logique :
```python
def _history_weight_is_plausible(signals):
    weights = [s.weight_kg for s in signals if s.weight_kg and s.weight_kg > 0]
    if len(weights) < 2:
        return True   # 0-1 entrée → pas d'aberrance
    lo, hi = min(weights), max(weights)
    if lo <= 0:
        return True
    return (hi / lo) <= _IMPLAUSIBLE_WEIGHT_RATIO
```

Si la cohorte historique présente un ratio max/min > 3× malgré tous les filtres ci-dessus, l'historique est retourné **vide** (`tuple()`). Le builder produit un `OverloadInput` avec `history=()` → `compute_overload_hint` retourne `unknown` → `explain_overload_hint` marque `is_silent=True` → l'UI ne propose **aucune** cible chiffrée.

Justification : défense en profondeur contre tout futur bug de filtrage. Le ratio 3× est tolérant aux deload progressifs (typiquement 0.9×) et aux progressions normales (1.025-1.05×), mais coupe les contaminations à ×5 ou ×10 comme celle observée.

## 7. Tests ajoutés (11 cas dédiés)

| # | Test | Couverture |
|---|---|---|
| 1 | `test_collision_across_templates_does_not_leak` | Reproduit le bug exact : E2 sur 2 templates différents, courant sur template A à 5 kg, historique ne contient que 5 kg (jamais 57 kg) |
| 2 | `test_overload_hint_never_proposes_aberrant_weight_after_fix` | Round-trip jusqu'au hint : `target_weight_kg < 15 kg`, jamais 57 kg |
| 3 | `test_overload_history_aligns_with_last_time` | `last_time_by_exercise_code` et l'overload renvoient le même premier work set sur même `(template, code)` |
| 4 | `test_prescribed_does_not_consume_substituted_history` | Prescrit courant ignore les historiques substitués (5 substitués à 80 kg + 1 prescrit à 40 kg → history contient 40, pas 80) |
| 5 | `test_substituted_current_returns_none_v1` | Substitut courant → `build_overload_input_for_exercise` renvoie `None` |
| 6 | `test_substituted_current_produces_silent_hint_in_pipeline` | Substitut courant + pipeline → `is_silent=True` |
| 7 | `test_two_different_substitutes_do_not_share_history` | 2 substituts différents (Variante A, Variante B) → tous deux `None` (V1 cap) |
| 8 | `test_implausible_history_drops_input_silently` | Cohorte 57+5+5 (ratio 11.4×) → history vide |
| 9 | `test_implausible_guard_produces_silent_hint_in_pipeline` | Même cohorte → hint = `unknown`, `is_silent=True` |
| 10 | `test_normal_same_template_prescribed_still_produces_hint` | Cas nominal : 2 séances 100 kg × 10 reps → hint non-`unknown` (non-régression) |
| 11 | `test_existing_overload_smoke_session_detail_still_200` | GET `/sessions/{id}` reste 200 sur cas normal (smoke pipeline complète) |

## 8. Statut tests complet

| Suite | Résultat |
|---|---|
| `tests/test_overload_history_identity_guard.py` (Sb_30.bugfix) | ✅ 11 passed |
| `tests/test_overload_engine.py` (Sb_30.1) | ✅ 33 non régressé |
| `tests/test_overload_explainer.py` (Sb_30.2) | ✅ 16 non régressé |
| `tests/test_overload_router_injection.py` (Sb_30.2) | ✅ 26 non régressé |
| `tests/test_overload_hint_render.py` (Sb_30.3 + Sb_30.4) | ✅ 16 non régressé |
| `tests/test_overload_engine_version_migration.py` (Sb_30.3) | ✅ 5 non régressé |
| `tests/test_overload_hint_a11y.py` (Sb_30.5) | ✅ 13 non régressé |
| `tests/test_overload_placeholder.py` (Sb_30.next) | ✅ 13 non régressé |
| **Sous-suite Sx_30 + bugfix** | ✅ **134 passed** |
| Suite complète locale | ⏳ background |
| Ruff | ✅ 529 ≤ 548 (inchangé) |
| Spec protocol | ✅ |
| Alembic drift | ✅ no diff |

## 9. CI réelle (post-push)

À renseigner après push.

- [ ] Job `pytest + QA scripts` — vert attendu
- [ ] Job `lint (ruff budget + bandit + actionlint + shellcheck)` — vert attendu
- [ ] Job `SonarCloud` — vert attendu

## 10. Contraintes respectées (verbatim user)

| Contrainte | OK |
|---|---|
| Aligner l'identité historique avec `last_time` (template + code) | ✅ |
| Filtrer par `template_slug_snapshot` | ✅ |
| Filtrer par politique substitution | ✅ V1 conservateur (substitut courant → None) |
| Garde-fou contre charges aberrantes | ✅ ratio 3× |
| `overload_engine.py` inchangé | ✅ |
| `overload_explainer.py` inchangé | ✅ |
| Scoring inchangé | ✅ |
| `substitution.py` inchangé | ✅ |
| `recommendation.py` inchangé | ✅ |
| `body_intelligence*` inchangés | ✅ |
| Aucune migration | ✅ |
| Aucun JS | ✅ |
| Aucune nouvelle UX lourde | ✅ |
| Aucun LLM / API externe | ✅ |

## 11. Verdict

**✅ Bugfix livré. Dogfood Sx_30 peut reprendre.**

Cause racine identifiée et corrigée à 3 niveaux :
1. **Identité template** (filtre `template_slug_snapshot`) — racine du bug 5 vs 57 kg.
2. **Politique substitution V1** (substitut courant → silent) — empêche le mélange prescrit/substitut.
3. **Garde-fou aberrant** (ratio 3×) — défense en profondeur contre tout futur leak.

11 tests dédiés couvrent les 3 niveaux + le scénario exact du bug + non-régression du cas nominal. La sous-suite Sx_30 complète (134 tests) reste verte. Aucune surface UX cassée. Aucune dette technique ajoutée.

L'opérateur peut reprendre le dogfood Sx_30 (template `docs/dogfood/DOGFOOD_Sx_30_OVERLOAD_ENGINE_TEMPLATE.md`) en confiance. Si un nouveau cas tombe en aberrance (ratio > 3×), le hint sera silencieux par défaut plutôt que trompeur.

**Note prospective** : un raffinement V2 (`Sb_30.next.substitution-history`) pourrait permettre aux substituts courants de consommer l'historique de leurs propres substitutions passées (match strict sur `substituted_name`). Le code `_matches_substitution_policy` est déjà prêt pour ce cas — il suffira de retirer l'early-return dans le builder. À évaluer après dogfood Sx_30 PASS.
