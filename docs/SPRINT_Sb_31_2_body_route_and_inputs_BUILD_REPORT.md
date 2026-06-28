# Sb_31.2 — Body Intelligence v2 : Route /body/intelligence + couche I/O (Build Report)

**Branche :** `claude/sprint-reporting-fitness-app-V7Qr6`
**Date :** 2026-06-28
**Spec parent :** `docs/strategy/SPIGNOS_BODY_INTELLIGENCE_V2_SPEC.md`
**Lot Sx_31 :** §N.2 — Sb_31.2 (route + I/O, 2/5 du cycle)
**Build authorization :** ✅ `BUILD AUTHORIZED FOR Sx_31` (override #4)
**Pré-requis :** Sb_31.1 ✅ (CI 28302706112, composeur pur livré)

---

## 1. Résumé exécutif

Première surface utilisateur Body Intelligence v2 livrée. Trois briques :
1. **Couche I/O lecture seule** `body_intelligence_inputs.py` qui compose les services existants (`profile_metrics`, `coach_report`, `quality_score`, `confidence`, `muscle_mapping`, `BodyMeasurement`, `User`) en un `BodyIntelligenceInput` pur.
2. **Route SSR** `GET /body/intelligence` (collision résolue : `/body` appartient au track parallèle Body Manual Profile via PR #15).
3. **Template** `body_intelligence.html` + 2 partials + CSS dédié `body_intelligence.css` — mobile-first, no-JS, marqueurs Mesuré/Dérivé/Inféré/Hors de portée visibles sur chaque bloc, status global avec cue non-color.

Le router se borne strictement à orchestrer : `build_body_intelligence_input → compute_body_intelligence → template`. Aucune logique métier dans le router ni dans le template. Aucune mutation. Aucune migration. Aucun nouveau JS.

## 2. Fichiers créés / modifiés

| Fichier | Type | Description |
|---|---|---|
| `app/services/body_intelligence_inputs.py` | **NEW** | Couche I/O lecture seule (240 lignes). Compose profile_metrics + coach_report private helpers + quality_score + confidence + BodyMeasurement + User. Wrappers `_safe(fn, ...)` qui retournent `None` plutôt que crasher. Mapping zone détaillée → 6 axes radar canoniques. |
| `app/routers/body_intelligence.py` | **NEW** | Router minimal (47 lignes) : 1 route `GET /body/intelligence`, 0 endpoint JSON public. Orchestre uniquement input → composer → template. |
| `app/main.py` | MODIFIED | +2 lignes : import `body_intelligence` + `app.include_router(body_intelligence.router)`. Aucune autre mutation. |
| `app/templates/body_intelligence.html` | **NEW** | Template principal (69 lignes). Affiche headline + bullets + priorités + 7 blocs + footer. Charge `body_intelligence.css` via `{% block extra_head %}`. |
| `app/templates/_partials/body_intelligence_block.html` | **NEW** | Partial bloc (122 lignes). Rendu par `block.key` avec marqueur classification visible. Aucune logique métier ; lecture pure de `block.content`. |
| `app/templates/_partials/body_intelligence_priority.html` | **NEW** | Partial priorité (18 lignes). Message + `<details>` natif pour la raison. |
| `app/static/css/body_intelligence.css` | **NEW** | CSS dédié, extrait/scoped (~230 lignes). Mobile-first, non-color cues sur status et classification, media query `< 380px`. |
| `tests/test_body_intelligence_inputs.py` | **NEW** | 11 tests : structure, sessions count, body metrics (priorité BodyMeasurement vs user, fallback), no DB mutation, no priorities, no overload compliance, garde structurelle import. |
| `tests/test_body_intelligence_route.py` | **NEW** | 19 tests : existence + structure des fichiers, smoke 200, status rendu, 7 blocs présents, labels classification, cap priorités ≤ 3, limits always-on, wording interdit, CSS chargé, garde anti-logique métier dans template/router, garde no-JS/no-migration. |
| `docs/SPRINT_Sb_31_2_body_route_and_inputs_BUILD_REPORT.md` | **NEW** | Ce rapport. |
| `docs/strategy/SPEC_REGISTRY.md` | MODIFIED | Sb_31.2 livré ✅. |

### Non touché (vérification explicite)
- `app/services/body_intelligence.py` (Sb_31.1, composer pur intact)
- `app/services/profile_metrics.py`, `muscle_scoring.py`, `quality_score.py`, `implicit_signal.py`, `confidence.py`, `coach_report.py`, `radar.py`, `overload_*`, `substitution.py`, `recommendation.py`, `body_tracking.py`
- `app/models/*`, `migrations/*`
- `app/routers/body.py` (track parallèle Body Manual Profile, **inchangé**)
- Aucun lien `/profile` → `/body/intelligence` ajouté (différé volontairement, l'éventuel changement est trivial mais hors scope Sb_31.2).
- `app/static/js/*` strictement intact (0 nouveau JS).

## 3. Diff métier

### 3.1 Sources de données réellement branchées

| Champ `BodyIntelligenceInput` | Source réelle |
|---|---|
| `sessions_7d/30d/90d` | Comptage `WorkoutSession` `status==completed` et `excluded_from_stats==False` filtré par fenêtre |
| `work_sets_per_week_30d` | `coach_report._work_sets_per_week(db, user_id, 30)` |
| `cardio_minutes_per_week_30d` | `profile_metrics.cardio_minutes_per_week(db, user_id, 30)` |
| `strength_volume_delta_pct_30d` | `profile_metrics.strength_volume_delta_pct(db, user_id, 30)` |
| `zone_session_counts_30d` | `profile_metrics.zone_session_counts(db, user_id, 30)` réagrégé sur 6 axes radar canoniques |
| `dominant_pattern_30d` | `profile_metrics.dominant_pattern(db, user_id, 30)` |
| `pattern_distribution_30d` | `profile_metrics.pattern_distribution(db, user_id, 30)` |
| `quality_score_avg_30d` + `quality_score_n` | Moyenne `quality_score.compute_session_quality(s)` sur sessions 30j |
| `confidence_score_avg` | Moyenne `confidence.compute_confidence_score(s)` sur sessions 30j |
| `implicit_labels_30d` | Compte des `SessionExercise.implicit_label` ≠ None sur sessions 30j |
| `body_height_cm` | `User.height_cm` (statique, non daté) |
| `body_weight_kg` + `body_weight_measured_at_iso` | `BodyMeasurement.weight_kg` le plus récent ; fallback `User.weight_kg` (sans date) |
| `waist_cm` | `BodyMeasurement.waist_cm` le plus récent ; fallback `User.waist_cm` |
| `weight_trend_90d_kg` | `coach_report._weight_trend_90d(db, user_id)` |

### 3.2 Sources de données *intentionnellement* non branchées V1

| Champ potentiel | Raison |
|---|---|
| `users.resting_hr`, `bp_*` | Hors scope V1 (cf. spec §B.1) — cardio readiness, futur |
| Overload compliance agrégée | Différé `Sb_31.next.overload-compliance` (cf. spec §G.5) |
| Asymétrie L/R (arm_cm_left/right, thigh_*) | Bruit > signal sur 1-2 mesures (cf. spec §E.4) |
| Composition corporelle | Non déductible structurellement |
| HealthKit / Health Connect | Hors scope (Sx_33+) |
| Photos / scans | Track parallèle Body Signal Model |

### 3.3 API de `body_intelligence_inputs.py`

```python
from app.services.body_intelligence_inputs import build_body_intelligence_input

inp: BodyIntelligenceInput = build_body_intelligence_input(db, user)
# → snapshot prêt à être passé à compute_body_intelligence(inp)
```

**Helpers privés exposés** (testables) : `_sessions_count_in_window`, `_completed_sessions_30d`, `_quality_avg_30d`, `_confidence_avg_30d`, `_implicit_labels_30d`, `_radar_zone_counts`, `_latest_weight_measurement`, `_latest_waist_measurement`, `_safe`.

### 3.4 Contrat route `/body/intelligence`

```python
GET /body/intelligence
→ 200 (template body_intelligence.html)
→ Authentification requise (CurrentUser)
→ Aucun query param
→ Aucun POST / DELETE / API JSON exposée
```

Pseudo-code :
```python
def body_intelligence_page(request, db, user) -> HTMLResponse:
    body_input = build_body_intelligence_input(db, user)
    snapshot = compute_body_intelligence(body_input)
    return templates.TemplateResponse("body_intelligence.html", {"snapshot": snapshot})
```

### 3.5 Structure template

```
<section.body-intelligence.body-intelligence--{status}>
  <header.body-intelligence__header>
    <h1.body-intelligence__headline>{snapshot.headline}</h1>
    <ul.body-intelligence__bullets>{snapshot.bullets}</ul>
  </header>
  <section.body-intelligence__priorities>           ← include partial priority
    {snapshot.priorities ≤ 3}
  </section>
  <section.body-intelligence__blocks>               ← include partial block
    {snapshot.blocks (7 toujours)}
  </section>
  <footer.body-intelligence__footer>
    Moteur Body Intelligence v{engine_version}
  </footer>
</section>
```

Chaque bloc partial expose :
- `data-block-key`, `data-block-classification`, `data-block-available`
- Badge classification : « Mesuré » / « Dérivé » / « Inféré » / « Hors de portée »
- Empty state explicite : « Données insuffisantes pour ce bloc. »
- Rendu spécialisé par `block.key` (training_consistency / body_metrics / muscle_zone_balance / push_pull_legs_balance / quality_and_confidence / implicit_signal_summary / unavailable_or_limits)

## 4. Statut des tests

| Fichier | Tests | Résultat |
|---|---|---|
| `tests/test_body_intelligence_inputs.py` | 11 | ✅ |
| `tests/test_body_intelligence_route.py` | 19 | ✅ |
| `tests/test_body_intelligence.py` (Sb_31.1) | 38 | ✅ non régressé |
| **Sous-suite Sb_31** | **68** | ✅ |
| Suite complète | ⏳ background run | (CI confirmera) |
| Ruff | ✅ 529 ≤ 548 |
| Spec protocol | ✅ |
| Alembic drift | ✅ no diff (aucune migration) |

### Garde-fous structurels

- `test_inputs_module_does_not_compute_overload_compliance` — aucun champ d'input ne contient "overload"
- `test_inputs_module_does_not_import_compute_body_intelligence` — séparation router-orchestrateur
- `test_build_does_not_mutate_db` — 3 appels successifs, comptage avant/après identique
- `test_template_has_no_business_loops_or_thresholds` — template ne référence aucune constante moteur (MIN_*, LOW_*, IMBALANCE_*, MAX_*, `compute_body_intelligence`)
- `test_router_does_not_recompute_business` — router n'importe aucun helper interne du composer
- `test_route_does_not_create_json_api` — `/body/intelligence.json` → 404/405
- `test_rendered_html_has_no_forbidden_wording` — scan régex du bloc rendu, 11 tokens interdits
- `test_no_new_js_file_introduced` — pas de nouveau .js
- `test_no_new_migration_introduced` — aucune migration ne mentionne `body_intelligence`

## 5. Limites produit (alignées spec §I/J)

- Le bloc « Hors de portée » est toujours rendu et liste explicitement : composition corporelle, esthétique, posture/symétrie réelles, cardio déclaratif, absence de signal médical.
- Aucun wording autoritaire ni esthétique n'apparaît dans le HTML rendu (scan testé).
- BMI affiché uniquement si height + weight présents, accompagné de son disclaimer et étiqueté comme « Dérivé » au lieu de « Mesuré ».
- Overload compliance affichée explicitement comme `not_available_v1` dans le bloc limits.

## 6. Coordination des routes /body — note importante

Au moment de l'audit pré-build, le merge concurrent **PR #15 « Manual Body Profile MVP under feature flag »** a introduit un router `app/routers/body.py` qui occupe déjà la route racine `/body` (avec `BodyGate = Depends(require_body_enabled)`). Pour éviter toute collision technique entre les deux tracks :

- Body Intelligence v2 utilise **`/body/intelligence`** comme route canonique.
- Le track parallèle Body Manual Profile garde `/body` et ses sous-routes (`/body/consent`, `/body/measurements`, `/body/export.json`, etc.).
- Les deux routers sont enregistrés indépendamment dans `app/main.py`. Aucune dépendance croisée.

Cette décision est documentée dans `app/routers/body_intelligence.py` (commentaire de module). Aucun lien `/profile` → `/body/intelligence` n'est ajouté V1 (OQ-G différé Sb_31.3 ou ultérieur).

## 7. Statut DoD locale

| Gate | Statut |
|---|---|
| `pytest tests/test_body_intelligence*.py -q` | ✅ 68 passed |
| `pytest --ignore=tests/test_v1_acceptance.py -q` | ⏳ background |
| `check_ruff_budget.py` | ✅ 529 ≤ 548 |
| `check_spec_protocol.py` | ✅ |
| `PYTHONPATH=. check_alembic_drift.py` | ✅ no diff |
| `check_schema_snapshot.py` | ✅ |
| `check_migration_patterns.py` | ✅ |
| `check_migration_roundtrip.py` | ✅ |

## 8. Contraintes respectées (verbatim user)

| Contrainte | OK |
|---|---|
| Couche I/O lecture seule | ✅ test `test_build_does_not_mutate_db` |
| Route `GET /body/intelligence` (collision `/body` → suffix) | ✅ |
| Template SSR mobile-first | ✅ + CSS extrait dédié |
| Status global + headline + bullets affichés | ✅ |
| 7 blocs affichés | ✅ test garde |
| Priorités max 3 | ✅ test cap |
| Classification visible (4 niveaux) | ✅ badges Mesuré/Dérivé/Inféré/Hors de portée |
| Limites explicites toujours visibles | ✅ bloc `unavailable_or_limits` always available |
| Wording autorisé / interdit | ✅ test scan rendu |
| Pas de modification `body_intelligence.py` | ✅ |
| Pas de migration | ✅ |
| Pas de modèle DB | ✅ |
| Pas de coach-report | ✅ |
| Pas de carte home | ✅ |
| Pas de HealthKit / API externe / LLM / photo / scan | ✅ |
| Pas d'overload compliance | ✅ marqueur `not_available_v1` exposé |
| Pas de modification Sx_30 overload / scoring / substitution | ✅ |
| Pas de JS ajouté | ✅ test `test_no_new_js_file_introduced` |
| Pas d'API JSON publique | ✅ test `test_route_does_not_create_json_api` |
| Pas de logique métier dans router | ✅ test garde |
| Pas de logique métier dans template | ✅ test garde |
| Pas de duplication seuils hors composeur | ✅ test garde |

## 9. CI réelle (post-push)

À renseigner après push.

- [ ] Job `pytest + QA scripts` — vert attendu
- [ ] Job `lint (ruff budget + bandit + actionlint + shellcheck)` — vert attendu
- [ ] Job `SonarCloud` — vert attendu

## 10. Métriques

| Item | Valeur |
|---|---|
| Lignes service I/O ajoutées | +240 |
| Lignes router ajoutées | +47 |
| Lignes template ajoutées | +209 (template + 2 partials) |
| Lignes CSS ajoutées | +230 (`body_intelligence.css`, fichier dédié) |
| Tests ajoutés | +30 (11 inputs + 19 route/template) |
| Migrations | 0 |
| Modèles SQLAlchemy | 0 |
| JS ajouté | 0 |
| Services métier core mutés | 0 |
| Ruff total | 529 ≤ 548 (inchangé vs Sb_31.1) |

## 11. Verdict

**✅ Sb_31.3 prêt.**

Prochaine étape : Sb_31.3 livrera un block « Snapshot body intelligence » dans `/coach-report` via une modification du **template seul** (`coach_report.html`), sans toucher au service `coach_report.py`. Le snapshot pourra réutiliser directement la pipeline `build_body_intelligence_input → compute_body_intelligence` exposée ici.

Aucun blocage anticipé. La route `/body/intelligence` est testée et validée en isolation. Le composer pur Sb_31.1 reste la seule source de vérité métier. Le router et le template restent des couches d'orchestration et de présentation strictement disciplinées.
