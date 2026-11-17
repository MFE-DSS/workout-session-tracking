# OPS-02 — reçu technique et gates réelles

17 novembre2026. Parent canonique348dc8c3fda4a0c9a74be54fe1e92f159e382142. **VÉRIFICATIONS LOCALES TERMINÉES ; CI/INTÉGRATION À ACQUÉRIR ; AUCUNE ACTIVATION QA.** Ce reçu conserve son instant de publication ; les références finales PR/HEAD/merge/CI seront acquises après exécution, jamais anticipées.

## Résultat du delta

Transport de la même archive image vers la garde privée : chiffrement, intention durable avant upload unique, UNKNOWN sans nouveau POST, download/readback et restauration après acquisition indépendante du reçu. Isolation dédiée du VPS partagé et ordre de démarrage ; initialisation exclusivement neuve par vraies migrations, référentiels canoniques et deux comptes synthétiques. Aucun changement app/SCI/migration/UI/SDK/lock/signature.

Revue indépendante du changement entier : fsync et catalogue builder vide corrigés RED→GREEN ; relecture du code sans Critical/Important restant. Relecture finale du paquet opérationnel favorable après correction du SHA post-configuration/CI, du backup initial et des droits des deux volumes. Avis technique, pas GO opérationnel.

## Vérifications locales constatées

- Transport14PASS ; hôte partagé/observateur23PASS ; contexte propre SCI/migrations1PASS ; initialisation réelle avec catalogue1PASS. Ces campagnes sont distinctes et ne remplacent pas la CI.
- Ruff neuf PASS ; budget259≤548 ; actionlint PASS ; protocole PASS ; OpenSpec strict28/28PASS. Aucun seuil ni baseline changé.
- Bandit nouveaux outils :0Medium/High. Scan étendu signale B108Medium sur la constante `/tmp` de la politique de tmpfs existante du collecteur, sans création de fichier hôte ; ligne inchangée. Pas de suppression/neutralisation du signal. Bandit applicatif obligatoire sera rejoué par CI.
- Sweep borné Python3.14 interrompu à187/458fichiers par mémoire ; Python3.11.14 (version cible déjà installée) atteint386/458, puis `test_training_preferences.py` dépasse1600Mio. Aucun test rouge observé dans ces passages. Continuation des72fichiers à partir de ce fichier, dont ses tests divisés en lots de20, sous **le même plafond1600Mio** et sans changer sources/fixtures : terminée :458/458fichiers couverts,8810PASS/3ignorés. Les97tests du fichier lourd ont tous été exécutés ;76lots de continuation verts, pic918Mio. Aucun faux PASS du script interrompu.
- Gitleaks du diff stagé PASS, zéro fuite. CI PR et canonique : à acquérir avant fusion. Aucun run d'une ancienne livraison ne couvre ce diff.

Preuves privées persistantes : `/Users/martinfeldmann/auren-review/rel03-ops02-20261116/`. Aucun secret ou contenu DB publié. Les limites et écarts restent dans les logs, y compris les arrêts mémoire.

## État opérationnel

Observation lecture seule17novembre13:23:26UTC : Ubuntu26.04.1/kernel7.0.0-43, services et huit conteneurs préservés,6178Mio disponibles/43178Mio disque. QA absent ; domaine non qualifié, certificat/vhost QA absents. Backup workout FAILED/resources, ExecStart disparu. Pas de réparation de cet ancien timer dans OPS-02.

**QA endpoint NOT_QUALIFIED ; image réelle non préparée ; backup/rollback QA opérationnels non éprouvés ; Android NOT_BUILT.** `proof-store.json` reste UNPROVISIONED, candidat sans endpoint/runtime/fingerprint réels. Aucun VPS/DNS/TLS/secret/état distant modifié ; aucune dépense, APK ou OTA.

Prochain gate : [paquet opérationnel unique](OPERATIONAL_DECISION.md), avec [actions exactes](COMMANDS.md) et désignation d'un second compte humain GitHub pour conserver la séparation d'approbation existante. Après GO seulement : provisioning privé, configuration avec sa propre CI, image réelle, déploiement isolé et qualification. Le build/distribution Android et l'acceptation physique restent séparés. REL03 demeure actif.
