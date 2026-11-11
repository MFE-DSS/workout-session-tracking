# MOB-05A — parité du pilote

10novembre2026. VERIFIED_NATIVE ci-dessous signifie preuve dans le banc contrôlé
avec consommateur de production et HTTP réel ; ce n'est pas une preuve dans
l'APK QA02 déjà remis au testeur. Le nouveau code n'est pas encore fusionné.

| Fonction | Preuve contrôlée actuelle | APK QA02 source5ed4e0e2 | Limite/operation suivante |
|---|---|---|---|
| Today reprise/choix réel MOB04 | VERIFIED_NATIVE iOS ; PARTIAL AndroidHost | PARTIAL : nouvelle orientation non distribuée | Code401/402fusionné, prochain paquet REL03 autorisé |
| Séances/détails | VERIFIED_NATIVE iOS ; VERIFIED_NATIVE présentateur Android | NOT_SERVED | Pixels/CI/merge puis APK compatible |
| Exercice/occurrences exacts | VERIFIED_NATIVE iOS ; VERIFIED_NATIVE présentateur Android | NOT_SERVED | Aucun delta/record inter-contextes |
| Fréquence réalisée sur période | VERIFIED_NATIVE rootiOS/AndroidHost + services141PASS | NOT_SERVED | Planning daté DOMAIN_ONLY/absent, aucun taux inventé |
| Poids BodyMeasurement read-only | VERIFIED_NATIVE root/graphique, source existante | DOMAIN_ONLY pour ce parcours | Accord applicable, pas de writer nouveau |
| Historique SCI typé | DOMAIN_ONLY + client réellement testé ; native complet PARTIAL | PARTIAL journal natif QA02 seulement | Prochaine recette APK sur cohorte guidée applicable |
| Offline/A-B/retour/foreground | PARTIAL : ressources/tests/captures, callbacks4PASS | PARTIAL QA02 borné à son reçu | Appareils physiques/restart du nouveau build requis |
| BODY01 saisie/corrections | NOT_SERVED, préparation séparée | NOT_SERVED | Conflit normatif et GO propre |
| NUT01 journal/Smart Capture | NOT_SERVED, préparation séparée | NOT_SERVED | Provider/policy/coût/GO propres |
| Android app complète nouvelle | BLOCKED dans ExpoGo par module conservé | QA02 ancienne installable, physiqueUNAVAILABLE | Build natif REL03 sous autorisation distincte |

Aucun mock ne vaut parité. MISSION verrouillée, producteurs SCI, compte et journal
canonique conservés ; les séquences BODY/NUT/MOB06 ne sont pas implémentées ici.
