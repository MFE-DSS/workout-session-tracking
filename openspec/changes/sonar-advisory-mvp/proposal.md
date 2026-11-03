# Proposal — GOV-SONAR-01 / sonar-advisory-mvp

## Why

L’opérateur a arrêté l’abonnement SonarCloud payant et arbitre une politique temporaire pendant le MVP natif :
Sonar devient consultatif. Le merge CODX-00 `60bea5d` a 8 jobs Actions verts mais une gate externe Sonar ERROR
sur une dette dont les totaux sont stables ; le rapport d’incident doit rester exact.

## What Changes

- Formaliser **TEMPORARY — MVP DEVELOPMENT**, Sonar **ADVISORY / NON-BLOCKING**, dans `CLAUDE.md §4`,
  le protocole de livraison, le contexte OpenSpec et une policy détaillée référencée au registre.
- Conserver tous les contrôles fonctionnels et de sécurité : Jest, TypeScript, backend, visuel, validation
  OpenSpec stricte, scope/spec protocol, Bandit, Gitleaks et audit des dépendances applicables.
- Préparer la suppression de `SonarCloud` des checks requis, sans retirer `pytest + QA scripts` ; proposer
  l’ajout des checks mobile, visuel et lint existants, après disponibilité vérifiée. Pas de bypass.
- Garder le scanner et son vrai résultat ; sa désactivation automatique serait une décision séparée.
- Imposer une revue sécurité/qualité avant bêta externe élargie, paiements, photos/mesures sensibles ou production.

## Capabilities

### New Capabilities

Aucune capacité produit. `skip_specs: true` : changement documentaire de gouvernance et proposition de protection.

### Modified Capabilities

Aucune spec produit ni baseline modifiée.

## Dependencies

La politique doit être livrée par sa propre PR et intégrée sous GO MERGE distinct avant d’être considérée
canonique. Le GO MERGE #347 reste acquis ; son sweep CI_INFRA complet sur sa base effective demeure requis.
L’application de la protection exige les droits administrateur et une relecture API avant revendication.

## Non-goals

Pas de correctif produit, migration, UI, baseline, changement de seuil Sonar ou résolution automatique d’issues.
Pas de scan supprimé, abonnement/compte modifié ou assouplissement des contrôles de sécurité.
Pas de build MOB-02. Aucune évaluation exhaustive de sécurité revendiquée.

## Impact

Contrats/documents normatifs et contexte OpenSpec uniquement ; workflows et code métier conservés à l’identique.
Le payload de protection est préparé pour revue, son application n’est pas confondue avec sa préparation.
La validation OpenSpec demeure une obligation locale explicite : aucun job CLI OpenSpec n’existe actuellement
dans le workflow, et ce changement ne prétend pas en avoir créé un.
