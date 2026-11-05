# Conception SCI-P01 / SCI-P02 — v1

## Context

Base canonique90da846 ; consommateur MOB-03 observé en lecture seule à2ba9fd4. Le manifeste v1 est identique à celui reçu dans la branche mobile. `training_preferences` connaît cadence, souhaits ordonnés et matériel nullable ; `User` taille/poids sans date de mesure ; `BodyMeasurement` une chronologie datée avec consentement séparé. Pas de profil canonique persistant d'expérience ou de disponibilité temporelle utilisateur. Un `duration_target_minutes` de séance de programme est une cible de cette séance, pas une disponibilité déclarée.

La chaîne `weekly_volume_budget → weekly_planner/weekly_capacity_allocator → weekly_plan_materialization` est exposée sur le web. Elle emploie11zones et des baselines héritées ; le catalogue scientifique porte15zones et107fiches/84identités canoniques. Les modèles ne sont pas interchangeables. `user_program_generator` tronque des cycles PPL/upper-lower, sans valider un plan global ; `morpho_program_generator` sélectionne des slots mais ne prescrit pas à lui seul une semaine. Les nombres hérités ne deviennent pas des recommandations par leur seule provenance.

## Brainstorming / Options / Risques / Choix retenu

1. Envelopper le premier plan web comme scientifiquement prêt : rapide, mais conserve des hypothèses de dose et de durée non vérifiées. Écarté.
2. Remplacer immédiatement l'ensemble de l'orchestration : trop large, implique schémas partagés, nouvelles règles et UI. Écarté.
3. **Contrat isolé + audit + vérification exécutable**, avec disponibilité future explicite : retenu dans le mandat. Coût : ne livre pas encore un moteur servi ; l'absence de politique validée reste visible même si les données utilisateur sont complètes.

## SCI-P01 — faits et suffisance

Chaque fait porte `state` (`KNOWN`, `UNKNOWN`, `CONFLICT`, `WITHHELD`), une valeur typée et une provenance. L'origine (déclaré/observé/historique/prior) reste distincte de la base de preuve (`STUDY_MEASURED`, `DERIVED`, `CONVENTION`, `UNKNOWN`) de la règle qui l'utilise. Une mesure saisie soi-même reste déclarée comme auto-mesurée ; aucune valeur importée de User n'acquiert une date ou une précision inventée. Des conflits restent présents et référencés ; pas de « dernier gagne » automatique.

Le contrat peut être structurellement complet avec des valeurs inconnues. Pour évaluer un premier plan : domaine bodybuilding fixé par produit ; cadence et budgets de séance explicites ; champ de contraintes avec réponse connue, pas simple absence assimilée à « aucune » ; périmètre de population défini par politique. Expérience utile mais inconnue tolérable uniquement pour une politique qui documente ce cas. Taille, poids, mensurations, souhaits et historique sont progressifs ; leur absence n'est pas une incapacité générale à planifier. Aucune charge initiale en kg calculée depuis le poids/taille, aucune faiblesse inférée d'un rang déclaré.

Le matériel n'est jamais un prérequis d'inventaire. Un contexte de salle inconnu reste inconnu ; une confirmation en contexte peut porter sur un exercice, pas sur tous les objets d'une salle. Une possibilité passée ne prouve pas la disponibilité présente.

## SCI-P02 — décision déterministe

Entrée : snapshot Blueprint, instant explicite, empreintes des référentiels et politique approuvée/versionnée. Même contenu logique + mêmes versions → même identité de décision, hors identifiants d'événement/timestamps de transport. Aucune horloge ou sélection aléatoire implicite.

Étapes normatives : validation → conflits/inputs requis → politique/versions → contraintes dures → éligibilité des archétypes audités → allocation hebdomadaire de la politique → slots et candidats canoniques distincts → compatibilité → temps → explication. Les souhaits départagent seulement ce que les contraintes autorisent. Un départage final par identifiant stable est une convention technique, pas un classement scientifique.

Statuts distincts : `INSUFFICIENT_DATA`, `CONFLICTING_DATA`, `POLICY_UNAVAILABLE`, `REVIEW_REQUIRED`, `READY`. READY exige une politique de dose et de temps explicitement validée, une prescription complète traçable, les contraintes satisfaites et une compatibilité connue au niveau requis. Un plan candidat dont le matériel est inconnu est REVIEW_REQUIRED ; on ne renvoie pas l'utilisateur vers un inventaire. Un moteur incomplet ne doit pas demander artificiellement davantage de mensurations.

