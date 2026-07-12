# Sx_BI_01 — Body Intelligence Activation Spec

**Type** : SPEC / cadrage — docs-only, **aucun code**.
**Date** : 2026-07-11
**Statut** : 🟢 SPEC LIVRÉE — READY FOR HUMAN DECISION
**Précondition** : `Sx_DOGFOOD_01` CLOSED (dogfooding terrain repoussé → on avance le cadrage BI).
**Audit associé** : [`SPRINT_Sx_BI_01_BODY_INTELLIGENCE_ACTIVATION_AUDIT_REPORT.md`](../SPRINT_Sx_BI_01_BODY_INTELLIGENCE_ACTIVATION_AUDIT_REPORT.md)

---

## 0. Constat de départ (issu de l'audit)

**Body Intelligence n'est PAS un greenfield.** Le repo contient déjà, issus des
cycles Sx_31 (composer) et Sx_32 (zones/mapping) :

| Surface | État réel | Visibilité |
|---|---|---|
| `/body/intelligence` (composer riche : 7 blocs, priorités, confidence, limits non-médicaux) | Implémenté (Sb_31.1/.2/.3) | **flag-off** (`body_intelligence_enabled=False`) → 404 en prod |
| `/physique` (dashboard `muscle_scoring.py` : score global **A/B/C opaque** + radar SVG + 11 zones) | Implémenté, **LIVE** (pages.py:478) | visible |
| `/progress` (historique, KPI, timelines) | LIVE | visible |
| `/dashboard` | **DEPRECATED** (Sb_27.6) | — |
| Modèles Sx_32 : BodyZone (11 zones seedées), ExerciseMuscleMapping (91 exos backfillés), Muscle (**vide** par design) | Implémentés | données réelles |
| `body_map_descriptor` (Sb_32.3) | Implémenté **et câblé** (Worked Area, `sessions.py:332`) | visible dans la séance |
| `/body` (Manual Profile + mesures + consent) | Implémenté | **flag-off** (`body_assessment_enabled=False`) |
| `/profile` → lien vers `/body/intelligence` | Existant (Sb_31.next.profile_link) | mène à une page flag-off |

**Tension centrale à trancher** : il existe **déjà** un score global opaque (A/B/C
sur `/physique`, LIVE) qui **contredit** le principe produit « pas de score global
opaque en premier ». La reprise BI ne doit pas ajouter un second score opaque —
elle doit **offrir une lecture par zones traçable et confidence-aware**, qui soit
la porte d'entrée sobre, et reléguer/encadrer le score global.

---

## 1. Objectif Sx_BI_01

Définir **le prochain build Body Intelligence utile, sobre et compatible** avec
l'état actuel — **sans coder**. La spec fixe :
- l'angle V1 (**Option A — Zone Intelligence Cards**, drillable, confidence-aware,
  non médical) ;
- comment il se positionne face à `/physique` (score global existant) et au
  composer `/body/intelligence` (flag-off) ;
- la séparation stricte **signal réel / estimation / donnée absente** ;
- le périmètre build minimal futur (`Sb_BI_01.1`) et ses critères d'acceptation.

---

## 2. Étape 0 — Brainstorming / Options / Risques / Choix retenu

### 2.1 Options comparées

| Option | Description | Verdict |
|---|---|---|
| **A** | **Zone Intelligence Cards V1** — cards par zone (volume récent, tendance, contribution, confidence, mention non-médicale, drill vers détail). Pas de radar opaque. | ✅ **RETENU** |
| B | Radar / hexagone synthétique | ❌ **niveau 2** — effet visuel fort mais opacité si score immature ; garder comme visualisation secondaire (le radar SVG existe déjà sur `/physique`) |
| C | Home widget | ❌ **différé** — risque de re-densifier la home juste nettoyée (Sx_UI_06) ; sauf mini-signal très sobre |
| D | Full Body Intelligence dashboard | ❌ **rejeté V1** — trop large, risque de recréer un cockpit lourd |

