# UX-CAL-02 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Rendre le calibrage partagé compact, fermer les deux mineurs et conserver la chaîne propriétaire réelle.
**Architecture:** Compatibilité/aide côté client puis composition locale sur vrais contrôleurs. Aucune mutation du moteur/transport serveur.
**Tech Stack:** React Native/Expo58, TypeScript/Jest, SQLite existant, vrais consommateurs HTTP de test.
**Spec:** [design](design.md), [scope](BUILD_SCOPE.md), [G1](UX_CAL_BOARD.md), [GO](BUILD_AUTHORIZATION.md).

## Global Constraints

- Base fe9f6e9 ; scope/GO/G1 reçus. Pas de re-question routinière de plan/merge.
- SCI/V1, workers, backend, API JSON, inventaire2, DB et baselines read-only ; pas de dépendance/asset nouveau.
- Aucun commit UI avant nouvelle acceptation pixels. L'implémentation locale et tests sont autorisés ; aucun déploiement.
- UNKNOWN et faits choisis/utilisés/occurrence/acceptation distincts, aucune charge/incrément ou permission déduits.
- Portes actuelles SCI, propriétaire, source_revision, génération/auth et reçu idempotent restent autoritaires.
- check_scope avant checks. Tests ciblés et broad consommateurs ; pas de full backend local pour shared_code/isolated.
- Pas de sousagents par le worker ; revue contrôleur après rapport. Aucun appareil/serveur natif démarré par le worker sans attribution pour éviter la recette parallèle.

## Review Focus

- DTO structurellement valide mais candidat/intent/realization/policy/type incohérent : aucun guidage, faits conservés.
- Aide demandée avant ouverture ou source/hash/section dérivée : pas de mutation ni procédure d'un autre mouvement.
- Brouillon ancien/partiel, reçu après réponse perdue, changementA/B : pas d'effacement, date neuve ou formulaire réouvert.
- Grande fonte/clavier/back : action requise lisible et atteignable sans confirmation implicite.
- Observation historique et autorité retirée : lecture/faits restent séparés de nouvelle permission.

### Task 1: Compatibilité négociée et aide applicable

**Files:** api/firstPlanV3.ts, calibrationV1.ts, firstUseV3.ts, nouveau api/calibrationProfilesV2.ts ; typesclient si requis ; nouveau ui/plan/calibrationHelp.ts ; tests voisins. Tous sous clients/mobile/src et scope.
**Consumes:** DTO réellement servis et autorités existantes ; designD3/D4.
**Produces:** helpers de validation/liaison du profil et projection d'aide typés, intégrés aux vrais ports ; noter leurs signatures exactes au rapport pour Task2.

- [ ] Écrire puis reproduire RED les tuples incompatibles pour les sept profils (omission/doublon, intention/réalisation/policy/type/version), sans exiger de champs non servis.
- [ ] Implémenter liaison des projections et rencontre aux capacités du même propriétaire, négociation effective, aucune permission sur erreur ; préserver le pilote non négocié et faits sans autorité.
- [ ] RED→GREEN aide préalable et projection source textuelle contrôlée : commun/sectionexacte/arrêt, chaque candidat, source/hash/section absent ou dérivé ; aucun POST d'ouverture.
- [ ] Exécuter ciblés puis broad des clients/contrôleurs/projections qui consomment ces fonctions, TypeScript ; consigner RED/GREEN et signatures.
- [ ] Self-review et rapport sans commit pour permettre revue du diff avant pixels/PR. Ne pas toucher les composants de composition Task2.

### Task 2: Instrument compact réellement consommé

**Files:** ui/plan/calibrationInstrument.tsx, calibrationModel.ts, calibrationEncounterInstrument.tsx, PlanV3FirstUseScreen.tsx, nouveaux calibrationLayout/Controls locaux et tests. Dépend de Task1 revu.
**Consumes:** signatures de Task1 et mêmes callbacks/ledger existants.
**Produces:** composition locale G1 ; observation deux sections avec champ UI optionnel compatible ; vrais écrans branchés.

- [ ] RED→GREEN consommateur : une action dominante, faits sans défaut, readoutunité unique, ouverture aide avant rencontre, arrêt accessible et aucun ack implicite.
- [ ] Reproduire G1 avec commandes48extensibles, fenêtre112minimum dynamique, détails progressifs ; conserver primitives et autres branches.
- [ ] Tester interruption/reprise anciens/nouveaux drafts, reçu exact après perte de réponse, changementA/B et contexte ; payload factuel identique ; clavier/focus/back/reducedmotion.
- [ ] Ciblés et broad mobiles/types ; rapport avec delta, source labels et limites avant capture native. Aucun commit UI.

### Task 3: Recette, pixels et livraison

**Files:** tests/consommateurs existants dans scope, docs/plan/ux-cal-02, receiptvisuelux-cal-02 et archive.
**Consumes:** Task1/2 revus, environnement de recette propriétaire isolé attribué par le contrôleur.
**Produces:** board natif réel accepté puis PR/merge/closeout canonique.

- [ ] Mesurer comparatif aux états/dimensions identiques ; iOS/Android360/390/480, fontes130/200%, clavier décimal/back/AX et drafts ; étiqueter limites physiques.
- [ ] Prouver la chaîne sept acquisitions → vraiV3/ackexact → même séance après réponse perdue via les vrais consommateurs ; aucune fixture servie.
- [ ] Revue globale code/interfaceSCI, correctionsRED→GREEN ; soumettre boardetobtenir pixels avant commitUI.
- [ ] Checks locaux du tier, commit/push/PR ; CI réelle du HEADfinal, mergegardeSHA, canonique/Sonar réels, archive/closeout/cleanup sans travail unique. DATA/RELEASE distincts.
