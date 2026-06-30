# Sb_Body_02.1 — Capture Quality Shell (Build Report)

**Branche source :** `sb-body-02-1-capture-quality-shell` (worktree isolé)
**Base :** `claude/sprint-reporting-fitness-app-V7Qr6` @ `a82ef41` (post-merge PR #20)
**Date :** 2026-06-30
**Spec parent :** `docs/strategy/SPIGNOS_BODY_CAPTURE_QUALITY_SPEC.md` (mergée PR #20)
**Lot :** Sb Body 02.1 (shell — 1er lot du build queue 02.1 → 02.R)
**Type :** **BUILD shell only** — flag dédié OFF par défaut, 0 caméra, 0 JS, 0 MediaPipe, 0 stockage.

---

## 1. Résumé exécutif

Pose le shell applicatif de la future capture-quality Body : un flag dédié `BODY_CAPTURE_QUALITY_ENABLED` (par défaut OFF), une route SSR `GET /body/capture-quality` derrière une dépendance router-level (404 avant auth), et un template placeholder strictement statique. Aucune caméra, aucun JavaScript, aucun MediaPipe, aucun modèle, aucun CDN, aucun web worker, aucun upload, aucun stockage. Aucun changement requirements/pyproject/.env*. Aucune migration.

## 2. Pré-checks (verbatim brief)

| Pré-check | Statut |
|---|---|
| PR #20 mergée (SHA `a82ef4169629c2946bcbac76e83cf9a20197cc4d`) | ✅ |
| Branche cible contient bugfix Sx_30 `10732e9` | ✅ |
| Branche cible contient bugfix Sx_30 `96d1eff` | ✅ |
| Working tree clean | ✅ |
| Aucune migration concurrente en vol | ✅ |
| Sx_30 / overload / dogfood non touchés | ✅ (test garde implicite par les non-régressions) |

## 3. Fichiers modifiés / créés

| Fichier | Type | Description |
|---|---|---|
| `app/config.py` | MODIFIED | +9 l : nouveau flag `body_capture_quality_enabled: bool = Field(default=False)` distinct de `body_assessment_enabled` et `body_intelligence_enabled`, accompagné d'un commentaire de contrat. |
| `app/routers/body_capture.py` | **NEW** | 57 l : router avec `require_body_capture_quality_enabled` (router-level dependency) + 1 route shell `GET /body/capture-quality` qui rend le template placeholder. |
| `app/main.py` | MODIFIED | +2 imports + +5 l include_router (mounted derrière le gate, inert quand flag OFF). |
| `app/templates/body_capture_quality.html` | **NEW** | 36 l : shell SSR strict. Aucun `<script>`, aucun `<form>`, aucun `<input>`, aucun lien externe. Wording placeholder fidèle au brief. |
| `tests/test_body_capture_quality_gate.py` | **NEW** | 21 tests : OFF/ON × anon/auth, indépendance vs `BODY_ASSESSMENT_ENABLED`/`BODY_INTELLIGENCE_ENABLED`, non-exposition liens, privacy/static, non-régression gates #17 et #19 + `/progress` + `/physique`. |
| `docs/SPRINT_Sb_Body_02_1_capture_quality_shell_BUILD_REPORT.md` | **NEW** | Ce rapport. |
| `docs/strategy/SPEC_REGISTRY.md` | MODIFIED | +1 ligne : entrée Sb Body 02.1. |

### Non touché (vérification explicite)
- `app/services/overload_*` / `body_intelligence*` / `body_profile.py` / scoring / substitution / recommendation
- `app/routers/body.py` (#17 intact), `app/routers/body_intelligence.py` (#19 intact), `app/routers/sessions.py`, `coach_report.py`
- `app/models/*` / `migrations/*` / `data/schema_snapshot.sql`
- `requirements.txt`, `pyproject.toml`, `.env*`
- `app/static/js/*` (aucun JS ajouté ni modifié)
- `app/static/css/*` (aucune nouvelle CSS — réutilisation strictes des classes `card`, `card__title`, `text-dim`)

## 4. Décisions implémentées (vs spec PR #20)

| Décision spec | Implémentation Sb_Body_02.1 |
|---|---|
| Flag dédié `BODY_CAPTURE_QUALITY_ENABLED=false` | ✅ `app/config.py` |
| Router-level gate (404 avant auth) | ✅ `dependencies=[Depends(require_body_capture_quality_enabled)]` (pattern aligné #17, #19) |
| Route shell `/body/capture-quality` | ✅ `GET` only |
| Placeholder SSR statique | ✅ template sans JS, sans form, sans input |
| Wording « aide à la capture » / état non actif | ✅ 6 marqueurs d'état présents (caméra/image envoyée/image stockée/landmark/diagnostic médical/score corporel — tous en dénégation explicite anti-pseudo-science) |
| CTA désactivé / informatif | ✅ `aria-disabled="true"` + texte "Caméra non disponible dans cette version. Disponible dans un prochain lot." |
| Pas de lien quand flag OFF | ✅ test garde + aucun lien ajouté nulle part |

## 5. Non-goals stricts respectés (verbatim brief)

| Non-goal | Statut |
|---|---|
| Pas de caméra / permission navigateur | ✅ |
| Pas de JavaScript | ✅ test garde `<script>` absent |
| Pas de MediaPipe / modèle / CDN / worker | ✅ test garde |
| Pas de fichier image / upload / stockage | ✅ test garde absence `<form>` + `<input type="file">` |
| Pas de Bodygram / provider externe | ✅ |
| Pas de migration / DB | ✅ |
| Pas de modification `requirements.txt` / `pyproject.toml` / `.env*` | ✅ |
| Pas de déploiement | ✅ |
| Pas de modification session mode | ✅ |
| Pas de modification Sx_30 / overload | ✅ |
| Pas de nouvelle CSS | ✅ réutilisation classes existantes |

## 6. Comportement gate (verbatim brief vs implémentation)

| Cas | Attendu brief | Test | Résultat |
|---|---|---|---|
| Flag OFF + anonyme `GET /body/capture-quality` | 404 avant auth | `test_capq_off_anonymous_returns_404` | ✅ 404 |
| Flag OFF + authentifié `GET /body/capture-quality` | 404 | `test_capq_off_authenticated_returns_404` | ✅ 404 |
| Flag ON + anonyme | 303 `/login` | `test_capq_on_anonymous_redirects_to_login` | ✅ 303 + `/login` in Location |
| Flag ON + authentifié | 200 | `test_capq_on_authenticated_returns_200` | ✅ 200 + "Qualité de capture" rendu |
| Flag OFF + `BODY_ASSESSMENT_ENABLED=true` | 404 (indépendance) | `test_capq_off_with_body_assessment_on_still_404` | ✅ 404 |
| Flag OFF + `BODY_INTELLIGENCE_ENABLED=true` | 404 (indépendance) | `test_capq_off_with_bi_on_still_404` | ✅ 404 |
| Flag ON + `BODY_ASSESSMENT_ENABLED=false` | 200 (autonome) | `test_capq_on_with_body_assessment_off_still_works` | ✅ 200 |
| Flag ON + `BODY_INTELLIGENCE_ENABLED=false` | 200 (autonome) | `test_capq_on_with_bi_off_still_works` | ✅ 200 |
| Flag OFF : aucun lien `capture-quality` sur `/profile` | invisible | `test_capq_off_no_link_on_profile` | ✅ |
| Flag OFF : aucun lien sur `/body/intelligence` (avec BI=ON) | invisible | `test_capq_off_no_link_on_body_intelligence_when_bi_on` | ✅ |

## 7. Privacy / static-only — tests garde

| Garde | Test |
|---|---|
| Aucun `<script>` dans le shell | ✅ `test_shell_has_no_script_tag` |
| Aucune mention MediaPipe (`mediapipe`/`@mediapipe`/`tasks-vision`/`pose_landmarker`) | ✅ `test_shell_has_no_mediapipe_reference` |
| Aucune référence CDN (`jsdelivr`/`unpkg`/`cdn.`/`cdnjs`) | ✅ `test_shell_has_no_cdn_reference` |
| Aucun `enctype="multipart/form-data"` | ✅ `test_shell_has_no_upload_form` |
| Aucun `<input type="file">` | ✅ `test_shell_has_no_file_input` |
| Wording strictement interdit (`body fat`, `morphotype`, `mauvaise posture`, `taux de gras`, `tu es gras/sec`) absent | ✅ `test_shell_wording_is_neutral` |
| `score corporel` / `diagnostic` uniquement en **dénégation explicite** (« aucun … ») — sécurité anti-pseudo-science conforme à l'intent du brief | ✅ même test |
| 6 placeholders requis présents (caméra, image envoyée, image stockée, landmark, diagnostic médical, score corporel) | ✅ `test_shell_contains_expected_placeholder` |

## 8. Non-régression

| Surface | Test | Résultat |
|---|---|---|
| Gate #17 Manual Body Profile (`/body` → 404 quand `BODY_ASSESSMENT_ENABLED=false`) | `test_non_reg_body_assessment_gate_still_404` | ✅ |
| Gate #19 Body Intelligence v2 (`/body/intelligence` → 404 quand `BODY_INTELLIGENCE_ENABLED=false`) | `test_non_reg_body_intelligence_gate_still_404` | ✅ |
| `/progress` 200 | `test_non_reg_progress_still_200` | ✅ |
| `/physique` 200 | `test_non_reg_physique_still_200` | ✅ |
| Suite gates existante (`test_body_profile.py` + `test_body_intelligence_gate.py`) | local | ✅ 23 passed |

## 9. Statut tests

| Suite | Résultat |
|---|---|
| `tests/test_body_capture_quality_gate.py` (Sb_Body_02.1) | ✅ **21 passed** |
| `tests/test_body_profile.py` (gate #17) | ✅ non régressé |
| `tests/test_body_intelligence_gate.py` (gate #19) | ✅ non régressé |
| Ruff budget | ✅ 529 ≤ 548 (inchangé) |
| Spec protocol | ✅ |

## 10. Verdict

**✅ Shell Sb_Body_02.1 livré. PR draft prête, non mergée, non déployée.**

Prochain lot **non lancé** : `Sb Body 02.2` (caméra locale, sans MediaPipe) — restera flag-gaté OFF par défaut. La suite du build queue (`02.3` MediaPipe client-side, `02.4` hardening, `02.R` recette privée) est documentée dans la spec mergée PR #20 et ne sera ouverte qu'au feu vert explicite.

Dogfood Sx_30 prévu ce soir : aucun impact (shell flag OFF par défaut, aucune surface exposée).
