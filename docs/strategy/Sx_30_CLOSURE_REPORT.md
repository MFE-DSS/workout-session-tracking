# Sx_30 — Progressive Overload Engine — Closure Report

**Spec source :** `docs/strategy/Sx_30_PROGRESSIVE_OVERLOAD_ENGINE_SPEC.md`
**Date closure :** 2026-06-27
**Statut :** ✅ **TECHNICALLY CLOSED + DOGFOOD ✅ PASS 2026-07-01**.
**Verdict dogfood opérateur :** engine v1 fonctionnel et cohérent, aucun hint chiffré absurde, bug de contamination inter-template (corrigé par `10732e9`) non reproduit. Aucun bugfix supplémentaire requis. `Sb_30.next.substitution-history` reste différé. Cf. `docs/dogfood/DOGFOOD_Sx_30_OVERLOAD_ENGINE_REPORT.md`.
**Branche :** `claude/sprint-reporting-fitness-app-V7Qr6`

---

## 1. Résumé exécutif

Sx_30 a livré un moteur de surcharge progressive **déterministe, explainable, conservateur**, intégré bout-en-bout en 5 sprints (`Sb_30.0` → `Sb_30.5`). Aucun service métier core touché. Aucune dépendance JS externe. No-JS fallback intégral préservé. UI sobre, mobile-first, accessible (aria-labelledby + focus-visible + non-color cues WCAG 1.4.1).

## 2. Sprints livrés

| Sprint | Objet | CI run |
|---|---|---|
| Sb_30.0 | Spec review (SPEC ONLY) | [28238984400](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/28238984400) ✅ |
| Sb_30.1 | `overload_engine.py` v1 + 33 tests unitaires | [28241678098](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/28241678098) ✅ |
| Sb_30.2 | `overload_explainer.py` + `overload_inputs.py` + injection router (+42 tests) | [28245446788](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/28245446788) ✅ |
| Sb_30.3 | Migration `6h9e4c0d1f32` + `_partials/overload_hint.html` + CSS + wire (+19 tests) | [28247518562](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/28247518562) ✅ |
| Sb_30.4 | Suppression `progression_hint.py` legacy + 3 garde-fous | [28250584691](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/28250584691) ✅ |
| Sb_30.5 | A11y consolidation + dogfood template + closure | (Sb_30.5 CI run) |

## 3. Tests avant/après

| Étape | Tests verts |
|---|---|
| Avant Sx_30 (post Sx_29 closure) | 1178 |
| Après Sb_30.1 | 1206 (+28 net) |
| Après Sb_30.2 | 1248 (+42) |
| Après Sb_30.3 | 1265 (+17) |
| Après Sb_30.4 | 1259 (-6 net : -9 legacy + 3 garde-fous) |
| Après Sb_30.5 | **~1272** (+13 a11y tests) — confirmation CI |

## 4. Architecture résultante

| Module | Rôle | Pur ? |
|---|---|---|
| `app/services/overload_engine.py` (Sb_30.1) | Décision overload (5 états, cibles, reasons) | ✅ |
| `app/services/overload_inputs.py` (Sb_30.2) | Lecture DB + catégorisation → `OverloadInput` | ❌ (I/O isolé) |
| `app/services/overload_explainer.py` (Sb_30.2) | `OverloadHint` → payload UI | ✅ |
| `app/routers/sessions.py` | Compose les trois + injecte `overload_hints` dans le contexte | ❌ (router) |
| `app/templates/_partials/overload_hint.html` | Rendu SSR + a11y aria-labelledby + `<strong>` | — |
| `app/static/css/session_focus.css` | Styles + 5 états + non-color cues + focus-visible | — |

Aucune dépendance circulaire. Engine et explainer testables en isolation.

## 5. Fichiers créés / modifiés / supprimés

