# Sprint Sx_BI_01 — Body Intelligence Activation (AUDIT)

**Statut** : 🟢 AUDIT COMPLET — READY FOR HUMAN DECISION
**Type** : AUDIT / SPEC ONLY — docs-only, **aucun code, aucun modèle, aucune migration**
**Date** : 2026-07-11
**Spec cible** : [`strategy/Sx_BI_01_BODY_INTELLIGENCE_ACTIVATION_SPEC.md`](strategy/Sx_BI_01_BODY_INTELLIGENCE_ACTIVATION_SPEC.md)

---

## 0. Méthode

Audit **read-only** (aucun fichier modifié) des surfaces Body Intelligence,
physique, muscle mapping, mesures et de leurs consommateurs / tests. Objectif :
établir un état des lieux factuel **avant de spécifier la reprise**. Conclusion
majeure : **Body Intelligence n'est pas un greenfield** — le socle existe (Sx_31 +
Sx_32) mais est majoritairement **flag-off**.

---

## 1. État actuel des surfaces Body Intelligence

| Surface | Fichier(s) | État | Visibilité prod |
|---|---|---|---|
| **Composer BI v2** (`/body/intelligence`) | `routers/body_intelligence.py`, `services/body_intelligence.py` (pur), `body_intelligence_inputs.py` (I/O), `body_intelligence.html` + 2 partials, `body_intelligence.css` | Implémenté (Sb_31.1/.2/.3) : 7 blocs, priorités (max 3), status, headline, bullets, limits non-médicaux | **flag-off** `body_intelligence_enabled=False` → 404 |
| **Dashboard physique** (`/physique`) | `pages.py:478`, `services/muscle_scoring.py`, `physique.html` | Implémenté, **LIVE** : score global **A/B/C opaque** + `global_score` + radar SVG + 11 zones (perf+exposure+anthropo) + confidence par zone | **visible** |
| **Progress** (`/progress`) | `pages.py:413`, `progress.html` | LIVE : historique, KPI, timelines qualité + poids | visible |
| **Dashboard** (`/dashboard`) | `pages.py:502` | **DEPRECATED** (Sb_27.6) | — |
| **Coach snapshot BI** | `_partials/coach_body_snapshot.html` (Sb_31.3) | Compact BI dans `/coach-report`, lien vers `/body/intelligence` | selon coach-report |
| **Manual Profile** (`/body`) | `routers/body.py`, `services/body_profile.py`, `body_assessment/*.html` | Mesures manuelles + consent granulaire + 6 ratios dérivés | **flag-off** `body_assessment_enabled=False` |
| **Capture quality** (`/body/capture-quality`) | `routers/body_capture.py` | Shell placeholder (pas de caméra) | **flag-off** |
| **Body map descriptor** | `services/body_map_descriptor.py` (Sb_32.3) | Implémenté **ET câblé** : Worked Area (`sessions.py:332` → `exercise_card.html:122`) | **visible en séance** |
| **Lien profil** | `profile.html:20` | Lien sobre `/profile → /body/intelligence` (Sb_31.next.profile_link) | mène à une page flag-off |

---

## 2. Données disponibles aujourd'hui (signal réel)

Toutes issues de modèles persistés réels (aucune invention, aucun provider externe) :

| Signal | Source | Fenêtre | Classe |
|---|---|---|---|
| Volume par exercice (weight_kg, reps) | `SetLog` (work sets, `completed`) | par set → agrégable | primaire |
| Classification exercice → zone | `ExerciseMuscleMapping` (91 exos backfillés) + fallback `classify_exercise` | — | primaire |
| Comptage séances par zone (11 zones) | `zone_session_counts` (profile_metrics) | 30/90 j | dérivé |
| Consistance (séances 7/30/90 j) | `WorkoutSession` (completed, hors `excluded_from_stats`) | 7/30/90 j | dérivé |
| Work sets / semaine | `_work_sets_per_week` (coach_report) | 30 j | dérivé |
| Delta volume force % | `strength_volume_delta_pct` | 30 j vs historique | dérivé |
| Quality score moyen | `compute_session_quality` (min 3 échantillons) | 30 j | dérivé |
| Confidence score moyen | `compute_confidence_score` | 30 j | dérivé |
| Labels implicites | `SessionExercise.implicit_label` (figé à la complétion) | 30 j | inféré |
| Poids corporel + tendance 90 j | `BodyMeasurement.weight_kg` ∪ `WorkoutSession.bodyweight_kg` | série + 90 j | mesuré |
| Circonférences (poitrine, bras, taille, cuisse, épaules, mollets…) | `BodyMeasurement.*_cm` (saisie manuelle) | latest + série | mesuré |
| Ratios push/pull & upper/lower | `body_intelligence` (depuis zone counts) | 30 j | dérivé |
| BMI | `_bmi` (si height ET weight présents) | latest | dérivé (jamais « measured ») |
| Dominant pattern + distribution | profile_metrics | 30 j | inféré |
| Score physique A/B/C + radar | `muscle_scoring.compute_physique_dashboard` | 30/60/90 j | **dérivé mais présenté de façon opaque** |

---

## 3. Données absentes (aucune source)

