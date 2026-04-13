# Physique Dashboard — Design Spec

**Date:** 2026-04-13
**Scope:** Muscle development KPI dashboard with radar chart, composite scoring, confidence levels, and analytical detail view.

## Decisions

- New page `/physique` (not merged into /progress)
- Score composite 3 piliers: performance proxy (50%), exposition utile (30%), anthropométrie (20%)
- Radar SVG server-rendered (6 axes macro)
- Détail analytique (11 zones) avec barres + cards
- Score de confiance par zone (élevée/moyenne/faible)
- Mapping exercice→muscle par nom (substring match, pas par code)
- Fenêtre temporelle paramétrable (30/60/90 jours)
- Tour de taille réactivé dans les mesures pour contexte body comp

## Constraints

- No new JS dependencies — SVG server-rendered + CSS-only interactions
- No route changes to existing pages
- No model changes to existing tables
- Additive only: new services, new route, new template
- Waist_cm: column already exists in BodyMeasurement, just add to MEASUREMENT_FIELDS

---

## 1. Muscle Mapping

### File: `app/services/muscle_mapping.py`

**11 zones détaillées:**

| Zone key | Label | Mesure associée |
|----------|-------|----------------|
| `pecs` | Pectoraux | chest_cm |
| `delt_lat` | Deltoïdes latéraux | — |
| `delt_post` | Deltoïdes postérieurs | — |
| `lats` | Dos largeur | — |
| `upper_back` | Dos épaisseur | — |
| `biceps` | Biceps | arm_cm |
| `triceps` | Triceps | arm_cm |
| `quads` | Quadriceps | thigh_cm |
| `posterior` | Ischios / Fessiers | thigh_cm |
| `calves` | Mollets | — |
| `core` | Core / Abdos | waist_cm (inverse) |

**6 axes radar (agrégation):**

| Axe | Label | Zones agrégées |
|-----|-------|---------------|
| `pecs` | Pectoraux | pecs |
| `shoulders` | Épaules | delt_lat, delt_post |
| `back_width` | Dos largeur | lats |
| `back_thickness` | Dos épaisseur | upper_back |
| `arms` | Bras | biceps, triceps |
| `lower` | Bas du corps | quads, posterior, calves |

**Mapping exercice → zone par substring match sur exercise_name_snapshot (case-insensitive).**

Patterns:
- Pressing horizontal/incliné, butterfly, écarté pec, dips pec → `pecs` (secondaire: `triceps`)
- Shoulder press, élévation latérale, tirage front → `delt_lat`
- Face pull, rear delt, écarté arrière, oiseau → `delt_post`
- Tirage vertical, pulldown, pullover câble → `lats` (secondaire: `biceps`)
- Rowing, seated row, shrug → `upper_back` (secondaire: `biceps`)
- Curl, biceps → `biceps`
- Triceps, skull, extension overhead, pushdown → `triceps`
- Hack squat, leg press, leg extension, squat → `quads`
- Leg curl, RDL, hip thrust, deadlift → `posterior`
- Mollet, calf, relevé mollet → `calves`
- Abdo, crunch, roulette, ab wheel, pallof → `core`

Fallback: exercice non reconnu → `("unknown", [])`, ignoré du scoring.

**Contribution secondaire:** 30% du poids d'un exercice principal.

---

## 2. Scoring Musculaire

### File: `app/services/muscle_scoring.py`

### Pilier 1 — Performance proxy (50%)

Pour chaque zone, sur la fenêtre (30/60/90j):
1. Identifier les exercices de cette zone via mapping
2. Calculer le tonnage par séance: `sum(weight_kg × reps)` des work sets complétés
3. Comparer moyenne des 2 dernières séances vs 2 précédentes
4. Normaliser:
   - régression ≤ -10% → 20
   - stable (-10% à +2%) → 50
   - progression légère (+2% à +10%) → 70
   - progression solide (+10% à +20%) → 85
   - progression forte (>+20%) → 95
5. Si pas de données de tonnage (exercices au poids de corps, etc.) → fallback sur reps totales

### Pilier 2 — Exposition utile (30%)

Pour chaque zone, sur la fenêtre:
1. Compter les hard sets (work sets complétés) attribués à cette zone
2. Comparer au volume cible hebdomadaire:
   - pecs, lats, upper_back, quads, posterior: 16 sets/sem
   - delt_lat: 18 sets/sem
   - biceps, triceps, calves, core: 10 sets/sem
   - delt_post: 10 sets/sem
3. Ratio = `hard_sets / (cible_hebdo × (window_days / 7))` × 100
4. Capper à 100

### Pilier 3 — Anthropométrie (20%)

Pour chaque zone ayant une mesure associée:
1. Récupérer les mesures dans la fenêtre
2. Si ≥ 2 mesures: tendance = (dernière - première) / première × 100
3. Normaliser: perte → 30, stable → 50, gain léger → 70, gain solide → 90
4. Pour `core` (waist_cm): logique inversée (baisse = positif pour body comp)
5. Si < 2 mesures → pilier exclu, redistribution 60% perf + 40% exposition

### Score composite final

```
Si anthropo disponible:
  score = 0.50 × perf + 0.30 × exposition + 0.20 × anthropo

Si anthropo non disponible:
  score = 0.60 × perf + 0.40 × exposition
```

### Score de confiance

5 signaux binaires par zone:

| Signal | Condition |
|--------|-----------|
| a_performance | ≥ 4 work sets logués sur cette zone dans la fenêtre |
| a_volume | ≥ 2 séances contenant cette zone |
| a_anthropo | ≥ 2 mesures de la mensuration associée |
| a_bodyweight | ≥ 2 mesures de poids corporel |
| a_waist | ≥ 1 mesure de tour de taille |