La durée est un budget déclaré et une estimation séparée avec modèle/version/composantes et borne de validité. Sans modèle validé, pas de nombre de minutes prédit depuis le nombre de séries et pas de READY garanti dans ce budget. Allocation : séries physiques et expositions par zone/rôle, politique de crédit versionnée séparément, contributions inconnues jamais égales à zéro. Ne pas mélanger les11zones servies avec les15scientifiques sans projection approuvée.

Candidats : ID scientifique canonique, alias/source legacy traçables, exigences connues/inconnues et vérification contextuelle. Substitution : autorisée par domaine, intention conservée, planifié distinct d'exécuté, aucun transfert de charge automatique. Les alternatives portent leurs propres inconnus ; aucune équivalence universelle.

Confiance : absence de pourcentage personnel ; preuve générale, données utilisées, faisabilité, validation de politique et réponse individuelle sont séparées. La réponse individuelle au premier plan reste non estimée. Une préférence ne devient pas une observation et une info manquante n'accroît pas une confiance.

## Packaging / tests / boundaries

`tools/science_contracts/blueprint_first_plan_v1.py` : DTO Pydantic v2 stricts et validation d'invariants de contrat, sans imports app/SQL/HTTP et sans fonction de génération de plan. JSON Schema exportés sous `docs/science/sci-p01-p02/v1/`. Tests et fixtures vérifient structure, inconnus/conflits, branches de réponse, provenance, références, déterminisme de contenu et absence de modification des référentiels. Aucune nouvelle dépendance : Pydantic/pytest déjà présents.

Une fixture Blueprint suffisamment renseignée peut retourner POLICY_UNAVAILABLE : suffisance des données ≠ maturité de l'algorithme. Une fixture de plan historique REVIEW_REQUIRED montre le futur contrat sans approuver sa dose. Les schemas décrivent READY ; aucun exemple n'affirme qu'une politique réelle a été approuvée pendant cette passe.

## Served versus proposed / collision risk

Aucun endpoint SCI-P01/02 n'existe ; MISSION mobile existante et planification web restent servis avec leurs contrats. Les déclarations JSON de la PR353 restent un producteur futur non déployé, distinct de cette base canonique. Un futur adaptateur doit conserver ownership, consentement, snapshot et versions. Seul le module isolé est ajouté ; toute mutation `app/schemas`, `app/models`, `app/routers`, `data/sci` ou UI requiert un change ultérieur et coordination.

## Decisions still needed

Politique initiale de dose (pas une conversion automatique des cibles héritées), budget/estimation de temps, périmètre de population/contraintes, intégration des confirmations contextuelles et projection11→15zones. Cette passe produit pour chaque décision les alternatives et effets attendus, sans en déguiser une en fait scientifique.

## Clarifications après revue de construction

- La suffisance d'inputs est évaluée contre `first-bodybuilding-inputs-v1-proposed`, un profil de collecte séparé de toute politique de dose. Il exige contexte adulte non clinique déclaré, cadence, budgets de temps correspondants et réponse explicite sur les limitations ; il ne constitue ni dépistage médical ni certificat d'aptitude. Cette délimitation reste proposée au produit. Une expérience inconnue reste possible mais exige une politique de démarrage documentant ce cas.
- La politique en entrée est nullable, avec état explicite ; un candidat historique peut être joint comme illustration, jamais comme plan approuvé. Priorité déterministe des statuts : conflit d'un fait requis/utilisé → données requises manquantes → politique indisponible → impossibilité démontrée → revue d'incertitude → prêt. Tous les bloqueurs restent listés, même si un seul statut est principal. Un conflit de mesure facultative non utilisée reste visible mais ne bloque pas le plan.
- Ajouter `CONSTRAINT_UNSATISFIABLE` : données présentes et politiques valides mais aucun plan ne satisfait les contraintes dures ; pas de candidat exécutable. Une disponibilité inconnue n'est pas une impossibilité démontrée et relève de REVIEW_REQUIRED si les autres politiques sont disponibles.
- Dans le paquet actuel, aucune politique réelle n'est promue APPROVED. La fixture suffisamment renseignée peut donc rester POLICY_UNAVAILABLE. Le schéma READY et ses conditions sont définis/testés ; aucun plan historique ne sera artificiellement marqué prêt pour obtenir un exemple positif.
