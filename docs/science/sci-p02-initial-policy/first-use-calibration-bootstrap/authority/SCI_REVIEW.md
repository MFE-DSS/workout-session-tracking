# Revue SCI effective — premier calibrage limité

8 novembre 2026. Reviewer agentique indépendant du builder : `/root/bootstrap_first_use_science_review`. Aucun titre professionnel humain ni certification clinique revendiqué. Lecture seule du dépôt ; seuls ce rapport et son fichier d'empreintes sont écrits hors dépôt.

Worktree examiné : `/private/tmp/auren-sci-first-use-calibration-bootstrap`. Base annoncée `d7de8aa`; HEAD lu `8187396c19493a3139d0f869d4c7b1b8d7276b1e`, avec fichiers candidats non commités. Les empreintes des fichiers pertinents lus sont dans `reviewed-hashes.json`. Le builder peut poursuivre en parallèle ; ces empreintes bornent le présent avis. CLAUDE.md et STANDING_MERGE_AUTHORIZATION.md lus. GO opérateur effectif consigné dans BUILD_AUTHORIZATION.md : « Valider le pilote et son build isolé ». Ce GO ne constitue pas une admission SCI.

## Décision

**Avis final après relecture ciblée : I1 et M1 sont clos ; la publication isolée du protocole et du bundle corrigé est défendable comme convention opérationnelle limitée. Admission `ADMITTED_WITH_LIMITS` recommandée pour le seul pilote leg-extensions-assises bilatéral, sous les limites de ce rapport et la clôture normale des sources/autorité.** Les constats initiaux sont conservés ci-dessous comme historique résolu ; aucun Important ni Critical SCI ouvert à l’issue de cette relecture. Aucun nouvel essai clinique, grand survey anatomique, kg initial, rampe de charge ou FirstPlan V4 n’est requis. Cet avis est une admissibilité de convention, pas une validation humaine réelle, clinique ou runtime.

Cette conclusion porte sur une convention d'acquisition d'observations. Elle ne valide ni efficacité individuelle, ni sécurité médicale, ni capacité du novice à choisir seul sa première charge, ni précision RIR, ni disponibilité réelle d'instructions/assistance. Schémas, tests, GO et hash ne sont aucune de ces preuves. Aucune activation/runtime, recette humaine ou collecte de données personnelles n'a eu lieu dans cette revue.

## Findings

### Critical

Aucun identifié dans ce périmètre. Le preview conserve `DRAFT_EVALUATION_SYNTHETIC_NOT_AUTHORITY` et `NOT_ADMITTED` ; l'entrée publique sans autorité ne donne ni INITIATE_TRIAL ni qualification. I1 est un défaut préadmission, pas une affirmation d'exposition réelle actuelle.

### Important I1 — préparation postérieure à l'essai promue en préparation applicable à sa qualification — RÉSOLU

