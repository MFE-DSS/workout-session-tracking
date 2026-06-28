# Sb_31.4 — Body Intelligence v2 : a11y + perf + responsive (Build Report)

**Branche :** `claude/sprint-reporting-fitness-app-V7Qr6`
**Date :** 2026-06-28
**Spec parent :** `docs/strategy/SPIGNOS_BODY_INTELLIGENCE_V2_SPEC.md`
**Lot Sx_31 :** §N.2 — Sb_31.4 (a11y + perf + responsive, 4/5 du cycle)
**Build authorization :** ✅ `BUILD AUTHORIZED FOR Sx_31` (override #4)
**Pré-requis :** Sb_31.1 ✅ + Sb_31.2 ✅ + Sb_31.3 ✅ (CI 28319392397)

---

## 1. Résumé exécutif

Sprint de consolidation. **Aucune nouvelle fonctionnalité produit.** Renforcement ciblé sur les 6 surfaces Body Intelligence v2 livrées par Sb_31.2/3, sur 3 axes :

1. **A11y** : CTA explicite + flèche décorative `aria-hidden` dans le snapshot coach-report ; vérification structurelle h1/h2, badges classification, status, focus-visible — déjà solides depuis Sb_31.2/5, garde-fous testés.
2. **Responsive** : règle stricte `≤ 360px` ajoutée + safety `width: 100% / box-sizing: border-box / overflow-x: hidden` sur le wrapper principal + collapse de la grille `kv` en single-column sur petit écran (anti-débordement valeurs longues).
3. **Perf** : tests p95 SSR avec budgets très généreux (catch egregious slowness, pas microbenchmark fragile) + smoke 20 itérations.

**0 modification** du composer, des inputs, du service coach_report, ou de la pipeline. **0 nouvelle fonctionnalité, 0 nouveau JS, 0 migration, 0 API JSON.**

## 2. Fichiers modifiés / créés

| Fichier | Type | Description |
|---|---|---|
| `app/templates/_partials/coach_body_snapshot.html` | MODIFIED | +5 l : `aria-label` explicite sur le CTA + flèche `→` enveloppée dans `<span aria-hidden="true">`. |
| `app/static/css/body_intelligence.css` | MODIFIED | +4 l sur `.body-intelligence` (safety `width:100%`/`box-sizing`/`overflow-x:hidden`) + +9 l dans la media query `< 380px` (grille `kv` → 1 colonne) + nouvelle media query `≤ 360px` (~10 l : bullets/list padding réduit, bi-block padding compact, head gap réduit). |
| `tests/test_body_intelligence_a11y_perf.py` | **NEW** | 17 tests : structure HTML rendu (8) + wording (1) + perf p95 (3) + garde-fous non-régression (5). |
| `tests/test_body_intelligence_responsive.py` | **NEW** | 11 tests : mobile-first + max-width safety + media queries 380/360 + collapse kv + non-color cues préservés + focus-visible + responsive coach snapshot. |
| `docs/SPRINT_Sb_31_4_body_intelligence_a11y_perf_responsive_BUILD_REPORT.md` | **NEW** | Ce rapport. |
| `docs/strategy/SPEC_REGISTRY.md` | MODIFIED | Sb_31.4 livré ✅. |

### Non touché (vérification explicite par tests garde)
- `app/services/body_intelligence.py` (composer pur)
- `app/services/body_intelligence_inputs.py` (couche I/O)
- `app/services/coach_report.py` (service intact depuis Sb_31.3)
- `app/services/coach_inference.py` / `profile_metrics.py` / `muscle_scoring.py` / `quality_score.py` / `implicit_signal.py` / `confidence.py` / `radar.py` / `overload_*` / `substitution.py` / `recommendation.py`
- `app/models/*` / `migrations/*`
- `app/routers/body.py` (track parallèle PR #15) / `app/routers/body_intelligence.py` / `app/routers/coach_report.py`
- `app/templates/body_intelligence.html` (h1, regions déjà correctes Sb_31.2)
- `app/templates/_partials/body_intelligence_block.html` (h2, badges, aria-label déjà Sb_31.2)
- `app/templates/_partials/body_intelligence_priority.html` (role="status", details, aria-label déjà Sb_31.2)
- `app/static/js/*` — aucun JS ajouté ni modifié.

## 3. Surfaces auditées

### `/body/intelligence` (page complète)
| Critère | État au sortir de Sb_31.4 | Origine |
|---|---|---|
| h1 unique | ✅ test `test_body_intel_has_exactly_one_h1` | Sb_31.2 |
| aria-labelledby pointe vers le h1 | ✅ test `test_body_intel_h1_id_matches_aria_labelledby` | Sb_31.2 |
| h2 sur les 7 blocs | ✅ test `test_body_intel_blocks_use_h2` | Sb_31.2 |
| Badge classification textuel (Mesuré/Dérivé/Inféré/Hors de portée) | ✅ test garde | Sb_31.2 |
| Status global non-color (?, ~, •) + texte | ✅ test garde | Sb_31.2 |
| Priorités en `<details>` natifs | ✅ test garde | Sb_31.2 |
| Liens explicites (texte ou aria-label) | ✅ test garde | Sb_31.2 |
| focus-visible | ✅ Sb_31.2 préservé | Sb_31.2 |
| Aucun wording médical / esthétique | ✅ test garde | Sb_31.2 |
| `<section>` avec aria-labelledby = landmark implicite | ✅ IDE check Web:S6822 (role="region" redondant retiré) | Sb_31.4 |

### `/coach-report` (snapshot block)
| Critère | État | Origine |
|---|---|---|
| `<h2>` du snapshot ne casse pas la hiérarchie du report (h1 = "Coach Report — @user" toujours unique) | ✅ Sb_31.3 préservé | Sb_31.3 |
| Badge status textuel ("Sur les séances loggées" / "Partiel" / "Données partielles") | ✅ | Sb_31.3 |
| CTA "Voir le détail" avec **aria-label explicite** | ✅ **ajouté Sb_31.4** | Sb_31.4 |
| Flèche `→` décorative marquée `aria-hidden="true"` | ✅ **ajouté Sb_31.4** | Sb_31.4 |
| Pas de duplication des 7 blocs (synthèse uniquement) | ✅ | Sb_31.3 |
| Format print A4 préservé (mêmes classes `coach-block`) | ✅ | Sb_31.3 |

## 4. Améliorations a11y appliquées (verbatim diff)

### `coach_body_snapshot.html` — CTA explicite

**Avant Sb_31.4** :
```html
<a class="link" href="{{ url_for('body_intelligence') }}">
  Voir le détail →
</a>
```

**Après Sb_31.4** :
```html
<a
  class="link"
  href="{{ url_for('body_intelligence') }}"
  aria-label="Voir le détail de la lecture corporelle Body Intelligence"
>
  Voir le détail <span aria-hidden="true">→</span>
</a>
```

Bénéfice : lecteur d'écran annonce *"Voir le détail de la lecture corporelle Body Intelligence, lien"* au lieu de *"Voir le détail flèche droite, lien"*. La flèche reste visible visuellement mais n'est plus lue comme du texte.

### `body_intelligence.html` — role redondant retiré

L'IDE a remonté `Web:S6822` : `<section aria-labelledby="...">` est déjà une landmark `region` implicite. L'attribut `role="region"` ajouté brièvement a été retiré. Aucun impact a11y (la landmark reste).

## 5. Améliorations responsive appliquées

### `body_intelligence.css` — wrapper safety

```css
.body-intelligence {
  /* ... */
  /* Sb_31.4 — safety mobile : pas de scroll horizontal sur 360px. */
  width: 100%;
  box-sizing: border-box;
  overflow-x: hidden;
}
```

### `body_intelligence.css` — collapse grille kv (< 380px)

```css
@media (max-width: 380px) {
  /* ... règles existantes Sb_31.2 ... */
  /* Sb_31.4 — empêche les valeurs longues (dates, mesures) de pousser
     la 2e colonne hors du viewport sur 360px. */
  .bi-block__kv {
    grid-template-columns: 1fr;
    gap: 2px 0;
  }
  .bi-block__kv dd {
    text-align: left;
    margin-bottom: 4px;
  }
}
```

### `body_intelligence.css` — nouvelle media query ≤ 360px

```css
/* ───── Mobile minimal (≤ 360px) — cible spec mobile Sx_29 ───── */
@media (max-width: 360px) {
  .body-intelligence__bullets,
  .bi-block__list {
    padding-left: 16px;
  }
  .bi-block {
    padding: 10px;
  }
  .bi-block__head {
    gap: 4px 8px;
  }
}
```

Justification : la cible mobile Sx_29 verbatim est 360×640. La règle `≤ 360px` traite explicitement ce point limite, indépendamment du seuil 380px.

## 6. Stratégie perf / p95

**Pattern** : mesure intra-test avec `time.perf_counter`, N=10 itérations, p95 via `statistics.quantiles(durations, n=20)[18]`. Budget très généreux pour absorber la variance CI.

```python
P95_BUDGET_MS_BODY_INTEL = 2500
P95_BUDGET_MS_COACH_REPORT = 3000
N_ITERATIONS = 10
```

**Pourquoi des budgets aussi larges ?**
- L'objectif est d'**attraper les régressions catastrophiques** (régression d'un ordre de grandeur), pas de microbenchmark précis.
- La variance entre laptop local et CI shared runner peut dépasser 500ms sur des routes SSR avec compose de services.
- Pattern aligné Sb_26.6 (budgets larges 30-250×).

**Mesure locale (laptop)** : p95 `/body/intelligence` ≈ ~120ms, p95 `/coach-report` ≈ ~280ms. CI peut multiplier par 5-10 sans toucher le budget.

**Smoke 20 itérations** : test additionnel qui appelle alternativement les 2 routes 20 fois sans assertion temporelle, juste pour vérifier que 200 reste stable sous charge répétée (catch leaks de session, états mutables).

Pas de mesure plus fine — éviter benchmarks fragiles en CI. Si une régression sérieuse apparaît, on creusera avec `scripts/perf_smoke.py` existant (Sb_26.6).

## 7. Tests ajoutés

### `tests/test_body_intelligence_a11y_perf.py` (17 tests)

**Structure HTML rendu (8)** :
- `test_body_intel_has_exactly_one_h1`
- `test_body_intel_h1_id_matches_aria_labelledby`
- `test_body_intel_blocks_use_h2` (≥ 5 h2 attendus)
- `test_body_intel_blocks_carry_classification_label` (4 labels)
- `test_body_intel_status_visible_hors_couleur`
- `test_body_intel_priorities_use_native_details`
- `test_body_intel_links_have_explicit_text`
- `test_coach_snapshot_cta_has_aria_label_or_explicit_text`
- `test_coach_snapshot_decorative_arrow_is_hidden` (flèche `aria-hidden`)

**Wording (1)** :
- `test_no_forbidden_wording_on_body_intel`

**Perf (3)** :
- `test_perf_body_intelligence_route_p95` (p95 < 2500ms)
- `test_perf_coach_report_route_p95` (p95 < 3000ms)
- `test_perf_routes_stay_200_under_repeated_load` (20 iter alternées)

**Garde-fous non-régression (5)** :
- `test_composer_signature_unchanged_by_sb_31_4`
- `test_inputs_layer_signature_unchanged_by_sb_31_4`
- `test_coach_report_service_still_unchanged_by_sb_31_4`
- `test_no_new_js_file_by_sb_31_4`
- `test_no_new_migration_mentions_a11y_perf`
- `test_no_json_api_introduced_sb_31_4` (parametrize 2)

### `tests/test_body_intelligence_responsive.py` (11 tests)

**Mobile-first (2)** :
- `test_css_has_baseline_mobile_first_rules` (pas de min-width > 400 dans non-media)
- `test_css_has_max_width_safety_on_wrapper` (max-width + width + box-sizing + overflow-x)

**Media queries (3)** :
- `test_css_has_380px_media_query`
- `test_css_has_360px_media_query` (Sb_31.4 nouveau)
- `test_kv_grid_collapses_to_single_column_on_narrow`

**Non-color cues préservés (3)** :
- `test_status_global_non_color_cues_preserved`
- `test_classification_non_color_cues_preserved`
- `test_priority_non_color_cues_preserved`

**Anti-overflow + focus + coach snapshot (3)** :
- `test_no_dangerous_overflow_visible_on_wrappers`
- `test_focus_visible_rule_preserved`
- `test_coach_snapshot_reuses_coach_block_classes`

## 8. Statut tests

| Suite | Résultat |
|---|---|
| `test_body_intelligence_a11y_perf.py` (Sb_31.4) | ✅ 17 (incluant 3 perf p95) |
| `test_body_intelligence_responsive.py` (Sb_31.4) | ✅ 11 |
| `test_body_intelligence.py` (Sb_31.1) | ✅ 38 non régressé |
| `test_body_intelligence_inputs.py` (Sb_31.2) | ✅ 11 non régressé |
| `test_body_intelligence_route.py` (Sb_31.2) | ✅ 19 non régressé |
| `test_coach_report_body_snapshot.py` (Sb_31.3) | ✅ 23 non régressé |
| **Sous-suite Sx_31** | ✅ **119** (+28 vs Sb_31.3) |
| Suite complète | ⏳ background run |
| Ruff | ✅ 529 ≤ 548 |
| Spec protocol | ✅ |
| Alembic drift | ✅ no diff |

## 9. Statut DoD locale

| Gate | Statut |
|---|---|
| `pytest tests/test_body_intelligence*.py tests/test_coach_report_body_snapshot.py -q` | ✅ 119 passed |
| `pytest --ignore=tests/test_v1_acceptance.py -q` | ⏳ background |
| `check_ruff_budget.py` | ✅ 529 ≤ 548 |
| `check_spec_protocol.py` | ✅ |
| `PYTHONPATH=. check_alembic_drift.py` | ✅ no diff |

## 10. Contraintes respectées (verbatim user)

| Contrainte | OK |
|---|---|
| Aucune nouvelle fonctionnalité produit | ✅ |
| Améliorer HTML sémantique / aria / focus / non-color / responsive | ✅ scope respecté |
| 0 modification `body_intelligence.py` | ✅ test garde |
| 0 modification `body_intelligence_inputs.py` | ✅ test garde |
| 0 modification `app/services/coach_report.py` | ✅ test garde |
| 0 migration / modèle DB | ✅ test garde |
| 0 JS / API JSON / LLM | ✅ test garde |
| 0 HealthKit / photo / scan | ✅ |
| 0 carte home, 0 lien /profile→/body | ✅ |
| 0 recalcul métier dans router/template | ✅ Sb_31.3 garde toujours valide |
| 0 changement seuils composer | ✅ |
| 0 changement wording métier (sauf a11y mineur : CTA aria-label) | ✅ |

## 11. CI réelle (post-push)

**Run GitHub Actions : [28321554285](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/28321554285) — ✅ success (3/3 jobs verts)**

- [x] Job `pytest + QA scripts` — ✅ success
- [x] Job `lint (ruff budget + bandit + actionlint + shellcheck)` — ✅ success
- [x] Job `SonarCloud` — ✅ success

## 12. Métriques

| Item | Valeur |
|---|---|
| Lignes template modifiées | +5 (coach snapshot CTA) |
| Lignes CSS modifiées | +4 (wrapper safety) + +9 (media 380 kv collapse) + +10 (media 360 nouvelle) = +23 |
| Tests ajoutés | +28 (17 a11y/perf + 11 responsive) |
| Services métier core mutés | 0 |
| Migrations | 0 |
| Modèles SQLAlchemy | 0 |
| JS ajouté | 0 |
| API JSON | 0 |
| Ruff total | 529 ≤ 548 (inchangé) |

## 11. Verdict

**✅ Sb_31.5 (closure) prêt.**

Les 3 axes consolidés (a11y, responsive, perf) sont couverts. La pipeline Sx_31 (`/body/intelligence` page complète + `/coach-report` snapshot) reste disciplinée : composer pur intouché, couche I/O intouchée, service coach_report intouché, aucune dette ajoutée. Aucun blocage anticipé pour la closure.

Prochaine étape : Sb_31.5 livrera le dogfood template + closure report Sx_31 + extraction CSS conditionnelle si volume `body_intelligence.css` justifie (V1 : ~280 lignes, sous le seuil 200 pré-extraction défini par Sx_29 OQ-B mais l'extraction est déjà faite — closure du cycle).
