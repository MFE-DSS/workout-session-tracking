# Proposal — NUT-01 : journal manuel et cibles déclarées

11 novembre 2026, base `3cf77e17f37448980b115d8e0e0adad783c1d0b2`.
**PROPOSED / NO_GO_BUILD / G1_PENDING / NOT_SERVED.** Change existant conservé. Le mandat MVP remplace la priorité fournisseur/étiquette par un journal manuel autonome ; ancienne préparation sauvegardée, aucun produit préexistant réécrit.

## Why
Le pilote doit suivre ses apports et ses propres cibles sans attendre l'autorisation d'un fournisseur. Aucun ledger nutrition runtime canonique trouvé ; BodyMeasurement et les séances ne sont pas détournés. Le mode manuel constitue une tranche complète ; les modes assistés sont un futur contrat, pas une condition de clôture.

## What Changes
Journal quotidien agrégé déclaré kcal/protéines/glucides/lipides, champs inconnus et complétude explicites, corrections versionnées, historique/tendance factuelle ; cibles utilisateur générales ou entraînement/repos avec choix humain explicite. Une famille native dans Progrès, quatre tabs conservées. Deux tables serveur de révisions jour/cibles et une table locale de commandes exactes, pas photos/candidats/media/providers. Aucune prescription ni calories d'entraînement déduites.

## Capabilities
### New Capabilities
- `mobile/manual-nutrition-ledger` : apports quotidiens et cibles réellement déclarés, audit/reprise, sommes/tendance avec couverture.
### Modified Capabilities
Aucun moteur SCI, modèle corps ou contrat séance. Le domaine nutrition nouveau requiert GO propre/migration additive et politique DATA pour réel.

## Non-goals
Pas photo/étiquette/barcode/free-text exécuté, fournisseur, coût externe, catalogue d'aliments, portion implicite, 4/4/9 de remplissage, prescription/score, nouveau tab/palette ou APK/OTA. Acquisition future décrite séparément ; manuel ne dépend d'aucun de ces modes.

## Dependencies
BODY d'abord sur leases partagés, puis GO NUT/migration/G1/pixels/revue/CI. Le responsable doit décider traitement réel/copies avant activation ; un accord BODY n'autorise pas nutrition. Préparation synthétique seulement, aucune donnée/clé/deploy ici. Engineering complet quand le vrai natif écrit/relit son journal et ses cibles sur serveur réel ; pas depuis mock ou capacité future.
