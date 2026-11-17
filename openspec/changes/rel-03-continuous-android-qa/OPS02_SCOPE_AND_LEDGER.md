# REL-03 OPS-02 — amendement technique local et ledger

17 novembre2026. Parent exact348dc8c3fda4a0c9a74be54fe1e92f159e382142. Mandat opérateur « Existing OVH VPS → Isolated QA → Consolidated Android MVP », reçu dans la session ; copie privée conservée. Ses §2–5 demandent explicitement de finir le transport/configuration/isolation en local avant un seul paquet opérationnel. Les GOs REL03 et OVH restent acquis. **LOCAL_ENGINEERING_AUTHORIZED / NO_OPERATIONAL_GO / NO_APK_OR_OTA.**

## Brainstorming / Options / Risques / Choix retenu

Réemployer le codec AES-GCM et le dépôt privé déjà prévus plutôt qu'une registry ; expliciter la liaison absente du producteur metadata-only. Le réseau bridge partagé et le restart Docker antérieurs n'ont jamais été déployés : le VPS partagé requiert un bridge interne propre, un filtre hôte borné et un ordre systemd. Initialiser un état neuf par les migrations et seeds canoniques, sans importer une fixture historique. Le SHA image doit contenir la future configuration de garde et obtenir ses propres checks ; l'ancien SHA non provisionné ne suffit pas.

## Leases et amendements explicites

Ce seul change possède `tools/qa_delivery/{image_transport,initialization}.py`, les deltas `image_receipts.py`/`ovh_observation.py`, `deploy/qa/{Dockerfile,observe_ovh.py,isolate_network.py,auren-qa-isolation.service,auren-qa-rel03.service}`, `.github/workflows/qa-release.yml`, leurs tests dédiés, les docs REL03/registre et ce change. Aucun fichier produit partagé, migration, SCI, UI, module natif, SDK/lock ou baseline modifié. Le checkout opérateur et les autres worktrees restent conservés.

Le présent amendement remplace explicitement les propositions jamais appliquées suivantes : metadata-only sans garde par custody optionnelle explicite ; bridge/unless-stopped par réseau interne nommé/restart=no/systemd ; TLS wildcard par écoute publique qualifiée ; initialisation absente par commande one-off sur état exclusivement neuf. L'ancien codec local2Gio reste compatible, mais le transport fournisseur ajoute une borne ciphertext strictement inférieure à2Gio. Caps DB128Mio/fichier et256Mio/paquet inchangées.

## Réalisation et preuves

- Transport : intent fsync fichier+répertoire avant un seul POST, UNKNOWN après réponse perdue, readback réel des bytes, repos privé fermé, redirection sans Bearer, restauration après acquisition indépendante du reçu GitHub. Tests RED puis14PASS, dont2RED de durabilité corrigés. Aucun upload réel.
- Hôte partagé : observation du réseau/attachements/règles INPUT, helper fermé et units propres, HTTP ACME80 compatible avec les listeners existants et TLSIP explicite.23PASS. Probe Docker local jetable : le gateway-mode isolated ne publie pas le port ; cette option n'est pas retenue. Aucun objet étranger modifié.
- Image : migrations/alembic.ini réellement inclus dans le contexte propre ; test SCI+graph Alembic1PASS après RED. Aucun changement de migration.
- Initialisation : DB vide réellement migrée, référentiels et catalogue builder non vide, deux comptes/device synthétiques, zéro mesure/nutrition/fait exécuté, FK propres et retry refusé. Test1PASS ; revue a révélé le catalogue vide, témoin RED puis seed canonique GREEN.
- Revue indépendante du code : défaut fsync et catalogue corrigés ; aucun Critical/Important restant identifié. Trois défauts du paquet opérationnel (SHA post-configuration/CI, codec du backup initial, droits des deux volumes) sont corrigés dans COMMANDS.md, relecture finale favorable, aucun Critical/Important restant identifié.
- Préflight SSH strict lecture seule17novembre13:23:26UTC : OS maintenu, sept services actifs, QA absent,6178Mio disponibles/43178Mio disque. Timer workout actif mais service backup FAILED/resources, chemin ExecStart absent ; aucun repair silencieux.
- Vérification : tierCI_INFRA, OpenSpec28/28 à l'état initial ; campagne globale locale458/458fichiers,8810PASS/3ignorés ; script interrompu à386 puis continuation72fichiers sous le même plafond1600Mio,97tests du fichier lourd découpés en lots20, aucun test omis/modifié. CI/PR/merge non exécutés à cet instant.

