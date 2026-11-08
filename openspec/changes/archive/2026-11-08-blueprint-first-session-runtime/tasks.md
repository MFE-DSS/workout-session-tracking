# Blueprint-to-first-session V3 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task **only after explicit PLAN design approval and GO BUILD**. GO_BUILD_CONTROLLED and G1 received; pixels accepted before code commit.

**Goal:** Construire, après autorisation, la première intégration réelle du Blueprint possédé vers une séance native créée une seule fois, lisible/reprenable/journalisable sans invention scientifique.

**Architecture:** Snapshot serveur cohérent et décision V3 négociée ; producteur/validateur SCI admis séparément. Commande atomique et binding de prescription immuable vers WorkoutSession/SessionExercise/SetLog, avec observation de réglage typée et adaptateurs natifs V3 parallèles.

**Tech Stack:** Python/FastAPI/SQLAlchemy/Alembic, SQLite et PostgreSQL selon supports existants ; TypeScript/React Native/Expo existants, outbox/stockage/auth natifs canoniques. Lire expo-overview avant tout futur code mobile.

**Spec:** [design](design.md), [requirements](specs/mobile/blueprint-first-session-runtime/spec.md), [test specification](TEST_SPEC.md), [scenarios](SCENARIO_INVENTORY.md).

## Global Constraints

- GO_BUILD_CONTROLLED reçu le8novembre2026 (BUILD_AUTHORIZATION.md) ; runtime réel désactivé par défaut. Préparation historique ne vaut pas preuve des tâches de build.
- DTO SCI V1/V2/V3, ancien validate_exchange V3 et FirstPlanClient/firstPlan.contract.json V1 inchangés ; pas de réécriture de pins historiques.
- Autorité positive : tools.science_initial_policy.v3_validation.validate_admitted_exchange_v3 livré par SCI stage2 et reçu final à vérifier, jamais fixture/schema/caller label.
- Sept réglages bilatéraux actuels qualifiés/acceptés pour le plan ; rencontre de calibrage distincte sans cette précondition, pilote seulement selon BOOTSTRAP_INTEGRATION. Pas de poids/taille/expérience requis ni inventaire full gym supposé.
- Science/temps/start_permission/séance créée distincts. UNKNOWN ne devient ni0 ni SUPPORTED ; ack réel exact requis selon policy.
- MISSION LOCKED, aucune nouvelle carte/résolution d’action ; rendu opérateur avant tout commit visible ; additive-only, historique invariant.
- Avant les checks futurs : python scripts/check_scope.py puis verdict complet ; migration => checks migration/full sweep local via bash scripts/run_local_sweep.sh, jamais script CI sur poste. CI réelle du HEAD final source de vérité.
- GO BUILD PLAN contrôlé et pixels reçus ; livraison autorisée sous contrôles, jamais activation réelle. Contrôle obligatoire rouge => STOP/rapport, sans élargir scope.

## Review Focus

- POST committé/réponse perdue puis compte changé : aucun second start ni résultat d’un autre owner (Task4/6, T12/T17).
- Ancien formulaire de préférences après capture : révision invalide l’évaluation sans effacer faits/équipement non possédés par ce formulaire (Task2, T03).
- Deux starts SCI/historique ou reopen/restauration : au plus une admission nouvelle, pas mutex mémoire (Task4, T13/T14).
- PER_IMPLEMENT ou MACHINE_DISPLAY_KG : le chiffre n’est jamais totalisé en kg ou perdu après relance (Task5/6, T19/T20).
- Policy retirée après création : faits/session lisibles, sortie/journal possibles, nouvelle consigne bloquée sans effacement historique (Task4/5, T16/T22).

---

### Task 1: Freeze reviewed dependencies and interfaces

**Files:** ce change et docs/strategy/SPEC_REGISTRY.md uniquement pendant la préparation ; futur reçu de livraison PLAN dans docs/plan/blueprint-first-session-runtime/DELIVERY.md.

**Interfaces:** consomme reçu SCI final livré (interfaces effectives PR375 : v3_admission.load_v3_registry, v3_producer.produce_v3, v3_validation.validate_admitted_exchange_v3 ; versions/manifeste/admission/revocations et oracles) ; produit tableau de pins PLAN vivant et lease des fichiers partagés. Ne crée aucun import produit pendant cette tâche. Consomme aussi le pilote livré PR377/378 et ses digests/limites/registre79sources ; pas de bootstrap de plan positif.

