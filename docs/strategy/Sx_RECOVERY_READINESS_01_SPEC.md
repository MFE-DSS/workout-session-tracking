# Sx_RECOVERY_READINESS_01 — Contrat sémantique canonique : readiness, fatigue, récupération, disponibilité

**Statut : SPEC ONLY.** Aucun code runtime n'est produit par ce document, et **aucun build n'est
autorisé par lui**. Chaque tranche du §11 exige un `GO BUILD` explicite.

**Base canonique :** `879d41d` · **Autorité primaire :**
[`Sx_AUREN_ORCHESTRATOR_01_GAP_CONSOLIDATION_SPEC.md`](Sx_AUREN_ORCHESTRATOR_01_GAP_CONSOLIDATION_SPEC.md)
(§C.0, §C.2, §D, §E, §G) · **Contexte produit secondaire :** blueprint opérateur
« Évolution d'AUREN vers un orchestrateur d'entraînement personnel ».

> **Statut du blueprint.** Ses idées cardio/récupération sont une **intention produit**, pas une
> vérité physiologique. En cas de tension entre le blueprint et les garde-fous scientifiques
> canoniques (§8), **les garde-fous l'emportent**. Ce document dit ce qu'on a le droit d'affirmer,
> pas ce qu'on aimerait pouvoir afficher.

**Ce que ce contrat n'est pas :** un score de plus. Le but est que l'orchestration future dépende
d'**un modèle sémantique explicite et traçable**, au lieu des 5 calculs indépendants et 6+ échelles
qui coexistent aujourd'hui.

---

## 1. Inventaire des signaux vivants — audit du CODE ACTIF

Méthode : lecture du code actif au SHA `879d41d`, pas des anciens rapports. Quand un rapport et le
code divergent, **le code fait foi**. Chaque ligne ci-dessous a été vérifiée à la source.

### 1.1 Matrice de source de vérité

