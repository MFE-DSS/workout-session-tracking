# SCI-P02-INITIAL-POLICY-ADMISSION/1.0.0 — évaluation du système effectif

7 novembre 2026. Base `2b52f4984e375faad0a1488feef1bfe3bcab01b0`. **ASSESSMENT_AND_DESIGN_ONLY ; décision auteur proposée NOT_ADMITTED ; revue indépendante de cohérence réalisée, aucune admission positive.** Aucun registre d'admission modifié. État réellement livré inchangé : `initial-policy-producer/2.0.0`, `initial-hypertrophy-policy/0.3.0-proposed`, `NOT_ADMITTED / NOT_SERVED / READY_NOT_PRODUCED`.

## Mandat et autorité

Mandat C du dossier ARCH-PO-PACKS/1.0.0, prochain scope scientifique ; A autorise planning, sans GO BUILD général. Le GO historique du producteur isolé a déjà été consommé par sa livraison ; il n'autorise pas fonctionnellement ce nouvel enfant. CLAUDE.md et STANDING_MERGE_AUTHORIZATION.md lus sur cette base : aucune admission par GO MERGE. L'enfant [science-initial-policy-admission](../../../../openspec/changes/archive/2026-11-07-science-initial-policy-admission/proposal.md) possède seul la prochaine admission ; le parent global reste ouvert, sans double écriture.

## Brainstorming / Options / Risques / Choix retenu

Le système réel sait sélectionner, rejouer et diagnostiquer, sans disposer d'autorité temporelle positive. On peut soit construire plus tard une projection numérique v1 explicitement admise, soit versionner le contrat pour la prescription opérationnelle/qualitative v2. Modifier implicitement READY v1 est exclu. Choix proposé par l'auteur : contrat successeur explicite, collecte temporelle C6 sortie C et maintien NOT_ADMITTED. Coût : migration coordonnée SCI/PLAN ; gain : aucune fausse exactitude ou durée. Le choix reste à approuver, pas une admission obtenue.

## Audit du vrai système et rejeu

Lecture directe de `tools/science_contracts/blueprint_first_plan_v1.py`, `v2_registry.py`, `v2_producer.py`, `load_calibration.py`, `session_time.py`, `time_feasibility.py`, fixtures et références. Après `check_scope` (diff alors vide, ISOLATED/no changes), probe Python existant avec `/Users/martinfeldmann/workout-session-tracking-mob02/.venv/bin/python`. Aucun nouveau module/test, aucun writer d'artefact invoqué. Les **12 sorties générées par generated_cases() sont exactement égales au fichier piné**, avec recomputation `verify_evaluation` réelle.

| Scénario réellement rejoué | Statut SCI v1 imbriqué | Séries physiques totales | Temps par séance / limite |
|---|---|---:|---|
| novice | POLICY_UNAVAILABLE | 28 | UNKNOWN ; plancher repos 780 s, haute absente |
| returning | POLICY_UNAVAILABLE | 28 | LIKELY_FITS expérimental, 1060–1060 s |
| unknown_equipment | POLICY_UNAVAILABLE | 28 | UNKNOWN ; unilatéral sélectionné non résolu, aucun plancher total utilisable |
| limited_time | POLICY_UNAVAILABLE | 28 | LIKELY_EXCEEDS, repos seul 780 s contre budget 1 min |
| cadence_3 | POLICY_UNAVAILABLE | 42 | 3 séances UNKNOWN ; repos 780 s chacune |
| g17_unqualified | POLICY_UNAVAILABLE | 28 | UNKNOWN ; qualification manquante |
| g17_qualified | POLICY_UNAVAILABLE | 28 | LIKELY_FITS expérimental, 1060–1060 s |
| held_vertical | POLICY_UNAVAILABLE | 28 | UNKNOWN ; G17 exclu, pas de réadmission des autres pulls retenus |
| calibration_pending | POLICY_UNAVAILABLE | 28 | UNKNOWN ; calibration non achevée visible |
| missing_inputs | INSUFFICIENT_DATA | 0 | pas d'allocation/temps |
| conflicting_inputs | CONFLICTING_DATA | 0 | pas d'allocation/temps |
| conflicting_context | POLICY_UNAVAILABLE | 28 | UNKNOWN et blocage de contexte explicite |

Pour les douze : candidate_plan=null, projection quantitative NOT_COMPUTED et pas READY. Les 1060 s incluent **10 s synthétiques** par certaines composantes et une préparation globale synthétique nulle : ils ne constituent ni observation réelle ni futur individuel. La borne de repos 780 = 5×120 + 2×90, sans travail, préparation ni opérations. Aucun de ces chiffres n'est promu en constante temporelle.

