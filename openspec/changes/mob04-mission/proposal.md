# Proposal — MOB-04, ouverture MISSION propriétaire

## Why

MISSION historique est réellement branchée, mais sa décision READY n'est pas une décision SCI V3. Le premier parcours et sa séance typée existent désormais sous contrôle ; Aujourd'hui doit orienter vers la bonne commande sans reproduire un moteur ni présenter une disponibilité fictive.

## What Changes

- Un résolveur de présentation serveur propriétaire, additif et en lecture seule, séparé de la décision scientifique et du read-model historique.
- Un consommateur natif Aujourd'hui explicite sur la source demandée, avec reprise prioritaire, actualisation, états absents/inconnus et délégation au contrôleur de séance existant.
- Aucun changement du style MISSION LOCKED. Une famille de nouveaux états d'orientation est proposée dans UX_BOARD.md ; G1 puis vrais pixels restent requis.

## Capabilities

### New Capabilities
- `mobile/mission-projection` : projection possédée des sources/actions existantes, sans nouvelle admission ni prescription.

### Modified Capabilities
Aucune. Les contrats V1/V3 et le calibrage sont conservés.

## Non-goals

Pas de nouvelle science, score, programme, séance supplémentaire, adaptation, calendrier, import, inventaire matériel obligatoire, nouvelle table, migration, activation réelle ou déploiement. Pas de repli scientifique vers une MISSION historique. Programmes et historique global relèvent de leurs changes.

## Impact

Nouveaux service/router/client/ressource de projection et branchement limité ConnectedApp/ShellProvider. Pas de Jinja copié, dépendance ou baseline éditée. Voir BUILD_SCOPE.md pour les leases et les tests. **PROPOSED / NO_GO_BUILD / G1_PENDING**.

## Authority

Base `2b83141106405f004f6447db3adcdadce88761a7`. Réutilise `docs/proposals/mob04-mission.md`, sans réécrire sa photographie du5novembre. Le brouillon ARCH non fusionné du même change dans `/private/tmp/auren-arch-po-packs-01` a été lu comme préparation antérieure, pas comme GO ni contrat servi ; aucun de ses fichiers n'est modifié. Cette préparation actuelle doit être réconciliée avec son propriétaire avant livraison concurrente ; une seule ligne d'apply/PR pour MOB04. GOV-MERGE-01 ne fournit pas le GO BUILD manquant.


Réconciliation du mandat PILOT VALUE DELIVERY du10novembre : [PILOT_VALUE_SCOPE](PILOT_VALUE_SCOPE.md) précise base canonique, option de navigation B, commandes locales et leases séquencés. Statut toujours NO_GO_BUILD/G1_PENDING.
