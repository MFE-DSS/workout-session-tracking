# account-native-release-acceptance — proposition réservée, sans GO BUILD

5 novembre 2026. Suite de la scission GOV-MOB03-SPLIT-01 ; aucun change/PR concurrent. Reprend intégralement les critères déployés/appareil de6.4 et6.5 au HEADd41eb2f, ainsi que les limites physiques du journal/consentement/compte non prouvées par le socle.

## Critères hérités conservés — tous ouverts

- [ ] RELEASE-01 : backend/client par SHA/build identifiés, configurations réellement observées, cible/rollback et GO de déploiement séparé ; ne pas déployer un client dépendant sur backend sans ses endpoints.
- [ ] RELEASE-02 : compteA/B, journal/outbox et historique de poids sans fuite ; credentials expirés/révoqués et réponses tardives, ancien journal non attribué conservé ; aucune substitution de nom de compte à preuve propriétaire.
- [ ] RELEASE-03 : Android physique puis iPhone physique connecté : interruption/force-kill, SQLite/réouverture et synchronisation hors ligne ; preuves par appareil/OS/build/heure, aucun verdict déduit d'un mock, capture web ou build réussi.
- [ ] RELEASE-04 : clavier, retour Android, grandes tailles de texte, petits formats, VoiceOver/TalkBack, focus et coque masquée, cibles44pt ; correction des défauts dans leur scope et gate visuelle si nécessaire.
- [ ] RELEASE-05 : consentement/acquisitions et effacement réels seulement après account-data-activation ; premier READY/démarrage seulement après blueprint-first-session-runtime. Ne pas tester destructivement sur production ou sur les preuves QA MOB02.
- [ ] RELEASE-06 : résultats exacts, couverture des scénarios du runbook et acceptation de release avant publication externe/Store. Aucun effacement, rétention ou conformité Store déclarés depuis un écran indisponible.

Le [runbook MOB03](../MOB03_RELEASE_RUNBOOK.md) est le plan de recette et de rollback, pas sa preuve. Cette suite se limite au compte MOB03 ; android-pilot-readiness (packaging/pilote), native-navigation-shell et session-native-integration/MOB02 gardent leurs gates/propriétaires. Pas de nouveau moteur, de nouvelle surface ni de nouveau contrat de données. Futur OpenSpec proposé/revu avant application.
