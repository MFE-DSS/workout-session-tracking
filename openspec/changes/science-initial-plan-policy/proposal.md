# SCI-P02-INITIAL-POLICY — proposition de producteur initial isolé

## Why

MOB-03 possède FirstPlanClient dans la PR353, mais aucune politique initiale approuvée ne produit un plan READY. Les contrats SCI-P01/P02 v1 sont déjà mergés : ils ne sont pas à refaire. Un Blueprint suffisamment renseigné ne remplace pas la preuve de dose, la faisabilité ou le temps.

Mandat du 5 novembre 2026 : auditer, définir une politique déterministe et son paquet de décision ; si aucun GO BUILD distinct n'existe, terminer proposition/design/tests spécifiés sans prétendre livrer le moteur. Canonique5fd18c3, consommateur353 à0ee7ba3, lu sans le modifier.

## What Changes

- Auditer à nouveau les 18 gabarits, 12 intentions réellement enregistrées, prescriptions et services servis ; conserver hashes et probes purs dans AUDIT.json.
- Proposer `initial-hypertrophy-policy/0.1.0-proposed` : démarrage corps entier borné, paramètres et conventions explicites, attribution directe aux15zones scientifiques, candidats canoniques et contexte d'exercice confirmé sans inventaire obligatoire.
- Spécifier un futur producteur pur, tests de déterminisme/contrat/science et handoff directement adaptable à FirstPlanClient v1, sans endpoint ni changement du schéma partagé.
- Séparer la borne de temps réellement justifiée de la simple arithmétique travail/repos ; aucune constante de transition/échauffement inventée pour réussir READY.
- Exposer les décisions d'admission, dose, effort, temps et sélection avant apply.

## Non-goals

Aucune UI/DA, baseline, modèle ou migration backend, endpoint, persistance de nouveaux inputs, activation du moteur servi, déploiement, nouvelle analyse morphologique ou réécriture des contrats v1. Aucun changement dans le worktree MOB-03. Pas d'archivage de ce change avant réalisation et vérification.

## Capabilities

### New Capabilities
- `science/initial-plan-policy` : politique initiale et producteur déterministe isolé, à réaliser après revue opérateur.

## Impact

Périmètre de cette passe : ce change, `docs/science/sci-p02-initial-policy/`, une ligne du registre. Périmètre de build proposé ensuite : `tools/science_initial_policy/`, `tests/test_science_initial_plan_policy.py`, artefacts versionnés dans le dossier science dédié. Les contrats, données et services existants restent en lecture seule. Les candidats et intentions du nouveau bundle dédié seront référencés par ReferenceSnapshot, sans modifier les intentions historiques.

## Approval boundary

**PROPOSED — GO BUILD NON REÇU.** La précédente autorisation « Valider les contrats et tests isolés » excluait un moteur de prescription. CLAUDE.md§6 impose « explore → propose → revue de l'opérateur → apply ». Le présent mandat conserve expressément cette frontière. Aucun module producteur ou test exécutable nouveau n'est écrit dans cette passe. Le plan de tests est une spécification, pas un résultat vert.

Une approbation du design autoriserait uniquement le producteur pur isolé et ses tests, sous politiques traçables et sans activation/API. Les points non soutenus restent bloquants ; le GO BUILD ne transforme pas une convention en preuve. Merge ultérieur par commit de merge, CI/readiness réelles et GO permanent ; aucune nouvelle demande de GO MERGE ponctuel.

## Approval received

Operator: **« Valider le build isolé proposé »**. Authorizes the isolated pure producer, dedicated registries, tests and generated fixtures described by this design. No API/UI/activation. Scientific admission and supported time remain separate gates; no artificial READY. Initial PROPOSED wording above is historical.
