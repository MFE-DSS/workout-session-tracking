# REL03 OPS-02 — décision opérationnelle unique

17 novembre 2026, Europe/Paris. **NON AUTORISÉE / NON EXÉCUTÉE.** Hôte existant uniquement, aucun achat. Cette proposition suit la maintenance livrée par #422 et le mandat OPS-02. La livraison technique locale, sa CI et son SHA final sont consignés dans DELIVERY_RECEIPT.md avant soumission de cette décision.

## État actuel et impact proposé

Observation fraîche du17novembre à13:23:26UTC : Ubuntu26.04.1, noyau7.0.0-43, huit conteneurs préservés, sept services initiaux actifs,6178Mio disponibles et43178Mio libres sur la racine. Les fichiers nginx et générations de processus sont observés, **pas une preuve de routage QA chargé**. Certbot4.0.0/timer actif ; iptables1.8.11 backendnf_tables. Aucun compte QA, conteneur, volume ou réseau de ce nom n'était présent.

Domaines nginx à préserver et vérifier séparément : spignos.com, varronotes.com, caracalla.co, review.caracalla.co, maltin.io, api.maltin.io, app.maltin.io et preview.maltin.io, avec leurs alias existants. Sept services système et huit domaines sont deux inventaires distincts.

Origine `qa.spignos.com` non résolue lors du probe ; aucun certificat QA ou endpoint QA attesté. GitHub `qa-release` et le dépôt privé proposé renvoient404 à l'accès authentifié courant. Seul le compte humain MFE-DSS est listé parmi les collaborateurs directs. Ces observations seront relues avant écriture ; un conflit bloque l'étape, il ne permet jamais d'écraser.

**Backup workout toujours défectueux :** timer actif, service maintenant failed/Result=resources, ExecStart pointe vers `/srv/workout/.venv/bin/python`, absent. Le précédent Result=success après boot ne prouvait aucune exécution. Il n'est ni modifié ni réutilisé pour QA. Les sauvegardes de maintenance personnelles restent hors de ce paquet.

| Ressource | Création/change proposé | Bornes / conservation |
|---|---|---|
| GitHub | Dépôt privé proposé `MFE-DSS/auren-qa-private`, release de garde dédiée, environnement `qa-release`, références de secrets et reviewer humain direct | Pas de dépôt/image/DB public ; aucune option payante ; pas de protection abaissée. Pas de création si ressource préexistante non qualifiée. |
| Image | Une préparation cloud explicite de l'exact SHA technique livré, approuvée dans `qa-release`, garde AES256GCM et readback des mêmes octets | Archive image≤2Gio−46octets ; ciphertext strictement<2Gio. Même imageID/config Docker/source ; aucune image recréée présentée comme identique. |
| Service | `auren-qa-rel03`, deux unités systemd propres, UID10001 dans le conteneur | 1CPU,2Gio RAM,128pids, rootfsRO, toutes capabilities retirées, no-new-privileges, tmpfs64Mio, logsDocker10Mio×3. Aucun accès Docker donné au compte d'audit. |
| Volumes | `auren-qa-rel03-data` RW et `auren-qa-rel03-config` RO, driver local sans option/bind | Nouveaux volumes seulement,0700/UID10001 ; fichiers privés0600. Aucun volume/site personnel monté. État DB `/var/lib/qa/state/qa.db`. |
| Réseau | `auren-qa-rel03-internal`, bridge `br-auren-qa`, internal, IPv4 seulement, ICC désactivé | Un seul conteneur raccordé. Filtre INPUT dédié en tête, retours établis autorisés puis DROP sur cette seule interface. Aucune policy globale modifiée, aucun flush. |
| Démarrage | Docker restart=no ; systemd ordonne isolation avant lancement et recontrôle le filtre avant chaque start | Pas de fenêtre de démarrage Docker automatique avant installation du filtre. Aucun service personnel arrêté/reconfiguré. |
| Comptes / clés | Deux comptes neufs `qa02-rel03-rc01-a/b` proposés, backend `qa-rel03-rc01-20261117`, références auth/NUT/Library/Builder distinctes ; clés image/proof/audit distinctes | Les préfixes qa02- sont imposés par les contrats historiques, **sans réutiliser leurs comptes, DB, tokens ou backend**. Aucun secret personnel, aucune valeur secrète dans le chat ou Git. |
| Domaine / TLS | Un RR A `qa.spignos.com`→51.91.79.44, pas d'AAAA ; certificat exact QA via compte Certbot existant et webroot propre | Racine/www/autres domaines inchangés. HTTP80 : ACME seulement, autres chemins404. HTTPS : écoute explicite51.91.79.44:443, upstream127.0.0.1:8088, logs de requête QA coupés. |
| Audit | `qa-audit`, clé dédiée, forced-command/restrict, sudo limité au collecteur root-owned | Aucun shell interactif/PTY/forwarding/agent-forwarding/Docker group. Reçus admin de config/activation/routage effectivement chargé. |
| Backup | Répertoire privé neuf, copie avant activation et avant chaque release, acquisition bornée et export chiffré hors writer | Outils backup/restore existants ; caps DB128Mio/fichier,256Mio/paquet conservées. Pas de purge automatique ni rétention de données personnelles décidée ici. Stop avant dépassement du plafond local approuvé. |

