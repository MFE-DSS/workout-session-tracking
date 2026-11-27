# SCI-OPS-QUALIFY-01 — exécution après GO du 27 novembre 2026

**GO opérationnel enregistré. Tentative unique déclenchée ; approbation humaine GitHub et précondition disque Mac encore ouvertes.** Ce reçu actualise l'instant de préparation sans réécrire ses résultats.

## Source et tentative exactes
Canonique revérifié : `1ac401f44b8af9444a8521b30cd47b7201fd1c8e`.
Workflow relu via GitHub et comparé aux octets locaux : `.github/workflows/qa-release.yml`, blob `38b959735d46eeea0394486d142ef74e0b152468`, SHA256 `8c679b63f0321c38e5992989dc0bf2bf2391ab7c55cd9436921b2ac97301d74c`.
Quatre checks obligatoires completed/success sur ce SHA ; Sonar consultatif distinct conservé.

Une intention durable a précédé le seul POST dispatch. Aucun run PREPARE_IMAGE de ce SHA n'existait au relevé initial. Réponse reçue, puis tentative acquise indépendamment : [45977551087](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/45977551087), attempt1, branche canonique et SHA exacts. Job `prepare`140432990399 completed/success ; `prepare-qa-image`140433119125 waiting ; `release` skipped conformément à PREPARE_IMAGE. Aucun APK/OTA/déploiement déclenché.

Action humaine propre au run : Review deployments → qa-release, commentaire `APPROVE_QA_IMAGE 1ac401f44b8af9444a8521b30cd47b7201fd1c8e`. L'agent ne l'effectue pas. Aucun second dispatch ne sera envoyé pour contourner cette attente.

## Préconditions observées
- VPS :44 232 839 168octets libres,6 146 682 880octets de mémoire disponible ; limites20Gio/3Gio PASS. Architecturex86_64. Aucune collision de nom conteneur/volume `auren-sciops01-`. QA/workout/varro/nginx/docker observés active ; inventaire conteneurs/config/montages conservé en privé. Aucune mutation distante.
- Mac :20 004 397 056octets libres, soit18,631Gio au relevé. **Acquisition/transfert HOLD** tant que le seuil20Gio n'est pas atteint. Investigation non destructive uniquement ; [28entrées de caches proposées](DISK_PRECONDITION_DELTA.md),1,914Gio alloués, aucune suppression. Les node_modules partagés sont exclus.
- Garde privée existante : dépôt réellement private, release448927197 retrouvée, variables et noms des secrets requis présents. Trois références locales relues par métadonnées : clé image32octets, token et config privés réguliers/nonliés, fichiers sans droits groupe/autres, parent0700 ; dépôt/release/key_file concordants. Aucune nouvelle clé et aucune valeur secrète copiée dans le paquet.

## Verdicts actuels
| Contrôle | État |
|---|---|
| Catalogue / parité SCI | Acquis SCI03 conservés ; nouvelle image HOLD |
| Image exacte de déploiement | HOLD — job de build en attente d'approbation |
| Confiance des chemins opérationnels | HOLD — aucun montage du nouveau paquet créé |
| Runtime / ressources | HOLD — campagne sur la nouvelle image non exécutée |
| Lecteur prêt pour activation QA | NO ; toujours DISABLED |

Le build cloud autorisé peut attendre son approbation malgré le HOLD local ; celui-ci empêche toute acquisition/transfert ultérieurs. Aucun profil de déploiement, raccordement des trois paramètres SCI ou SCI-ACTIVATE-01 exécuté par anticipation.

## Conservation
Preuves : `sci-ops-qualify-01-evidence-20261127/execution-20261127/` hors Git, avec acte opérateur, intention/réponse/run/jobs, préflights, garde et inventaire disque. Pas de code produit, CI, worktree ou service existant modifié. La revue de préparation et les315tests précédents ne sont pas renommés qualification de l'image.

Incident de relevé local : une ligne de commande de processus a affiché une clé de service héritée. Arguments bruts ni valeur de clé sauvegardés dans ce paquet ; les relevés suivants filtrent les références en mémoire et n'émettent que métadonnées. Cette clé doit être révoquée/remplacée par son propriétaire ; aucune modification de secret existant n'est incluse dans ce GO.
