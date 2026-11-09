# Design PLAN-CAL-01 — inventaire de rencontres et projection propriétaire

**PROPOSED / NO_GO_BUILD**,9novembre2026, canonique692d4c8. Le manifeste conjoint
produit/science V1.0 est la référence déjà choisie par l'opérateur. Contrats SCI,
pilote et six admissions sont des entrées, pas de nouvelles règles à réadmettre.

## Brainstorming / Options / Risques / Choix retenu

1. Deux workers/bundles indépendants : réemploi possible, mais deux générations
   d'autorité à coordonner lors d'un snapshot/start. Complexité transactionnelle
   inutile et davantage de cas de retrait partiel.
2. Un nouvel inventaire privé v2 regroupant pilote+six+V3 : choix technique de
   l'agent soumis au GO. Une seule génération opérationnelle, mêmes tables,
   routing attesté par contexte canonique et replays v1 conservés.

Pas de modification en place des publications SCI ou des bundles v1 déjà
construits. Le builder historique et science_worker.py restent read-only.
Coût assumé : un successeur de worker/inventaire, une projection de contexte
courant explicite et les gardes de compatibilité correspondantes.

## État de départ vérifié

- scripts/build_plan_v3_runtime_bundle.py atteste un bundle format1.0.0 ;
  science_worker.py importe uniquement le pilote et les vrais V3, sans factory.
- authority.lock_authority vérifie une génération/packaging_digest et pins V3
  dans FirstPlanRuntimeAuthority. Flags test contrôlé et guidage déjà disponibles.
- calibration.py ouvre/lit/écrit des rencontres depuis BlueprintSourceEvent,
  révision source et guard_owner ; observations factuelles distinctes des actions.
- Le snapshot contient tous les épisodes bruts. Les choix/préparations manquants
  ou indisponibles créent review_source_refs ; un choix disponible mais changé
  n'est pas systématiquement confronté à la qualification courante de rencontre.
- Le V3 exige exactement un épisode applicable par exercice et un contexte de
  lieu cohérent. Un dernier événement ne constitue pas une règle de sélection.
- FirstUseV3Controller persiste une source JSON propriétaire et clés/corps avant
  mutation ; il n'a qu'un encounter_ref actif. PlanV3FirstUseScreen ne guide que
  le pilote, émet une confirmation de familiarisation sans setting et déduit le
  motif d'arrêt depuis succès/gêne/complétion. Les six exigent setting explicite
  et motif réellement rapporté. Les formes V1 scientifiques pinées sont distinctes.

## Inventaire v2, packaging inchangé de format

Nouveau builder tools/plan_calibration_runtime_bundle.py, nouveau worker
app/services/plan_v3/science_worker_v2.py. Le builder réemploie la construction
v1 dans un répertoire NEUF vide puis complète les octets/source closure des
extensions et du nouveau worker avant publication. Aucun bundle existant modifié.

Le fichier de manifeste reste packaging-manifest.v1.json, format
plan-v3-private-science-bundle/1.0.0. Son inventaire explicite est versionné
`plan-calibration-inventory/2.0.0` et lie sept profils à leurs vrais IDs,
realization_ref, policy_ref, bundle_digest, sémantiques et protocoles. Format
packaging et version de capacité sont deux axes, pas un faux rehash v1.
Absence d'inventaire = ancien profil pilote seulement ; version inconnue = refus.
Le choix du worker est une allowlist fixe par version reconnue, jamais un chemin
ou exécutable fourni par une requête. Interpréteur fixe/-I/stdin JSON/timeout
et erreurs privées restent ceux de packaging.py.

