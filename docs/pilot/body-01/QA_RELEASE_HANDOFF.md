# BODY-01 — compatibilité du prochain candidat QA

Code fusionné par PR407 au merge045a3dbc35fdd0bb6ab49fe50a25ebddeb984af0,
source0aec100b14d72813f5c915c2471bf256d9a6b859 ; CI canonique43656641030 success.
À intégrer au manifeste REL03 avec ces références exactes et les gates restantes. Aucun build APK/OTA n’est déclenché par ce document.

- Backend : migration additive body_measurement_operations_01, parent plan_v3_20261107_01 ; nouveaux writers et lecteurs de têtes doivent être déployés ensemble. Zéro DDL startup, zéro backfill des valeurs historiques.
- API : body-measurements/1.0.0, en-tête X-Auren-Body-Contract, Bearer/no-store, onze routes sous /api/mobile/v1/me/body. Contrat weight-history/1.0.0 conservé ; Progrès nouveau utilise la projection source-aware.
- Science : aucun bundle/registre/hash/producteur modifié. Flags PLAN indépendants, aucune inférence BODY nouvelle. Collecte native fraîche limitée à APP_ENVtest/flag contrôlé ; absence ou retrait d’accord bloque nouvelle collecte.
- Local : body_pending_commands_v1 sur journal/connexion possédés, partition owner/backend ; schémas PLAN/journal_sets/outbox inchangés. Préserver fichierSQLite lors de l’upgrade.
- Rollback : fermer nouvelles acquisitions, conserver schéma/lecteurs têtes/audit et reprise de reçus. Un ancien lecteur brut est incompatible avec une lignée corrigée. Downgrade peuplé refusé ; roundtrip vide ne prouve pas un rollback destructif. Sauvegarde/restauration réelles et cutover sous autorisation de release distincte.
- Binaire QA02 source5ed4e0e2/code2 ne contient pas ce slice. SDK/modules/package/signature/lock inchangés ici ; compatibilité OTA et runtimeVersion à vérifier dans REL-03 sur le candidat réellement installé, jamais déduite de ce diff JS.
- Smoke candidat : compte/accord→saisie→correction→versions→Progrès sans doublon→effacement→kill/réponse perdue→même commande→A/B/backend. AndroidBack/clavier/TalkBack et appareils physiques restent ouverts.
