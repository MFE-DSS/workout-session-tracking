# Sx_31 — Body Intelligence v2 (Sprint Spec Report)

**Branche :** `claude/sprint-reporting-fitness-app-V7Qr6`
**Date :** 2026-06-27
**Type :** **SPEC ONLY** — aucun code, aucune migration, aucune dépendance.
**Spec parent livrée :** `docs/strategy/SPIGNOS_BODY_INTELLIGENCE_V2_SPEC.md`

---

## 1. Objectif

Spécifier la prochaine évolution majeure de la couche body/lecture corporelle de SPIGNOS, sans coder, en consolidant les données déjà loguées (sessions, scoring, overload, profile_metrics, body_measurements) en une lecture synthétique mobile-first qui sait dire ce qu'elle sait, ce qu'elle dérive, ce qu'elle infère et ce qu'elle ne sait pas.

## 2. Override de lancement

- Sx_30 TECHNICALLY CLOSED + UX COMPLET 2026-06-27 (CI 28297660877).
- Dogfood Sx_30 reste pending, mais override humain explicite 2026-06-27 pour ouvrir le prochain grand cycle produit en **SPEC ONLY**.
- Build Sx_31 reste subordonné à `BUILD AUTHORIZED FOR Sx_31` (override #4 à venir, après validation OQ et build queue).

## 3. Fichiers inspectés (audit réel du repo)

### 3.1 Modèles
- `app/models/user.py` — champs corporels statiques (`height_cm`, `weight_kg`, `waist_cm`, `resting_hr`, `bp_systolic/diastolic`)
- `app/models/measurement.py` — table `body_measurements` time-series (chest/arm L/R/waist/thigh L/R/hip/neck/calf + weight, datée)
- `app/models/session.py` — `workout_sessions` + `session_exercises` + `set_logs` + `implicit_label` + `scoring_version` + `overload_engine_version`

### 3.2 Services métier (lecture seule pour Sx_31)
- `app/services/profile_metrics.py` (~528 lignes) — streak / volume_delta / top_zone / neglected_zone / dominant_pattern / discipline_rates / strength_cardio_ratio / zone_session_counts / pattern_distribution / build_preview / build_page
- `app/services/muscle_scoring.py` — `compute_physique_dashboard` (11 zones + confidence)
- `app/services/muscle_mapping.py` — 11 zones détaillées + 6 axes radar (`pecs`, `shoulders`, `back_width`, `back_thickness`, `arms`, `lower`)
- `app/services/coach_report.py` — `build_report` (Identity + Volume + Zones + Patterns + ImplicitSignals)
- `app/services/quality_score.py` — `compute_session_quality` V1+V2
- `app/services/implicit_signal.py` — 5 labels, `detect_intra_set_label`
- `app/services/confidence.py` — `compute_confidence_score` + `level_for`
- `app/services/radar.py` — `build_radar_svg` (SSR pur)
- `app/services/overload_engine.py` + `overload_explainer.py` + `overload_inputs.py` (Sx_30)
- `app/services/measurements.py` — helpers `compute_arm_avg`, `compute_thigh_avg`
- `app/services/substitution.py` — utilisé par overload, hors scope Body Intelligence direct

### 3.3 Routes + templates
- `/profile` → `profile.html`
- `/physique` → `physique.html` (consomme `compute_physique_dashboard` + radar)
- `/progress` → `progress.html`
- `/coach-report` → `coach_report.html`
- `/u/{username}` → `user_profile.html`
- `/` → `home.html` + partial `home_coaching_loop`

### 3.4 Documents stratégiques sœurs (déjà présents sur la branche)
- `docs/strategy/SPIGNOS_BODY_INTELLIGENCE_ROADMAP.md` (Sx Body 00, cadrage 5 lots photos/scans)
- `docs/strategy/SPIGNOS_BODY_SIGNAL_MODEL_SPEC.md` (Sx Body 01, signaux photos/scans)
- `docs/strategy/SPIGNOS_BODY_PRIVACY_AND_CONSENT_SPEC.md`
- `docs/strategy/SPIGNOS_BODY_MANUAL_PROFILE_BUILD_SPEC.md`
- `docs/strategy/SPIGNOS_BODY_METRICS_READINESS_SPEC.md`
- `docs/strategy/SPIGNOS_BODY_ENGINEERING_DASHBOARD_V1.md`

**Décision de positionnement Sx_31 vs ces sœurs :**
La présente spec `SPIGNOS_BODY_INTELLIGENCE_V2_SPEC.md` traite spécifiquement de la **consolidation des signaux d'entraînement déjà loggés** en une lecture corporelle (`/body`). Elle n'introduit ni photos, ni scans, ni morphotype. Les specs Body Signal Model / Body Privacy / Body Manual Profile restent un track parallèle indépendant — sans conflit technique mais à coordonner sur les noms de routes (cf. spec §L.R7).

## 4. Surfaces existantes concernées

| Surface | Sx_31 V1 impact |
|---|---|
| `/profile` | Ajout d'un lien sobre vers `/body`. Inchangé sinon. |
| `/physique` | **Inchangé.** Continue à servir la vue analytique 11 zones, complémentaire de la lecture `/body`. |
| `/progress` | Inchangé. |
| `/coach-report` | **Ajout** d'un block "Snapshot body intelligence" via modification du template **uniquement** (le service `coach_report.py` reste intact). |
| `/` (home) | Inchangé V1 (carte mini-summary différée OQ-F). |
| `/u/{user}` | Inchangé. |

## 5. Métriques réutilisables (sans modification de service)

| Métrique | Service | Couverture Sx_31 |
|---|---|---|
| `streak_days(db, user_id)` | profile_metrics | ✅ Bloc Volume |
| `cardio_minutes_per_week(db, user_id, days=30)` | profile_metrics | ✅ Bloc Volume |
| `strength_volume_delta_pct(db, user_id, days=30)` | profile_metrics | ✅ Bloc Volume + arbre priorité |
| `top_zone / neglected_zone(db, user_id, days=30)` | profile_metrics | ✅ Bloc Zones + arbre priorité |
| `dominant_pattern(db, user_id, days=30)` | profile_metrics | ✅ Bloc Zones |
| `discipline_rates(db, user_id, days=30)` | profile_metrics | ✅ Bloc Volume + arbre priorité |
| `strength_cardio_ratio(db, user_id, days=30)` | profile_metrics | ✅ Bloc Volume |
| `zone_session_counts(db, user_id, days=30)` | profile_metrics | ✅ Heatmap radar |
| `pattern_distribution(db, user_id, days=30)` | profile_metrics | ✅ Cohérence push/pull |
| `compute_physique_dashboard(db, user_id, window_days=30)` | muscle_scoring | ✅ Bloc Zones + radar SVG |
| `build_radar_svg(axes, size, compact)` | radar | ✅ Rendu radar SSR |
| `compute_session_quality(s)` | quality_score | ✅ Bloc Qualité (moyenne 30j) |
| `compute_confidence_score(...)` | confidence | ✅ Marqueur Inféré sur Bloc Qualité |
| Implicit signals block | coach_report._implicit_signals_30d | ✅ Bloc Qualité |
| `_weight_trend_90d(db, user_id)` | coach_report | ✅ Bloc Identity (réutilisable) |

**Aucune mutation prévue** de ces services. Le nouveau `body_intelligence.py` (Sb_31.1) sera un composeur pur qui orchestre les appels existants + un arbre de décision pour la priorité unique.

## 6. Trous de données identifiés

| Trou | Conséquence Sx_31 | Mitigation |
|---|---|---|
| `users.weight_kg` / `waist_cm` non datés | Ambiguïté "est-ce le poids actuel ?" | Privilégier `body_measurements` le plus récent, badger la date |
| BMI requiert `height_cm` ET `weight_kg` | Indispensable pour le bloc Identity | Afficher "Donnée manquante" si l'un absent |
| `body_measurements` peut être vide | Bloc Identity ne montre que ce qui est disponible | Fallback explicite |
| Implicit signals nécessitent ≥ 3 work sets par exercice | Bruit sur petits volumes | Confidence badge sur le bloc Qualité |
| `success_score` / `execution_quality` saisis post-exercice — souvent skipped | Quality_score sous-estimé | Pas un blocage Sx_31, déjà géré par quality_score V2 |
| Pas de cible utilisateur (poids visé, taille visée) | Pas de feature "objectif" possible | Volontairement hors scope V1 (Sx_31 = lecture, pas coach goal-driven) |
| `overload_engine` n'a pas d'agrégat 30j | Compliance overload non disponible V1 | Différé `Sb_31.next.overload-compliance` |
| Pas de cardio HR series | Cardio reste déclaratif | Hors scope (HealthKit = Sx_33+) |

## 7. Risques d'interprétation abusive

| Risque | Garde-fou spec §I/§J |
|---|---|
| L'utilisateur prend les inférences pour des faits | Marqueur **Mesuré / Dérivé / Inféré** obligatoire sur chaque bloc |
| Promesse esthétique / composition corporelle | Spec §J liste 8 phrases interdites, dont "tu progresses bien physiquement", "tu as pris du muscle", "ton physique est équilibré" |
| Comparaison à un standard absent | Pas de score global numérique unique (interdit §H.3) |
| Confusion `/body` vs `/physique` | `/physique` reste analytique 11 zones inchangé ; `/body` = lecture synthétique 1-écran |
| Conflit avec spec sœur Body Signal Model | Aucun overlap technique (photos/scans hors scope V1) ; coordination routes documentée §L |
| Dérive autoritaire dans l'arbre priorité | Wording test garde-fou hérité Sx_27/30 ("tu dois" interdit) |

## 8. Arbitrages clés

| Arbitrage | Décision Sx_31 | Justification |
|---|---|---|
| Nouvelle route vs enrichir `/physique` | **Nouvelle route `/body`** | `/physique` est analytique (11 zones tonnage) ; `/body` est synthétique (lecture + priorité). Rôles distincts. |
| Mutation `coach_report.py` vs ajout block template seul | **Template seul** (Sb_31.3) | Service `coach_report` intact = no-regression facile à tester |
| Score global unique vs blocs séparés | **Blocs séparés avec marqueurs niveau** | Anti pseudo-science |
| Multi-priorités vs 1 seule | **1 seule** | Charge cognitive mobile, alignement avec philosophie Sx_27 "narrative ne ment jamais" |
| Inclusion BMI | **Oui avec disclaimer**, si height ET weight présents | BMI = indicateur grossier mais réutilisable comme jalon Mesuré×Dérivé |
| CSS inline vs extraction immédiate | **Inline V1**, extraction Sb_31.5 si > 200 lignes | Pattern Sx_29 §OQ-B |
| Overload compliance dans V1 | **Différé** `Sb_31.next.overload-compliance` | Dogfood Sx_30 reste pending — éviter mélange |
| JS vanilla pour interactivité | **Aucun** V1 | `<details>` natif suffit pour blocs collapsibles |

## 9. Build queue recommandée

| Sprint | Objet | Touche métier core ? |
|---|---|---|
| **Sx_31 (ce sprint)** | Spec doc only | Aucune |
| `Sb_31.0` | Spec review explicite + acceptation OQ (peut être fusionné avec Sx_31) | Aucune |
| `Sb_31.1` | `body_intelligence.py` composeur pur + arbre priorité + tests unitaires | Nouveau service uniquement |
| `Sb_31.2` | Route `GET /body` + template + partials + tests intégration | Router + templates |
| `Sb_31.3` | Block "Snapshot body intelligence" dans `/coach-report` (template uniquement) | Template uniquement, **pas** le service |
| `Sb_31.4` | A11y consolidation + perf assertion + non-color cues + responsive | Tests + CSS |
| `Sb_31.5` | Dogfood template + closure Sx_31 + extraction CSS si déclenchée | Docs + CSS extraction conditionnelle |
| `Sb_31.next.overload-compliance` | Block agrégation overload 30j (différé) | Service + template, sous override séparé |
| `Sb_31.next.home-card` | Carte mini-summary home (différé) | Template uniquement, sous override séparé |

## 10. Acceptance criteria spec

Spec acceptée ssi l'opérateur valide (cf. spec §M) :

1. Distinction Mesuré / Dérivé / Inféré / Non déductible claire.
2. Modèle métriques §G exhaustif et explicite sur les exclusions.
3. Hiérarchie UI §H pertinente (`/body` nouveau + bloc snapshot dans `/coach-report`).
4. Règle "1 seule priorité" §G.6 défendable.
5. Périmètre "0 nouvelle dépendance, 0 migration V1" confirmé.
6. OQ §N.1 tranchées ou explicitement reportées.
7. Build queue §N.2 confirmée ou amendée.

## 11. CI réelle (post-push)

**Run GitHub Actions : [28300352085](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/28300352085) — ✅ success (3/3 jobs verts)**

- [x] Job `pytest + QA scripts` — ✅ success
- [x] Job `lint (ruff budget + bandit + actionlint + shellcheck)` — ✅ success
- [x] Job `SonarCloud` — ✅ success

## 12. OQ à trancher avant Sb_31.1 (rappel)

| OQ | Question | Recommandation V1 |
|---|---|---|
| OQ-A | Route name | `/body` |
| OQ-B | CSS inline ou extrait | inline V1, extraire Sb_31.5 si > 200 l |
| OQ-C | Seuils arbre priorité | figés V1 |
| OQ-D | BMI inclus ? | oui avec disclaimer si height+weight présents |
| OQ-E | Overload compliance V1 ? | non, différé `Sb_31.next.overload-compliance` |
| OQ-F | Carte home V1 ? | non, différé `Sb_31.next.home-card` |
| OQ-G | `/profile` → `/body` lien | complément (pas de redirection) |

## 13. Hors scope confirmé (rappel)

- Photos / scans / morphotypes (track parallèle Body Signal Model)
- HealthKit / Health Connect / wearables (Sx_33+)
- PWA / service worker (Sx_32)
- Body composition (DEXA / impédance)
- Coach LLM
- React / SPA / bundler
- Score global numérique unique
- Mutation `profile_metrics`, `muscle_scoring`, `quality_score`, `implicit_signal`, `coach_report`, `radar`, `muscle_mapping`, `overload_*`, `substitution`, `recommendation`

## 14. Non-goals

Voir spec §P (rappel structurel).

## 15. Verdict

**✅ Sx_31 SPEC livrée. Prêt pour Sb_31.1 sous 3 conditions :**

1. **Trancher OQ-A → OQ-G** (§12 ci-dessus + spec §N.1).
2. **Confirmer build queue §9** (= spec §N.2).
3. **Bascule explicite `BUILD AUTHORIZED FOR Sx_31`** (override #4).

Sans ces 3 conditions : **NE PAS commencer le build Sb_31.1**. Cette spec reste un document d'alignement, et l'opérateur garde le contrôle de l'ouverture du cycle build.

Indépendamment :
- Dogfood Sx_30 reste pending (non bloquant pour Sx_31 SPEC, bloquant pour ouverture *automatique* d'un autre cycle).
- Sx_32 / Sx_33+ restent bloqués (override séparé requis pour chacun).
- Track parallèle Body Signal Model (`SPIGNOS_BODY_SIGNAL_MODEL_SPEC.md`) reste indépendant.
