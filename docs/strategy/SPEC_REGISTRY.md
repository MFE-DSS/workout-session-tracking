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
| Sb_30.0 | Spec review + sprint report spec (SPEC ONLY) | ✅ | Sx_30 §17 | `SPRINT_Sb_30_0_REPORT.md` | [28238984400](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/28238984400) ✅ 3/3 | Aucun code touché en app/ ; 0 service, 0 migration, 0 template, 0 test |
| Sb_30.1 | overload_engine.py v1 + tests unitaires (33 cas) | ✅ | Sx_30 §14 | `SPRINT_Sb_30_1_REPORT.md` | [28241678098](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/28241678098) ✅ 3/3 | Moteur pur 260 lignes ; 0 router/template/migration/modèle ; 0 service métier core touché ; OQ A/B/C/D implémentées |
| Sb_30.2 | overload_explainer.py + overload_inputs.py + injection router (42 tests) | ✅ | Sx_30 §14 | `SPRINT_Sb_30_2_REPORT.md` | [28245446788](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/28245446788) ✅ 3/3 | +259 lignes services (84 explainer + 175 inputs) ; +14 lignes router ; 0 template / 0 migration / 0 modèle / 0 CSS / 0 JS ; 0 service métier core mutually modifié |
| Sb_30.3 | Migration overload_engine_version + overload_hint.html + CSS + wire (19 tests) | ✅ | Sx_30 §14 | `SPRINT_Sb_30_3_overload_hint_ui_first_render_BUILD_REPORT.md` | [28247518562](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/28247518562) ✅ 3/3 | Migration `6h9e4c0d1f32` ; partial 41 l + CSS +132 l ; exercise_card.html +9 l (active card only) ; 0 changement engine/inputs/explainer/scoring/legacy |
| Sb_30.4 | Suppression `progression_hint.py` legacy + 3 garde-fous | ✅ | Sx_30 §14 | `SPRINT_Sb_30_4_remove_progression_hint_legacy_BUILD_REPORT.md` | [28250584691](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/28250584691) ✅ 3/3 | -184 lignes legacy (50 service + 134 tests) ; -13 router net ; -4 template net ; Ruff 535 → 528 ; 0 service core touché ; 0 migration ; cherry-pick propre sans parasites |
| Sb_30.5 | A11y consolidation + closure Sx_30 + dogfood template (13 tests) | ✅ | Sx_30 §14 | `SPRINT_Sb_30_5_a11y_and_closure_BUILD_REPORT.md` | [28288760013](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/28288760013) ✅ 3/3 | Partial overload_hint.html : +aria-labelledby + id per-se + `<strong>` + aria-label summary ; CSS focus-visible + padding ergonomique ; 0 changement engine/inputs/explainer/scoring/substitution/coach ; 0 migration ; 0 JS |
| **Sx_30 CLOSURE** | Technically closed + Dogfood ✅ PASS 2026-07-01 | ✅ TECH CLOSED + DOGFOOD PASS | `Sx_30_CLOSURE_REPORT.md` + `dogfood/DOGFOOD_Sx_30_OVERLOAD_ENGINE_REPORT.md` (verdict) + `dogfood/DOGFOOD_Sx_30_OVERLOAD_ENGINE_TEMPLATE.md` (template) | — | [28288760013](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/28288760013) ✅ | Engine v1 validé en usage réel. Aucun bugfix supplémentaire. `Sb_30.next.substitution-history` reste différé. OQ-E livrée via `Sb_30.next.placeholder` 2026-06-27. |
| Sb_30.next.placeholder | Light placeholders sur 1er work set actif (OQ-E) — 13 tests | ✅ | Sx_30 §18 OQ-E | `SPRINT_Sb_30_next_placeholder_BUILD_REPORT.md` | [28297660877](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/28297660877) ✅ 3/3 | Router +28 l (helper + dict + injection) ; template +6 l (placeholder conditionnel `is_active and loop.first`) ; 0 CSS / 0 JS / 0 migration ; 0 changement engine/inputs/explainer/scoring/substitution/coach/recommendation ; `value=""` strict (jamais préremplissage) |
| Sb_30.bugfix.history-identity-guard | Bugfix critique dogfood : alignement template + politique substitution V1 + garde-fou aberrant (11 tests) | ✅ | dogfood Sx_30 | `SPRINT_Sb_30_bugfix_overload_history_identity_guard_BUILD_REPORT.md` | [28433445051](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/28433445051) ✅ 3/3 | `overload_inputs.py` +85 l (filtre `template_slug_snapshot`, `_matches_substitution_policy`, `_history_weight_is_plausible` ratio 3×) ; 0 changement engine/explainer/scoring/substitution/recommendation/body_intelligence ; 0 migration / 0 JS |
| **Sx_31** Body Intelligence v2 | SPEC ONLY ouverte sous override #4 (post-closure Sx_30) | 🟡 EN COURS | `SPIGNOS_BODY_INTELLIGENCE_V2_SPEC.md` | `SPRINT_Sx_31_body_intelligence_v2_REPORT.md` | [28300352085](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/28300352085) ✅ 3/3 | Build queue Sb_31.1→Sb_31.5 ; OQ A/B/C/D/E/F/G tranchées 2026-06-27 |
| Sb_31.1 | `body_intelligence.py` composeur pur + 38 tests | ✅ | Sx_31 §N.2 | `SPRINT_Sb_31_1_body_intelligence_composer_BUILD_REPORT.md` | [28302706112](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/28302706112) ✅ 3/3 | 415 lignes service ; 0 router/template/migration/CSS/JS ; 0 service métier core touché ; OQ-C (seuils figés) + OQ-D (BMI derived) + OQ-E (overload not_available_v1) implémentées |
| Sb_31.2 | Route `GET /body/intelligence` + couche I/O + template + CSS dédié (30 tests) | ✅ | Sx_31 §N.2 | `SPRINT_Sb_31_2_body_route_and_inputs_BUILD_REPORT.md` | [28317125588](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/28317125588) ✅ 3/3 | Collision `/body` (track Body Manual Profile PR #15) résolue via `/body/intelligence` ; 240 l service I/O + 47 l router + 209 l template + 230 l CSS ; 0 migration / 0 JS / 0 service métier core muté ; pipeline `inputs → compute_body_intelligence → template` |
| Sb_31.3 | Bloc Snapshot Body Intelligence dans `/coach-report` (23 tests) | ✅ | Sx_31 §N.2 | `SPRINT_Sb_31_3_body_snapshot_in_coach_report_BUILD_REPORT.md` | [28319392397](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/28319392397) ✅ 3/3 | Router coach-report +6 l ; partial 67 l + include 6 l template ; 0 modification `coach_report.py` service (test garde) ; 0 CSS / 0 JS / 0 migration ; pipeline canonique réutilisée |
| Sb_31.4 | A11y consolidation + responsive 360px + perf p95 (28 tests) | ✅ | Sx_31 §N.2 | `SPRINT_Sb_31_4_body_intelligence_a11y_perf_responsive_BUILD_REPORT.md` | [28321554285](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/28321554285) ✅ 3/3 | CTA snapshot aria-label explicite + flèche aria-hidden ; CSS +23 l (wrapper safety + collapse kv + media 360px) ; tests p95 budgets larges (2.5s body, 3s coach) ; 0 modif composer/inputs/coach_report service ; 0 migration / 0 JS / 0 API JSON |
| Sb_31.5 | Closure docs + dogfood template (DOC only) | ✅ | Sx_31 §N.2 | `SPRINT_Sb_31_5_body_intelligence_closure_BUILD_REPORT.md` | [28322377053](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/28322377053) ✅ 3/3 | Doc only ; 0 code applicatif modifié ; closure + dogfood template livrés |
| **Sx_31 CLOSURE** | Technically closed — dogfood device réel pending | ✅ TECH CLOSED | `Sx_31_CLOSURE_REPORT.md` + `dogfood/DOGFOOD_Sx_31_BODY_INTELLIGENCE_TEMPLATE.md` | — | [28322377053](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/28322377053) ✅ | 6/7 OQ implémentées (OQ-G livrée via Sb_31.next.profile-link 2026-06-29 ; OQ-F home-card reste différée). Sx_32/33+ restent bloqués. |
| Sb_31.next.profile-link | Lien /profile → /body/intelligence (OQ-G) — 17 tests | ✅ | Sx_31 §N.1 | `SPRINT_Sb_31_next_profile_link_BUILD_REPORT.md` | [28358444492](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/28358444492) ✅ 3/3 | Template +13 l (carte standalone "Lecture corporelle") ; 0 CSS / 0 JS / 0 migration / 0 service métier core muté ; aucune duplication contenu Body Intelligence |
| Sx_29+ alternatives | Sx_32 (PWA) / Sx_33+ (Health/API) | ❌ BLOQUÉS | — | — | — | Override séparé requis pour chaque |

## 1quater. Cycle Body Intelligence — Manual Body Profile → providers later (actif)

**Specs :** `docs/strategy/SPIGNOS_BODY_SIGNAL_MODEL_BRAINSTORMING.md`, `SPIGNOS_BODY_INTELLIGENCE_ROADMAP.md`, `SPIGNOS_BODY_SIGNAL_MODEL_SPEC.md`, `SPIGNOS_BODY_PRIVACY_AND_CONSENT_SPEC.md`, `SPIGNOS_BODY_MANUAL_PROFILE_BUILD_SPEC.md`.
**Hard contracts spécifiques :** non médical, non discriminatoire, « morphotype » jamais vérité primaire ; privacy-by-design (consentement granulaire, hard-delete, minimisation) ; providers (MediaPipe/Bodygram) derrière interfaces, flags OFF par défaut ; **une seule migration Body en vol** ; ADD COLUMN ONLY.

| Sprint | Domaine | Statut | Spec ref | Rapport | CI run | Notes |
|---|---|---|---|---|---|---|
| Sx Body 00 (spec) | Brainstorming + roadmap (taxonomie 6 états, 30 Q&A, 5 lots) | ✅ mergé | — | PR #13 | (squash `3fb8faa`) | Docs only ; admin merge inutile (UNSTABLE) |
| Sx Body 01 (spec) | Signal model + privacy/consent + build spec Sb Body 01 (7 états, mesures MVP, ratios, versionnement) | ✅ mergé | — | PR #14 | (squash `662ed49`) | Docs only ; admin override (SonarCloud skip docs-only) |
| Sb Body 01 | Manual Body Profile MVP sous flag `BODY_ASSESSMENT_ENABLED` (mesures manuelles, consentement, hard-delete, export, ratios à la volée, 1 migration additive) | 🟡 build | `SPIGNOS_BODY_MANUAL_PROFILE_BUILD_SPEC.md` | `SPRINT_Sb_Body_01_manual_profile_BUILD_REPORT.md` | (PR draft) | Migration `7i0f5d1e2g43` (3 colonnes additives + `body_consents`) ; 0 provider / 0 photo / 0 MediaPipe / 0 Bodygram ; mode séance intact ; 10 tests dédiés |
| Sx Body 02 (spec) | MediaPipe Capture Quality spec — client-side only, vendored (pas de CDN), flag dédié `BODY_CAPTURE_QUALITY_ENABLED`, 0 persistance image/vidéo/landmark, build plan 02.1→02.R | 🟡 spec | `SPIGNOS_BODY_CAPTURE_QUALITY_SPEC.md` | `SPRINT_Sx_Body_02_capture_quality_SPEC_REPORT.md` | (PR draft) | Docs only ; recherche docs officielles MediaPipe Pose Landmarker ; 0 code / 0 dépendance / 0 MediaPipe installé |
| Sb Body 02 | MediaPipe Capture Quality (build) | 🟡 en cours | `SPIGNOS_BODY_CAPTURE_QUALITY_SPEC.md` | — | — | Pré-requis : Sx Body 02 verrouillée ; flag `BODY_CAPTURE_QUALITY_ENABLED` distinct ; build queue Sb Body 02.1→02.R |
| Sb Body 02.1 | Capture Quality shell (flag dédié OFF + route `GET /body/capture-quality` + template placeholder) — 21 tests | ✅ (PR draft) | `SPIGNOS_BODY_CAPTURE_QUALITY_SPEC.md` | `SPRINT_Sb_Body_02_1_capture_quality_shell_BUILD_REPORT.md` | (PR draft) | 0 caméra / 0 JS / 0 MediaPipe / 0 CDN / 0 worker / 0 upload / 0 stockage / 0 migration / 0 dépendance / 0 CSS nouvelle ; router-level gate aligné #17 et #19 ; non-régression Sx_30 / overload garantie |
| Sb Body 03 | Bodygram Integration | ⏳ | roadmap | — | — | Pré-requis : Sb Body 01 mergé + consent provider |
| Sb Body 04 | Archetype Engine | ⏳ | roadmap | — | — | Pré-requis : Sb Body 01 mergé |
| Sb Body 05 | Link to Training Engine | ⏳ | roadmap | — | — | Pré-requis : Sb Body 04 |

## 1quinquies. Cycle Sx_UI — Auren Visual & Product Transformation (SPEC PENDING)

**Roadmap :** `docs/strategy/UI_TRANSFORMATION_ROADMAP.md`
**Brainstorm sources :** `docs/strategy/brainstorm/UI_TRANSFORMATION_BRAINSTORM_V1_normalized.md`, `..._V2_normalized.md`
**Rebrand :** Spignos → **Auren** (documented direction only, no code touched)
**Statut :** ⚪ 11 specs à écrire ; ordre strict Sx_UI_01 → Sx_UI_11 (avec Sx_UI_11 baseline avant Sx_UI_04)
**Unlocked by :** `PROD STRUCTURALLY STABLE FOR UI RENOVATION` (`docs/OPS_PROD_STABILIZATION_PROFILE_BODY_COACH_REPORT.md` §10, verdict signé 2026-07-02, commit `ddd476b`)
**Caveat :** `PROD_DOGFOOD_57KG_LIVE_CHECK` reste pending (dette prod critique parallèle, ne bloque pas le cycle UI)
**Hard contracts :**
- aucune spec Sx_UI ne modifie la logique métier (scoring, substitution, coach_report, body_intelligence, overload_engine, recommendation, implicit_signal, quality_score, body_tracking)
- SSR FastAPI + Jinja conservé
- no-JS fallback préservé
- pas de React, pas de SPA, pas de bundler applicatif
- WCAG 2.2 tap targets 44×44 conservés et étendus au shell global
- un accent visuel unique (amendement Sx_UI_02bis requis pour tout ajout)
- rebrand Spignos → Auren exécuté uniquement à `Sx_UI_10`

| Sprint | Domaine | Statut | Précondition | Peut modifier code ? | Rapport |
|---|---|---|---|---|---|
| Sx_UI_01 | Brand Foundation (nom Auren, tone, principes, dispo juridique) | 🟢 **SPEC delivered — pending human review** 2026-07-02 | Gate OPS ✅ | Non (docs) | [`SPRINT_Sx_UI_01_REPORT.md`](../SPRINT_Sx_UI_01_REPORT.md) + [`Sx_UI_01_BRAND_FOUNDATION_SPEC.md`](Sx_UI_01_BRAND_FOUNDATION_SPEC.md) |
| Sx_UI_02 | Design Tokens (palettes teal chirurgical désaturé + bleu minéral fallback, typo, tokens candidats) | ✅ **SPEC ACCEPTED — human reviewed** 2026-07-02 | Sx_UI_01 validé implicite par override opérateur (OQ-B tranché) | Non (docs) | [`SPRINT_Sx_UI_02_REPORT.md`](../SPRINT_Sx_UI_02_REPORT.md) + [`SPRINT_Sx_UI_02_HUMAN_REVIEW_REPORT.md`](../SPRINT_Sx_UI_02_HUMAN_REVIEW_REPORT.md) + [`Sx_UI_02_DESIGN_TOKENS_SPEC.md`](Sx_UI_02_DESIGN_TOKENS_SPEC.md) |
| Sx_UI_03 | App Shell + Navigation (bottom nav 4 = Séance/Programmes/Progression/Profil, Coach contextualisé, Squads/Classement dans Profil, rail desktop) | ✅ **SPEC ACCEPTED — human reviewed** 2026-07-02 | Sx_UI_02 accepted ✅ | Non (docs) | [`SPRINT_Sx_UI_03_REPORT.md`](../SPRINT_Sx_UI_03_REPORT.md) + [`SPRINT_Sx_UI_03_HUMAN_REVIEW_REPORT.md`](../SPRINT_Sx_UI_03_HUMAN_REVIEW_REPORT.md) + [`Sx_UI_03_APP_SHELL_NAVIGATION_SPEC.md`](Sx_UI_03_APP_SHELL_NAVIGATION_SPEC.md) |
| Sx_UI_04 | Session Focus Reskin — 5 sous-sprints, initialement listés Sb_UI_04.1 CSS → .5 polish. **Recadrage 2026-07-04 via `Sx_UI_04_FOCUSED_EXERCISE_FLOW_SPEC`** : passage d'une liste verticale à un **flow séquentiel single-active exercise**. Redécoupage Sb_UI_04.3 = Single Active Exercise Shell, .4 = Set Logging Focus + Next Flow, .5 = Worked Area Visual Slot + Hardening. | ✅ **SPEC PARENT ACCEPTED** 2026-07-02 + ✅ **`Sb_UI_04.1` ACCEPTED** 2026-07-04 (commit `4451743`, CI ✅ [`28700626885`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/28700626885)) + ✅ **`Sb_UI_04.2` ACCEPTED WITH VISUAL DEPTH RESERVATION** 2026-07-04 (commit `8524851`, CI ✅ [`28702740118`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/28702740118)) + 🟢 **RECAST SPEC `Sx_UI_04_FOCUSED_EXERCISE_FLOW_SPEC` delivered — pending human review** 2026-07-04, **renforcée par le Live Exercise Expert Model** (§18, brainstorm PO + lead architecte). Cœur d'écran = **active exercise cockpit** (7 couches : orientation · exercise intent · worked area · technical cues · set logging console · alternatives/substitution · up next), pas simple hero card. Progress rail X/Y + N restants. Worked Area Panel textuel dès V1 + placeholder clinique (pas de GIF/pipeline média, contrat futur `exercise_code → primary_zone → asset_key`). 7 OQ **tranchées direction produit** (§19). Redécoupage renforcé : Sb_UI_04.3 = Active Exercise Cockpit Shell · .4 = Set Logging Console + Progression Guidance · .5 = Worked Area Visual Slot + Alternatives + Hardening. Simple recolor / accordéon **explicitement rejeté**. **Amendement final §23 — Body Representation System** : couche transverse (session card + program preview + profile body intelligence), taxonomie V1 (15 zones), rôles biomécaniques, contrat futur `exercise_code → body_map_descriptor`, visuel V1→V3, prudence anti-médical. **Documentaire uniquement** (aucun modèle/migration/service/asset). Worked Area Panel de Sb_UI_04.3 = premier jalon ; profil/body intelligence = direction future. Aucun build ouvert. `Sb_UI_04.3` BLOCKED tant que recast non accepté. | Sx_UI_11 ✅ + baseline P0 ✅ + Sb_UI_04.1 ✅ + Sb_UI_04.2 ✅ | Non (spec docs-only) ; `Sb_UI_04.k` = Oui (surface uniquement) | [`SPRINT_Sx_UI_04_REPORT.md`](../SPRINT_Sx_UI_04_REPORT.md) + [`SPRINT_Sx_UI_04_HUMAN_REVIEW_REPORT.md`](../SPRINT_Sx_UI_04_HUMAN_REVIEW_REPORT.md) + [`Sx_UI_04_SESSION_FOCUS_RESKIN_SPEC.md`](Sx_UI_04_SESSION_FOCUS_RESKIN_SPEC.md) + [`BASELINE_P0_CAPTURED_2026_07_04.md`](../BASELINE_P0_CAPTURED_2026_07_04.md) + [`SPRINT_Sb_UI_04_1_REPORT.md`](../SPRINT_Sb_UI_04_1_REPORT.md) + [`SPRINT_Sb_UI_04_1_HUMAN_REVIEW_REPORT.md`](../SPRINT_Sb_UI_04_1_HUMAN_REVIEW_REPORT.md) + [`SPRINT_Sb_UI_04_2_REPORT.md`](../SPRINT_Sb_UI_04_2_REPORT.md) + [`SPRINT_Sb_UI_04_2_HUMAN_REVIEW_REPORT.md`](../SPRINT_Sb_UI_04_2_HUMAN_REVIEW_REPORT.md) + [`Sx_UI_04_FOCUSED_EXERCISE_FLOW_SPEC.md`](Sx_UI_04_FOCUSED_EXERCISE_FLOW_SPEC.md) + [`SPRINT_Sx_UI_04_FOCUSED_EXERCISE_FLOW_REPORT.md`](../SPRINT_Sx_UI_04_FOCUSED_EXERCISE_FLOW_REPORT.md) |
| Sx_UI_05 | Today / Readiness Home | ⚪ | Sx_UI_04 | Oui (surface) | — |
| Sx_UI_06 | Exercise Intelligence Presentation | ⚪ | Sx_UI_05 | Oui (surface) | — |
| Sx_UI_07 | History & Progress | ⚪ | Sx_UI_06 | Oui (surface) | — |
| Sx_UI_08 | Portability & Installability (PWA mature) | ⚪ | Sx_UI_07 | Oui (manifest + SW minimal) | — |
| Sx_UI_09 | Accessibility & Motion | ⚪ | parallèle possible dès Sx_UI_04 | Oui (surface + attributs) | — |
| Sx_UI_10 | Rebrand Migration Spignos → Auren (scope infra + code) | ⚪ | Sx_UI_04 minimum validé + OQ-A verdict favorable | Oui (infra + code) | — |
| Sx_UI_11 | Screenshot Regression Baseline — protocole (Playwright Python, 18 écrans × 2 viewports, P0/P1/P2, fixture locale déterministe, revue humaine primaire) | ✅ **SPEC ACCEPTED — human reviewed** 2026-07-02 | Sx_UI_03 accepted ✅ | Non (docs) — build tooling Sb_UI_11.1 séparé, candidat futur non-ouvert | [`SPRINT_Sx_UI_11_REPORT.md`](../SPRINT_Sx_UI_11_REPORT.md) + [`SPRINT_Sx_UI_11_HUMAN_REVIEW_REPORT.md`](../SPRINT_Sx_UI_11_HUMAN_REVIEW_REPORT.md) + [`Sx_UI_11_SCREENSHOT_REGRESSION_BASELINE_SPEC.md`](Sx_UI_11_SCREENSHOT_REGRESSION_BASELINE_SPEC.md) |

**Build remains blocked.** Aucun sprint `Sb_UI_NN.k` d'implémentation autorisé. `Sx_UI_02` reste blocked tant que `Sx_UI_01` n'a pas été validé par human review. Après validation Sx_UI_01, prochain step docs-only : `Sx_UI_02_DESIGN_TOKENS_SPEC` SPEC ONLY.

## 1sexies. Sprints OPS hors-cycle (infra CI, tooling, cost control)

Sprints infra chirurgicaux ne relevant d'aucun cycle produit `Sx_`. Chaque sprint est indépendant, docs + fichier infra ciblé, aucun impact code applicatif.

| Sprint | Domaine | Statut | Rapport | Motivation |
|---|---|---|---|---|
| Sb_OPS.ci-path-filter | Ajout `paths-ignore: ['docs/**']` sur trigger `push` de `.github/workflows/ci.yml`. PR trigger non affecté. `deploy-production.yml` non affecté. | 🟢 **DELIVERED — pending human review** 2026-07-02, validé sur 6 pushes docs-only consécutifs (`b4ed2c6`, `fdfd71a`, `b3ae3a9`, `88ca206`, `2a2be71`) | [`SPRINT_Sb_OPS_ci_path_filter_BUILD_REPORT.md`](../SPRINT_Sb_OPS_ci_path_filter_BUILD_REPORT.md) | Réduction facture GitHub Actions sur cycles docs-only. Économie observée cumulée : ~132 min compute (6 × ~22 min) évitées à ce jour. |
| Sb_UI_11.1 | Screenshot Tooling Build — matrice + CLI Playwright + 92 tests unitaires + anti-secret hard rule + `.gitignore` + extra dep `[baseline]`. Aucun app code touché. Aucun screenshot capturé côté sprint. Aucun Chromium installé en CI. **Capture P0 locale à exécuter par opérateur** avec `.env.baseline` fixture. | ✅ **DELIVERED + CI GREEN + HUMAN REVIEW ACCEPTED** 2026-07-02 (commit `e8ba190`, CI run [`28595637219`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/28595637219) 3/3 jobs ✅ en 21 min 18 s) — **baseline P0 : pending local capture** | [`SPRINT_Sb_UI_11_1_SCREENSHOT_TOOLING_BUILD_REPORT.md`](../SPRINT_Sb_UI_11_1_SCREENSHOT_TOOLING_BUILD_REPORT.md) + [`SPRINT_Sb_UI_11_1_HUMAN_REVIEW_REPORT.md`](../SPRINT_Sb_UI_11_1_HUMAN_REVIEW_REPORT.md) | Précondition dure pour `Sb_UI_04.k` : baseline P0 réellement capturée localement OU dérogation opérateur explicite (**non accordée**). |
| Sb_UI_11.2 | Baseline Runtime Integration Patch — CLI `visual_baseline_runtime.py prepare/verify` intégré à l'app existant (`get_settings`, `SessionLocal`, `instantiate_session`, cookie signé `session_token`). Refuse `app_env=production` + refuse DB non-locale. Patch `visual_baseline_capture.py --runtime-file` avec fallback env vars pour compat Sb_UI_11.1. 145 tests unitaires (dont canary anti-leak + cookie roundtrip auth). Élimine `.env.baseline` manuel + exports shell fragiles. | ✅ **DELIVERED + CI GREEN + HUMAN REVIEW ACCEPTED** 2026-07-02 (commit `a2846a2`, CI run [`28604484292`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/28604484292) 3/3 jobs ✅ en 21 min 21 s) — **baseline P0 CAPTURED LOCALLY 2026-07-04 (16/16 PNG)** | [`SPRINT_Sb_UI_11_2_BASELINE_RUNTIME_PATCH_REPORT.md`](../SPRINT_Sb_UI_11_2_BASELINE_RUNTIME_PATCH_REPORT.md) + [`SPRINT_Sb_UI_11_2_HUMAN_REVIEW_REPORT.md`](../SPRINT_Sb_UI_11_2_HUMAN_REVIEW_REPORT.md) + [`BASELINE_P0_CAPTURED_2026_07_04.md`](../BASELINE_P0_CAPTURED_2026_07_04.md) | Débloque l'exécution locale P0 sans environnement parallèle. **`Sb_UI_04.k` peut désormais être proposé** — précondition baseline P0 satisfaite. Aucune dérogation nécessaire. |

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
