# MOB-06 — reprise de la branche et fin de la réservation Maltin

12 novembre 2026 — Europe/Paris. Delta documentaire autorisé par la décision
opérateur ci-dessous. Aucun code produit, rendu, migration, APK ou déploiement.

## Décision opérateur

Réponse à `call_7f3a180e5cd14150b24dfe2a5927c3ea` :

> non tu vas reprendre cette branche et oublié maltin qui était une branche pour tester un service de gouvernance spec driven que j'ai abandonné

L'opérateur abandonne l'essai de gouvernance Maltin et demande de reprendre la
branche existante `feature/bibliotheque-seances`. Aucun passage de relais,
registre signé ou décision dans Maltin n'est désormais requis pour cette tranche.
Les questions O-1–O-8 de l'ancienne déclaration ne sont pas transformées en
réponses opérateur : le cadrage reprend les demandes produit et les domaines
canoniques sous OpenSpec, en exposant les vrais choix encore nécessaires.
La précédente proposition « consultation d'abord » n'a pas été acceptée par
cette réponse et ne doit pas devenir une restriction implicite du mandat MVP.

## Brainstorming / Options / Risques / Choix retenu

- Maintenir le verrou Maltin contredirait la décision reçue : option écartée.
- Effacer les archives ou réécrire la branche ferait perdre la preuve historique :
  option écartée.
- Choix retenu : conserver les traces, lever explicitement la réservation dans
  les documents courants et reprendre la même branche sous OpenSpec/AUREN.

La réservation historique est conservée dans Git :
[roadmap au commit 1000d2e](https://github.com/MFE-DSS/workout-session-tracking/blob/1000d2e56b273a31400b8458a4e96c30bfc3810c/docs/strategy/AUREN_MOBILE_CRITICAL_PATH_2026_11_03.md#réservation-maltin--mob-06-bibliothèque-de-séances).
Les fichiers du test Maltin et les reçus des livraisons antérieures sont laissés
intacts. Leurs mentions de réservation décrivent leur date, pas un verrou actuel.

## Reprise Git contrôlée

Fetch du 12 novembre : canonique
`3cf77e17f37448980b115d8e0e0adad783c1d0b2`. Branche locale et distante
`feature/bibliotheque-seances` initialement sur
`b9a334d22e6b75e9b83650eb1b2b833d4ed5d169`, sans commit unique par rapport au
canonique (35 commits de retard, zéro propre). Worktree dédié durable :
`/Users/martinfeldmann/auren-review/mob06-library-20261112`.
Avance rapide normale au canonique, sans reset, rebase ou force-push.

Le checkout opérateur et les worktrees BODY/NUT restent intacts. La branche de
bibliothèque sera conservée pour la suite, y compris après la livraison de cette
correction documentaire ; aucun nettoyage ne doit la supprimer par routine.

## Contrats toujours applicables

OpenSpec, Visual Contract, UI Iteration Protocol, CI et GOV-MERGE-01 restent les
seules gouvernances applicables du dépôt. Le périmètre fonctionnel et son design
restent à cadrer avant implementation ; les validations G1/pixels et les conditions
scientifiques ne sont pas accordées par la levée d'un essai de gouvernance.
Aucune recommandation, compatibilité d'équipement, séance réalisée ou permission
hors ligne ne se déduit d'une ligne de catalogue ou d'un programme possédé.

La reprise suit le mandat MVP : rendre la bibliothèque et les programmes
réellement utiles au pilote, puis le constructeur personnel canonique, en
préservant faits planifiés/exécutés, identité des exercices et reprise possédée.
Les sources partagées ConnectedApp/mobile_api/journal sont séquencées avec
BODY/NUT ; pas de PR de code concurrente et pas de second moteur scientifique.
Aucun nouveau GO BODY/NUT ni GO MERGE routinier n'est demandé.

## Vérification et livraison

Le diff de cette reprise est uniquement documentaire. Exécuter check_scope,
appliquer son tier, puis check_spec_protocol et relire le diff avant commit.
La CI de PR reste obligatoire selon ses déclencheurs ; un push canonique
100 % docs ne déclenche pas de run sous paths-ignore. Ne pas inventer de run.
La PR pourra être fusionnée par commit de merge après ses contrôles exacts,
sans bypass et sans demander un GO MERGE supplémentaire.

La livraison de cette décision ne ferme pas MOB-06, BODY, NUT, REL-03 ou le MVP.
