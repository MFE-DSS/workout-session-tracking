# Sb_31.1 — Body Intelligence v2 Composer (Build Report)

**Branche :** `claude/sprint-reporting-fitness-app-V7Qr6`
**Date :** 2026-06-27
**Spec parent :** `docs/strategy/SPIGNOS_BODY_INTELLIGENCE_V2_SPEC.md`
**Lot Sx_31 :** §N.2 — Sb_31.1 (composeur pur, 1/5 du cycle)
**Build authorization :** ✅ `BUILD AUTHORIZED FOR Sx_31` (override #4, 2026-06-27)

---

## 1. Objectif

Livrer le composeur pur `body_intelligence.py` + suite de tests unitaires complète, sans toucher router / template / CSS / JS / migration / modèle / autres services. Première brique du cycle Sx_31 Body Intelligence v2.

## 2. Fichiers créés / modifiés

| Fichier | Type | Description |
|---|---|---|
| `app/services/body_intelligence.py` | **NEW** | 415 lignes. Composeur pur, dataclasses frozen, arbre de priorité déterministe, seuils figés en constantes nommées. Aucun import DB / FastAPI / Jinja / réseau / I/O. |
| `tests/test_body_intelligence.py` | **NEW** | 38 tests : structure + status + blocs + BMI + priorités + seuils + déterminisme + vocabulaire + overload-not-V1 + ratios + sérialisable. |
| `docs/SPRINT_Sb_31_1_body_intelligence_composer_BUILD_REPORT.md` | **NEW** | Ce rapport. |
| `docs/strategy/SPEC_REGISTRY.md` | MODIFIED | Sb_31.1 livré ✅ (entrée ajoutée). |

**Non touché (vérification explicite)** :
- `app/services/profile_metrics.py` / `muscle_scoring.py` / `muscle_mapping.py`
- `app/services/quality_score.py` / `implicit_signal.py` / `confidence.py`
- `app/services/coach_report.py` / `coach_inference.py`
- `app/services/radar.py`
- `app/services/overload_engine.py` / `overload_inputs.py` / `overload_explainer.py`
- `app/services/recommendation.py` / `substitution.py` / `body_tracking.py`
- `app/routers/*` / `app/templates/*` / `app/static/*`
- `app/models/*` / `migrations/*`
- Aucune nouvelle dépendance externe.

## 3. API finale du composeur

```python
from app.services.body_intelligence import (
    BODY_INTELLIGENCE_VERSION,         # int = 1
    # Inputs
    BodyIntelligenceInput,             # frozen dataclass, tous champs optionnels
    # Outputs
    BodyIntelligenceBlock,             # frozen
    BodyIntelligencePriority,          # frozen
    BodyIntelligenceSnapshot,          # frozen
    # Constantes seuils (testables)
    MIN_SESSIONS_OK,                   # 3
    MIN_SESSIONS_CONSISTENCY_30D,      # 8
    LOW_QUALITY_THRESHOLD,             # 50.0
    LOW_CONFIDENCE_THRESHOLD,          # 50.0
    IMBALANCE_LOW_RATIO,               # 0.5
    IMBALANCE_HIGH_RATIO,              # 2.0
    UNDERTRAINED_OTHER_ZONE_MIN,       # 3
    MIN_QUALITY_SAMPLE,                # 3
    MAX_PRIORITIES,                    # 3
    RADAR_AXIS_ORDER,                  # tuple alignée muscle_mapping
    DEFAULT_LIMITS,                    # tuple[str, ...]
    # Pure entry point
    compute_body_intelligence,         # input -> Snapshot
)
```

## 4. Diff métier

### 4.1 Inputs (BodyIntelligenceInput, frozen)

22 champs, tous optionnels au type-level. Catégories :
- **Fréquence** : `sessions_7d/30d/90d`
- **Volume** : `work_sets_per_week_30d`, `cardio_minutes_per_week_30d`, `strength_volume_delta_pct_30d`
- **Zones** : `zone_session_counts_30d` (dict clé→count), `dominant_pattern_30d`, `pattern_distribution_30d`
- **Qualité** : `quality_score_avg_30d`, `quality_score_n`, `confidence_score_avg`
- **Implicit** : `implicit_labels_30d`
- **Body metrics** : `body_height_cm`, `body_weight_kg`, `body_weight_measured_at_iso`, `waist_cm`, `weight_trend_90d_kg`

Le composeur **ne va jamais chercher** ces données : elles seront construites par une couche I/O (cf. §11) qui sera livrée en Sb_31.2. Sb_31.1 reste 100% pur.

### 4.2 Output (BodyIntelligenceSnapshot, frozen)

- `engine_version` : int
- `status` : `"ok"` / `"partial_data"` / `"insufficient_data"`
- `headline` : str sobre, dépend du status
- `bullets` : tuple ≤ 4
- `blocks` : tuple de 7 `BodyIntelligenceBlock` (toujours 7, certains `available=False`)
- `priorities` : tuple 1–3 `BodyIntelligencePriority`
- `limits` : tuple = `DEFAULT_LIMITS` (always-on disclaimer)

### 4.3 7 blocs émis (toujours)

| Bloc | Classification | Disponibilité |
|---|---|---|
| `training_consistency` | `derived` | si `sessions_*` > 0 |
| `body_metrics` | `measured` (BMI = `derived` dans `content.bmi_classification`) | si l'un des champs body présent |
| `muscle_zone_balance` | `derived` | si `zone_session_counts_30d` non vide |
| `push_pull_legs_balance` | `derived` | si pull > 0 ou lower > 0 |
| `quality_and_confidence` | `derived` | si quality OU confidence présents (avec quality_score_n ≥ 3) |
| `implicit_signal_summary` | `inferred` | si `implicit_labels_30d` non vide |
| `unavailable_or_limits` | `not_deductible` | **toujours** `available=True` |

### 4.4 Arbre de priorité (déterministe, ordre figé)

```
1. insufficient_data       → sessions_30d < 3                 → STOP (1 seule priorité)
2. low_logging_confidence  → quality < 50 OU confidence < 50
3. consistency_gap         → sessions_30d < 8
4. imbalance_gap           → push/pull ou upper/lower ∉ [0.5, 2.0]
5. undertrained_zone       → ≥ 1 zone à 0 ET ≥ 1 autre à ≥ 3
6. stable_or_progressing   → fallback unique si rien sinon
```

Cap dur à `MAX_PRIORITIES = 3`.

### 4.5 Seuils V1 (constantes nommées, tous testés)

```python
MIN_SESSIONS_OK = 3
MIN_SESSIONS_CONSISTENCY_30D = 8           # ≈ 2/semaine × 4 semaines
LOW_QUALITY_THRESHOLD = 50.0               # /100
LOW_CONFIDENCE_THRESHOLD = 50.0            # /100
IMBALANCE_LOW_RATIO = 0.5
IMBALANCE_HIGH_RATIO = 2.0
UNDERTRAINED_OTHER_ZONE_MIN = 3
MIN_QUALITY_SAMPLE = 3                     # n minimal pour exposer la moyenne
MAX_PRIORITIES = 3
```

Aucune personnalisation V1. Faciles à ajuster (constantes en haut du module).

### 4.6 Exemples de sortie

**Cas A — input vide** (`BodyIntelligenceInput()`) :
```python
status="insufficient_data"
headline="Données insuffisantes pour une lecture stable."
bullets=("0 séance(s) sur 30 jours.", "Logue quelques séances pour activer la lecture complète.")
priorities=(BodyIntelligencePriority(key="insufficient_data", severity="info", ...),)
blocks=7 blocs avec available=False pour la plupart, sauf unavailable_or_limits
```

**Cas B — solid input** (12 séances/30j, qualité OK, équilibre OK) :
```python
status="ok"
headline="Lecture corporelle issue de l'entraînement (30 derniers jours)."
bullets=("12 séances loggées sur 30 jours.", "Volume strength +5% vs 30 jours précédents.")
priorities=(BodyIntelligencePriority(key="stable_or_progressing", severity="info", ...),)
blocks=7 blocs tous available=True
limits=DEFAULT_LIMITS  # toujours
```

**Cas C — qualité basse + peu de séances** :
```python
status="ok"
headline="Lecture corporelle issue de l'entraînement (30 derniers jours)."
priorities=(
  BodyIntelligencePriority(key="low_logging_confidence", severity="watch", ...),
  BodyIntelligencePriority(key="consistency_gap", severity="watch", ...),
)
```

### 4.7 Garde-fous anti-pseudo-science

- `BMI` toujours classé `derived` (test dédié), accompagné d'un disclaimer dans `content`.
- 12 tokens interdits scannés sur l'ensemble des strings de tout snapshot (parametrize sur 5 scénarios) — incluant *"tu es déséquilibré"*, *"ton physique est"*, *"ton taux de gras"*, *"ta posture"*, *"symétrie corporelle"*, *"diagnostic"*, *"problème médical"*, et les héritages Sx_27/30 (*"tu dois"*, *"il faut absolument"*, *"obligatoire"*).
- Vocabulaire autorisé vérifié explicitement : *"données insuffisantes"*, *"zone moins représentée"*.
- `overload_compliance_status = "not_available_v1"` exposé dans le bloc limits (test garde explicite).
- `DEFAULT_LIMITS` toujours retourné, mentionne explicitement composition / esthétique / posture (tests).

## 5. Statut des tests (Sb_31.1)

| Catégorie | Tests | Résultat |
|---|---|---|
| Version + structure | 3 | ✅ |
| Status (3 valeurs) | 4 | ✅ |
| Blocs (présence + always-on limits) | 2 | ✅ |
| BMI (4 cas) | 4 | ✅ |
| Priorités (arbre + cap + ordre) | 8 | ✅ |
| Seuils figés + alignement RADAR_AXIS_ORDER | 2 | ✅ |
| Déterminisme + types output | 2 | ✅ |
| Vocabulaire (parametrize 5 scénarios + autorisé) | 2 | ✅ |
| Overload non V1 | 2 | ✅ |
| Limits par défaut | 1 | ✅ |
| Ratios cas dégénérés (pull=0, lower=0) | 2 | ✅ |
| Sérialisable + reload sans side-effect | 2 | ✅ |
| **Total Sb_31.1** | **38** | **✅ 38 passed en 0.03 s** |

### Suite complète (background run en cours)

Tests Sx_30 (122) + Sx_29 (76) + Sx_27 + Sx_26 + reste → confirmé en CI post-push.

## 6. Statut DoD locale

| Gate | Statut |
|---|---|
| `pytest tests/test_body_intelligence.py -q` | ✅ 38 passed |
| `pytest --ignore=tests/test_v1_acceptance.py -q` | ⏳ background run |
| `check_ruff_budget.py` | ✅ 529 ≤ 548 (autofix I001 appliqué) |
| `check_spec_protocol.py` | ✅ |
| `PYTHONPATH=. check_alembic_drift.py` | ✅ no diff (aucune migration Sb_31.1) |

## 7. Contraintes techniques respectées (verbatim user)

| Contrainte | OK |
|---|---|
| 0 route | ✅ |
| 0 template | ✅ |
| 0 CSS | ✅ |
| 0 JS | ✅ |
| 0 migration | ✅ |
| 0 dépendance externe | ✅ |
| 0 LLM | ✅ |
| 0 HealthKit / Health Connect | ✅ |
| 0 photo / scan | ✅ |
| Aucun changement Sx_30 overload engine | ✅ |
| Aucun changement scoring | ✅ |
| Aucun changement substitution | ✅ |
| Aucun changement coach report | ✅ |
| Composer ne touche pas la DB | ✅ test garde structurel |
| Composer ne touche pas le réseau | ✅ test garde structurel |
| Composer ne touche pas FastAPI/Jinja | ✅ test garde structurel |
| Dataclasses frozen | ✅ test dédié |
| Fonction déterministe | ✅ test dédié |
| Pas de personnalisation V1 | ✅ seuils figés |

## 8. OQ Sx_31 — état au sortir de Sb_31.1

| OQ | Statut Sb_31.1 |
|---|---|
| OQ-A `/body` route | ⏳ Sb_31.2 |
| OQ-B CSS extrait | ⏳ Sb_31.2/5 |
| OQ-C seuils figés | ✅ implémenté |
| OQ-D BMI faible + derived | ✅ implémenté + testé |
| OQ-E overload compliance non V1 | ✅ marqueur `"not_available_v1"` exposé + tests |
| OQ-F carte home | ⏳ différé `Sb_31.next.home-card` |
| OQ-G lien `/profile` → `/body` | ⏳ Sb_31.2 ou Sb_31.3 |

## 9. CI réelle (post-push)

**Run GitHub Actions : [28302706112](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/28302706112) — ✅ success (3/3 jobs verts)**

Note : un premier run [28302661277](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/28302661277) sur le commit `0016f7f` (Sb_31.1 strict) a été cancelled par un push concurrent `e681040` (merge PR #15 — Manual Body Profile MVP du track parallèle Body Signal Model). Le run final couvre `e681040` qui contient `0016f7f` + le merge — Sb_31.1 est validé en CI.

- [x] Job `pytest + QA scripts` — ✅ success
- [x] Job `lint (ruff budget + bandit + actionlint + shellcheck)` — ✅ success
- [x] Job `SonarCloud` — ✅ success

## 10. Métriques

| Item | Valeur |
|---|---|
| Lignes service ajoutées | +415 (`body_intelligence.py`) |
| Tests ajoutés | +38 |
| Routers touchés | 0 |
| Templates touchés | 0 |
| Migrations | 0 |
| Modèles SQLAlchemy | 0 |
| CSS / JS ajoutés | 0 |
| Services métier core mutés | 0 |
| Dépendances externes ajoutées | 0 |
| Ruff budget | 529 ≤ 548 (inchangé vs Sx_30 closure) |

## 11. Couche I/O à venir (Sb_31.2)

Le composeur attend des inputs purs. La couche I/O qui les construit n'existe pas encore et sera livrée en Sb_31.2, en appelant les services existants (lecture seule) :
- `profile_metrics.streak_days`, `cardio_minutes_per_week`, `strength_volume_delta_pct`, `zone_session_counts`, `pattern_distribution`, `dominant_pattern`, `discipline_rates`
- `muscle_scoring.compute_physique_dashboard` (déjà 30j window)
- `coach_report._weight_trend_90d`
- `compute_session_quality` + comptage → moyenne 30j
- `compute_confidence_score` → moyenne globale
- `body_measurements` desc + `users.height_cm/weight_kg/waist_cm` fallback
- Agrégation `implicit_label` 30j

Aucune mutation prévue de ces services en Sb_31.2 — uniquement composition.

## 12. Non-goals respectés (rappel)

- Pas de promesse esthétique
- Pas de composition corporelle supposée
- Pas d'analyse morphologique
- Pas de pseudo-science
- Pas de LLM
- Pas de calcul overload compliance V1
- Pas de personnalisation des seuils V1
- Pas de mutation des services métier core

## 11. Verdict

**✅ Sb_31.2 prêt.**

Prochaine étape : `Sb_31.2` livrera :
1. La **couche I/O** `body_intelligence_inputs.py` qui compose les services existants pour produire un `BodyIntelligenceInput`.
2. La **route** `GET /body` (SSR).
3. Le **template** `body_intelligence.html` + partials par bloc.
4. Les **tests d'intégration** route + template.

Aucun blocage anticipé. Le composeur est testable en isolation et prêt à recevoir des inputs purs depuis la couche I/O Sb_31.2.
