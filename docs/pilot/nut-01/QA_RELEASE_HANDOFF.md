# NUT-01 → REL-03 : intégration du candidat consolidé

Ne pas builder un APK par merge. NUT rejoint le candidat seulement après son HEAD/merge exact et CI canonique, puis MOB-06 et les autres gates explicitement retenus. Le reçu vivant406 et le closeout fixeront ces SHA ; ne pas embarquer le checkpointddcdd4b comme feature complète.

| Contrat | Identité |
| --- | --- |
| Nutrition API | nutrition-manual/1.0.0 |
| Mutation | nutrition-command/1.0.0 |
| Reçu | nutrition-operation/1.0.0 |
| Migration | nutrition_manual_01 → body_measurement_operations_01 → plan_v3_20261107_01 |
| Tables serveur | nutrition_day_revisions_v1 / nutrition_target_revisions_v1 |
| Local | nutrition_pending_commands_v1 sur journal possédé/queue existants |
| Accord | nutrition_manual, wording1, distinct de BODY |
| Nouveaux effets | contexte test + NUTRITION_MANUAL_CONTROLLED_TEST_ENABLED |

Aucun package, module, SDK, lock, runtimeVersion, canalOTA, identité Android ou signature modifiés. L’APK QA02source5ed4e0e2 ne contient pas NUT. Les fingerprint SCI existants restent intacts ; pas de science nutritionnelle ajoutée.

Rollback opérationnel : suspendre les nouvelles acquisitions par configuration contrôlée, préserver données/révisions/reçus et lectures autorisées. Pas de downgrade sur historique peuplé. Restaurer une sauvegarde seulement dans un environnement isolé sous le plan de release ; jamais effacer les observations pour refaire passer une migration.

Recette candidat à exécuter sur le vrai binaire consolidé : installation/upgrade/signature, login/restauration, consentements séparés, zéro/null/jour/zone, cibles et versions exactes, réponse perdue/kill/SQLite/GET sans secondPOST, A/B/backend, offline/reconnect, clavier/retour/accessibilité, compatibilité après redémarrage. Les preuves iOS/Hosts contrôlées sont réutilisables comme cas, pas comme recette Android physique.

OVH existant reste la cible QA à qualifier par REL-03 ; aucun service/DNS/base personnel partagé modifié ici. Autorisations DATA, hébergement/cutover, APK/OTA externe et physique restent distinctes.
