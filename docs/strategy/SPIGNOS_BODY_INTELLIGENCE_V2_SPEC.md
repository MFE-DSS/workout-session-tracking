# SPIGNOS — Body Intelligence v2 Spec

**Sprint :** `Sx_31 — Body Intelligence v2 Spec`
**Date :** 2026-06-27
**Type :** **SPEC ONLY**. Aucun code, aucune migration, aucune dépendance ajoutée.
**Branche cible :** `claude/sprint-reporting-fitness-app-V7Qr6`

---

## A. Statut du document

| Champ | Valeur |
|---|---|
| Statut | ⚪ **DRAFT — spec stratégique pour validation utilisateur** |
| Convention | `Sx_31` = spec only, `Sb_31.k` = build sprints (cf. `SPEC_DRIVEN_ENGINEERING_PROTOCOL_v1.md`) |
| Stack contrainte | FastAPI SSR + Jinja2 + SQLite + SQLAlchemy + Alembic |
| Hard contracts hérités | SSR-first, mobile-first 360×640, ADD COLUMN ONLY, snapshot + drift guard + roundtrip, ruff budget verrouillé, ownership utilisateur (`user_id` + `ondelete=CASCADE`), no-JS fallback partout |
| Override de lancement | Humain explicite 2026-06-27 (post-closure Sx_30, post-dogfood Sx_29 PASS, dogfood Sx_30 toujours pending et non bloquant pour cette spec) |
| Documents sœurs (à coordonner) | `SPIGNOS_BODY_INTELLIGENCE_ROADMAP.md` (cadrage Body 5 lots), `SPIGNOS_BODY_SIGNAL_MODEL_SPEC.md` (signaux photos/scans, hors scope direct Sx_31), `SPIGNOS_BODY_PRIVACY_AND_CONSENT_SPEC.md` (consentement, hors scope Sx_31) |
| Scope Sx_31 vs ces sœurs | **Body Intelligence v2 = consolidation des données d'entraînement déjà loguées en une lecture corporelle synthétique.** Pas de nouvelle source d'input (pas de photos, pas de scan, pas de HealthKit). Les specs « Body Signal Model » et « Body Privacy » restent indépendantes et orthogonales. |

> **Garde-fou produit (valable partout) :** SPIGNOS ne diagnostique pas, ne prédit pas l'esthétique réelle, ne juge pas le corps. Tout signal produit doit être **mécaniquement traçable** à des données d'entraînement loguées et **mécaniquement explicable** dans la même UI.

---

## B. Contexte et état actuel (audit repo 2026-06-27)

### B.1 Données déjà persistées

| Surface | Table / champ | Notes |
|---|---|---|
| Identité | `users.height_cm` `weight_kg` `waist_cm` `resting_hr` `bp_systolic/diastolic` | Saisie manuelle libre, non datée, non versionnée |
| Mesures corporelles | `body_measurements` (`measured_at`, `weight_kg`, `chest_cm`, `arm_cm_left/right`, `waist_cm`, `thigh_cm_left/right`, `hip_cm`, `neck_cm`, `calf_cm`) | Time-series datée, chaque ligne = 1 mesure, champs nullables |
| Séances strength | `workout_sessions` + `session_exercises` + `set_logs` (work + warmup, weight_kg + reps + completed) | Snapshot-based, lié à un template |
| Séances cardio | `workout_sessions` (`cardio_duration_min`, `cardio_bpm_avg`, `cardio_machine_type`, `cardio_machine_calories`) | Champ optionnel par session, complète strength |
| Qualité séance | `compute_session_quality()` (0..100) | Formula V1 (work + success + concentration + global_state) ou V2 (V1 + implicit signal) selon `scoring_version` |
| Signal implicite | `session_exercises.implicit_label` ∈ {RESERVE_PROBABLE, TRAJECTOIRE_COHERENTE, PYRAMIDAL_ASCENDANT, PYRAMIDAL_DESCENDANT, INCOHERENT}, freezé au passage in_progress→completed | Sx_24 |
| Confiance | `compute_confidence_score()` | Cf. `app/services/confidence.py`, score numérique + label qualitatif |
| Overload | `compute_overload_hint()` + `overload_engine_version` (per session) | Sx_30 — 5 états par exercice (`progress` / `consolidate` / `top-range` / `deload` / `unknown`), cible chiffrée + reasons |
| Substitution | `app/services/substitution.py` | N1/N2/N3, pattern motor, propose alternatives ; pas exploité dans Body Intelligence |
| Mapping exercice→zone | `app/services/muscle_mapping.py` | 11 zones détaillées + 6 axes radar (`pecs`, `shoulders`, `back_width`, `back_thickness`, `arms`, `lower`) |
| Profile metrics | `app/services/profile_metrics.py` | Streak, cardio_minutes/week, volume_delta_pct, top/neglected zone, dominant_pattern, last_session_summary, discipline_rates, strength_cardio_ratio, zone_session_counts, pattern_distribution |
| Physique dashboard | `app/services/muscle_scoring.py::compute_physique_dashboard` | 11 zones avec score performance + exposure + anthropo, confidence pondéré, top exercises par zone |
| Radar SVG | `app/services/radar.py::build_radar_svg` | 6 axes, SSR-rendered |
| Coach report | `app/services/coach_report.py::build_report` | Identity + Volume + Zones + Patterns + ImplicitSignalsBlock, 30j |
| Routes existantes | `/profile`, `/physique`, `/progress`, `/coach-report`, `/u/{username}` (leaderboard public preview) | SSR uniquement, no JS critique |

