# RELEASE-01 — identité du banc contrôlé

9 novembre 2026. **SYNTHETIC_LOCAL_QA / NOT_DEPLOYED.** Ce document fixe les
conditions observées, pas la cible finale de release. Preuves privées dans
`/private/tmp/auren-data-release-01-review-evidence/` ; aucun credential, identifiant
personnel d'appareil ou base de données n'est publié par cette documentation.

## Source et configuration observées

| Élément | Valeur / preuve |
|---|---|
| Backend et source JS | fe9f6e9beb585a271ae2c2726e338359057b9f58, copie produit sans diff fonctionnel |
| Backend | Loopback127.0.0.1:8130, APP_ENV=test, Sentry désactivé |
| Bundle neuf | inventaire `plan-calibration-inventory/2.0.0`, packaging SHA256 `22b066a0fb363b1bd435323269bad8a7fa47e4149f18b91e4b039e89d8352dfc` |
| Autorité initiale / évolution | génération1 ACTIVE au reçu initial ; sonde finale génération3 ACTIVE →4 WITHDRAWN →5 ACTIVE de test ; approval_ref de fixture synthétique contrôlée, pas publication de production |
| Pins SCI V3 | bundle78b3e5d99fe05093d6141678fd40f16e744b88d3d87405f14b0f8be357724d94 ; binding9ef301da08ec3614c7e2a4fbbb95a2384f1c870bca84b6b69eeb4e20a1897389 ; autres pins exacts conservés au reçu |
| Flags du banc | controlled_test/acquisition/evaluation/creation/guidance = true ; défauts du dépôt inchangés et aucune activation réelle |
| Base | Nouveau SQLite synthétique ;40tables observées, empreinte schéma `fd0f7b35d7c9de52f97dde42e6f58ad4db3a8aefc27c2ef95d13459ed0193128` |
| Application DB effective | init_db/create_all des métadonnées non PLAN puis DDL existant `plan_v3_20261107_01`, révision parent déclaréez7a2u8v9x20 ; **pas** un replay attesté de toute la chaîne Alembic |
| Identité/migration | Fichier migration et schéma réel empreintés dans QA_ENVIRONMENT.json/QA_SCHEMA.sql ; aucune migration nouvelle ou base opérateur touchée |
| Projet natif de test | Wrapper privé important le vrai ConnectedApp, pas une galerie ; source/hash des modules enregistrés |
| Metro | Initialement bindIPv6::1/localhost:8131 puis relancé en loopbackIPv4 pour Android ; max-workers1, aucune exposition publique attestée. localhost et127.0.0.1 ne sont pas interchangeables dans le bind initial |
| Hôte iOS simulateur | Expo Go58.0.7/SDK58, iOS26.3/iPhone16e dédié ; ce n'est pas un binaire autonome AUREN signé |
| Android observé | ADB41/emulator, AVD QA en mode read-only ; Expo Go58.0.5 bloque le vrai ConnectedApp sur ExpoTopicSubscriptionModule absent ; aucun Android physique connecté |
| iPhone physique détecté | iPhone15Plus/iOS27.0.1, joignable et DeveloperMode ; AUREN Lab0.0.1build1 installé, **SHA/backend non établis** et aucune recette physique encore effectuée |

L'application déjà installée sur le téléphone personnel n'a pas été remplacée,
son journal/SecureStore n'a pas été lu ni réinitialisé. La présence d'un build
0.0.1(1) ne prouve aucune compatibilité avecfe9. Les identifiants physiques et
la signature restent dans le préflight privé, hors dépôt public.

## Résultat live HTTP observé

Le script privé appelle le vrai serveur loopback, ses routes auth/ledger et
les vrais loaders/évaluateurs/validateurs. Il ne sert aucune fixture READY.
Deux comptes synthétiques distincts, sept réalisations avec observations
synthétiques clairement étiquetées : toutes QUALIFIED selon les vraies gates.
Snapshot propriétaire → SCIENTIFICALLY_READY limité, deux temps
BUDGET_UNCERTAIN → ack altéré refusé409 → ack exact ELIGIBLE → séance1,
7exercices/14séries. Rejeu de la commande : mêmesession_id. Snapshot et séance
deA refusés404 àB. Journal RDL relu PER_IMPLEMENT sans totalisation ; rejeu
d'écriture acquitté sans duplication. Résultats dans LIVE_HTTP_JOURNEY.json.

Ce résultat est **LIVE_LOOPBACK_HTTP_SYNTHETIC_NOT_NATIVE_OR_PHYSICAL**. Il ne
prouve pas que l'utilisateur a physiquement effectué ces essais et ne remplace
aucune ligne de recette native ou d'acceptation physique.