- [x] Design/scope PLAN et GO BUILD contrôlé reçus ; G1 validé, pixels encore à présenter.
- [x] Partir du handoff SCI PR375 et du manifeste exact du design (coordination57ec, lecture locale74d30b), puis lire reçu SCI final et vérifier SHA/manifestes/signatures avant d’inscrire les pins/imports produit. SCI est livré/clos sur d7de8aa, quatre CI9jobs réussies ; actualiser seulement si canonique plus récent, sans réécrire les pins. Rejouer les preuves après GO PLAN sans modifier registres/modèles scientifiques, jamais mélanger pins anciens/nouveaux.
- [ ] Pour toute activation réelle, faire admettre DATA (pas préalable aux seules bases synthétiques autorisées par GO) : graphe snapshots/observations/ack/commands/bindings, consent assessment réel, export/fermeture/suppression, ordre de verrous avec compte. Aucune durée arbitraire.
- [x] Accepter namespace/profils/routes, unicité du premier handoff, comportement des écritures/lectures legacy et erreurs du design ; classer chaque route ajoutée dans l’inventaire canonique MOB-00.
- [x] Confirmer le lease des fichiers partagés après SCI : training_preferences/mobile_api/sessions/user_programs/restore/mobile_read_models/models/migrations/ConnectedApp ; aucun writer concurrent non coordonné.

### Task 2: Persist real declarations, observations and coherent snapshots

**Files:** créer app/models/first_plan_runtime.py (les sept modèles exacts de MINIMAL_PERSISTENCE et indexes composites externes), app/services/plan_v3/snapshots.py, app/routers/mobile_plan_v3.py ; migration additive nouvelle, inventaire modèle/data/schema_snapshot.sql selon mécanisme canonique. Modifier app/services/training_preferences.py, ses callers observés app/routers/auth_routes.py, mobile_training_preferences.py et user_programs.py, ainsi que le montage des routes. Tests nouveaux tests/test_blueprint_runtime_sources.py et tests/test_blueprint_runtime_http.py.

**Interfaces:** apply_training_preferences_in_transaction(db, user_id, *, sessions_per_week, focus_priorities, available_equipment) valide/flush sans commit ; wrappers historiques gardent leurs signatures/réponses. Révision MAX(BlueprintSourceEvent.source_revision) contrôlée sous garde, token SCI texte blueprint-source/N ; pas de table SourceRevision. build_owned_snapshot(db, owner_id, *, expected_revision) retourne OwnedBlueprintSnapshot immuable + FirstPlanRequestV3 canonique ; owner jamais body. append_owned_observation(db, owner_id, *, request_id, expected_revision, event) append/rejeu exact sans qualification inventée.

- [x] Réaliser T26/T28/T29/T30/T31 en RED→GREEN : sept tables/FK/indexes/rollback, garde SQLite réelle et authentification préservée, startup sans DDL implicite, source révision cohérente et politique absente bloquant l’activation réelle.
- [x] Écrire T01..T05 en échec : propriétaire/404, cinq familles/manques/conflits, héritage/provenance, anciennes écritures, observations contextualisées et consentement pertinent ; aucune fixture positive servie.
- [x] Lancer tests ciblés ci-dessus, constater l’échec attendu lié aux interfaces absentes, puis implémenter modèles/services transactionnels et routes d’acquisition/capture négociées.
- [x] Capturer bool/int/NaN/futur date/contexte autre owner et doubles captures avec même request_id ; transport snapshot séparé des DTO SCI.
- [x] Relancer ces tests ; PASS attendu avec ancienne API de préférences inchangée, révisions atomiques et rollback sans faits partiels.
- [x] Exécuter check_scope avant vérifications requises. Livrer cette unité seulement sous GO PLAN et dépendances Task1, sans activer port SCI absent.

### Task 3: Evaluate the admitted V3 authority and exact real time acknowledgment

**Files:** créer app/services/plan_v3/science.py et calibration.py ; compléter mobile_plan_v3.py et modèle FirstPlanEvaluation parent/enfant TIME_ACK, sans table d’ack. Tests tests/test_first_plan_v3_runtime_authority.py et tests/test_first_plan_v3_runtime_http.py.

**Interfaces:** evaluate_owned_snapshot(db, owner_id, *, snapshot_ref, request_id, expected_pins) retourne FirstPlanEvaluation persistée et recommendation V3 validée ; acknowledge_time(db, owner_id, *, evaluation_ref, request_id, expected_context) crée TimeAcknowledgmentV3 réel et nouvelle décision. expected_context porte les champs exacts TimeAcknowledgmentV3 du design ; pins proviennent exclusivement de Task1.

