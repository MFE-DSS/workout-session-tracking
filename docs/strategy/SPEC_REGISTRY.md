# SPIGNOS — Spec & Sprint Registry

**Source de vérité** des specs `Sx_NN` et des sprints `Sb_NN.k` du projet. Mise à jour à chaque ouverture/fermeture de sprint (cf. `docs/strategy/SPEC_DRIVEN_ENGINEERING_PROTOCOL_v1.md §13`).

**Légende statut :**
- ✅ livré (sprint clos, CI verte, dogfooded ou production-tested)
- 🟢 livré (sprint clos, CI verte, pas encore dogfooded)
- 🟡 en cours
- 🔵 spec validée, build à ouvrir
- ⚪ spec en draft
- ⏳ en attente d'OQ ou d'un sprint amont
- ❌ abandonné

> **Note V1 :** la table ci-dessous est constituée par parcours des fichiers `docs/SPRINT_Sb_*_REPORT.md` et `docs/strategy/*SPEC*.md` au 2026-06-14. Les associations spec ↔ sprint des cycles anciens (Sb_05 → Sb_20) sont reconstruites à partir des titres et peuvent être incomplètes. Cette V1 sert d'amorce, à compléter par l'opérateur à chaque sprint futur.

---

## 1. Cycle Sx_26 — Engineering Control Plane & Anti-Drift Hardening (actif)

**Spec :** `docs/strategy/Sx_26_ENGINEERING_CONTROL_PLANE_AND_ANTI_DRIFT_HARDENING_SPEC.md`
**Statut spec :** ✅ VALIDATED + amendement §19bis (OQ-1 ruff budget).
**Hard contracts :** SQLite, deploy manuel, snapshots historiques, ADD COLUMN ONLY, ruff budget locked.

| Sprint | Domaine | Statut | Spec ref | Rapport | CI run | Notes |
|---|---|---|---|---|---|---|
| Sb_26.1 | CI hardening (ruff budget, bandit, actionlint, shellcheck) | ✅ | Sx_26 §16 | `SPRINT_Sb_26_1_REPORT.md` | 27478562739 | Baseline ruff 548 |
| Sb_26.2 | Migration hardening (snapshot, linter, roundtrip) | ✅ | Sx_26 §16 | `SPRINT_Sb_26_2_REPORT.md` | 27479515017 | 17 migrations grandfathered |
| Sb_26.3 | Observability (deploy_state, healthz strict, Sentry/Discord opt-in) | ✅ | Sx_26 §16 | `SPRINT_Sb_26_3_REPORT.md` | 27480361229 | No app/services métier touché |
| Sb_26.4 | Security baseline (rate limit, pip-audit, gitleaks, Dependabot, lockfile) | ✅ | Sx_26 §16 | `SPRINT_Sb_26_4_REPORT.md` | 27499160260 | Gitleaks bloque DEPLOY_OVH.md placeholder (fix `fe9aede`) |
| Sb_26.5 | Spec/process discipline (templates + protocol + registry) | ✅ | Sx_26 §16 | `SPRINT_Sb_26_5_REPORT.md` | 27500839234 | Gate `check_spec_protocol` required |
| Sb_26.6 | Performance baseline (p95 endpoints, slow query log) | ✅ | Sx_26 §16 | `SPRINT_Sb_26_6_REPORT.md` | 27503005562 | Smoke 5 iter, budgets larges 30–250x |
| Sb_26.7 | Multi-tenant prep — scope auth audit + isolation tests | ✅ | Sx_26 §16 | `SPRINT_Sb_26_7_REPORT.md` | (ce sprint) | Aucun gap d'ownership détecté |

**Cycle Sx_26 clôturé le 2026-06-14.** Cf. `docs/strategy/Sx_26_CLOSURE_REPORT.md`.

## 1bis. Cycle Sx_27 — Coaching Loop & Product Activation (actif)

**Spec :** `docs/strategy/Sx_27_COACHING_LOOP_AND_PRODUCT_ACTIVATION_SPEC.md`
**Statut spec :** ✅ VALIDATED 2026-06-14 (OQ-5 tranchée à 360×640, autres OQ différées).
**Hard contracts :** hérités Sx_26 verbatim ; spécifique Sx_27 : la narrative ne ment jamais.

