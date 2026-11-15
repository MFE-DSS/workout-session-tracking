# MOB-07 — constructeur personnel et continuité du journal

15 novembre 2026. **ENGINEERING MERGE et CI canonique vérifiés.** Aucun APK, OTA, déploiement ou traitement réel par cette livraison. Les reçus finaux résoudront le suivi de publication sans réécrire cet instant.

## Résultat, autorisations et limites

Programmes permet de créer un programme personnel, ordonner ses séances, sélectionner des exercices par identité canonique exacte et déclarer séries/plages de répétitions. Sauvegarde, validation de structure, publication et nouveau cycle utilisent UserProgram. MOB06 relit la composition publiée et conserve la même occurrence possédée dans Today et le journal. Les anciens slots non résolus, noms, indices et prescriptions restent conservés. Aucun programme actif, calendrier, défaut de prescription ou moteur scientifique client ajouté.

GO BUILD/amendement/G1 : **« Autoriser MOB-07, l’amendement et G1 »**, call_dd254c785ba7430897ac13dc9b579cbc. Pixels : **« Accepter pour le pilote, avec les limites indiquées »**, call_8c8924d28fa04247b1cfb692f2868145, avant commit UI. Famille DA08 et réserves des parents conservées ; aucune primitive, baseline, palette ou dépendance native modifiée. Android complet/pixels et physique ne sont pas acceptés par ce reçu ; focus/insets/gestes exhaustifs restent ouverts. GOV-MERGE-01 couvre livraison et closeout, jamais le déploiement.

## Révisions et contrôles réels

