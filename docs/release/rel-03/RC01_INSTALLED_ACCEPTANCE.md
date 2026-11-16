# MVP RC01 — recette ConnectedApp à exécuter sur le binaire réel

16 novembre2026. **NOT_RUN : nouvel APK/backend QA absents.** Ne pas utiliser cette checklist comme résultat. Garder SHA natif/JS/backend, package/certificat, versionCode/runtime/channel, imageID/source/SCI/génération/schéma et modèle/OS de l’appareil dans chaque reçu. Séparer émulateur et appareil physique.

| Flux | Preuve d’acceptation attendue | État actuel |
|---|---|---|
| Installation | APK terminé, digest/certificat/manifeste vérifiés ; lancement ConnectedApp sans ExpoTopicSubscriptionModule manquant. | NOT_RUN |
| Upgrade QA02 | Même package/certificat/version supérieure ; installer sans uninstall/clear-data, préserver faits et partitions. Sinon installation séparée explicitement classée. | NOT_RUN |
| Compte | Création/login synthétique, token après kill, A/B/A ; aucun fait/commande A visible en B ni dans un autre backend. | NOT_RUN |
| Builder | Créer programme, choisir identités canoniques, ordonner séances/mouvements, prescriptions manuelles ; valider et publier explicitement. Conflit→relecture. | NOT_RUN |
| Library | Même programme publié/readback exact ; VALIDATED non lançable, templates catalogue séparés. | NOT_RUN |
| Départ/Today | Départ contrôlé, même session_id possédée dans Today et journal ; gates Legacy/V3 effectives. | NOT_RUN |
| Séries | Faits saisis, unités MACHINE_DISPLAY_KG/PER_IMPLEMENT conservées, aucune conversion arbitraire en total. | NOT_RUN |
| Reprise | Hors ligne, réponse perdue et force-kill : SQLite durable, UNKNOWN conservé, vérification serveur puis même commande explicite ; pas de nouveau POST automatique. | NOT_RUN |
| Fin/histoire | Clôture, relecture historique propriétaire et Progrès ; faits distincts des prescriptions. | NOT_RUN |
| BODY | Accord applicable, mesure datée, correction/version ; retrait puis gestion minimale d’effacement sans valeurs, relecture CAS et reçu exact. | NOT_RUN |
| NUT | Accord distinct, jour/zone, champs absents≠0, complétude déclarée, cible personnelle, correction/version et reprise. | NOT_RUN |
| Ergonomie | Back Android, clavier décimal réel, safe areas, focus/TalkBack, fonte normale/grande sans commande inaccessible. DA08 et réserves pilote préservées. | NOT_RUN |
| Rollback/update | Référence connue bonne, compatibilité runtime/API/schema et état courant ; incompatible refusé. Aucun OTA sans GO. | NOT_RUN |

Un échec s’inscrit FAIL avec déclencheur, source et effet ; absence d’appareil/outillage=UNAVAILABLE, jamais PASS. Aucune série, mesure ou prescription fabriquée pour remplir la recette. Tests locaux112PASS et fixtures de restauration ne satisfont pas ces lignes installées.

Physique : **UNAVAILABLE**, aucun Android connecté ; l’opérateur a déjà indiqué qu’il n’en possède pas. Le testeur reçoit ultérieurement le vrai APK sous autorisation de distribution, puis retourne modèle/OS/version et PASS/FAIL/UNAVAILABLE. Ne pas redemander un branchement USB à l’opérateur.
