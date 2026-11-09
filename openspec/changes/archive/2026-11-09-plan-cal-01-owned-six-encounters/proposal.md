# PLAN-CAL-01 — six rencontres SCI vers le runtime propriétaire

9 novembre2026. **PROPOSED / NO_GO_BUILD / NOT_ACTIVATED.** Base après fetch :
`692d4c8e9af2dcdb5f912eff6b9fb2b158089c0c`. Branche spec/plan-cal-01, isolation
/private/tmp/auren-plan-cal-01 ; checkout opérateur61ca08c et travaux ARCH/QA préservés.

## Why

SCI386/387 est CLOSED+CLEANED : six politiques admises avec limites existent,
mais le runtime PLAN379/380 charge seulement le pilote. Sa preuve initiale
utilisait des observations synthétiques pour les six autres, pas leur acquisition
guidée. Relier ces nouveaux évaluateurs aux vrais consommateurs propriétaires
permet de préparer un premier plan sans sept réglages à l'ouverture.

## What Changes

- Inventaire privé de rencontres v2 explicite : pilote conservé + six extensions,
  mêmes formats encounter1.0.0 et SCI V3. Bundle neuf immuable, worker attesté,
  vrais load/evaluate/validate ; aucun compile_candidate ou checkout fallback.
- Même ledger : préparation/choix/familiarisation au réglage/essai/acceptation,
  sélection explicite du contexte courant et invalidation propriétaire. Pas de
  table, migration, seconde chronologie ou moteur scientifique nouveau.
- Projection de snapshot : permission actuelle réellement revérifiée pour les
  rencontres guidées, sans prendre ancien essai qualifié pour choix courant.
- Négociation et consommateurs natifs du profil d'inventaire, reprise et commandes
  durables existantes ; mots/formulaires propres aux six réalisations sous UX-CAL.
- Preuve HTTP hermétique et native contrôlée : sept vraies acquisitions sur
  comptes/entrées synthétiques isolés → snapshot → vrai V3 → ack exact → même
  séance possédée après réponse perdue → exécution/journal canoniques.

## Scope boundary

Le build contrôlé reste APP_ENV=test et flags off par défaut. Aucune donnée
personnelle, activation réelle, déploiement, Store ou recette physique. Sources
SCI, hashes historiques, SDK scientifique V1 et baselines LOCKED read-only.
MOB03 global/DATA/RELEASE restent ouverts. GO BUILD et croquis UX-CAL nécessaires
avant apply/composition ; vrais pixels soumis avant commit UI. GOV-MERGE-01
couvre ensuite toute la livraison du scope autorisé, sans GO MERGE routinier.

[Design](design.md), [lease et acceptations](BUILD_SCOPE.md),
[tests réels spécifiés](TEST_SPEC.md), [croquis UX-CAL](UX_CAL_BOARD.md).
