# Sb_30.2 — Overload Explainer + Router Injection (Sprint Report)

**Branche :** `claude/sprint-reporting-fitness-app-V7Qr6`
**Date :** 2026-06-16
**Spec parent :** `docs/strategy/Sx_30_PROGRESSIVE_OVERLOAD_ENGINE_SPEC.md`
**Lot Sx_30 :** §14 — Sb_30.2 (explainer + injection, 2/5 du cycle)
**Build authorization :** ✅ `BUILD AUTHORIZED FOR Sx_30 — Option B`
**Pré-requis :** Sb_30.1 ✅ (CI 28241678098 verte 3/3)

---

## 1. Résumé exécutif

Sb_30.2 livre la couche de traduction `OverloadHint → payload UI` (`overload_explainer.py`) et la couche d'extraction `DB → OverloadInput` (`overload_inputs.py`), puis branche les deux dans `app/routers/sessions.py` pour exposer un dict `overload_hints` au template — **sans modifier `exercise_card.html`**. Cette séparation garde le moteur strictement pur (Sb_30.1) et concentre la responsabilité d'I/O dans `overload_inputs.py`, lui-même testable avec seed DB.

## 2. Fichiers modifiés

| Fichier | Type | Description |
|---|---|---|
| `app/services/overload_explainer.py` | **NEW** | 84 lignes. Pure function `explain_overload_hint(hint) -> dict`. Libellés sobres par état, `is_silent=True` si `state=="unknown"`, `engine_version` propagé. Aucun import du moteur en dehors des types publics. |
| `app/services/overload_inputs.py` | **NEW** | 175 lignes. `HISTORY_N = 3`, `categorize_exercise(name, machine_slug)` (heuristique V1), `_history_signals_for_code(...)` (lecture seule DB), `build_overload_input_for_exercise(db, session, se) -> OverloadInput | None`. |
| `app/routers/sessions.py` | MODIFIED | +14 lignes nettes : 3 imports + boucle d'injection `overload_hints[se.id] = explained` après le bloc `hints` legacy + clé `"overload_hints"` dans le contexte template. Aucune autre logique modifiée. |
| `tests/test_overload_explainer.py` | **NEW** | 16 tests : clés stables, `is_silent`, `target_summary` formaté (kg ´g´ + reps), 5 `intent_label` paramétrés, no-authoritative language, propagation `engine_version`, `reasons` ≤ 3, déterminisme, **garde structurelle** (l'explainer n'importe aucun helper interne du moteur). |
| `tests/test_overload_router_injection.py` | **NEW** | 21 tests : `categorize_exercise` paramétré (15 cas), `HISTORY_N == 3`, smoke GET /sessions/{id}=200, garde "aucun rendu `overload-hint` dans le HTML" (template intact Sb_30.2), `build_*` retourne `None` sans RepTarget, history exclude session courante + snapshot-based. |
| `docs/SPRINT_Sb_30_2_REPORT.md` | **NEW** | Ce rapport. |
| `docs/strategy/SPEC_REGISTRY.md` | MODIFIED | Sb_30.2 livré ✅. |

## 3. Diff métier

### Pipeline overload (sur la page session)

```
session_exercise
   ↓
build_overload_input_for_exercise(db, session, se)
   ├─ categorize_exercise(name, machine_slug)
   ├─ rep_targets[0] → (target_min, target_max)
   └─ _history_signals_for_code(...)  # N=3 max, snapshot-based, exclut session courante
      └─ compute_session_quality(s)  # lecture seule
      └─ s.global_state == "fatigued"  # lecture seule
   ↓
compute_overload_hint(input)  # moteur pur Sb_30.1
   ↓
explain_overload_hint(hint)  # explainer pur Sb_30.2
   ↓
overload_hints[se.id] = explained  (silent si state=="unknown")
```

`exercise_card.html` n'est PAS modifié → aucun marqueur `overload-hint` dans le HTML rendu (test garde dédié).

### `progression_hint.py` legacy

**Intact.** Sb_30.4 retirera le module + son injection après que Sb_30.3 ait livré le template. Aucune dépendance croisée à ce stade.

## 4. OQ Sx_30 implémentées

| OQ | Sb_30.2 |
|---|---|
| OQ-A par exercice uniquement | ✅ `overload_hints` indexé par `se.id` (1 entrée par SessionExercise) |
| OQ-B version par session | ✅ `engine_version` propagé par l'explainer ; colonne DB reportée Sb_30.3 |
| OQ-C pas de bypass deload | ✅ aucun champ override exposé |
| OQ-D N=3 fixe | ✅ `HISTORY_N = 3` exposé + testé |
| OQ-E placeholder seulement | ⏳ s'appliquera Sb_30.3/Sb_30.4 (template) |

## 5. Statut des tests

