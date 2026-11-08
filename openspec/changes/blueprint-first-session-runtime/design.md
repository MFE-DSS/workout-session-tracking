# Design — Blueprint propriétaire vers première séance V3

## Context

**Préparation du 7 novembre 2026, base initiale9717368, réconciliée au canonique b4a4242 le8novembre2026 ; aucun apply autorisé. [Intégration du premier calibrage](BOOTSTRAP_INTEGRATION.md).** [Proposal](proposal.md), [test specification](TEST_SPEC.md) et [scenario inventory](SCENARIO_INVENTORY.md) voyagent avec ce design.

Observé : TrainingPreferences conserve cadence/priorités/familles/objets distincts ; NULL n’est pas []. Ses deux writers committent séparément. FirstPlanClient utilise les schémas V1 et un port absent par défaut ; FirstUseController retourne SESSION_HANDOFF_NOT_SERVED après un résultat scientifique valide. Aucun ne construit de Blueprint.

POST /api/mobile/v1/sessions prend template_slug sans évaluation SCI ni clé idempotente. latest_open_session suivi d’insert n’est pas une exclusion transactionnelle. instantiate_session ajoute deux warmups puis au moins un aux autres exercices, même avec warmup_sets=0. Le read-model d’exécution lit dose depuis template et calcule overload/préremplissage/substitutions historiques. Stocker seulement une SessionExercise ne préserverait donc pas la prescription SCI. Les FK template sont nullable et SetLog est le journal canonique des séries.

Types SCI existants : FirstPlanRequestV3, FirstPlanRecommendationV3, Blueprint1.0.0 imbriqué, profil first-bodybuilding-inputs/2.0.0 et PlanV2 qualitatif. V3 n’est pas V1 renommé et ne demande pas V4. L’ancien validate_exchange V3 reste historiquement négatif. Le profil admis implémenté isolément dans SCI PR375 est tools.science_initial_policy.v3_validation.validate_admitted_exchange_v3 ; le code est fusionné89c7eb2 et le closeout d7de8aa, sans import produit PLAN ; CI canonique finale suivie dans la passation.

## SCI stage2 handoff reference — livré, runtime non servi

Base PLAN initiale9717368 réconciliée par avance rapide à **d7de8aa02248c63d8914fb69f8c4c8a9fd980ee0**, après sauvegarde des sept documents et de l’append propre au registre ; aucun travail opérateur/ARCH remplacé. CodeSCI PR375 HEAD74d30b28c203a2fae6cbc331b61cce8b73061495, merge89c7eb2 ; closeout PR376 HEAD95e5192, merged7de8aa. CI PR code42407244113, canonique code42409455038 et PR closeout42409836099 réussies, neuf jobs chacune. CI canonique finale42411121652 completed/success, neuf jobs ; scope SCI CLOSED+CLEANED, aucune activation. Les points57ec/74d30b ci-dessous conservent l’historique de coordination, pas deux autorités interchangeables.

Sources ciblées dans ce snapshot SCI : docs/science/sci-p02-initial-policy/stage2-v3/AGENT_HANDOFF.md, DELIVERY.md, authority/registry.v1.json et producer-artifact-manifest.v1.json. Ces sources sont désormais présentes sur la base d7de8aa reçue par avance rapide ; la préparation PLAN ajoute seulement ses Markdown, sans modification SCI ni copie de payload READY dans le change PLAN.

Admission **publiée isolée** du registre : ADMITTED, binding ACTIVE ; C1–C5 ADMITTED_WITH_LIMITS et C6 EXPLORATION_POLICY_ADMITTED, runtime_availability NOT_SERVED. Revue SCI indépendante favorable après correction de la chronologie I1 ; ce verdict ne vaut ni validation humaine/clinique, ni readiness runtime PLAN. Selon le handoff/reçu SCI lus, vrai loader+producteur+validateur fournissent deux sorties positives (UNKNOWN/REQUIRES_TIME_ACK puis ack exact/ELIGIBLE) et deux négatives, artifact_kind REAL_PRODUCER_SYNTHETIC_INPUT_NOT_SERVED. Aucune reproduction de ces payloads dans la préparation, aucun compte ou réglage réel acquis.

