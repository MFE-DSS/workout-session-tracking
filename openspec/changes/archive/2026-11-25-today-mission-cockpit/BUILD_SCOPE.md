# Scope autorisé — pixels avant commit UI

## Autorité
Préparation demandée après DA09-B/C. Choix acquis : « Préparation dans le même instrument ». GO BUILD, amendement MISSION et G1 approuvés explicitement : « Autoriser le scope, l’amendement et G1 ». AUTHORIZATION.json conserve la décision ; les pixels corrigés sont ACCEPTED_SCOPED par la décision explicite du25novembre, conservée dans PIXEL_ACCEPTANCE_20261125.json.

## Fichiers autorisables
Nouveau composite et tests sous clients/mobile/src/ui/mission/ ; MissionActionHost.tsx et son test ; raccordement minimal de présentation dans ConnectedApp.tsx et ses tests, après vérification des leases. MissionScreenV1, ses quatre fixtures/baselines, assets de géométrie, contrôleurs, ressources/transport/SQLite, TIME01 et SCI sont hors écriture. Le registre visuel pourra documenter la nouvelle autorité spécifique après l’amendement, sans modifier les primitives. Aucun nouvel état métier ou permission.

## Preuve et livraison
Un croquisG1 unique puis preuve ConnectedApp Android360/480dp et178,6%, mêmes fixtures sourcées : READY fermé/ouvert, reprise, UNKNOWN, refus/lecture précédente, sans zones, long nom, conflit/indisponibilité. Vérifier Démarrer ou l’action applicable accessible, retour/focus/scroll, absence de POST depuis Préparer. Tests commandes/owners/provenance, scope réel, revue indépendante, pixels opérateur avant commit, CI et GOV-MERGE-01 ensuite. Pas de nouvelle galerie de variantes ni publication QA.
