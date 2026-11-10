# Design REL-03 — pipeline QA Android

**Base vérifiée : b9a334d22e6b75e9b83650eb1b2b833d4ed5d169, 10 novembre 2026. PROPOSED / NO_GO_BUILD.** [Périmètre](BUILD_SCOPE.md), [tests](TEST_SPEC.md), [décisions externes](HOSTING_DECISION.md).

## Observé et autorité

Le manifeste produit/scientifique est conjoint (`docs/strategy/AUREN_MANIFESTO_V1.md`). CLAUDE §6 exige proposition/revue/apply ; GOV-MERGE-01 autorise les fusions conditionnelles après GO du scope, pas le déploiement. Registre courant : QA02 encore ouvert pour la recette physique ; pas de REL-03 existant. Les reçus vivants396/397 résolvent leur CI et leur livraison, sans réécrire les anciens statuts de préparation.

QA02 : APK source5ed4e0e, version0.0.1/code2, `dev.auren.releaseqa02`, certificat SHA25612b13109a2a41e2e2c0e97578364793e659a7548da4ce210d0dbd2f912f4bc75. SDK58.0.17/RN0.88.0, EAS projectc7243bfc-29b3-4486-aafe-e69b9c904bbe. `expo-updates` absent ; seul `expo-updates-interface`58.0.1 est verrouillé. Manifeste APK : `expo.modules.updates.ENABLED=false`, pas de runtime/version/canal. `eas channel:list` retourne une liste vide. Pas de réactivation OTA possible de ce binaire.

Le profil QA existant et son helper imposent l'ancien hostname trycloudflare. Leur reçu/source historique sont conservés. Le backend fonctionnelB8 et son bundle22b066a…/inventaire2/génération3 servent une SQLite synthétique complète, schéma `plan_v3_20261107_01`. Aucune preuve physique complète, politique DATA ou permission de cloud-spend nouvelle.

## Brainstorming / Options / Risques / Choix retenu

1. **Service dédié géré + disque SQLite** : réutilise le dialecte et le journal éprouvés, hostname fourni/TLS/persistance/supervision. Un seul service/instance, déploiement avec courte indisponibilité, sauvegarde SQLite en ligne à assurer. **Choix proposé pour le pilote**, Render0.5c-512mb + disque1Go ; mesurer mémoire/latence avant approbation de ce dimensionnement, jamais auto-upgrade payant.
2. **Service géré + Postgres géré** : sauvegardes DB gérées et meilleure concurrence ; ajoute driver, nouvelle qualification du dialecte et coût. Garder comme évolution si charge/concurrence mesurée le justifie, pas une dépendance par défaut de cette semaine.
3. **VPS existant, environnement dédié** : pourrait éviter un nouveau fournisseur mais accès, ressources, domaine et isolation ne sont pas établis ; toute modification partagée exigerait son GO. Aucun accès production entrepris.

Gratuit avec veille/disque éphémère et nouveau tunnel temporaire ne remplissent pas la continuité demandée. Docker/config sont portables ; le choix d'hébergement n'est pas prétendu approuvé. Source et coût dans HOSTING_DECISION.

## A. Cible stable et continuité de l'environnement

Un nouveau service QA dédié, hostname HTTPS fourni par la plateforme (nom réel connu seulement après création), auto-deploy désactivé, une instance et un worker applicatif. Le serveur canonique écoute seulement en loopback ; une façade QA bornée expose auth mobile et V3, comptes attribués et email vide, sans web/admin/docs/fichiers. Réutiliser les gardes de QA02, sans modifier son processus en cours. Pas de fixture READY ni import d'artifacts SCI.

Entrypoint supervisé : runtime Python verrouillé, source exacte, vrai bundle SCI construit et vérifié en image puis lecture seule, SQLite sur volume privé. Secret QA et allowlist administratifs hors Git/APK ; aucune valeur production réutilisée. SMTP/Sentry/consommateurs corporels/log SQL sensibles explicitement off et vérifiés. Délais, tailles, concurrence et arrêt propres bornés ; aucune migration automatique d'une base existante à chaque déploiement.

`/__qa_health` prouve transport/DB/schéma/bundle, jamais une permission scientifique. `GET /__qa_version` expose seulement environment_id, source déployée, contrats/API, schéma, inventaire/digests et état/génération courants réellement lus. Aucun owner, secret, token ou chemin privé. Retrait SCI conserve lecture/journal ; santé du transport n'invente pas READY.

