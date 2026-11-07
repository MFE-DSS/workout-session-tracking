# Revue SCI effective — stage2 v3, profil limité

Date : 7 novembre 2026. Reviewer : **agent `/root/stage2_effective_science_review`** ; revue agentique distincte de l'auteur, aucune identité ou qualification humaine revendiquée.

Worktree : `/private/tmp/auren-sci-p02-stage2-admission-v3`.
HEAD effectivement lu : **`a941e645f55f7da86285b811b673562aa93db6d5`**.
Base annoncée du changement : `97173680c1474bb906d413c192e6c120b97bfe5d`.

## Décision de revue

**Avis SCI final après relecture ciblée du correctif I1 : condition scientifique levée ; admission limitée recommandée.** Cette revue soutient le passage du profil exact de CANDIDATE à ADMITTED, avec C1–C5 `ADMITTED_WITH_LIMITS` et C6 `EXPLORATION_POLICY_ADMITTED`. La correction non commitée sur le HEAD ci-dessus est identifiée par ses empreintes dans l'addendum final. Le registre est encore CANDIDATE au moment de cette conclusion ; la publication devra figer les sources effectives, la décision et cette revue, puis suivre les contrôles de livraison applicables. Aucun nouveau survey anatomique, modèle de temps ou contrat n'est requis par cet avis. Les constats I1 ci-dessous sont conservés comme historique **résolu**, pas comme blocker ouvert.

Cette conclusion est une décision d'admissibilité de politique sous incertitude. Elle n'établit ni effet biologique individuel, ni sécurité clinique, ni optimalité, ni vraie mesure de RIR, ni durée positive, ni autorisation de transport/runtime. Les tests ne produisent aucune de ces preuves.

## Findings

### Critical

Aucun identifié dans cette revue SCI ciblée. Le registre reste effectivement CANDIDATE et `produce_v3` exige l'autorité ADMITTED avant un résultat autoritaire : le défaut ci-dessous n'est pas présenté comme une activation actuelle.

### Important — I1 : état/chronologie de qualification C3 non garantis — RÉSOLU par le correctif relu

Références : `authority/PROTOCOL.md:6–12`, `v3_producer.py:124–145`, `v3_validation.py:31–50`, et helper historique `load_calibration.py:90–95`.

Le protocole accepté exige la familiarisation avant essai ou travail. Le premier positif s'appuie précisément sur un essai qualifié suivant ce protocole. Pourtant le helper repris accepte un événement `FAMILIARIZATION_CONFIRMED` antérieur à l'acceptation, même s'il est **postérieur à l'essai**, et même lorsque l'essai ne porte aucune confirmation de familiarisation. Ni le producteur v3 ni les invariants indépendants v3 ne ferment cette possibilité. Le replay du même producteur ne constitue pas une seconde garde de cette condition.

Reproduction exécutée sans modification du repo, avec le Python du venv canonique, après `scripts/check_scope.py` (ISOLATED ; aucun sweep lancé) :

```python
from tests.test_science_initial_policy_v3 import request
from tools.science_initial_policy.v3_admission import load_v3_registry
from tools.science_initial_policy.v3_producer import compile_plan_v3
r = load_v3_registry()
raw = request(r)
ep = raw['episodes'][0]
familiar, trial = ep['events'][1:3]
familiar['sequence'], trial['sequence'] = 3, 2
familiar['provenance']['recorded_at'] = '2026-11-07T11:03:00Z'
trial['provenance']['recorded_at'] = '2026-11-07T11:02:00Z'
trial['provenance']['measured_at'] = '2026-11-07T11:02:00Z'
out = compile_plan_v3(raw, r)
print(out.plan is not None, out.issues)
# True ()
```

Les autres faits synthétiques restent inchangés : essai terminé/réussi, qualité acceptable, aucune gêne, réglage courant accepté. L'essai n'a pas de `familiarization_confirmed=True`. Les dates et séquences sont cohérentes ; il ne s'agit pas d'une attaque par dataclass non revalidée. Le résultat observé est un **draft calculé sous autorité candidate**, pas un positif publié. Le défaut deviendrait éligible à la voie positive après seule promotion d'autorité.

À la demande de l'auteur, trois prolongements étroitement liés ont aussi été reproduits, avec tous les `recorded_at`/`measured_at` réordonnés selon les séquences :

