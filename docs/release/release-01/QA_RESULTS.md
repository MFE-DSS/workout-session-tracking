# RELEASE-01 — résultats effectivement observés

9 novembre 2026. Source produit et client :
`fe9f6e9beb585a271ae2c2726e338359057b9f58`.
**PARTIAL_CONTROLLED_ACCEPTANCE / PHYSICAL_AND_RELEASE_GATES_OPEN.**
Les colonnes portent le niveau de preuve, pas une qualification générale du
produit. Aucun scénario HTTP ne devient un PASS natif ou physique.

## Parcours serveur réel — données synthétiques

`LIVE_HTTP_JOURNEY.json`, `LIVE_CAPABILITIES.json`, `LIVE_EXECUTION.json` et
le script privé `live_http_journey.py` constituent le reçu. Le script utilise
un client HTTP vers le serveur loopback et les vraies routes ; le helper
versionné `Journey` envoie choix/familiarisation/observations, sans fabriquer
un résultat READY. Les observations sont synthétiques, pas des gestes réalisés
par un utilisateur ou des instructions validées pour une machine réelle.

| Scénario | Résultat observé | Limite |
|---|---|---|
| Création et authentification | Deux comptes synthétiques distincts créés par HTTP ; tokens employés pour leurs requêtes | Pas de signup natif réussi ; ni service email ni cycle d'effacement réel |
| Rencontre neuve / réglage | Sept rencontres ouvertes sans historique préchargé ; préparation, réglage disponible, contexte et familiarisation envoyés explicitement | Pas d'exécution physique ; exhaustive matrice invalide/absent non rejouée dans cette passe live |
| Observation / qualification | Observation et acceptation liées au vrai réglage ; sept résultats `QUALIFIED` | Qualification contrôlée/provisoire selon runtime, sans promesse scientifique au-delà du contrat |
| SCI V3 | Snapshot propriétaire, vraie évaluation `SCIENTIFICALLY_READY` et deux temps `BUDGET_UNCERTAIN` | Préparation synthétique locale, pas activation réelle |
| Ack exact | Contexte altéré refusé HTTP 409 ; contexte exact → `ELIGIBLE` | Pas de parcours natif complet du dialogue d'ack |
| Création idempotente | Même commande rejouée → même séance ; sept exercices et quatorze séries | Pas une épreuve native de perte réseau ou d'écriture hors ligne |
| Séparation A/B | Snapshot de A et exécution de sa séance renvoient 404 à B | Pas de changement de compte natif/SecureStore ou de fuite locale testé |
| Journal typé / historique | RDL écrit et relu `PER_IMPLEMENT`, sans totalisation ; rejeu de l'écriture acquitté sans duplication | Mutation HTTP, pas journalisation native ni synchronisation SQLite éprouvée |

Les sept identités réellement traversées sont `leg-extensions-assises`,
`chest-press-machine`, `rowing-chest-supported`, `romanian-deadlift-halteres`,
`tirage-poulie-haute-prise-neutre`, `elevations-laterales-machine` et
`releves-mollets-debout-machine`. Six contextes sont `MACHINE_DISPLAY_KG`,
le RDL est `PER_IMPLEMENT`. Les valeurs de fixture ne deviennent pas des
valeurs de prescription recommandées ni une politique de calibrage nouvelle.

## Retrait et restauration de l'autorité — HTTP synthétique

`LIVE_ROLLBACK_PROBE.json` enregistre génération 3 ACTIVE → génération 4
WITHDRAWN → génération 5 ACTIVE, dans la seule DB jetable. Après retrait :
autorité servie absente, revalidation d'applicabilité `BLOCKED` avec
`authority_not_served` et génération 4 ; lecture de séance et snapshot HTTP
200, exercices/faits inchangés ; rejeu de la commande déjà CREATED → même séance.

Le flag configuré de guidage est resté `true`. La première tentative de sonde
supposait à tort qu'il devait devenir faux lorsque l'autorité était retirée ;
cette assertion de banc a été corrigée. La preuve finale porte sur l'autorité
servie et l'applicabilité réelle, pas sur une modification du flag. Ce reçu
n'atteste ni coupure de tous les flags, ni tentative exhaustive de toute
nouvelle mutation sous retrait, ni rollback d'un déploiement réel.

Le rejeu CREATED réconcilie une identité durable : il ne donne aucune permission
courante. Le retrait conserve les faits et n'autorise aucun fallback V1
permissif, nouvelle consigne ou nouvelle séance sans autorité valable.

## iOS — vrai consommateur natif, résultat partiel