### Créés
- `app/services/overload_engine.py` (Sb_30.1, 260 lignes)
- `app/services/overload_inputs.py` (Sb_30.2, 175 lignes)
- `app/services/overload_explainer.py` (Sb_30.2, 84 lignes)
- `app/templates/_partials/overload_hint.html` (Sb_30.3, 41 → 56 lignes Sb_30.5)
- `migrations/versions/20260616_add_overload_engine_version.py` (Sb_30.3)
- `tests/test_overload_engine.py` (Sb_30.1)
- `tests/test_overload_explainer.py` (Sb_30.2)
- `tests/test_overload_router_injection.py` (Sb_30.2)
- `tests/test_overload_hint_render.py` (Sb_30.3 + Sb_30.4 garde-fous)
- `tests/test_overload_engine_version_migration.py` (Sb_30.3)
- `tests/test_overload_hint_a11y.py` (Sb_30.5)
- `docs/strategy/Sx_30_PROGRESSIVE_OVERLOAD_ENGINE_SPEC.md`
- `docs/dogfood/DOGFOOD_Sx_30_OVERLOAD_ENGINE_TEMPLATE.md` (Sb_30.5)
- `docs/SPRINT_Sb_30_0_REPORT.md` … `docs/SPRINT_Sb_30_5_a11y_and_closure_BUILD_REPORT.md`
- `docs/strategy/Sx_30_CLOSURE_REPORT.md` (ce document)

### Modifiés
- `app/models/session.py` (+5 lignes : `overload_engine_version`)
- `app/routers/sessions.py` (+14 puis -13 net = +1 net après Sb_30.4 ; injection inline)
- `app/templates/_partials/exercise_card.html` (+9 puis -4 net = +5 net après Sb_30.4 ; include conditionnel)
- `app/static/css/session_focus.css` (+132 puis +~10 a11y Sb_30.5)
- `data/schema_snapshot.sql` (régénéré Sb_30.3)
- `docs/strategy/SPEC_REGISTRY.md` + `ROADMAP_AND_NEXT_STEPS.md`

### Supprimés
- `app/services/progression_hint.py` (-50 lignes, Sb_30.4)
- `tests/test_progression_hint.py` (-134 lignes, Sb_30.4)

## 6. Contrats Sx_30 respectés

| Contrat | Statut |
|---|---|
| FastAPI SSR + Jinja2 conservé | ✅ |
| Pas de React / SPA / bundler / dep externe | ✅ |
| Pas de service métier core touché (scoring, reco, body, substitution, coach) | ✅ |
| Pas de modification `quality_score.py` / `implicit_signal.py` | ✅ (lecture seule uniquement) |
| No-JS fallback obligatoire | ✅ `<details>` natif + role="status" |
| Aucun JS introduit dans Sx_30 | ✅ pas de `.js` ajouté |
| Mobile 360×640 | ✅ media query `< 380px` |
| WCAG 2.5.5 (tap targets ≥ 44 sur primary) | ✅ primary CTA inchangée ; summary 24px ergonomique secondary |
| WCAG 1.4.1 (non-color cues) | ✅ 5 icônes unicode + border-left epaisse |
| WCAG 4.1.2 (programmatic name) | ✅ aria-labelledby + aria-label sur summary |
| Ruff budget ≤ 548 | ✅ 528 post Sb_30.4 |
| Migration additive uniquement | ✅ `6h9e4c0d1f32` |
| Versioning moteur per session (OQ-B) | ✅ colonne `overload_engine_version INT NOT NULL DEFAULT 1` |
| Options C/D/E restent bloquées | ✅ |
| Dogfood Sx_27 reste PENDING | ✅ indépendant |

## 7. OQ Sx_30 — état final

| OQ | Décision | Implémentation |
|---|---|---|
| OQ-A : granularité | Par exercice V1 | ✅ `overload_hints` indexé par `se.id` |
| OQ-B : versioning | Par session | ✅ migration + colonne + propagation DOM |
| OQ-C : bypass deload | Pas de bypass V1 | ✅ aucune UI override |
| OQ-D : historique | N=3 fixe | ✅ `HISTORY_N = 3` testé |
| OQ-E : placeholder inputs | Différé | ⏳ **Sb_30.next.placeholder** sous override séparé |