Interfaces effectives à consommer après GO PLAN et vérification courante de l’autorité :
- tools.science_initial_policy.v3_admission.load_v3_registry(root: Path = ROOT) -> V3Registry : publication/source digests et autorité réelle ; ne pas inventer de module v3_registry.
- tools.science_initial_policy.v3_producer.produce_v3(request, registry: V3Registry) -> FirstPlanRecommendationV3 : moteur pur, sans identité de compte ou fraîcheur réseau.
- tools.science_initial_policy.v3_validation.validate_admitted_exchange_v3(request, response, registry) : invariants indépendants, recomputation stricte et retour de la recommandation recomputée. Ancien validate_exchange V3 négatif et SDK V1 préservés.

Versions stables dans les deux snapshots : first-plan-request/recommendation3.0.0 ; registry initial-policy-v3-admission-registry/1.0.0 ; engine initial-policy-producer/3.0.0 ; policy initial-hypertrophy-policy/1.0.0-limited ; binding initial-plan-v3-binding/1.0.0 ; protocole initial-observed-qualification/1.0.0 ; start_policy initial-plan-exploration/1.0.0. Le binding couvre OBSERVED_SETTING uniquement,2×7bilatéral qualifié/accepté courant ; familiarisation réellement antérieure à l’essai, pas simple ordre d’enregistrement. RIR cible subjectif, réglage provisoire, poids/taille/expérience/priorités facultatifs et inventaire globalUNKNOWN, sans bootstrap positif, tempsSUPPORTED ou reprise après préoccupation admis.

Historique des pins de coordination — la colonne74d30b correspond au contenu conservé dans la publication89c7eb2/d7de8aa :

| Identité | HEAD57ec de coordination | Snapshot local74d30b lu |
|---|---|---|
| SHA256 du manifeste d’artefacts | 2299e81252c4338be1839691ab03215e60485ca9e5d622caf1d95bae137bee21 | 160f51a6ff8d01fe3f1f7cc20b4e8163eb771326f968df9d81c497b6f045d207 |
| binding_digest | 3f8565c135b719ab2460cbc8f35d84a9da37e3a2edd740f54d6dcce54c86c148 | 9ef301da08ec3614c7e2a4fbbb95a2384f1c870bca84b6b69eeb4e20a1897389 |
| bundle_digest | 324a633e2d97f082c47b5732fede09ab21d29a52585e2a7b073cd8f245db8817 | 78b3e5d99fe05093d6141678fd40f16e744b88d3d87405f14b0f8be357724d94 |

registry_digest commun602ff0d32ebc625b4c9474660b5b36ee9983c4c598f16ae9b1269e67e5cea50f ; effective_science_digest commun10e92afb04cd1b14036f5c21e4b3f755a7ac58eddd2cb369be99a355de05b5b9. Pour les hashes de modules/exports, relire le manifeste au SHA SCI final, jamais mélanger les deux snapshots ou réécrire une référence historique. Les pins de préparation ne confèrent aucune autorité runtime ; Task1 doit vérifier ces pins canoniques et l’autorité courante avant apply ; une évolution exige son versionnement, jamais le remplacement silencieux des anciennes références.

## Brainstorming / Options / Risques / Choix retenu

1. Blueprint mobile depuis préférences : manque provenance/cohérence et autorité, rejeté.
2. Template historique après label READY : introduit dose/préparation/overload étrangers, rejeté.
3. Snapshot/décision serveur, V3 parallèle et binding vers journal canonique : proposition retenue. Coûts assumés : stockage additif, writers partagés et exécution typée. Ce choix ne prétend pas que la séance est déjà servie.

Le mandat fixe déjà V3, autorité serveur, idempotence et MISSION verrouillée. Routes, tables et détails d’exécution ci-dessous restent des choix techniques proposés à revue.

## Owned declarations and acquisition