## Bornes restantes

Paquet concret [OPERATIONAL_DECISION](../../../docs/release/rel-03/ops02/OPERATIONAL_DECISION.md), commandes associées et reçu de livraison. Le second compte humain GitHub doit être désigné pour respecter prevent_self_review et approbation directe. Aucun provisioning, secret, DNS/TLS, service distant, cloud image, Docker load, APK ou OTA autorisé par la livraison technique. REL03 reste actif jusqu'aux preuves opérationnelles et installées ; aucun faux archivage COMPLETE.

## Correctif feuille avant livraison finale

Observation nginx-T : conf.d précède les sites existants et aucun default_server nest déclaré. Le chemin fixe est corrigé vers sites-enabled/zz-auren-qa-rel03.conf ; le paquet exige de comparer routage/certificat par défaut avant/après. Deux témoins de chemin RED puis25GREEN,169tests consommateurs PASS ; relecture indépendante favorable. Le sweep global précédent reste un reçu de son état ; pas de replay local complet pour cette feuille, CI finale exacte requise. CI initiale44095240072 success11jobs sur2ac1a60, non réutilisée comme preuve du HEAD corrigé.


## Actualisation explicite — opérateur solo,17novembre2026

Le blocage « second compte humain » ci-dessus est historique et remplacé par la décision « je travail seul donc uniquement le mien, MFE-DSS ». [Amendement, options/risques/choix et plan](SOLO_OPERATOR_AMENDMENT.md). MFE-DSS seul, self-review permis explicitement, bypass administrateur désactivé ; approbation réelle du run/SHA toujours requise. Aucun auto-approve de l'agent, aucun nouveau GO produit/SCI/APK/OTA. Correction bornée de la préparation d'image pour respecter cette politique déjà supportée par la publication générale ; anciennes protections si true conservées.


## Correction de récupération du 17 novembre — endpoint GitHub

### Brainstorming / Options / Risques / Choix retenu

Le run image44166495880, source389221fa821c58e4119d93c1c69645ab5504ac72, est successful et approuvé par MFE-DSS avec le commentaire exact. La récupération refuse ensuite GET `/repos/MFE-DSS/workout-session-tracking/` (404), après téléchargement du reçu200. L’endpoint sans slash est déjà employé par `pipeline.gh_get`. Choix : corriger seulement la construction de cette URL et rendre la frontière HTTP de test fidèle (root canonique200, variante slash404, accès refusé toujours bloquant). Ni ignorer le404, ni remplacer les contrôles par un reçu copié, ni reconstruire l’image ne corrige cette cause. Risque : casser les suffixes des autres lectures ; la suite image et ses consommateurs servent de garde. Aucun changement du producteur, Dockerfile, image, app, SCI, DB, UI ou autorisation.

Plan borné : régression RED → correction minimale → GREEN ciblé/broad QA selon check_scope → revue indépendante → PR/CI/merge gardé → reprendre la lecture des mêmes octets avec le client corrigé. Le nouveau SHA du client ne réattribue pas l’image source389221f. Correction couverte par le scope REL03 et GOV-MERGE-01 ; aucun nouveau GO.

Vérification avant commit : tier ISOLATED ; RED2échecs/30PASS, puis broad `tests/test_qa_delivery_*.py`402PASS (une dépréciation Starlette/httpx existante), Ruff des deux fichiers PASS, budget259≤548, protocole PASS, OpenSpec28/28, Bandit-ll PASS et Gitleaks outils PASS. Les exécutables Ruff/Bandit n’étaient pas présents dans le venv QA : invocation des outils déjà installés du checkout opérateur, sans installation ni modification de son venv. Aucun full sweep local. Revue indépendante du diff complet : zéro Critical/Important/Minor. Test réel du client corrigé : même run44166495880/attempt1/artefact14366208172, `QA_IMAGE_RESTORED_AUTHENTICATED_NO_DOCKER_LOAD`. Ce reçu ne vaut aucun chargement VPS ou release. CI exacte et closeout encore à suivre après publication.


