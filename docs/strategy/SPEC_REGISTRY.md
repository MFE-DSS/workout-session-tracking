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
| Sb_27.6 | UX simplification pass | 🔵 | Sx_27 §14 | — | — | OQ-3 à trancher avant |
| Sb_27.7 | Product closure report + dogfood | 🔵 | Sx_27 §14 | — | — | Tous les lots précédents requis |

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