Le serveur tire owner_id de l’auth et associe subject_ref opaque ; aucun owner/subject du body ne choisit le compte. Faits requis SCI : objectif, population adulte non clinique déclarée, cadence, budgets par séance, réponse explicite sur limitations. Expérience/priorités facultatives, jamais faiblesses analysées. Exclusions utiles conservées. Poids/taille non consommés par ce binding restent UNKNOWN/WITHHELD ; users.weight_kg ne devient pas une mesure datée.

Cadence/priorités et équipement gardent la source TrainingPreferences. Extraire un helper transactionnel validation/flush et conserver les wrappers publics historiques. Tous les writers pertinents (profil web, programme, mobile, nouveaux faits/observations) incrémentent une source_revision propriétaire sous verrou dans leur transaction. Le writer nouveau utilise If-Match et ne remplace que ses champs. Ancien client sans révision : contrat de remplacement actuel conservé, aucun CAS de brouillon promis ; l’écriture invalide les évaluations précédentes et ne touche pas les nouveaux faits hors scope.

Provenance par champ : origin/acquisition/source_ref/recorded_at/measured_at des vrais événements. updated_at global n’est pas la date d’acquisition de chaque fait. Héritage insuffisamment sourcé = UNKNOWN ou reconfirmation explicite, jamais redate par GET. UNKNOWN/WITHHELD/CONFLICT et [] déclaré restent distincts. L’assessment canonique décide des manques utiles, pas une liste mobile.

Le premier positif limité nécessite sept contextes bilatéraux exacts et sept réglages actuels observés/qualifiés/acceptés selon le binding SCI final. « Salle » ou disponibilité seule ne suffit pas. Utiliser BlueprintSourceEvent, ledger propriétaire append-only de déclarations et contextes/événements : réalisation/appareil/côté/sémantique du réglage, source/date, familiarisation/essai, qualité/gêne/acceptation/préoccupations. Serveur vérifie sujet/contexte/ordre/références, producteur juge qualification/applicabilité. Logs importés anciens ≠ acceptation présente. Acquisition non servie aujourd’hui : nouvelles commandes/UI exigent leur revue et GO. Bootstrap sans sept réglages qualifiés reste draft/revue/DENIED ; jamais fabriquer ces faits pour amorcer un positif.

Inventaire global UNKNOWN accepté lorsque réalisations nécessaires connues. NULL ne devient ni [] ni full gym ; pas de famille→objet, transfert d’appareil/côté/unité ou candidat hors binding. Confirmation actuelle = action réelle, pas date renouvelée par lecture.

## Snapshot, consent, revisions and fingerprints

Modèle minimal révisé : **sept tables**, détaillées et justifiées dans [MINIMAL_PERSISTENCE.md](MINIMAL_PERSISTENCE.md) : BlueprintSourceEvent, OwnedBlueprintSnapshot, FirstPlanEvaluation (ack enfant inclus), FirstSessionRequest (handoff CREATED inclus), FirstPlanExecutionBinding, FirstPlanSetObservation append-only et FirstPlanRuntimeAuthority. Pas de nouvelle colonne sur User ou le journal canonique ; trois indexes composites pour ownership. Cette liste remplace les dix tables initialement proposées. Stocker le minimum de faits/références/provenance utile. DATA doit admettre graphe de copies, export/fermeture/suppression et traitement des limitations/observations avant activation ; aucune durée/politique inventée ici.

Capture cohérente sous révision propriétaire : snapshot_ref, as_of UTC, source_revision, schema/profil, faits/provenance, receipt de consentement pertinent et références d’autorité immuables. L’envelope transport porte owner_id et consent_assessment (NOT_REQUIRED/SATISFIED/REQUIRED/UNAVAILABLE, purpose/ref/revision) séparément du DTO SCI inchangé. Sans consommateur corporel utilisé, aucune permission corporelle générale. REQUIRED demande l’acquisition pertinente ; UNAVAILABLE ne devient ni refus consenti ni succès.

Empreintes SCI calculées par fonctions V3 canoniques : request_fingerprint (faits), observation_fingerprint (faits+épisodes/temps), full_evaluation_fingerprint (observation+ack). plan_time_fingerprint identifie plan/temps, pas séance possédée. Digest du snapshot transport, digest du corps de commande et bundle/science/binding digests restent distincts. Canonicalisation/types stricts : pas bool=nombre, NaN ou hash maison remplaçant SCI.