## 8. Dette restante

1. **Dogfood Sx_30 device réel** — PENDING. Cf. `docs/dogfood/DOGFOOD_Sx_30_OVERLOAD_ENGINE_TEMPLATE.md`.
2. **OQ-E placeholder cible dans les inputs poids/reps** — explicitement différé à `Sb_30.next.placeholder`. UX différente, risque utilisateur (écrasement valeur précédente) → traité dans un sprint dédié sous override séparé.
3. **Catégorisation V1 par mot-clé** dans `overload_inputs.py::categorize_exercise` — heuristique simple compound/isolation_free/isolation_machine. Cas limites possibles (ex. "Goblet squat" = compound mais détecté correctement ; "Push press" = compound OK ; mais certains exercices machine sans `machine_slug` peuvent être mal classés en `isolation_free`). À raffiner Sb_30.next.categorize si dogfood le révèle.
4. **Pas de Lighthouse CI** — aligné OQ-D Sx_29, audit a11y statique uniquement (lecture code + tests structurels).

## 9. Périmètres explicitement non touchés

- `app/services/scoring/` (aucune)
- `app/services/recommendation.py` + `reco/`
- `app/services/implicit_signal.py` (lecture seule uniquement)
- `app/services/quality_score.py` (lecture seule uniquement)
- `app/services/coach_report.py` / `coach_inference.py`
- `app/services/body_tracking.py`
- `app/services/substitution.py`

Vérifiable via `git log --oneline d2cc068..HEAD -- app/services/scoring/ app/services/recommendation.py app/services/reco/ app/services/coach_*.py app/services/body_tracking.py app/services/substitution.py`.

## 10. Non-goals (rappel et confirmation)

Sx_30 a EXPLICITEMENT exclu, et reste exclu :

- React production / SPA / bundler / dépendance JS externe
- Persistance des hints en base (recalcul à chaque GET — déterministe)
- Notification push / service worker / PWA
- Substitution modal / dialog inline
- Tracking analytique
- Modification du moteur de recommandation template-level
- Modification du scoring core
- Body tracking
- OQ-E placeholder cible dans les inputs (différé)
- Lighthouse CI (différé)
- Ouverture automatique de Sx_31 / Sx_32 / Sx_33+

## 11. Recommandation

**Sx_30 TECHNICALLY CLOSED + DOGFOOD PENDING.**

Conditions pour ouvrir le prochain Sx_ :
1. Dogfood Sx_30 device réel exécuté avec verdict ✅ ou ⚠️.
2. Frictions sévérité high traitées (`Sb_30.next.*` si nécessaire).
3. Override utilisateur explicite si Sx_31 / Sx_32 doit ouvrir avant dogfood Sx_30.

OQ-E (placeholder inputs) reste un candidat raisonnable pour un sprint dédié `Sb_30.next.placeholder` sous override séparé — recommandé avant ouverture d'un nouveau Sx_ pour clore définitivement le cycle UX overload.

Options Sx_31 / Sx_32 / Sx_33+ restent indépendamment bloquées par leurs propres conditions d'override.

## 12. Pointeurs

- Spec source : `docs/strategy/Sx_30_PROGRESSIVE_OVERLOAD_ENGINE_SPEC.md`
- Sprint reports : `docs/SPRINT_Sb_30_0_REPORT.md` … `SPRINT_Sb_30_5_a11y_and_closure_BUILD_REPORT.md`
- Dogfood template : `docs/dogfood/DOGFOOD_Sx_30_OVERLOAD_ENGINE_TEMPLATE.md`
- Spec registry : `docs/strategy/SPEC_REGISTRY.md`
- Roadmap : `docs/strategy/ROADMAP_AND_NEXT_STEPS.md`
- Closure Sx_29 (référence pattern) : `docs/strategy/Sx_29_CLOSURE_REPORT.md`
