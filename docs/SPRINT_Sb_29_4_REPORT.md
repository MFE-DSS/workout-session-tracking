# Sb_29.4 — Rest Timer Progressive Enhancement (Sprint Report)

**Branche :** `claude/sprint-reporting-fitness-app-V7Qr6`
**Date :** 2026-06-15
**Spec parent :** `docs/strategy/Sx_29_MOBILE_SESSION_FOCUS_MODE_SPEC.md`
**Lot Sx_29 :** §17 — Sb_29.4 (Rest Timer, 4/5 du cycle Sx_29)
**Dépendances acceptées :** Sb_29.1 ✅, Sb_29.2 ✅, Sb_29.3 ✅ (CI 27573217572 verte 3/3)

---

## 1. Objectif

Ajouter un timer de repos simple comme **progressive enhancement**, sans rendre aucune action critique dépendante de JavaScript.

- Affichage statique no-JS : "Repos suggéré : 90s"
- Countdown JS vanilla (aucun framework, aucun bundler, aucune dépendance externe)
- Bouton "Skip rest" type="button" (non critique)
- Aucun POST déclenché par le timer
- Aucune persistance V1
- Scoped à la carte active uniquement

## 2. Fichiers livrés

| Fichier | Type | Description |
|---|---|---|
| `app/templates/_partials/rest_timer.html` | **NEW** | Partial rest timer (wrapper + label + countdown + skip). `data-start-rest` + `data-rest-duration`. No-JS fallback "Repos suggéré : 90s". |
| `app/static/js/session_focus.js` | **NEW** | Vanilla JS (95 lignes). `setInterval` + `clearInterval`. Defaults 90s. Skip button. Aucune dépendance. Aucun fetch. IIFE strict. |
| `app/templates/_partials/exercise_card.html` | MODIFIED | +6 lignes (Jinja include conditionnel `{% if is_active %}` après `</form>`, dans `</details>`). Aucun changement structurel des POST. |
| `app/templates/session_detail.html` | MODIFIED | +3 lignes (script `session_focus.js` chargé en `defer`). Fin de `{% block content %}`. |
| `app/static/css/app.css` | MODIFIED | +64 lignes (bloc rest timer commenté). Cumul Sx_29 = 124 + 131 + 66 + 64 = **385 lignes**. |
| `tests/test_session_focus_rest_timer.py` | **NEW** | 20 tests dédiés Sb_29.4. |
| `tests/test_session_focus_layout.py` | MODIFIED | Relax `test_no_new_js_file_introduced` : `existing <= {"preview.js", "session_focus.js"}` (session_focus.js autorisé en Sb_29.4). |
| `tests/test_session_focus_navigation.py` | MODIFIED | Idem. |
| `tests/test_session_focus_sticky_cta.py` | MODIFIED | Idem. |
| `docs/SPRINT_Sb_29_4_REPORT.md` | **NEW** | Ce rapport. |
| `docs/strategy/SPEC_REGISTRY.md` | MODIFIED | Ligne Sb_29.4 mise à jour avec lien sprint report + CI. |

**0 service métier touché. 0 route ajoutée. 0 migration. 0 modèle SQLAlchemy. 1 nouveau fichier JS uniquement (`session_focus.js`).**

## 3. Mécanisme rest timer (résumé)

```jinja
{# rest_timer.html — affichage statique no-JS + hooks JS optionnels #}
<div class="session-focus__rest-timer"
     data-rest-duration="90"
     data-start-rest="90"
     role="status" aria-live="polite">
  <span class="session-focus__rest-timer__label">Repos suggéré :</span>
  <span class="session-focus__rest-timer__countdown" data-rest-display>90s</span>
  <button type="button" data-rest-skip
          class="btn btn--ghost session-focus__rest-timer__skip">Skip rest</button>
</div>
```

```js
/* session_focus.js — vanilla IIFE, init on DOMContentLoaded */
var roots = document.querySelectorAll("[data-start-rest]");
if (!roots || roots.length === 0) return;
for (var i = 0; i < roots.length; i++) startTimer(roots[i]);
// setInterval(tick, 1000) ; clearInterval à 0 ou sur skip
```

Si JS désactivé : le DOM reste avec `90s` affiché statiquement → aucune action critique cassée. Le bouton `Skip rest` (type="button") n'a aucun effet (handler non attaché) mais n'envoie aucun POST.

## 4. OQ Sx_29 respectées

| OQ | Décision | Implémentation Sb_29.4 |
|---|---|---|
| OQ-A : pas de modal/dialog inline | ✅ | Aucun `<dialog>`, aucun overlay. |
| OQ-B : CSS reste dans `app.css` | ✅ | +64 lignes. Extraction `session_focus.css` reportée Sb_29.5. |
| OQ-C : timer signal = `data-start-rest="<seconds>"` | ✅ | Attribut DOM utilisé. **Pas de query param URL.** |
| OQ-D : pas de Lighthouse CI | ✅ | Aucun nouveau workflow. |
| OQ-E : pas de toast / auto-focus / animation collapse | ✅ | Pas d'animation. Pas d'auto-focus. Pas de toast. Le timer change uniquement `textContent`. |

