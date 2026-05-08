# SPIGNOS — Sprint Index

Index navigable de tous les sprints livrés. Chaque ligne pointe vers le rapport correspondant. Utiliser ce fichier pour retrouver rapidement « qu'est-ce qui a été fait dans Sb_X » sans parcourir 50 fichiers.

**Dernière mise à jour :** 2026-05-08 — post Sb_20.5

---

## Cycles produit majeurs

| Cycle | Période | Statut | Sprints inclus |
|-------|---------|--------|----------------|
| Bootstrap (S0–S4 / 01–08) | mars–avr. 2026 | ✅ clos | Pré-Session System V1 (catalogue, sessions, scoring, exports) |
| Sx_01–Sx_04 | avr. 2026 | ✅ clos | Specs fondatrices (scoring, modèle, exercices, substitution) |
| Session System V1 (Sb_05 → Sb_10) | avr. 2026 | ✅ clos + Sx_10 audit | Flow horizontal, catalog, atlas, review, history |
| Reco engine (Sb_11a → Sb_18) | avr.–mai 2026 | ✅ clos | Briefing, V1 reco, telemetry, V2 antagoniste |
| CI/CD (Sx_16 → Sb_16.5) | avr. 2026 | ✅ live | Pipeline GitHub Actions → OVH VPS |
| Dogfooding fixpacks | mai 2026 | ✅ traité | Fixpack v1, catalog v13, profile/leaderboard sprints |
| Security & Sonar (Sx_20 → Sb_20.5) | mai 2026 | ✅ V1 advisory | Coverage, ruff/bandit, hardening fonctionnel, SonarCloud, gate |

---

## Phase Bootstrap (avant Session System V1)

| Sprint | Sujet | Rapport |
|--------|-------|---------|
| S0 | Bootstrap projet | [SPRINT_S0_REPORT.md](SPRINT_S0_REPORT.md) |
| S1 | Logique métier base | [SPRINT_S1_REPORT.md](SPRINT_S1_REPORT.md) |
| S2 | Sessions schema | [SPRINT_S2_REPORT.md](SPRINT_S2_REPORT.md) |
| S3 | Scoring V1 | [SPRINT_S3_REPORT.md](SPRINT_S3_REPORT.md) |
| S4 | Exports + tests | [SPRINT_S4_REPORT.md](SPRINT_S4_REPORT.md) |
| Sprint 01 | (legacy) | [SPRINT_01_REPORT.md](SPRINT_01_REPORT.md) |
| Sprint 02 | (legacy) | [SPRINT_02_REPORT.md](SPRINT_02_REPORT.md) |
| Sprint 03 | (legacy) | [SPRINT_03_REPORT.md](SPRINT_03_REPORT.md) |
| Sprint 04 | (legacy) | [SPRINT_04_REPORT.md](SPRINT_04_REPORT.md) |
| Sprint 05 | (legacy) | [SPRINT_05_REPORT.md](SPRINT_05_REPORT.md) |
| Sprint 06 | (legacy) | [SPRINT_06_REPORT.md](SPRINT_06_REPORT.md) |
| Sprint 07 | (legacy) | [SPRINT_07_REPORT.md](SPRINT_07_REPORT.md) |
| Sprint 08 | (legacy) | [SPRINT_08_REPORT.md](SPRINT_08_REPORT.md) |
| Synthesis | Bilan multi-sprints | [SPRINT_SYNTHESIS.md](SPRINT_SYNTHESIS.md) |
| V2.1 | Refonte intermédiaire | [SPRINT_V2.1_REPORT.md](SPRINT_V2.1_REPORT.md) |

---

## Phase Sx_01–Sx_04 — Specs fondatrices

| Sprint | Sujet | Rapport |
|--------|-------|---------|
| Sx_01 | Scoring rules | [SPRINT_Sx_01_FINAL_REPORT.md](SPRINT_Sx_01_FINAL_REPORT.md) |
| Sx_02 | Domain model | [SPRINT_Sx_02_FINAL_REPORT.md](SPRINT_Sx_02_FINAL_REPORT.md) |
| Sx_03 | Exercice substitution graph | [SPRINT_Sx_03_FINAL_REPORT.md](SPRINT_Sx_03_FINAL_REPORT.md) |
| Sx_04 | Mobile UX exercise entry | [SPRINT_Sx_04_FINAL_REPORT.md](SPRINT_Sx_04_FINAL_REPORT.md) |

