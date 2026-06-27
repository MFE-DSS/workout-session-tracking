# SPRINT Sb Body 01 — Manual Body Profile (BUILD REPORT)

**Branche :** `sb-body-01-manual-profile` (worktree isolé sur le tip de référence `662ed496`)
**Spec amont :** `docs/strategy/SPIGNOS_BODY_MANUAL_PROFILE_BUILD_SPEC.md` (+ `SPIGNOS_BODY_SIGNAL_MODEL_SPEC.md`, `SPIGNOS_BODY_PRIVACY_AND_CONSENT_SPEC.md`)
**Date :** 2026-06-27
**Statut :** 🟡 build livré, PR draft, **non mergé, non déployé**.

---

## 1. Objectif

Implémenter le MVP **Manual Body Profile** sous feature flag `BODY_ASSESSMENT_ENABLED` (défaut OFF) : profil corporel manuel, consentement explicite, CRUD avec hard-delete, export Body, ratios MVP calculés à la volée, pages SSR mobile-first. **Aucun** provider, photo, MediaPipe, Bodygram, ni modification du mode séance.

## 2. Périmètre livré

| Domaine | Détail |
|---|---|
| Feature flag | `body_assessment_enabled: bool = Field(default=False)` (`app/config.py`). Flag OFF → toutes les routes `/body` renvoient 404. |
| Modèle (additif) | `body_measurements` + 3 colonnes Float nullable : `shoulder_width_cm`, `calf_cm_left`, `calf_cm_right`. Nouveau modèle `BodyConsent` (`body_consents`). |
| Migration | **Une seule** migration additive `7i0f5d1e2g43` (down_revision `6h9e4c0d1f32`). ADD COLUMN ONLY + `CREATE TABLE body_consents`. Guards idempotents. |
| Consentement | `consent_body_measurements` granulaire, explicite, versionné, retirable. Saisie bloquée sans consentement. |
| CRUD | Création / édition / suppression (**hard-delete**) de mesures, **ownership** strict (`user_id`). |
| Ratios MVP | 6 ratios `derived` calculés **à la volée** (jamais persistés), avec fallback/proxy + confiance + `ratio_engine_version`. |
| Export | `GET /body/export.json` — mesures + consentements + ratios du dernier point, **user-scoped**. |
| UI | SSR mobile-first : `body_overview.html`, `measurement_form.html` (consentement inline). |
| Garde wording | `FORBIDDEN_WORDING` + `assert_no_forbidden_wording` (aucun terme médical/discriminatoire). |

## 3. Fichiers

**Ajoutés :**
- `app/models/body_consent.py`
- `app/services/body_profile.py`
- `app/routers/body.py`
- `app/templates/body_assessment/body_overview.html`
- `app/templates/body_assessment/measurement_form.html`
- `migrations/versions/20260627_add_body_profile_mvp.py`
- `tests/test_body_profile.py`
- `docs/SPRINT_Sb_Body_01_manual_profile_BUILD_REPORT.md`

**Modifiés (additif) :**
- `app/config.py` (flag)
- `app/models/measurement.py` (+3 colonnes)
- `app/models/__init__.py` (enregistrement `body_consent`)
- `app/main.py` (include router)
- `data/schema_snapshot.sql` (régénéré)
- `docs/strategy/SPEC_REGISTRY.md` (cycle Body)

**Non touchés (interdits respectés) :** `requirements.txt`, `pyproject.toml`, `.env*`, `deploy/`, `scripts/`, mode séance (`session_detail.html`, `session_focus.*`, overload).

## 4. Contrat DB

- ADD COLUMN ONLY ✅ — aucune suppression / rename / changement incompatible.
- Une seule migration ✅. Colonnes additives nullable (pas de server_default requis). `body_consents` créé.
- Legacy `calf_cm` (single) **préservé** ; nouvelles entrées écrivent `calf_cm_left/right`.
- Migration linter (`check_migration_patterns.py`) : **OK** (0 pattern dangereux non justifié).
- Schema snapshot régénéré + `check_schema_snapshot.py` : **OK** (snapshot == alembic head).
- Roundtrip (`check_migration_roundtrip.py`) : **OK** (schéma identique upgrade→downgrade→upgrade).
- Drift guard (`test_alembic_drift.py`) : **OK** (Base.metadata == head).

