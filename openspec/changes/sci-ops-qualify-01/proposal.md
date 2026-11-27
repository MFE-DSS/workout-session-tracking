# SCI-OPS-QUALIFY-01 — paquet exact avant activation

## Why
Le canonique revérifié le 27 novembre 2026 est `1ac401f44b8af9444a8521b30cd47b7201fd1c8e`. SCI-RUNTIME-03 est clos. Son candidat Linux utilisait une image historique et un montage de source : cette preuve ne qualifie pas une image de déploiement reconstruite.

## What Changes
- Préparer le contexte Git exact, ses empreintes et la campagne sur image immuable, avec les outils REL-03 existants.
- Qualifier séparément image, sources, chemins, montages et ressources ; ne pas transférer les PASS du banc précédent.
- Soumettre le seul delta opérationnel nécessaire : un PREPARE_IMAGE protégé, garde privée, acquisition et qualification dans un banc natif neuf sur le VPS existant.
- Garder l'activation QA et le raccordement du lanceur sous un acte ultérieur.

## Capabilities
### Modified Capabilities
- `science/documented-muscular-exposure`: preuve du paquet opérationnel exact, distincte de la qualification du lecteur en banc.

## Impact
Préparation documentaire et preuves privées uniquement à ce stade. Aucun changement app/tests/CI/Dockerfile, SCI, DTO, SQL, TIME-01 ou client. Aucun service QA modifié. [Décision opérationnelle précise à soumettre](OPERATIONAL_DELTA.md).

## Non-goals
Pas d'activation, déploiement du service QA, nouvelle infrastructure payante, nouvel APK/OTA, collecte réelle, optimisation CPU supplémentaire ou réouverture de BUILD-01/SCI01/02/03.

## Amendement V3 admis — 27 novembre 2026
Le paquet exact a révélé la fuite d’un contexte interne à six propriétés dans le DTO fermé à cinq. Le GO explicite enregistré dans AUTHORIZATION.md autorise le seul correctif provenance.py et ses deux modules de tests (BUILD_AMENDMENT.md), sans modification de contrat SCI/DTO ni nouvelle opération de déploiement. Les mentions de préparation ci-dessus conservent leur chronologie.