Références : `tools/science_calibration_bootstrap/evaluator.py:163` (préparation seulement courante depuis le début), `:115` (conditions de qualification sans lien temporel avec préparation), `contracts.py:48` (Preparation liée au contexte mais pas à l'essai), `OPERATIONAL_PROTOCOL.md:9`, `:14`, `:23` (installation/instructions comprises, familiarisation préalable, essai comparable).

Cas reproduit sans modifier le repo : partir de `tests.science_bootstrap_samples.encounter()`, garder l'essai mesuré à 11:03, puis fournir une préparation nouvelle, explicitement acquise à 11:04, avec `setup_ref='synthetic:NEW-seat-axis-pad-after-trial'` et `provenance.measured_at=recorded_at='2026-11-07T11:04:00Z'`. `compile_candidate` retourne encore **QUALIFIED**. Insérer son portable_episode dans le vrai plan synthétique à sept épisodes fait retourner **SCIENTIFICALLY_READY** au vrai `produce_v3`.

Effet : un réglage essayé avant la préparation actuellement déclarée peut être qualifié comme si cette préparation lui était applicable. Le même appareil/réalisation/côté/unité ne prouve pas que l'installation siège/axe/coussin ou les instructions comprises après essai étaient déjà applicables. La confirmation de familiarisation générique à 11:02 ne règle pas la contradiction explicite d'une préparation nouvellement acquise à 11:04. Le V3 historique ne possède pas cette nouvelle préparation ; sa réussite ne peut détecter ni résoudre cette incohérence de la rencontre.

Correction minimale attendue : définir et imposer la relation de préparation applicable à l'essai (temps réel d'acquisition, avec enregistrement tardif distingué de préparation tardive ; identité/référence d'installation applicable). Refuser QUALIFIED et l'offre d'acceptation lorsque la seule préparation disponible est postérieure ou correspond à une installation changée non réessayée. Préserver l'observation passée ; permettre un nouvel essai non préoccupant selon décision humaine et préparation effective. Ne pas réécrire les anciens contrats/helpers. Vérifier au minimum : préparation antérieure valide, saisie tardive d'une préparation réellement antérieure, préparation réellement postérieure refusée, préparation modifiée puis nouvel essai qualifiant valide. Une ancienne familiarisation générique ne doit pas suffire à effacer la contradiction.

Reproduction exacte utilisée :

```python
from tests.science_bootstrap_samples import encounter, plan_input
from tools.science_calibration_bootstrap.evaluator import compile_candidate
from tools.science_initial_policy.v3_admission import load_v3_registry
from tools.science_initial_policy.v3_producer import produce_v3
raw = encounter()
raw['preparation']['setup_ref'] = 'synthetic:NEW-seat-axis-pad-after-trial'
raw['preparation']['provenance'] = dict(
    raw['preparation']['provenance'],
    measured_at='2026-11-07T11:04:00Z',
    recorded_at='2026-11-07T11:04:00Z',
)
out = compile_candidate(raw)
print(out.state)  # QUALIFIED
plan = plan_input()
plan['episodes'][0] = out.portable_episode.model_dump(mode='json')
print(produce_v3(plan, load_v3_registry()).scientific_readiness)
# SCIENTIFICALLY_READY
```

### Minor M1 — acceptation proposée sans les préconditions complètes de qualification — RÉSOLU

`evaluator.py:243` promet de n'offrir ACCEPT_EXACT_SETTING que si l'épisode qualifie après acceptation réelle. Pourtant `encounter(stage='observed')`, avec le seul CONTEXT_CONFIRMED retiré (`events = events[1:]`), offre encore cette action. La qualification finale reste refusée : ce n'est pas une promotion de charge positive, mais une invitation incohérente dans la procédure. Réutiliser une garde commune d'éligibilité d'essai, sans créer d'événement fictif, éviterait cette divergence. Inclure I1 dans la même garde.

### Minor M2 — statut documentaire de préparation

proposal/design/ADMISSION_CASE/CONTRACT_AND_PLAN/TEST_SPEC contiennent encore des mentions préparation, NO_GO_BUILD ou absence de tests. BUILD_AUTHORIZATION consigne correctement le GO reçu. Au closeout/publication, identifier sans ambiguïté l'état final, les empreintes, la revue et les limites, tout en conservant les décisions historiques. Aucun changement de doctrine n'est nécessaire.

## Appréciation scientifique et frontières

| Sujet | Appréciation |
|---|---|
| Zéro historique | Ouverture de l'aide et collecte distinctes de la permission d'essai. Aucun poids/taille/sexe ou sept réglages requis pour ouvrir. Cela est cohérent : l'absence d'historique n'est pas l'absence de possibilité de collecte. |
| Population | Adulte déclaré non clinique, limitations connues vides, conditions réelles nécessaires à l'action physique. Déclarations sans valeur d'examen médical. |
| Curation | Le vrai loader V3 retrouve `leg-extensions-assises`, bilatéral, `ADMITTED_WITH_CONTEXT_CONFIRMATION`, réalisation `initial-candidate-realisation/1.0.0@c05c6596f8f5578bad0b322db8644ebd8f37e319e733d8099a1f4ea18934bdda`. La curation soutient une réalisation et des rôles qualitatifs ; elle ne prouve pas aptitude autonome universelle, notice concrète, premier réglage ou sécurité. Aucun nouveau survey anatomique utile à ce delta. |
| Instructions/setup | Notice/aide spécifique réellement obtenue et comprise, siège/axe/coussin/manipulation maîtrisés : conditions légitimes. L'app ne remplace pas une notice. Référence opaque et checkbox ne les authentifient pas. I1 doit préserver leur application avant l'essai concerné. |
| Réglages/ordre | Choix humain réellement disponible, sémantique explicite ; machine kg n'est pas masse externe totale, assistance/PER_IMPLEMENT exclus du pilote. Aucune direction, incrément, minimum ou pourcentage calculé. Pas besoin d'inventer un ordre de difficulté entre dispositifs : aucun algorithme n'en consomme. Un éventuel changement humain reste contextuel et doit être confirmé. |
| Fenêtre/effort | 8–12 est une convention de qualification C3 héritée, pas une dose universelle de familiarisation ou un optimum. RIR peut rester inconnu ; réussite n'est pas vraie mesure de 2RIR. Ni échec imposé, ni ajout de préparation chiffrée ou temps universel. |
| Arrêt volontaire | USER_STOPPED/TIME_LIMIT avec completed=False, successful=null, qualité acceptable et absence de gêne explicites reste observation non qualifiée ; demande humaine explicite avant nouvel essai. Un null ne transforme pas un échec connu. |
| Préoccupation | False/FAILURE/CONCERN, qualité/gêne inconnues et cause UNKNOWN ferment le nouvel essai. Toute préoccupation de l'épisode est conservée ; aucun mécanisme de reprise après concern admis. |
| Ledger/prédécesseurs | ledger_complete/source et predecessor_blocked ferment les cas déclarés incomplets/bloqués. Le moteur ne peut savoir qu'un client omet un prédécesseur ou ment sur CLEAR. Ledger propriétaire exhaustif, identité, révisions, retrait et relecture sont des obligations PLAN/DATA avant runtime ; pas des vérités produites par le contrat. |
| Portabilité V3 | Le helper courant, les conditions préalables contexte/réglage/familiarisation/acceptation et le test vers le vrai producteur sont appropriés. Un épisode seul ne produit pas le plan à sept. Le bridge positif synthétique démontre une compatibilité technique, pas acquisition réelle ni preuve biologique ; I1 illustre précisément sa limite. |
| Six autres réalisations | Chest press, rowing avec appui, RDL haltères, tirage haut neutre, élévations latérales machine et mollets machine conservent leur qualification observée historique. Elles ne reçoivent pas ces permissions de première rencontre. Instructions/manipulation/sémantique doivent faire l'objet de leur admission applicable. |
| Travail/temps | CALIBRATION_ACTIVITY n'est pas SetLog, volume de travail, crédit d'exposition ou séance. Durée inconnue conservée ; vrai plan et ack temps exact restent séparés. |

## Sources ciblées et limites de lecture

- [Wiedenmann et al. 2026, étude primaire](https://link.springer.com/article/10.1186/s13102-026-01997-y), texte éditeur lu : 26 adultes ayant une expérience préalable du travail en résistance, bench press/leg press, séances supervisées, estimation puis poursuite à l'échec. Ce protocole ne démontre ni estimation exacte chez un novice sans historique, ni transferabilité au premier leg extension, ni nécessité d'imposer l'échec ici. Il conforte le maintien d'une incertitude sur le RIR ; aucune dose de son protocole n'est importée.
- [Steele et al. 2022](https://link.springer.com/article/10.1007/s40279-022-01717-9), résumé éditeur et notes lus : revue exploratoire, pas étude primaire individuelle de ce pilote. Ses moyennes de sélection ne sont pas une charge personnelle, et les auteurs signalent des limites d'implémentation. Aucun ratio n'est repris dans la procédure.
- [ACSM 2026, DOI référencé](https://doi.org/10.1249/MSS.0000000000003897) : récupération directe échouée dans cette revue (redirection Ovid inaccessible). Le dossier déclare une consultation antérieure. Je ne revendique pas une nouvelle lecture ni une validation du pilote tirée de ce texte ; le verdict ne dépend pas d'un résultat particulier inaccessible.
- C3 historique `stage2-v3/authority/PROTOCOL.md`, revue effective SCI historique, producteurs/validateurs V3, contrats de calibration, curation EVIDENCE/REPORT et candidat réellement chargé lus. Leurs limites restent applicables. Aucun champ de rôle musculaire ne constitue une preuve de charge initiale ou de sûreté.

## Vérifications réellement effectuées et suite

`python` n'étant pas dans le PATH, `scripts/check_scope.py` a été exécuté avec `/Users/martinfeldmann/workout-session-tracking/.venv/bin/python` avant les reproductions : verdict ISOLATED. Aucun full sweep lancé. Reproductions ciblées uniquement ; les 49 tests annoncés par le builder ne sont pas présentés ici comme une preuve scientifique ni comme un run de cette revue. Aucun fichier du repo modifié. RTK.md n'a pas été trouvé aux emplacements du repo/canonique/personnel examinés.

Attendu avant admission : correction I1, relecture ciblée, décision/revue et octets effectifs pinés dans la nouvelle autorité ; tests publics après publication via vrai loader/évaluateur/validateur, puis revue code et contrôles de livraison. Ces étapes publient une convention limitée, sans validation humaine réelle ni runtime. Aucune permission clinique, de reprise après préoccupation ou d'accompagnement des six autres réalisations n'est dérivée de cet avis.


## Addendum final — relecture ciblée du correctif I1/M1

8 novembre 2026, même reviewer, même HEAD, correctifs non commités identifiés par le nouveau `reviewed-hashes.json`. Les empreintes du premier état sont conservées dans `reviewed-hashes-before-I1.json`. Il s'agit uniquement de la fermeture des constats précédents, sans nouvel audit élargi.

Changements relus : `_qualified` exige maintenant que l'occurrence réelle de la préparation et du choix n'arrive pas après l'essai ; `_familiar(..., not_before=prep_at)` rend une ancienne familiarisation insuffisante pour une nouvelle préparation. Le drapeau de familiarisation porté par l'essai peut conserver sa signification existante d'attestation d'une familiarisation préalable applicable, sans prétendre authentifier le fait. La garde d'offre d'acceptation exige explicitement un CONTEXT_CONFIRMED courant, même réglage, séquence et occurrence antérieures à l'essai. Un contexte absent ou confirmé après ne donne plus cette invitation. L'initiation d'un nouvel essai exige le dernier contexte/réglage confirmé et une familiarisation applicable à la préparation courante.

Les tests nouveaux relus couvrent préparation et choix postérieurs (deux cas), absence de confirmation de contexte et confirmation de contexte après l'essai. Le builder annonce 53/53 tests ciblés verts ; ce chiffre n'est pas présenté comme un run indépendant du reviewer. Après nouveau `check_scope` ISOLATED, les reproductions ciblées du reviewer ont effectivement constaté :

| Cas | Résultat observé |
|---|---|
| Trajectoire d'origine | QUALIFIED |
| Préparation réellement acquise à 11:04, essai à 11:03 | OBSERVED, aucune INITIATE_TRIAL ou ACCEPT_EXACT_SETTING |
| Choix réellement acquis après essai | OBSERVED, mêmes actions fermées |
| Préparation réellement antérieure à 11:00, enregistrée tard à 11:04 | QUALIFIED ; occurrence et enregistrement ne sont pas confondus |
| Nouvelle préparation à 11:02:30, confirmation de familiarisation à 11:02:45, essai à 11:03 | QUALIFIED ; une préparation suivie d'un essai applicable reste possible |
| Confirmation de contexte absente | OBSERVED, aucune ACCEPT_EXACT_SETTING |
| Confirmation de contexte après essai, provenance du choix conservée indépendamment | OBSERVED, aucune ACCEPT_EXACT_SETTING |

Ces vérifications ferment I1 et M1 dans leur portée. Elles vérifient la cohérence du protocole et de sa représentation ; elles ne prouvent pas authenticité des déclarations, maîtrise réelle d'un dispositif ni bénéfice/sûreté biologique. Un changement réel de setup doit toujours être enregistré comme nouvelle préparation par le propriétaire PLAN : falsifier ou omettre sa chronologie n'est pas détectable par un moteur pur. Aucun comportement historique V3 n'a dû être modifié pour la correction.

**Verdict final : publication isolée limitée désormais défendable.** Le protocole peut être admis dans ce seul périmètre, avec pins du bundle effectivement corrigé, décision et revue réelles ; l'entrée publique ne doit devenir positive qu'après publication de cette autorité. Tests publics avec vrai loader et contrôles de livraison restent à réaliser par le builder. M2 est traité comme mise à jour du reçu final, sans réécriture des sources historiques pinées. L'avis n'est ni une validation humaine/runtime, ni une certification clinique, ni une admission des six autres procédures de premier usage.