Modification des faits/contexte/exclusions/consentement pertinent/version/binding/admission invalide l’applicabilité future sans réécrire snapshots/séances. Fraîcheur = même révision et événements applicables selon SCI, pas TTL chiffré inventé. Start relit autorité publiée courante/sources/révocations ; cache de succès insuffisant. Publication/retrait d’autorité serveur possède une génération verrouillable partagée avec start ; si la génération courante ne peut être établie, refus fermé. Le moteur isolé ne prouve pas une fraîcheur réseau.

## Explicit negotiation and proposed transport

Namespace proposé /api/mobile/v3, Bearer existant, no-store. Envelope first-session-runtime/3.0.0 avec first-plan-request/3.0.0, first-plan-recommendation/3.0.0, first-plan-execution/3.0.0 et profil d’autorité admis explicites. Client demande ces versions exactes et vérifie l’écho ; mismatch =>406 contract_not_supported, aucun downgrade V1. Serveur choisit l’autorité, jamais policy APPROVED ou registre arbitraire du body. Les faits évalués viennent exclusivement du snapshot propriétaire, pas d’un Blueprint opaque envoyé par téléphone.

| Route proposée sous /api/mobile/v3 | Contrat/effet |
|---|---|
| GET /me/first-plan/capabilities | Versions/disponibilité réelles ; ne prouve aucune science positive |
| GET/PUT /me/blueprint/declarations | Faits éditables/révision ; PUT If-Match et scope borné |
| POST /me/blueprint/observations | Événement réel, request_id/digest et expected source_revision ; append/rejeu exact |
| POST /me/blueprint/snapshots ; GET /me/blueprint/snapshots/{id} | Capture request_id/digest idempotente et relecture possédée |
| POST /me/first-plan/evaluations ; GET /me/first-plan/evaluations/{id} | Snapshot/pins exacts, POST idempotent, lecture résultat/pending/refus |
| POST /me/first-plan/evaluations/{id}/time-acknowledgments | Action réelle à clé durable et références/empreintes exactes, date serveur |
| POST /me/first-session-requests ; GET /me/first-session-requests/{request_id} | Commande/réconciliation définies ci-dessous |
| POST /me/first-session-requests/{request_id}/cancel | Tombstone même identité/digest avant création, sinon ALREADY_CREATED |
| GET /me/first-session-handoff | Retrouver commande/séance possédée après relance sans cache ni MISSION |
| GET /sessions/{id}/execution ; PUT /sessions/{id}/sets/{set_id} | Exécution/journal V3 typés liés au domaine canonique |
| POST /sessions/{id}/applicability | Revalidation propriétaire avant nouvelle consigne/reprise active ; aucune mutation des faits du snapshot |

401 auth ; 404 inconnu/étranger identiques ; 409 révision/idempotency mismatch/session ouverte ; 406 négociation ; 422 structure. Indisponibilité producteur/autorité explicite, timeout = inconnu transport. Échec transitoire ≠ refus métier durable irréversible. Aucun endpoint ajouté dans cette préparation.

Adaptateurs V3 nouveaux : firstPlanV3.ts, blueprintV3.ts, firstSessionV3.ts, firstUseV3.ts. firstPlan.ts, firstPlan.contract.json, fixtures/tests V1 et leur port restent octets/pins inchangés. FirstUseController V1 conserve comportement ; composition choisit V3 après négociation seulement. Conserver auth.revision/sequence/invalidation : résultat retardé après mutation/logout/changement de compte ignoré, y compris après verify/ack/start/réconciliation. Stockage durable partitionné par compte/génération.

## Science, time and real acknowledgment

Le producteur et validateur réels existent dans le build isolé SCI PR375 ; après reçu de livraison finale seulement, PLAN pourra les intégrer et appeler producteur réel puis validate_admitted_exchange_v3 contre octets/pins/registre admis courants. Schéma, réponse moteur ou fixture ne font pas autorité. Revalider owner/snapshot/révision, empreintes/versions avant exposition et avant création. Ancien validateur négatif préservé ; profil admis choisi explicitement sans bypass.

