# Sprint Sx_12 Report — Next-Session Recommendation Spec

**Date :** 2026-04-21
**Type :** SPEC ONLY — aucun code produit
**Branche :** `claude/sprint-reporting-fitness-app-V7Qr6` @ commit `d96d3e2`
**Livraison :** 2 documents (spec principale + ce rapport)
**Successeur :** Sb_12_next_session_recommendation_build

---

## 1. Surfaces inspectées

Lecture directe et via agent Explore ciblé des briques produisant un signal utile pour la recommandation :

### 1.1 Services

- [app/services/launcher.py](app/services/launcher.py) — `BRANCH_TREE` figé, 3 niveaux type/variant/template, **aucune logique contextuelle**.
- [app/services/muscle_mapping.py](app/services/muscle_mapping.py) — `classify_exercise(name)` retourne 11 zones canoniques + secondaires.
- [app/services/muscle_scoring.py](app/services/muscle_scoring.py) — `_compute_tonnage_by_zone` produit tonnage + hard_sets + session_count par zone sur fenêtre 30j par défaut. Pondération 30 % sur secondaires.
- [app/services/behavioral.py](app/services/behavioral.py) — `compute_behavioral_state` retourne `fatigue_score` (0–100), `streak_days`, `sessions_30d`, `trend_7d_vs_7d`.
- [app/services/stats.py](app/services/stats.py) — `last_time_by_exercise_code` **exo-level uniquement**, pas session-level par kind.
- [app/services/kpis.py](app/services/kpis.py) — `compute_template_kpis` : `count_completed`, `last_done_at`, `avg_success_score` par template.
- [app/services/quality_score.py](app/services/quality_score.py) — alias public `session_kind` (strength/cardio).

### 1.2 Modèles

- [app/models/session.py](app/models/session.py) — `WorkoutSession` avec index `ix_ws_user_status_excl_started` qui couvre la query type « 5 dernières completed ».
- [app/models/readiness.py](app/models/readiness.py) — 1 ligne / jour / user, `fatigue_level` + `soreness_level` **globaux, pas par zone**.
- [app/models/catalog.py](app/models/catalog.py) — `WorkoutTemplate` a `focus` (string), `kind`, `catalog_section`, `display_order`, `suggested_label`.

### 1.3 Surfaces UI

- [app/routers/pages.py](app/routers/pages.py) — `home` et `launcher` sont les deux points d'injection naturels.
- [app/templates/index.html](app/templates/index.html) — bloc `open_session` visible si session en cours, sinon un espace libre en haut.
- [app/templates/launcher.html](app/templates/launcher.html) — picker 3-step, remplaçable/complétable mais pas à refondre.

### 1.4 Catalogue (signaux indirects)

- [data/reference_split.json](data/reference_split.json) — 16 templates v12. Répartition :
  - core 6 (push-a, push-b, pull-a, pull-b, legs-a, legs-b)
  - utility 4 (liss-only, liss-abs, short-upper, short-lower)
  - specialization 3 (catch-up-shoulders, catch-up-arms, catch-up-back-width)
  - archived 4 (upper-pecs-delts, upper-back-arms, lower-quad-bias, lower-posterior-bias)

## 2. Briques existantes réutilisables

| Signal | Disponible | Qualité |
|--------|-----------|---------|
| Zone d'un exercice | `classify_exercise` | ★★★ — déjà testée par `catalog_qa` |
| Tonnage / hard sets par zone | `muscle_scoring` | ★★★ — juste élargir la fenêtre |
| Fatigue globale récente | `behavioral.fatigue_score` | ★★★ |
| Dernière occurrence d'un template | `compute_template_kpis.last_done_at` | ★★★ |
| Kind d'une session | `session_kind` | ★★★ |
| Activité cardio récente | dérivé de `session_kind` sur les N dernières sessions | ★★ — à composer |
| Staleness par zone sur 7j | **à construire** | — ajout V1 |
| Map template → zones primaires | **à construire** (cache applicatif) | — ajout V1 |

**Conclusion :** 70 % des briques sont déjà là. La recommandation exige principalement une **agrégation cible** (staleness 7j par zone) et une **map statique** (template → zones primaires). Aucune migration, aucune nouvelle source de données.

## 3. Ambiguïtés restantes

1. **Pondérations G2** — les 40/20/−15/15 de §H.3 sont un premier jet raisonnable, pas un optimum. Calibration post-dogfooding inévitable.
2. **Seuil spécialisation justifiée** — le ratio < 0.5 sur 14j est arbitraire. À ajuster si les catch-up ne se déclenchent jamais en pratique.
3. **Phrase d'explication** — risque de répétitivité sur quelques utilisations. Prévu pour V2 : pool de phrases alternatives par slot.
4. **Interaction reco ↔ briefing Sb_11a** — si l'utilisateur démarre la reco, le briefing s'applique dès la 1ʳᵉ carte. Pas de conflit attendu, pas de logique additionnelle requise.
5. **Readiness quotidienne** — volontairement non consommée V1. Hypothèse : `fatigue_score` behavioral suffit. Si le dogfooding montre le contraire, V2 peut mixer.

