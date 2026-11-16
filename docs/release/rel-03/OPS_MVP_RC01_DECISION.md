# REL03 OPS / MVP RC01 — décision opérationnelle bornée

**Actualisation du 16 novembre après décisions opérateur :** le VPS existant a été maintenu vers Ubuntu 26.04.1 LTS, puis ses services vérifiés après deux boots. Le [reçu de maintenance](EXISTING_HOST_MAINTENANCE_RECEIPT_20261116.md) distingue opérations, incidents et limites. Ce document conserve ci-dessous sa proposition initiale ; aucun achat ni déploiement QA n'est réalisé ou autorisé par son actualisation.

16 novembre 2026, Europe/Paris. **PROPOSITION, AUCUNE MUTATION DISTANTE AUTORISÉE OU EXÉCUTÉE.** Parent relu `c2f01b26823961a09cd5ce903dc76ea203d823e3`. Le mandat OPS autorise les lectures et la préparation indépendante ; il exige une décision distincte avant services, secrets, DNS/TLS, exposition ou distribution. Ce paquet ne rouvre aucun GO produit ni DA08.

**Décision opérateur ultérieure du 16 novembre : réutiliser le VPS existant, sans nouvel achat.** « oui je veux réutiliser l'existant ». Le panier du nouvel hôte a été fermé sans acceptation contractuelle ni paiement ; cette décision remplace le chemin d'achat précédemment autorisé. Les options et commandes « nouvel hôte » ci-dessous conservent leur statut historique de proposition et ne doivent pas être exécutées sur l'hôte partagé. Le [paquet de maintenance de l'existant](EXISTING_HOST_MAINTENANCE.md) fixe la suite et ses autorisations encore nécessaires. Le choix du réemploi ne vaut pas autorisation de mise à niveau, reboot, modification des sauvegardes, déploiement QA ou changement de secrets/DNS/TLS.

## État réel et décision utile

SSH authentifié, clé d’hôte existante vérifiée, lecture du 16 novembre à 09:14:43 UTC : Ubuntu25.04, noyau6.14.0-37, Docker28.2.2/linux-amd64,4CPU,7750Mio RAM dont5881 disponibles,45660Mio disque disponibles. Les huit conteneurs existants, dix-neuf volumes Docker et services workout/nginx sont préservés. L’insuffisance de capacité n’est pas le blocage constaté.