---

## Phase build pré-V1 (catalog / launcher / cardio / R3)

| Sprint | Sujet | Rapport |
|--------|-------|---------|
| Sb_01 | Bootstrap session | [SPRINT_Sb01_REPORT.md](SPRINT_Sb01_REPORT.md) |
| Sb_02 | Carte exercice | [SPRINT_Sb02_REPORT.md](SPRINT_Sb02_REPORT.md) |
| Sb_02.1 | Jump bar + CTA | [SPRINT_Sb_02_1_REPORT.md](SPRINT_Sb_02_1_REPORT.md) |
| Sb_03 | Substitution | [SPRINT_Sb03_REPORT.md](SPRINT_Sb03_REPORT.md) |
| Sb_R3 | Terminal state /done | [SPRINT_Sb_R3_REPORT.md](SPRINT_Sb_R3_REPORT.md) |
| Sb_cardio_capture | Cardio fields | [SPRINT_Sb_cardio_capture_REPORT.md](SPRINT_Sb_cardio_capture_REPORT.md) |
| Sb_catalog_substitution_v1 | Substitution graph build | [SPRINT_Sb_catalog_substitution_v1_REPORT.md](SPRINT_Sb_catalog_substitution_v1_REPORT.md) |
| Sb_catalog_balance_v1 | Push A trim → v10 | [SPRINT_Sb_catalog_balance_v1_REPORT.md](SPRINT_Sb_catalog_balance_v1_REPORT.md) |
| Sb_launcher_v1 | New session picker | [SPRINT_Sb_launcher_v1_REPORT.md](SPRINT_Sb_launcher_v1_REPORT.md) |
| Sb_science_page | /science page | [SPRINT_Sb_science_page_REPORT.md](SPRINT_Sb_science_page_REPORT.md) |

---

## Cycle Session System V1 (Sb_05 → Sb_10 + audit Sx_10)

| Sprint | Sujet | Rapport | Spec |
|--------|-------|---------|------|
| Sx_05 | Session flow & intelligence spec | [report](SPRINT_Sx_05_session_flow_and_intelligence_spec_REPORT.md) | [strategy/SPIGNOS_SESSION_FLOW_AND_INTELLIGENCE_SPEC_v1.md](strategy/SPIGNOS_SESSION_FLOW_AND_INTELLIGENCE_SPEC_v1.md) |
| Sx_06 | Scoring/load/time semantics | [report](SPRINT_Sx_06_REPORT.md) | [strategy/SPIGNOS_SCORING_LOAD_TIME_SEMANTICS_SPEC_v1.md](strategy/SPIGNOS_SCORING_LOAD_TIME_SEMANTICS_SPEC_v1.md) |
| Sx_07 + Sx_08 | Atlas + review intelligence | [report](SPRINT_Sx_07_Sx_08_REPORT.md) | [atlas](strategy/SPIGNOS_MACHINE_KNOWLEDGE_AND_SUBSTITUTION_SURFACE_SPEC_v1.md), [review](strategy/SPIGNOS_SESSION_REVIEW_INTELLIGENCE_SPEC_v1.md) |
| Sb_05 | Session flow horizontal | [report](SPRINT_Sb_05_REPORT.md) | — |
| Sb_06 | Scoring/load/time build (4 étapes) | [report](SPRINT_Sb_06_REPORT.md) | — |
| Sb_07 | Machine atlas + substitution surface | [report](SPRINT_Sb_07_REPORT.md) | — |
| Sb_08 | Session review intelligence | [report](SPRINT_Sb_08_REPORT.md) | — |
| Sb_09 | History visual & analytics alignment | [report](SPRINT_Sb_09_REPORT.md) | — |
| **Sx_10** | **V1 gap audit** (post-cycle) | [report](SPRINT_Sx_10_session_v1_gap_audit_spec_REPORT.md) | [spec](strategy/SPIGNOS_SESSION_V1_GAP_AUDIT_SPEC.md) + [matrix](strategy/SPIGNOS_SESSION_V1_GAP_MATRIX.md) |
| Sb_10 | Polish (G1 + G2 closure) | [report](SPRINT_Sb_10_session_v1_polish_REPORT.md) | — |
| catalog v12 | Pull A balance | (interne au commit `b7a43ee`) | — |