**Upgrade = continuité possédée, pas réutilisation de numéros.** Les partitions locales sont liées aux user_id/devices, pas à une identité globale de backend. Interdit de pointer le même package vers une DB neuve réutilisant ces IDs. Le premier déplacement doit transférer la DB QA02 complète (toutes tables auth/identités/PLAN, pas export JSON legacy) et le seul secret d'auth QA, vers une nouvelle cible isolée. Le restore legacy refuse PLAN et n'est pas détourné.

Cutover seulement sous GO de déploiement : vérifier que les données restent synthétiques ; passer l'ancienne entrée en maintenance503 retryable pour **tout forwarding canonique**, y compris login/refresh et les GET susceptibles d'écrire ; drainer les requêtes puis arrêter proprement l'ancien writer avant capture. Les faits locaux restent conservés et la lecture serveur revient sur la cible validée ; une indisponibilité brève est déclarée, pas cachée. Snapshot cohérent SQLite backup API et reçu ; copier vers **nouveau chemin/volume**, jamais écraser la source ; vérifier intégrité/FK/schéma/comptes, refresh token, subject_ref, commandes/op_id et faits typés ; revalider autorité publiée courante ; ouvrir la nouvelle cible après preuve. L'ancien binaire peut conserver sa lecture locale et ses envois pending jusqu'à upgrade. L'ancienne source ne redevient pas writer après ouverture de la cible : un retour d'hôte exige gel des deux entrées, nouvelle copie de l'état courant et preuve d'un seul writer, jamais réactivation d'un snapshot périmé. Sans preuve de continuité, diffusion bloquée ; aucun reset local, réattribution ou nouvelle clé de start.

Sauvegarde : SQLite online backup atomique de toute la DB, manifeste source/schema/digests/continuity et contrôle intégrité. Avant chaque déploiement, après migration autorisée et quotidiennement pendant le pilote. Copies privées sur volume + export opérateur hors service avant premier cutover et chaque release ; si export/contrôle manque, gate release reste fermé. Les snapshots de disque fournisseur ne remplacent pas une sauvegarde DB. Aucun accès public, purge automatique, rétention personnelle inventée ou restauration en place. Restaurer en copie isolée puis contrôler avant tout basculement. RPO visé24h pour le banc ; RTO inconnu jusqu'au drill. Coûts/limites de stockage à relever.

## B. Identités de release

Deux documents versionnés, sans secret : **candidat** avant action et **reçu final** après faits. Schéma `qa-release/1.0.0` : release_id, état PREPARED/APPROVED/BUILT/VERIFIED/ROLLED_BACK, source Git exacte, native appVersion/versionCode, EAS build ID/URL, package/certificat/checksum, native runtimeVersion/fingerprint, projet/channel/branch, JS source/update group/id/assets hashes, environment_id/URL/source backend, contrats/API, SCI bundle/policy/génération capturés, schémas serveur/local admis, CI/revues/visuel/approbation réelle, preuves d'installation et rollback. Inconnu reste null/pending ; pas d'EAS ID futur inventé.

Conserver `dev.auren.releaseqa02`, schéma d'app et certificat QA. Première version proposée0.0.2/code3 ; valeur finale contrôlée contre dernier reçu/binaire, jamais versionCode réutilisé. Android uniquement. Les profils historiques/pilot et contrat scientifique restent préservés. Toute collision avec identifiant production ou signature différente bloque l'upgrade ; ne pas demander de désinstaller pour masquer le problème.

Séparer native et JS : versionCode/version native lus via `expo-application` (déjà transitif, à rendre explicite au même verrou si nécessaire) ; runtimeVersion/updateId/isEmbeddedLaunch via Expo Updates ; source JS via métadonnées générées déterministes depuis le checkout propre. Le reçu immuable lie package/versionCode/certificat/checksum au Git SHA du binaire, même après OTA. Ne pas présenter le SHA JS courant comme SHA de compilation native.

Les données volatiles (Git SHA, capture temporelle, source backend/génération observés lors de release) vont dans les métadonnées JS et le reçu, pas dans la configuration native qui définit la compatibilité. `extra` du nouveau profil garde seulement les paramètres stables nécessaires (environment_id, URL, profils de contrat). La science actuelle vient toujours du serveur, jamais d'un reçu de build historique.

## C. OTA réellement compatible