| Sprint | Domaine | Statut | Spec ref | Rapport | CI run | Notes |
|---|---|---|---|---|---|---|
| Sb_27.1 | Home dashboard activation (today/last/week) | ✅ | Sx_27 §14 | `SPRINT_Sb_27_1_REPORT.md` | 27506478583 | 0 modèle, 0 migration, 0 service core touché |
| Sb_27.2 | Session review V1 (`/sessions/{id}/done`) | ✅ | Sx_27 §14 | `SPRINT_Sb_27_2_REPORT.md` | 27509053460 | 5 sub-payloads + Triptyche Non déductible |
| Sb_27.3 | Weekly training loop (enrichit `/progress`) | ✅ | Sx_27 §14 | `SPRINT_Sb_27_3_REPORT.md` | 27511608805 | OQ-1 tranchée : enrichir /progress, pas de /weekly |
| Sb_27.4 | Recommendation explanation (wrapper externe) | ✅ | Sx_27 §14 | `SPRINT_Sb_27_4_REPORT.md` | 27531258753 | OQ-4 tranchée : wrapper externe, recommendation.py NON modifié |
| Sb_27.5 | Deterministic coach narrative (3 helpers purs) | ✅ | Sx_27 §14 | `SPRINT_Sb_27_5_REPORT.md` | 27535088857 | OQ-2 tranchée pas de LLM ; OQ-6 tranchée "tu" informel ; garde anti-"vous" |
| Sb_27.6 | UX simplification pass (dépréciation /dashboard, nav Synthèse → Progression) | ✅ | Sx_27 §14 | `SPRINT_Sb_27_6_REPORT.md` | 27537795326 | OQ-3 tranchée : /dashboard → 303 → /, pas de suppression brutale |
| Sb_27.7 | Product closure report + dogfood deferred | ✅ | Sx_27 §14 | `SPRINT_Sb_27_7_REPORT.md` | 27545919573 | Doc only ; closure report + dogfood deferred livrés |

**Cycle Sx_27 technically closed le 2026-06-15** (`docs/strategy/Sx_27_CLOSURE_REPORT.md`). **Product validation pending real dogfood** (`docs/dogfood/DOGFOOD_Sx_27_DEFERRED.md`).

> 📖 **Pour reprendre une session, lire d'abord [`docs/strategy/ROADMAP_AND_NEXT_STEPS.md`](ROADMAP_AND_NEXT_STEPS.md)** — document de référence vivant qui contient l'état actuel, la roadmap réconciliée (ancien S0→S10 vs cycles livrés) et les prompts verbatim à utiliser pour `Sb_27.dogfood-1`, `Sx_28`, `Sx_29`.

## 1ter. Cycle Sx_28 — Product Roadmap Reconciliation (BUILD AUTHORIZED FOR OPTION A UNDER OVERRIDE)

**Spec :** `docs/strategy/Sx_28_PRODUCT_ROADMAP_RECONCILIATION_SPEC.md`
**Statut spec :** ✅ AMENDED (2026-06-15 sprint `Sb_28.override-build-authorization`).
**Statut build :** ✅ **AUTHORIZED FOR OPTION A** (Sx_29 Mobile Session Focus Mode) sous override explicite. Options B/C/D/E **restent bloquées** (override séparé requis).
**Override :** humain, daté 2026-06-15, dogfood reste PENDING (non simulé). Voir spec §15.1bis + §16 + §20 et `SPRINT_Sb_28_OVERRIDE_BUILD_AUTHORIZATION_REPORT.md`.

