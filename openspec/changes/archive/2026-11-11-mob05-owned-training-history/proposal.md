# Proposal — MOB-05A / Progress Core

**PROPOSED / NO_GO_BUILD / G1_PENDING**, 10 novembre 2026, base b9a334d22e6b75e9b83650eb1b2b833d4ed5d169. Le change existant mob05-owned-training-history est réconcilié pour la tranche A ; aucun deuxième change historique concurrent.

## Why

Le pilote dispose d'une vraie séance et de son journal typé, mais l'onglet Progrès reste un PendingSpace. Une surface compacte doit rendre accessibles les faits possédés, la fréquence réelle sur une période explicite et la chronologie BodyMeasurement déjà disponible, sans confondre charge machine/haltère/total, prescription et réalisation.

## What Changes

- Quatre GET propriétaires paginés de liste/détail/index/occurrences, sans mutation ; source canonique WorkoutSession/SessionExercise/SetLog et binding SCI.
- Un seul espace Progrès : séances récentes, période, exercice et poids ; lectures mémoire owner-bound, reprise réseau honnête et drill-down read-only.
- Réemploi du GET /me/body/weight-history et de WeightHistoryClient/Resource existants, consentement/flag respectés ; trend = points datés bruts, pas moyenne ou recommandation nouvelle.
- Compatibilité des charges explicite : contexte exact connu seulement, legacy sans contexte non comparable, faits SCI typés conservés ; aucun score/delta/record nouveau.

## Capabilities

### New Capabilities
- `mobile/training-history` : lectures possédées, fréquence factuelle et composition native de Progress Core avec la chronologie poids existante.

### Modified Capabilities
Aucun contrat SCI/V3/Body modifié ; façade additive. Le calendrier prescrit non persisté est indisponible, pas reconstitué depuis la cadence ou les templates.

## Non-goals
Pas de writer/second modèle poids, nutrition, cible corporelle, moyenne7jours, 1RM, score de croissance, qualité/continuité SCI, import, calendrier de programmes, cache SQLite neuf, migration, dépendance, palette, onglet ou baseline nouvelle. BODY01/NUT01 restent des propositions distinctes ; DATA et déploiement séparés.

## Impact

Voir design.md, BUILD_SCOPE.md, TEST_SPEC.md et UX_BOARD.md. PR après MOB04 et relecture canonique des fichiers partagés ; aucune PR chevauchante. GOV-MERGE-01 ne fournit pas GO BUILD ni validation visuelle.