| Suite d'événements du premier épisode, essai sans drapeau de familiarisation | Résultat réellement observé |
|---|---|
| Familiarisation confirmée1 → essai2 → contexte/réglage confirmé3 → acceptation4 | Plan calculé, aucune issue |
| Contexte1 → familiarisation confirmée2 → essai3 → FAMILIARIZATION_STARTED4 → acceptation5 | Plan calculé, aucune issue |
| Contexte1 → familiarisation confirmée2 → FAMILIARIZATION_STARTED3 → essai4 → acceptation5 | Plan calculé, aucune issue |

Le premier cas n'apporte pas de confirmation du réglage/contexte applicable avant l'essai. Les deux derniers ne prouvent pas que la nouvelle phase de familiarisation est terminée et que l'essai reste qualifié. Ils sont regroupés sous I1 : même absence de contrôle d'état/chronologie, aucun nouvel audit élargi. Le helper compare aussi la confirmation du réglage à l'acceptation (`load_calibration.py:85–88`) et ne bloque `FAMILIARIZATION_STARTED` que **postérieur à l'acceptation** (`:73`).

Correction minimale attendue : garde spécifique au profil v3 garantissant que le contexte/réglage et la familiarisation attestés s'appliquent déjà à l'essai qualifiant, et que cette qualification n'a pas été invalidée par une nouvelle phase de familiarisation non requalifiée entre confirmation, essai et acceptation, dans le producteur et les invariants du validateur. Préserver les validateurs/helpers historiques pinés ; ne pas modifier leur interprétation rétroactivement. Préserver la possibilité d'une attestation sur l'essai lui-même, si elle indique effectivement la familiarisation préalable. Vérifier refus des quatre scénarios ci-dessus et conservation du scénario chronologique valide, y compris une nouvelle familiarisation suivie d'un nouvel essai qualifié valide. Ce point ne demande aucun ajout de charge initiale, nombre d'essais universel, échec imposé ou preuve de vraie2RIR.

### Condition de publication connue, non nouvelle objection de doctrine

Le registre, le protocole et `ADMISSION.md` sont encore explicitement CANDIDATE/PENDING ; c'est correct avant décision effective. Le manifeste courant ne clôt pas encore les octets du producteur/validateur/revue SCI. L'auteur confirme que cette clôture est prévue avant la première publication : sources effectives et décision/revue doivent entrer dans le manifeste, loader exclu du cycle et piné séparément par le manifeste final d'artefacts. Ne pas transformer le présent avis conditionnel en admission déjà reçue, ni promouvoir simplement un label. Cette clôture est un prérequis de publication, pas une preuve scientifique supplémentaire ni une demande de nouvelle étude. Les entrées synthétiques demeurent des preuves d'exécution distinctes de l'autorité.

### Minor — M1 : statut documentaire de préparation encore daté

`design.md`, `POLICY_CANDIDATE.md` et `REVIEW_AND_VALIDATION.md` conservent des formulations « pas de GO BUILD reçu »/préparation, alors que `BUILD_AUTHORIZATION.md` et le bandeau de `DECISION_FOR_OPERATOR.md` consignent les décisions reçues. Le dossier historique peut rester lisible, mais la publication doit identifier clairement l'état final et son SHA ; aucune contradiction de statut ne doit laisser croire que le GO BUILD vaut admission ou que l'admission est déjà publiée. Ce nettoyage ne change pas la doctrine et ne bloque pas son admissibilité conceptuelle.

## Appréciation par critère

