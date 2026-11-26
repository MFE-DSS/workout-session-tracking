# SCI-RUNTIME-01 — préparation de qualification

26 novembre 2026. Parent vérifié : `9ef96e39aac400bc53583f62aecafc09f4dda1e3`.

**BUILD_AUTHORIZED_IN_PROGRESS / RUNTIME_HOLD / NO_ACTIVATION.**

Acte exact : [BUILD_AUTHORIZATION.md](BUILD_AUTHORIZATION.md),26 novembre2026. Les preuves d'analyse précédentes restent historiques.

## Why

BUILD-01 est clos. Son catalogue échoue sur une note de 4 302 octets et son image cible n'est pas qualifiée. Cette tranche vérifie les causes, compare les trois adaptations demandées et prépare un seul amendement minimal sans réimplémenter le lecteur.

## What Changes

Préparation documentaire et expériences jetables, sur données synthétiques et sources Git attestées. Aucune modification de app/, data/, tests/, deploy/, CI, mobile ou du VPS. L'éventuel adaptateur produit et son harness de qualification nécessitent un GO distinct sur le paquet exact.

## Brainstorming / Options / Risques / Choix retenu

Comparer (1) projection sélective avec digest intégral, (2) lecture incrémentale intégrale sous les mêmes plafonds, (3) hausse de plafond uniquement si les deux premières approches ne préservent pas les invariants. Ne pas confondre validation du document entier et matérialisation des seules données consommées. Le choix final dépendra des parités et contre-exemples, pas du seul cas nominal.

## Gates

Lecteur désactivé ; aucune admission SCI nouvelle, donnée réelle, activation QA, OVH, APK ou OTA. Runtime HOLD si OS/architecture/Python/SQLite/image/contraintes ne peuvent être reproduits. PILOT-01 et le G1 artistique restent indépendants.