| Sprint | Domaine | Statut | Spec ref | Rapport | CI run | Notes |
|---|---|---|---|---|---|---|
| Sx_28 (spec) | Reconciliation ancien S0→S10 ↔ repo réel + 5 options + matrice + décision Option A sous override | ✅ amendée | Sx_28 §1-20 | `SPRINT_Sx_28_SPEC_REPORT.md` + `SPRINT_Sb_28_OVERRIDE_BUILD_AUTHORIZATION_REPORT.md` | 27554090915 + (post-push) | DOGFOOD INPUT = PENDING ; build Option A autorisé sous override |
| Sb_28.override-build-authorization | Bascule verdict Sx_28 §15+§16+§20 vers BUILD AUTHORIZED FOR OPTION A | ✅ livré | Sx_28 §15.1bis | `SPRINT_Sb_28_OVERRIDE_BUILD_AUTHORIZATION_REPORT.md` | (post-push) | Doc only ; override borné à Option A |
| Sb_28.dogfood-integration | Mettre à jour Sx_28 §15+§20 si dogfood arrive a posteriori (peut reverser Option A) | 🔵 optionnel post-override | Sx_28 §17 | — | — | SPEC ONLY ; reste exécutable si dogfood livré plus tard |
| **Sx_29** Mobile Session Focus Mode | Spec + build en cours (Option A autorisée) | 🟡 en cours | Sx_29 §1-20 | `SPRINT_Sx_29_SPEC_REPORT.md` | 27559252205 | FastAPI SSR + Jinja2 ; React production INTERDIT ; build queue Sb_29.1-5 |
| Sb_29.1 | Visual skeleton (partials + CSS hooks + 21 tests) | ✅ | Sx_29 §17 | `SPRINT_Sb_29_1_REPORT.md` | 27562617417 | session_detail.html 551 → 161 lignes ; +124 lignes CSS ; 0 service métier touché |
| Sb_29.2 | Active exercise navigation (renforcement visuel + 19 tests) | ✅ | Sx_29 §17 | `SPRINT_Sb_29_2_REPORT.md` | 27571228735 | +131 lignes CSS (cumul Sx_29 = 255 lignes > seuil 200 — extraction Sb_29.5) ; 0 service métier touché, 0 JS, 0 template modifié |
| Sb_29.3 | Sticky CTA on active card (CSS-only, scoped, safe-area) | ✅ | Sx_29 §17 | `SPRINT_Sb_29_3_REPORT.md` | [27573217572](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/27573217572) ✅ 3/3 | +66 lignes CSS (cumul Sx_29 = 321) ; 16 tests ; 0 service métier, 0 JS, 0 changement structure |
| Sb_29.4 | Rest timer progressive enhancement (vanilla JS, no-JS fallback) | ✅ | Sx_29 §17 | `SPRINT_Sb_29_4_REPORT.md` | [27577849433](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/27577849433) ✅ 3/3 | `session_focus.js` 95 lignes ; +64 lignes CSS (cumul Sx_29 = 385) ; 20 tests dédiés ; 0 service métier, 0 route, 0 migration, 0 dep externe |
| Sb_29.5 | Template tests + mobile smoke + a11y + extraction `session_focus.css` + closure | ✅ | Sx_29 §17 | `SPRINT_Sb_29_5_REPORT.md` | [27604565634](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/27604565634) ✅ 3/3 | Extraction 384 lignes CSS → `session_focus.css` (app.css revient pré-Sx_29) ; 17 tests ajoutés (9 smoke + 8 a11y) ; 0 service métier, 0 route, 0 migration, 0 dep externe |
| **Sx_29 CLOSURE** | Technically closed + Dogfood ✅ PASS 2026-06-16 | ✅ TECH CLOSED + DOGFOOD PASS | `Sx_29_CLOSURE_REPORT.md` + `SESSION_FOCUS_MOBILE_AUDIT_2026-06-16.md` + `dogfood/DOGFOOD_Sx_29_FOCUS_MODE_TEMPLATE.md` | — | [27604565634](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/27604565634) ✅ | Verdict opérateur satisfaisant. Sx_30 autorisé en SPEC ONLY ; build Sx_30 subordonné à Sb_30.0 review. Sx_31/32/33+ restent bloqués (override séparé). |
| **Sx_30** Progressive Overload Engine | SPEC ONLY ouvert sous override #3 (post-dogfood Sx_29) | 🟡 SPEC ONLY | Sx_30 §1-20 | `Sx_30_PROGRESSIVE_OVERLOAD_ENGINE_SPEC.md` | (Sb_30.0 CI) | FastAPI SSR + Jinja2 ; pas de React ; build queue Sb_30.1-5 à valider ; OQ-A→OQ-E à trancher |
| Sb_30.0 | Spec review + sprint report spec (SPEC ONLY) | ✅ | Sx_30 §17 | `SPRINT_Sb_30_0_REPORT.md` | (post-push) | Aucun code touché en app/ ; 0 service, 0 migration, 0 template, 0 test |
| Sb_30.1 | overload_engine.py v1 + tests unitaires | 🔵 spec-pending | Sx_30 §14 | — | — | Pré-requis : Sb_30.0 accepté + override #3 BUILD AUTHORIZED |
| Sb_30.2 | overload_explainer.py + injection router | 🔵 spec-pending | Sx_30 §14 | — | — | Pré-requis : Sb_30.1 |
| Sb_30.3 | Migration + template overload_hint.html + CSS | 🔵 spec-pending | Sx_30 §14 | — | — | Pré-requis : Sb_30.2 |
| Sb_30.4 | Remplacement legacy progression_hint.py | 🔵 spec-pending | Sx_30 §14 | — | — | Pré-requis : Sb_30.3 |
| Sb_30.5 | A11y + tests + closure Sx_30 | 🔵 spec-pending | Sx_30 §14 | — | — | Pré-requis : Sb_30.4 |
| Sx_29+ alternatives | Sx_30 (Overload) / Sx_31 (Body v2) / Sx_32 (PWA) / Sx_33+ (Health/API) | ❌ BLOQUÉS | — | — | — | Override séparé requis pour chaque |