Pour returning/G17 qualifié, l'allocation actuelle est : `hack-squat-machine`, `chest-press-machine`, `rowing-cable-assis-prise-neutre`, `romanian-deadlift-barre`, `tirage-poulie-haute-prise-neutre`, `elevations-laterales-halteres`, `calf-press-leg-press`. Ces sept réalisations sont bilatérales dans le bundle, deux séries chacune, 8–12 reps, 2 RIR cible ; repos 120 s pour les cinq premières, 90 s pour les deux dernières. CALIBRATED sur observations synthétiques ne signifie pas RIR réel connu.

### Binding observé

- bundle_digest : `091cdfe0758db0d96912a94a47034291624f7939bad7b9e10d177958c877c26a`.
- effective_science_digest : `10e92afb04cd1b14036f5c21e4b3f755a7ac58eddd2cb369be99a355de05b5b9`.
- catalogue effectif : `initial-plan-effective-catalogue/1.0.0@10e92afb04cd1b14036f5c21e4b3f755a7ac58eddd2cb369be99a355de05b5b9`.
- curation : `initial-candidate-curation/1.0.0` ; pull : `vertical-pull-exposure/1.0.0` ; calibration : `initial-load-calibration/1.0.0` ; temps : `initial-session-time/1.0.0`.
- approved_policy_refs et approved_restart_refs : vides. `_read_policy` refuse des références approuvées dans ce v2 ; `assert_trusted` verrouille le matériel. Impossible d'admettre par une édition documentaire ou un drapeau client.

## Décisions C1..C6 proposées pour revue indépendante

**Statut de chacune des six décisions : PROPOSED_FOR_SCIENTIFIC_REVIEW.** Ces décisions n'ont pas la signature d'une admission indépendante. Les dispositions 0.2.0 antérieures sont conservées comme base de raisonnement, pas transférées automatiquement à un binding exécutable 0.3.0.

| Gate | Décision auteur proposée | Fondement et limite / condition restante |
|---|---|---|
| C1 Population | ADMITTED_WITH_LIMITS pour le scope proposé ; non enregistré | Adulte **déclaré**, non clinique, hypertrophie, 2–3 séances ; limitations KNOWN explicitement vides. Une valeur non vide est actuellement bloquée par `_input_blocks` ; « renseigné » n'implique pas « limitation prise en charge ». Pas de supériorité physiologique du périmètre. Admettre ce scope exact et préserver la frontière clinique |
| C2 Dose | ADMITTED_AS_CONSERVATIVE_DEFAULT pour chaque convention, sous limites ; non enregistré sur le bundle | 2 séries/intention : démarrage, pas dose optimale ; 8–12 : plage pratique, pas 8–12RM ; 2 RIR : cible comportementale, pas mesure ; repos 120/90 : défauts pouvant devoir être allongés, jamais compressés ; cadence 2/3 : restriction produit, 28/42 séries physiques hebdomadaires et contributions chevauchées. Ne pas conclure que 14 séries/séance sont individuellement conservatrices. Revue du bundle complet restant requise |
| C3 Protocole initial | NOT_ADMITTED pour le protocole exécutable complet | Réemploi comparable/contextuel et réglage provisoire défendables ; manque un bootstrap opérationnel admis et temporalisé. Ancien historique seul mal étiqueté « en cours » à corriger avant admission. Préoccupation/échec bloquent ; reprise non admise. RIR absent ne devient ni 2 observé ni nouvelle exigence universelle. Voir ci-dessous et TEST_SPEC |
| C4 Sélection/réalisation | ADMITTED_WITH_LIMITS **proposé pour les sept réalisations qualifiées** ; binding effectif encore NOT_ADMITTED | Curation + overlay G17 exact + `match_distinct`, disponibilité courante, réalisation/appareil/côté, exclusions et UNKNOWN. Le tri contexte puis ID est reproductibilité opérationnelle, pas rang biologique. Pas d'inventaire imposé. Qualification G17 directe requise ; aucune fraction d'hypertrophie. Unilatéral non appairé reste bloqué. Les quatre autres pulls retenus ne sont pas requis pour un plan qui ne les choisit pas |
| C5 Projection / READY | NOT_ADMITTED en l'état ; contrat successeur proposé | Draft réel sans crédit/exposition calculé, prescription PROPOSED_NOT_EXECUTABLE, `execution_ready=false`. v1 exige 15 EXACT, allocation REVIEWED, faisabilité CONFIRMED, durée ESTIMATED admise et prescription complète. Le sens qualitatif/opérationnel v2 n'est pas cette sortie. Revue explicite contrat/consumers avant apply ; aucune relaxation v1 |
| C6 Temps positif | NOT_ADMITTED ; sortie **C : preuve insuffisante, protocole défini** | Composantes/rejeu/union et réfutation structurelle existent, aucun modèle prévisionnel ou convention produit bornée actuellement admis. LIKELY_FITS expérimental laisse Duration UNKNOWN par construction. [TIME_PROTOCOL](TIME_PROTOCOL.md) définit la preuve à produire ; choix ultérieur A modèle/B convention requiert décision explicite et bases applicables |