## Garde humaine GitHub indispensable

Le protocole actuel exige `prevent_self_review=true`, un reviewer humain direct et un approbateur distinct de l'acteur qui déclenche le run. **MFE-DSS est actuellement le seul humain listé.** Avant toute préparation cloud, désigner un second compte humain habilité et son rôle (acteur du dispatch ou approbateur), avec l'accès minimal nécessaire. Aucun compte invité, rôle ajouté ou approbation simulée par l'agent. Aucune boucle de dispatch par bot destinée à contourner l'auto-approbation interdite.

L'autorisation de ce paquet ne remplace pas le commentaire exact du reviewer dans l'environnement protégé : `APPROVE_QA_IMAGE <SHA exact>` pour l'image. Aucun token ne doit être fourni dans le chat ; les références sont matérialisées dans un canal privé et revues par présence/mode/digest uniquement.

## Exécution bornée après GO seulement

Les commandes et paramètres sont dans [COMMANDS.md](COMMANDS.md). Elles ne sont pas une commande globale à copier-coller. L'agent les exécute séquentiellement après contrôle d'état et conserve le reçu de chaque action. Les identifiants GitHub/image/config dérivés seront remplis depuis leurs réponses réelles, jamais inventés.

1. Revalider SSH strict, services préservés, espace≥20Gio, mémoire disponible≥3Gio, source/CI exactes et absence de collisions. Garder les backups personnels intacts. Pas de reboot OS requis par ce paquet.
2. Provisionner la garde GitHub privée et `qa-release` avec la séparation humaine décidée ; créer seulement les références dédiées. Pas d'exécution cloud si reviewer/permissions/quotas restent inconnus. Aucun achat/plan payant.
3. Livrer la référence de garde CONFIGURED et son contrat OpenSpec dans un delta de configuration borné, puis attendre les propres checks/CI de ce nouveau SHA canonique. Préparer une seule image de **ce SHA contenant la configuration**, avec approbation humaine exacte, et conserver son archive chiffrée privée ; réacquérir run/attempt/job/artefact/checksum auprès de GitHub, relire l'asset et déchiffrer en privé. Le parent OPS-02 encore UNPROVISIONED n'est pas une source d'image admissible. Après réponse perdue : UNKNOWN, lecture de la tentative, jamais nouveau POST automatique.
4. Charger l'image exacte sur le VPS après vérification checksum ; inspecter imageID, plateformeamd64, User10001, Entrypoint/Cmd et source embarquée. Refuser toute différence, pas de tag mutable en substitut.
5. Créer les deux volumes neufs et le réseau/filtre dédiés. Initialiser une DB vide via Alembic jusqu'à `program_builder_operations_01`, puis les seuls référentiels canoniques et les deux comptes synthétiques via les services existants. Aucun `create_all`, aucun import de fixture ni seed de faits exécutés. Le mode `ACTIVE_PUBLISHED` sélectionne uniquement les pins SCI déjà publiés du bundle ; génération opérationnelle initiale1 de ce backend neuf, sous référence du GO, pas nouvelle admission scientifique. BODY/NUT sans consentement accordé implicitement.
6. Valider config privée, références et ancre ; retirer du montage runtime les seules entrées temporaires contenant les mots de passe après conservation du kit privé. Lancer d'abord en maintenance sans marqueur : liveness200/data_readyfalse, routes métier503. Ne pas créer le marqueur avant la sauvegarde/restauration initiale de l'étape7. Si dépendance inconnue : refus, pas de fallback.
7. Sauvegarder/exporter, restaurer en copie jetable distincte et comparer identité/ancre/tables/faits avant exposition. Capturer un rollback en arrêtant puis relançant le seul QA, sans restaurer une vieille copie comme writer. Aucun effacement/downgrade de faits.
8. Après backup/restore validés, créer le marqueur exact et redémarrer QA seul ; obtenir version/health/API/SCI réels. Appliquer le seul A DNS approuvé et le vhost ACME ; vérifier les autres domaines avant/après reload nginx. Obtenir le certificat QA exact, installer le vhost complet généré, nginx-t et chargement explicite. Aucun changement Tailscale. Requalifier réellement la génération nginx, l'activation et le conteneur dans les reçus root.
9. Vérifier depuis l'extérieur DNS/TLS/peer/origin→upstream→container, lectures nonce fraîches avant/après HTTPS, auth et parcours synthétiques propriétaires. Tester absence d'accès aux services hôte/autres réseaux, absence d'egress Internet, réseau unique et reprise après redémarrage du **seul service QA**. Un reboot VPS supplémentaire n'est pas couvert implicitement.
10. Éprouver la sauvegarde QA indépendante avant activation et chaque release ; seulement après résultat effectif déclarer QUALIFIED. Une modification ultérieure des workers nginx, des règles réseau ou du conteneur peut refuser la qualification et impose une nouvelle preuve admin.