- [x] Réaliser T27 en RED→GREEN : bundle SCI hors checkout, imports effectifs vérifiés et absence de nouveau payload READY de fixture. Toucher uniquement fichiers non pinés ; pyproject app-only n’est pas preuve de packaging.
- [x] Écrire T06..T10 en échec : absence producteur/policy, registre/validator final réels, mismatch/owner/stale, science/temps/permission séparés, ack réel exact et invalidations.
- [x] Exécuter les tests ciblés, vérifier échec attendu ; implémenter sélection explicite du profil admis, négociation/états transport et recomputation stricte.
- [x] Tester entrée adulte2/no limitations avec sept réglages qualifiés synthétiques uniquement dans l’environnement de test du vrai producteur ; sans anthropométrie/inventaire global. Bootstrap reste DENIED ; ne copier aucun résultat READY dans app/mobile.
- [x] Tester versions/binding/source retirés, altération profonde et schéma valide non autoritaire ; pas de comparaison permissive.
- [x] Relancer tests Task2/3 : PASS ; aucune évolution des octets/pins V1 ni validate_exchange historique. Autorité fraîche au start reste Task4.

### Task 4: Admit exactly one real first session and reconcile commands

**Files:** créer app/services/plan_v3/transactions.py et app/services/plan_v3/commands.py ; compléter modèles/router V3 ; modifier starts app/routers/mobile_api.py, sessions.py, user_programs.py, réouverture et app/services/restore.py. Tests tests/test_first_session_commands.py, tests/test_session_start_admission.py, tests/test_first_session_recovery_http.py.

**Interfaces:** start_owned_first_session(db, owner_id, *, request_id, body) retourne CREATED(session_id)/DENIED, identique au rejeu exact ; cancel_owned_first_session(db, owner_id, *, request_id, body_digest) retourne CANCELLED ou ALREADY_CREATED(session_id). read_owned_first_session_request et read_owned_first_session_handoff ne lisent que owner. Admission commune impose l’ordre de locks design et garde persistée pour chaque writer.

- [x] Écrire T11..T18 en échec avec vraies connexions/transactions concurrentes et barrières de synchronisation, pas sleeps arbitraires ni mutex du test.
- [x] Exécuter ces tests ; implémenter unicités owner/request_id/digest, handoff unique owner, exclusion des starts concurrents et autorité/version/source fraîche avant commit.
- [x] Couvrir SQLite par écriture/CAS réel et PostgreSQL lorsque supporté ; inventorier chaque transition vers in_progress et empêcher le contournement web/reopen/restore. Plusieurs opens historiques => refus sans réparation.
- [x] Injecter crash avant/après commit et course cancel/start : aucun orphan ni deuxième session ; réponse perdue récupère même session, GET absent ne crée pas nouvelle clé.
- [x] Relancer Task2..4 ; PASS et ancien start toujours son contrat métier hors exclusion concurrente. Ne pas activer création avant projection Task5 et consommateur Task6 validés.

### Task 5: Materialize exact prescription and persist contextual native logs

**Files:** créer app/services/plan_v3/execution.py et app/services/plan_v3/journal.py ; compléter binding/observation de série, routes V3 ; modifier projection dispatch dans app/services/mobile_read_models.py et gardes du profil dans routers mobile/web concernés, sans changer MISSION. Inventorier/adapter aussi feedback.py, implicit_signal.py, session_recap.py, stats.py, session_completion.py, session_provenance.py, plan_adaptation.py, weekly_planner.py et lectures web/historique/export pour le dispatch de profil. Tests tests/test_first_plan_execution.py et tests/test_first_plan_execution_http.py.

**Interfaces:** materialize_first_plan_session(db, owner_id, *, validated_evaluation, first_scientific_session_id, started_at) construit sans commit séance/binding/lignes ; first_plan_execution_read_model(db, owned_session) rend first-plan-execution/3.0.0 ; record_first_plan_set(db, owner_id, session_id, set_id, *, op_id, expected_set_revision, observation) écrit SetLog+setting/contexte atomiquement et ack durable.

