# RELEASE-01 — recette contrôlée du runtime livré

9 novembre 2026. Basefe9f6e9 après388/389. **QA_SYNTHETIC_AUTHORIZED /
NOT_DEPLOYED / PHYSICAL_ACCEPTANCE_OPEN.**

## Why

Le mandat DATA/RELEASE du9novembre demande de préparer et tester le runtime
PLAN/calibrage réellement fusionné, sans refaire science ou intégration et sans
traitement personnel/effacement irréversible. Une preuve HTTP, un simulateur
et un appareil physique sont trois niveaux distincts.

## What Changes

Plan de recette exécutable et reçus du backend/bundle/DB/config/builds exacts,
tests sur vrais consommateurs synthétiques, sécurité packaging contextualisée,
rollback sans perte de faits et matrice des gates restantes. Réutilisation des
scripts/runtime/tests existants ; scripts de banc privés hors produit.

## Non-goals

Aucun code produit/contrat SCI/UI, migration nouvelle, correction d'historique,
compte Store, credential production, déploiement ou activation réelle. Pas de
confirmation de politique du responsable. Pas de verdict physique depuis un
simulateur, Playwright ou HTTP. Les quatre checks et Sonar consultatif conservés.
