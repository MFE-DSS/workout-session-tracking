# Sb_29.5 — Template Tests, Mobile Smoke, A11y, Sx_29 Closure (Sprint Report)

**Branche :** `claude/sprint-reporting-fitness-app-V7Qr6`
**Date :** 2026-06-16
**Spec parent :** `docs/strategy/Sx_29_MOBILE_SESSION_FOCUS_MODE_SPEC.md`
**Lot Sx_29 :** §17 — Sb_29.5 (clôture technique, 5/5 du cycle Sx_29)
**Dépendances acceptées :** Sb_29.1 ✅ / Sb_29.2 ✅ / Sb_29.3 ✅ / Sb_29.4 ✅ (CI 27577849433 verte 3/3)

---

## 1. Objectif

Clôturer techniquement Sx_29 :
- Extraire les blocs CSS Sx_29 hors `app.css` (OQ-B : cumul 385 > seuil 200).
- Consolider la couverture tests mobile / accessibilité / no-JS.
- Livrer un dogfood template + audit mobile V1.
- Produire un closure report Sx_29.
- Mettre à jour registry + roadmap.

## 2. Fichiers livrés

| Fichier | Type | Description |
|---|---|---|
| `app/static/css/session_focus.css` | **NEW** | 405 lignes (header de 20 + 385 lignes Sx_29 extraites verbatim depuis `app.css`). |
| `app/templates/base.html` | MODIFIED | +1 ligne (`{% block extra_head %}{% endblock %}`) pour permettre des `<link>` ciblés par page. |
| `app/templates/session_detail.html` | MODIFIED | +5 lignes : `{% block extra_head %}` charge `session_focus.css` APRES `app.css` (cascade préservée). |
| `app/static/css/app.css` | MODIFIED | **-385 lignes** (extraction Sb_29.1 → Sb_29.4). `app.css` revient à sa surface pré-Sx_29 (~3020 lignes). |
| `tests/test_session_focus_layout.py` | MODIFIED | `FOCUS_CSS` ajouté, `_css()` lit app.css + session_focus.css. |
| `tests/test_session_focus_navigation.py` | MODIFIED | Idem. |
| `tests/test_session_focus_sticky_cta.py` | MODIFIED | Idem. |
| `tests/test_session_focus_rest_timer.py` | MODIFIED | Idem. |
| `tests/test_session_focus_mobile_smoke.py` | **NEW** | 9 tests : extraction garde, link ordering, surface Sx_29, no overflow-x, flex-wrap. |
| `tests/test_session_focus_accessibility.py` | **NEW** | 8 tests : tap-target 44×44, aria-current step, aria-live polite, button types, non-color cues. |
| `docs/dogfood/DOGFOOD_Sx_29_FOCUS_MODE_TEMPLATE.md` | **NEW** | Template dogfood device réel (Sb_29.1 → 5, no-JS optional). |
| `docs/SESSION_FOCUS_MOBILE_AUDIT_2026-06-16.md` | **NEW** | Audit manuel V1 (statique, pas de Lighthouse — OQ-D). |
| `docs/strategy/Sx_29_CLOSURE_REPORT.md` | **NEW** | Bilan technique Sx_29. |
| `docs/SPRINT_Sb_29_5_REPORT.md` | **NEW** | Ce rapport. |
| `docs/strategy/SPEC_REGISTRY.md` | MODIFIED | Sb_29.5 livré ; Sx_29 marqué technically closed. |
| `docs/strategy/ROADMAP_AND_NEXT_STEPS.md` | MODIFIED | Sx_29 closed ; prochaine action recommandée = dogfood. |

**0 service métier touché. 0 nouvelle route. 0 migration. 0 modèle. 0 dépendance JS externe. Aucun nouveau fichier JS.**

## 3. Extraction CSS (OQ-B)

**Avant Sb_29.5 :** `app.css` = 3404 lignes, dont 385 lignes Sx_29 (3021→3404).
**Après Sb_29.5 :** `app.css` = 3020 lignes (résidu Sx_29 = 0). `session_focus.css` = 405 lignes (header 21 + corps 384).

**Ordre de chargement préservé :**
- `<head>` : `app.css` → `session_focus.css` (cascade override sur classes legacy `.ex-jump`, `.exercise-card`, `.card`).
- Test `test_session_focus_css_link_in_rendered_page` : `body.index("css/app.css") < body.index("css/session_focus.css")`.

**Mécanisme :** `base.html` expose `{% block extra_head %}{% endblock %}`. Seul `session_detail.html` l'override pour ajouter le `<link>`. Aucun poids ajouté sur les autres pages.

## 4. Tests Sb_29.5

### Nouveaux tests : `test_session_focus_mobile_smoke.py` (9 cas)
- `test_session_focus_css_exists_and_nonempty` — fichier présent, > 1000 chars, contient les 4 marqueurs Sb_29.1 → Sb_29.4.
- `test_app_css_no_longer_contains_sx29_blocks` — résidu = 0 dans `app.css`.
- `test_session_detail_loads_session_focus_css` — template référence le fichier.
- `test_session_focus_css_link_in_rendered_page` — ordre de chargement validé en HTML rendu.
- `test_all_sx29_surfaces_rendered` — sticky header + jump + active card + sticky CTA + rest timer + session_focus.js tous présents.
- `test_route_still_200_completed_session` — session terminée ne casse pas (suit redirect vers `/done`).
- `test_rest_timer_uses_flex_wrap` — anti scroll horizontal.
- `test_no_overflow_x_scroll_introduced_in_session_focus_css` — anti dette mobile.

