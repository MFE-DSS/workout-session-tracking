# MOB-03 — correction de placement des reçus visuels

5 novembre 2026. Correction dans le périmètre autorisé, aucun comportement produit modifié.

## Constat et preuve

Run 42042770262, job `pytest shard 1`, étape `Run pytest with coverage` : `test_no_raw_binary_source_in_git_docs` échoue sur les trois captures MOB-03 rangées sous docs/evidence. Résultat du lot : 1 failed, 2486 passed. Les deux autres lots, les contrôles mobile/visuel/lint réussissent. Le job agrégé échoue ensuite sur `Fail if any shard failed`. Sonar n'a pas été exécuté dans ce run.

Reproduction locale : 1 échec, 14 réussites dans le module de politique de sources. Les images étaient des rendus de notre interface ; la garde interdit néanmoins leur emplacement dans docs, hors exception UIV3 précise. L'erreur est le placement choisi lors de la conservation des preuves.

## Brainstorming / Options / Risques / Choix retenu

Élargir l'exception du test affaiblirait une règle existante ; supprimer les preuves perdrait le rendu accepté. Choix : conserver les captures, identiques, dans `clients/mobile/visual-contract/review-receipts/mob03-account-v1/`, distinct des baselines. Corriger les liens du rapport et ajouter un reçu d'origine. Aucune modification du test, du workflow, du moteur, de la UI ou des données.

Le nouveau modèle de préférences en préparation reste non committé pendant cette correction ciblée. Aucun nouveau composant de composition n'est ajouté sans validation du croquis.


## Vérification locale du correctif

33 tests de politique de sources et gouvernance visuelle passent, deux avertissements de dépendances. Les trois images sont identiques octet pour octet avant/après déplacement. Protocole et diff contrôlés avant commit. Aucun test de politique élargi ou désactivé ; validation de la CI réelle du nouveau HEAD encore requise.
