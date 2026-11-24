# UX11 Implementation Plan

> For agentic workers: REQUIRED SUB-SKILL superpowers:executing-plans. Exécution inline déjà demandée par l’opérateur ; pas de micro-GO entre tâches. Commit différé au gatepixels du repo.

**Goal:** une référence brute admissible disponible dans Action, puis un reçu situé, pour leg-extensions-assises V3.
**Architecture:** resource read-only existant TrainingHistoryClient, sélection de contexte stricte et composite de présentation. Contrôleurs, horloges, sync, SQLite et SCI inchangés.
**Tech Stack:** Expo58/RN0.88/React19.3, mêmes dépendances ; @expo/ui absent, aucun ajout natif.
**Spec:** design.md, COMPARATIVE_SOURCE_CONTRACT.md et UX_BOARD.md de ce change.

## Global Constraints
Même occurrence/owner/backend/binding/exercice, source d’indice courant−1 seulement ; bilatéralMACHINE_DISPLAY_KG/MASS_KG/kg. Pas de préremplissage. Incertitude d’envoi combinée. Pas d’API/DTO/backend/domaine/contrôleur/TIME/sync/SQLite/primitive/dependency/OTA. UI non committée avantpixels.

## Review Focus
RéponseA aprèsB ; révision source annulant sa complétion ; UNKNOWN égal àUNKNOWN ; ACK sans fait courant relu ; curseur qui avance hors exercice pendant feedback.

### Task 1: Source située
Files create src/ui/contextual/referenceModel.ts, referenceRead.ts et tests. Consumes PlanV3Stored, HistoricalDetail, TrainingHistoryClient sessions/detail. Produces ContextTarget, selectReference(target,detail), readContext(reader,target,current) ; sélection de série et métadonnées distinctes index/détail.
- [x] RED: même source positive17,5/9 ; refus crossowner/session/binding/exercice/contexte/unité/révision/noncompleted/source locale ; précédent exact seulement.
- [x] GREEN minimal selector et lecture paginée≤5×100, annulation et unknown ; pas d’effet mutation.
- [x] Tests du vrai TrainingHistoryClient sur son boundaryHTTP et filtre de compte, broad pertinent.

### Task 2: Instrument et branchement
Files create useContextRead.ts, ContextualInstrument.tsx, ContextualPrimitives.tsx/tests. Modify uniquement PlanV3ExecutionScreen/Host et ConnectedApp construction/props. Consumes target, readContext et callbacks actuels. Produces une branche pour l’exercice éligible avec pin du set soumis, champs indépendants, clavier/Retour/annulation et sources dépliables.
- [x] RED: champs vides malgré référence ; édition préserve l’autre champ ; unevalidation au temps du clic ; pending/refus/ACK/read distincts ; focus du set soumis conservé quand le curseur avance ; cas sans source.
- [x] GREEN: code natif avecAUREN LOCKED existants et abonnements resource read-only.
- [x] Vérifier actions/rest/setup actuels et invalidations source au background/owner/version ; TS et broad consumers.

### Task 3: Preuve et gate
- [x] check_scope puis contrôles requis, Jestmobile/TS, backend ciblé si impact réel, visuelLOCKED et sécurité.
- [x] Revue indépendante du diff entier, correctifsImportant RED→GREEN.
- [x] Copie de banc synthétique, vrai ConnectedApp Android, avant/aprèsmêmesfaitsV3, référence/absence/pending/refus/ACK/read,360/480/grande fonte/IME/Retour. Mesurer activations et transitions sans gain inventé.
- [ ] Max8captures+vidéo, source/UUID/révision, limites et décisionpixels unique.
- [ ] Aprèspixels seulement : commit/PR/CIexacte/mergeGOV/closeout. AucunOTA.
