# Sb_30.3 — Overload Hint UI First Render (Build Report)

**Branche :** `claude/sprint-reporting-fitness-app-V7Qr6`
**Date :** 2026-06-26
**Spec parent :** `docs/strategy/Sx_30_PROGRESSIVE_OVERLOAD_ENGINE_SPEC.md`
**Lot Sx_30 :** §14 — Sb_30.3 (UI first render + migration, 3/5 du cycle)
**Build authorization :** ✅ `BUILD AUTHORIZED FOR Sx_30 — Option B`
**Pré-requis :** Sb_30.1 ✅ (CI 28241678098) + Sb_30.2 ✅ (CI 28245446788).

---

## 1. Résumé exécutif

Sb_30.3 rend visible pour la première fois l'overload hint dans l'UI session, **uniquement sur la carte active**, **uniquement quand `is_silent` est False**. Trois livrables clés :

1. **Migration Alembic** `6h9e4c0d1f32` qui ajoute `workout_sessions.overload_engine_version INT NOT NULL DEFAULT 1` (Sx_30 OQ-B).
2. **Partial `_partials/overload_hint.html`** — rendu compact (intent + cible + reasons dépliables via `<details>` natif). No-JS friendly.
3. **CSS dédié dans `session_focus.css`** — 5 états avec non-color cues (border-left + icône unicode `↑ → 🏁 ↓ ?`), mobile-first.

`exercise_card.html` est branché en pure inclusion conditionnelle (`{% if is_active %}` + `{% if hint %}`), sans toucher au reste de la carte. Aucun changement sur l'engine, l'explainer, les inputs, ou `progression_hint.py` legacy.

## 2. Fichiers modifiés / créés

| Fichier | Type | Description |
|---|---|---|
| `migrations/versions/20260616_add_overload_engine_version.py` | **NEW** | Migration additive idempotente, downgrade safe. Pattern aligné Sb_24.1. |
| `app/models/session.py` | MODIFIED | +5 lignes : champ `overload_engine_version: Mapped[int]` avec `server_default="1"` et `default=1` côté Python. |
| `data/schema_snapshot.sql` | REGEN | `generate_schema_snapshot.py` régénéré, drift check OK. |
| `app/templates/_partials/overload_hint.html` | **NEW** | 41 lignes. Render conditionnel défensif. `<details>` natif pour reasons. `data-engine-version` + `data-overload-state` exposés. |
| `app/static/css/session_focus.css` | MODIFIED | +132 lignes (5 états + responsive < 380px + reset details marker). Cumul Sx_29+Sx_30 inclus. |
| `app/templates/_partials/exercise_card.html` | MODIFIED | +9 lignes : bloc Sb_30.3 conditionnel actif-card uniquement (`{% if is_active %}` + `{% if hint %}` + `include`). |
| `tests/test_overload_hint_render.py` | **NEW** | 14 tests : render visible (progress/deload), absence (unknown/history empty), active-card-only (1 occurrence exacte), wording non autoritaire, flow Sx_29 intact, CSS 5 états + icônes, partial structure, owner isolation. |
| `tests/test_overload_engine_version_migration.py` | **NEW** | 5 tests : colonne présente, default=1 via ORM, default=1 via raw SQL, constante Python = DB, revision id correct. |
| `docs/SPRINT_Sb_30_3_overload_hint_ui_first_render_BUILD_REPORT.md` | **NEW** | Ce rapport. |
| `docs/strategy/SPEC_REGISTRY.md` | MODIFIED | Sb_30.3 livré ✅. |

**0 changement** sur `overload_engine.py`, `overload_inputs.py`, `overload_explainer.py`, `progression_hint.py`, `quality_score.py`, `implicit_signal.py`, `recommendation.py`, `coach_*.py`, `body_*.py`, `substitution.py`.

## 3. Diff métier

### 3.1 Migration

```python
revision = "6h9e4c0d1f32"
down_revision = "5g8d3b9c0e21"

def upgrade():
    if not _column_exists("workout_sessions", "overload_engine_version"):
        op.add_column(
            "workout_sessions",
            sa.Column(
                "overload_engine_version", sa.Integer(),
                nullable=False, server_default="1",
            ),
        )

def downgrade():
    if _column_exists("workout_sessions", "overload_engine_version"):
        op.drop_column("workout_sessions", "overload_engine_version")
```

- Additive only, idempotent, downgrade safe.
- Toutes les rows pré-existantes héritent `1` via `server_default` — cohérent avec `OVERLOAD_ENGINE_VERSION = 1`.
- Schema snapshot régénéré → drift check OK.

### 3.2 Partial `overload_hint.html`

```jinja
{% if hint and not hint.is_silent %}
<div class="overload-hint overload-hint--{{ hint.state }}"
     data-overload-state="{{ hint.state }}"
     data-engine-version="{{ hint.engine_version }}"
     role="status">
  <div class="overload-hint__head">
    <span class="overload-hint__intent">{{ hint.intent_label }}</span>
    {% if hint.target_summary %}
    <span class="overload-hint__target">{{ hint.target_summary }}</span>
    {% endif %}
  </div>
  {% if hint.reasons %}
  <details class="overload-hint__why">
    <summary>Pourquoi&nbsp;?</summary>
    <ul>{% for r in hint.reasons %}<li>{{ r }}</li>{% endfor %}</ul>
  </details>
  {% endif %}
</div>
{% endif %}
```

- Garde défensive `if hint and not hint.is_silent` (le router skip déjà côté Python).
- `data-engine-version` propagé jusqu'au DOM → traçabilité future analytics / DevTools / debug.
- `<details>` natif → no-JS friendly, conforme contrat Sx_29.
- `role="status"` pour lecteurs d'écran.

