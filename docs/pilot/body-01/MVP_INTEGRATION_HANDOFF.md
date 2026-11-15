# BODY → NUT → MOB06 — parent réel d'intégration

15 novembre 2026. Ce manifeste décrit les sources ; ce n'est pas un candidat
Android ni une acceptation des trois fonctionnalités assemblées.

| Scope | Référence réelle | État courant |
|---|---|---|
| BODY01 | PR407, source0aec100b14d72813f5c915c2471bf256d9a6b859, merge045a3dbc35fdd0bb6ab49fe50a25ebddeb984af0 | Code fusionné, pixels contrôlés acceptés avec réserves ; CI canonique completed/success11jobs |
| NUT01 | Draft406, checkpointddcdd4b15c3639ba2b40c29eb5d615814e0cbc0c et diff conservé | GO technique/G1 fonctionnel acquis ; vraie migration après parent BODY, intégration/consommateur/pixels natifs à terminer |
| MOB06 | Draft408, checkpoint66111aea0052bd8b39cc5d255cb03cff15d95d2c et diff conservé | GO/G1 acquis ; réconciliation après BODY/NUT, ConnectedApp et pixels finaux à terminer |
| MOB07 | Préparation après livraison MOB06 | Aucun constructeur ou moteur scientifique nouveau admis par BODY |
| REL03 | Préparation indépendante, réemploi OVH privilégié | Aucun changement du service existant, cutover, APK ou OTA par BODY |

La note locale non suivie `docs/pilot/mvp-integration/MANIFEST.md`, datée du
11 novembre, est préservée à l'identique et sauvegardée dans les preuves. Ses
anciens statuts GO/non-livraison ne remplacent pas le présent état ni les reçus
plus récents. Aucun travail unique de NUT/MOB06 n'est réinitialisé.

## Contrat pour le parent suivant

- BODY ajoute `body_measurement_operations_01` après `plan_v3_20261107_01`.
  Utiliser ce vrai graphe pour la promotion NUT ; conserver migration additive,
  lecteurs de têtes et reprises exactes, sans création DDL au startup.
- API BODY `body-measurements/1.0.0`, poids historique1.0.0 conservé et projection
  source-aware nouvelle ; SCI et unités de charges d'exercice inchangées.
- Journal possédé et nouvelle partition locale BODY : connexion/file partagées,
  namespaces/owner/backend distincts. Fusionner les ajouts NUT sans remplacer
  les tables, types et gardes BODY. Préserver SQLite lors d'un futur upgrade.
- Fichiers partagés : modèles/export, mobile_api, ConnectedApp, journal/types,
  routeur/config et entrées Profil/Progrès selon leur diff réel. Les anciens
  patches d'assemblage sont des entrées à vérifier sur le parent exact, jamais
  un verdict applicable par défaut. Une PR correspond à un change.
- Après vérification canonique BODY, reprendre NUT406 sur le parent réel,
  terminer la verticale manuelle et son gate natif ; ensuite MOB06408.
  Masters/famille acceptés ne valent pas pixels ConnectedApp NUT/Programmes.

## Release distincte

QA02 source5ed4e0e2/code2 ne contient pas BODY. Le futur manifeste REL03 doit
énumérer uniquement les slices fusionnés, API/schéma/runtime/signature compatibles,
backend QA stable autorisé, sauvegarde/rollback et smoke installé. Pas d'APK par
merge, pas d'OTA supposée compatible. DATA, exposition réelle et recette physique
restent séparées. Voir QA_RELEASE_HANDOFF.md pour les contraintes BODY.