### Second défaut réel — identité exportée, même correction OPS

Après récupération et transfert vérifiés (image75357184octets, SHA25676cbbd867c22d223a7d2cbf8deb72c7e6439d3525c4c93cada5ff8102462a069), le seul Docker load autorisé ne démarre aucun conteneur. Le reçu indique `sha256:1ade5a8337ad39f2630519b39bf67db4a7a75ea336b810caf7ddb9506ea03ee6`, index OCI containerd ; le VPS expose `sha256:6d08d4880cf4ab0d3c5bb324ddb21ef369f8f3f9bee5079a295f7878cff4a32a`, configuration amd64 effectivement incluse. Le contrat OVH_EVIDENCE_AND_CONFIG exige déjà le digest de configuration, pas celui d’un manifeste. Le producteur emploie à tort Docker inspect.Id comme si sa sémantique était portable.

Choix : calculer le digest de configuration depuis les octets exportés, vérifier le chemin content-addressed, le profil/source et les couches contre l’inspection de l’image, puis publier ce digest contractuel. Ni modifier le moteur Docker du VPS partagé, ni réécrire le reçu389221f, ni accepter des IDs arbitrairement différents. Ce correctif du producteur reste dans le même scope/PR427 ; il exigera sa propre CI et une nouvelle préparation d’image approuvée. L’image389221f est conservée comme preuve de l’écart, jamais déclarée qualifiée. Les services, volumes, réseau QA et DNS/TLS ne sont pas créés.

Vérification du second correctif : six cas RED (nouvelle API de calcul absente), puis38tests image PASS et broad QA408PASS sur l’état corrigé ; une dépréciation historique Starlette/httpx. Le calcul sur l’archive réelle retourne6d08d488… et correspond à l’inspection VPS, sans modifier son ancien reçu. Revue indépendante complète : aucun Critical/Important ; un mineur de fidélité de fixture (Layers vide contre rootfs non vide) corrigé avec une vraie couche tar et son diff_id. Pas de seconde relecture de ce seul changement de fixture revendiquée. Ruff/budget259≤548, protocole, Bandit-ll et Gitleaks PASS. L’ancien run CI du premier commit ne couvrira pas le nouveau HEAD ; une nouvelle CI sera attendue, sans annulation manuelle ni résultat hérité.


### CI finale044b41c — échec de fixture de checksum

Run44177319803/job134372169626, pytest shard3, step Run pytest with coverage : `test_store_refuses_unsafe_remote_before_upload_or_import[wrong_checksum]`, `DID NOT RAISE ValueError` (1724PASS/2ignorés dans ce shard). Cause vérifiée : la corruption remplace le dernier octet du ciphertext aléatoire par X ; si ce dernier vaut déjà0x58, aucun octet ne change (probabilité1/256). Ce n’est ni une annulation infra, ni une preuve d’un garde crypto défaillant. Patch minimal en scope : XOR1 du dernier octet, conservation de longueur et de toutes les assertions de refus. Le RED CI est conservé ; aucun simple rerun pour chercher un vert. Nouvelle CI de tout le HEAD après correctif, sans réutiliser l’ancien résultat.

Correctif de fixture vérifié : broad QA408PASS, une dépréciation historique ; Ruff/protocole/budget259≤548 PASS. Le témoin mathématique sur256valeurs confirme l’ancien no-op à88 et la différence garantie par XOR1. Revue indépendante finale des quatre fichiers : zéro Critical/Important/Minor ; fidélité de couche tar relue et résolue. Aucun garde de production ni seuil modifié. Le prochain HEAD exact attend sa CI complète ; aucune réussite de44177319803 n’est prétendue.
