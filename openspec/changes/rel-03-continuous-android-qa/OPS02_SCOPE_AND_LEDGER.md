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