Premier périmètre SCI séparé : adulte déclaré non clinique, hypertrophie, deux séances, limitations connues vides, sept réglages exacts actuels observés/qualifiés/acceptés. PLAN ne réadmet ni dose/candidat/source ; pins finaux viennent du reçu livré, pas des versions candidates. Retrait/contexte contradictoire => refus/revue précis.

SCIENTIFICALLY_READY ≠ temps démontré ≠ séance créée. Ce binding conserve BUDGET_UNCERTAIN/UNKNOWN ; sans ack REQUIRES_TIME_ACK, ack exact et autorité applicable ELIGIBLE. Restfloor>=budget =>STRUCTURALLY_TOO_LONG/DENIED selon contrat. Budget déclaré jamais durée estimée ; UNKNOWN jamais0 ou SUPPORTED inventé.

UI expose incertitude, absence de garantie d’achever, préparation/opérations inconnues et sortie à limite/préoccupation sans comprimer les repos. Clic d’ack réel lié au snapshot/révision, empreintes faits/observations/plan+temps et start_policy exacte ; serveur date/conserve puis produit une nouvelle décision liée. Facts/observations/plan_time inchangés, full_evaluation change. Navigation/CGU/fixture ne créent aucun ack. Modification invalide l’ack ; nouveau clic seul ne valide pas des faits périmés.

## Atomic first-session command and recovery

Client persiste request_id aléatoire durable et corps avant premier envoi. Corps : snapshot_ref, evaluation_ref final, source_revision, trois empreintes V3, plan_time_fingerprint, bundle/binding/policy/engine/contract pins et selected_scientific_session_id. Ce dernier doit être la **première séance dans l’ordre du plan admis**, fixé serveur ; aucun choix local de la seconde. Pas owner/dose/exercice libre/date exécutée dans le body.

Unicité owner/request_id+digest strict : même clé/corps =>même résultat ; même clé/autre corps =>409 idempotency_mismatch. Une commande déjà finale est reconnue avant de contrôler à nouveau la fraîcheur : le rejeu de CREATED rend sa séance existante, sans redonner une permission de travail actuelle. La même règle de lookup/rejeu précède le CAS source pour captures/observations/acks idempotents déjà committés ; elle ne réexécute pas une mutation devenue périmée. Le FirstSessionRequest terminal CREATED, unique par propriétaire via index partiel, revendique ce premier handoff Blueprint (pas toutes ses séances historiques). Une seule séance peut lui être liée malgré deux évaluations/acks/clés. Après création, cette voie ne crée jamais une deuxième séance, même après fin/abandon ; replanification ultérieure hors scope. Course perdante retourne handoff possédé existant ou session_open, sans dire que sa demande a créé une autre séance.

Transaction : compte/admission propriétaire, révision sources, génération autorité, commande/handoff verrouillés dans un ordre unique documenté ; vérifier compte, négociation, sources/consentement, autorité fraîche/recomputation SCI/permission, absence de séance ouverte, représentabilité. Créer WorkoutSession+SessionExercise+SetLog+binding+handoff+résultat CREATED dans **un seul commit**. Avant commit : zéro artefact partiel ; après commit : GET retrouve le même session_id. Télémétrie hors atomicité métier.

Starts historiques mobile/web/programme, reopen et restauration doivent partager l’admission persistée propriétaire : PostgreSQL verrou de ligne, SQLite écriture/CAS et contrainte unique d’initialisation, jamais mutex mémoire ni SELECT FOR UPDATE supposé actif. Inventorier tous writers d’ouverture avant apply et tester courses croisées. Restauration sous même helper ou exclusion opérationnelle vérifiée. Plusieurs séances ouvertes préexistantes =>conflit, aucune réparation de données par migration. DATA coordonne ordre avec fermeture de compte.

Résultats durables : CREATED(session_id), DENIED(code précis), CANCELLED ; pending seulement si commande durable réelle. Panne infra non committée =>UNKNOWN client, pas DENIED inventé. GET absent ne prouve pas qu’un POST concurrent ne commettra pas : rejouer **même clé/corps**, jamais nouvelle clé pour réessayer.