**Verdict du système effectif : NOT_ADMITTED, pas ADMITTED_INITIAL_POLICY.** Les éléments partiellement défendables ne fournissent pas un binding admis. Bloqueurs concrets : bootstrap exécutable admis/temporalisé et sémantique historique C3 ; admission effective de sélection C4 ; projection/contrat et intégrité C5 ; base temporelle positive applicable C6. C6 est le verrou de preuve principal ; grand budget, charge connue ou simple label de modèle ne le lèvent pas.

## C3 : protocole candidat à faire admettre, sans kg froid

1. Confirmer exercice/appareil/réalisation/côté et réglage réellement disponible ; aucune conversion pile/assistance/poids corporel en charge effective ni transfert d'exercice.
2. Familiarisation courante confirmée avant acceptation d'une tentative. Définir l'instruction pratique et le responsable de sa validation ; aucune durée, rampe ou nombre universel d'essais n'est inventé ici.
3. Première tentative sourcée, réglage choisi effectivement par la personne/protocole autorisé, reps et complétude/succès/technique/gêne renseignés. 8–12 et cible subjective 2 RIR restent instructions distinctes de l'effort observé.
4. Une acceptation explicite cite la tentative et le réglage actuellement confirmé. Un essai non qualifié n'est pas un résultat positif ; un réessai est un nouvel événement, aucune correction automatique de kg.
5. En cas de préoccupation/échec : arrêter les suggestions automatiques, conserver les faits et demander la revue prévue ; aucun redémarrage autorisé par le registre actuel. Pas de qualification clinique implicite.
6. États : NEEDS_CALIBRATION sans activité courante qualifiante, CALIBRATION_IN_PROGRESS pour épisode courant, CALIBRATED pour réglage observé accepté seulement, INSUFFICIENT_DATA/UNAVAILABLE selon contexte. UNKNOWN d'effort persiste même lorsque le réglage est accepté. Tout temps de cette séquence doit être couvert par C6 avant READY de bootstrap.

Ce protocole est un **design opérationnel proposé**, pas une procédure scientifique déjà validée ni une consigne clinique. La précision d'instruction de première tentative et le traitement d'une difficulté réelle doivent être relus avant GO/build ; une formule corporelle ne les remplace pas.

## C5 : incompatibilité précise et chemins licites

`REQUIRED_FIELDS` = objective/population_scope/sessions_per_week/session_budgets_minutes/limitations. Anthropométrie et expérience restent facultatives ; priorité n'est pas diagnostic. L'évaluation réelle respecte l'ordre conflit → manque → politique indisponible. Les statuts du futur runtime PLAN ne sont pas les enums SCI v1 et requièrent mapping explicite.

`Plan.accounting` exige les quinze zones EXACT si exposure_complete ; `_validate_ready_plan` exige ce flag, REVIEWED, cadence exacte, faisabilité CONFIRMED, durée ESTIMATED référencée/haute≤budget et prescription tracée avec RIR/repos et load_mode≠NOT_DEFINED. Le réglage non massique v2 peut être correctement observé sans représentation v1 ; le draft utilise aussi source_kind PROPOSED_NOT_EXECUTABLE, hors enum Prescription v1. Une simple copie dans candidate_plan échouerait donc à plusieurs niveaux.

Ce constat **ne démontre pas que v1 impose une certitude biologique** : ses crédits peuvent être des conventions exactes de comptabilité. Un futur producteur pourrait explicitement les admettre/calculer sans renommer la croissance mesurée ; ce travail n'existe pas dans v2 actuel. Option proposée : [contrat successeur](../../../../openspec/changes/archive/2026-11-07-science-initial-policy-admission/design.md), quinze déclarations avec inconnus honnêtes, prescription de bootstrap/réglage typée et gates d'exécution conservées. Aucun READY ne sera projeté de force sous v1. Aucune exposition nouvelle, coefficient G17 ou hypothèse de durée n'est appliquée ici.

## Mineurs affectant directement l'admission — racines vérifiées