---

## Cycle Reco Engine (Sb_11a → Sb_18)

| Sprint | Sujet | Rapport | Spec |
|--------|-------|---------|------|
| Sx_11a | Pre-session briefing | [report](SPRINT_Sx_11a_pre_session_briefing_spec_REPORT.md) | [spec](strategy/SPIGNOS_PRE_SESSION_BRIEFING_SPEC_v1.md) |
| Sb_11a | Briefing build (chip + peek) | [report](SPRINT_Sb_11a_pre_session_briefing_BUILD_REPORT.md) | — |
| Sx_12 | Next-session recommendation V1 | [report](SPRINT_Sx_12_next_session_recommendation_spec_REPORT.md) | [spec](strategy/SPIGNOS_NEXT_SESSION_RECOMMENDATION_SPEC_v1.md) |
| Sb_12 | Reco V1 build | [report](SPRINT_Sb_12_next_session_recommendation_BUILD_REPORT.md) | — |
| Sx_13 | Reco calibration spec | [report](SPRINT_Sx_13_recommendation_calibration_spec_REPORT.md) | [spec](strategy/SPIGNOS_RECOMMENDATION_CALIBRATION_SPEC_v1.md) |
| Sb_13 | Telemetry `creation_source` + CLI report | [report](SPRINT_Sb_13_recommendation_telemetry_and_tuning_BUILD_REPORT.md) | — |
| **Sx_18** | **Reco V2 antagoniste + récup scientifique** | (commit `e0a5ff1`) | [spec](strategy/SPIGNOS_RECO_V2_ANTAGONIST_SPEC_v1.md) |
| **Sb_18** | **Reco V2 build — availability_by_zone** | (commit `eda3512`, +13 tests) | — |

---

## Cycle CI/CD (Sx_16 → Sb_16.5)

| Sprint | Sujet | Rapport | Spec |
|--------|-------|---------|------|
| Sx_16 | Prod CI/CD pipeline spec | [report](SPRINT_Sx_16_prod_cicd_pipeline_spec_REPORT.md) | [spec](strategy/SPIGNOS_PROD_CICD_PIPELINE_SPEC_v1.md) |
| Sb_16 | Pipeline build initial | [report](SPRINT_Sb_16_prod_cicd_pipeline_BUILD_REPORT.md) + [runbook](CICD_RUNBOOK.md) | — |
| Sb_16.1 | Align VPS layout `/opt/...` + user `ubuntu` | (commit `00011e4`) | — |
| Sb_16.2 | `SKIP_GIT_PULL` redondance | (commit `dbdd658`) | — |
| Sb_16.3 | `deploy_prod.sh` en root pour `systemctl` | (commit `6a75529`) | — |
| Sb_16.4 | YAML paths align | (commit `809aced`) | — |
| Sb_16.5 | Smoke `cd` + ordre backup avant /healthz/strict | (commit `19c9c52`) | — |

---

## Cycle Dogfooding (post Sb_16.5)

| Sprint | Sujet | Commit / Rapport |
|--------|-------|------------------|
| Dogfooding pass v1 | Notes operator 7j | [DOGFOOD_NOTES.md](DOGFOOD_NOTES.md) (commit `6670c0b`) |
| Sb_dogfood_fixpack v1 | B1 wording / B2 textarea / B3 hexagone | commit `59a93ea` |
| Sb_catalog_v13 | C1 adductions + C2 tirage Pull B | [report](SPRINT_Sb_catalog_v13_REPORT.md) (commit `73ab0d0`) |
| Sb_17 | F1 — fusion sources poids profile | commit `fffc282` |
| **Sx_19** | **Leaderboard drilldown spec** | [spec](strategy/SPIGNOS_LEADERBOARD_DRILLDOWN_SPEC_v1.md) (commit `9082c0b`) |
| **Sb_19** | **Tooltip mini radar + /users/{username}** | commit `c3693d9` |

---

## Cycle Security & Sonar (Sx_20 → Sb_20.5)