### B.2 Surfaces de rendu existantes

| Route | Template | Contenu actuel |
|---|---|---|
| `/profile` | `profile.html` | Identité + page payload (L3 du Profile Synthesis v2) |
| `/physique` | `physique.html` | Physique dashboard 11 zones + radar 6 axes + body measurements |
| `/coach-report` | `coach_report.html` | 5 blocs Identity/Volume/Zones/Patterns/ImplicitSignals + narratives Sx_27 |
| `/progress` | `progress.html` | Timeline + weekly loop (Sx_27) |
| `/` (home) | `home.html` | Dashboard activation (Sx_27) avec `home_coaching_loop` partial |
| `/u/{user}` | `user_profile.html` | Preview L2 + dashboard public |

### B.3 Ce que la lecture actuelle ne fait PAS

1. **Pas de lecture corporelle synthétique unifiée** : l'utilisateur doit visiter 3-4 pages pour reconstituer "qu'est-ce que mon entraînement produit sur mon corps".
2. **Pas de distinction explicite Mesuré / Dérivé / Inféré** dans l'UI. Le `quality_score` ressemble à un fait alors qu'il est dérivé ; les top/neglected zones sont calculées mais affichées comme des constats.
3. **Pas d'agrégation longue durée** au-delà des fenêtres 30j (la timeline atteint 90j mais sans synthèse).
4. **Pas de signal "ce que tu sous-travailles vs ce que tu devrais peut-être travailler"** : seul le constat est exposé, pas le delta cible vs réel.
5. **Pas d'intégration des données body_measurements dans la lecture training** (la progression tour de taille est isolée de la progression force/volume).
6. **Pas d'utilisation des implicit_label agrégés** comme signal de qualité dans le coach report v1 (présent mais sous-exploité).
7. **Pas de lecture overload-aware** : Sx_30 vient d'être livré mais Body Intelligence n'en consomme rien.

---

## C. Problème produit

L'utilisateur sait :
- combien il a logué de séances (Sx_27)
- comment il s'est senti par séance (declarative + implicit)
- quelle cible overload viser sur l'exercice courant (Sx_30)