Cancel avant création crée/verrouille même owner/request_id avec digest attendu, même avant arrivée du POST start ; tombstone bloque arrivée tardive. Si création gagne, cancel rend ALREADY_CREATED et même session ; abandon/pause/fin canoniques ensuite, jamais DELETE de l’histoire. Séance ouverte historique bloque avant création. Révocation après création n’efface session/séries : lectures et sortie/journal restent disponibles ; nouvelle consigne de travail dépend d’applicabilité courante. Pas de retry automatique après préoccupation ni reprise clinique admise implicitement.

**Continuation après création — choix conservateur proposé.** ELIGIBLE du moteur pur n’est ni autorité temps réel ni commande de travail. Distinguer reprise de lecture/position et reprise active : nouveau guidage ou passage vers une nouvelle série de travail exigent une assessment d’applicabilité serveur courante, absence de préoccupation bloquante et contexte encore valide. Autorité retirée/inconnue, réseau absent ou source pertinente changée =>applicability UNKNOWN/BLOCKED et aucune nouvelle consigne de travail autorisée ; lecture de prescription capturée explicitement historique, journal factuel même tardif et sortie restent possibles. Ne pas prétendre connaître une révocation offline. Aucun auto-retry après préoccupation ; nouvelle admission applicable requise hors de ce premier scope si la règle scientifique de reprise manque.

Les séries ordinaires de cette séance alimentent son journal, pas automatiquement la source_revision des faits d’entrée du snapshot. Un événement pertinent de contexte/indisponibilité/préoccupation l’invalide et bloque les nouvelles consignes ; une nouvelle acceptation n’est jamais fabriquée depuis le simple acquittement d’une série. L’API V3 rend explicitement applicability, motif/source/génération, actions autorisées et observation_only lorsque nécessaire ; nouvel endpoint de refresh propriétaire à ajouter à l’inventaire de routes, sans statut SCI ou champ canonique nouveau.

## Canonical session and native execution

Adaptateur dédié sans instantiate_session/template inventé : template_id/template_exercise_id NULL, noms factuels, slug technique réservé au profil et alias code court sans collision dans la séance. Binding conserve identité complète non tronquée : allocation/scientific session/slot/intent/canonical_exercise_id, contexte/réalisation/appareil/côté/unité, prescription/setting, sources/protocoles, versions/digests et liens se_id/set_id. Alias String(16) n’est jamais identité canonique.

Sept intentions et séries du vrai plan : pas warmup2/1, dose reconstruite, poids inconnu comblé ou exécution inventée. Préparation liée au protocole admis ; quantité/durée inconnues ne deviennent pas lignes universelles. Calibration antérieure conservée comme acquisition, pas travail de cette séance. À création tous SetLog non complétés et reps/weight_kg/completed_at nuls ; cible/réglage prescrit séparés des faits.

first-plan-execution/3.0.0 conserve session_id/se_id/set_id, statut/cursor/transitions/actions/timestamps canoniques, ajoute prescription exacte/réglage typé. TOTAL_EXTERNAL/PER_IMPLEMENT/MACHINE_DISPLAY_KG distingués et étiquetés ; jamais doublement en total. ASSISTANCE_SETTING/NON_MASS/BODYWEIGHT/unité absente acceptés seulement si mapping UI/journal explicitement couvert par binding+design ; sinon refus de représentabilité **avant création**. Premier binding bilatéral seulement.

Journal V3 écrit réglage typé/contexte dans FirstPlanSetObservation liée au SetLog canonique ; reps/complétion/date restent dans SetLog. weight_kg historique reçoit une masse seulement si réellement TOTAL_EXTERNAL ; PER_IMPLEMENT/MACHINE_DISPLAY_KG restent typés, pas promus en total. Read-model V3 relit cette source, aucun second journal métier. Bornes d’horloge et conservation completed_at lors de correction suivent domaine canonique. Identité owner/session/set/op_id+digest empêche rejeu ancien d’écraser correction récente ; correction explicite exige révision de série courante. Outbox durable et ack serveur distinguent pending/refused/unknown/acked après relance.

