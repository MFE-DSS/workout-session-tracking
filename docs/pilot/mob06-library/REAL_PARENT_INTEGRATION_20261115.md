# MOB-06 — intégration sur les vrais parents, gate pixels ouvert

15 novembre 2026. Branche existante conservée. **Implémenté et testé localement ; pixels acceptés pour le pilote avec réserves artistiques ; PR408 reste un checkpoint draft.** Aucun nouveau code UI committé, APK, OTA ou déploiement.

## Brainstorming / Options / Risques / Choix retenu
Le patch du13novembre n’était plus directement applicable : cinq chemins divergeaient des vrais parents BODY/NUT. Préflight des13chemins et empreintes avant application, résolution additive trois voies, tests consommateurs et merge normal des parents. Choix : poursuivre le même scope et reconstruire le masterC avec la familleDA08 acceptée ; aucune nouvelle géométrie globale ou autorité SCI. Parent runtime c9ce3713, closeout NUT47c7411 ; HEAD de branche f6d9b1d. Les fichiers BODY/NUT sont préservés.

## Croquis validé avant le code
GO BUILD/G1 call_4321044cec284c79898cb7d2dd483990 ; masterC DA07 call_e22888c3c8c64715bb1544af27dc95fb ; familleDA08 call_cbab5c2ca76c4afd8bb803eb3115f699. Le board natif8274 a reçu sa propre décision avant commit UI : « Accepter pour le pilote, avec réserves artistiques », call_b56c9db4e9754b4fb7435df10a6fda49. Aucun des SVG antérieurement refusés n’est une baseline.

## Inventaire — une information, une seule fois
Noms/statuts depuis source.name/kind/source_status ; ordre depuis composition[].position ; unités prévues depuis counts.prescribed_sets et working_sets ; prescriptions exactes dans le détail. Catalogue et programmes personnels distincts. La signature de catalogue encode seulement le compte exercise_slots (cap visuel12, compte exact lisible), jamais les muscles ou la récupération. Intention locale et occurrence possédée sont deux objets ; UNKNOWN ne devient pas un reçu de création par simple relecture.