Mais l'utilisateur **ne sait pas** :
- Où son corps progresse vraiment sur 30/90 jours (volume × zone × cohérence).
- Quelles zones sont sous-travaillées par rapport à un équilibre raisonnable (push/pull, haut/bas, antagonistes).
- Si la qualité moyenne de logging est suffisante pour faire confiance à ces lectures.
- Quoi ajuster en priorité (1 action recommandée, pas un dashboard d'arbitrage).
- Ce que SPIGNOS ne peut PAS lui dire (limites assumées).

Body Intelligence v2 doit traiter ces 5 manques sans ajouter de source de données externe ni promettre des mesures que le système n'a pas.

---

## D. Objectifs Body Intelligence v2

D1. **Lecture corporelle dérivée de l'entraînement**, consolidée en un seul endroit sur mobile.
D2. **Distinguer rigoureusement** ce qui est mesuré, dérivé, inféré, non déductible.
D3. **Produire 1 priorité d'ajustement** (pas plus, pas moins) actionnable la séance suivante.
D4. **Réutiliser** les services existants (`profile_metrics`, `muscle_scoring`, `coach_report`, `overload_engine`, `quality_score`, `implicit_signal`) sans en muter aucun.
D5. **Mobile-first 360×640**, SSR, zéro JS obligatoire, no-JS fallback intégral.
D6. **Aucune promesse esthétique ou médicale.** Vocabulaire training-centric uniquement.

---

## E. Inventaire des données disponibles (matrice détaillée)

### E.1 Sources d'input utilisateur (mesurées)

| Champ | Source | Cadence | Persistance | Utilisable Sx_31 ? |
|---|---|---|---|---|
| `users.height_cm` | Saisie profil unique | Statique | `users` | ✅ pour ratios |
| `users.weight_kg` | Saisie profil (overwrite) | Ad-hoc | `users` | ⚠️ pas datée — privilégier `body_measurements` |
| `users.waist_cm` | Saisie profil (overwrite) | Ad-hoc | `users` | ⚠️ idem |
| `users.resting_hr` / `bp_*` | Saisie profil | Statique | `users` | ⚠️ hors scope Sx_31 V2 (cardio readiness, futur) |
| `body_measurements.*` | Saisie datée | Au gré de l'utilisateur | `body_measurements` | ✅ time-series propre |
| `set_logs.weight_kg` / `reps` / `completed` | Saisie séance | À chaque séance | `set_logs` | ✅ pierre angulaire |
| `session_exercises.success_score` / `execution_quality` / `muscle_sensation` | Saisie post-exercice | Par exercice | `session_exercises` | ✅ signal qualitatif |
| `workout_sessions.concentration` / `global_state` | Saisie post-séance | Par séance | `workout_sessions` | ✅ contribue quality_score |
| `workout_sessions.cardio_*` | Saisie cardio | Par séance cardio | `workout_sessions` | ✅ pour volume cardio |

### E.2 Dérivés déterministes

| Métrique | Service | Inputs | Notes Sx_31 |
|---|---|---|---|
| `streak_days` | `profile_metrics.streak_days` | sessions datées | Réutilisable tel quel |
| `cardio_minutes_per_week(30d)` | `profile_metrics.cardio_minutes_per_week` | `cardio_duration_min` | Réutilisable |
| `strength_volume_delta_pct(30d vs 30d-prev)` | `profile_metrics.strength_volume_delta_pct` | tonnage agrégé | Réutilisable, central pour D3 |
| `top_zone(30d)` / `neglected_zone(30d)` | `profile_metrics.top_zone` / `neglected_zone` | zone counts par session | Réutilisable, **renommer pour clarté** dans l'UI v2 |
| `dominant_pattern(30d)` | `profile_metrics.dominant_pattern` | pattern motor distribution | Réutilisable |
| `discipline_rates(30d)` | `profile_metrics.discipline_rates` | sessions cardio/strength | Réutilisable |
| `strength_cardio_ratio(30d)` | `profile_metrics.strength_cardio_ratio` | comptes sessions par type | Réutilisable |
| `zone_session_counts(30d)` | `profile_metrics.zone_session_counts` | par session, dédupliqué | Réutilisable pour heatmap |
| `pattern_distribution(30d)` | `profile_metrics.pattern_distribution` | sessions × patterns | Réutilisable |
| `compute_physique_dashboard(window_days=30)` | `muscle_scoring.compute_physique_dashboard` | tonnage + exposure + anthropo + confidence par zone | Réutilisable, **principal consommé** par Body Intelligence v2 |
| `compute_session_quality(s)` | `quality_score` | per session | ✅ moyennable sur 30j |
| `compute_overload_hint(input)` | `overload_engine` | per exercice | ✅ agrégeable en compliance Sb_31.next (V2 différé) |
| `build_report(db, user)` | `coach_report` | tout le précédent | Source narrative — réutilisable mais à compléter par Body Intelligence |

### E.3 Inférés (qualitatifs ou probabilistes)

| Inférence | Source | Confiance | Notes |
|---|---|---|---|
| `implicit_label` per exercice | `implicit_signal.detect_intra_set_label` | Faible (≥3 work sets requis) | Agrégat 30j = signal de cohérence intra-set |
| `confidence_score` per dashboard zone | `confidence.compute_confidence_score` | Numérique 0-100 | Pondère les zones avec peu de données |
| Implicit signals block (coach_report) | `coach_report._implicit_signals_30d` | Agrégat 30j | À exposer en v2 |
| Profile L3 page | `profile_metrics.build_page` | Composition de dérivés | Réutilisable |

### E.4 Non déductibles (à interdire dans l'UI)

| Promesse interdite | Raison |
|---|---|
| Composition corporelle (% masse grasse / masse maigre) | Pas de DEXA / impédancemètre / pli cutané dans l'app |
| Esthétique réelle / symétrie visuelle | Pas de photo, pas de scan |
| Hypertrophie musculaire vérifiée | Pas d'imagerie / mensuration musculaire précise |
| Posture | Pas de capteur, pas de photo posturale |
| Risque de blessure | Pas un médecin, pas de KPI clinique |
| VO2max / capacité cardio précise | Cardio loggué = `bpm_avg` déclaratif + machine_calories indicatives |
| Calories brûlées vraies | `machine_calories` = affichage machine, jamais vérité |
| Pourcentage de fibres lentes/rapides | Hors mesure |
| Asymétrie L/R fine | `body_measurements.arm_cm_left/right` existe mais bruit > signal sur 1-2 mesures |

---

## F. Classification Mesuré / Dérivé / Inféré / Non déductible

| Niveau | Définition Sx_31 | Marqueur UI proposé |
|---|---|---|
| **Mesuré** | Saisi par l'utilisateur ou enregistré par le système sans transformation. Aucune ambiguïté. | `Mesuré` (sobre, gris) |
| **Dérivé** | Calculé déterministiquement depuis des `Mesuré`. Reproductible bit-à-bit. | `Dérivé` (gris ou neutre) |
| **Inféré** | Probabiliste ou heuristique. Peut être faux. Toujours accompagné d'un signal de confiance. | `Inféré` (warn discret) + confidence_score |
| **Non déductible** | SPIGNOS ne peut pas le dire. Doit être **explicitement absent** ou marqué « non disponible ». | Pas d'affichage, ou bloc "Hors de portée" |

> **Règle UI Sx_31 :** chaque carte/bloc de Body Intelligence v2 **doit** porter un marqueur de niveau, même discret. C'est la contremesure principale contre la dérive pseudo-scientifique.

---

## G. Modèle de métriques recommandé

### G.1 Bloc Identity (`Mesuré` + `Dérivé`)
- `height_cm`, `weight_kg` (le plus récent entre `users.weight_kg` ad-hoc et `body_measurements.weight_kg` datée le plus récent — prendre le plus récent et badger sa date)
- `weight_trend_90d` (`Dérivé` : `body_measurements` régression linéaire ou simple delta dernier/premier) — réutilise `coach_report._weight_trend_90d`
- `waist_cm` le plus récent + delta 90j si disponible
- BMI (`Dérivé` : `weight_kg / (height_m)²`) — **uniquement si height et weight présents**, accompagné de la limite "BMI = indicateur grossier, jamais un objectif"

### G.2 Bloc Volume & Discipline (`Dérivé`)
- `sessions_30d` + `sessions_90d`
- `streak_days`
- `strength_cardio_ratio` (badge `équilibré` / `cardio-light` / `cardio-lourd`)
- `cardio_minutes_per_week`
- `work_sets_per_week` (déjà calculé par `coach_report._work_sets_per_week`)
- `volume_delta_pct` 30j vs 30j précédents

### G.3 Bloc Zones (`Dérivé`)
Réutiliser `compute_physique_dashboard(30)` + `zone_session_counts(30)`.
- **Top 3 zones** (volume × performance)
- **Bottom 3 zones** (sous-travaillées vs équilibre attendu)
- **Heatmap 6 axes radar** (réutilise `radar.build_radar_svg`, déjà SSR)
- Cohérence push/pull (ratio `(pecs + shoulders)/(back_width + back_thickness)`)
- Cohérence haut/bas (ratio `(arms + pecs + shoulders + back_*)/(lower)`)

### G.4 Bloc Qualité de signal (`Dérivé` + `Inféré`)
- `quality_score` moyen 30j (`Dérivé`, accompagné de n sessions)
- Distribution implicit_labels 30j (`Inféré`, badge confiance)
- `confidence_score` global (`Inféré`)
- Volume sessions sans logging complet (signal de friction)

### G.5 Bloc Overload Compliance (V2 différé — Sb_31.next)
- Combien d'exercices ont reçu un état `progress` / `consolidate` / `top-range` / `deload` sur 30j
- À implémenter si Sb_31 V1 est validé en dogfood

### G.6 Bloc "1 priorité d'ajustement" (`Inféré`)
**Une seule** ligne, mécaniquement dérivée d'un arbre de décision :
- Si `discipline_rates.sessions_per_week < 2` → "Augmenter la régularité avant tout".
- Sinon si `volume_delta_pct < -15%` → "Volume en baisse — vérifier la régularité ou la motivation".
- Sinon si une zone bottom-3 est aussi dans `RADAR_AXIS_ORDER` haute priorité → "Travailler [zone] cette semaine (sous-exposé sur 30j)".
- Sinon si `quality_score` moyen < 60 → "Loguer plus précisément aide les recos (concentration + global_state)".
- Sinon → "Tendance saine — maintenir le cap".

L'arbre est **déterministe**, **explainable** (le bloc doit dire pourquoi), et **borné à 1 priorité**.

### G.7 Bloc "Limites de cette lecture" (méta)
Listé explicitement (pas une note de bas de page) :
- BMI = indicateur grossier
- Pas de mesure de composition corporelle
- Pas de mesure d'esthétique / symétrie
- Pas de prédiction de blessure
- Signal cardio = déclaratif

---

## H. Hiérarchie UI recommandée

### H.1 Page principale : nouvelle route SSR `/body`

(Évite la collision sémantique avec `/physique` qui reste centré "tonnage par zone").

Structure mobile-first :
1. **Header** identité (nom, statut, dernière séance)
2. **Bloc Volume & Discipline** (compact, 3-4 chiffres clés)
3. **Bloc Zones** (heatmap radar SVG + top/bottom 3 + ratios push-pull / haut-bas)
4. **Bloc Qualité de signal** (1 ligne + confidence badge)
5. **Bloc 1 priorité** (mise en valeur, encadré sobre)
6. **Bloc Limites** (toujours visible, dépliable via `<details>` natif)

### H.2 Surfaces existantes — quoi compléter

| Surface | Action Sx_31 V1 |
|---|---|
| `/profile` | Ajouter un lien "Voir lecture Body" vers `/body`. Aucun changement structurel. |
| `/physique` | **Inchangé** (continue à servir comme vue analytique 11 zones, complémentaire). |
| `/progress` | Inchangé. |
| `/coach-report` | Ajouter un block "Snapshot body intelligence" qui inclut la priorité + le delta volume + le BMI le plus récent (compact). |
| `/` (home) | Optionnel V1 : 1 carte mini-summary (`home_coaching_loop` extension ou nouveau partial). Différer si charge cognitive trop élevée. |

### H.3 Anti-patterns UI

- Pas de score global numérique unique ("body score 78/100"). Trop pseudo-scientifique.
- Pas de gauge / graphique animé. SSR-only.
- Pas de carte "objectif" sans input utilisateur explicite. Body Intelligence v2 n'a pas d'input objectif/cible utilisateur — c'est une lecture, pas un coach goal-driven.
- Pas de comparaison entre utilisateurs sur cette page.

---

## I. Interprétations autorisées

| Phrase autorisée | Justification |
|---|---|
| "Tu as logué N séances strength et M cardio sur 30 jours" | Constat brut |
| "Ton volume strength est en hausse/baisse de X% vs 30j précédents" | Dérivé déterministe |
| "Zone X est ton top de volume sur 30j" | Dérivé |
| "Zone Y est sous-exposée vs équilibre push-pull" | Dérivé avec règle explicite |
| "Quality_score moyen 30j = N (sur N' sessions)" | Dérivé |
| "Ton corps semble plus régulièrement sollicité sur le haut que sur le bas (ratio R)" | Dérivé + ratio explicite |
| "BMI calculé : X (indicateur grossier, jamais un objectif en soi)" | Dérivé + disclaimer |
| "Priorité suggérée : [action], parce que [raison déterministe]" | Inféré explainable |

## J. Interprétations interdites

| Phrase interdite | Raison |
|---|---|
| "Tu progresses bien physiquement" | Vide, non vérifiable |
| "Tu as pris du muscle / perdu du gras" | Composition corporelle non mesurée |
| "Ton physique est équilibré" | Esthétique non mesurée |
| "Ton risque de blessure est faible/élevé" | Pas médical |
| "Tu brûles N kcal" (énoncé comme vérité) | machine_calories = affichage indicatif |
| "Ton VO2max est..." | Pas mesuré |
| "Tu devrais peser X kg" | Pas un coach goal-driven |
| Tout verbe autoritaire ("tu dois", "il faut absolument") | Style SPIGNOS (Sx_27/30 contract) |

---

## K. Impacts techniques

| Couche | Impact Sx_31 V1 |
|---|---|
| `app/services/` | **Nouveau** `body_intelligence.py` (compose les dérivés existants + arbre de décision priorité). **Aucune mutation** de `profile_metrics`, `muscle_scoring`, `quality_score`, `implicit_signal`, `coach_report`, `radar`, `muscle_mapping`. |
| `app/routers/` | **Nouvelle route** `GET /body` (SSR). Ajout block dans `/coach-report`. Aucune mutation des autres routes. |
| `app/templates/` | **Nouveau** `body_intelligence.html` + partials `_partials/body_*` (header, volume, zones, quality, priority, limits). |
| `app/static/css/` | Extensions ciblées `app.css` ou nouveau `body_intelligence.css` selon volume (cf. OQ-B). |
| `app/static/js/` | **Aucun JS obligatoire.** Pas de nouveau fichier JS Sx_31 V1. |
| `app/models/` | **Aucune nouvelle table** V1. Pas de colonne. |
| `migrations/` | **Aucune migration** V1. |
| `tests/` | Nouveaux tests pour le composeur + tests d'intégration de la route + a11y. |
| Dépendances | **Zéro nouvelle dépendance externe** (pas de matplotlib, pas de plotly, le radar SVG existe déjà). |

---

## L. Risques

| Risque | Sévérité | Mitigation |
|---|---|---|
| Dérive pseudo-scientifique (l'utilisateur prend les inférences pour des faits) | **Haute** | Marqueurs Mesuré/Dérivé/Inféré obligatoires sur chaque bloc + section Limites toujours visible |
| Sur-redondance avec `/physique`, `/coach-report`, `/profile` | Moyenne | Spec UI claire (§H), `/body` = lecture synthétique 1-écran, `/physique` reste analytique |
| Charge cognitive trop élevée sur mobile | Moyenne | "1 seule priorité" stricte, blocs collapsibles via `<details>` |
| Dépendance implicite à des champs nullables (`height_cm`, `weight_kg`) | Moyenne | Chaque bloc doit gérer le cas "donnée absente" avec un fallback explicite |
| Lectures contradictoires entre `/body` et `/coach-report` | Moyenne | Les deux consomment les mêmes dérivés (réutilisation `profile_metrics` + `coach_report`) — vérifié par tests d'égalité |
| Performance (compose 5+ services en 1 requête GET) | Faible | Toutes les fonctions sont déjà optimisées single-window 30j ; ajouter assertion p95 < 250ms en Sb_31.4 |
| Friction utilisateur si arbre de décision donne une priorité non pertinente | Moyenne | Dogfood Sb_31.5, ajuster les seuils ; reasons toujours visibles pour que l'utilisateur juge |
| Conflit conceptuel avec spec parallèle `SPIGNOS_BODY_SIGNAL_MODEL_SPEC.md` | Faible | Body Intelligence v2 = training-derived ; Body Signal Model = photos/scans. Pas d'overlap technique, mais coordonner les noms de routes (`/body` ici ; le signal model utilisera autre chose) |

---

## M. Acceptance criteria

Sx_31 SPEC est acceptée ssi l'opérateur valide :

1. La distinction **Mesuré / Dérivé / Inféré / Non déductible** est claire et applicable.
2. Le modèle de métriques **§G** est exhaustif sur ce qui est disponible et explicite sur ce qui est exclu.
3. La hiérarchie UI **§H** (nouvelle route `/body` + complément `/coach-report`) est pertinente.
4. La règle "1 seule priorité" **§G.6** est défendable.
5. Le périmètre "**0 nouvelle dépendance, 0 migration V1**" est confirmé.
6. Les **OQ §N.1** sont tranchées ou explicitement reportées.
7. La **build queue §N.2** est confirmée ou amendée.

---

## N. Open questions + Lotissement build recommandé

### N.1 Open questions à trancher avant Sb_31.1

| OQ | Question | Recommandation V1 |
|---|---|---|
| OQ-A | Route name : `/body` ou `/lecture-corps` ou `/intelligence` ? | `/body` (court, mobile-first, alignement avec spec sœur Body Signal Model qui utilisera `/body/profile` plus tard) |
| OQ-B | CSS : inline `app.css` ou nouveau `body_intelligence.css` extrait Sb_31.5 ? | Inline V1 ; extraire si > 200 lignes (pattern Sx_29 §OQ-B) |
| OQ-C | Arbre de décision priorité §G.6 : seuils figés v1 (15%, 60, 2/sem) ou paramétrables ? | Figés v1 ; paramétrables différé |
| OQ-D | Inclusion BMI : oui avec disclaimer, ou exclusion totale ? | Oui avec disclaimer **uniquement si height ET weight présents** ; afficher "Donnée manquante" sinon |
| OQ-E | Sb_31 V1 inclut-il l'overload compliance §G.5 ? | **Non**, différé `Sb_31.next.overload-compliance` après dogfood V1 |
| OQ-F | Bloc home : carte mini-summary ou laisser intact ? | Laisser intact V1 ; évaluer post-dogfood |
| OQ-G | Lien `/profile` → `/body` : remplacement ou complément ? | Complément (lien sobre, pas de redirection) |

### N.2 Build queue recommandée

| Sprint | Objet | Touche métier ? |
|---|---|---|
| `Sb_31.0` | **Spec review** (ce sprint, doc only) | Aucune |
| `Sb_31.1` | `body_intelligence.py` (composeur pur + arbre priorité) + tests unitaires | Nouveau service uniquement |
| `Sb_31.2` | Route `GET /body` + template `body_intelligence.html` + partials + tests intégration | Router + templates, aucun service core touché |
| `Sb_31.3` | Bloc "Snapshot body intelligence" dans `/coach-report` (additif) + tests | Modifie `coach_report.html` template uniquement, **pas** le service `coach_report.py` |
| `Sb_31.4` | A11y consolidation + perf assertion p95 + responsive 360×640 + non-color cues | Tests + CSS uniquement |
| `Sb_31.5` | Dogfood template + closure report Sx_31 + extraction CSS si > 200 lignes | Docs + CSS extraction si OQ-B le déclenche |

### N.3 Hors scope Sx_31 V1 (explicite, différé)

- Overload compliance agrégée (`Sb_31.next.overload-compliance`)
- Carte home mini-summary (`Sb_31.next.home-card`)
- Intégration des photos / scans / morphotypes (cf. spec sœur `SPIGNOS_BODY_SIGNAL_MODEL_SPEC.md` — track séparé)
- HealthKit / Health Connect / Apple Watch (Sx_33+)
- PWA / offline / service worker (Sx_32)
- Body composition (DEXA / impédancemètre) — pas de mesure, hors scope structurel
- Coach LLM (jamais dans Sx_31 V1)

---

## O. Recommandation du prochain sprint build

**Sb_31.1 — `body_intelligence.py` composeur pur + tests unitaires.**

Justification :
- Cohérent avec le pattern Sx_30 (Sb_30.1 = engine pur, testable en isolation, avant tout I/O).
- Permet de valider l'arbre de décision priorité §G.6 sur des inputs synthétiques avant de toucher router/template.
- Aucun risque sur les surfaces utilisateur existantes.

**Pré-requis avant Sb_31.1 :**
1. Trancher OQ-A → OQ-G (§N.1).
2. Confirmer build queue §N.2.
3. Bascule explicite `BUILD AUTHORIZED FOR Sx_31` (override #4).

Sans ces 3 conditions : **NE PAS commencer Sb_31.1**. Restent indépendamment bloqués : Sx_32 (PWA), Sx_33+ (Health/API), Body Signal Model track (`SPIGNOS_BODY_SIGNAL_MODEL_SPEC.md`), Sb_30.next.overload-compliance.

---

## P. Non-goals (rappel structurel)

Sx_31 V1 a EXPLICITEMENT exclu :

- React / SPA / bundler / dépendance JS externe
- PWA / service worker / offline mode
- HealthKit / Health Connect / Apple Watch / Garmin
- Photos / scan / morphotype (track séparé Body Signal Model)
- Coach LLM
- Body composition (DEXA / impédance)
- Score global numérique unique ("body score")
- Animations / gauges / charts dynamiques (SVG SSR uniquement)
- Mutation `profile_metrics`, `muscle_scoring`, `quality_score`, `implicit_signal`, `coach_report`, `radar`, `muscle_mapping`, `overload_*`, `substitution`, `recommendation`
- Nouvelle table SQL V1
- Migration Alembic V1
- Carte home mini-summary (différée)
- Ouverture automatique de Sx_32 / Sx_33+
