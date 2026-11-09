# Design proposé — extension isolée des rencontres, échange V1 conservé

> Actualisation9novembre : design et GO BUILD reçus ; voir [autorisation](BUILD_AUTHORIZATION.md) et [livraison effective](../../../docs/science/sci-p02-initial-policy/calibration-six-extensions/DELIVERY.md). Les mentions préparatoires ci-dessous conservent leur instant d’origine.

**PROPOSED / NO_GO_BUILD**, 9 novembre 2026, base ba2dbbc. Sources nécessaires :
spécification science/first-use-calibration, autorité du pilote1.0.0, contrats
EncounterRequest/Result, CalibrationEpisode/Setting, registry V3 limité et
producteur/validateur V3, curation et overlay G17. Le manifeste produit/science
canonique conjoint reste la référence déjà acceptée. PLAN #379/#380 est clos
pour son scope contrôlé ; ses fixtures ne deviennent pas preuve personnelle.

## Brainstorming / Options / Risques / Choix retenu

1. Une extension par exercice : scope très court, mais six cycles de publication
   et aucun dossier global de progression disponible au reviewer.
2. Six procédures dans un scope isolé, admissions séparées par réalisation :
   choix proposé par l'agent. Une seule frontière d'intégration, verdict explicite
   pour chaque contexte. Coût : revue plus large et aucune fin positive si l'une
   ne peut être défendue sans une décision supplémentaire.
3. Élargir le pilote ou son ID par substitution : rejeté. Le noyau a un PILOT
   fixe et ses octets sont pinés ; cela falsifierait son autorité historique.

Le « continue » délègue la préparation technique ; le choix2 reste soumis avec
ce design au GO scientifique explicite. Un lecteur frais vérifie ce dossier
avant présentation. Aucun code fonctionnel ou plan d'implémentation avant ce GO.

## Contrats et autorités

EncounterRequest/Result1.0.0 portent déjà contexte, préparation, choix de réglage,
provenances, épisodes, arrêt/retrait, références/empreintes et actions distinctes.
Aucune incompatibilité de forme identifiée. Pas de changement V1/V2/V3, SDK ou
anciens schémas/fixtures/manifestes/validateurs. Le premier pilote reste leg seul.

Nouvelle namespace proposée `tools/science_calibration_extension/` :
policy.py (loader strict), evaluator.py (orchestration par profil), validation.py
(recomputation stricte + contrôle C3 et familiarisation chargée), artifacts.py (exports synthétiques non
servis). Versions proposées : politique `initial-calibration-extension/1.0.0`,
registre `initial-calibration-extension-registry/1.0.0`, moteur
`calibration-extension-evaluator/1.0.0`, échange encounter1.0.0 inchangé.

Chaque entrée lie candidate_id, intent_id, realization_ref exact, sémantique
admise, protocole, conditions, décision/reviewer/version et retrait. Aucun label
ADMITTED, hash ou dictionnaire fourni par le caller ne crée l'autorité. La
publication de développement reste non admise jusqu'à revue SCI du bundle
réel. Loader vérifie octets, source closure exacte et parent V3 réel ; inventaire
transitif généré, pas un compte de sources deviné. Retrait/incohérence ferme
les consignes, jamais fallback sur un preview.

Réemploi en lecture seule : modèles/strict_record, C3 calibrate_for_admission,
helpers purs _current/_concerns/_familiar/_qualified du noyau historique, avec
leurs invariants/limites. Ne pas appeler compile_candidate/evaluate historiques
pour une autre identité, ne pas monkeypatcher PILOT et ne pas copier tout le
moteur. La nouvelle orchestration porte seulement sélection de profil, portes
spécifiques et états/actions de rencontre. Revue vérifie les appels privés et
source pins ; toute incompatibilité démontrée revient à la gouvernance avant
modification historique. Ne pas réparer les mineurs historiques hors scope.

## Population, contexte et réglages

Aide/collecte dès zéro épisode. Action physique conditionnelle : adulte déclaré
non clinique, limitations explicitement vides, ledger propriétaire complet sans
préoccupation non résolue, disponibilité/contexte/instructions réellement acquis
et compris, contrôle actuel déclaré. Cette déclaration n'est pas une mesure de
technique, un diagnostic ou une garantie de sûreté. L'aide humaine n'est jamais
présumée disponible ; demander aide/revue ou sortir si les conditions manquent.

