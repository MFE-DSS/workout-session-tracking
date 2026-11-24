# UX11 — build proposé et leases

Base fetchée : 9dd90ac777d21291939bdf6b03d9a4b43ca59d21. Branche spec/ux11-contextual-instrument, worktree persistant ux11-contextual-20261123. GO de continuation reçu le24novembre2026 après présentation du scope/amendement/G1 ; reçu exact dans AUTHORIZATION.json. Pixels et release restent PENDING.

Périmètre demandé : un composite Action pour leg-extensions-assises V3 bilatéral/MACHINE_DISPLAY_KG ; référence serveur de la série précédente de la même occurrence, champs vides indépendants, feedback de commande dans l’objet. Bibliothèque, programme et autres exercices restent canoniques. Copie de recette synthétique distincte, client Android de revue existant, aucune cible QA publique modifiée.

Fichiers produit proposés après GO : clients/mobile/src/ui/contextual/* (sélecteur de source, resource read-only, composite, tests), src/ui/plan/PlanV3ExecutionScreen.tsx (branche de présentation et callbacks existants), PlanV3Host.tsx (passage des props uniquement, aucun changement lifecycle), ConnectedApp.tsx (construction/passage du lecteur propriétaire uniquement), tests consommateurs réels pertinents. Réutiliser TrainingHistoryClient/FirstSessionV3Client existants ; ne pas modifier les API ni DTO. Docs/OpenSpec/registre de ce scope.

Interdits : backend, modèle/migration, DTO et transport contractuels, SCI/calibration, auth, FirstUseV3Controller, domain/planV3Workout/performedAt, handlers AppState canoniques, journal/outbox/sync/stockage, valeurs historiques, dépendances/native/runtime, LOCKED/palette/baselines, OTA/APK. Si le branchement exige un changement hors liste, exposer l’écart avant apply.

Ownership : UX10-01 possède encore un diff unique non committé (32fichiers), figé et sauvegardé ; ses pixels ne sont pas acceptés. DA09.1 reste distinct non accepté. Pas de PR source concurrente. UX11 part du canonique, ne copie pas en bloc UX10 ou DA09 ; il réutilise leurs preuves sans prétendre que leur code est fusionné. Relecture des writers/leases/base avant apply puis avant PR obligatoire. S’il existe un writer actif sur les mêmes fichiers, préparer le patch isolé et attendre sa libération ; continuer les tests/lectures indépendantes.

Après GO/G1 : implémentation/tests pertinents/revue indépendante, un gate natif UX11, pixels opérateur avant commit ; check_scope adapté, CI exacte, merge par commit sous GOV-MERGE-01 sans GO routinier. Aucun merge de checkpoint déclaré comme fonctionnalité complète. Sans pixels, conserver le diff et ses preuves, pas d’archive faussement terminée.

Précision lifecycle : un abonnement AppState read-only propre au nouveau resource est permis uniquement pour invalider/canceller sa lecture de référence. Aucun appel pause/temps/mutation et aucun remplacement des abonnements canoniques.
