# Test specification — MOB04

Futurs tests sur vrais services/routes/ressource/host, aucun test exécuté dans cette préparation.

| Cas | Oracle attendu |
|---|---|
| Séance legacy ou SCI ouverte, chacun des deux chemins | Même session possédée prioritaire, profil exact, aucune nouvelle séance |
| Deux séances préexistantes ouvertes | Conflit, aucune réparation |
| FIRST_USE sans schéma/flag/autorité | UNAVAILABLE, aucun appel historique de remplacement, aucun POST de science |
| Trace SQL/worker du GET sur chacune des branches | Aucune DML ; worker authorities seulement si nécessaire, jamais evaluate/produce ni chargement de l'exécution |
| Host V3 absent ou en-tête représentation inconnu | Profil requis/406 selon cas, aucune route legacy pour séance SCI ; capacité client ne donne pas d'autorité |
| FIRST_USE disponible, zéro charge | OPEN_FIRST_USE ; sept rencontres déjà livrées inchangées ; pas sept prérequis d'ouverture |
| V3 prêt mais temps incertain/ack absent | Navigation seulement ; vrai host exige son ack exact et sa commande existante |
| Handoff CREATED rejoué puis séance close | Même session historique ; pas second start ni permission de nouvelle série |
| HISTORICAL prêt ou impossible | Payload/raison/zones de mission_read_model identiques, isStartable conservé ; absence sans défaut |
| Retrait/inconnu/hors ligne après création | Lecture/faits/sortie conservés ; pas de nouvelle consigne V3 |
| Cookie seul, mauvais owner, mauvais echo/profil/commande, source arbitraire | Refus explicite, pas de donnée de tiers ou downgrade |
| A→B→A, logout, mutation/chemin puis réponse tardive | Résultat dépassé ignoré, ressource séparée des brouillons/outbox |
| Bootstrap pending et navigation entre projection/host | Un seul contrôleur/journal, pending conservé, aucun retry source ou start neuf depuis refresh ; version avant start/close invalidée |
| Réponse start perdue, refresh répété | Même commande via réconciliation existante ; GET sans nouvelle identité/mutation |
| Host réel/Today/retour système/détail/grande fonte | Un seul CTA dominant, aucun démarrage implicite, actions atteignables |

Base de broad : tests/test_d9_mobile_sessions.py, tests/test_plan_v3*.py consommateurs concernés, clients/mobile/src/sync/connectedApp.test.ts, API mission/types/auth et tests du host. Déterminer la liste réelle après diff/check_scope ; pas de prétendue CI nouvelle à ce stade.


Réconciliation du mandat PILOT VALUE DELIVERY du10novembre : [PILOT_VALUE_SCOPE](PILOT_VALUE_SCOPE.md) précise base canonique, option de navigation B, commandes locales et leases séquencés. Statut toujours NO_GO_BUILD/G1_PENDING.