Les six IDs/ref viennent uniquement de la sélection V3 publiée (voir cas
scientifique). Cinq profils à affichage machine kg identifié, sans supposer stack
ou couple de poulies ; RDL bilatéral : kg par haltère explicitement identifiés.
Les autres sémantiques reconnues historiquement ne sont pas supprimées du V3,
mais ne reçoivent pas ce premier accompagnement limité. Aucun setting0, cran
minimal, pourcentage, transfert entre appareils/côtés/réalisations ou total
calculé. Inventaire global UNKNOWN accepté ; aucun formulaire d'inventaire.

## Deux temps de familiarisation, aucune charge calculée

Avant choix réel : aide, identification/manipulation/installation et compréhension
selon le contexte. Pas de répétition contre une résistance inconnue. Pour le
RDL, répétition du geste sans haltères est une préparation facultative distincte
si les instructions et le contrôle le permettent : jamais ATTEMPT_OBSERVED,
réglage BODYWEIGHT ou masse0 dans le contexte PER_IMPLEMENT, jamais qualification
ou série de travail. Sinon rester à aide/assistance/pause.

Après choix humain d'un réglage réellement disponible : nouvelle confirmation
courante du contexte, puis familiarisation réellement applicable à CE réglage.
Pour ces six extensions, INITIATE_TRIAL, offre ACCEPT_EXACT_SETTING et QUALIFIED
exigent un FAMILIARIZATION_CONFIRMED explicite au réglage choisi, après choix,
préparation et confirmation de contexte, avant l'essai. Un booléen isolé sur
l'essai ou une ancienne familiarisation sans setting ne suffit pas. Un changement
de choix/contexte/setup referme cette porte jusqu'aux faits applicables. Le
validateur recontrôle également cette porte, même si le diagnostic C3 ancien
retourne CALIBRATED. Dates compatibles et ordre explicite suffisent, sans imposer
un délai en secondes ou prétendre que deux timestamps égaux prouvent durée0.

Aucun nombre d'essais, repos ou durée universel. L'essai réel vise la fenêtre
C3 existante8–12, sans devoir y parvenir ni aller à l'échec. Effort/RIR inconnu
permis, subjective2RIR jamais mesurée. Relever faits exacts ; arrêt volontaire
sans préoccupation reste observation non qualifiée. False/CONCERN/UNKNOWN de
qualité/gêne/cause ne se transforme pas en null pour continuer. Pas de reprise
après préoccupation admise, même sous un ID neuf ; retrait préserve faits.

Dernier essai comparable complet/réussi, qualité/gêne effectivement rapportées,
chronologie réelle et acceptation exacte → réglage provisoire qualifié. Aucune
optimalité, exposition, score ou entraînement accompli n'en découle.

## Preuve positive et handoff PLAN

Construire des entrées synthétiques suffisamment spécifiées et étiquetées,
sans kg moteur ou faux faits personnels. Appeler les vrais évaluateurs/validateurs
publiés, obtenir six épisodes portables qualifiés ; ajouter celui du vrai pilote
historique. Alimenter le vrai FirstPlanRequestV3 et produire/valider la décision
avec loader V3 réel, puis ack exact et nouvelle décision. Ni enveloppe READY
construite à la main, ni allègement du binding sept épisodes.

Science prête, temps UNKNOWN/BUDGET_UNCERTAIN, ack requis/ELIGIBLE et création
de séance restent des étapes séparées. L'isolé ne crée aucune séance ni identité
de compte. Les exemples n'ont jamais d'autorité de production.

PLAN livré consomme encore l'autorité de pilote ancienne dans son worker piné.
Aucun import/route/UI/SDK/capability ni packaging app modifié ici. Handoff donne
profils/pins/source closure et refus ; le futur delta PLAN choisira explicitement
l'autorité supportée, conservera les replays et assurera auth/source revision,
ledger exhaustif, consentements, idempotence, réponse perdue et acquisition réelle.
Un JSON pur ne prouve ni contrôle humain ni présence réelle d'un appareil.

## Fichiers possédés, tests et livraison future

Lease après GO : nouveaux tools/science_calibration_extension/* ;
tests/test_science_calibration_six_extensions.py ; nouveaux docs scientifiques
calibration-six-extensions/* et exports propres ; présent change ; append seul
SPEC_REGISTRY. Anciens modules/contrats/registres/manifestes/payloads pinés read-only.
Aucun app/mobile/API/migration/CI/asset/baseline. Tests spécifiés dans TEST_SPEC.

Après approbation : plan inline/TDD, tests ciblés et broad selon check_scope,
revues SCI et code fraîches distinctes, correctifs avec régressions, vraie CI du
HEAD, merge sous GO permanent, canonique/closeout/cleanup vérifiés. Déploiement
séparé ; six admissions non défendables = arrêt précis, aucune acceptation
partielle renommée complète ou nouvelle PR chevauchante.