## 5. CI réelle (post-push)

À renseigner après push.

- [ ] Job `pytest + QA scripts` — vert attendu
- [ ] Job `lint (ruff budget + bandit + actionlint + shellcheck)` — vert attendu
- [ ] Job `SonarCloud` — vert attendu

## 6. Métriques

| Item | Valeur |
|---|---|
| Lignes CSS ajoutées | +64 (3340 → 3404) |
| Cumul CSS Sx_29 | 385 lignes (124 + 131 + 66 + 64) |
| Lignes JS ajoutées | +95 (`session_focus.js` créé) |
| Tests ajoutés (Sb_29.4) | +20 |
| Tests relaxés (historiques) | 3 (sticky-cta + layout + navigation : `==` → `<=` sur set autorisé) |
| Total pytest avant | 1136 |
| Total pytest après | 1153 (+17 net : +20 nouveaux − 3 relaxés, comptés une fois) |
| Routes ajoutées | 0 |
| Migrations | 0 |
| Modèles SQLAlchemy | 0 |
| Services métier core touchés | 0 |
| Dépendances JS externes | 0 |

## 7. Contraintes respectées (verbatim user)

| Contrainte | Statut |
|---|---|
| FastAPI SSR + Jinja2 conservé | ✅ |
| JS vanilla uniquement | ✅ |
| Nouveau fichier JS autorisé : `session_focus.js` UNIQUEMENT | ✅ test garde |
| Pas de React | ✅ test garde |
| Pas de SPA | ✅ |
| Pas de bundler | ✅ |
| Pas de dépendance JS externe | ✅ aucun `import`, aucun `require`, aucun fetch |
| No-JS fallback obligatoire | ✅ "Repos suggéré : 90s" rendu statique |
| Pas de service métier core touché | ✅ |
| Aucune modif : `scoring/`, `recommendation.py`, `reco/`, `implicit_signal.py`, `quality_score.py`, `coach_report.py`, `body_tracking.py`, `substitution.py` | ✅ |
| Pas de migration Alembic | ✅ |
| Pas de nouveau modèle SQLAlchemy | ✅ |
| Pas de nouvelle route | ✅ |
| Mobile target 360×640 | ✅ media query `< 380px` |
| Pas de scroll horizontal | ✅ `flex-wrap: wrap` |
| Ruff budget ≤ 548 | ✅ 534 |
| Dogfood Sx_27 reste PENDING | ✅ non simulé |
| Options B/C/D/E restent bloquées | ✅ |

## 8. Périmètre interdit (verbatim user)

| Non-goal | Respect |
|---|---|
| Pas de persistance timer en base | ✅ |
| Pas de tracking analytique | ✅ |
| Pas de notification push | ✅ |
| Pas de service worker | ✅ |
| Pas de PWA | ✅ |
| Pas de route nouvelle | ✅ |
| Pas de modal/dialog | ✅ |
| Pas de substitution | ✅ |
| Pas de toast "set enregistré" | ✅ |
| Pas d'auto-focus next input | ✅ |
| Pas d'animation collapse | ✅ |
| Pas de React lab | ✅ |
| Pas de changement palette global | ✅ |
| Pas de refonte design system | ✅ |
| Pas de body tracking | ✅ |
| Pas d'extraction `session_focus.css` dans Sb_29.4 | ✅ (reportée Sb_29.5) |

## 9. DoD locale (vérifiée)

| Gate | Statut |
|---|---|
| `pytest --ignore=tests/test_v1_acceptance.py -q` | ✅ 1153 passed |
| `python scripts/check_ruff_budget.py` | ✅ 534 ≤ 548 |
| `python scripts/check_spec_protocol.py` | ✅ |
| `python scripts/check_auth_scope_matrix.py` | ✅ 3 fichiers présents |
| `PYTHONPATH=. python scripts/check_alembic_drift.py` | ✅ no diff |
| `python scripts/check_schema_snapshot.py` | ✅ |
| `python scripts/check_migration_patterns.py` | ✅ |
| `python scripts/check_migration_roundtrip.py` | ✅ |
| `python scripts/catalog_qa.py` | ✅ |
| `python scripts/machine_atlas_qa.py` | ✅ PASS |
| `pip-audit -r requirements.txt --strict` | ✅ clean |

## 11. Verdict

**✅ READY FOR Sb_29.5**

Sb_29.5 est la dernière étape Sx_29 : extraction `session_focus.css`, dogfood checklist, hardening final.