## Sauvegarde, limites et rollback

Aucune écriture dans les bases existantes. Avant la première mutation, copies privées des seuls fichiers/états touchés (nouveaux fichiers attendus absents, enregistrement DNS actuel et règles/units existantes inventoriés). La sauvegarde QA précède chaque release ; les copies restaurées vont dans une **nouvelle** destination et restent distinctes du writer. Plafond proposé pour les copies opérationnelles privées de QA :2Gio au total, avec20Gio libres sur le Mac et l'hôte avant acquisition ; arrêt à la borne, aucune purge/augmentation tacite.

En cas d'échec : fermer l'accès QA, arrêter `auren-qa-rel03` uniquement, conserver volumes/DB/clé/preuves. Restaurer uniquement le fichier nginx QA et le RR QA changés, puis nginx-t/reload contrôlé et huit domaines préexistants vérifiés. Ne pas modifier leurs fichiers ni le routage Tailscale. Conserver le filtre QA tant qu'un conteneur y reste raccordé ; sa suppression se fait après arrêt, vérification des références et retrait des seules règles exactes créées. Aucun flush global, volume prune, restauration personnelle ou rollback automatique de la DB.

Le code QA ne revient à une image antérieure qu'après compatibilité avec ce **même état courant** et preuve de source. Après de nouvelles écritures, sauvegarder les faits actuels avant tout autre changement. La restauration d'une ancienne copie ne devient jamais un effacement silencieux des derniers faits.

## Acceptation effective et candidat Android

L'opération est acceptée seulement après HTTPS public qualifié, une instance/un writer, isolation éprouvée, identité image/config/API/SCI/schéma concordante, commandes propriétaires et backup/restore/rollback réels. Une image valide, un localhost200 ou un PREPARE ne suffit pas.

**APK, OTA et distribution externe exclus de ce GO.** Après QA qualifié : figer le candidat consolidé avec tous les merges BODY/NUT/MOB06/MOB07 et les consommateurs antérieurs, source réelle, endpoint embarqué, fingerprint/runtime, schémas et signature. Le profil prévu est `qa-continuous-android`, package `dev.auren.releaseqa02`, version0.0.2/code3, certificat QA02 attendu `12b13109a2a41e2e2c0e97578364793e659a7548da4ce210d0dbd2f912f4bc75`. Ces références ne prouvent pas l'accès actuel à la clé ni une compatibilité d'upgrade. Tester un APK réel sur émulateur après GO build distinct ; préserver l'ancien journal si continuité impossible. Les gates DATA pour personnes réelles et la recette physique restent ouvertes.

## Décision attendue

Autoriser ou refuser ce seul paquet d'activation synthétique QA, avec son plafond de copies et sans nouvel abonnement ; désigner le second compte humain GitHub et son rôle avant toute préparation cloud. Aucun élément bancaire, clé ou mot de passe à transmettre ici.