## Recette iOS native réellement effectuée — partielle

Le vrai ConnectedApp sourcefe9 a affiché la connexion sur le simulateur dédié.
Connexion du compte synthétique créé par HTTP, récupération de la même séance
possédée, prescription capturée d'abord observation-only, puis revalidation
explicite courante et affichage17kg machine/provisoire/RIRsubjectif : observés.
La saisie typée du réglage machine a été ouverte, sans journalisation native
déclarée réussie.

Création de compte native non achevée : suggestion système de mot de passe et
erreurs CUA noWindowsAvailable. Une relance du seul hôte QA a permis de reprendre
la connexion. Saisie décimale : mapping de l'outil a produit18m5 au lieu de18,5 ;
aucun fait erroné accepté. La fenêtre du simulateur a ensuite changé pendant
l'automatisation ; arrêt des entrées, appareil dédié observé Shutdown sans
cause établie. Aucun reset ou arrêt du simulateur personnel demandé/effectué.
Ces limites de l'outil ne deviennent ni PASS produit ni diagnostic de défaut
applicatif. Receipt IOS_NATIVE_PARTIAL_RECEIPT.json et captures privées.

Le clavier/Back/lecteurs d'écran complets, le parcours natif entier des sept
rencontres et l'iPhone physique restent non prouvés par cette passe.

## Comptes, arrêt et rollback à contrôler

Comptes réservés au banc, sans email, finalités réelles ou données corporelles
personnelles. Credentials synthétiques hors dépôt ; ne pas réutiliser un compte
de production ou les anciennes preuves MOB02. Pas d'effacement de données
personnelles testé ; une demande/reçu d'effacement réel attend la politique.

Le plan de rollback cible est de fermer les flags applicables et retirer
l'autorité sous génération nouvelle, sans supprimer DB/snapshots/journal/
commandes. La sonde HTTP effectivement réalisée ne coupe pas les flags :
génération3 ACTIVE →4 WITHDRAWN →5 ACTIVE de test. Sous retrait : autorité
servie absente, applicabilité BLOCKED/authority_not_served, lectures200,
facts inchangés et même séance au rejeu CREATED. Le flag configuré de guidage
reste true : il n'est pas une autorité ni une permission courante. La première
assertion de banc qui supposait ce flag faux a été corrigée ; reçu final
LIVE_ROLLBACK_PROBE.json. Aucun fallback V1 permissif, downgrade DB ou effacement.

Cette sonde ne prouve pas une coupure de tous les flags, l'exhaustivité des
nouvelles mutations sous retrait ou un rollback de release réelle. Conserver
les reçus avant arrêt des seuls processus attribués, ne pas restaurer une
autorité réelle sans accord applicable/pins et nouvelle génération.

## Compatibilité et artefacts

Le relevé officiel Expo SDK58 du9novembre (EXPO_OFFICIAL_VERSIONS.json,
[métadonnées Expo](https://exp.host/--/api/v2/versions)) annonce AndroidGo58.0.5
et iOSGo58.0.7. C'est bien l'hôte Android essayé, malgré le module natif absent :
aucun PASS Android. Le graphe app source est Expo58.0.17/RN0.88.0 ; un client
natif compatible doit être établi. Aucun APK AUREN QA autonome n'a été produit.
Java25 observé, SDKplatform/build-tools absents et environ8,9Gio libres au
relevé ne constituent pas une toolchain de build validée. Voir le
[brief interne](INTERNAL_BUILD_BRIEF.md) pour les prérequis exacts et gates.

## Portée encore ouverte

Politique du responsable/finalités/consentements/copies/effacement réels,
replay complet des migrations sur la cible choisie, artefacts AUREN installables
avec source/build/backend attestés, Android/iPhone physiques, accessibilité et
force-kill/SQLite complets, évaluation risque/rollback de la cible, acceptation
alpha et GO de déploiement distinct. Aucune distribution Store requise par ce
seul banc ; un futur APK QA autonome peut suivre la voie interne revue.

L'environnement initial est conservé dans `QA_ENVIRONMENT_INITIAL.json` ;
`QA_ENVIRONMENT.json` reflète aussi le redémarrage contrôlé à génération5,
sans changement du bundle, du schéma ou des flags. Le complément de
[recette](QA_RESULTS.md#complément-de-recette--redémarrage-et-contention-du-banc)
distingue les incidents du banc et la récupération HTTP de la séance existante.
