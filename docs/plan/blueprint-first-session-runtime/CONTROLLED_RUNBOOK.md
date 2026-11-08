# PLAN V3 — compatibilité et rollback du périmètre contrôlé

8 novembre2026. Ce runbook décrit le build de test autorisé. Aucun environnement
réel, secret d'exploitation, Store, OTA ou déploiement n'est ouvert par ce texte.

## Matrice backend/client

| Client / backend | Comportement |
|---|---|
| V1 / ancien backend | Contrats historiques conservés |
| V1 / nouveau backend, séances historiques | Même contrat ; garde commune des starts quand le schéma PLAN existe |
| V1 / séance SCI V3 | Refus explicite execution_profile_required, pas de conversion en kilogrammes V1 |
| V3 / ancien backend ou version inconnue | Capacité inconnue/indisponible ou406 ; aucun downgrade ni MISSION rebaptisée SCI |
| V3 / nouveau backend non migré, off | NOT_SERVED, pas de tables/index PLAN créés par startup |
| V3 / schéma/bundle incomplet ou autorité absente | Refus fermé ; pas d'évaluation/permission depuis cache ou schéma JSON |
| V3 / test contrôlé explicitement actif | Négociation exacte, snapshot possédé, vrai SCI, ack et commande ; aucune production activée |
| V3 / création/acquisition/guidage coupés après faits | Lectures, réconciliation, faits permis et fin conservés ; nouvelles consignes UNKNOWN/BLOCKED |

Versions exactes : first-session-runtime/3.0.0,
first-plan-request/recommendation3.0.0, first-plan-execution/3.0.0,
first-calibration-encounter/1.0.0. Le transport vérifie propriétaire et écho ;
le serveur choisit l'autorité, le sujet et l'instant. Un client ne choisit pas
une policy APPROVED dans son body.

## Reproduire les contrôles autorisés

Utiliser un checkout isolé du SHA livré, un venv compatible déjà installé et des
bases jetables. Commencer par python scripts/check_scope.py. Les tests versionnés
test_first_plan_v3_runtime_packaging, test_first_session_recovery_http,
test_first_plan_execution_http et test_first_calibration_runtime_http exercent
la vraie API/SCI et les reprises sans comptes privés. Le test de packaging
copie app/data hors checkout et reconstruit le bundle via
scripts/build_plan_v3_runtime_bundle.py ; le sous-processus ne dispose d'aucun
fallback vers le poste.

Pour le full local de ce tier MIGRATION : bash scripts/run_local_sweep.sh, lots et
watchdog mémoire inchangés. Jamais run_ci_pytest.sh sur le poste ou pytest -n auto.
Pas de full local redondant après une maintenance documentaire.

La preuve native utilise un simulateur dédié, un serveur127.0.0.1, APP_ENV=test,
une base vide et une publication opérationnelle explicitement de test.
EXPO_PUBLIC_PLAN_V3_CONTROLLED_TEST=1 sélectionne le consommateur parallèle ;
l'auth et la résolution de propriété restent obligatoires. L'app de test possède
une configuration distincte ; la preuve observée utilise Expo Go sur l'instance
dédiée, pas un IPA de distribution. Ne pas réutiliser les installations QA MOB02,
les comptes privés ou un APP_ENV réel. Les scripts et captures de la preuve sont
conservés avec le reçu ; ils ne sont pas un entrypoint d'exploitation.

## Rollback sans perte

Couper les nouvelles acquisitions/évaluations/créations/consignes avec les flags
existants. Conserver le schéma, le bundle nécessaire aux lectures autorisées et
le kernel d'invalidation des propriétaires déjà entrés dans PLAN. Une ancienne
version du backend incapable de protéger le marker SCI n'est pas un rollback
admissible. Ne pas downgrader les tables ni convertir les réglages typés en V1.

Une réponse perdue se réconcilie par sa même identité et le handoff possédé.
Une opération factuelle inconnue conserve son corps ; elle n'est pas résolue
comme un refus connu. Un refus confirmé exige une relecture et le choix
explicite USE_SERVER_VERSION. RESOLVED garde son ancienne saisie et n'est pas
ACKED ; une nouvelle correction est un nouvel acte sur la révision courante.
La clôture en attente reprend ensuite ; aucun fait refusé n'est prétendu appliqué.

DATA doit autoriser les copies/traitements et leur maintien pendant rollback
avant toute acquisition réelle. Le déploiement, ses SHA/configurations effectifs
et les appareils physiques restent une décision RELEASE séparée.
