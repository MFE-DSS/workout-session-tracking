# PLAN — rencontre de calibrage et premier plan, deux autorités distinctes

8 novembre2026, canonique b4a42420afa1aca384a16bd3966ab85a97cfd724. Préparation seulement, **NO_GO_BUILD_PLAN / NOT_SERVED**. Le pilote SCI PR377 et son closeout PR378 sont intégrés, quatre CI réussies/neuf jobs chacune ; statut final dans le reçu vivant378. Aucun ancien critère PLAN acquis par cette réconciliation.

## Autorités à sélectionner explicitement

| Besoin | Entrées réelles | Publication |
|---|---|---|
| Rencontre initiale | tools.science_calibration_bootstrap.policy.load_authority ; evaluator.evaluate ; validation.validate_result ; contracts.validated_input/input_digest | first-calibration-encounter/1.0.0 ; initial-calibration-encounter/1.0.0 ; initial-calibration-encounter-registry/1.0.0 ; ADMITTED_WITH_LIMITS/NOT_SERVED |
| Premier plan | tools.science_initial_policy.v3_admission.load_v3_registry ; v3_producer.produce_v3 ; v3_validation.validate_admitted_exchange_v3 | V3 et binding1.0.0 observé inchangés ; sept réalisations bilatérales réellement qualifiées |

Bundle rencontre : **e840d5edfc2bbe150f077062227a503a6f3a996fb92a3f7e7cbe49972dee72f9**,79sources transitives. Bundle plan : **78b3e5d99fe05093d6141678fd40f16e744b88d3d87405f14b0f8be357724d94**. Ne pas confondre les digests, registres, types de sortie ou permissions. Le transport PLAN3.0.0 négocie explicitement les deux sous-contrats, sans modifier FirstPlanClientV1 ou les modèles SCI V3.

La rencontre peut être ouverte avec zéro réglage et sans cadence/budgets complets. Aide et collecte sont toujours distinguées d'une consigne physique ; celle-ci exige les déclarations personnelles datées et conditions effectivement consommées par le pilote. Poids/taille/expérience/inventaire global ne deviennent pas requis. Objectif/cadence/budgets restent nécessaires au plan, pas pour lire la première aide.

## Ledger et lectures cohérentes, sans huitième table serveur

- Réutiliser BlueprintSourceEvent et ses sous-types typés OBSERVATION : CALIBRATION_ENCOUNTER_OPENED, PREPARATION_REPORTED, SETTING_CHOICE_REPORTED, CALIBRATION_EVENT_REPORTED, ENCOUNTER_WITHDRAWN. L'ouverture ne produit aucun CalibrationEvent historique FAMILIARIZATION_STARTED, ATTEMPT_OBSERVED ou SETTING_ACCEPTED fictif.
- Ouverture à request_id/digest sous garde propriétaire/révision, encounter_ref serveur stable, subject_ref depuis auth. Données/contrat/contexte/références et retrait liés à l'owner. Même clé/corps retourne même ouverture avant CAS ; clé divergente409, réponse perdue relue sans nouvelle identité.
- Les faits réels sont soumis par POST observations existant proposé, avec référence d'encounter et preuve d'occurrence. recorded_at/source_ref serveur, measured_at réellement rapporté et borné par règles canoniques. Date de navigation/import ne devient pas occurrence de familiarisation/essai. Les confirmations personnelles/datées ne viennent ni d'un prior ni d'une valeur par défaut.
- GET reconstruit une requête de rencontre depuis ledger propriétaire exhaustif, déclarations et contexte applicables sous source_revision/as_of cohérents ; charge vraie autorité locale autorisée puis evaluate/validate_result. Le résultat est une lecture recomputable, pas une nouvelle décision FirstPlanEvaluation ou une huitième table. Les actes d'acceptation/retrait se conservent dans le ledger avec références/digest/pins de leur lecture réellement revalidée.
- Avant accepter une action autorisée, relire garde/sources/autorité et recomputer ; action INITIATE_* ne signifie pas exercice réalisé. RECORD_TRIAL enregistre un fait passé et n'autorise pas à répéter. Un fait de préoccupation enregistré reste bloquant, même sous nouveau numéro d'encounter ; parenté et ledger exhaustif choisis serveur, pas booléen auto-certifié du body.
- Tout champ/sub-type d'observation passe par schéma strict de transport proposé, pas dict arbitraire permettant propriétaire/provenance/autorité libres. Aucun durcissement ou modification d'un module SCI piné dans ce GO PLAN.

FirstPlanEvaluation reste exclusivement le résultat immuable de plan et ses enfants TIME_ACK. Une sortie de rencontre QUALIFIED ne satisfait jamais FirstSessionRequest : le serveur exige le type de décision V3, les sept épisodes exacts, le bon plan/temps/ack et toutes gardes déjà proposées. L'observation portable est transmise sans réécriture aux contrats existants.

## Deux routes supplémentaires proposées, pas servies

