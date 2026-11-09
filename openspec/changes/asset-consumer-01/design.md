# Design — ASSET-CONSUMER-01

## Context

Les cinq vues de référence mannequin sont reçues historiquement, le master de production est absent. `ExecutionScreen.tsx` V1 montre une zone du plan ; `PlanV3ExecutionScreen.tsx` montre identité/réalisation et prescription typée. Aucun des deux ne fournit aujourd'hui un contrat de média illustré ni une fiche d'exercice native autonome. `routes/programmes.tsx` reste une passerelle vers le site.

## Goals / Non-Goals

Rendre reviewable une composition et la readiness de ses assets, sans implémentation ni activation. Préserver les contrats et l'histoire DA-05.1, distinguer Push A historique des calibrations, ne jamais déduire des instructions ou une anatomie depuis une image.

## Decisions

Une fiche secondaire native indépendante du cockpit LOCKED est proposée ; sa composition est dans `docs/assets/asset-consumer-01/NATIVE_COMPOSITION_PROPOSED.md`. Elle consomme uniquement une paire exacte START/END à cadrage identique, une identité/version, une réalisation et une provenance explicites. Les identifiants de futures illustrations sont des propositions locales au dossier, pas des entrées approuvées du manifest.

Les contrôles de série et valeurs de calibration n'y sont pas dupliqués. Sans asset recevable, une absence explicite remplace le média ; les instructions ne sont affichées qu'avec leur propre source applicable et leur contrat. L'illustration ne ferme aucune gate de familiarisation ou d'essai.

## Alternatives considered

Produire tout le catalogue avant le composant retarderait la preuve de consommation et contredirait l'ordre adopté. Remplacer la fenêtre BodyMap du cockpit modifierait une surface LOCKED et confondrait geste et localisation. La fiche secondaire isole la preuve pilote sans réinterpréter le cockpit.

## Platforms

Même ordre et contenu proposés iOS/Android. Les conventions de fermeture, retour Android, safe area, taille de texte et lecteur d'écran seront éprouvées sur vrais rendus après G1 et GO BUILD. Aucun rendu ou écart plateforme n'est déjà accepté ici.

## Risks / Trade-offs

Une homonymie d'exercice ne prouve pas même réalisation ; une seule vue ou un accessoire absent invalide la paire. Les zones SCI et les onze zones BodyMap ne sont pas le même vocabulaire : aucune conversion implicite ni nouvelle zone `delt_ant`. Les assets BodyParts3D/Servier hérités ne remplacent pas le corps MIT dessiné dans le natif.

## Migration Plan

Aucune migration ou apply. Réception et revue du dossier → GO BUILD distinct et G1 → assets exacts gouvernés → vraie fiche pilote et pixels → décision sur les sept Push A. Pas d'autorisation de série avant la preuve du consommateur.

## Open Questions

Master et fichier matériel exacts non livrés ; réalisation Smith et instructions applicables à qualifier ; budgets/cadrage final à mesurer ; approbation de composition et pixels à recevoir. Ces inconnues sont détaillées dans le rapport et ne sont pas résolues par défaut.
