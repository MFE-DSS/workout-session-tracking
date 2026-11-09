# Proposal — account-data-activation / DATA-ACT-01

## Why

La [proposition réservée du 5 novembre](../../../docs/proposals/account-data-activation.md)
porte déjà DATA01–07, toujours ouverts. Il manque un paquet unique de décisions
du responsable incluant les copies PLAN V3 livrées depuis l'inventaire MOB03.
Ce change réutilise cette identité ; il n'ouvre pas un second projet d'effacement.

## What Changes

- Préparation DATA-ACT-01 seulement : questionnaire D01–D09, catégories C01–C11,
  graphe complémentaire des sept tables PLAN et copies locales/export/backups.
- Audit statique des fondations livrées et des manques réels, sans recréer le
  workflow isolé, ses capacités ni la chronologie corporelle existante.
- Faits de code, propositions et décisions OPEN restent distincts ; aucun
  fondement, durée, identité ou URL ne reçoit une valeur fabriquée.

## Capabilities

### New Capabilities

- `data/controller-decision-package` : paquet de décision documentaire et
  condition d'admission ; ne fournit pas de traitement opérationnel.

### Modified Capabilities

- Aucune spec produit modifiée : account-lifecycle et PLAN restent inchangés.

## Non-goals

Aucun code produit, test produit nouveau, migration ou accès à une base ; aucune
suppression, activation, collecte réelle, politique juridique admise, secret ou
donnée personnelle. Aucun nouveau parcours visible, baseline, Store ou déploiement.
DATA01–07 ne sont pas déclarés clos. Le build opérationnel devra préciser sa
propre évolution du présent change et recevoir revue/GO, sans apply implicite.

## Dependencies

Réponses signées du responsable D01–D09 et inventaire opérateur réel. Pour les
suites : politiques/copies approuvées, exception destructive explicite, revue du
producteur/migration, autorisation de build et déploiement distinct ; validations
UI/appareils lorsqu'applicables. Le GO MERGE permanent ne fournit aucun de ces GO.