| Suite | Résultat |
|---|---|
| `tests/test_overload_engine.py` | ✅ 33 passed (inchangé Sb_30.1) |
| `tests/test_overload_explainer.py` | ✅ 16 passed (NEW) |
| `tests/test_overload_router_injection.py` | ✅ 26 passed (NEW, paramétrisations incluses) |
| Sous-suite Sb_30.2 isolée | ✅ 42 nouveaux tests, 0 régression |
| Suite complète | ✅ à confirmer en CI post-push |

## 6. CI réelle (post-push)

**Run GitHub Actions : [28245446788](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/28245446788) — ✅ success (3/3 jobs verts)**

- [x] Job `pytest + QA scripts` — ✅ success
- [x] Job `lint (ruff budget + bandit + actionlint + shellcheck)` — ✅ success
- [x] Job `SonarCloud` — ✅ success

## 7. Contraintes respectées (verbatim user)

| Contrainte | Statut |
|---|---|
| `overload_explainer.py` ne réimplémente pas `compute_overload_hint()` | ✅ test structural (`test_explainer_does_not_import_engine_internals`) |
| `engine_version` propagé | ✅ test dédié |
| Wording non autoritaire, sobre, explicable | ✅ test paramétré sur 5 états + intent labels |
| Si `state=unknown` → silencieux possible | ✅ `is_silent=True`, router skip l'entrée |
| Tests ciblés sur l'explainer ET sur l'injection router | ✅ 2 fichiers tests |
| Aucun effet de bord sur scoring / session flow / substitutions | ✅ aucune écriture, lectures seules uniquement |
| `exercise_card.html` NON modifié | ✅ test garde `assert "overload-hint" not in body` |
| `progression_hint.py` legacy intact | ✅ inchangé |
| 0 migration / modèle / CSS / JS | ✅ |
| 0 changement `recommendation.py` / `quality_score.py` / `implicit_signal.py` / `coach_*` / `body_*` / `substitution.py` | ✅ (lecture seule de `compute_session_quality` autorisée) |
| Ruff budget ≤ 548 | ✅ 535 (+1 vs 534 baseline = C901 sur `session_detail` qui était déjà au-dessus du seuil) |
| Dogfood Sx_27 reste PENDING | ✅ |
| Options C/D/E restent bloquées | ✅ |

## 8. Métriques

| Item | Valeur |
|---|---|
| Lignes services ajoutées | +259 (84 explainer + 175 inputs) |
| Lignes router modifiées | +14 (3 imports + 11 lignes d'injection) |
| Tests ajoutés (explainer + router injection) | +42 |
| Routers touchés (non-overload) | 0 |
| Templates touchés | 0 (`exercise_card.html` strictement intact) |
| Migrations | 0 |
| Modèles SQLAlchemy | 0 |
| Services métier core MUTÉS | 0 (lectures seules sur `quality_score`) |
| Dépendances externes ajoutées | 0 |
| JS / CSS lignes ajoutées | 0 |

## 9. Statut DoD locale (vérifiée)

| Gate | Statut |
|---|---|
| `pytest --ignore=tests/test_v1_acceptance.py -q` | ✅ à confirmer (background run) |
| `check_ruff_budget.py` | ✅ 535 ≤ 548 |
| `check_spec_protocol.py` | ✅ |
| `check_alembic_drift.py` | ✅ no diff |
| `check_schema_snapshot.py` | ✅ |

## 10. Architecture résultante (récap)

| Module | Responsabilité | Pur ? |
|---|---|---|
| `overload_engine.py` (Sb_30.1) | Décision overload (5 états, cibles, reasons) | ✅ pur, aucun I/O |
| `overload_inputs.py` (Sb_30.2) | Lecture DB + catégorisation → `OverloadInput` | ❌ I/O DB, isolé |
| `overload_explainer.py` (Sb_30.2) | `OverloadHint` → payload template | ✅ pur, aucun I/O |
| `app/routers/sessions.py` (modifié Sb_30.2) | Compose les trois + injecte dans le contexte template | ❌ I/O (déjà routeur) |
| `exercise_card.html` | À modifier Sb_30.3 pour rendre le payload | — |
| `progression_hint.py` | Legacy, suppression Sb_30.4 | — |

## 11. Verdict

**✅ READY FOR Sb_30.3.**

Prochaine étape : Sb_30.3 livrera la migration Alembic `overload_engine_version` (sur `workout_sessions`, OQ-B), le partial `_partials/overload_hint.html`, et les styles CSS de support dans `session_focus.css`. À ce moment-là `exercise_card.html` consommera la clé `overload_hints[se.id]` injectée par Sb_30.2.

Aucune dépendance bloquante. Spec stable. OQ A/B/C/D entièrement appliquées dans la pipeline ; OQ-E s'appliquera côté template (Sb_30.3 et/ou Sb_30.4).