Le nouveau worker partage les opérations anciennes via le run historique
attesté (chargé depuis le fichier privé vérifié, sans démarrer l'app), et porte
uniquement les extensions d'orchestration. Pour calibration il choisit le
profil depuis le contexte du ledger serveur : pilote→vrai pilote ; six→les trois
interfaces SCI livrées. Aucune demande client ne choisit registre ou moteur.
Après imports/opérations, tous les modules tools effectivement chargés sont
vérifiés sous root/digests, y compris imports tardifs/relatifs. Les artefacts
nécessaires aux anciens loaders restent preuves privées : jamais factory ou
source des faits. Aucun import tools.science_* dans le processus app principal.

authorities conserve les champs v1 encounter/v3 pour les callers historiques
et ajoute inventory/profiles/matériaux par réalisation sous version2. Une
opération batch de rencontres peut vérifier les sept requêtes dans un processus
SCI unique avec la même publication, sans clone de règles scientifiques.

## Négociation et compatibilité de transport

Le namespace /api/mobile/v3, first-session-runtime/3.0.0 et encounter1.0.0 restent.
Nouveau header explicite X-Auren-Calibration-Inventory:
plan-calibration-inventory/2.0.0 et écho dans capacités/lectures/projections du
nouveau profil. Header absent conserve le parcours pilote historique ; inconnu,
absent côté serveur demandé v2, ou bundle seulement v1→406/refus explicite,
jamais downgrade silencieux. Les six ne reçoivent pas de guidage depuis un
consommateur qui n'a pas négocié leur inventaire.

Capacités nouvelles : profils sept avec display_name catalogue, realization,
semantics réellement supportées, politique/digest et material_ref/hash ; progression
propriétaire/selection courante séparée des capacités statiques. Aucun score ou
label JSON ne prouve qualification. Decodeurs TS vérifient owner/version/profil/
réalisation/sémantique/echo et lient la lecture à l'encounter_ref demandé.
firstPlan.ts/firstPlan.contract.json, contrats SCI et decoder scientifique V3
ne changent pas ; seules enveloppes runtime et nouveaux champs explicitement
négociés sont étendus dans ce delta partagé.

## Acquisition réelle et journal existant

Conserver les sept tables serveur et la table SQLite locale existantes. Les
nouveaux états sont des payloads versionnés du ledger et source JSON locale,
sans nouvelle colonne, migration, backfill ou réattribution. Les faits requis
par l'essai restent population/limitations applicables ; les cinq familles du
premier plan et les préférences continuent leurs consommateurs canoniques.

Ouvrir aide/choix de mouvement dès zéro réglage. Disponibilité et préoccupation
restent UNKNOWN jusqu'à déclaration explicite ; pas AVAILABLE/CLEAR depuis un
nom, un chargement ou une valeur de formulaire. Contexte/device/côté/réalisation/
sémantique sont réellement identifiés ; les aides par réalisation sont projections
traçables des procédures publiées, pas notice universelle ou garantie technique.
La source d'instructions de l'appareil et les réglages/setup réellement compris
restent faits humains référencés. Pas d'inventaire global obligatoire.

Préparation/choix/CONTEXT_CONFIRMED/familiarisation au Setting exact/essai/motif/
acceptation sont événements distincts. Le serveur attribue owner/subject/id/
sequence/recorded_at et conserve l'occurrence réelle de l'essai ; les déclarations
actuelles n'acquièrent pas une date historique arbitraire. RDL sans haltères
reste préparation sans setting, pas BODYWEIGHT/0kg/essai PER_IMPLEMENT. Les cinq
machines affichent kg appareil, RDL kg par haltère, aucune conversion en total.

Succès, complétion, qualité, gêne et motif d'arrêt sont saisies distinctes, dont
UNKNOWN/TIME_LIMIT/USER_STOPPED/CONCERN/FAILURE/COMPLETED selon compatibilité des
faits. Aucun motif causal déduit d'un booléen. Réessai explicitement demandé,
permissions SCI courantes avant toute nouvelle consigne ; pas incrément ou
acceptation automatique. Pause locale/navigation ≠ retrait du ledger.
Le retrait explicite garde la portée conservatrice propriétaire actuelle ; une
préoccupation ou un retrait ne disparaissent pas en changeant d'exercice/ID.
Lecture et faits tardifs restent séparés ; si leur validation de forme fiable
est indisponible, conserver pending/erreur explicite, jamais faux ACK.

## Sélection du contexte courant et snapshot

Pour le nouveau profil, l'ouverture explicite «utiliser ce contexte pour ma
préparation» porte une sélection dans son payload atomique. Relire un ancien
contexte ne sélectionne rien. Un événement idempotent
CALIBRATION_ENCOUNTER_SELECTED permet un changement explicite vers une rencontre
possédée déjà existante ; réutiliser la route observations. Tous passent par
request_id/digest/CAS source_revision sous garde propriétaire. Aucun «dernier
épisode gagne» implicite et aucune suppression d'anciens faits.

La sélection courante par candidat est dérivée uniquement de ces actes explicites.
Les historiques v1 sans marqueur restent conservés et compatibles : cas unique
inchangé, ambiguïté non choisie→review, pas sélection arbitraire. Un nouveau
contexte UNKNOWN/indisponible peut être sélectionné : il invalide l'ancien positif
jusqu'à ses propres preuves. L'aide seule peut précéder toute ouverture, sans
inventer un contexte/device. Réouvrir après réponse perdue reprend même clé/reçu,
une seconde demande identique de contexte propose la rencontre existante plutôt
que créer une ambiguïté cachée. Un contexte différent exige sa sélection humaine.

Avant snapshot, construire les requêtes de rencontre depuis le ledger complet,
appeler vrais evaluate/validate du profil publié et ne projeter comme applicable
qu'un épisode portable effectivement QUALIFIED pour le choix courant exact.
Un ancien CALIBRATED C3 brut ne contourne pas les gardes chargées des six.
Un choix modifié disponible mais non familiarisé/accepté ferme le positif.
Les épisodes non courants restent dans l'histoire, leurs préoccupations/retraits
et faits tardifs restent dans l'agrégat propriétaire : aucune sélection ne les
cache. Cas non qualifié/refus→review_source_refs et état précis, pas faux manque
corporel ou vieille charge. Plusieurs lieux courants contradictoires→refus/revue,
jamais reprise du lieu de la dernière ligne pour fabriquer une compatibilité.

Snapshot JSON conserve sélection/refs d'événements, inventaire/packaging/politiques,
preuves input_digest/as_of et génération opérationnelle en plus des champs SCI
inchangés. Ancien snapshot n'est pas réécrit. Nouvelles évaluations/acks/starts
vérifient ce contexte runtime exact en plus de propriétaire/révision/pins/empreintes
SCI ; un changement d'inventaire/packaging ne devient pas frais depuis les seuls
pins V3 inchangés. Même si la génération a été mal reconduite lors d'une config,
la comparaison des métadonnées capturées refuse le positif périmé.

## Reprise, V3 et séance réelle

Le ledger serveur fournit liste des rencontres, sélection et progression
courante ; aucun état local de formulaire ne devient qualification. Le contrôleur
persiste refs et pending par propriétaire, génération auth et interaction. Changer
de rencontre invalide l'affichage/actions précédents ; une réponse tardive ne
remonte pas l'ancien réglage dans le nouveau formulaire. Une demande en pending
se réconcilie sous sa même identité avant autre mutation, y compris après relance.

Avec sept épisodes effectivement applicables : même snapshot→vrai V3/validation,
BUDGET_UNCERTAIN/UNKNOWN→ack exact→commande idempotente existante→session possédée.
Conserver identité/intent/canonical_exercise et setting typé dans exécution/journal.
Réponse perdue après CREATED rend la même séance, pas nouveau start. Le rejeu
terminal précède fraîcheur sans redonner permission actuelle de travail ; lectures,
journal et sorties de séances anciennes restent disponibles après rollback.
Aucun MISSION fallback, clone de moteur, exercice/charge/READY synthétique servi.

## Contrôlé, visuel et livraison

APP_ENV=test/flags existants/default-off et comptes synthétiques/bases jetables
uniquement après GO. Les anciennes installations QA restent intactes. Preuve
native sur app/simulateur dédiés, sans prétendre accepter Android/iPhone physiques.
Rollback coupe acquisition/création/guidage mais conserve lecture/reconciliation/
facts/journal ; ne redéployer aucun ancien backend ignorant les nouveaux marqueurs
après leur création. DATA et autorité de consentement réel restent hors activation.

[BUILD_SCOPE](BUILD_SCOPE.md) fixe le lease ; [TEST_SPEC](TEST_SPEC.md) les preuves.
[UX_CAL_BOARD](UX_CAL_BOARD.md) doit recevoir G1 avant composition ; pixels natifs
réels comparés aux références avant commit UI. MISSION/exécution/journal LOCKED,
primitives/tokens existants ; pas nouvelle DA, asset, package ou baseline changée.
Un lecteur frais examine d'abord ce dossier. Après GO : plan inline, TDD, broad
selon check_scope (shared_code attendu, pas full local), revue code et frontière
SCI distinctes, CI réelle/merge gardé/canonique/closeout/cleanup sans GO routinier.

## Clarifications d’apply sous le GO reçu

Inventaire2 ne promeut aucune acquisition C3 brute en autorité de rencontre : les faits et anciens replays/bundles restent conservés, mais tout nouveau positif inventaire2 exige les rencontres effectivement qualifiées. La capture de faits reste possible avant publication opérationnelle ; elle ne confère aucune permission. Une capture lit la publication sans verrou d’écriture après le propriétaire, afin d’éviter l’ordre inverse des commandes ; les étapes evaluate/ack/start/applicability verrouillent et confrontent toujours la génération/package courants. Capture sans publication applicable = aucune preuve de qualification/permission.

Brouillons d'observation privés : conservés par encounter_ref dans source JSON existante, avec phase, réglage, faits, motif et occurrence réellement indiquée. Aucune nouvelle table. La complétion ne date jamais un essai passé à l'heure de saisie ; action présente explicitement déclarée ou date/heure locale saisie. Reprise des faits distincte du droit de nouvel essai.