| Constat réel | Cause | Design de correction / stop |
|---|---|---|
| Épisode commencé à 11:10, events acceptés 11:01–11:04 seuls → CALIBRATION_IN_PROGRESS | `started` inspecte tous les events ATTEMPT_OBSERVED/FAMILIARIZATION_STARTED, pas le sous-ensemble courant | Qualifier l'activité courante ; ancien historique seul → NEEDS_CALIBRATION. Garder les concerns et garde de reprise. C3 exige correction avant admission |
| `draft.executable: false` remplacé par `0` passe `verify_evaluation` | Égalité Python bool/nombre ; le vérificateur renvoie toutefois la décision recalculée `False` | Comparaison canonique stricte sur types, test avant adaptateur de confiance. Aucune exploitation servie revendiquée |
| Borne basse d'une composante ignorée si sa haute manque ; retour au plancher repos | Toute erreur COMPONENT_BOUND_UNKNOWN empêche `_total` | Séparer agrégation basse sûre/haute complète. Conserver UNKNOWN de Duration ; pas bloquant positif « résolu » par ce durcissement |

Les corrections sont spécifiées, **aucune n'est appliquée**. Aucun retour favorable ne transforme l'état général en admis.

## Preuves existantes réutilisées, pas nouvelle revue musculaire

Réemploi borné de [admission-01/policy.json](../admission-01/policy.json), [curation/EVIDENCE](../curation-01/EVIDENCE.md), [pull/SCIENTIFIC_REVIEW](../pull-exposure-01/SCIENTIFIC_REVIEW.md), [calibration/EVIDENCE](../calibration-time-01/EVIDENCE.md). Les articles primaires et limites y sont référencés. Cette passe audite la cohérence du bundle ; elle ne revendique aucune nouvelle recherche bibliographique ni nouvelle validation empirique. EV-04/11 bornent le scope, EV-01/04/10 et EV-80 les conventions de dose sous limites, EV-14/15/16 l'effort, EV-54/55 le repos ; EV-40/42/44 ne donnent pas une correction personnelle universelle de RIR. EV-70/71 et G17 restent qualitatifs/contextuels. Les études temporelles du dossier antérieur ne fournissent pas de borne AUREN applicable à une première séance autonome. Aucune promotion E0.

## Pins de cette lecture

SHA256, calculés sur la base ci-dessus ; leur rôle est l'audit de cette préparation, pas un nouveau registre exécutable.

| Fichier | SHA256 |
|---|---|
| tools/science_initial_policy/v2_producer.py | ad8c154feb8b439a25d7b39b37defcf236d6b4f847a058f64d9c1976df70fd02 |
| tools/science_initial_policy/v2_registry.py | 5f9d17f531f28cda18595d0aace9fc8b91340e931bc77d4dedac170cc05ac59b |
| tools/science_initial_policy/load_calibration.py | f75b03d0a81691a5e2bab94c5bf22cfc8e01e40745f297a0ae9e9bbca6a41b7c |
| tools/science_initial_policy/session_time.py | 4ff7ad6ccf11fb64dea10aaee76a96bc732ce124f493e3d844d691b776490564 |
| tools/science_contracts/blueprint_first_plan_v1.py | 0f467360aaf829c437144486e15610b402a3a54d1ec2544330ce0cfd96fc1bfa |
| calibration-time-01/policy.v1.json | 08a4834113b01f1417a9f45a5c7195c9d6c24c4dd8d1dd72d982b0c51aa73462 |
| calibration-time-01/producer-fixtures.json | faa684a328c2017030ded27c965bbf81d31bf953a4f304c4a03a55ffd6357a1b |

## Vérification et limites de cette passe

Rejeu/probes existants réalisés, aucune suite fonctionnelle nouvelle ni preuve appareil/runtime/CI revendiquée. `RTK.md` demandé par le contrat de session est absent du worktree et du repo racine consulté ; aucune règle de ce fichier supposée. Après écriture des huit fichiers du paquet : `check_scope` DOCS (diff partagé alors de 14 fichiers), `check_spec_protocol` passant, `openspec validate science-initial-policy-admission --strict` valide ; vérification des liens locaux des huit fichiers, aucune cible absente. Aucun sweep produit requis par ce tier documentaire. Le coordinateur revérifie son diff final et consigne les revues indépendantes encore en attente. [TEST_SPEC](TEST_SPEC.md) décrit des cas futurs, pas un nombre de tests passants. Aucun commit/staging/push/checkout par l'auteur de ce paquet.

## Revue finale de cette préparation

La revue scientifique fraîche a recoupé les sources/validateurs et confirmé la cohérence de NOT_ADMITTED, sans Critical/Important, sans admission positive ni preuve temporelle nouvelle. La revue builder a été réalisée séparément ; ses trois points inter-scopes PLAN/F sont précisés et relus sans Important résiduel. Voir [reçu coordinateur](DELIVERY.md). Les gates positives, le contrat choisi et le build restent à autoriser ; aucune policy/fixture exécutables modifiées.