## 2. Cycle Sx_24 — Implicit Signal Scoring v2

**Spec :** `docs/strategy/SPIGNOS_IMPLICIT_SIGNAL_SCORING_SPEC_v1.md`
**Statut :** ✅ Livré + dogfood Sb_24.next.reco

| Sprint | Domaine | Statut | Rapport |
|---|---|---|---|
| Sb_24.1+2 | Foundations (modèle implicit_label + scoring_version) | ✅ | `SPRINT_Sb_24_1_and_2_foundations_BUILD_REPORT.md` |
| Sb_24.3 | Completion hook (persist_implicit_labels) | ✅ | `SPRINT_Sb_24_3_completion_hook_BUILD_REPORT.md` |
| Sb_24.4 | Checkbox "fait" déprécié | ✅ | `SPRINT_Sb_24_4_checkbox_deprecation_BUILD_REPORT.md` |
| Sb_24.5 | quality_score V2 + cleanup | ✅ | `SPRINT_Sb_24_5_cleanup_and_24_6_BUILD_REPORT.md` + `SPRINT_Sb_24_5_quality_score_v2_BUILD_REPORT.md` |
| Sb_24.7+8 | Coach Report bloc Implicite agrégé + clôture cycle | ✅ | `SPRINT_Sb_24_7_and_8_implicit_aggregate_BUILD_REPORT.md` |
| Sb_24.next.reco | Zone-freshness fix gradient 3 sessions | ✅ | `SPRINT_Sb_24_next_reco_zone_freshness_BUILD_REPORT.md` |

## 3. Cycle Sx_23 — Coach Report

**Spec :** `docs/strategy/SPIGNOS_COACH_REPORT_SPEC_v1.md` + `..._v2.md` (LLM Narrative)
**Statut :** ✅ Livré + étendu en Sb_24.7

| Sprint | Domaine | Statut | Rapport |
|---|---|---|---|
| Sb_23 | Coach Report v1 (Mesuré/Inféré/Non déductible triptyche) | ✅ | `SPRINT_Sb_23_coach_report_BUILD_REPORT.md` |

## 4. Cycle Sx_22 — Substitution & Profile Synthesis

**Specs :** `SPIGNOS_EXERCISE_SUBSTITUTION_GRAPH_SPEC.md`, `..._REFINEMENTS.md`, `_FINAL.md`, `SPIGNOS_PROFILE_SYNTHESIS_SPEC_v2.md`

| Sprint | Domaine | Statut | Rapport |
|---|---|---|---|
| Sb_22a substitution-gap-pack | Substitution graph V1 | ✅ | `SPRINT_Sb_22a_substitution_gap_pack_BUILD_REPORT.md` |
| Sb_22a next-lower-subzone-fix | Subzone fix | ✅ | `SPRINT_Sb_22a_next_lower_subzone_fix_BUILD_REPORT.md` |
| Sb_22a next2 atlas-follows-substitute | Atlas link follow | ✅ | `SPRINT_Sb_22a_next2_atlas_follows_substitute_BUILD_REPORT.md` |
| Sb_22b profile-synthesis-v2 | Profile synthesis V2 | ✅ | `SPRINT_Sb_22b_profile_synthesis_v2_BUILD_REPORT.md` |

## 5. Cycle Sx_20 — Prod CICD Pipeline

**Spec :** `docs/strategy/SPIGNOS_PROD_CICD_PIPELINE_SPEC_v1.md`

| Sprint | Domaine | Statut | Rapport |
|---|---|---|---|
| Sb_20.1 | Coverage XML + SonarCloud config | ✅ | `SPRINT_Sb_20_1_REPORT.md` |
| Sb_20.2 | Linters advisory (ruff + bandit) | ✅ | `SPRINT_Sb_20_2_REPORT.md` |
| Sb_20.3 | Coverage path fix | ✅ | `SPRINT_Sb_20_3_REPORT.md` |
| Sb_20.4 | SonarCloud advisory | ✅ | `SPRINT_Sb_20_4_REPORT.md` |
| Sb_20.5 | SonarCloud required | ✅ | `SPRINT_Sb_20_5_REPORT.md` |

## 6. Cycles antérieurs (Sb_02 → Sb_16) — historique pré-discipline

Ces sprints précèdent la formalisation Sb_26.5 du protocole. Reconstitution chronologique :