`IOS_NATIVE_PARTIAL_RECEIPT.json` : simulateur dédié iPhone 16e/iOS 26.3,
Expo Go 58.0.7, vrai `ConnectedApp` source fe9 via wrapper privé et manifeste
de sources `JS_SOURCE_MANIFEST.json`.

| Action | État et preuve |
|---|---|
| Connexion du compte HTTP synthétique | Observée dans le vrai écran natif |
| Récupération après lancement neuf | Même séance propriétaire retrouvée |
| Prescription et revalidation | D'abord observation seule ; revalidation explicite courante, 17 kg machine/provisoire et RIR subjectif observés |
| Saisie du réglage machine | Champ typé et libellé de l'unité ouverts ; aucune écriture native acceptée déclarée |
| Signup natif | Inachevé : suggestion de mot de passe système et outil `noWindowsAvailable` |
| Décimale | Outil de saisie : `18,5` devenu `18m5` ; pas de fait erroné accepté, ni PASS clavier décimal |
| Captures / cycle simulateur | Capture signup exploitable ; fichier de capture décimale vide, inutilisable comme preuve ; simulateur dédié ensuite observé Shutdown, cause non attribuée |

Lors d'un changement de fenêtre pendant l'automatisation, les entrées ont été
arrêtées. Aucun reset ou changement de cycle de vie du simulateur personnel
n'est revendiqué. Les limites d'outil ne prouvent ni succès ni bug produit.
La récupération d'une séance après lancement neuf n'est pas un test complet
de force-kill, reprise d'une saisie en vol ou persistance/synchronisation SQLite.

## Android et physique — blocages concrets

Sur l'AVD QA en mode read-only, le vrai ConnectedApp a échoué dans Expo Go
58.0.5 avec `Cannot find native module 'ExpoTopicSubscriptionModule'`.
Capture `android-native-fe9.png` et traces de banc privées. Le reçu officiel
`EXPO_OFFICIAL_VERSIONS.json`, relevé le 9 novembre, annonce encore pour SDK 58
Android 58.0.5 et iOS 58.0.7 : recommander simplement « le dernier Expo Go »
ne résout pas le blocage observé. Il faut un client natif dont les modules
sont compatibles, puis reprendre les scénarios ; aucun contournement de module
ni build correctif n'a été fait dans cette tranche.

Le préflight read-only confirme un iPhone 15 Plus/iOS 27.0.1, Developer Mode,
AUREN Lab 0.0.1 build 1 installé, **SHA et backend inconnus**. Aucune interaction
de recette ou remplacement de ce build personnel ; aucun Android physique
connecté. Il n'existe aucun PASS physique Android ou iPhone dans ces preuves.

## Scénarios et décisions encore ouverts

Restent à éprouver sur les vrais consommateurs compatibles : signup natif,
parcours complet des sept rencontres, ack et création natifs, journalisation
typée machine/RDL et lecture historique natives, reprise d'interruption en vol,
perte réseau/retry, séparation A/B locale, clavier décimal/fermeture/Back,
VoiceOver/TalkBack, accessibilité, force-kill et SQLite. Puis reprendre la
matrice physique avec device/OS/build/backend exacts et gestes observés.

Les gates politique DATA, intégrité/sécurité de la vraie cible, migration
complète, artefacts installables, rollback cible et GO de déploiement restent
ouverts. Les quatre checks GitHub obligatoires et Sonar consultatif restent
inchangés ; aucun nouveau run CI ou verdict de release n'est inventé ici.

## Complément de recette — redémarrage et contention du banc

Pendant la préparation simultanée des cas natifs, des réponses
`runtime_storage_unavailable` et un `database is locked` lors de la rotation
de session ont été observés. Un contrôle HTTP en lecture a ensuite obtenu
200 avant le redémarrage : aucun deadlock persistant n'est établi. Le seul
backend local possédé a été relancé avec la même base synthétique, le même
bundle et l'autorité génération5 conservée. Une connexion normale puis
GET handoff retrouvent toujours la séance1. Preuve privée :
`BACKEND_RESTART_RECOVERY.json` ; environnement initial conservé séparément
dans `QA_ENVIRONMENT_INITIAL.json`. Ce résultat ne ferme pas la recette
concurrente/force-kill native ou physique.

Le banc comparatif UX a aussi été corrigé pour partager une seule session
d'authentification entre ses variantes avant/après et attendre le choix de
variante avant de monter un consommateur. Des requêtes annulées de son
ancienne double initialisation ne sont pas imputées comme défaut démontré
du produit. Aucun module d'authentification produit n'a été modifié. Les
limites normales de connexion sont conservées ; aucune option de quota
n'a été désactivée pour la recette.