## 4. Arbitrages clés

### 4.1 Modèle choisi — G2 avec garde-fous G3

Scoring pondéré + filtre de sécurité. Compromis lisibilité / flexibilité. G1 trop rigide (mécanique), G3 seul trop sec (risque zéro candidat).

### 4.2 Pas de signal de retour utilisateur

V1 ne track pas si l'utilisateur accepte ou ignore la reco. Pas de learning loop. La reco s'adapte uniquement via l'historique de sessions réellement complétées.

### 4.3 Une seule fenêtre staleness — 7 jours

La fenêtre 30j de `muscle_scoring` est pertinente pour le radar, trop longue pour une décision « aujourd'hui ». 14j a été évalué mais double l'influence de séances déjà bien récupérées. 7j colle à la structure hebdo implicite.

### 4.4 Fallback toujours garanti

Jamais zéro recommandation. Cold start → Push A. Sinon → LISS. Documenté §H.4.

### 4.5 Home + Launcher, pas de nouvelle route

Deux points d'injection, un seul partial Jinja. Pas de page `/recommend` séparée — ce serait une fuite de scope.

## 5. Pourquoi ce chantier est le bon prochain saut de valeur

**Justification produit :**
- Toutes les briques analytiques sont en place (zones, fatigue, kinds, recency). Les **exposer produitement** est le maillon manquant.
- Le ratio valeur utilisateur / effort build est **très bon** : ~10h de build pour un signal visible dès la home de chaque utilisateur actif.
- Rend lisible **la donnée déjà collectée**. Autre chantier (programme-builder Sx_11b) demande 15–20h de build pour un bénéfice qui ne se déclenche qu'au moment où l'utilisateur créé un template custom (rare).
- Squad v2 (Sx_11c) est orthogonal à la valeur « moi, aujourd'hui, je fais quoi » — moins prioritaire.

**Justification technique :**
- Zéro migration, zéro IA, zéro dépendance, zéro refonte.
- Tests unitaires faciles à écrire avec fixtures contrôlées.
- Calibration post-dogfooding possible en changeant 4–5 constantes.
- Si le moteur s'avère mauvais, on peut le désactiver en un flag sans impact sur le reste du système.

**Justification timing :**
- Session System V1 est clos, les signaux sont stables, pas de sprint parallèle en concurrence.
- Le briefing Sb_11a a démontré qu'ajouter un signal léger au flow existant est digestible sans refonte.
- Ouvrir programme-builder maintenant (Sx_11b) alors que la reco est inexistante reviendrait à construire la sur-structure avant la colonne vertébrale.

## 6. Recommandation explicite du build suivant

**Sb_12 — Next-Session Recommendation build**, scope §L de la spec principale.

**Préconditions avant de lancer le build :**
- Branche V1 + Sb_11a mergée et stable.
- Micro-dogfooding Sb_11a validé (pas de FAIL critique/haute sur chip + peek).
- Paramètres numériques de §H.2 relus par l'utilisateur (possiblement ajustés avant le build).

**Effort estimé :** 8–12h.

**Valeur attendue :** un signal concret visible dès l'ouverture de `/`, qui répond à la seule question qui compte en ouvrant l'app : « je fais quoi aujourd'hui ? ».

**Risque de retour :** faible — le moteur est un signal additif, jamais bloquant. S'il déçoit, l'utilisateur ignore le bloc et utilise le picker. Pas de dégradation du flow existant.

**Sprint spec suivant probable :** Sx_13 à définir selon les priorités après Sb_12. Candidats naturels : calibration fine de la reco post-dogfooding (Sx_12.1), ou Sx_11b programme-builder utilisateur qui devient plus pertinent une fois la reco en place.

## 7. Livrables produits par ce sprint

| Fichier | Action |
|---------|--------|
| `docs/strategy/SPIGNOS_NEXT_SESSION_RECOMMENDATION_SPEC_v1.md` | New |
| `docs/SPRINT_Sx_12_next_session_recommendation_spec_REPORT.md` | New (ce rapport) |

Zéro code. Zéro migration. Zéro test.

## 8. Synthèse exécutive

- Moteur déterministe **G2 + garde-fous G3** retenu : scoring pondéré 4 composants sur templates candidats filtrés par règles de sécurité.
- **Zéro IA, zéro migration, zéro refonte.** 70 % des briques existent déjà (muscle_scoring, behavioral, classify_exercise, session_kind). Ajouts : staleness 7j, map template → zones, service recommandation.
- **UX home + launcher** : bloc « Prochaine séance suggérée » au-dessus des existants, phrase d'explication en 1 ligne, 2 alternatives dans `<details>`.
- **Explicabilité via slots** : 8 signaux primaires + 4 raisons de template → phrase composable ≤ 140 chars, neutre factuelle.
- **10 cas particuliers traités** : cold start, fatigue haute, cardio absent, programme custom futur, etc.
- **Build suivant recommandé : Sb_12** (8–12h), préconditions explicites, critères d'acceptation chiffrés.