| Critère | Appréciation scientifique ciblée |
|---|---|
| C1 | Admissible pour adulte **déclaré** non clinique, hypertrophie, exactement deux séances, limitations connues vides. Le code exige les cinq familles requises, traite manque/conflit avant compilation et refuse population/cadence/limitations hors scope. Ce sont des déclarations, pas un examen médical. |
| C2 | Les valeurs 2 séries, 8–12 reps, cible subjective2RIR, repos120/90 sont les conventions historiques explicitement réadmises sur ce bundle. 14 séries physiques/séance et28/semaine sont de l'arithmétique, pas des séries efficaces par muscle. Aucun optimum ni tolérance individuelle garanti. Pas de charge calculée depuis poids/âge/sexe, ni d'ajustement automatique. |
| C3 | Protocole opérationnel admissible ; condition I1 levée après relecture ciblée du correctif identifié dans l'addendum. La qualification actuelle exige par ailleurs essai comparable observé, plage8–12 réalisée, qualité/gêne connues acceptables et acceptation courante ; les préoccupations conservées bloquent, bootstrap non qualifié reste hors positif. L'acceptation est provisoire et ne mesure pas l'effort exact. |
| C4 | Sept identités/réalisations bilatérales explicitement liées ; contexte/appareil/source actuels nécessaires, exclusion/indisponibilité sans remplacement silencieux hors binding. G17 reprend la qualification conditionnelle existante ; pas d'ouverture des quatre autres pulls ou de nouveau claim musculaire. L'inventaire global peut rester inconnu : les confirmations locales consommées ne sont pas un inventaire fabriqué. |
| C5 | Quinze états de connaissance depuis les rôles curés exacts ; les slots non documentés restent unresolved/UNKNOWN. Le producteur et les invariants maintiennent ce sens. Aucune couverture régionale complète, quantité de croissance, crédit numérique ou faiblesse diagnostiquée n'est déduite. |
| C6 | Admissible comme **politique d'exploration**, compte tenu de l'approbation opérateur spécifique. Structure séquentielle liée au binding,750s de repos/séance, refus si cette borne consomme le budget ; sinon temps UNKNOWN/BUDGET_UNCERTAIN. L'ack exact conditionne la permission et ne change pas la preuve temporelle. SUPPORTED, durée positive et anciennes gates temporelles v1/v2 ne sont pas satisfaits. |

## Sources effectivement examinées et limites

Lecture effective : CLAUDE.md, STANDING_MERGE_AUTHORIZATION.md, design et BUILD_AUTHORIZATION du change ; ADMISSION_CASE, POLICY_CANDIDATE, EVIDENCE, DECISION_FOR_OPERATOR ; authority/{ADMISSION,PROTOCOL,registry,sources} ; les trois modules v3 demandés ; helpers de calibration, modèles d'épisodes, contrats v3 et validation de slots v2 ; conventions0.2.0, génération des profils v2, passage pertinent de l'overlay G17 et manifeste conjoint (doctrine de volume/incertitude/provenance). Les tests existants ont été **lus comme scénarios**, jamais traités comme preuve d'efficacité ou d'admission. Aucun sweep ni suite positive complète n'est revendiqué par cette revue.

Recoupement externe ciblé de sources primaires, sans promotion de nouvelles références runtime :