Transitions V3 proposées : REST_THEN_SET entre deux séries du même slot avec repos exact de dose ; SETUP_NEXT_EXERCISE entre slots avec consigne d’installation source et durée non établie ; BILAN après dernier slot. SETUP_NEXT_EXERCISE n’est ni un repos prescrit supplémentaire ni une durée0 et ne lance aucun chrono90/120/fallback. Le helper transitions() historique ne s’applique donc pas aveuglément au profil. La borne SCI750s couvre les repos entre les deux séries de chaque slot, pas une preuve de durée des transitions/setup. Le delta nécessaire au consommateur d’exécution est soumis au gate visuel.

Guidage/rest/reps/RIR proviennent du binding. Pas overload/best/previous par code historique non contextualisé, pas repos fallback différent ou cible traitée comme observé. Intent et canonical_exercise_id d’origine immuables ; remplacement éventuel ajouterait identité/contexte exécutés et autorité séparés. Premier binding : aucun remplacement hors des sept réalisations admis ; alternatives absentes restent absentes, route legacy refuse. Toute option future réutilise domaine de substitution et vérifie binding SCI, sans refaire MOB10.

Routes V1 execution/set/substitution refusent explicitement execution_profile_required pour ce nouveau profil seulement ; séances historiques/formats inchangés. Reprise V3 par handoff+GET execution puis pause/fin/abandon canoniques. Clôture et faits incomplets préservent setting/contexte/intent même après retrait ; aucun score/bilan SCI nouveau. Écritures web historiques ne doivent pas permettre de contourner ce profil.

**Dérivés — correction issue de revue fraîche.** Le profil sans template ne peut appeler compute_success_score(se,None) (défaut80), implicit_signal avec masse NULL traitée comme0, ni _persist_implicit_labels_on_completion/_record_continuity_on_completion et la planification historique comme s’ils étaient admis. Introduire un dispatch profil explicite aux frontières de log/clôture/lecture/agrégat. Conserver statut canonique, compte des séries réellement faites et timestamps ; réussite, charge totale, records/progression/implicit labels/continuité/recommandation restent NON_EVALUABLE ou omis sans compatibilité réellement démontrée. Aucun nouveau score n’est introduit. Inventorier consommateurs session_recap/stats/feedback/implicit_signal/session_completion/session_provenance/plan_adaptation/weekly_planner et lectures web/historique/export ; leurs filtres de profil doivent empêcher NULL→0 et comparaisons hors contexte. Si un consommateur ne peut préserver les faits sans inférence inapplicable, il refuse/omet l’agrégat et conserve l’accès aux faits typés, jamais activation avec un faux résultat. L’exclusion technique d’un calcul n’est pas excluded_from_stats=True ni une suppression de séance : faits/statut restent visibles. Ce lease partagé est à approuver ; aucune mutation ici.

## Visual, platform, migration and rollback

MISSION carte/composition/tokens/baselines LOCKED ; aucune sélection de carte ni fallback start ici. Navigation vers Aujourd’hui ne prouve pas réussite ; entrée exécution après CREATED vérifié seulement.

Acquisition/proposition/ack et éventuel label de réglage sont surfaces nouvelles/deltas visibles : croquis opérateur, inventaire information→source, comparaison référence, un changement par itération, rendu réel et décision humaine avant commit UI. Réutiliser primitives acceptées ; pas de baseline auto-approuvée. Exécution/reprise gardent composition LOCKED tant que delta non accepté. Aucun rendu prétendu dans cette préparation.

Sémantique serveur partagée iOS/Android ; stockage durable/relance/réseau/clavier-unités/VoiceOver-TalkBack/retour Android vérifiés respectivement. Aucune divergence fonctionnelle proposée, nécessité native à documenter/revoir.

Futures migrations additive-only sans backfill de faits/requalification/réattribution/purge. DATA intègre relations aux politiques avant activation. Ports off tant que SCI/DATA/PLAN/visuel/recettes manquent. Rollback coupe création/acquisition sans perdre lectures/reprise/sortie/journal ni réconciliation ; backend V3 reste lisible pour sessions créées. Aucun retour permissif V1 sur ces séances.