### Nouveaux tests : `test_session_focus_accessibility.py` (8 cas)
- `test_tap_target_min_height_44` + `test_tap_target_min_width_44`.
- `test_session_focus_tap_target_class_applied` — appliqué en HTML rendu.
- `test_aria_current_step_on_active_jump_item` (WCAG 4.1.2 + 2.4.8).
- `test_rest_timer_has_aria_live_polite`.
- `test_skip_rest_is_type_button` + `test_primary_cta_is_type_submit` (no-JS contract).
- `test_non_color_cues_for_card_states` + `test_active_state_has_non_color_cue` (WCAG 1.4.1).

### Tests historiques mis à jour
4 fichiers tests `test_session_focus_*.py` ajoutent une constante `FOCUS_CSS` et lisent `app.css + session_focus.css` concaténés. Aucun test régressé.

## 5. CI réelle (post-push)

À renseigner après push.

- [ ] Job `pytest + QA scripts` — vert attendu
- [ ] Job `lint (ruff budget + bandit + actionlint + shellcheck)` — vert attendu
- [ ] Job `SonarCloud` — vert attendu

## 6. Métriques

| Item | Valeur |
|---|---|
| Lignes CSS déplacées vers `session_focus.css` | 384 |
| Lignes header `session_focus.css` | 21 |
| `app.css` avant | 3404 |
| `app.css` après | 3020 |
| `session_focus.css` après | 405 |
| Tests ajoutés (Sb_29.5) | +17 (9 smoke + 8 a11y) |
| Tests modifiés (FOCUS_CSS) | 4 fichiers, 0 régression |
| Nouvelles routes | 0 |
| Migrations | 0 |
| Modèles SQLAlchemy | 0 |
| Services métier core touchés | 0 |
| Nouveaux fichiers JS | 0 |
| Dépendances JS externes | 0 |

## 7. Contraintes respectées (verbatim user)

| Contrainte | Statut |
|---|---|
| Pas de React / SPA / bundler / dep externe | ✅ |
| JS autorisé : `session_focus.js` UNIQUEMENT (déjà existant) | ✅ |
| Pas de nouveau JS hors `session_focus.js` | ✅ test garde |
| FastAPI SSR + Jinja2 conservé | ✅ |
| No-JS fallback obligatoire | ✅ |
| Pas de service métier core touché | ✅ |
| Aucune modif `scoring/`, `recommendation.py`, `reco/`, `implicit_signal.py`, `quality_score.py`, `coach_report.py`, `body_tracking.py`, `substitution.py` | ✅ |
| Pas de migration / modèle / route / persistance / SW / PWA / body tracking | ✅ |
| Mobile 360×640 + media queries | ✅ |
| Ruff budget ≤ 548 | ✅ 534 |
| Dogfood Sx_27 reste PENDING | ✅ non simulé |
| Options B/C/D/E restent bloquées | ✅ |

## 8. OQ Sx_29 respectées

| OQ | Sb_29.5 |
|---|---|
| OQ-A : pas de modal/dialog inline | ✅ |
| OQ-B : extraction `session_focus.css` réalisée (cumul > 200 atteint) | ✅ |
| OQ-C : timer signal = `data-start-rest="<seconds>"` | ✅ inchangé |
| OQ-D : pas de Lighthouse CI ; audit manuel V1 livré | ✅ `SESSION_FOCUS_MOBILE_AUDIT_2026-06-16.md` |
| OQ-E : pas de micro-interactions polish | ✅ différé `Sb_29.next.polish-1` |

## 9. Périmètre interdit (verbatim user)

| Non-goal | Respect |
|---|---|
| Pas de nouvelle feature produit | ✅ |
| Pas de changement UX majeur | ✅ |
| Pas de route substitution | ✅ |
| Pas de modal/dialog | ✅ |
| Pas de notification / push | ✅ |
| Pas de PWA / service worker | ✅ |
| Pas de tracking | ✅ |
| Pas de persistance timer | ✅ |
| Pas de React lab | ✅ |
| Pas de micro-interactions polish | ✅ |
| Pas de toast / auto-focus / animation collapse | ✅ |
| Pas de Sx_30 | ✅ non ouvert |
| Pas de modification scoring/recommendation/body/substitution | ✅ |

## 10. DoD locale (vérifiée)

| Gate | Statut |
|---|---|
| `pytest --ignore=tests/test_v1_acceptance.py -q` | ✅ ~1178 passed |
| `python scripts/check_ruff_budget.py` | ✅ 534 ≤ 548 |
| `python scripts/check_spec_protocol.py` | ✅ |
| `python scripts/check_auth_scope_matrix.py` | ✅ |
| `PYTHONPATH=. python scripts/check_alembic_drift.py` | ✅ no diff |
| `python scripts/check_schema_snapshot.py` | ✅ |
| `python scripts/check_migration_patterns.py` | ✅ |
| `python scripts/check_migration_roundtrip.py` | ✅ |
| `python scripts/catalog_qa.py` | ✅ |
| `python scripts/machine_atlas_qa.py` | ✅ PASS |
| `pip-audit -r requirements.txt --strict` | ✅ clean |

## 11. Verdict

**✅ Sx_29 TECHNICALLY CLOSED**

- Toute la surface technique Sx_29 est livrée et testée.
- `session_focus.css` extrait sans régression cascade (cf. test ordering).
- Mobile/a11y/no-JS contracts assertés par tests structurels.
- Dogfood Sx_29 device réel reste **PENDING** — cf. template.
- Sx_30 ne s'ouvre PAS automatiquement (override utilisateur ou dogfood validé requis).