## Comparaison avec la référence validée
[Board contrôlé](http://127.0.0.1:8274/) :18captures natives et3références conservées. MasterC, familleDA08 et MISSIONLOCKED comparés. InstrumentSurface/EmbeddedAction réutilisés, AurenMark et D4 préservés. Ni FrameC, RecessedWindow, NumericReadout, palette, rail, MISSION, exécution ou baseline modifiés. Texte extensible, séquence verticale à grande fonte ; aucune palette musculaire, E7 ou calendrier ajouté.

## Un changement par itération
Cette itération intègre le consommateur Programmes déjà autorisé et reconstruit le masterC/familleDA08. Elle ne crée ni constructeur, ni moteur de prescription. Le gate demandé porte sur ces pixels contrôlés ; NUT a son acceptation pilote avec réserves distincte.

## Revue entière et corrections RED→GREEN
Une revue indépendante fraîche de50chemins a relevé zéroCritical, deuxImportant et unMinor. Rapport original et empreintes conservés horsGit. I1 : hydrate pouvait perdre un blocage session_open sans lecture propriétaire positive ; correction par projection propriétaire fraîche, état indisponible conservé si inconnue. I2 : la note cardio canonique était absente de la projection ; correction du champ cardio_note et divulgation située. Minor : technique prescrite affichée dans Sources. Un seul passage de corrections ; aucune deuxième revue indépendante des correctifs prétendue.

Reproduction :3échecs/28PASS mobile et1échec/21PASS backend ; après correction36PASS mobile ciblés et24PASS backend. Le foreground pendant préparation est gardé : aucune invalidation de sélection en plein enregistrement.

La recette native a ensuite exposé un autre défaut : un repaint parent recréait la configuration linking de l’ExpoRoot installé et démontait le contrôleur. Quatre intentions PREPARED ont été annulées explicitement, sansPOST et UNKNOWN conservé. Correction minimale : référence linking stable ; test de cycle de vie fondé sur le comportement du SDK58 installé, RED1/4PASS → GREEN5PASS +TypeScript. Aucun SDK, module ou lock modifié. Banc sans instrumentation après correction.

## Vérifications et preuve du vrai consommateur
check_scope SHARED_CODE. Broad réel initial129PASS ; broad final bibliothèque/mission/historique126PASS après correctifs, campagnes distinctes. Mobile final116suites/1377PASS +TypeScript. La fusion documentaire du closeout NUT ne change aucun fichier app/mobile ; garde du brouillon archivé NUT1PASS sur ce parent. Ruff neuf7fichiersPASS, budget260≤548, protocolePASS, Bandit-ll3modulesPASS, Gitleaks du scope50cheminsPASS, OpenSpec strict27/27. Gate visuel Docker77/77PASS, mêmes image/fixtures/baselines que CI, sans réécriture ; aucune CI408 de ce nouveau candidat revendiquée.

Vrai ConnectedApp iOS26.3 dédié390×844 : lecture catalogue et programmes, VALIDATED consultable non lançable ; un POST committé201 puis503 de test, intention durableUNKNOWN, kill/reprise, vérification de#1, adoption dans journalSQLite réel, Today puis exécution même#1. Clôture synthétique sans série : historique terminé et fréquence0, charges/répétitions inconnues. Coupure du backend réel puis lecture précédente explicitement non confirmée ; reconnexion sans POST automatique. Second départ humain normal201 après clôture : CREATED_CONFIRMED et snapshot#2. DeuxPOST au total, aucun doublon automatique. Reçus SQLite/HTTP horsGit.

AndroidAPI36 : vrais Hosts de production/HTTP/SQLite à360/480dp normal/130%, horsConnectedApp, overlayExpoGo visible ; absence du module dans ExpoGo non contournée. Aucun nouvel APK ou physique. iOS grande fonte : disposition, sélection et Retour éprouvés ; défilement CUA indisponible(noWindowsAvailable), pas de PASS exhaustif VoiceOver/focus/rotation/retourAndroid. Les témoins API/Jest ne sont pas une recette physique.

## Suite de livraison
Décision pixels Programmes reçue avant commit UI. Suite autorisée : relecture décisions, commit/push de la même PR408, CI HEAD exact, merge gardé sous GOV-MERGE-01, canonique/Sonar et closeout. Aucun nouveau GO BUILD/G1/merge routinier. Les sources non committées et preuves sont conservées. MOB07 se prépare après livraison. REL03 reçoit le manifeste des slices fusionnés ; pas d’APK par merge.

Preuves : /Users/martinfeldmann/auren-review/mob06-canonical-integration-20261115/ ; board public local ne contient aucune configuration privée.

## Relecture des décisions avant commit UI —15novembre
Les deux registres DESIGN_DECISIONS_HOME_UIV2 et DESIGN_DECISIONS_UIV2_SURFACES ont été relus entièrement, amendements mobiles compris.

| Décision | Statut sur ce delta | Vérification |
| --- | --- | --- |
| HOME D1 | Respectée dans sa sémantique applicable | Contrôles distincts des étiquettes ; cibles48dp, famille DA08 acceptée. Les anciens rangs web ne sont pas redessinés. |
| HOME D2 | Respectée | Aucune revendication Recommandé IA, recommandation ou moteur nouveau. |
| HOME D3 | Legacy visuel, tokens natifs respectés | Signal pour action ; structure neutre, pas de bleu décoratif ou de palette nouvelle. |
| HOME D4 | Non concernée | Aucun retrait sur l’accueil web. |
| HOME D5 | Legacy visuel, direction respectée | Séances ordonnées et unités prévues sourcées ; aucun asset biologique inventé. |
| HOME D6 | Respectée | Ordre des séances distinct d’un calendrier ; aucune disponibilité physiologique déduite. |
| HOME D7 | Non concernée | Fréquence et faits Progrès conservés ; clôture sans séries ne crée pas une fréquence positive. |
| HOME D8 | Respectée | Quatre onglets conservés, Progrès et journal existants utilisés. |
| HOME D9 | Respectée | Aucun N+2 recommandé ou futur entraînement promis ; la bibliothèque montre des prescriptions consultables. |
| SURFACES Q1 | Non concernée | Connexion et compte inchangés. |
| SURFACES Q2 | Non concernée | MISSION/barres de récupération non modifiées ; les traits de structure ne mesurent aucune récupération. |
| SURFACES Q3/amendement | Respectée | Aucun nouvel état du jour ou formulaire1–5. |
| SURFACES Q4/amendement | Non concernée pour le journal, sémantique conservée | Aucune ligne d’exécution modifiée ; faits prescrits/exécutés distincts. |
| SURFACES Q5 | Supersédée en mobile | Famille DA08 et masterC acceptés, pas de nouvelle carte universelle. |
| SURFACES Q6 | Supersédée en mobile | Rôles du thème natif existant ; aucun changement global de typo. |
| SURFACES Q7 | Supersédée en mobile, souveraineté respectée | Une action de départ/confirmation/reprise selon stade effectif ; pas d’actions concurrentes inventées. |
| SURFACES Q8 | Supersédée en mobile, tokens respectés | Aucun hex/opacité décoratif ajouté ; primitives et baselines inchangées. |

Aucune décision applicable violée. Réserves artistiques gardées au backlog, sans promesse state-of-the-art universelle. Le reçu n’accorde aucun traitement réel, activation, publication APK/OTA ou acceptation physique.