- [x] Écrire T19..T23 en échec : dose/repos/intent/exercise exacts, pas warmups2/1, inconnus conservés, prescription distincte de fait exécuté, réglage typé et corrections/rejeux.
- [x] Exécuter en échec puis implémenter mapping lossless ; invalide/non représentable =>refus AVANT session. Alias court jamais identité canonique. Ne pas appeler constructeur de template/overload/substitutions historiques pour ce profil.
- [x] Vérifier anciennes écritures execution/set/substitution refusent le profil SCI avec execution_profile_required ; pause/finish/abandon canoniques restent utilisables avec dispatch V3 sans dérivés legacy, historique V1 identique. Reprise/sortie/fin/journal natifs conservent source et faits incomplets après retrait.
- [x] Implémenter revalidation propriétaire POST /sessions/{id}/applicability, observation_only et actions courantes ; offline/inconnue/concern bloque nouvelle consigne mais pas journal tardif/sortie. Une série ordinaire ne change pas source_revision d’entrée.
- [x] Dispatch SCI explicite des dérivés/clôture : pas score80, implicit NULL→0, continuité/replanning/record historique incompatible. Comptes factuels conservés ; agrégats non évaluables omis sans masquer la séance. T23 couvre chaque frontière relevée.
- [x] Transitions V3 REST_THEN_SET dans le même slot, SETUP_NEXT_EXERCISE sans durée entre slots, BILAN final ; pas de repos inter-exercice chiffré ni helper legacy aveugle. Le consommateur est couvert par gate visuel.
- [x] Prendre les repos du binding, pas fallback ; conserver sidecar typed pour PER_IMPLEMENT/MACHINE_DISPLAY_KG, weight_kg historique sans faux total.
- [x] Relancer Task4/5 + consommateurs existants ciblés ; PASS avec vrai GET execution puis PUT set et relance DB/session.

### Task 6: Wire negotiated native consumers and durable recovery

**Files:** créer clients/mobile/src/api/blueprintV3.ts, firstPlanV3.ts, firstSessionV3.ts, firstUseV3.ts, modules domain/sync/storage parallèles V3 et tests exactement listés dans BUILD_SCOPE ; adapter composition clients/mobile/ConnectedApp.tsx, stockage/outbox et écrans d’acquisition/proposition/ack après choix visuels. Ne modifier ni firstPlan.ts/firstPlan.contract.json/tests/fixtures V1 ni MISSION/baselines.

**Interfaces:** contrôleur V3 séparé consomme envelope négocié, snapshot/évaluation/ack/command/handoff propriétaires ; composant d’exécution lit profil V3 typé. Contrat d’outbox porte owner/session/profile/request_id/op_id/digest/révision, jamais un nouveau corps à chaque retry.

- [x] Lire expo-overview avant code mobile et les skills routés requis ; écrire tests T24/T25 et T12/T17/T20/T21 au niveau consommateurs réels et HTTP, pas seulement helpers.
- [x] Montrer croquis puis rendu acquisition/proposition/ack/éventuel label typé ; opérateur valide avant commit UI. Comparer aux références LOCKED, une information/source une fois ; aucune baseline auto-acceptée.
- [x] Implémenter table locale journal_v3_set_operations et port transactionnel commun sous propriétaire prouvé ; queue mixte routée par profil, ancien active_session non écrasé avant reconciliation.
- [x] Implémenter sélection V3 explicite, guards de génération aux awaits, persistance avant start, relecture handoff après relance et outbox de série typée. Refus/inconnu/no-producer/manque/consentement restent honnêtes ; aucune redirection MISSION vendue comme succès.
- [x] Vérifier state unknown après logout/compte changé et anciennes réponses ; aucune commande étrangère récupérée. Routes réseau testées réellement contre application de test FastAPI pour scénarios backend et contrat intégré natif selon infrastructure.
- [x] Relancer suites V1 inchangées, tests V3 ciblés, TypeScript et Jest applicables : PASS ; déposer revue visuelle et preuve native contrôlée T32 avant readiness du scope proposé ; T25 Android/iPhone physiques reste gate RELEASE ouverte, sans PASS inféré.

### Task 7: Verify scoped implementation and delivery evidence

**Files:** futur docs/plan/blueprint-first-session-runtime/DELIVERY.md, checklists et SPEC_REGISTRY ; archive OpenSpec seulement après merge effectif.