### 3.3 Wire dans `exercise_card.html`

```jinja
{% if is_active %}
  {% set hint = overload_hints.get(se.id) %}
  {% if hint %}
    {% include "_partials/overload_hint.html" %}
  {% endif %}
{% endif %}
```

- Inclusion strictement dans `{% if is_active %}` → jamais rendu sur les cards pending/done/skipped/substituted.
- `overload_hints.get(se.id)` retourne `None` si le router a skip (silent / unknown) → `if hint` empêche tout rendu vide.
- Pas de duplication avec `progression_hint` legacy (qui produit un message qualitatif court, affiché plus haut dans la carte). L'overload propose en plus une **cible chiffrée** (kg/reps).

### 3.4 CSS (`session_focus.css`)

- Wrapper `.overload-hint` : `border-left: 3px solid var(--fg-dim)` par défaut.
- Modifiers `--progress` / `--consolidate` / `--top-range` / `--deload` / `--unknown` : couleur `border-left` (var --ok / --accent / --warn / --fg-dim) + icône unicode dans `intent::before`.
- `<details>` summary stylé avec chevron `▸` / `▾` (CSS pur, pas de JS).
- Media query `< 380px` pour padding / font-size mobile.

## 4. OQ Sx_30 — état au sortir de Sb_30.3

| OQ | Statut |
|---|---|
| OQ-A par exercice uniquement | ✅ `overload_hints` indexé par `se.id` |
| OQ-B version par session | ✅ colonne DB livrée + propagée dans le DOM |
| OQ-C pas de bypass deload | ✅ aucun UI bypass |
| OQ-D N=3 fixe | ✅ inchangé depuis Sb_30.2 |
| OQ-E placeholder seulement | ⏳ Sb_30.4 (le hint ne touche pas encore les inputs poids/reps) |

## 5. Statut tests

| Suite | Résultat |
|---|---|
| `test_overload_engine.py` (Sb_30.1) | ✅ 33 |
| `test_overload_explainer.py` (Sb_30.2) | ✅ 16 |
| `test_overload_router_injection.py` (Sb_30.2) | ✅ 26 |
| `test_overload_hint_render.py` (Sb_30.3) | ✅ 14 |
| `test_overload_engine_version_migration.py` (Sb_30.3) | ✅ 5 |
| **Sous-suite Sb_30.3** | ✅ 19 nouveaux, 0 régression |
| Suite complète | ✅ à confirmer en CI (background run en cours) |

### Tests garde-fous explicites (mappés sur la demande)

| Garde-fou demandé | Test |
|---|---|
| rendu visible quand hint présent | `test_hint_rendered_on_active_card_when_progress` + `..._when_deload` |
| absence quand silent/unknown | `test_no_render_when_history_empty` (= unknown → silent → skip router) |
| présence uniquement sur la carte active | `test_hint_only_on_active_card_not_others` (`occurrences == 1`) |
| wording non autoritaire | `test_rendered_hint_has_no_authoritative_wording` (scan du bloc rendu) |
| absence de régression du flow session | `test_session_flow_intact_with_hint` (sticky-cta / rest-timer / sticky-jump présents) |
| migration OK | suite complète `test_overload_engine_version_migration.py` (5 tests) |
| engine_version transporté proprement | `data-engine-version="1"` asserté dans `test_hint_rendered_on_active_card_when_progress` |

## 6. Statut DoD locale

| Gate | Statut |
|---|---|
| `pytest --ignore=tests/test_v1_acceptance.py -q` | ✅ background run (résultat sera stamped) |
| `check_ruff_budget.py` | ✅ 535 ≤ 548 |
| `check_spec_protocol.py` | ✅ |
| `PYTHONPATH=. check_alembic_drift.py` | ✅ no diff |
| `check_schema_snapshot.py` | ✅ après `generate_schema_snapshot.py` |
| `check_migration_patterns.py` | ✅ |
| `check_migration_roundtrip.py` | ✅ |
| `check_auth_scope_matrix.py` | ✅ |
| `catalog_qa.py` | ✅ |
| `machine_atlas_qa.py` | ✅ |

## 7. Contraintes respectées (verbatim user)

| Contrainte | OK |
|---|---|
| hint seulement si `is_silent=False` | ✅ partial garde + router skip |
| ton sobre, jamais autoritaire | ✅ test scan du bloc rendu |
| pas de rendu pour `unknown` | ✅ unknown → is_silent → router skip |
| rendu compact, mobile-first | ✅ media query `< 380px` |
| carte active uniquement | ✅ test `occurrences == 1` |
| pas de mur de texte | ✅ reasons dépliables via `<details>` |
| pas de contradiction avec “Dernière fois” / “Delta” | ✅ overload propose une cible **complémentaire** (kg/reps) |
| pas de duplication avec progression_hint legacy | ✅ message qualitatif legacy reste affiché ; overload ajoute cible chiffrée |
| 0 changement engine / inputs / explainer / scoring / progression_hint legacy | ✅ |

## 8. CI réelle (post-push)

**Run GitHub Actions : [28247518562](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/28247518562) — ✅ success (3/3 jobs verts)**

- [x] Job `pytest + QA scripts` — ✅ success
- [x] Job `lint (ruff budget + bandit + actionlint + shellcheck)` — ✅ success
- [x] Job `SonarCloud` — ✅ success

## 11. Verdict

**✅ Sb_30.4 prêt.**

Prochaine étape : Sb_30.4 supprimera `progression_hint.py` legacy + son injection dans le router + ses tests dédiés, et fera potentiellement basculer le placeholder de l'input poids/reps sur la cible overload (OQ-E). Aucune régression bloquante anticipée.
