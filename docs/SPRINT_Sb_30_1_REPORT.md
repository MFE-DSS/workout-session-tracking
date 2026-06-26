# Sb_30.1 — Progressive Overload Engine V1 (Sprint Report)

**Branche :** `claude/sprint-reporting-fitness-app-V7Qr6`
**Date :** 2026-06-16
**Spec parent :** `docs/strategy/Sx_30_PROGRESSIVE_OVERLOAD_ENGINE_SPEC.md`
**Lot Sx_30 :** §14 — Sb_30.1 (engine pur, 1/5 du cycle Sx_30)
**Build authorization :** ✅ `BUILD AUTHORIZED FOR Sx_30 — Option B` (override #3, 2026-06-16)
**OQ tranchées :** A par exercice / B par session / C pas de bypass / D N=3 fixe / E placeholder seulement.

---

## 1. Objectif

Livrer le moteur pur `app/services/overload_engine.py` + tests unitaires complets, sans toucher router / template / migration / modèle / DB / autres services.

## 2. Fichiers livrés

| Fichier | Type | Description |
|---|---|---|
| `app/services/overload_engine.py` | **NEW** | Moteur pur (260 lignes). Aucune dépendance sur services métier core. Dataclasses frozen, API `compute_overload_hint(input)`. |
| `tests/test_overload_engine.py` | **NEW** | 33 tests unitaires : 5 états, incréments par catégorie, deload arrondi, déterminisme, max 3 raisons, no-authoritative language, fallback conservateur. |
| `docs/SPRINT_Sb_30_1_REPORT.md` | **NEW** | Ce rapport. |
| `docs/strategy/SPEC_REGISTRY.md` | MODIFIED | Sb_30.1 livré ✅, lien run. |

**0 router touché. 0 template. 0 migration. 0 modèle SQLAlchemy. 0 CSS. 0 JS. 0 service métier core touché.**

`progression_hint.py` legacy intact (suppression prévue Sb_30.4).

## 3. API publique

```python
from app.services.overload_engine import (
    OVERLOAD_ENGINE_VERSION,   # int = 1
    HistoricalSetSignal,        # weight_kg, reps, quality_score, fatigue_signal
    OverloadInput,              # exercise_category, target_min, target_max, history
    OverloadHint,               # state, engine_version, target_weight_kg,
                                # target_reps_min, target_reps_max, reasons
    compute_overload_hint,      # pure function
)
```

Tous les dataclasses sont `frozen=True` (immutables). Le moteur n'effectue aucun I/O, aucun accès DB, aucun appel réseau.

## 4. Règles V1 (récap Sx_30 §9)

| Priorité | État | Trigger |
|---|---|---|
| 1 | `unknown` | Historique vide |
| 2 | `deload` | `mean_quality(last 2) ≤ 0.55` OU `reps[0] < reps[1] < reps[2]` |
| 3 | `progress` | 2 dernières séances `reps ≥ target_max` ET `mean_quality ≥ 0.75` (ou None) ET pas de fatigue |
| 4 | `top-range` | `reps[0] < target_min` |
| 5 | `consolidate` | Sinon |

Incréments :
- `compound` → +2.5 kg
- `isolation_free` → +1.0 kg
- `isolation_machine` → +2.5 kg
- Catégorie inconnue → +1.0 kg (fallback conservateur)
- `deload` → `floor(prior * 0.90, increment)`

## 5. CI réelle (post-push)

**Run GitHub Actions : [28241678098](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/28241678098) — ✅ success (3/3 jobs verts)**

- [x] Job `pytest + QA scripts` — ✅ success
- [x] Job `lint (ruff budget + bandit + actionlint + shellcheck)` — ✅ success
- [x] Job `SonarCloud` — ✅ success

## 6. Métriques

| Item | Valeur |
|---|---|
| Lignes service ajoutées | +260 (`overload_engine.py`) |
| Tests ajoutés | +33 (`test_overload_engine.py`) |
| Routers touchés | 0 |
| Templates touchés | 0 |
| Migrations | 0 |
| Modèles SQLAlchemy | 0 |
| Services métier core touchés | 0 |
| Lignes JS ajoutées | 0 |
| Lignes CSS ajoutées | 0 |
| Dépendances externes ajoutées | 0 |

## 7. Contraintes respectées (verbatim user)

| Contrainte | Statut |
|---|---|
| FastAPI SSR + Jinja2 inchangé | ✅ (aucun changement) |
| Pas de React / SPA / bundler / dep externe | ✅ |
| Pas d'accès réseau / DB dans le moteur V1 | ✅ pure function |
| Pas de router / template / migration / modèle | ✅ |
| Pas de suppression legacy `progression_hint.py` | ✅ intact |
| Pas de changement `recommendation.py` | ✅ |
| Pas de changement `quality_score.py` | ✅ |
| Pas de changement `implicit_signal.py` | ✅ |
| Pas de changement `coach_*` / `body_*` / `substitution.py` | ✅ |
| Ruff budget ≤ 548 | ✅ 534 |
| Dogfood Sx_27 reste PENDING | ✅ |
| Options C/D/E restent bloquées | ✅ |

## 8. OQ Sx_30 implémentées (recap)

| OQ | Implémentation Sb_30.1 |
|---|---|
| OQ-A par exercice uniquement | ✅ `OverloadInput` = 1 exercice ; pas de set-level |
| OQ-B version par session | ✅ `engine_version` exposé sur le hint, prêt pour migration Sb_30.3 |
| OQ-C pas de bypass deload | ✅ aucun champ `override_deload` |
| OQ-D N=3 fixe | ✅ `_is_consecutive_reps_decline` exige len ≥ 3 ; pas d'extension automatique |
| OQ-E placeholder seulement | ⏳ s'appliquera Sb_30.3 / Sb_30.4 (template) |

## 9. DoD locale (vérifiée)

| Gate | Statut |
|---|---|
| `pytest tests/test_overload_engine.py` | ✅ 33 passed |
| `pytest --ignore=tests/test_v1_acceptance.py -q` | ✅ (full suite) |
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

## 10. Coverage tests (résumé)

- ✅ `unknown` si historique vide
- ✅ `progress` si 2 séances ≥ top range + quality OK
- ✅ `progress` bloqué par fatigue → fallback `consolidate`
- ✅ `progress` bloqué par quality < 0.75 → fallback `consolidate`
- ✅ `progress` accepté si quality_score=None (no exigé)
- ✅ `consolidate` si dans la range mais pas top
- ✅ `top-range` si reps < target_min
- ✅ `deload` si quality_score moyen ≤ 0.55
- ✅ `deload` si 2 baisses de reps consécutives (3 séances)
- ✅ `deload` prioritaire sur `progress` si fatigue / quality drop
- ✅ Incrément compound +2.5 kg
- ✅ Incrément isolation_free +1.0 kg
- ✅ Incrément isolation_machine +2.5 kg
- ✅ Incrément fallback inconnu +1.0 kg
- ✅ Deload arrondi vers le bas (compound 2.5, isolation 1.0)
- ✅ Max 3 raisons
- ✅ Aucune raison ne contient "tu dois" / "il faut absolument" / "obligatoire"
- ✅ Raisons dédupliquées
- ✅ Output déterministe pour mêmes inputs
- ✅ `engine_version` = 1
- ✅ Dataclass immutable (frozen)
- ✅ Historique 1 séance ne déclenche pas progress
- ✅ Catégorie inconnue → fallback conservateur

## 11. Verdict

**✅ READY FOR Sb_30.2** (explainer + injection router).

Prochaine étape : `Sb_30.2` ajoutera `overload_explainer.py` (formatage français court) + injection dans `app/routers/sessions.py` pour exposer les hints au template (sans encore modifier `exercise_card.html` — réservé Sb_30.3 / Sb_30.4).
