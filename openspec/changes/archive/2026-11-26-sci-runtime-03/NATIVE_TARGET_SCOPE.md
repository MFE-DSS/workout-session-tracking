# SCI-RUNTIME-03 — autorisation du seul banc Linux natif proposée

26 novembre2026 Europe/Paris. Analyse locale autorisée ; **banc natif autorisé par call_c7d26b9a63444e668003141b1b5c9d04 et exécuté dans les seuls éléments dédiés**. Parent3d4c7577e5ffd39fb59de58d1aab3bded1936edb.

## Cible et identité
VPS OVH existant51.91.79.44, connexionubuntu connue/pin SSH strict existant. Lecture actuelle : Ubuntu26.04.1LTS/x86_64,4CPU,7745Mio RAM,5840Mio disponibles,42Gio disque libre. Aucun achat ni nouvel hôte. L'image historique déjà présente5ee90ab09696c4312cbe2a99654d5d2368d26f2050839858cca0ec801128334e doit être revérifiée contre l'archive/manifeste attesté ; aucun pull/build autorisé ici.

## Écritures exactes proposées
- Conteneurs et volumes Docker **nouveaux** étiquetés auren.scope=sci-runtime-03 et préfixe auren-sci03- ; inventaire initial obligatoire, refus de tout nom préexistant.
- Source Git3d4c757 complète et empreintée montée readonly à /opt/auren, profil TEST_FIXTURE_NOT_OPERATIONAL et bundle source-attesté root-owned/readonly ; aucune lecture/réutilisation des volumes QA/personnels ni de leurs secrets.
- SQLite synthétique neuf, schéma canoniqueprogram_builder_operations_01, jeux A/B/vide et admissibles/adversariaux. Les identités et commandes métier réelles ne sont jamais importées.
- RuntimeUID10001, capsALLdrop/no-new-privileges, rootfsro, réseaunone/aucun port publié,1CPU,2Gio mémoire sans swap,pids128,tmpfs64Mio. Aucun autre processus HTTP que le serveur loopback de test. Limites enfant2/3sCPU/512MioAS/3swall inchangées.
- Root de staging jetable uniquement pour l'ownership initial avec CHOWN ; aucun privilège du service QA modifié. Source/autorité restent ro dans le candidat exécuté.
- Fichiers temporaires privés sous répertoire mktemp du compteubuntu pour les scripts/source Git, maximum256Mio avant nettoyage. Pas de modification /etc,/opt du host, systemd,nginx,DNS,TLS,.env ou secret existant.

## Gardes et arrêt
Avant tout lancement : MemAvailable≥3Gio, disque libre≥10Gio, charge1min<2 sur4CPU ; sinon HOLD sans modifier de seuil. Campagnes sérielles, un seul candidat mémoire à la fois. Plafonds inchangés ; aucune hausse pour obtenir PASS. Vérifier identité/StartedAt/config/mounts/ports de QA et services personnels avant/après sans exposer Env. Arrêt si écart inattendu.

## Conservation et nettoyage
Résultats/logs/digests téléchargés dans le dossier privé SCI03 du Mac ; pas de tokens dans Git/PR. Nettoyer uniquement nos conteneurs arrêtés et volumes sans dépendance, après capture des preuves et vérification des IDs/labels. Aucun prune, arrêt/restart, chmod/chown ou effacement d'un service/volume préexistant. Image historique conservée.

## Portée et décision
Autoriser ce banc natif isolé ne vaut ni GO BUILD produit/CI, ni nouvelle politique de ressources, ni activation QA/DATA/OTA. La source actuelle demeure inchangée ; une optimisation fera l'objet d'un amendement séparé avant apply.

Le mandatSCI03 §3 demande une cible jetable autorisée. Le GO précédentSCI02 excluait les actions VPS ; cette extension opérationnelle précise est donc soumise distinctement, sans supposer son admission.