- [ACSM/Currier2026, PMID41843416](https://pubmed.ncbi.nlm.nih.gov/41843416/) : résumé primaire retrouvé par recherche ; synthèse adulte sain et bénéfices généraux du RT. Cela appuie une direction de départ, sans valider les sept exercices, leurs paramètres exacts ou leur effet individuel. Le PMC direct a renvoyé un contrôle d'accès ; aucune lecture intégrale nouvelle n'est revendiquée.
- [Hermann2025, PMID40249908](https://pubmed.ncbi.nlm.nih.gov/40249908/) : résumé lu ; résultats favorables dans les deux conditions et nuance possible en faveur de l'échec pour certaines mesures. Ne permet pas de déclarer une équivalence universelle ou un optimum2RIR ; ne commande pas un essai initial à l'échec.
- [Singer2024](https://www.frontiersin.org/journals/sports-and-active-living/articles/10.3389/fspor.2024.1429789/full) : source primaire accessible ; incertitude des effets de repos. Pas de preuve d'une coupure biologique universelle mono/poly120/90 ou de durée de séance.
- [Wiedenmann2026](https://link.springer.com/article/10.1186/s13102-026-01997-y) : méthodes/résumé lus ;26participants, six séances et poursuite à l'échec dans le protocole étudié. Son apprentissage du RIR ne valide pas automatiquement le protocole AUREN sans échec ou la confiance individuelle.
- Les accès directs PubMed pour Pelland41343037, Refalo38393985 et Steele35790622 ont donné des pages sans résumé exploitable dans cet outil. Leur présentation dans EVIDENCE et les pins E0 sont examinés comme provenance existante ; aucune vérification fraîche intégrale de ces trois articles n'est revendiquée. La décision présente ne dépend pas d'une nouvelle précision empirique issue de ces accès.

## Jugements explicitement déclinés

Aucune certification clinique, validation d'un vrai utilisateur ou appareil, preuve que chaque groupe/région reçoit sa dose efficace, classement optimal d'exercices, seuil personnel de volume/récupération, dose sûre pour tout adulte, vraie mesure de RIR, modèle de temps positif, bootstrap positif, reprise après préoccupation, fraîcheur serveur/révocation réseau, authentification/ownership transport, journal d'exécution, activation SDK/API/UI ou déploiement. Ces absences sont conservées comme limites ; elles ne sont pas transformées en défauts demandant un audit général hors scope.

Aucune modification effectuée dans le repo par ce reviewer. Seul ce rapport externe est écrit. Les nouveaux fichiers non suivis apparus pendant la revue appartiennent au travail parallèle de l'auteur et n'entrent pas dans la décision sur le SHA ci-dessus.


## Addendum — relecture ciblée de résolution I1

Reviewer : **agent `/root/stage2_effective_science_review`**, 7 novembre2026. Aucune identité ou qualification humaine. Relecture limitée à ma condition C3 ; pas de nouvel audit global, bibliographique ou codewide.

HEAD inchangé : `a941e645f55f7da86285b811b673562aa93db6d5`. Le correctif relu est encore non commité. Pour éviter d'attribuer sa résolution aux seuls octets de ce commit, voici les SHA256 des fichiers effectivement relus :

| Fichier | SHA256 |
|---|---|
| tools/science_initial_policy/v3_producer.py | `056b094eebc42dd9aedaaa924df2c0c29b5cef22db805cfefc0cb361b17b3427` |
| tools/science_initial_policy/v3_validation.py | `b9facc8f6ef9a91b016d584d0143bb6ab4a047597ea04f08ed86280514038ccc` |
| tests/test_science_initial_policy_v3.py | `a369db5058d933464e86979222b69755ba5afe54e0afff7352d44baa2d27a373` |

`_qualified_order` impose au producteur une confirmation actuelle du contexte/réglage identique avant l'essai, une familiarisation applicable à l'essai depuis la dernière phase STARTED, ou l'attestation portée par l'essai lui-même, et aucun nouveau STARTED après l'essai. `_check_phase_order` reconstruit indépendamment ces préconditions dans le validateur : un STARTED remet la familiarisation à non confirmée et le dernier état précédant l'essai est vérifié ; une nouvelle phase après l'essai bloque aussi. Les helpers/validateurs historiques examinés ne sont pas modifiés par ce correctif. Les quatre scénarios de I1 sont ainsi fermés sans changer la signification scientifique d'OBSERVED_SETTING ou de CONFIRMED.

Preuves ciblées lues : `.superpowers/sdd/IMPLEMENTATION_PLAN/sci-review-red.log` montre les huit échecs attendus avant correction (quatre variantes × producteur/validateur) ; `sci-review-green.log` montre30tests passants, dont ces huit cas et le scénario valide existant. Les tests adverses du validateur présentent un slot valide et des observations à chronologie altérée directement à la garde indépendante ; ils ne se contentent pas d'un replay du producteur. Ces logs ont été lus, pas relancés par ce reviewer. Aucun nouveau probe général effectué lors de cette relecture. La décision de résolution repose aussi sur les gardes effectivement lues, pas seulement sur le nombre de tests.

**Conclusion de résolution : I1 CLOSED ; aucun Important SCI restant dans le périmètre examiné.** Je recommande l'admission limitée du bundle corrigé avec C1–C5 `ADMITTED_WITH_LIMITS` et C6 `EXPLORATION_POLICY_ADMITTED`, sous les mêmes limites exactes de la revue : adulte déclaré non clinique, hypertrophie, exactement deux séances, limitations connues vides, sept réalisations bilatérales précises, réglages actuels observés/qualifiés/acceptés, conventions de dose héritées, temps UNKNOWN et ack exact pour la permission exploratoire. Aucun bootstrap positif, preuve clinique/biologique individuelle, optimum, fit temporel positif ou runtime n'en découle. L'alignement du minor documentaire et la clôture des sources restent les travaux de publication annoncés ; ils ne rouvrent pas la doctrine ou une nouvelle demande d'admission si ses règles effectives restent identiques.