| Sprint | Domaine | Rapport |
|---|---|---|
| Sb_02.1 | Bootstrap V1 | `SPRINT_Sb_02_1_REPORT.md` |
| Sb_05 → Sb_10 | Itérations produit V1 polish | `SPRINT_Sb_0[5-9]_REPORT.md`, `SPRINT_Sb_10_session_v1_polish_REPORT.md` |
| Sb_11a | Pre-session briefing | `SPRINT_Sb_11a_pre_session_briefing_BUILD_REPORT.md` |
| Sb_12 | Next-session recommendation | `SPRINT_Sb_12_next_session_recommendation_BUILD_REPORT.md` |
| Sb_13 | Recommendation telemetry & tuning | `SPRINT_Sb_13_recommendation_telemetry_and_tuning_BUILD_REPORT.md` |
| Sb_16 | Prod CICD pipeline (avant Sx_20) | `SPRINT_Sb_16_prod_cicd_pipeline_BUILD_REPORT.md` |
| Sb_R3 | Refactor 3 (non-rattaché) | `SPRINT_Sb_R3_REPORT.md` |
| Sb_cardio_capture | Cardio capture | `SPRINT_Sb_cardio_capture_REPORT.md` |
| Sb_catalog_balance_v1 | Catalog balance | `SPRINT_Sb_catalog_balance_v1_REPORT.md` |
| Sb_catalog_substitution_v1 | Catalog substitution | `SPRINT_Sb_catalog_substitution_v1_REPORT.md` |
| Sb_catalog_v13 | Catalog v13 | `SPRINT_Sb_catalog_v13_REPORT.md` |
| Sb_launcher_v1 | Intelligent session launcher | `SPRINT_Sb_launcher_v1_REPORT.md` |
| Sb_science_page | Science page | `SPRINT_Sb_science_page_REPORT.md` |

## 7. Specs sans sprint dédié recensé (artefacts de pensée)

Documents de stratégie/spec qui n'ont pas (ou pas encore) déclenché un cycle Sx_NN/Sb_NN.k formel :

- `SPIGNOS_ARCHITECTURE_AND_ROBUSTNESS_SYNTHESIS_v1.md` — synthèse architecte, pas un sprint
- `SPIGNOS_BODY_ENGINEERING_DASHBOARD_V1.md`
- `SPIGNOS_BODY_METRICS_READINESS_SPEC.md`
- `SPIGNOS_CATALOG_BENCHMARK_REVIEW_v1.md`
- `SPIGNOS_CATALOG_GOVERNANCE.md`
- `SPIGNOS_CATALOG_QA_REPORT.md` — rapport auto-généré
- `SPIGNOS_CATALOG_SUBSTITUTION_MATRIX_v1.md`
- `SPIGNOS_COACH_REPORT_LLM_NARRATIVE_SPEC_v2.md`
- `SPIGNOS_DOGFOODING_GENERALIZATION_SPEC_v1.md`
- `SPIGNOS_EXERCISE_FEEDBACK_RATIONALIZATION*.md`
- `SPIGNOS_EXERCISE_SYSTEM_CONSOLIDATION_SPEC*.md` / `_ROADMAP.md`
- `SPIGNOS_INTELLIGENT_SESSION_LAUNCHER_SPEC.md` → Sb_launcher_v1
- `SPIGNOS_LEADERBOARD_DRILLDOWN_SPEC_v1.md`
- `SPIGNOS_MACHINE_KNOWLEDGE_AND_SUBSTITUTION_SURFACE_SPEC_v1.md`
- `SPIGNOS_MOBILE_EXERCISE_ENTRY_UX*.md`
- `SPIGNOS_NEXT_SESSION_RECOMMENDATION_SPEC_v1.md` → Sb_12 + Sb_13 + Sb_24.next.reco
- `SPIGNOS_PRE_SESSION_BRIEFING_SPEC_v1.md` → Sb_11a
- `SPIGNOS_RECOMMENDATION_CALIBRATION_SPEC_v1.md`

## 8. Mainteneurs

Ce registry doit être mis à jour :

- **À l'ouverture** d'un `Sx_NN` (ligne dans §X dédiée à la spec)
- **À l'ouverture** d'un `Sb_NN.k` (ligne dans la table du cycle)
- **À la fermeture** d'un sprint (statut + lien rapport + run CI)
- **À tout amendement** (`§Nbis`) d'une spec

La mise à jour est faite par l'agent **dans le même commit** que le sprint report. Pas de PR séparée pour le registry.

## 9. Limites V1

- Reconstitution historique partielle pour Sb_02 → Sb_19 (pas tous les sprints associés à une spec formelle)
- Pas de lien direct commit ↔ ligne du registry (Sb_26.next.spec-traceability-1 candidat)
- Pas de validation automatique que tout sprint mergé est dans le registry (vérifié humainement à la GO/NO-GO review)
