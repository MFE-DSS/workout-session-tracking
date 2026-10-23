# Sx_AUREN_SCIENTIFIC_ENGINE_V2 — Moteur scientifique de prescription

**Statut :** SPEC — **en attente des livrables du chercheur** (A–F) · **Date :** 2026-10-23 ·
**Aucun build autorisé.** · **Origine :** revue scientifique transmise par l'opérateur
(agent entraîneur), après le premier essai physique vNext et la tranche `Sx_REC_ROLLOUT_01`.

## 1. Pourquoi

Les règles actuelles se sont enrichies une par une : récupération par zone, couverture sur
quatorze jours, classement de gabarits, progression de charge, substitution, score de séance.
La revue conclut qu'il faut désormais **formaliser un moteur de prescription**, et **figer son
modèle de décision avant de curer les 107 exercices** — sinon la recherche exercice par
exercice produira des champs que le moteur ne sait pas lire.

## 2. Doctrine

> Personnaliser fortement ce que la science montre comme important ; ne pas feindre une
> personnalisation scientifique sur ce que la littérature ne permet pas de prédire précisément.

Conséquences, retenues comme contrat :

1. **Aucune moyenne de population ne devient un fait individuel.** Sexe, âge, ancienneté
   modifient des priors ; ils ne décident pas du programme.
2. **Toute règle et toute valeur portent deux étiquettes distinctes** : sa base de preuve
   (`STUDY_MEASURED`, `DERIVED`, `CONVENTION`, `UNKNOWN`) et l'origine de la donnée
   (`USER_OBSERVED`, `USER_REPORTED`, `POPULATION_PRIOR`, `DERIVED_FROM_HISTORY`). « Mesuré
   dans une étude » et « mesuré chez cet utilisateur » ne se confondent jamais.
3. **Un backend continu n'autorise pas un affichage continu.** Les estimations internes
   (charge résiduelle, écart de performance) restent derrière des bandes et des phrases :
   aucun score de préparation, aucun pourcentage d'activation.
4. **Pas de classement universel d'exercices** : le meilleur exercice l'est pour une intention,
   un utilisateur, une salle, un jour.
5. **Pas de score composite opaque** : chaque gagnant s'explique en une chaîne causale courte.
6. **Rejet des métriques perverses** comme objectifs d'optimisation : tonnage brut, nombre de
   séances, longueur de série de jours, séries pour elles-mêmes.
7. Déterministe, explicable, testable ; **aucun apprentissage automatique requis**.
8. **La science estime, le produit décide** : un modèle d'état (charge résiduelle, confiance
   dans le RIR) ne prononce jamais d'interdiction ; une politique séparée et nommée traduit
   l'état en décision.
9. **Une convention de comptabilité n'est pas une propriété** : le crédit de 0,5 série
   indirecte appartient à la politique d'exposition, pas à la fiche de l'exercice, qui ne
   déclare qu'un rôle (`PRIMARY / SECONDARY / MINOR / UNKNOWN`).
10. **Hiérarchie d'autorité** : contraintes dures → objectif → besoin → preuve propre à
    l'utilisateur → preuve de population → heuristiques produit → ordre du catalogue.
11. **Une dose de population n'est jamais une cible individuelle** (« ≥ 10 séries par semaine »
    est un prior, jamais un seuil de conformité) ; **aucune décharge planifiée** au seul motif
    du temps écoulé ; **l'e1RM est une tendance propre à un exercice**, jamais une mesure de
    force comparable d'un exercice à l'autre.

**Statut du contrat de recherche (2026-10-23)** : `READY FOR DEEP SCIENTIFIC RESEARCH — CORE
MODEL SCOPE FROZEN`. Aucun concept n'est ajouté au modèle avant les six livrables.

## 3. Les neuf couches, et l'existant (relevé du code, 2026-10-23)

| Couche | Fonction | Existant | Plus gros manque |
|---|---|---|---|
| E0 Registre de preuve | pourquoi une règle existe, son niveau de preuve | `epistemic.py` (`MEASURED / DERIVED / INFERRED / NOT_DEDUCIBLE`, une seule surface) ; trois autres vocabulaires de confiance | pas de `CONVENTION` ; aucune constante étiquetée |
| E1 Contexte utilisateur | objectif, historique, expérience, contraintes, matériel | `TrainingPreferences` ; mesures corporelles | le moteur servi ne lit que le matériel ; aucun objectif |
| E2 Graphe des exercices | biomécanique, zones, substitutions | EKB 107, atlas 32 machines, substitution N1–N3 | zones de gabarit = primaires ≥ 1/4 des exercices (`_primary_zones_of`) |
| E3 Registre d'exposition | dose directe et indirecte | fenêtres 24 h / 7 j / 14 j ; déficit relatif à la médiane | crédit indirect 0,3 arrondi (`muscle_scoring`) contre 0,5 (`set_contribution`) ; pas de 28 j ; pas d'enveloppe de référence |
| E4 Récupération / charge résiduelle | ce qui est encore fatigué | `zone_recovery` : heures / cible 24–72 h, trois bandes | temps seul : ni volume, ni effort, ni nouveauté |
| E5 Besoin d'entraînement | ce qui mérite d'être travaillé | `recommendation_v3.classer_candidats` (gabarits) | pas de besoin par zone contre une cible |
| E6 Compilateur de séance | exercices, ordre, séries, reps, effort, repos | `morpho_program_generator` (programmes) | la séance du jour reste un gabarit figé |
| E7 Autorégulation | charge série par série | `overload_engine` (5 états) | aucun RIR/RPE saisi ; repos fixe 90 s |
| E8 Modèle de réponse | ce qui marche pour cette personne | historique, « la dernière fois », étiquettes implicites | aucun e1RM ; aucun attendu contre observé |

