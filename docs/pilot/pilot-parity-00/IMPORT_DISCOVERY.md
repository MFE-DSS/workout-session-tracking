# Migration pilote — découverte avant import

**DESIGN_ONLY / SOURCE_EXPORT_NOT_RECEIVED / NO_IMPORT_IMPLEMENTED.**

## Ce qui est effectivement disponible

Outil source : nom/URL/contrôle/export inconnus dans les pièces reçues. Aucune API, CSV/JSON ou possibilité de télécharger les PDF d'origine n'est supposée. Le dépôt AUREN possède des exports de séances et de corps, pas un importeur de l'outil pilote. L'export corps actuel a sa limite10k et omet certains champs historiques ; il ne doit pas être annoncé comme dossier complet sans contrat corrigé.

Première découverte à réaliser avec l'opérateur/pilote : fonctions d'export réellement accessibles, échantillon de schéma contrôlé, propriétaires et identités de source, unités, périodes/fuseaux, dates de mesure versus saisie/modification, IDs stables et versions, programme actif versus brouillon, estimations de balance versus mesure. Collecter seulement après autorisation/finalités applicables ; pas de credentials tiers demandés ou export personnel aspiré automatiquement.

## Proposed secure route — future IMPORT-01, not an API served today

1. Réception privée d'un fichier autorisé et référence de source/version ; contrôles format/taille/document actif, hash de transport et droits. Pas de donnée personnelle/fichier source dans Git ni logs publics. Retenir l'original seulement sous politique de rétention approuvée, jamais « sauvegarde indéfinie » par défaut.
2. Prévisualisation sans écriture canonique : mapping par champ, unité, précision/date/fuseau, nature déclaré/mesuré/estimé, propriétaire source/cible et liste des lignes rejetées avec motif/position expurgés. Timestamp naïf ou unité ambiguë reste erreur de mapping, pas inférence. Une balance « muscle » conserve son mesurande/méthode ; pas promotion en tissu musculaire.
3. Identité durable : `(authenticated_owner, source_system, source_owner_ref, source_record_id)` ; version/digest de contenu séparés. Nom/email venant du fichier ne choisissent pas le compte. Source_owner_ref ambigu : refus jusqu'à résolution explicite, aucun rattachement heuristique. Si pas d'ID durable, ne pas dédupliquer deux pesées légitimes par date/valeur seulement ; définir/revoir une identité avant commit.
4. Confirmation humaine d'un manifeste immuable des lignes acceptées et de leurs digests. Rejets restent visibles ; leur absence de commit n'est pas un succès silencieux. Commit transactionnel du sous-ensemble exactement confirmé avec clé durable et body digest ; retry exact renvoie ses reçus, corps différent sous même clé409, aucune double ligne. Nouvelle version source est une correction liée/revue, pas un overwrite implicite. Conflit de révision de cible détecté avant mutation.
5. Import dans le domaine canonique uniquement, source/source_ref/dates et méthode conservées. Pas de seconde série poids ou de deuxième journal séances. Aucune observation historique importée ne devient acceptation actuelle de calibrage. Aucun per-haltère/machine→kg total. Les champs dont le contrat n'existe pas restent rejetés/en attente, pas perdus ou recomputés.
6. Résultat propriétaire : reçus par ligne/lot et compte accepté/rejeté/ignoré/déjà importé ; possibilité de relire après réponse perdue, sans nouvelle identité. Un rollback de l'UI ne détruit pas l'histoire ; aucune purge/annulation destructive inventée pour « annuler un import ».

## Training PDF

Extraction future → **UserProgram draft révisable**, références de document/version/pages, champs incertains/manquants et différences explicites. L'utilisateur corrige ; validation domaine/publication existantes seulement après revue. Le résultat du LLM n'est pas une admission scientifique ni une commande de travail. Pas d'activation du programme, de charge, de qualification, d'ack ou de série faite depuis l'extraction. Appel de fournisseur/LLM externe, document privé et coûts exigent leur scope/permissions propres.

## Acceptance before any real migration

Exporter réellement depuis l'outil source, tester sur versions/unités/dates connues, doublons et corrections, mauvais owner, mêmes valeurs légitimes distinctes, champs inconnus, payload altéré/retry/perte réponse, transaction/rejets, export/restauration/exclusion et données partielles. Tous tests d'abord synthétiques ou échantillons explicitement autorisés. DATA doit admettre source/backups/staging/copies/reçus/effacement ; aucune durée/finalité/base légale choisie par l'agent. Les APIs mentionnées ici sont étapes conceptuelles, aucun endpoint n'est créé dans cette préparation.
