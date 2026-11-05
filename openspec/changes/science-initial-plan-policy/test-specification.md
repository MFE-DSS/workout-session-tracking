# Tests d'admission et de disponibilité — spécification, non exécutée

Version0.1.0-proposed. Le présent fichier **ne constitue pas des tests passants d'un producteur** : aucun module producteur n'est écrit sans GO BUILD. Les tests v1 existants ne sont ni refaits ni présentés comme des tests du futur moteur.

## Matrice déterministe

| ID | Input / perturbation | Résultat attendu une fois le producteur réalisé |
|---|---|---|
| T01 | Cadence UNKNOWN, autres inputs connus | INSUFFICIENT_DATA, REQUIRED_INPUT_MISSING, aucun nombre de séances deviné |
| T02 | Budgets absents ou nombre incohérent | Absence→INSUFFICIENT_DATA ; cardinalité invalide→rejet structurel v1 avant producteur |
| T03 | Cadence contradictoire avec deux sources distinctes | CONFLICTING_DATA ; INPUT_CONFLICT, aucune source choisie silencieusement |
| T04 | Inputs suffisants, bundle non approuvé | POLICY_UNAVAILABLE ; aucune promotion de policies.state seule |
| T05 | Taille/poids/expérience UNKNOWN ou WITHHELD | Pas de faux manque anthropométrique ; expérience reste UNKNOWN et incertitude explicite ; autres gates inchangées |
| T06 | User.weight_kg hérité sans date | Jamais une mesure datée, pas de charge initiale déduite ni double-write |
| T07 | Priorités modifiées uniquement | Aucun diagnostic ni hausse automatique de dose ; seul ordre d'accessoires/tie-break autorisé ; conflits facultatifs inutilisés ne bloquent pas artificiellement |
| T08 | Environnement inconnu, bundle complet et approuvé | REVIEW_REQUIRED/COMPATIBILITY_UNKNOWN ; aucune salle complète ni vide supposée |
| T09 | Inventaire absent, tous exercices confirmés dans le même contexte | Compatibilité possible sans inventaire ; temps/dose/autres gates restent requis |
| T10 | Confirmation d'un autre contexte ou future à as_of | Autre contexte rejeté par validate_exchange ; provenance future refusée par v1 ; pas de réécriture silencieuse ni de TTL inventé |
| T11 | Tous candidats d'un slot réellement exclus/indisponibles | NO_FEASIBLE_PLAN uniquement après recherche exhaustive dans le périmètre approuvé ; sinon CATALOG_GAP/revue |
| T12 | Alias + ID canonique d'un même exercice | Une seule identité ; aucune duplication ou exposition double |
| T13 | Changement d'ordre du JSON/catalogue/registre | Même sortie canonique et même empreinte de décision sous mêmes références |
| T14 | Candidats admissibles multiples/slots en compétition | Affectation globale déterministe, pas de slot affamé par glouton ; lexicographie stable après contraintes |
| T15 | Changement de version/hash catalogue/politique/engine | Nouvelle référence attendue ; mismatch rejeté, pas de décision ancienne réécrite |
| T16 | Rôle UNKNOWN ou correspondance mouvement/zone incohérente | Borne d'exposition inconnue/CATALOG_GAP, pas de crédit0 ou EXACT artificiel |
| T17 | Comptage normal15zones | Total séries physiques égal somme slots ; rôles/crédits distincts ; pas de conversion implicite11→15 |
| T18 | Temps sans composante haute justifiée | Politique temps absente/non admise→POLICY_UNAVAILABLE ; modèle admis mais non applicable→REVIEW_REQUIRED/TIME_UNCERTAIN et Duration UNKNOWN ; jamais READY grâce à un budget très grand |
| T19 | Temps approuvé borné mais dépassement budget | Pas de repos raccourci ou couverture supprimée ; impossibilité seulement si toutes configurations admises échouent, sinon revue |
| T20 | Cadence1/4–7 connue, hors sous-ensemble2/3 proposé | REVIEW_REQUIRED, CONSTRAINT_VIOLATION expliquant périmètre ; pas « donnée manquante » ou « physiologiquement impossible » |
| T21 | Limitation non comprise/ambiguë dans requête v1 valide ; population hors enum testée séparément | Limitation→revue explicite sans diagnostic ; population hors enum→rejet structurel/admission amont, pas sortie métier sur input invalide |
| T22 | Substitution d'un exercice confirmé | Nouveau contrôle identité/intention/compatibilité/exposition/temps ; pas de READY hérité aveuglément |
| T23 | Toutes politiques réellement approuvées, inputs complets, sélection/contextes,15zones et temps valides | Le **vrai producteur** peut produire READY et validate_exchange doit accepter ; load_kg=null/CALIBRATION_REQUIRED, dose/temps/preuves tracés |
| T24 | Fixture T23 avec1policyref fictive,1contexte changé,1borne inventée ou fingerprint altéré | Validation échoue ou sortie de revue ; pas de test double qui approuve sa propre autorité |
| T25 | Producteur absent côté FirstPlanClient existant | unavailable/NOT_SERVED ; aucune requête MISSION ou recommandation de repli |
| T26 | Fixture producteur réelle via adaptateur consommateur isolé | available seulement après .verify canonique ; pending/insufficient/rejected/unavailable/unknown restent distincts et réponse tardive neutralisée |

## Ordre d'exécution après GO BUILD

1. Écrire tests ciblés RED sur module producteur absent et politiques non disponibles, puis réaliser l'algorithme pur. Zéro accès réseau/compte dans ces tests.
2. Charger vraies références figées du catalogue/crédit et définitions approuvées, non un registre ad hoc autorisant une pseudo-READY. Tester adversarialement les preconditions.
3. Exécuter tests de compatibilité v1 et invariants T01–T24. Générer une fixture READY seulement si le temps et les autres politiques sont réellement disponibles ; sinon livrer le statut bloqué exact, sans fixture positive fictive.
4. Handoff versionné : requête/sortie, empreinte, hashes, politique, preuve d'exécution du producteur et distinction NOT_SERVED. Diff de parité consommateur T25/T26 coordonné avec MOB-03 ; aucune modification mobile concurrente.
5. check_scope avant vérifications locales ; son tier règle Ruff/budget/protocole et broad ciblé. CI réelle et revues avant merge sous GO permanent ; pas de déploiement déduit d'une fixture.

## État après GO BUILD

Le producteur isolé et ses tests sont maintenant réalisés ; la matrice ci-dessus reste le contrat d’admission complet. T23/READY positif et les règles dépendant de politiques admises ne sont pas prétendus verts. Voir REPORT.md pour les tests réellement exécutés et les11fixtures générées, toutes non servies.