## 4. Statut des règles en vigueur au regard de la doctrine

| Règle en vigueur | Statut V2 |
|---|---|
| Cibles de récupération 24 / 36 / 48 / 72 h | **priors de démarrage**, pas une autorité ; à remplacer par une charge résiduelle (E4) |
| D14 — rotation par récupération, cardio en plan B (`Sx_REC_ROLLOUT_01`) | **règle produit provisoire** pour muscle / force ; remplacée par la répartition par objectif |
| D12 — score de séance (volume 40, cibles 40, progression 20) | **retiré** (arbitrage opérateur, ruling 11) : trace de décision interne, performance par exercice contre l'historique personnel, assiduité au programme repos prévu compris — jamais une note unique |
| Séances utilitaires (`short-upper`, `no-equipment-full-body`) dans la rotation | **à sortir de la rotation** : modes de compilation sous contrainte de temps (`time_budget_minutes`) ou de matériel |
| Zones déclarées d'un gabarit (primaires ≥ 1/4) | **remplacées** par un vecteur d'exposition calculé depuis les exercices |
| Bandes `RECUPEREE / PARTIELLE / INSUFFISANTE` | la science estime une **charge résiduelle** (`LOW / MODERATE / HIGH / UNKNOWN`) ; une politique produit séparée décide ; `UNAVAILABLE` réservé aux contraintes dures |
| Régularité : programme d'abord, série active secondaire | maintenue ; la longueur de série n'est **jamais** un objectif d'optimisation du moteur |
| Charges de départ par sexe × ancienneté × exercice (brief initial) | **suspendue** : historique exact → transfert → calibration → prior large, à confirmer par le chercheur |

## 4 bis. Arbitrage opérateur des livrables A–F (2026-10-23)

Les six livrables ont été produits puis arbitrés par l'opérateur (14 rulings). Points
structurants, désormais contrat :

- **15 zones atomiques de comptabilité** : pecs, lats, upper_back, anterior_delts,
  lateral_delts, rear_delts, biceps, triceps, quads, hamstrings, glutes, adductors, calves,
  abs, hip_flexors. `posterior_chain` n'est plus qu'un regroupement de présentation ;
  l'interface n'expose pas forcément les 15.
- **Rôle d'un exercice** : preuve longitudinale d'hypertrophie, sinon action articulaire
  chargée + anatomie fonctionnelle, sinon `UNKNOWN` ; jamais l'amplitude EMG. Un `UNKNOWN`
  ne bloque que le rôle PRIMARY de **cette** zone ; contributions secondaires inconnues →
  `exposure_vector_complete = false`, sans invalider l'exercice.
- **Hors du catalogue** : le pas de charge (appartient à l'équipement réel de la salle) et la
  classe de repos (dérivée à la prescription).
- **Plan d'exposition versionné** : le moteur compare l'exposition réelle à une exposition
  **planifiée** (`PRESCRIPTION_GAP`), jamais à un « optimum biologique » ; la V2 n'infère pas le
  volume optimal individuel.
- **RIR** : aucune correction individuelle par la moyenne de population ; seul l'étalonnage
  propre à l'utilisateur établit un biais personnel ; saisie facultative.
- **Crédit secondaire 0,5** versionné, calculé à la lecture sur des comptes bruts.
- **Cardio** : plancher aérobie de premier rang pour `GENERAL_FITNESS` ; outil de planification
  de premier rang pour `FAT_LOSS_WITH_MUSCLE_RETENTION` (sans plancher OMS imposé) ; secondaire
  pour muscle / force.
- **Première exposition** : aucun coefficient générique de transfert entre exercices.
- **Score unique /100 retiré** (voir §4).

Livrables arbitrés : `reports/Moteur scientifique AUREN V2 arbitré.md` (hors dépôt, à
versionner avec la tranche qui les adopte). Prochaine étape : **curation des 107 exercices sur
GO opérateur**, selon le contrat d'entrée de ce document.

## 5. Ce qui débloque le build

Les six livrables du chercheur (brief « Brief — agent scientifique AUREN », mission V2) :
`SCIENTIFIC_ENGINE_V2.md`, `EVIDENCE_REGISTRY.md`, `TRAINING_DECISION_MODEL.md`,
`EXERCISE_UTILITY_SCHEMA.json`, `EXPOSURE_RECOVERY_MODEL.md`, `LOAD_AUTOREGULATION_MODEL.md`,
leur verdict (`SCIENTIFIC CORE READY FOR EXERCISE CURATION` ou
`SCIENTIFIC ARBITRATION REQUIRED`) et la liste des champs requis du catalogue. Les citations de
la revue d'origine sont des pistes à vérifier : aucune n'est reprise ici comme fait.

Ordre de build visé, une fois les livrables acceptés : E0 (registre unique) → E3 (crédit
indirect unifié, fenêtres) → E4 (charge résiduelle derrière les bandes existantes) → E1
(objectif) → E5/E6 (besoin puis compilateur) → E7 (calibration, RIR) → E8 (réponse,
écart de performance) ; la curation des 107 exercices après approbation des champs.

## 6. Non-goals

- Aucun code de production, aucune migration, aucune constante modifiée dans cette spec.
- Aucune curation d'exercice, aucune charge de départ chiffrée.
- Aucun score de préparation, aucun pourcentage d'activation, aucune affirmation médicale.
- Aucun apprentissage automatique.