- [x] Exécuter python scripts/check_scope.py puis tous checks du tier effectif : spec protocol, OpenSpec strict, ruff/budget, ciblés+broad, migrations/drift/snapshot et full sweep local si migration. Aucune commande pytest -n auto, aucun sweep CI sur poste.
- [x] Revue code et SCI indépendantes du HEAD final ; preuve de l’autorité et du mapping, pas nouvelle admission par PLAN. Exécuter T32 dans vraie application native contrôlée et conserver preuve A→J. Préparer/exécuter T25 physiques seulement avec cible/appareils autorisés ; rester OPEN si non disponibles.
- [x] CI réelle/contrôles obligatoires du HEAD final ; Sonar réel consigné consultatif, aucune gate affaiblie. Livraison du scope contrôlé uniquement après GO confirmant BUILD_SCOPE, preuve A→J native et visuel applicable, commit de merge sans bypass sous GO permanent.
- [ ] Vérifier canonique, conserver vrais SHAs/runs/gates et dépendances ouvertes, puis closeout/cleanup des seuls éléments sans travail unique. Ne cocher PLAN-01..07 qu’après preuves effectives correspondantes, jamais grâce à la préparation.

## Réconciliation des entités et des gates du nouveau mandat

Autorité de schéma : MINIMAL_PERSISTENCE (sept tables, trois indexes, aucun champ User/session ajouté). Pas de TimeAcknowledgment/SourceRevision/FirstSessionHandoff séparés ; l’ack enfant Evaluation et le CREATED unique Request les remplacent. Ajouter FirstPlanRuntimeAuthority, absente de la liste initiale. Source SCI et client V1 pinés read-only.

Autorité de scope : BUILD_SCOPE. Ne pas cocher T25/device/DATA-production/déploiement grâce à T32 ou aux bases synthétiques. Ce document n’accorde pas GO BUILD ; aucun test exécutable ou migration ajouté dans la présente préparation.

Résolutions de revue de faisabilité : modes non migré/off/migré existant et kernel source explicités dans MINIMAL_PERSISTENCE ; T28/T30 couvrent off→mutation legacy→on et nouvelle génération après rupture. Le lease natif complet est BUILD_SCOPE (domain/reducer V3, sync/reconcile/transport typés, une table SQLite locale). Pas de huitième table serveur, pas de cast numérique V1. Données synthétiques avant DATA autorisées seulement par le futur GO ; DATA réel avant activation.

## Complément de tâches après réconciliation b4a4242

- [x] Task1 : lire les deux autorités publiées réelles, source closure79 et ancres de chargement, garder historiques immuables ; vérifier le correctif de projection proposé face au mineur d’état SCI.
- [x] Task2/3 : T33–T35 en RED→GREEN, ouverture et événements de rencontre dans BlueprintSourceEvent, deux routes négociées, lecture/recomputation propriétaire et contrôle courant avant action ; pas nouvelle table.
- [x] Task6 : T36/T37, client calibrationV1 parallèle et faits de progression séparés de state/allowed_actions ; pas guidage des six autres ni accomplissement depuis un clic.
- [x] Task7 : packaging privé des preuves pinées, entrée runtime sans appel/import de factory, vrais load/validate hors checkout. Contrats/pins1.0.0 immuables ; ne pas déclarer le mineur SCI corrigé par transport.

## État contrôlé de clôture des tâches — 8 novembre2026

Les cases cochées ci-dessus concernent la réalisation/tests/revues et le scope
contrôlé effectivement autorisé. T25/recette physique, DATA réelle et déploiement
restent OPEN ; leurs mentions dans une tâche composée ne prétendent pas qu'ils
ont été exécutés. Preuves : docs/plan/blueprint-first-session-runtime/TEST_EVIDENCE.md
et UI_REVIEW.md (pixels acceptés «Valider ces pixels PLAN contrôlés»).
Le full backend a terminé418fichiers ; ses deux sentinelles sont revérifiées
(24/24 et14/14 sur tree propre), exit initial conservé. La livraison distante
reste en cours et ses cases ouvertes jusqu’aux résultats observés.

- [ ] T25 / RELEASE : Android+iPhone physiques et compatibilité déployée.
- [ ] DATA : auteur/version/finalités/consentements/copies/rétention/effacement autorisés avant données réelles.
- [ ] Activation/déploiement : autorisation distincte, environnement et rollback effectifs.
- [ ] Six autres premières rencontres : protocole et admission SCI propres, hors ce scope contrôlé.

## Instant de préparation de l'archive

Code PR379 intégré31b89f9 après CI42523124371 neuf jobs réussis.
Archive locale et spec canonique préparées en draft sous le périmètre contrôlé
approuvé ; CI canonique code42526541847 encore en suivi. Les six cases restantes
sont suivies explicitement : cinq dépendances externes (DATA répétée à ses deux
points d'entrée, T25, déploiement, six pilotes) et livraison canonique/cleanup.
Aucune n'est déclarée réussie par l'archivage local ; ce dernier ne devient
canonique qu'à la fusion de maintenance après les contrôles requis.
