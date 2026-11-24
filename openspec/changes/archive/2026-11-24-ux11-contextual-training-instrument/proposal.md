# UX11 — Contextual Training Instrument

## Why
UX10-01 a prouvé l’identité propriétaire, les commandes et la reprise ; ses pixels restent non acceptés. L’athlète doit pouvoir consulter une observation pertinente sans quitter l’exercice, saisir son fait actuel et comprendre son enregistrement. Une autre retouche cosmétique UX10-R3 ne répondrait pas à ce besoin.

## What Changes
Proposition bornée : un instrument pour `leg-extensions-assises` V3 bilatéral, réglage `MACHINE_DISPLAY_KG`. La série immédiatement précédente du même exercice et de la même occurrence, relue du serveur et sous contexte enregistré intégralement identique, peut être présentée en référence secondaire. Brouillons actuels vides et indépendants. Retour d’enregistrement situé dans le même instrument ; l’acquittement et la relecture restent distincts.

Aucune comparaison entre séances : l’index historique reste NON_COMPARABLE. Legacy/adduction est inéligible, son contexte manque. Aucune prescription, variation de charge, score ou interprétation biologique nouvelle.

## Impact
Présentation ConnectedApp/PlanV3Host/PlanV3ExecutionScreen, nouveau composite et resource read-only utilisant les API existantes, tests ciblés et broad consommateurs. Aucun backend, migration, schéma, SCI, TIME-01, contrôleur de mutations, SQLite, primitive, dépendance ou release modifié.

## Status and gates
AUTHORIZED_IN_EXECUTION / GO_BUILD_ACCEPTED / G1_ACCEPTED / PIXELS_PENDING. Ce paquet expose une nouvelle convention d’affichage dans CONTRACT_RECONCILIATION.md, pas une admission scientifique. Un change/une PR après GO et pixels. UX10-01 préservé et non clôturé artificiellement ; DA09.1 et QA installé intacts.