| # | Signal | Producteur | Sens sémantique | Échelle | Direction | Persisté | Fenêtre | Données manquantes | Consommateurs | Décide ou affiche ? |
|---|---|---|---|---|---|---|---|---|---|---|
| S1 | `ReadinessEntry.{sleep_quality, fatigue_level, soreness_level, stress_level, motivation_level}` | Formulaire utilisateur (`routers/readiness.py`) | **Déclaratif subjectif du jour** | **1–5** | **5 = meilleur état** (donc `fatigue_level=5` ⇒ « Très frais ») | **OUI** (`readiness_entries`, 1 ligne / user / jour calendaire) | Le jour même | Ligne absente = pas d'entrée ; validation stricte 1–5 à l'écriture | `pages.py:150` (affichage), `pages.py:544` (historique 90 j), `dashboard.compute_recovery_axis` | **Affiche + décide** (via S2) |
| S2 | `dashboard.compute_recovery_axis` → `AxisScore(key="recovery")` | Dérivé de S1 | Axe « Récupération » du tableau de bord | **0–100** | Plus haut = mieux | Non (dérivé) | Moyenne des entrées **7 j**, portail ≥ **5 entrées / 30 j** | **Explicite et exemplaire** : `< 5` entrées ⇒ `active=False`, `confidence="insuffisante"`, `score=0` + `guidance` | Tableau de bord | **Affiche** |
| S3 | `behavioral.fatigue_score` | `compute_weighted_fatigue` sur les **3 dernières séances complétées** | Fatigue accumulée **subjective** | **0–100** | **Plus haut = plus fatigué** | Non | 3 dernières séances (pas une fenêtre temporelle) | Aucune séance ⇒ **50.0** (défaut « plat ») | `behavioral.compute_recommendation`, `recommendation.build_signals`, `profile.html` | **Décide** |
| S4 | `behavioral.readiness_score` | `0.5·(100−fatigue) + 0.3·consistency + 0.2·performance` | « Readiness » **calculée** | **0–100** | Plus haut = mieux | Non | Hérite de S3 / S5 / S6 | Hérite | `compute_recommendation` (bandes ≥ 80 / ≥ 50), `index.html` KPI | **Décide + affiche** |
| S5 | `behavioral.consistency_score` | `min(100, sessions_14d / 14 × 100)` | Régularité | **0–100** | Plus haut = mieux | Non | **14 j** | 0 séance ⇒ 0.0 (légitime) | S4 | Indirect |
| S6 | `behavioral.performance_score` | `compute_composite_score(quality, completion_ratio)` de la **dernière** séance | Performance récente | **0–100** | Plus haut = mieux | Non | 1 séance | Aucune séance ⇒ 0.0 | S4 | Indirect |
| S7 | `recommendation.availability_by_zone` | `clamp(hours_since_last / RECOVERY_HOURS_TARGET[zone], 0, 1)` | **Aptitude d'entraînement par zone** | **0.0–1.0** | Plus haut = plus disponible | Non | 14 j de lookback | **Jamais entraînée ⇒ `1.0`** | Scoring `recommendation` (poids 35) | **Décide** |
| S8 | `recommendation.hours_since_last_by_zone` | Delta horaire depuis le dernier travail de la zone | Ancienneté par zone | **heures** | Plus haut = plus ancien | Non | 14 j | **Jamais ⇒ `24 × 365`** | S7, explications | Indirect |
| S9 | `RECOVERY_HOURS_TARGET` | Constante littéraire (Schoenfeld, Helms, Heaselgrave, Krieger) | Cible de récupération par **zone détaillée** | heures (24–72) | — | Non (code) | — | Zone inconnue ⇒ défaut **48** | S7 | **Décide** |
| S10 | `recommendation.days_since_last_cardio` / `_strength` | Delta jours par `kind` | Ancienneté par modalité | **jours** \| `None` | Plus haut = plus ancien | Non | 14 j | `None` explicite | Scoring, `recommendation_explainer` (règle D) | **Décide** |
| S11 | `Signals.fatigue_score` | Recopie S3 | Fatigue transmise au moteur | **0–100** | Plus haut = plus fatigué | Non | Hérite | **Exception ⇒ `0.0`** (sentinelle d'échec) | `_passes_fatigue_filter`, `context` | **Décide** |
| S12 | `ZONE_FRESHNESS_BONUS_{BASE,STEP,MIN}` | Recouvrement avec l'union des zones des **3 dernières** séances strength | Fraîcheur de zone à court terme | **points de score** (15 / −6 / min −6) | Plus haut = plus frais | Non | 3 dernières séances strength | Pas de séance ⇒ pas de bonus | Scoring `recommendation` | **Décide** |
| S13 | `recommendation_explainer.normalize_fatigue_score` | Conversion 0–100 → 0–1 | **Seule conversion d'échelle explicite et nommée du repo** (livrée par `Sb_FATIGUE_SCALE_FIX_01`) | **0.0–1.0** | Plus haut = plus fatigué | Non | — | `None` = « pas de lecture exploitable » ; plancher productible 15 ⇒ rejette la sentinelle `0.0` | `_fatigue_reason` | **Décide (texte)** |
| S14 | `WorkoutSession.{cardio_duration_min, cardio_bpm_avg, cardio_machine_calories, cardio_machine_type}` | Saisie utilisateur | Charge cardio brute | min / bpm / kcal / texte(32) | — | **OUI** (tous **nullable**) | Par séance | `None` partout, aucun champ obligatoire | `export_builder`, `session_recap` (affichage), `profile_metrics.cardio_minutes_per_week`, `coach_inference` (seuil OMS) | **Affiche uniquement** |
| S15 | `WorkoutSession.{global_state, concentration}` | Saisie post-séance | Ressenti subjectif de séance | catégoriel `String(16)` nullable — `{fatigued, flat, good}` / `{low, medium, high}` | Vocabulaire fermé | **OUI** | Par séance | `None` ⇒ défauts 50 / 40 dans S3 | S3 | **Décide** |
| S16 | `available_equipment` (`program_quality_engine`), `availability` (`morpho_program_generator`) | Profil de salle / appel | **Familles d'équipement disponibles** | `tuple[str, ...]` \| `None` | — | Non | — | `None` = pas de contrainte | Générateur morpho, moteur qualité | **Décide** |
| S17 | `{"available": bool}` (`home.py`, `session_review.py`, `weekly_loop.py`, `recommendation_explainer`) | Composeurs de surface | **Ce bloc d'UI est-il affichable** | booléen | — | Non | — | Exception ⇒ `available: False` + `error_type` | Templates | **Affiche** |

### 1.2 Les six constats qui motivent ce contrat

**C1 — Deux « readiness » qui ne se rencontrent jamais.** S1 (déclaratif, 1–5, persisté, un
questionnaire que l'utilisateur remplit) et S4 (calculée, 0–100, dérivée de la charge) portent le
même mot. **S1 n'alimente aucune décision d'entraînement** : elle ne sort pas du tableau de bord et
de sa page d'historique. Le moteur de recommandation ne la lit pas. L'utilisateur qui déclare
« épuisé » ce matin reçoit la même recommandation que s'il avait déclaré « très frais ».

**C2 — Le mot « fatigue » change de direction selon l'endroit.** `ReadinessEntry.fatigue_level = 5`
signifie **« Très frais »** (plus haut = moins fatigué). `behavioral.fatigue_score = 80` signifie
**« fatigué »** (plus haut = plus fatigué). Deux champs, un mot, **directions opposées**, aucune
conversion nommée entre eux.

**C3 — « Availability » désigne quatre choses différentes.** Aptitude biologique par zone (S7),
équipement disponible (S16), **affichabilité d'un bloc d'UI** (S17), et — absente du code —
disponibilité d'agenda. Les trois premières coexistent aujourd'hui dans le même vocabulaire.

**C4 — Deux *fail-open* structurels subsistent.** Une zone **jamais entraînée** obtient
`availability = 1.0`, c'est-à-dire « parfaitement disponible » : l'absence de donnée est rendue
comme la meilleure donnée possible. Et `Signals.fatigue_score = 0.0` sur exception reste produit —
`Sb_FATIGUE_SCALE_FIX_01` a neutralisé sa **lecture** côté explainer (plancher productible 15),
mais le producteur ment toujours à quiconque le lira sans passer par `normalize_fatigue_score`.

**C5 — Le cardio est une île.** Quatre champs persistés (S14) et **zéro contribution** à la
fatigue, à la readiness ou à la disponibilité. Une heure de vélo n'a aucun effet sur ce que l'app
recommande le lendemain pour les jambes.

**C6 — `RECOVERY_HOURS_TARGET` est un 4ᵉ exemplaire du dictionnaire des 11 zones**, et `BodyZone`
n'a **aucune colonne** capable de le porter. `Sb_32.4` a fait de `ExerciseMuscleMapping`/`BodyZone`
la source de vérité pour *l'attribution* d'un exercice à une zone ; les *paramètres de
récupération* de ces zones restent, eux, en dur dans `recommendation.py` — c'est-à-dire dans le
fichier non modifiable.

### 1.3 Ce qui est déjà bien fait (à ne pas casser)

Deux précédents servent de modèle et sont **repris tels quels** par ce contrat :

- **`dashboard.compute_recovery_axis`** applique déjà exactement la politique du §4 : portail de
  suffisance (≥ 5 entrées / 30 j), état `insuffisante` explicite, `active=False`, et un message
  d'orientation. C'est le comportement de référence.
- **`normalize_fatigue_score`** (S13) est déjà une conversion **explicite, bornée, nommée, testée**,
  avec une borne volontairement asymétrique (« on refuse d'inventer une bonne nouvelle, on ne
  supprime pas une mauvaise »). Ce contrat en généralise le principe.

---

## 2. Le contrat sémantique canonique

Cinq concepts distincts. **Aucun ne doit être fusionné dans un score unique.**

### 2.1 `ReadinessSignal` — l'état subjectif déclaré aujourd'hui

> **Ce que c'est** : ce que la personne a **déclaré** ressentir aujourd'hui.
> **Ce que ce n'est pas** : une mesure de récupération. Jamais présenté comme objectif.

| Champ | Type | Sémantique |
|---|---|---|
| `declared_on` | `date` | Jour calendaire de la déclaration |
| `age_days` | `int` | Ancienneté vs aujourd'hui ; `0` = déclaré aujourd'hui |
| `sleep`, `soreness`, `stress`, `motivation`, `self_reported_freshness` | `float \| None`, **0.0–1.0**, **plus haut = mieux** | Les 5 dimensions de S1, normalisées |
| `overall` | `float \| None`, **0.0–1.0**, plus haut = mieux | Moyenne des dimensions présentes ; `None` si aucune |
| `sufficiency` | `Sufficiency` (§4) | `sufficient` / `partial` / `insufficient` / `stale` |
| `basis` | `tuple[str, ...]` | Provenance lisible, p. ex. `("readiness_entry:2026-08-11",)` |

**Renommage obligatoire.** Le champ S1 `fatigue_level` est exposé ici sous le nom
`self_reported_freshness`, parce que **5 signifie « Très frais »**. Conserver le nom `fatigue_level`
sur un axe orienté « plus haut = mieux » perpétue exactement l'inversion du constat **C2**. Le
champ persisté n'est **pas** renommé (aucune migration) : le renommage vit dans l'adaptateur.

**Source autorisée en V1 : `ReadinessEntry` uniquement.** Pas de wearable, pas d'inférence.

**Péremption.** `age_days == 0` ⇒ `sufficient`. `1..2` ⇒ `partial`. `≥ 3` ⇒ **`stale`**, et un
signal `stale` **ne peut pas** justifier une recommandation plus agressive — il ne peut que réduire
la confiance ou déclencher une invitation à re-déclarer.

### 2.2 `FatigueSignal` — la charge accumulée, décomposée

> **Direction : plus haut = plus fatigué.** Fixée, jamais inversée en silence.
> Le complément orienté disponibilité est exposé séparément, jamais implicitement.

| Champ | Type | Sémantique |
|---|---|---|
| `strength_component` | `float \| None`, 0.0–1.0 | Contribution de la charge de musculation |
| `cardio_component` | `float \| None`, 0.0–1.0 | Contribution cardio (§5) |
| `subjective_component` | `float \| None`, 0.0–1.0 | Ressenti post-séance (S15), **conservé** |
| `overall` | `float \| None`, 0.0–1.0 | Agrégat **déterministe** des composantes présentes |
| `as_availability` | `float \| None`, 0.0–1.0 | **`1.0 − overall`**, exposé explicitement — jamais un flip implicite |
| `sufficiency`, `confidence`, `basis` | §4 | — |

**Séparation obligatoire.** Les trois composantes restent lisibles individuellement : un
utilisateur fatigué par du cardio et un utilisateur fatigué par des jambes lourdes ne sont pas dans
la même situation, et une surface d'explication doit pouvoir le dire.

**Agrégation.** L'agrégat est une combinaison **déterministe et documentée** des composantes
**présentes** — une composante `None` est **exclue du calcul et de la normalisation**, et **ne vaut
jamais 0.0** (0.0 signifierait « aucune fatigue de cette origine », ce qu'on ne sait pas). Les poids
exacts sont une **question ouverte** (§12 · OQ-3).

### 2.3 `ZoneRecoveryEstimate` — une **estimation** par zone

> **Vocabulaire imposé.** On dit **estimation**. Jamais « récupération mesurée », jamais
> « % de récupération physiologique », jamais « readiness musculaire mesurée ». Voir §8.

Une instance **par `BodyZone` canonique** (les 11 zones détaillées de `ZONE_LABELS`).

| Champ | Type | Sémantique |
|---|---|---|
| `zone_code` | `str` | Code `BodyZone` canonique — **aucun vocabulaire nouveau** (§6) |
| `estimate` | `float \| None`, 0.0–1.0 | **Plus haut = plus probablement disponible.** `None` = non estimable |
| `band` | `RecoveryBand` | `likely_available` / `partially_recovered` / `likely_fatigued` / `unknown` |
| `confidence` | `Confidence` | `high` / `medium` / `low` / `none` |
| `basis` | `tuple[str, ...]` | Ce sur quoi l'estimation repose, lisible par un humain |
| `last_relevant_load_at` | `datetime \| None` | Dernière charge pertinente pour cette zone |
| `hours_since_last_load` | `float \| None` | `None` si jamais chargée — **pas** `24×365` |
| `contributing_signals` | `tuple[str, ...]` | Identifiants des signaux ayant contribué |
| `staleness` | `Sufficiency` | Fraîcheur des données d'entrée |

**Correction de fail-open, normative.** Une zone **jamais entraînée** ⇒ `estimate = None`,
`band = unknown`, `confidence = none`, `hours_since_last_load = None`. **Interdit** de rendre
`1.0`. « Je n'ai jamais vu cette zone » et « cette zone est parfaitement récupérée » sont deux
affirmations différentes, et une seule des deux est vraie.

**La bande prime sur le nombre en surface.** Toute UI doit pouvoir afficher `band` sans jamais
afficher `estimate` : un nombre à deux décimales suggère une précision que le modèle n'a pas.

### 2.4 `AvailabilitySignal` — le mot désambiguïsé

Le constat **C3** est résolu en **séparant les types**. Ces trois notions **ne doivent jamais
partager un champ**.

| Type | Question | Source | Statut V1 |
|---|---|---|---|
| `EquipmentAvailability` | « Cette machine existe-t-elle là où je m'entraîne ? » | S16 (`available_equipment`, familles d'équipement) | **Existe** — enveloppé, non modifié |
| `ScheduleAvailability` | « Ai-je le temps aujourd'hui / cette semaine ? » | **N'existe pas en code** | **Déclaré, non implémenté** — placeholder typé, `None` en V1 |
| `TrainingSuitability` | « Est-il indiqué d'entraîner cette zone maintenant ? » | S7 + §2.3 | **Renommage de `availability_by_zone`** |

**Renommage normatif.** `availability_by_zone` devient `TrainingSuitability`. Le mot
« availability » **reste réservé** aux deux premiers sens (équipement, agenda) — les seuls où il
décrit une contrainte externe plutôt qu'une inférence sur le corps.

**Non-collision UI.** Le `{"available": bool}` des composeurs (S17) est un **quatrième** sens :
« ce bloc est affichable ». Il reste tel quel et **hors** du contrat — mais aucun nouveau champ du
contrat ne portera ce nom.

### 2.5 `TrainingState` — l'agrégat déterministe

L'unique objet que les consommateurs futurs lisent.

| Champ | Type |
|---|---|
| `computed_at` | `datetime` |
| `readiness` | `ReadinessSignal` |
| `fatigue` | `FatigueSignal` |
| `zone_recovery` | `tuple[ZoneRecoveryEstimate, ...]` — **une par zone canonique, toujours les 11** |
| `equipment` | `EquipmentAvailability \| None` |
| `schedule` | `ScheduleAvailability \| None` (V1 : toujours `None`) |
| `overall_sufficiency` | `Sufficiency` |
| `overall_confidence` | `Confidence` |
| `basis` | `tuple[str, ...]` |

**Règle d'exposition.** `TrainingState` **expose des primitives**. Il **n'expose aucun score global
unique** susceptible de devenir « le » chiffre affiché : ce serait recréer le problème que ce
contrat corrige. Un consommateur qui veut un scalaire le dérive lui-même, explicitement, et assume
sa formule.

**Pureté.** Lecture seule. Aucune écriture, aucune mutation, aucun effet de bord. Déterministe à
horodatage d'entrée fixé.

---

## 3. Normalisation des échelles

**Règle canonique.** Toute valeur normalisée est en **`0.0–1.0`**, et **la direction est explicite
dans le nom du champ ou sa documentation**. Préférence : *plus haut = plus disponible / meilleure
readiness*. La fatigue conserve *plus haut = plus fatigué* (nommée sans ambiguïté), et son
complément est exposé **explicitement** via `as_availability`. **Jamais d'inversion silencieuse.**

### 3.1 Table de conversion des échelles héritées

Toute conversion est **nommée**, **bornée** et **testée unitairement**. Le nom donné ici est
normatif : la tranche `Sb_RECOVERY_CONTRACT_01` doit implémenter ces fonctions sous ces noms.

| Source | Échelle héritée | Direction héritée | Conversion nommée | Cible | Notes |
|---|---|---|---|---|---|
| `ReadinessEntry.sleep_quality` etc. (S1) | **1–5** entiers | 5 = meilleur | `normalize_readiness_scale(v)` | 0.0–1.0, plus haut = mieux | `(v − 1) / 4`. Hors 1–5 ou non entier ⇒ `None` |
| `ReadinessEntry.fatigue_level` (S1) | 1–5 | **5 = très frais** | `normalize_readiness_scale(v)` → exposé `self_reported_freshness` | 0.0–1.0, plus haut = **plus frais** | **Piège C2** : ne jamais mapper ce champ vers `FatigueSignal` sans complément |
| `behavioral.fatigue_score` (S3) | **0–100** | plus haut = plus fatigué | **`normalize_fatigue_score`** — *existe déjà* (S13) | 0.0–1.0, plus haut = plus fatigué | **Réutiliser, ne pas réécrire.** Plancher productible **15.0**, `< 15` ⇒ `None` (sentinelle d'échec) |
| `behavioral.readiness_score` (S4) | 0–100 | plus haut = mieux | `normalize_behavioral_readiness(v)` | 0.0–1.0 | **Non intégré au contrat V1** — voir §10 (dépréciation) |
| `dashboard` recovery axis (S2) | 0–100 | plus haut = mieux | `normalize_percent_scale(v)` | 0.0–1.0 | Conserver l'état `active=False` d'origine, ne pas le convertir en 0.0 |
| `availability_by_zone` (S7) | **déjà 0.0–1.0** | plus haut = disponible | `identity`, mais **le cas « jamais » change** | 0.0–1.0 \| `None` | `1.0` → **`None`** quand jamais entraînée (§2.3) |
| `hours_since_last_by_zone` (S8) | heures, `24×365` = jamais | plus haut = plus ancien | `hours_since_last_or_none(v)` | `float \| None` | La sentinelle `24×365` devient `None` |
| `days_since_last_*` (S10) | jours \| `None` | plus haut = plus ancien | conservé tel quel | — | Déjà honnête (`None` explicite) |
| `RECOVERY_HOURS_TARGET` (S9) | heures 24–72 | — | `recovery_target_hours(zone)` | heures | **Copie unique** : le contrat lit la constante existante, il n'en crée pas une cinquième (§6) |
| `global_state` / `concentration` (S15) | catégoriel fermé | — | `normalize_session_feedback(gs, co)` | 0.0–1.0, plus haut = plus fatigué | Réutilise `compute_session_fatigue` puis `normalize_fatigue_score` |
| Effort cardio (S14) | min / bpm / kcal / texte | — | `cardio_load_estimate(...)` (§5) | 0.0–1.0 + confiance | **Nouveau**, borné, heuristique déclarée |
| `ZONE_FRESHNESS_BONUS_*` (S12) | **points de score** | plus haut = plus frais | **aucune** | — | **Reste dans `recommendation.py`.** Ce n'est pas une grandeur normalisable, c'est un poids de scoring interne |
| Libellés de confiance (`insuffisante`/`faible`/`moyenne`/`élevée`) | catégoriel FR | — | `confidence_from_legacy_label(s)` | `Confidence` | Mapping explicite, `None` sur libellé inconnu |

### 3.2 Interdits de normalisation

- **Interdit** de convertir une absence de donnée en `0.0` ou en `1.0`.
- **Interdit** d'inverser une direction sans passer par un champ nommé (`as_availability`).
- **Interdit** d'ajouter une conversion non listée ci-dessus sans amender cette spec.

---

## 4. Politique de données manquantes — *fail-closed*

> **Règle canonique, non négociable : une donnée manquante ne signifie JAMAIS « frais ».**

### 4.1 Les états

```
Sufficiency = sufficient | partial | insufficient | stale
Confidence  = high | medium | low | none
```

| État | Signification | Effet autorisé |
|---|---|---|
| `sufficient` | Assez de données récentes | Valeur exploitable, confiance normale |
| `partial` | Quelques données, sous le seuil de confort | Valeur exploitable, **confiance réduite** |
| `insufficient` | Trop peu pour estimer | **Valeur `None`** — pas de nombre inventé |
| `stale` | Données présentes mais trop anciennes | **Valeur `None` ou confiance minimale** ; **ne peut jamais justifier une recommandation plus agressive** |

### 4.2 Interdictions explicites

Le contrat **interdit** :

- `exception` → fraîcheur parfaite ;
- `unknown` → readiness élevée ;
- `pas de donnée cardio` → « totalement récupéré » ;
- **zone jamais entraînée** → `availability = 1.0` (le fail-open **C4** vivant aujourd'hui) ;
- toute valeur neutre affichée sans son `confidence`/`sufficiency`.

### 4.3 Comportement neutre — explicite et explicable

Quand un consommateur exige malgré tout une valeur, le neutre doit être :

1. **nommé** (`NEUTRAL_ESTIMATE`, pas un `0.5` littéral perdu dans une formule) ;
2. **accompagné** de `confidence = low` ou `none` et de la `basis` qui l'explique ;
3. **incapable de déclencher une escalade** — un neutre ne peut jamais rendre une séance *plus*
   dure ; il peut seulement laisser le comportement par défaut.

**Cas hérité à corriger explicitement.** `dashboard.compute_recovery_axis` renvoie `score=50.0`
avec `confidence="faible"` quand il y a ≥ 5 entrées sur 30 j mais **aucune** sur 7 j. C'est un
neutre fabriqué : il respecte (2) mais pas (1). À aligner lors de l'intégration — **sans changer la
surface affichée** tant qu'aucune tranche UI n'est autorisée.

---

## 5. Intégration cardio — V1 sur données réellement capturées

### 5.1 Ce qui existe vraiment aujourd'hui

Quatre colonnes, **toutes nullable**, sur `WorkoutSession` (S14) : `cardio_duration_min`,
`cardio_bpm_avg`, `cardio_machine_calories`, `cardio_machine_type` (`String(32)`, **texte libre**).
Plus `WorkoutTemplate.kind == "cardio"` et `cardio_note`.

**Aucun wearable. Aucune zone de fréquence cardiaque. Aucun RPE cardio structuré.** Le blueprint en
souhaite ; ce document n'en invente pas.

### 5.2 Le modèle V1

`cardio_load_estimate(...) -> (value: float | None, confidence: Confidence, basis: tuple[str, ...])`

**Entrées autorisées, et elles seules** : type d'activité (`cardio_machine_type`, **normalisé via
un vocabulaire fermé versionné**, valeur inconnue ⇒ générique), durée (`cardio_duration_min`),
signal d'intensité disponible (`cardio_bpm_avg` **si présent**, sinon absent — jamais estimé depuis
les calories), et **fraîcheur temporelle** (`started_at`).

**Sorties : bornées.** `value ∈ [0, 1]`. La contribution cardio est **plafonnée** : elle ne peut
pas, à elle seule, porter `FatigueSignal.overall` au maximum. Le plafond exact est une **question
ouverte** (§12 · OQ-4).

**Règles de confiance :**

| Données disponibles | Confiance |
|---|---|
| type connu + durée + bpm | `medium` — jamais `high` : pas de mesure de charge interne |
| type connu + durée, pas de bpm | `low` |
| durée seule | `low` |
| ni durée ni type | `none`, `value = None` |

**Le plafond de confiance est `medium`.** Aucune combinaison des données actuelles ne justifie
`high` : nous n'observons ni la charge interne, ni l'état de récupération.

### 5.3 Distribution par zone — heuristique, et déclarée comme telle

Une activité cardio peut contribuer **davantage** à certaines zones (le vélo sollicite le bas du
corps plus que le haut). Le contrat autorise une table **explicite, déterministe, versionnée et
testable**, sous quatre conditions strictes :

1. elle est **documentée comme heuristique**, jamais comme un fait physiologique ;
2. elle est **bornée** — une contribution cardio ne peut pas dominer une charge de musculation
   directement mesurée sur la même zone ;
3. elle utilise **exclusivement** les codes `BodyZone` canoniques (§6) ;
4. **l'absence d'entrée dans la table réduit la confiance**, elle ne produit pas une contribution
   nulle silencieuse.

**Formulations interdites** (§8) : « jambes récupérées à 25 % », « 72 h de récupération
nécessaires », tout pourcentage de fatigue tissulaire. **Formulation autorisée** : « vélo récent —
bas du corps probablement moins disponible (estimation, confiance faible) ».

> **Si le modèle est insuffisant, il rend une confiance faible. Il ne fabrique pas de précision.**

---

## 6. Intégration BodyZone — aucune taxonomie nouvelle

`Sb_32.4` a fait de `ExerciseMuscleMapping` + `BodyZone` la source de vérité formelle pour le
premier consommateur lourd. Ce contrat **consomme** cette fondation.

**Interdits :** aucun vocabulaire de zone nouveau · aucun classifieur par sous-chaîne nouveau ·
aucune taxonomie JSON nouvelle · aucune 5ᵉ copie du dictionnaire des 11 zones.

**Obligations :**

- l'attribution exercice → zone passe **exclusivement** par le contrat de `Sb_32.4`
  (`body_zone_source.resolve_exercise_zones`), y compris son `resolution_path` — un consommateur du
  `TrainingState` doit pouvoir savoir si l'attribution vient de la table formelle ou du repli ;
- la projection **zone détaillée → axe macro** pour une UI compacte réutilise **la projection
  canonique de `Sb_ZONE_COUNT_TAXONOMY_FIX_01`** : `muscle_mapping.radar_axis_for_zone` /
  `ZONE_TO_RADAR_AXIS`, dérivée de `RADAR_AXES`. **Ne pas la recopier** ;
- `core` n'a **pas** d'axe radar : en présentation macro, une zone qui projette sur `None` est
  **abandonnée de l'axe**, jamais rattachée arbitrairement. Elle reste pleinement présente au
  niveau détaillé ;
- l'agrégation d'un axe macro à partir de ses zones détaillées doit être **explicite** (min ? pire
  zone ? moyenne pondérée ?) — **question ouverte** (§12 · OQ-5).

**Cas `RECOVERY_HOURS_TARGET`.** Le contrat **lit** la constante existante de `recommendation.py`
(§7 l'autorise : lire n'est pas modifier). Il **n'en crée pas** de copie. Son déplacement éventuel
vers une colonne `BodyZone` est une **question ouverte** (§12 · OQ-2) et exigerait une migration —
donc hors de ce contrat.

---

## 7. Frontière avec `recommendation.py`

> **Contrainte dure : `app/services/recommendation.py` reste NON MODIFIABLE.**
> Cette spec est conçue pour ne pas en avoir besoin. Si une tranche future découvre qu'elle en a
> besoin, c'est un **HARD STOP** et un arbitrage opérateur séparé.

| Élément | Statut |
|---|---|
| `recommendation.py` | **Moteur de recommandation hérité.** Continue de fonctionner à l'identique |
| `TrainingState` / contrat de récupération | **Service séparé, additif, en lecture seule** |
| `recommendation_explainer` et couches orchestrateur futures | **Peuvent consommer les deux** |
| Migration de `recommendation.py` lui-même | **Décision future explicite et séparée** |

**Anti-duplication.** Il est **interdit** de réimplémenter un moteur de recommandation en
parallèle. Le contrat produit un **état**, pas une décision. Le choix d'une séance reste au moteur
hérité jusqu'à décision contraire.

**Lecture autorisée.** Le contrat **peut lire** les constantes et fonctions publiques de
`recommendation.py` (`RECOVERY_HOURS_TARGET`, `FATIGUE_HIGH_THRESHOLD`) — c'est même préférable à
une copie, et `Sb_FATIGUE_SCALE_FIX_01` a déjà établi le précédent en **pinnant l'alignement par un
test** plutôt qu'en dupliquant la valeur.

---

## 8. Garde-fous scientifiques et produit

### 8.1 Vocabulaire autorisé

**estimation** · **indicatif** · **inféré depuis l'entraînement récemment enregistré** ·
**confiance** · **base / fondement** · **charge récente** · **probablement disponible** ·
**probablement fatigué** · **plage** · **cible ajustable**.

### 8.2 Vocabulaire interdit

**« % physiologiquement récupéré »** · **« récupération musculaire mesurée »** sans source de
mesure · tout **diagnostic de blessure** · toute **prescription thérapeutique** · toute
revendication d'**activation type EMG** · tout **temps de récupération exact** présenté comme une
vérité biologique.

### 8.3 Règles de fond

- **Volume** : décrire des **plages** et des **cibles ajustables**. Jamais un « optimal »
  universel.
- **Échec** : l'entraînement à l'échec **n'est pas requis** comme règle universelle.
- **Morphologie** : peut **biaiser des priorités initiales** ; ne **détermine pas** la récupération
  quotidienne.
- **Aucune donnée EMG**, aucune inférence d'activation.
- **Anthropométrie à confiance bornée** : ni fémur, ni posture, ni insertion, ni diagnostic.
- **L'agentique propose, le déterministe décide.** Ce contrat est intégralement déterministe.

### 8.4 Test de wording exigé

Chaque tranche produisant du texte utilisateur **doit** embarquer un test qui échoue si une
formulation interdite du §8.2 apparaît dans une chaîne rendue. Le garde-fou vit dans le code, pas
seulement dans ce document.

---

## 9. Architecture cible

```
Signaux bruts (persistés)
  ├─ WorkoutSession complétées (strength)      → tonnage, hard sets, zones via Sb_32.4
  ├─ WorkoutSession cardio                     → duration / bpm / calories / machine_type
  ├─ ReadinessEntry                            → 5 dimensions 1–5, 1/jour
  ├─ global_state / concentration              → ressenti post-séance
  └─ horodatages (started_at, recorded_on)
          │
          ▼
Adaptateurs hérités / normalisation  ── §3, conversions nommées et bornées
  ├─ normalize_readiness_scale        (1–5      → 0–1, plus haut = mieux)
  ├─ normalize_fatigue_score          (0–100    → 0–1)   ← EXISTE DÉJÀ (Sb_FATIGUE_SCALE_FIX_01)
  ├─ normalize_session_feedback       (catégoriel → 0–1)
  ├─ cardio_load_estimate             (min/bpm/type → 0–1 + confiance)   ← §5
  ├─ hours_since_last_or_none         (24×365   → None)
  └─ resolve_exercise_zones           ← CONTRAT Sb_32.4, pas de taxonomie nouvelle
          │
          ▼
TrainingState            ── déterministe · lecture seule · aucune écriture
  ├─ ReadinessSignal          (déclaré, daté, périmable)
  ├─ FatigueSignal            (strength | cardio | subjectif, + as_availability)
  ├─ ZoneRecoveryEstimate[]   (11 zones canoniques, band + confidence + basis)
  ├─ EquipmentAvailability    (enveloppe l'existant)
  ├─ ScheduleAvailability     (déclaré, None en V1)
  ├─ overall_sufficiency / overall_confidence
  └─ basis
          │
          ▼
Consommateurs déterministes (aucun n'est autorisé par cette spec)
  ├─ WeeklyVolumeBudget   (futur — plages ajustables)
  ├─ WeeklyPlan           (futur)
  ├─ replanification adaptative (futur)
  └─ explainer / cockpit  (texte déterministe, garde-fous §8)

recommendation.py  ──────────────────────────────►  reste EN PARALLÈLE, non modifié
                                                     (migration = décision séparée)
```

### 9.1 Graphe de dépendances

```
Sb_RECOVERY_CONTRACT_01        (types purs, normalizers)
        │
        ├──────────────► Sb_CARDIO_FATIGUE_ADAPTER_01     (dépend des types + §5)
        │                        │
        ▼                        ▼
Sb_TRAINING_STATE_AGGREGATOR_01  ◄── dépend aussi de Sb_32.4 (déjà livré)
        │
        ▼
Sb_ZONE_RECOVERY_ESTIMATE_01     (dépend de l'agrégat + Sb_32.4 + P0.1 projection)
        │
        ▼
Sb_RECOVERY_EXPLAINER_01         (texte déterministe, garde-fous §8)
        │
        ▼
[consommateurs de planification — hors périmètre, GO séparé]
```

---

## 10. Stratégie de migration et de dépréciation des signaux hérités

**Principe : additif d'abord, aucune dépréciation dans la même tranche que l'introduction.**

| Signal hérité | Devenir | Quand |
|---|---|---|
| S7 `availability_by_zone` | **Conservé** dans `recommendation.py` (non modifiable). Le contrat expose `TrainingSuitability` en parallèle, avec le fail-open corrigé | Divergence **attendue et documentée** sur les zones jamais entraînées : `1.0` côté hérité, `None` côté contrat. Un test doit **pinner cette divergence** au lieu de la découvrir |
| S8 `hours_since_last_by_zone` | Conservé ; le contrat expose `None` au lieu de `24×365` | idem |
| S3/S11 `fatigue_score` 0–100 | Conservé en production. Le contrat le lit **via `normalize_fatigue_score`** | Aucune dépréciation avant migration de `recommendation.py` |
| S4 `behavioral.readiness_score` | **Candidat à dépréciation** — c'est le doublon du constat **C1**. **Non intégré** au contrat V1 | Décision opérateur requise (§12 · OQ-1) |
| S1 `ReadinessEntry.fatigue_level` | Colonne **conservée** (aucune migration). Renommée `self_reported_freshness` **à la frontière seulement** | Immédiat, dans l'adaptateur |
| S2 axe recovery du dashboard | Conservé. Alignement du neutre `50.0` sur §4.3 | À l'intégration |
| S9 `RECOVERY_HOURS_TARGET` | **Lu**, jamais copié | Déplacement vers `BodyZone` = OQ-2 |
| S12 `ZONE_FRESHNESS_BONUS_*` | **Hors contrat** — poids de scoring interne | Jamais migré tel quel |
| S17 `{"available": bool}` | **Hors contrat** — sens UI | Inchangé |

**Règle de non-régression.** Tant que `recommendation.py` n'est pas migré, **les deux chemins
coexistent** et peuvent diverger. Chaque divergence connue doit être **listée et testée**, comme
`Sb_32.4` l'a fait pour les attributions de zone. Une divergence non documentée est un défaut.

---

## 11. File de build ordonnée

Aucune de ces tranches n'est ouverte. **Chacune exige un `GO BUILD` explicite.**

### Sb_RECOVERY_CONTRACT_01 — types purs et normalizers

**Contenu** : `dataclasses` gelées et `enum` du §2 · les conversions nommées du §3.1 · les états
`Sufficiency` / `Confidence` / `RecoveryBand` du §4. **Aucun accès DB, aucun moteur de décision,
aucune agrégation.**

**Tier attendu** : `ISOLATED` (module neuf, non importé). **À traiter `SHARED_CODE`** dès que
`muscle_mapping` ou `recommendation` est importé, même en lecture.

**Risques** : figer une direction ou un nom qu'on regrettera ; réimplémenter
`normalize_fatigue_score` au lieu de le réutiliser.

**DoD** : chaque conversion du §3.1 implémentée sous **le nom normatif** et testée sur ses bornes,
son `None` et son type invalide · `normalize_fatigue_score` **réutilisé, pas réécrit** (test qui
échoue s'il est dupliqué) · aucune direction inversée sans champ nommé · 0 accès DB (test de
source) · toutes les structures immuables.

### Sb_CARDIO_FATIGUE_ADAPTER_01 — contribution cardio bornée

**Contenu** : `cardio_load_estimate` (§5.2) · vocabulaire fermé versionné pour
`cardio_machine_type` · table de distribution par zone **déclarée heuristique** (§5.3).

**Dépend de** : `Sb_RECOVERY_CONTRACT_01`.

**Risques** : **le risque principal du cycle** — fabriquer de la précision physiologique.
Secondaire : `cardio_machine_type` est du texte libre `String(32)`, donc le vocabulaire réel en
base est inconnu et probablement sale.

**DoD** : sortie **bornée** [0,1] et **plafonnée** · confiance **jamais `high`** (test) · type
inconnu ⇒ générique + confiance réduite, **jamais** contribution nulle silencieuse · absence de
durée ⇒ `None` · **audit préalable des valeurs réelles** de `cardio_machine_type` en base ou dans
les fixtures, documenté · test de wording (§8.4) · aucun champ cardio inventé.

### Sb_TRAINING_STATE_AGGREGATOR_01 — agrégation en lecture seule

**Contenu** : construction de `TrainingState` depuis les entrées persistées · `ReadinessSignal`
complet · `FatigueSignal` à trois composantes · `overall_sufficiency` / `overall_confidence`.

**Dépend de** : les deux précédentes + le contrat `Sb_32.4`.

**Risques** : requête N+1 (le piège exact rencontré en `Sb_32.4`) · réintroduire un fail-open en
agrégeant des `None` comme des `0.0` · dériver vers un score global unique.

**DoD** : **0 écriture** (garde au niveau source, comme le wipe-guard de `Sb_32.4`) · pureté et
déterminisme à horodatage fixé · un `None` **n'entre jamais** dans une moyenne · **aucun champ de
score global** exposé · résolution par **nom distinct** mémoïsée par invocation · les 11 zones
toujours présentes.

### Sb_ZONE_RECOVERY_ESTIMATE_01 — estimation par zone

**Contenu** : `ZoneRecoveryEstimate` par zone canonique · bandes · `basis` et
`contributing_signals` · **correction du fail-open** « jamais entraînée ⇒ 1.0 ».

**Dépend de** : l'agrégateur.

**Risques** : divergence assumée avec `availability_by_zone` (§10) · tentation de présenter
`estimate` plutôt que `band`.

**DoD** : zone jamais entraînée ⇒ `None` / `unknown` / `confidence=none` (test explicite) ·
divergence vs le chemin hérité **listée et pinnée** · `band` dérivable sans exposer `estimate` ·
projection macro via **`radar_axis_for_zone`** (test qui échoue sur toute recopie) · `core` non
rattaché à un axe.

### Sb_RECOVERY_EXPLAINER_01 — explication déterministe

**Contenu** : texte utilisateur déterministe depuis `TrainingState`, avec `basis` et confiance.

**Dépend de** : les précédentes.

**Risques** : le vocabulaire interdit du §8.2 · afficher un nombre là où une bande suffit ·
affirmer une causalité que l'estimation ne porte pas.

**DoD** : test de wording (§8.4) échouant sur chaque terme interdit · toute phrase de disponibilité
accompagnée de sa confiance · confiance `none` ⇒ **silence**, jamais une phrase rassurante ·
aucun LLM, 100 % déterministe.

### Ensuite seulement — consommateurs de planification

`WeeklyVolumeBudget`, `WeeklyPlan`, replanification adaptative. **Hors périmètre de cette spec** ;
chacun exigera son propre cadrage.

---

## 12. Questions ouvertes exigeant une décision opérateur

| # | Question | Pourquoi elle ne peut pas être tranchée ici | Défaut si pas de réponse |
|---|---|---|---|
| **OQ-1** | Que devient `behavioral.readiness_score` (S4) ? Le contrat le remplace-t-il, ou les deux coexistent-ils durablement ? | C'est le doublon du constat **C1** et il est **affiché** en KPI sur l'accueil. Le retirer est un changement produit visible, pas un refactor. | Coexistence, `TrainingState` **n'intègre pas** S4 en V1 |
| **OQ-2** | `RECOVERY_HOURS_TARGET` doit-il devenir une colonne `BodyZone.recovery_hours` ? | Exige une **migration** (interdite dans ce cycle) et déplace un paramètre depuis un fichier non modifiable. | Le contrat **lit** la constante ; aucune migration |
| **OQ-3** | Pondération des trois composantes de `FatigueSignal` (strength / cardio / subjectif) ? | Aucune base empirique dans le repo, et le choix est **produit** avant d'être technique. | Aucune valeur figée par la spec — la tranche devra la proposer avec sa justification, et elle sera revue |
| **OQ-4** | Plafond de la contribution cardio à la fatigue globale ? | Même raison ; un plafond trop haut ferait passer une sortie vélo pour une séance de jambes. | Plafond conservateur à proposer, révisable |
| **OQ-5** | Agrégation d'un axe macro depuis ses zones détaillées : minimum, pire zone, ou moyenne pondérée ? | Trois sémantiques légitimes et différentes (« l'axe est disponible si **toutes** ses zones le sont » vs « en moyenne »). | Aucune ; à trancher avant `Sb_ZONE_RECOVERY_ESTIMATE_01` |
| **OQ-6** | Seuil de péremption de `ReadinessSignal` : `stale` à 3 jours ? | Dépend de la fréquence réelle de remplissage du questionnaire, non mesurée. | 3 jours, révisable après mesure |
| **OQ-7** | La déclaration subjective doit-elle **influencer** la recommandation, ou seulement l'expliquer ? | C'est **la** question produit du constat **C1**, et elle touche `recommendation.py`, non modifiable. | Explication seulement en V1 |

**Aucune de ces questions ne bloque `Sb_RECOVERY_CONTRACT_01`** : la première tranche est
constituée de types et de conversions, dont aucune ne dépend d'OQ-1 à OQ-7.

---

## 12bis. Décisions opérateur — RÉSOLUES

> **Ajout daté du 2026-08-11, à l'ouverture de `Sb_RECOVERY_CONTRACT_01`.**
> Cette section **complète** le §12 sans le réécrire : l'audit d'origine et les défauts proposés y
> restent lisibles tels qu'ils ont été soumis. Ce qui suit est ce que l'opérateur a **tranché**.
> **En cas de contradiction entre le §12 et le §12bis, le §12bis fait foi.**

| OQ | Décision | Conséquence normative |
|---|---|---|
| **OQ-1** — `behavioral.readiness_score` | **Hérité, candidat à une dépréciation visible ultérieure.** Ne **DOIT PAS** entrer dans `TrainingState`. Producteur et UI restent compatibles ; **aucun retrait dans ce cycle**. Remplacement seulement une fois la surface `TrainingState`/explainer existante. | `normalize_behavioral_readiness` **existe** comme conversion nommée (la table §3.1 doit rester complète), mais **aucun champ de `TrainingState` ne la consomme**. Un test pinne cette absence. |
| **OQ-2** — `RECOVERY_HOURS_TARGET` | **Pas de `BodyZone.recovery_hours`.** La durée de récupération **n'est pas une propriété anatomique intrinsèque**. La constante héritée peut être **lue via un adaptateur** tant que `recommendation.py` reste hérité. Le remplacement futur sera une **`RecoveryPolicy` versionnée**, pas un attribut de schéma. **Aucune migration.** | `recovery_target_hours(zone)` lit la constante existante en **import différé**, et le §6 est amendé : la piste « colonne `BodyZone` » est **fermée**. |
| **OQ-3** — pondération de `FatigueSignal` | **Aucune pondération globale en V1.** Les trois composantes restent **séparément observables**. `FatigueSignal` **NE DOIT PAS** inventer d'agrégat pondéré. Un consommateur futur qui exige un scalaire **possède et documente sa propre formule**. | **Amende le §2.2** : les champs `overall` et `as_availability` **sont retirés** de `FatigueSignal`. Le complément de disponibilité devient une **fonction pure nommée** appliquée par l'appelant à une composante de son choix. Un test pinne l'absence de tout agrégat. |
| **OQ-4** — plafond cardio | **Aucun pourcentage cardio universel.** La contribution cardio reste **explicite et séparée**. La confiance issue des champs actuels **ne peut jamais dépasser `medium`**. Les règles de magnitude appartiennent à `Sb_CARDIO_FATIGUE_ADAPTER_01`, **après audit du vocabulaire réellement stocké**. **Ne pas inventer de coefficient dans ce sprint.** | `cardio_load_estimate` est **déclarée** dans le contrat (la table §3.1 reste complète) mais rend `None` / `Confidence.NONE` en V1 : un **contrat déclaré, non implémenté**, pas un coefficient inventé. |
| **OQ-5** — zones détaillées vs axes macro | Les **décisions** d'entraînement utilisent les **zones détaillées canoniques**. Les **axes macro sont de présentation uniquement**. Quand une présentation compacte exige une valeur macro : **pire zone constituante (WORST/MIN)**, et la **zone limitante est exposée dans `basis`**. La valeur macro **ne doit pas** devenir source de vérité du planificateur. | **Résout le §6** : l'agrégation macro est le **minimum**, conservatrice, traçable. |
| **OQ-6** — péremption de la readiness | `age_days == 0` ⇒ `sufficient`, potentiellement pertinent pour une décision future. `1..2` ⇒ `partial`, **contexte seulement**. `>= 3` ⇒ `stale`. Une readiness non courante **ne peut jamais** justifier une recommandation plus agressive. | **Confirme le §2.1** et fige le seuil. |
| **OQ-7** — influence de la readiness subjective | **OUI**, elle doit à terme influencer l'orchestration — **de façon ASYMÉTRIQUE**. Une mauvaise readiness courante **peut** réduire la confiance / l'agressivité. Une bonne readiness subjective **NE PEUT JAMAIS**, à elle seule, **augmenter** l'agressivité prescrite. Ce cycle V1 **ne modifie pas** `recommendation.py` ; l'intégration initiale est `TrainingState` + explication ; l'influence sur la décision appartient au consommateur orchestrateur futur. | **Direction produit actée.** Le contrat expose de quoi appliquer l'asymétrie plus tard, sans l'appliquer ici. |

### Le principe d'asymétrie, énoncé une fois pour tout le cycle

OQ-4, OQ-5 et OQ-7 disent la même chose sous trois angles, et c'est la règle de conception
transversale de ce contrat :

> **Un signal dégradé, ancien ou incertain peut rendre le système plus prudent.
> Il ne peut jamais le rendre plus agressif.**

C'est la généralisation de la borne unilatérale déjà retenue par `Sb_FATIGUE_SCALE_FIX_01` :
*on refuse d'inventer une bonne nouvelle, on ne supprime pas une mauvaise.*

## 12ter. Corrections d'audit — cardio (`Sb_CARDIO_FATIGUE_ADAPTER_01`)

> **Ajout daté du 2026-08-11.** Deux affirmations du §1.1 et du §5.1 étaient **imprécises** et sont
> corrigées ici sans réécrire l'audit d'origine.

### C-1 — `cardio_machine_type` : le stockage est permissif, **l'UI ne l'est pas**

Le §5.1 décrivait ce champ comme du « texte libre » et en concluait que le vocabulaire réellement
présent était **inconnu**. C'est **inexact pour la saisie** :

- **Vocabulaire de stockage** : `String(32)`, historiquement permissif — et
  `routers/sessions.py:628` n'applique **aucune allow-list** (`clean_str(max_length=32)` seulement).
  Un POST forgé peut donc stocker n'importe quelle chaîne ≤ 32 caractères. La permissivité est
  **réelle**, mais elle vient de l'**endpoint**, pas de la saisie.
- **Vocabulaire d'UI courant** : `session_detail.html` expose un `<select>` **fermé** —
  `""` · `velo` · `marche` · `rameur` · `elliptique` · `autre`.

Les deux garanties sont différentes et l'adaptateur ne s'appuie que sur la **plus faible**.

**Vocabulaire réellement observé** (audit fait, sources déclarées) :

| Source | Valeurs observées |
|---|---|
| `<select>` de `session_detail.html` | `velo`, `marche`, `rameur`, `elliptique`, `autre` |
| `tests/test_cardio_capture.py` | `velo` |
| `tests/test_session_done.py:183` | **`stairmaster`** — valeur **hors liste réellement présente dans le dépôt** |
| Base de dev locale `var/workout.db` | **7 séances, `cardio_machine_type` NULL partout**, 0 durée, 0 bpm |
| **Base de production** | **NON AUDITÉE — aucun accès** (voir ci-dessous) |

> **L'audit de la base de production n'a pas pu être réalisé** : cette session n'a ni identifiants
> ni accès DB au VPS (déjà constaté en `Sb_OPS_DEPLOY_SAFETY_01`, où le smoke test devait rester
> non authentifié pour cette raison). **Les fixtures ne valent pas la production** et ne sont pas
> présentées comme telles. Si des lignes historiques portent d'autres valeurs, l'adaptateur les
> traite comme `UNKNOWN` — dégradation prévue, pas surprise.

**Aucun alias n'est encodé** : aucun n'est attesté dans le dépôt. `velo` est stocké sans accent ;
`vélo` n'existe que comme libellé d'affichage. Inventer des orthographes jamais observées est
exactement la fabrication que le §5 interdit.

### C-2 — BPM : preuve, jamais magnitude

Le §5.2 autorisait `cardio_bpm_avg` comme « signal d'intensité disponible ». **Précision
normative** : la BPM moyenne **absolue** ne détermine **jamais** la magnitude.

AUREN n'a **aucun ancrage cardiaque individuel** — ni FCmax mesurée, ni FC de repos, ni réserve de
FC, ni seuil ventilatoire ou lactique. 130 bpm n'est donc pas comparable d'une personne à l'autre.

**Le catalogue le rend concret** : les deux templates cardio (`liss-only`, `liss-abs`) prescrivent
la **même** cible « 120-130 bpm » à **tout le monde**. Une lecture dans cette bande ne distingue
personne.

La BPM peut donc uniquement : alimenter la `basis`, et **faire monter la confiance de `LOW` à
`MEDIUM`** sur une modalité spécifique. Elle ne peut **jamais** agrandir la valeur.

### C-3 — Calories machine : exclues du calcul

`cardio_machine_calories` **n'influence pas** `cardio_load_estimate` — ce n'est même pas un
paramètre. Le produit les étiquette « indicatif » dans le formulaire de saisie, elles proviennent
d'estimateurs machine de calibration inconnue, et ne constituent pas une mesure de charge interne
individualisée. Elles restent de l'**affichage et de l'export**.

### C-4 — La référence de durée vient du catalogue

`CARDIO_DURATION_REFERENCE_MINUTES = 30.0` n'est pas inventée : les deux templates cardio de
`reference_split.json` prescrivent **« 20-30 min LISS »**, et 30 est le haut de cette plage. C'est
une **constante de normalisation produit, pas un seuil biologique de fatigue** — rien de
physiologique ne se produit à 30 minutes.

`coach_inference.CARDIO_LOW_MIN_PER_WEEK` (90) a été examinée et **écartée** : c'est un plancher de
volume **hebdomadaire** issu d'une recommandation de santé publique, mauvaise granularité pour un
proxy d'exposition **par séance**.

## 13. Definition of Done de cette spec

| Exigence | § |
|---|---|
| Inventaire complet des signaux vivants | §1.1 (17 signaux) |
| Matrice de source de vérité | §1.1 |
| Table de conversion d'échelles | §3.1 |
| Contrat sémantique | §2 |
| Politique de données manquantes | §4 |
| Règles d'intégration cardio | §5 |
| Règles d'intégration BodyZone | §6 |
| Frontière `recommendation.py` | §7 |
| Garde-fous de formulation scientifique | §8 |
| Diagramme d'architecture cible | §9 |
| Graphe de dépendances | §9.1 |
| File de build ordonnée | §11 |
| Risques et DoD par tranche | §11 |
| Non-goals explicites | §14 |
| Migration / dépréciation des signaux hérités | §10 |
| Questions ouvertes pour l'opérateur | §12 |

Aucun terme vague n'est laissé sans définition : « fatigue » (§2.2), « récupération » (§2.3),
« availability » (§2.4) et « readiness » (§2.1) ont chacun une sémantique, une échelle, une
direction et une politique de données manquantes.

---

## 14. Non-goals — périmètre interdit

Ce document **ne fait pas** et **n'autorise pas** :

- modifier du code runtime produit — **SPEC ONLY** ;
- modifier `app/services/recommendation.py` (**contrainte dure permanente**) ;
- modifier `app/services/behavioral.py` ;
- ajouter une migration Alembic, un modèle ou une table ;
- activer Body Intelligence ou changer un flag de production ;
- refondre l'accueil ou une quelconque surface UI ;
- construire un planificateur hebdomadaire ou une replanification adaptative ;
- intégrer un wearable, ou inventer une donnée physiologique non capturée ;
- modifier le moteur de morphologie, la substitution, l'overload ;
- ajouter des profils de salle ;
- déployer en production ;
- **créer un score global unique** de readiness ou de récupération ;
- **ouvrir** l'une des tranches du §11 — chacune exige un `GO BUILD` explicite.