| Sprint | Sujet | Lien |
|--------|-------|------|
| **Sx_20** | **Security hardening + SonarCloud integration spec** | [spec](strategy/SPIGNOS_SECURITY_HARDENING_AND_SONAR_INTEGRATION_SPEC_v1.md) (commit `0f5eb9f`) |
| Sb_20.1 | Coverage infra (pytest-cov, 89.97%) | [report](SPRINT_Sb_20_1_REPORT.md) (commit `5e59062`) |
| Sb_20.2 | Linters CI advisory (ruff + bandit) | [report](SPRINT_Sb_20_2_REPORT.md) (commit `9ef742a`) |
| Sb_20.3 | Hardening fonctionnel (username regex, mdp ≥8, email regex, /users path) | [report](SPRINT_Sb_20_3_REPORT.md) (commit `7097022`) |
| Sb_20.4 | SonarCloud integration (config + ci.yml job + runbook §3.4 + triage template) | [report](SPRINT_Sb_20_4_REPORT.md) + [template](SONARCLOUD_TRIAGE_TEMPLATE.md) (commit `8c9244f`) |
| Sb_20.5 | Verrouillage CI gate + bilan avant/après | [report](SPRINT_Sb_20_5_REPORT.md) |

---

## Specs strategy notables (sans build associé direct)

| Sujet | Lien |
|-------|------|
| Catalog benchmark review | [strategy/SPIGNOS_CATALOG_BENCHMARK_REVIEW_v1.md](strategy/SPIGNOS_CATALOG_BENCHMARK_REVIEW_v1.md) |
| Catalog governance | [strategy/SPIGNOS_CATALOG_GOVERNANCE.md](strategy/SPIGNOS_CATALOG_GOVERNANCE.md) |
| V1 dogfooding checklist | [strategy/SPIGNOS_V1_DOGFOODING_CHECKLIST.md](strategy/SPIGNOS_V1_DOGFOODING_CHECKLIST.md) |
| Squads model (privacy) | [strategy/SPIGNOS_SQUADS_PRIVACY_MODEL.md](strategy/SPIGNOS_SQUADS_PRIVACY_MODEL.md) |
| Body engineering dashboard | [strategy/SPIGNOS_BODY_ENGINEERING_DASHBOARD_V1.md](strategy/SPIGNOS_BODY_ENGINEERING_DASHBOARD_V1.md) |
| Session system consolidation (Sx_09) | [strategy/SPIGNOS_SESSION_SYSTEM_CONSOLIDATION_SPEC_v1.md](strategy/SPIGNOS_SESSION_SYSTEM_CONSOLIDATION_SPEC_v1.md) |
| Sprint queue master | [strategy/SPIGNOS_SUPERPOWER_SPRINT_QUEUE.md](strategy/SPIGNOS_SUPERPOWER_SPRINT_QUEUE.md) |

---

## État branche actuel — `claude/sprint-reporting-fitness-app-V7Qr6`

- **HEAD** : `30e3a81` (Sb_20.x cycle clos + CI fixes)
- **Tests** : 739 passed (+5 vs Sb_18 — tests Sb_20.3 hardening)
- **Coverage** : 89.97 % (mesurée Sb_20.1)
- **Catalog** : v13
- **Atlas** : 8 familles / 29 machines
- **Migrations** : head Alembic `c3d5f1e82a04`
- **Pipeline CI/CD** : Active sur 3 jobs (test + lint advisory + sonar advisory), dernier deploy réussi `19c9c52` (Sb_16.5, 21 avril)
- **SonarCloud** : org `mfe-dss`, scan advisory V1, Quality Gate `Spignos Way` à activer côté UI (runbook §3.4)
- **Branche en attente de deploy** : ≥ 12 commits non déployés (de `73ab0d0` à `30e3a81` inclus)

## Comment ajouter un sprint à cet index

À chaque nouveau sprint Sb/Sx livré :

1. Ajouter une ligne dans la section cycle correspondante.
2. Mettre à jour `Dernière mise à jour` en tête.
3. Mettre à jour la section « État branche actuel » si pertinent.
4. Commit en standalone : `docs: SPRINT_INDEX update — Sb_XX added`.

Pas de tests sur ce fichier — pure documentation navigable.