```
total = sum(signals)
  4-5 → "élevée"
  2-3 → "moyenne"
  0-1 → "faible"
```

### Dataclasses

```python
@dataclass
class ZoneScore:
    zone: str           # "pecs", "delt_lat", ...
    label: str          # "Pectoraux"
    score: float        # 0-100
    trend: str          # "up", "down", "stable"
    confidence: str     # "élevée", "moyenne", "faible"
    hard_sets: int      # volume utile dans la fenêtre
    session_count: int  # nb séances contenant cette zone
    top_exercises: list[str]  # 3 exercices principaux
    measurement_label: str | None
    measurement_trend: str | None  # "+1.5 cm" ou None

@dataclass
class RadarAxis:
    axis: str           # "pecs", "shoulders", ...
    label: str          # "Pectoraux", "Épaules"
    score: float        # 0-100 (moyenne des zones agrégées)
    confidence: str

@dataclass
class PhysiqueDashboard:
    global_score: float      # moyenne des 6 axes radar
    global_grade: str        # A/B/C basé sur global_score
    zone_scores: list[ZoneScore]   # 11 zones
    radar_axes: list[RadarAxis]    # 6 axes
    radar_svg: str                  # SVG string
    window_days: int
```

---

## 3. Radar SVG

### File: `app/services/radar.py`

**`build_radar_svg(axes: list[RadarAxis], size: int = 300) -> str`**

- Hexagone régulier, 6 sommets à 60° d'intervalle
- 3 anneaux concentriques (33/66/100%) en `#232834` (--border)
- Lignes d'axes du centre vers chaque sommet, même couleur
- Labels d'axes: Inter 11px, `#9aa3ad` (--fg-muted), positionnés hors de l'hexagone
- Polygon du score: fill `#f25f3a1a` (accent 10% opacité), stroke `#f25f3a` 2px
- Points interactifs: circles 5px accent, hover agrandit + montre score (même CSS `.chart-point`)
- Score global au centre: JetBrains Mono 28px bold
- Fond: `#161a22` (--surface), radius 8px
- viewBox-based responsive, width 100%

---

## 4. Route + Template

### Route: `GET /physique` dans `app/routers/pages.py`

- Query param: `window` (int, default 30, values 30/60/90)
- Appelle `compute_physique_dashboard(db, user.id, window_days)`
- Passe au template: `dashboard` (PhysiqueDashboard), `window`

### Template: `app/templates/physique.html`

**Mobile (narration):**
1. Page title "Physique"
2. Score global (JetBrains Mono 32px, grade A/B/C badge)
3. Radar SVG
4. Sélecteur fenêtre (30j/60j/90j) — pills `.filter-bar`
5. Section "Détail par zone" — 11 `.zone-card` empilées

**Desktop (cockpit ≥768px):**
- `.cockpit-grid` 2 colonnes
- Gauche: score global + radar + sélecteur
- Droite: 11 zone-cards en scroll

**Zone card:**
```
┌──────────────────────────────────────────┐
│ Pectoraux                      ● élevée │
│ ██████████████████░░░░░ 78/100      ↑   │
│ 14 hard sets · 3 séances                │
│ Incline Smith, Chest Press, Dips        │
│ Poitrine: +1.2 cm                       │
└──────────────────────────────────────────┘
```

### Navigation

Ajouter "Physique" dans `base.html` topbar entre "Historique" et "Board".

---

## 5. Tour de taille — réactivation

Ajouter `waist_cm` à `MEASUREMENT_FIELDS` dans `measurements.py`. La colonne existe déjà dans `BodyMeasurement`. Le formulaire et les graphes l'intègreront automatiquement via l'itération sur `MEASUREMENT_FIELDS`.

Aussi réactiver `waist_cm` dans le endpoint POST `/profile/measurements` (ajouter le param Form + la logique comme pour les autres champs).

---

## 6. CSS

Ajouts dans `app/static/css/app.css`:

- `.radar-wrap` : conteneur centré, max-width 320px, margin auto
- `.zone-card` : card avec barre de progression
- `.zone-bar` : barre horizontale 6px height, `--surface-2` bg, fill coloré
- `.zone-bar__fill` : width dynamique via `style="width: X%"`, bg `--accent`
- `.zone-confidence` : point 8px inline (`.--high` ok, `.--medium` warn, `.--low` fg-dim)
- `.zone-meta` : 12px fg-muted, exercices contributeurs
- `.global-score` : JetBrains Mono 32px bold centré
- `.window-selector` : réutilise `.filter-bar` existant

---

## 7. Files Summary

| Action | File |
|--------|------|
| Create | `app/services/muscle_mapping.py` — exercise→zone mapping |
| Create | `app/services/muscle_scoring.py` — composite scoring + confidence |
| Create | `app/services/radar.py` — hexagon SVG builder |
| Create | `app/templates/physique.html` — dashboard page |
| Create | `tests/test_muscle_scoring.py` — scoring + mapping tests |
| Modify | `app/routers/pages.py` — add GET /physique route |
| Modify | `app/templates/base.html` — add "Physique" nav link |
| Modify | `app/services/measurements.py` — re-add waist_cm to MEASUREMENT_FIELDS |
| Modify | `app/routers/auth_routes.py` — re-add waist_cm to POST /profile/measurements |
| Modify | `app/static/css/app.css` — zone-card, radar-wrap, zone-bar classes |