**Choix retenu : Option A** — Body Intelligence **par zones**, drillable,
confidence-aware, non médical. **Pas de score global opaque en premier.**

### 2.2 Sujets clivants tranchés

| # | Sujet | Décision |
|---|---|---|
| 1 | Page dédiée / widget Home / insight post-séance ? | **Page dédiée** (réutiliser/reprendre `/body/intelligence`, déjà routée + liée depuis `/profile`). Pas de widget Home V1 (Sx_UI_06 vient de dé-densifier). Insight post-séance = piste future. |
| 2 | Score global d'abord ou zones ? | **Zones d'abord.** Le score global A/B/C existe déjà sur `/physique` (opaque) ; on ne le reproduit pas — on offre la lecture traçable par zone comme entrée. |
| 3 | Radar / carte musculaire / cards par zone ? | **Cards par zone.** Radar = niveau 2 (déjà présent sur `/physique`, on ne le met pas en avant V1). Carte musculaire = piste future (body_map_descriptor existe mais V1 reste textuel/cards). |
| 4 | Score volume / progression / consistency / composite ? | **Traçable, pas de score composite opaque.** Chaque card montre des **chiffres sources** : volume récent (hard sets/semaine), tendance (↑/↓/→ vs fenêtre précédente), contribution (part de la zone dans le volume total). Pas de note /100 mise en avant en V1. |
| 5 | Éviter les faux positifs (poids / mensurations / substitutions) ? | **Substitution-aware par héritage** : le volume par zone s'appuie sur `classify_exercise` / `ExerciseMuscleMapping` (identité d'exercice) ; on réutilise la discipline « silence plutôt que faux poids » de Sx_DOGFOOD_01. **Mensurations = signal séparé, jamais mélangé au volume** (classe « measured » distincte de « derived »). |
| 6 | Distinguer signal réel / estimation / manque de données ? | **3 classes explicites** (déjà dans le composer) : `measured` (mesure saisie), `derived` (calculé depuis du réel : volume, ratios), `inferred` (heuristique : patterns), + `not_deductible` (composition/esthétique/médical). Chaque card porte sa classe. |
| 7 | Confidence score affiché ? | **Oui, par zone** (`muscle_scoring` a déjà « élevée / moyenne / faible » basé sur nb de signaux). Affiché comme **badge sobre**, pas comme un %. |
| 8 | Signaux primaires vs dérivés ? | **Primaires** : volume par zone (hard sets/reps/weight depuis SetLog via mapping). **Dérivés** : tendance, contribution, ratios push/pull & upper/lower. **Inférés** : dominant pattern. **Mesurés (séparés)** : circonférences. |
| 9 | Fenêtre V1 : 30 / 60 / 90 j ? | **30 jours par défaut** (cohérent avec le composer et `muscle_scoring`), sélecteur 30/60/90 possible en V2 (déjà présent sur `/physique`). |
| 10 | BodyZone / Muscle / ExerciseMuscleMapping sans sur-vendre ? | **Utiliser BodyZone (11 zones seedées) + ExerciseMuscleMapping (91 exos)**. **Muscle reste vide** (pas d'anatomie fine inventée — OQ-32 déjà tranchée). Les zones inconnues → « À qualifier », jamais une zone inventée. |
| 11 | Lien avec readiness ? | **Aucun en V1.** La table readiness existe mais n'est pas intégrée ; ne pas la brancher (éviter la sur-lecture). Piste future. |
| 12 | Lien avec recommandations de séance ? | **Aucun couplage nouveau en V1.** Les zones sous-travaillées sont déjà signalées par le composer (`undertrained_zone`) ; on n'ajoute pas de reco automatique. |
| 13 | Ce qui reste non médical ? | **Tout.** Aucune composition corporelle, aucun body-fat, aucune posture, aucun diagnostic. Les `DEFAULT_LIMITS` du composer sont conservés et affichés. Wording garde `FORBIDDEN_WORDING` de `body_profile`. |
| 14 | Interdit tant que pas assez de données ? | **Silence** : une zone sans volume suffisant → « Données insuffisantes » (pas de score inventé). Statut `insufficient_data` déjà géré. Seuils : réutiliser `MIN_SESSIONS_OK=3`. |
| 15 | Build minimal après spec ? | **`Sb_BI_01.1` — Zone Intelligence Cards** (voir §5). |

### 2.3 Risques / parades

| Risque | Parade |
|---|---|
| Ajouter un 2e score opaque en plus de `/physique` | V1 = **cards traçables**, pas de note /100 mise en avant ; chaque chiffre est sourcé |
| Fausse intelligence sur peu de données | Statut `insufficient_data` + confidence badge par zone + **silence** si volume < seuil |
| Contamination substitution (charge d'un autre exercice attribuée à une zone) | Volume par zone via **identité d'exercice** (mapping), héritage de la discipline Sx_DOGFOOD_01 |
| Mélange mensurations ↔ volume | **Classes séparées** (`measured` vs `derived`) ; jamais additionnées |
| Re-densifier la home | **Pas de widget Home V1** (Option C différée) |
| Sur-vendre l'anatomie (Muscle vide) | Rester au niveau **zone** ; Muscle reste vide ; inconnu → « À qualifier » |
| Réveiller le score A/B/C opaque de `/physique` | Ne pas le mettre en avant ; V1 pointe vers les cards par zone |

---

## 3. Proposition V1 — Zone Intelligence Cards

**Surface** : reprise de la page `/body/intelligence` (déjà routée, liée depuis
`/profile`, flag-gated). L'activation V1 = rendre une **section « Zones »** de
cards lisibles, **en amont** des blocs existants du composer.

**Chaque card de zone affiche** (tous les chiffres traçables, aucune note opaque
en tête) :
- **zone** (label FR, ex. « Pectoraux ») — parmi les 11 zones seedées ;
- **volume récent** : hard sets/semaine sur 30 j (source : SetLog work sets via mapping) ;
- **tendance** : ↑ / → / ↓ vs la fenêtre précédente (source : delta de tonnage/volume) ;
- **contribution** : part de la zone dans le volume total 30 j (%) ;
- **confidence** : badge sobre « élevée / moyenne / faible » (nb de signaux) ;
- **classe** : `derived` (volume) — la mesure corporelle éventuelle est une ligne
  `measured` **séparée**, jamais fusionnée ;
- **mention** : « Estimation indicative, non médicale. » ;
- **drill** : lien vers le détail de la zone (top exercices, historique volume) —
  réutilise les données déjà calculées par `muscle_scoring` (`top_exercises`, etc.).

**États de silence** :
- zone sans volume 30 j → « Données insuffisantes » (pas de tendance inventée) ;
- moins de `MIN_SESSIONS_OK` (3) séances → statut global `insufficient_data`,
  cards masquées ou grisées avec message.

**Ce que V1 NE fait PAS** :
- pas de radar mis en avant (niveau 2, déjà sur `/physique`) ;
- pas de score global /100 ni A/B/C en tête ;
- pas de widget Home ;
- pas de couplage readiness / reco ;
- pas de carte musculaire graphique (textuel/cards V1) ;
- pas d'anatomie fine (Muscle reste vide).

---

## 4. Non-goals stricts (spec)

- **pas de code** (ce sprint = spec/audit docs-only) ;
- **pas de modèle** (BodyZone/Muscle/ExerciseMuscleMapping/Measurement inchangés) ;
- **pas de migration** ;
- **pas de score nouveau** (on réutilise les signaux existants ; pas de note composite opaque) ;
- **pas de changement home** (index.html intact) ;
- **pas de changement session** (flux de séance intact) ;
- **pas de JS** (SSR/Jinja only) ;
- **pas de deploy** ;
- **pas de release tag** ;
- **pas de claims médicaux** ; **pas de « diagnostic corporel »** ;
- pas de branchement readiness ni de reco automatique V1 ;
- Muscle table reste **vide** (aucune anatomie fine inventée).

---

## 5. Build minimal futur — Sb_BI_01.1 — Zone Intelligence Cards

**Périmètre build (à ouvrir sur GO séparé, hors de ce sprint)** :
- reprendre `/body/intelligence` : ajouter une **section « Zones »** de cards en
  tête, alimentée par les signaux **déjà calculés** (`muscle_scoring` / composer) ;
- réutiliser `compute_physique_dashboard` (`ZoneScore` : `hard_sets`,
  `session_count`, `trend`, `confidence`, `top_exercises`) **sans recalcul** ni
  nouveau score composite mis en avant ;
- template `body_intelligence.html` + un partial `_partials/zone_intelligence_card.html` ;
- CSS `body_intelligence.css` (existant) — mobile-first, pas de nouveau framework ;
- décision d'activation du flag `body_intelligence_enabled` : **à trancher au build**
  (rester flag-gated jusqu'à validation, ou activer derrière la revue).

**Chaque card = zone / volume récent / tendance / contribution / confidence /
mention estimation non médicale / drill vers détail. Pas de radar opaque en V1.**

### 5.1 Critères d'acceptation du futur build

- **mobile-first** ;
- **SSR / Jinja** ; **pas de React** ; **pas de JS** ;
- **pas de score opaque** (aucune note /100 ni A/B/C en tête de card) ;
- **chaque chiffre doit être traçable** (volume = hard sets réels ; tendance = delta sourcé) ;
- **confidence visible** (badge par zone) ;
- **silence si données insuffisantes** (jamais de valeur inventée) ;
- **aucune recommandation médicale** ;
- **aucune promesse de transformation physique** ;
- substitution-aware par héritage (identité d'exercice) ;
- mensurations en classe `measured` séparée du volume `derived`.

---

## 6. Build split recommandé (au-delà de V1)

| Sprint | Contenu | Statut |
|---|---|---|
| **Sb_BI_01.1** | Zone Intelligence Cards (§5) — reprise `/body/intelligence`, cards par zone traçables, confidence-aware | 🟡 à proposer sur GO |
| Sb_BI_01.2 | Drill zone → détail (top exercices, historique volume par zone) | futur |
| Sb_BI_01.3 | Radar en niveau 2 (visualisation secondaire, encadrer/relier au score `/physique` existant) | futur |
| Sb_BI_01.next | Décision produit sur le score global A/B/C de `/physique` (garder / encadrer / déprécier) | à cadrer |
| Différé | Home widget (Option C), insight post-séance, couplage readiness/reco, carte musculaire graphique, activation `/body` Manual Profile | deferred |

---

## 7. Verdict

**Verdict :** 🟢 **Sx_BI_01 Body Intelligence Activation — SPEC LIVRÉE, READY FOR HUMAN DECISION.**

La reprise Body Intelligence se cadre sur un système **déjà riche mais flag-off**
(composer `/body/intelligence`) coexistant avec un **score global opaque LIVE**
(`/physique`). L'angle V1 retenu — **Option A, Zone Intelligence Cards** — offre
une lecture **par zones, traçable, confidence-aware et non médicale**, sans ajouter
de second score opaque, sans toucher la home ni la séance, en réutilisant les
signaux déjà calculés (`muscle_scoring`) et les fondations Sx_32 (zones + mapping,
Muscle vide). Build minimal futur : **`Sb_BI_01.1`**. Aucun code, modèle, migration,
JS, deploy ou claim médical dans ce sprint. Prochaine décision : GO (ou ajustement
d'angle) avant d'ouvrir `Sb_BI_01.1`.