Parent f31b6e7b8411bf9668906a3a5dc38b22fef8ae55. [PR414](https://github.com/MFE-DSS/workout-session-tracking/pull/414), HEAD c614241123eae018df4b7c4d3a176bdc9091c38e, merge dbad35d4634442e985b2964ff85fad6254efae74 ; arbres HEAD/merge identiques. Les quatre checks protégés, revues et threads ont été relus avant fusion ; aucun avis bloquant. Commit de merge avec expected_head_sha, sans bypass, force ou squash.

[CI PR43750397616](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/43750397616) completed/success,11jobs, tentative1 : **8755backend/3ignorés**,127suites/1448mobiles +TypeScript et77visuels réellement exécutés. Cinq shards passants, attestation SHADOW seulement. Ruff requis259≤548, Bandit, Gitleaks, audit Python et gardes de migration passent ; format Ruff consultatif711fichiers. L’audit Python ne constitue pas un audit global de l’APK.

Local MIGRATION : sweep canonique454fichiers/114lots,8764PASS/1ignoré, exit0, pic2763MiB sous3000. Les campagnes arrêtées par le watchdog sont conservées comme arrêts de ressources, pas PASS. Après le sweep, seul le delta JSON/test de l’entrée PREPARE active a changé : RED réel puis270tests QA rejoués sous les versions verrouillées. Mobile1448+TS, visuel77, HTTP/inventaire24, migrations/drift/snapshot/roundtrip, Ruff neuf11fichiers, Bandit nouveaux modules0, Gitleaks sources/public0 et OpenSpec28/28. Les comptes local et CI sont ceux de leurs campagnes respectives.

Revue indépendante entière :3Important corrigés RED→GREEN et relus (brouillon perdu sur changement d’onglet, ancien reçu écrasant une création sale, borne globale refusant plusieurs programmes légaux). Relectures bornées des consommateurs de schéma et de l’entrée PREPARE sans finding ; aucune nouvelle exécution indépendante des tests prétendue.

### Sonar PR : ERROR consultatif, résultat conservé

17CODE_SMELL et1BUG déclaré, zéro vulnérabilité/hotspot ; couverture app92,2%, nouvelle90,89456869009585%. Le BUG AaHgsPiy8-rYvi0mGcmX, pythonbugs:S2259, signale `.strip()` sur None dans program_builder_commands.py:42. La garde de type exacte et le court-circuit `or` rendent cet appel impossible pour une valeur non str. Huit témoins exécutés sur le vrai module, dont canonical_command avec titre None, confirment le refus422 ; nullable None sort avant le prédicat. **Ruling : faux positif de cet analyseur**, pas absence d’alerte Sonar. Les remarques de complexité et autres smells restent consultatives. Aucun seuil, profil, état d’issue ou baseline modifié.

Preuve SONAR_S2259_WITNESS.json ; SHA256 du fichier2f2544bcb33539cdc5b51f8ac379ecb423ad15005f4994d7b4384b5e96245d19. Sonar canonique sur dbad35d, analyse ffb030d0-8beb-449f-a95d-29ed0c849bb6 : **ERROR consultatif,9bugs/654smells/8entrées externes Bandit/0hotspot**, couverture app92,2%/nouvelle92,22626906442066%. Les16anciennes entrées BUG/Bandit concernent des sources identiques au parent f31 ; la seule nouvelle alerte BUG (AaHgyybj4B142AX0qyV0) est le même S2259 évalué ci-dessus. Les huit entrées Bandit sont exposées par le service comme VULNERABILITY ; elles ne sont ni masquées ni requalifiées en preuve globale d’innocuité. Aucun total calculé par addition avec les issues PR.

## Consommateurs, reprise et faits historiques

Kernel transactionnel owner/CAS partagé web/natif, quotas et publication sérialisés, reçu atomique avec effet domaine. Une page périmée reçoit409 et demande relecture. Migration additive program_builder_operations_01 après nutrition_manual_01, sans backfill ni DDL startup. Les cinq routes Bearer sont montées et classées dans l’inventaire canonique.

SQLite conserve les octets de commande avant HTTP sur la connexion/file du journal possédé, partitionnée compte/backend. Après réponse perdue : UNKNOWN conservé, vérification GET du reçu exact ; aucun POST automatique. Le rejeu humain explicite garde clé/corps/digest. Réponses tardives A/B, mutation concurrente et ancien reçu ne remplacent pas les brouillons.

Vrai ConnectedApp iOS26.3,390×844pt : créer → mouvement canonique → deux séries/plages8–12 saisies → sauvegarder/valider/publier → MOB06 → même séance1 Today/journal. Kill/reprise, puis clôture avec0série réalisée/2prévues. Création distincte avec réponse perdue après commit : SQLite UNKNOWN après kill, GET retrouve le reçu,5reçus natifs égaux au serveur, compteur POST inchangé5 pendant reprise/vérification. Un sixième reçu serveur ultérieur appartient au test SSR de coexistence, pas à un rejeu automatique. Relecture HTTP sous FastAPI0.141.1/Starlette1.6.0 : programme publié, historique completed, completed_with_work0 et prescription UNKNOWN_NOT_CAPTURED ; refus étrangers404. Aucun fait effectué fabriqué.

Board http://127.0.0.1:8290/ :13captures iOS,3SSR,2références MOB06, clavier réel/grande fonte. Paquet soumis SHA256940cacbcbeeca5f4991d678b2216496fc6bb0a0869f1f71265f335b6e4ea3cbe ; il conserve son instant antérieur à l’acceptation, résolue par NATIVE_PIXEL_ACCEPTANCE.json. Android Host HTTP/SQLite360/480dp masqué par ExpoGo, Qt non pilotable : pixels/gestes UNAVAILABLE. Aucun Android complet,130% ou physique déduit de ces montages.

## Préparation de release et rollback

Les vérificateurs backup/release couplés au snapshot suivent le nouveau head ; vraie migration/backup/export/restore avec lignes propriétaires/reçu, négatifs ancien/forgé et digest vérifiés. Le modèle candidate.json est une entrée active du workflow : seul son pin de schéma est actualisé. Les octets f31 et les vrais anciens reçus PREPARE/binaire sont conservés.

[PREPARE43753502730](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/43753502730) sur dbad35d : prepare success, release skipped par la condition PREPARE. Artefact14177018006, ZIP SHA256c961b55fff5c61949959fadc1ea5e79921a95e61e0e3a03428d70bf1139418ee ; candidat a5e06ba5633f8c01c329b2620d66b869edcee7f07f12294aa310d3426831955a. Source exacte, schéma program_builder_operations_01 et hash des sources de stockage691c7acd7cfb3b7d8e6700c3c00aab85ac97ed32cecb127b7c9976194ee9ea29 consignés dans le reçu machine. **NON_DISTRIBUTABLE**, target/runtime/fingerprint/build/artifact non vérifiés ; BUILD_APK est l’action préparée, aucune compilation lancée.

Le garde de stockage inclut le nouveau store ; une ancienne réception native ne prouve pas la compatibilité OTA. Rollback : conserver intentions inconnues et reçus, vérifier la capacité de lecture/reconciliation de l’ancien bundle ; ne pas effacer ou rétrograder aveuglément la lignée. Le downgrade non vide est gardé. QA02 ancien reste sans support Updates démontré. REL03 global NOT_READY : endpoint stable non provisionné, host OVH hors support à qualifier, adaptation fournisseur/configuration et environnement protégé à autoriser ; aucune modification distante.

## Archive, conservation et suivi

Archive CLI après merge code : 2026-11-15-mob07-owned-program-builder,4exigences canoniques,15/16tâches. Le Purpose généré vide a échoué au strict, puis sa description a été complétée sans modifier les exigences :28/28PASS. Gardes de closeout23PASS, budget259≤548, protocole et Gitleaks0. La seule tâche ouverte porte sur publication/CI du closeout et conservation, résolue par reçus finaux sans réécrire cet instant. Preuves durables : /Users/martinfeldmann/auren-review/mob07-implementation-20261115/. Identifiants synthétiques privés hors Git. Board statique indépendant conservé ; seuls les processus de banc possédés ont été arrêtés après vérification PID/commande/cwd. Checkout opérateur, références feature/bibliotheque-seances, worktrees BODY/NUT/REL03 et appareils personnels préservés.

[CI canonique43753463939](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/43753463939) completed/success,11jobs, tentative1 :8755backend/3ignorés,1448mobiles+TypeScript,77visuels réellement rejoués ; mêmes sources produit que le HEAD accepté. Les prochaines opérations du périmètre sont publication du closeout puis conservation normale après zéro commit unique. Le worktree historique MOB06 est conservé ; seules les deux branches MOB07 propres seront retirées après fusion et preuve d’ascendance. Le prochain candidat Android consolidé exige cible QA autorisée, compatibilité serveur/API/schéma/runtime/signature, rollback et smoke installé ; la recette physique reste distincte. Disponibilité musculaire NOT_SERVED, sans producteur SCI admis ni calcul depuis les séries.