Installer le `expo-updates` compatible SDK58 avec Expo CLI ; ne pas mettre à niveau le framework. Utiliser `eas update:configure` Android, projet existant, environnement explicite, et relire son diff dynamique selon les docs ; pas d'URL Updates inventée à la main. Configurer seulement le nouveau profil QA continu ; garder les autres profils sans activation OTA incidente. Canal stable **qa → branche qa**, Android seulement ; aucun nom production ni canal inféré du git branch.

Politique proposée **fingerprint**, standard SDK58 : pas d'exclusion globale de config/plugins/packages. La provenance variable est sortie de la config native plutôt que masquée par une empreinte permissive. Vérifier expérimentalement que la seule métadonnée JS/asset admise conserve la même empreinte ; ajout/modification de module, plugin, permission, identifiant, schéma SQLite ou config native exige nouvel APK et empreinte. À la moindre classification inconnue : refus OTA/new APK, pas downgrade de garde.

Un observateur QA sans UI, consommé par ConnectedApp réel seulement dans ce profil, relève version native, runtime, updateId/isEmbeddedLaunch et source JS sans owner/token/donnée personnelle. Sert au smoke réel : installer APK, capturer embeddedA ; publier après autorisation une révision JS de métadonnées réellement consommées B, télécharger/appliquer sur le client installé, constater updateId/sourceB, relancer, vérifier token/SQLite/séance ; publier rollback connu ou embedded, constater retourA sans perte de faits. Un test mock du SDK ou une doc ne ferme pas cette preuve.

Ni channel, runtime ni backend ne sont modifiés à distance dans l'APK QA02. Nouveau binaire nécessaire. Tant que la cible stable/quotas/diffusion ne sont pas autorisés et attestés, tous les artefacts de préparation restent NON_DISTRIBUTABLE ; aucun nouvel APK à URL factice ou nouveau tunnel de substitution.

## D. CI et autorisation de release

Un seul orchestrateur de release, réutilisant CI GitHub ; pas de deuxième pipeline EAS Workflows payant par défaut. Workflow **manual dispatch uniquement**, candidat exact, aucune publication au push/merge. Préparation/validation possible sans secret de publication. Les jobs publiants demandent un environnement GitHub `qa-release` avec approbation opérateur ; préflight vérifie qu'il est réellement protégé/configuré, sinon refus. EXPO_TOKEN et credentials hébergeur restent secrets administrés, jamais créés/lus dans les logs par défaut.

Ordre : change approuvé → code/tests → CI réelle/visuel applicable → revue HEAD/base → merge gardé → compatibilité/package/cible actuelle → **approbation de release distincte** → build interne ou OTA QA → client installé → reçu/rollback. Le mandat/GO BUILD ne vaut pas approbation de job de diffusion ou connexion/spend. Le GO MERGE n'est jamais utilisé comme GO déploiement. L'agent ne valide pas lui-même le review de publication.

Candidat OTA refuse : SHA sale/non fusionné, checks requis manquants/rouges, visuel nécessaire absent, target non attestée/temporaire/production, channel/projet/platform erronés, native fingerprint différent, versions/schéma/SCI incompatibles, signature d'APK inattendue, approbation absente, update actif en rollout inconnu. Backend release et OTA séparés ; aucune migration DB ni règle SCI par publication JS.

Rollback : re-publier update connu ou retour embedded sur runtime exact ; vérifier après redémarrage. Serveur : ancien build compatible + même DB/faits, sans downgrade/migration destructive. Si ancien code ne supporte plus le schéma ou l'autorité courante, rollback refusé et correctif forward nécessaire. Restaurer un backup est une opération de récupération séparée, pas la méthode normale pour annuler du JS.

## E. Gates et sortie

Tests négatifs/consommateurs selon TEST_SPEC. check_scope avant checks ; risque ci_infra prévu si workflow/dépendances, donc full sweep **local borné** selon scripts actuels, jamais pytest -n auto ou script CI sur le poste. CI réelle exacte obligatoire, revues indépendantes code/autorité/limites. Pixels uniquement si un changement visible devient nécessaire : sortir alors le delta pour croquis/rendu/acceptation, pas d'auto-baseline.

COMPLETE : cible stable réellement servie/persistée, sauvegarde restaurée en copie avec mêmes identités, nouvel APK signé installé en upgrade de QA02 sans effacement, vrai chemin de release contrôlé vérifié (OTA et rollback si OTA annoncé), source/runtime/backend/CI reçus exacts. Physique distinct et OPEN tant que retour testeur absent. Un paquet prêt en code sans fournisseur/autorisation est PREPARED/BLOCKED_EXTERNAL, pas pipeline opérationnel. DATA/production/Store restent séparés.