| Signal absent | Raison |
|---|---|
| Body fat % | pas de DEXA / impédance / caliper |
| Masse musculaire | pas de DEXA / imagerie |
| Posture / symétrie réelle | pas de photo / motion capture |
| Calories cardio vérifiées | valeurs machine déclaratives seulement |
| Diagnostic / évaluation clinique | SPIGNOS n'est pas un outil médical |
| Verdict esthétique / composition | pas de photo, pas de service externe |
| Overload compliance | explicitement **différé** (`Sb_31.next.overload-compliance`) |
| Anatomie musculaire fine | table `Muscle` **vide** par design (OQ-32) |
| Readiness intégrée à BI | table readiness existe mais **non branchée** à BI |
| Données provider externe | shell capture inactif |

---

## 4. Consommateurs existants

| Consommateur | Ce qu'il lit |
|---|---|
| `/body/intelligence` (composer) | tous les signaux dérivés/inférés/mesurés ci-dessus → 7 blocs + priorités |
| `/physique` (`muscle_scoring`) | volume par zone (SetLog via `classify_exercise`) + mesures + score A/B/C + radar |
| `/coach-report` (`coach_body_snapshot`) | headline + bullets + priorités du composer |
| Worked Area (séance) | `body_map_descriptor` (zone primaire/secondaires, resolution_path) |
| `leaderboard.py` | `compute_physique_dashboard` (comparaison sociale) — **couplage à noter** |

---

## 5. Risques de fausse lecture (identifiés)

| Risque | Où | Mitigation V1 (spec) |
|---|---|---|
| **Second score opaque** ajouté au-dessus de `/physique` A/B/C | tension centrale | V1 = **cards traçables**, pas de note en tête |
| Fausse intelligence sur peu de données | toute surface BI | statut `insufficient_data` + confidence badge + **silence** |
| Contamination substitution (charge d'un autre exo → mauvaise zone) | volume par zone | identité d'exercice (mapping), héritage discipline Sx_DOGFOOD_01 |
| Mensurations mélangées au volume | cards zone | classes **séparées** `measured` vs `derived` |
| Sur-vente anatomie (Muscle vide) | mapping | rester **au niveau zone** ; inconnu → « À qualifier » |
| Score A/B/C de `/physique` réveillé comme entrée BI | `/physique` LIVE | ne pas le mettre en avant ; V1 pointe vers les cards |
| Re-densifier la home (juste nettoyée Sx_UI_06) | Home widget | **pas de widget Home V1** |
| Couplage `leaderboard` ↔ `compute_physique_dashboard` | social | ne pas modifier `muscle_scoring` en V1 (réutilisation lecture seule) |

---

## 6. Confidence / non-médical déjà en place (à conserver)

- **Composer** `DEFAULT_LIMITS` (5 disclaimers : composition/esthétique/posture/cardio/médical non déductibles) — rendus sur la page.
- **`body_profile.FORBIDDEN_WORDING`** : bloque diagnostic, pathologie, body fat, morphotype, ethnie, attractivité… (verrouillé par tests).
- **Confidence** par zone dans `muscle_scoring` (« élevée / moyenne / faible » selon nb de signaux) ; **status** BI (`insufficient_data` / `partial_data` / `ok`) ; **classes** `measured / derived / inferred / not_deductible`.
- **Templates** : « guidance esthétique non médicale », « signaux dérivés recalculables », « — » si non calculable, BMI toujours étiqueté dérivé.

→ La V1 **réutilise** ce socle : aucune nouvelle règle non-médicale à inventer, on
l'applique aux cards de zone.

---

## 7. Proposition V1 (résumé — détail dans la spec)

**Option A — Zone Intelligence Cards** sur `/body/intelligence` (reprise) :
cards par zone (volume récent / tendance / contribution / confidence / mention
non-médicale / drill), **sans radar opaque**, **sans score global en tête**,
mobile-first SSR, silence si données insuffisantes. Réutilise les signaux déjà
calculés (`muscle_scoring` `ZoneScore`) — pas de nouveau score composite.

---

## 8. Non-goals (rappel)

Pas de code / modèle / migration / score nouveau / changement home / changement
session / JS / deploy / release tag / claim médical / diagnostic corporel. Muscle
reste vide. Readiness et reco non branchées V1.

---

## 9. Build split recommandé

| Sprint | Contenu | Statut |
|---|---|---|
| **Sb_BI_01.1** | Zone Intelligence Cards (reprise `/body/intelligence`) | 🟡 à proposer sur GO |
| Sb_BI_01.2 | Drill zone → détail (top exercices, historique volume) | futur |
| Sb_BI_01.3 | Radar niveau 2 (encadrer le score `/physique`) | futur |
| Sb_BI_01.next | Décision produit sur le score A/B/C de `/physique` (garder / encadrer / déprécier) | à cadrer |
| Différé | Home widget, insight post-séance, readiness/reco, carte graphique, activation `/body` | deferred |

---

## Verdict

**Verdict :** 🟢 **Sx_BI_01 Body Intelligence Activation — AUDIT COMPLET, READY FOR HUMAN DECISION.**

Body Intelligence est un socle **déjà implémenté mais flag-off** (`/body/intelligence`)
qui coexiste avec un **score global opaque LIVE** (`/physique` A/B/C). L'audit
établit précisément les données réelles disponibles (volume par zone, consistance,
qualité/confidence, mensurations) vs absentes (composition, posture, médical) et
les consommateurs existants. La spec `Sx_BI_01` retient **l'Option A — Zone
Intelligence Cards** : lecture par zones traçable, confidence-aware, non médicale,
sans second score opaque, réutilisant le socle existant. Build minimal futur :
**`Sb_BI_01.1`** (à ouvrir sur GO séparé). Aucun code touché par ce sprint.