Sous /api/mobile/v3, auth Bearer/no-store et négociation exacte :
- POST /me/blueprint/calibration-encounters : ouverture durable à request_id/digest/expected_revision ; owner/subject choisis serveur, aucun essai inventé.
- GET /me/blueprint/calibration-encounters/{encounter_ref} : lecture possédée et évaluation courante réelle ;404inconnu/étranger identiques, défaillance d'autorité explicite, pas résultat depuis cache permissif.

POST /me/blueprint/observations acquiert les sous-types typés et faits ci-dessus. Pas d'endpoint séparé autorisant du travail ou convertissant un clic en essai. Les commandes utilisent la négociation first-calibration-encounter/1.0.0 en plus de first-session-runtime/3.0.0. Ajouter capacités/pins d'autorité rencontre dans l'enveloppe serveur, jamais contrat SCI partagé ni défaut de compatibilité silencieux.

## Pilote et autres réalisations

Seul leg-extensions-assises bilatéral reçoit les consignes du nouveau pilote, selon dispositif et instructions réellement présents/compris, choix humain et absence de préoccupation. Les six autres ne sont pas activés comme accompagnement initial par cette API. L'enregistrement de faits déjà survenus et leur qualification observée C3 applicable restent possibles, sans nouvelle consigne physique inventée. Un utilisateur déjà qualifié pour les sept réalisations peut suivre le vrai handoff de plan ; un nouvel utilisateur ayant seulement le pilote qualifié n'a pas encore un plan complet.

La preuve contrôlée A→J utilise sept épisodes synthétiques explicitement soumis par les vrais consommateurs/API de test, puis vrai producteur et vraie séance possédée. Le backend ne complète jamais six épisodes manquants en production. L'acceptation du scope contrôlé ne ferme ni entrée autonome universelle, ni DATA/RELEASE ou appareils physiques.

## Mineur SCI connu et projection honnête

Le pilote1.0.0 peut retourner state=SUPPORTED_INITIAL_EXPLORATION et phase=FAMILIARIZE si le choix courant manque malgré une observation passée. Les sources et le résultat SCI restent immuables ; PLAN ne réécrit pas ce statut et ne prétend pas corriger l'autorité historique.

L'enveloppe de lecture propriétaire fournit séparément des faits de progression : références/observations réellement présentes dans le ledger, et état de complétude de ce ledger. Une observation inconnue n'est pas zéro ; présence passée ne devient pas qualification courante. Le client ne déduit jamais «aucune observation» de la seule phase/du seul state SCI : il montre le fait disponible et la condition actuelle manquante, sans ajouter de permission à allowed_actions. Ce choix de projection est soumis avec le board G1. Si un consommateur ne peut rendre cette distinction honnêtement, montage UI du pilote bloqué et correctif SCI versionné séparé, pas édition in-place des sources1.0.0.

## Packaging et preuve privée

Le loader rencontre vérifie79sources, dont certains modules de génération et le SYNTHETIC_INPUT historique de stage2. Ils sont nécessaires comme **pièces privées d'attestation d'octets** ; les omettre casserait le vrai loader. Réviser la règle initiale trop générale «aucun SYNTHETIC_INPUT dans le bundle» : aucun accès à ces pièces depuis endpoint/app assets, aucun appel de factory/fixture sur le chemin runtime, aucune utilisation comme données ou résultat de l'utilisateur.

Le bundle hermétique conserve chemins et hashes historiques, le code effectivement exécuté et ses références transitives. La route runtime n'importe/appelle pas artifacts.py ni v3_fixtures, même si le fichier piné est présent pour être hashé. Tests en sous-processus hors checkout : vrai loader et vraies API, preuve des __file__/digests, refus si source absente/altérée ; piège sur factory synthétique/import de fixture ; aucune réponse ne contient les marqueurs de scénarios synthétiques. L'existence d'un hash de packaging ne constitue pas admission ou preuve de véracité des observations.

## Ownership de réalisation proposé après GO

Ajouter app/services/plan_v3/calibration.py et clients/mobile/src/api/calibrationV1.ts (+tests), compléter route/contrôleur/enveloppe V3 déjà proposés. Réutiliser sept tables/une locale et les gardes existantes du design ; aucun schéma SCI/SDK V1 ou source pinée modifié. DATA doit admettre finalités/copies/provenance et policy de lecture/écriture réelle ; bases de test synthétiques seulement avant ces gates.

## Digest de lecture et acte courant

Le input_digest d'un GET identifie une lecture avec son as_of ; ce n'est ni ticket d'autorisation ni reçu durable à rejouer. L'action soumise lie encounter_ref, expected_source_revision, contexte/événement visé et versions/bundle/génération d'autorité attendus. Le serveur recompose la requête avec son **as_of courant**, relit l'autorité et valide l'action sous garde dans la transaction d'append. Il conserve dans l'événement les références et le digest de cette validation serveur fraîche ; pas de comparaison naïve avec le digest d'un GET dont l'heure a changé, ni as_of arbitraire choisi par client pour ignorer des faits récents. Changement de sources/politique/génération => refus/relecture explicite. Rejeu d'une mutation déjà committée reste lookup même clé/digest avant CAS, sans nouvelle permission. Aucune table ou capacité secrète supplémentaire n'est nécessaire.