## Scope exact et revue à obtenir

Le [BUILD_SCOPE](BUILD_SCOPE.md) et le [schéma minimal](MINIMAL_PERSISTENCE.md) bornent l’apply proposé : ingénierie/migrations sur bases jetables, backend et application native contrôlée, activation par défaut coupée. Le [board consolidé de croquis](REVIEW_BOARD.md) est soumis à G1 ; les pixels réels demanderont leur acceptation ultérieure. Toutes les sources SCI pinées, y compris les fichiers app, restent read-only ; modifications dans nouveaux modules et callers non pinés.

## Decisions and dependencies before apply

Choix proposés à revue : namespace V3 parallèle, sidecar typée, handoff unique par compte et première séance seulement, admission commune des starts, refus legacy du profil SCI. Dépendances ouvertes : réévaluation de l’autorité SCI livrée et du reçu final (pins/imports/oracles, CI finale42411121652 réussie, scope SCI clôturé), contrats DATA et fermeture de compte, approbation design PLAN puis GO BUILD, acquisitions réelles, gates visuelles et recettes. Aucune case PLAN-01..07 fermée.

## Pins canoniques reçus

- engine_version : `initial-policy-producer/3.0.0`.
- policy_version : `initial-hypertrophy-policy/1.0.0-limited`.
- binding_ref : `initial-plan-v3-binding/1.0.0`.
- binding_digest : `9ef301da08ec3614c7e2a4fbbb95a2384f1c870bca84b6b69eeb4e20a1897389`.
- bundle_digest : `78b3e5d99fe05093d6141678fd40f16e744b88d3d87405f14b0f8be357724d94`.
- registry_digest : `602ff0d32ebc625b4c9474660b5b36ee9983c4c598f16ae9b1269e67e5cea50f`.
- effective_science_digest : `10e92afb04cd1b14036f5c21e4b3f755a7ac58eddd2cb369be99a355de05b5b9`.
- SHA256 manifeste d’artefacts : `160f51a6ff8d01fe3f1f7cc20b4e8163eb771326f968df9d81c497b6f045d207`.
- Fichiers clients historiquement pinés à conserver : `clients/mobile/src/api/firstPlan.ts` et `firstPlan.contract.json`. Le nouvel adaptateur est parallèle ; le packaging runtime doit conserver les sources immuables nécessaires au vrai loader.

## Révision source, identité et transaction minimales

Le compteur source est dérivé du journal sous garde propriétaire : MAX(BlueprintSourceEvent.source_revision),0si aucun événement. Le DTO SCI reçoit le token texte `blueprint-source/<entier>`, jamais un entier dans un champ Text. subject_ref est un alias serveur opaque lié au propriétaire, jamais fourni par téléphone ni username ; origine et cohérence inter-épisodes/snapshot sont vérifiées. Toute évolution d’alias invalide l’admission et conserve les anciennes références.

Garde et FK/indexes sont précisés dans MINIMAL_PERSISTENCE ; la forme SQLite no-op proposée doit prouver qu’elle ne change aucune identité/époque, et busy est retryable sans mutation métier. Pas de compteur de révision dans session_epoch ni de pseudo verrou mémoire.

## Suite canonique du8novembre — calibrage distinct du plan

[BOOTSTRAP_INTEGRATION](BOOTSTRAP_INTEGRATION.md) actualise l’autorité de rencontre, ses79sources, les deux routes supplémentaires et leurs sous-types de ledger. Il fait partie du scope soumis à revue. Les passages d7de8aa/SCI375 ci-dessus conservent la coordination historique du plan ; la base courante est b4a4242 après livraison des PR377/378. Le V3 observé et ses digests sont inchangés. Ouverture du calibrage avec zéro réglage, guidage du seul pilote et faits d’observation séparés des consignes ; pas de nouvelle qualification des six autres. Les7tables serveur/1locale restent le minimum proposé, sans table d’évaluation de rencontre supplémentaire.