## 5. Tests

`tests/test_body_profile.py` — 10 tests, tous verts :
- feature flag OFF (404 sur toutes les routes) ;
- consentement requis (POST sans consentement → 0 ligne) ;
- consentement accordé → création OK ;
- bornes de plausibilité (valeur hors plage / non numérique → 400, 0 ligne) ;
- ownership (mesure d'un autre user → 404) ;
- hard-delete (ligne réellement supprimée) ;
- export user-scoped (n'expose pas les données d'autrui) ;
- ratios fallback/confiance (proxy chest/waist, none si inputs manquants) ;
- wording guard (aucun terme interdit ; lève sur terme médical) ;
- non-régression mode séance (`/`, `/physique`, `/history` → 200 flag ON).

## 6. Checks exécutés (local, .venv)

| Check | Résultat |
|---|---|
| `pytest tests/test_body_profile.py` | ✅ 10 passed |
| sous-ensemble guards + non-régression (drift, migration hardening, auth scope, dashboard routes, export) | ✅ 46 passed |
| `pytest --ignore=tests/test_v1_acceptance.py` (CI-equivalent, suite complète) | ✅ **1269 passed** in 402s (0 failed) |
| `pytest` (full local, incl. v1_acceptance) | 4 échecs `*vscode*` environnementaux (CI les exclut) — non causés par ce sprint |
| `ruff check` (fichiers du sprint) | ✅ All checks passed (0 nouveau warning) |
| `check_ruff_budget.py` | ✅ 526 ≤ 548 (baseline non dépassée) |
| `check_migration_patterns.py` | ✅ OK |
| `check_migration_roundtrip.py` | ✅ OK |
| `check_schema_snapshot.py` | ✅ OK |

## 7. Non-goals respectés

❌ photo upload · ❌ image analysis · ❌ MediaPipe · ❌ Bodygram · ❌ provider externe · ❌ body fat estimation · ❌ diagnostic médical · ❌ score humiliant · ❌ morphotype comme vérité primaire · ❌ recommandation persistée complète (différée Sb Body 04) · ❌ modification auto du programme · ❌ lien graphe de substitution (Sb Body 05) · ❌ modification mode séance / templates session · ❌ `requirements.txt` / `.env*` · ❌ déploiement.

## 8. Limites restantes

- Ratios calculés sur le **dernier** point uniquement (pas de tendance ≥ 3 points — hors MVP).
- `recommandation` non persistée (le MVP affiche des ratios, pas de moteur de reco — `Sb Body 04`).
- `body_recommendations` **non créé** (conforme à la consigne).
- `shoulder_width_cm` manuel = best-effort (OQ-S1 ouverte).
- Pas de lien training / substitution (`Sb Body 05`).
- Coordination multi-agent : build réalisé en **worktree isolé** sur `662ed49` pour éviter tout drift (cf. incident `61a6ffb`).

## 9. CI réelle

<!-- À compléter après push : run GitHub Actions de la PR (lint budget / pytest / SonarCloud). -->

## Verdict

🟡 **BUILD LIVRÉ — PR draft, non mergé, non déployé.**

- Périmètre MVP conforme à la spec `Sb Body 01` : mesures manuelles, consentement, hard-delete, export, ratios à la volée, 1 migration additive, flag OFF par défaut.
- Contrat DB respecté (ADD COLUMN ONLY, snapshot/roundtrip/drift verts).
- 10 tests dédiés verts ; sous-ensemble guards + non-régression vert (46).
- 0 provider / 0 photo / 0 MediaPipe / 0 Bodygram ; mode séance intact.
- Tests `test_v1_acceptance::*vscode*` (4) rouges = **environnementaux** (fichiers `.vscode/` gitignorés absents d'un checkout neuf), **non causés par ce sprint** ; identiques sur la base.
- Reste subordonné à : CI réelle verte + revue anti-drift + feu vert opérateur avant tout merge.