Ubuntu25.04 a atteint sa fin de support le15janvier2026 ([annonce Ubuntu](https://lists.ubuntu.com/archives/ubuntu-announce/2026-January/000320.html)). Un conteneur récent partagerait son noyau et ne corrigerait pas ce problème. Aucun upgrade, reboot ou migration de service personnel n’est inclus.

Le compte `qa-audit`, le collecteur et les trois reçus administrateur sont absents. Le collecteur fort livré ne peut donc pas être utilisé sur cet hôte ; la lecture de qualification via le compte existant n’est pas renommée attestation de déploiement. `nginx -T` réussit, ne contient pas le nom QA ; son digest et les générations de processus sont conservés en privé. Cela décrit les fichiers/processus observés, pas une preuve qualifiée de configuration QA chargée.

`qa.spignos.com` ne résout pas depuis le poste de qualification. `spignos.com` répond avec TLS vérifié pour ses propres SAN, sans SAN QA. L’échec de correspondance TLS sur le hostname technique du VPS ne prouve pas une panne du site. Aucun contournement TLS/hosts ni réemploi du certificat du site.

Le Python du service web ancien est3.13.3 ; ses métadonnées sont FastAPI0.141.1/Starlette1.6.0/SQLAlchemy2.0.52/Alembic1.19.1. Il ne sera pas utilisé comme serveur QA. Le Dockerfile QA reste Python3.11.14-slim avec lock propre, à qualifier dans l’image réelle. Source web observée `90da8461803e87897c3d8f48627c4b704b3cfcd6` ; pas le canonique MVP.

## Brainstorming / Options / Risques / Choix retenu

1. Ajouter QA sur le VPS actuel : ressources disponibles, mais OS hors support et services personnels partagés. Non retenu pour une nouvelle exposition.
2. Mettre à niveau/migrer ce VPS : réutilise sa capacité, mais exige une vraie fenêtre de maintenance, inventaire/sauvegarde/restauration des services personnels et autorisation distincte. Le chemin n’est pas une simple commande Docker et n’est pas exécuté ici.
3. **Proposition recommandée : QA sur un hôte OVH séparé supporté**, même domaine existant, sans toucher au site. Ubuntu24.04LTS amd64,2vCPU/4Gio/40Go minimum proposé ; limite conteneur1CPU/2Gio. Préférence d’isolation et de réversibilité, pas obligation d’acheter si l’opérateur dispose déjà d’un tel hôte.

[Offre OVH consultée](https://www.ovhcloud.com/fr/vps/) : VPS-1 annoncé à partir de3,81€HT/mois (4,57€TTC),2vCPU/4Go/40Go. **Ce n’est pas un devis panier ni une dépense autorisée.** Proposition de budget : au plus6€HT/mois, mensuel sans engagement annuel, aucune option payante ni dépassement automatique. Arrêter avant commande si le panier dépasse ce plafond ou impose une durée différente. Aucun accès au compte de facturation OVH n’a été requis. Une machine existante supportée peut remplacer cet achat après qualification.

Première décision demandée : autoriser uniquement cette ressource QA séparée/qualification dans le budget, ou retenir une maintenance séparée du VPS actuel. **La première décision n’autorise pas encore DNS/TLS, exposition, secrets, image cloud ou APK.** Il serait trompeur de faire approuver un déploiement exact tant que l’hôte, les clés et les octets d’image n’existent pas.

## Séquence d’opérations et diff attendu

Les variables ci-dessous sont des champs à remplir dans un reçu privé après qualification, jamais des valeurs attestées : `QA_HOST`, `QA_SOURCE_SHA`, `QA_IMAGE_ID`, `QA_ENVIRONMENT_ID`, configuration/anchor/digests, clé d’hôte. Toute valeur absente interdit l’étape dépendante. Ne jamais sourcer un fichier fourni comme du shell ou exécuter une valeur issue de JSON.

| Étape | Action exacte prévue et condition d’entrée | Impact / panne / retour arrière | Preuve |
|---|---|---|---|
| Hôte | Hôte séparé Ubuntu24.04LTS amd64 ; qualification SSH stricte, OS, CPU/RAM/disque, versions runtime et ports. Nouveau devis dans plafond seulement après GO ressource. | Aucun service ancien touché. Si besoin de coût/ressource différent : arrêt. Pas de résiliation automatique. | Identité, host key vérifiée hors bande, OS supporté, reçu de commande privé et limites réelles. |
| Gouvernance | Créer après GO un dépôt GitHub **privé** de garde, puis l’environnement `qa-release` avec reviewer humain direct et politique compatible. Désigner les acteurs réels ; l’approbateur image doit être distinct de l’acteur du dispatch. | L’environnement est actuellement absent (404 ; seule `production` listée). Ne pas le créer par simple dispatch. Aucune protection existante abaissée. | GET repository/private, GET environment/rules, références de secrets absentes des sorties. |
| Transport | Appliquer d’abord le delta précis décrit dans `IMAGE_CUSTODY_NEXT_DELTA.md`, après son amendement propre. Puis une seule préparation d’image explicitement autorisée au SHA exact et approuvée `APPROVE_QA_IMAGE <sha>`. | Le job actuel détruit l’archive ; il ne peut déployer son ancien reçu. Il faut produire de nouveaux octets et un nouveau reçu. Aucun upload public ni reconstruction revendiquée identique. | Reçu GitHub indépendant, archive/chiffrement/readback, imageID et entrée exacte. |
| État QA | Sous GO secrets/données : créer une base **neuve synthétique** migrée `program_builder_operations_01`, comptes de test distincts A/B et une session synthétique admissible avant capture d’anchor. Aucun compte/token/DB du site ou QA02 repris. | Proposition de nouvelle identité backend, à accepter explicitement ; l’anchor n’admet pas une base sans utilisateurs/devices. Les fixtures de tests ne sont jamais la base à déployer. | IDs privés, accords séparés initialement absents, anchor, contrôle de collisions et partition compte/backend. |
| Stockage | Créer seulement `auren-qa-rel03-data` et `auren-qa-rel03-config` sur hôte séparé ; UID10001, fichiers0600/dossiers0700, config RO. Remplir les références de clés stables et distinctes NUT/Library/Builder via canal privé approuvé. | Refuser collision de nom, bind personnel, socket Docker, mauvais owner/mode ou secrets non disponibles. Ne pas chown un volume existant. | Essai WAL UID10001 dans le nouveau volume ; références et digests seulement dans le reçu. |
| Maintenance | Charger la seule image qualifiée puis lancer le conteneur neuf sans activation, loopback8088. Voir commande ci-dessous, à ne pas exécuter avant GO. | Toutes les routes métier doivent rester503 ; seul liveness200/data_readyfalse. Sur échec/OOM : arrêter le seul nouveau conteneur, conserver volumes. | Docker imageID/argv/mounts/UID/ressources et liveness local. |
| Activation | Après validation complète config/DB/SCI/backup/export : marqueur `qa-activation/1.0.0` exact et redémarrage explicite du conteneur neuf. Installer collecteur fixe et fichiers root-owned hors checkout, compte d’audit forced-command sans shell/Docker group. | Une instance/un writer. Échec d’une dépendance : fermeture, pas d’augmentation de limites ou remplacement de DB. | Version/health locales, image/config/anchor, générations SCI et tests HTTP propriétaires. |
| DNS/TLS | Après GO exposition seulement : créer A `qa` vers IPv4 qualifiée du nouvel hôte, sans modifier racine/www ; aucun AAAA tant qu’IPv6 non qualifié. Obtenir certificat SAN QA et installer le vhost exact exigé par le collecteur. `nginx -t` puis chargement explicitement approuvé sur le nouvel hôte. | Backup avant chaque fichier/config DNS modifié. Sur erreur : refermer QA et restaurer uniquement ce vhost/RR ; pas de rollback d’autres sites. Le site ancien ne change pas d’IP. | DNS externe/TLS validé et peer attendu, génération nginx administrateur après chargement, observation nonce≤60s avant/après HTTPS. |
| Candidat | Attester la cible réelle v2, fixer le manifest natif final et calculer le vrai fingerprint Android. CI exacte puis autorisation release protégée et **un seul** build interne consolidé. | Refuser cible absente/tunnel/signature différente/version déjà utilisée. Pas de Play ni OTA automatique. | Build EAS terminé, SHA/hash APK/certificat/manifeste/API/schema/runtime puis smoke installé. |

## Commande de maintenance proposée

**Non exécutée.** Seulement sur le nouvel hôte qualifié après autorisation de création, volumes neufs préparés et `QA_IMAGE_ID` reçu indépendamment. Laisser ENTRYPOINT/CMD du Dockerfile intacts. Le réseau `bridge` est imposé par le contrat actuel, pas un réseau dédié déjà attesté. Seul ce service existerait sur l’hôte QA ; aucun réseau personnel n’y sera raccordé. Un réseau Docker différent exigerait un amendement du collecteur/policy.

```sh
set -eu
: "${QA_IMAGE_ID:?digest réellement acquis requis}"
case "$QA_IMAGE_ID" in sha256:*) ;; *) exit 1 ;; esac
test -z "$(docker ps -aq --filter name='^/auren-qa-rel03$')"
test "$(ss -H -ltn 'sport = :8088' | wc -l)" -eq 0
# Avant run : imageID exact, deux volumes neufs qualifiés, healthcheck de l'image
# et toutes les contraintes du collecteur doivent être relus par l'administrateur.
docker run --detach --name auren-qa-rel03 --restart unless-stopped \
  --user 10001 --read-only --cap-drop ALL \
  --security-opt no-new-privileges --network bridge --ipc private \
  --cpus 1 --memory 2147483648 --memory-swap 2147483648 --pids-limit 128 \
  --tmpfs /tmp:rw,noexec,nosuid,size=67108864,mode=1777 \
  --publish 127.0.0.1:8088:8080 \
  --mount type=volume,src=auren-qa-rel03-data,dst=/var/lib/qa \
  --mount type=volume,src=auren-qa-rel03-config,dst=/etc/secrets,readonly \
  --health-cmd 'python -c "import http.client as h;c=h.HTTPConnection(\"127.0.0.1\",8080,timeout=3);c.request(\"GET\",\"/__qa_liveness\");assert c.getresponse().status==200"' \
  --health-interval 30s --health-timeout 5s --health-retries 3 --health-start-period 30s \
  --log-driver local --log-opt max-size=5m --log-opt max-file=2 \
  "$QA_IMAGE_ID"
curl --fail --max-time 5 http://127.0.0.1:8088/__qa_liveness
```

Le healthcheck ci-dessus contrôle seulement le processus ; l’admission exige aussi health/version forts et les preuves indépendantes. La politique/réception administrateur doit être qualifiée avant run. Le vhost autorisé est le texte fermé dans `deploy/qa/observe_ovh.py::verify_loaded_routing`, pas une approximation. Les générations master/workers doivent être requalifiées après reload ou remplacement. Pas de reverse proxy/CDN supplémentaire dans ce profil.

Rollback maintenance : `docker stop --time 20 auren-qa-rel03`, vérifier l’absence de listener8088 et l’état intact des services anciens. Ne pas supprimer volumes/image/preuves. Après des écritures QA, fermer les accès, drainer/arrêter le writer, capturer/exporter les faits courants ; rollback code uniquement vers une image compatible avec ce même schéma/état. Aucun retour à une vieille copie comme writer, aucun downgrade destructif. La restauration se fait dans une destination nouvelle avant bascule approuvée.

## Backup, identité et exposition

Le helper canonique backup/verify/restore est réutilisé sans évolution de cap (128Mio/fichier DB,256Mio/paquet). Copie complète SQLite+manifeste, toutes tables/IDs/digests conservés. Rehearsal local frais :46tables, head réel program_builder_operations_01, intégrité OK/FK0, digests et continuité identiques, source inchangée. **Ces fichiers synthétiques de fixture ne sont pas un état distant ni une base pilote qualifiée.**

Avant toute exposition : export chiffré hors service et restauration en copie constatés ; copie quotidienne et avant chaque release, rétention opérateur proposée7jours sans purge automatique. La sauvegarde annoncée par OVH ne prouve pas la cohérence SQLite ni une restauration d’application. Ne pas enregistrer corps/Bearer/credentials dans les logs ; qualifier également les logs nginx/SSH/Docker. Le vhost fermé actuel ne configure pas explicitement `access_log off` : son comportement hérité doit être vérifié, pas silencieusement changé dans ce paquet.

Audit npm frais :28 advisories (3high/24moderate/1low), notamment node-forge1.4.0 et zod3.25.76, avec propagation CLI Expo. Aucun `npm audit fix` ni upgrade SDK lancé. L’applicabilité image/APK/toolchain et l’audit Python/image restent à qualifier sur les octets réels avant exposition ; ce constat n’est pas une déclaration de vulnérabilité exploitable ni une dispense. Sonar consultatif ne remplace pas ce gate.

## Identité Android et état des preuves

EAS relu : QA02 build `1c56f099-734b-4bf9-87f5-189fef95ccc5` FINISHED, source5ed4e0e2,0.0.1/code2, runtimeVersion et channel null. La signature historique pin reste `12b13109a2a41e2e2c0e97578364793e659a7548da4ce210d0dbd2f912f4bc75` ; aucune nouvelle lecture de keystore ou signature d’un binaire nouveau n’est revendiquée.

Prévu : `dev.auren.releaseqa02`,0.0.2/code3, profil `qa-continuous-android`, distribution internal APK, canal/brancheqa, Expo58.0.17, runtime policyfingerprint. Même package prévu ne suffit pas à prouver upgrade : certificat du nouveau binaire doit être identique, versionCode supérieur ; sinon classer installation séparée, ne pas contourner par désinstallation du QA02 pour « réussir » un upgrade.

La proposition de **nouvelle identité backend** ne réutilise aucun credential/owner/DB QA02. La continuité des données anciennes n’est pas acquise par continuité de package ; l’upgrade et les partitions SQLite compte/backend doivent être exercés. Pas d’uninstall/clear-data automatique, ni d’effacement de faits existants pour la recette.

SDK Android local retrouvé sous `/opt/homebrew/share/android-commandlinetools` : adb, emulator, apksigner36.0.0 disponibles ; aucun appareil connecté, trois AVD répertoriées mais non démarrées/touchées. EAS quota Android observé5/15 utilisés ; disponibilité restante10 à cet instant, sans réservation de capacité ou promesse de coût futur. Canalqa existant vers brancheqa sans update publié ; QA02 ne devient pas OTA-compatible.

PREPARE local frais au c2f01b2 : digest `62ac38059a64a98f4aa088e5fb7147a49e1d694d18e6961d29ce2deba818f5fd`, NON_DISTRIBUTABLE. Config native réelle refuse la cible absente (`Continuous QA target unavailable or not attested`). Ne pas fabriquer un target ATTESTED pour calculer un faux fingerprint final.

Le SHA produit02e6a4d reste ancêtre canonique avec CI complète ; le canonique c2f01b2 est documentaire sans CI push. Le pipeline exige les checks au SHA de build exact : sélectionner un ancêtre approuvé avec les checks effectifs, ou obtenir une vraie CI sur le nouveau source technique ; ne pas attribuer la CI de l’ancêtre au HEAD documentaire. Toute nouvelle cible/fingerprint issue de l’opération exige le changement source relu prévu par le protocole existant.

## Sortie de cette passe

112 tests ciblés existants PASS : backup/restore, serveur supervisé réel des quatre familles, bootstrap, observation et reçus image. Ce sont des preuves locales synthétiques au parent courant, pas ConnectedApp installé contre OVH. Aucun code produit, migration, secret, environnement GitHub ou service distant modifié.

Le candidat doit inclure compte/onboarding, MOB04 Today, MOB05A Progrès, BODY, NUT, MOB06, MOB07 et gardes Legacy/V3. [Contenu exact](RC01_CONTENT_AND_GATES.json) et [recette installée](RC01_INSTALLED_ACCEPTANCE.md). Chaque flux reste NOT_RUN tant que le nouveau binaire/backend n’existent pas ; physique UNAVAILABLE. La suite exécutable dépend d’abord de la décision hôte, puis du delta de garde d’image et des autorisations opérationnelles exactes. Aucune déclaration MVP COMPLETE.
