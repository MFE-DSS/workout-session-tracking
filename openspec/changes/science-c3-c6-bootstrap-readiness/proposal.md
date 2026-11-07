# Why
Le paquet opérateur C3/C6/1.0.0 propose un départ observé et une convention temporelle produit pour éviter d'attendre un historique que seule l'exécution peut fournir. Le contrat v2 livré impose pourtant une durée SUPPORTED dans le budget avant READY. La pièce recommande elle-même une évolution versionnée (§24–25) et laisse les conventions C6 au PO (§34). Aucune nouvelle borne ou admission positive n'est fournie implicitement par sa réception.

# What Changes
- Conserver intégralement la pièce, sa provenance et les décisions recommandées, et vérifier ses références scientifiques.
- Proposer un contrat majeur v3 séparant admissibilité scientifique, état temporel et autorisation produit de commencer ; préserver READY v1/v2 et leurs consommateurs.
- Spécifier le protocole C3 opérationnel avec inconnus, arrêt, réglages disponibles sourcés et recalibration, sans kg/1RM/échec ou seuil d'expérience imposés.
- Définir les oracles de temps honnêtes : borne structurelle des repos seulement si applicable ; budget non démontré compatible lorsque travail/préparation/opérations restent inconnus.
- Distinguer décision produit du droit de démarrer TIME_UNCERTAIN, admission scientifique du bundle exact et GO de build/activation.

# Capabilities
## New Capabilities
- `science/first-plan-scientific-time-readiness` : proposition v3 orthogonale, non servie ; les trois décisions restent identifiées et autoritaires.
## Modified Capabilities
- Aucune modification de `science/first-plan-v2-binding`, des modèles v1/v2 ou du client v1. Aucune nouvelle autorité admise.

# Impact
Propriétaire de cette préparation : ce change, docs/science/sci-p02-initial-policy/c3-c6-admission-pack-01/, ajout au registre des propositions. Futur build seulement après revue opérateur : modules/types/schémas/tests successeurs séparés sous tools/science_contracts et tools/science_initial_policy, sans modifier sources/pins historiques. Aucun fichier app/mobile, DB/migration, route, UI, asset ou registre existant. PLAN possède négociation, authentification/snapshot, démarrage/reprise et consentement pertinent ; pas de travail concurrent sur ces fichiers.

# Approval boundary
GO_BUILD_STAGE1_RECEIVED : « Valider v3 et ce build isolé », consigné dans BUILD_AUTHORIZATION.md. Étape1 seulement ; les descriptions préparatoires précédentes ne constituent pas admission positive. Le choix v3 et la permission produit conditionnelle TIME_UNCERTAIN ont été explicitement acceptés pour le contrat ; aucune admission scientifique positive n’en découle. Pas de nouvelle API, runtime, collecte ou déploiement. Le GO MERGE permanent reste actif pour les périmètres effectivement autorisés ; ce document n'accorde pas leur build.

# Completion
Stage1 COMPLETE après modèles/schémas/validations et artefacts reproductibles, tests ciblés/broad, revues code/SCI, CI du HEAD et canonique, archive/closeout. Les décisions formelles C1–C6, binding/producteur positif, activation PLAN et recette restent dans la proposition de suite sans réussite prétendue.
