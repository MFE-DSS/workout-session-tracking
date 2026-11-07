# SCI-P02 STAGE2 — design de l’admission limitée et du vrai producteur v3

**7 novembre2026. PROPOSED, pas de GO BUILD/admission positive reçus.** Base97173680c1474bb906d413c192e6c120b97bfe5d. Décisions préparées : [dossier C1–C6](../../../docs/science/sci-p02-initial-policy/stage2-v3/ADMISSION_CASE.md), [politique candidate](../../../docs/science/sci-p02-initial-policy/stage2-v3/POLICY_CANDIDATE.md), [décision opérateur](../../../docs/science/sci-p02-initial-policy/stage2-v3/DECISION_FOR_OPERATOR.md).

## Brainstorming / Options / Risques / Choix retenu

A. Exiger un temps SUPPORTED avant toute première utilisation : respecte les anciens profils, mais nécessite modèle/observations validés absents. Aucun nouveau modèle ne sera improvisé.
B. Faire admettre le départ exploratoire déjà représentable en v3, garder la durée inconnue et appliquer un protocole/ack précis : chemin retenu pour proposition, avec modification C6 explicitement revue.
C. Déclarer READY depuis le draft v2 ou un label d’approbation : écarté, pas de vraie autorité et contrats historiques incompatibles.

Le choix technique B réutilise v3 ; aucune incompatibilité de forme ne justifie v4. Il reste une décision de politique, pas une preuve de durée. Risques dominants : dilution de C6, contexte inventé depuis disponibilité, revalidation insuffisante et dégradation des pins historiques. Les clauses ci-dessous les rendent testables.

## D1 — périmètre positif minimal

Adulte déclaré non clinique, objectif hypertrophie, exactement deux séances/semaine, deux budgets déclarés, limitations connues vides. Expérience/anthropométrie/priorités facultatives. Sept réalisations bilatérales fixées par le binding pour sept intentions existantes ; ce n’est pas un classement universel. Inventaire global inconnu autorisé si les seuls contextes d’exercices réellement consommés sont confirmés. Contexte/réalisation/appareil/côté/sémantique et sources courants complets nécessaires, jamais déduits du nom d’une salle.

Deux séances du même schéma initial, sans calendrier inventé ;14séries physiques/séance,28/semaine depuis conventions existantes à réadmettre. Aucun optimum, adaptation automatique ou engagement que toutes les zones/régions sont directement couvertes. Chaque nouvelle séance exige réévaluation de l’état courant avant handoff ; pas de TTL arbitraire.

## D2 — C3 et prescriptions

Réutiliser CalibrationEpisode, `calibrate_for_admission`, TrialReviewV3 et les types de prescription existants. Le premier binding positif accepte **OBSERVED_SETTING uniquement**, pour sept réglages qualifiés/acceptés au présent, avec réalisation et exécution comparables. Ces observations peuvent avoir été acquises lors de la familiarisation initiale dans AUREN ; elles ne supposent pas des mois d’historique.

Un slot encore BOOTSTRAP_PROTOCOL/NEEDS_CALIBRATION, ou une réalisation dont la plage n’a pas été observée, ne satisfait pas ce premier binding positif : draft/revue, permission DENIED. Le protocole C3 décrit comment préparer/acquérir ces faits, sans devenir une prescription positive avant qualification. Cela évite de redéfinir `confidence.feasibility=CONFIRMED` exigé par v3 : ce champ s’appuie ici sur la capacité d’exécution effectivement observée, pas sur la seule disponibilité du dispositif. Il ne mesure ni l’effort exact ni le temps. Le chemin bootstrap positif reste un manque précisément borné hors première admission, sans nouvelle version de contrat imposée.

Aucune charge initiale calculée, série d’échauffement universelle, nombre de tentatives ou incrément générique. Ordre d’effort/disponibilité du réglage provient du dispositif actuel ; l’algorithme ne produit pas de nouvelle charge depuis des reps seules. Cause inconnue/interruption reste non évaluable. Préoccupation/échec/signaux de sécurité inconnus interrompent le chemin positif. Aucun restart automatique après préoccupation : aucune base de reprise n’est admise dans ce scope.

L’essai de calibration est distinct des séries prescrites. Le protocole peut préparer des observations sans prétendre la faisabilité des8–12reps déjà établie. La confiance demeure LOW/UNKNOWN et individual_response NOT_ESTIMATED. Si l’exécution ne permet pas le protocole, sortie/revue ; aucune consigne de poursuite à l’échec.

## D3 — C6 explicite, sans borne supérieure inventée

Le binding prescrit une structure traditionnelle séquentielle ; cette structure provient de la politique, pas d’un champ absent de PlanV2. La borne de repos applicable est calculée par `assess_structural_time(..., structure=...)` existant. Sur la sélection proposée : quatre poly120s et trois mono90s entre deux séries, soit750s de repos par séance ; c’est une somme prescrite, pas la durée.

R≥budget réfute la configuration non vide ; sinon BUDGET_UNCERTAIN avec composantes inconnues. Ni SUPPORTED, ni BUDGET_COMPATIBLE_BY_POLICY ne sont produits dans cette première admission. Aucun budget minimal chiffré arbitraire. La permission couvre l’exploration, pas une promesse d’achever les14séries dans le budget. Atteinte de limite/arrêt préserve les faits incomplets ; repos jamais raccourcis.

État d’admission à proposer pour C6 : `EXPLORATION_POLICY_ADMITTED`, avec `supported_time=NOT_ESTABLISHED`. Les gates positives temporelles v1/v2 et du mode SUPPORTED v3 restent intactes. Le delta normatif porte exactement cette exception v3 ; sans approbation, aucune science positive sous temps inconnu.

## D4 — autorité successeur et préservation des anciens profils

Nouveau profil d’autorité, pas nouveau contrat : `initial-policy-v3-admission-registry/1.0.0` et binding `initial-plan-v3-binding/1.0.0`. Registre historique vide1.0.0 et fonctions historiques inchangés. Le nouveau loader vérifie les octets admis, source/manifestes, statut actif et recompute le matériel ; aucun dataclass modifié ou label du caller ne fait autorité.

La décision documentaire identifie auteur/reviewer/version/base/règles/limites et approbation reçue. Un hash n’est pas une preuve de revue : le registre ne sera publié qu’après cette admission et la revue SCI. Manifeste des sources : E0/catalogue/curation/pull/profils, conventions de dose, protocole/temps/approbation et code effectif. Exclure le loader de son propre cycle de hash ; le manifeste d’artefacts final le pinnera séparément. Ne pas pinner un chemin OpenSpec actif destiné à l’archive.

`bundle_digest` est nouveau et lie policy/binding/code/admission ; le digest de science et la version de catalogue réutilisent les faits curés inchangés. Engine proposé `initial-policy-producer/3.0.0`, policy candidate `initial-hypertrophy-policy/1.0.0-limited` après admission réelle. Les versions de proposition ne sont pas des références approuvées.

Le validateur `blueprint_first_plan_v3.validate_exchange` reste historiquement négatif et inchangé. Le nouvel entrypoint canonique **du profil admis** `v3_validation.validate_admitted_exchange_v3` est déclaré par cette spec : modèles canoniques v3, vérifications indépendantes d’invariants, autorité réelle et recomputation du producteur. Ce chemin ne doit pas être un validateur permissif parallèle ; aucun positif n’est accepté seulement parce que le producteur l’a construit.

## D5 — producteur et validation indépendamment testables

`produce_v3(request, registry)` est pur, sans horloge globale/IO d’écriture/aléa. Réemploi du matching déterministe et de l’assessment. Affectation fixe des sept intentions dans l’ordre revu, uniquement dans le pool admis disponible/contextualisé/exclusions respectées ; pas d’algorithme nouveau de ranking ou d’optimisation biologique. Toute substitution hors binding exige recalcul/admission applicable ; pas de choix forcé si le pool est vide.

PlanV2/sessions/slots/dose/projection qualitative restent les types existants. Quinze rapports : rôles effectivement sourcés, UNKNOWN pour ce qui manque, pas zéro physiologique. G17 utilise seulement la qualification déjà curée pour sa réalisation exacte ; pas de nouveau spike d’exposition ni réouverture des quatre autres pulls.

Le validateur positif doit vérifier indépendamment : cinq inputs/scope, deux séances et allocation exacte, chaque intention/candidat/réalisation/contexte/exclusion, dose/source/conventions, calibration ou protocole admis, références qualitatives et inconnus, temps depuis structure effectivement liée au binding, empreintes/owner/snapshot/révision/version/ack. Puis recomputation stricte sensible aux types de la sortie complète. Ne pas appeler l’ancien validateur négatif comme s’il admettait le positif ; réutiliser ses helpers pertinents quand leurs préconditions s’appliquent, sans les modifier ou recopier tout le module.

`generated_at=max(as_of, acknowledged_at si présent)` ; aucune date nouvelle pour un fait. Empreintes facts/observations/évaluation et plan+temps existantes. Identité logique du plan = plan_time_fingerprint ; aucune nouvelle identité persistée ou champ de contrat.

Une première sortie SCIENTIFICALLY_READY/BUDGET_UNCERTAIN rend REQUIRES_TIME_ACK. L’utilisateur synthétique peut ensuite fournir explicitement son ack lié au plan/temps/politique exacts ; le producteur réel rend ELIGIBLE si toutes conditions sont inchangées. L’ack ne modifie ni preuve scientifique ni temps. Un test ne fabrique pas cette action en production.

## D6 — invalidation et absence

Manque/conflit requis prend priorité ; hors population/cadence/limitation/protocole donne refus/revue explicite. Contexte inconnu n’est pas une salle complète. Préoccupation antérieure sans reprise admise reste bloquante. Changement/retrait de policy/source/contexte, exclusion ou révocation du binding invalide résultat et ack avant nouveau handoff. Aucune réutilisation implicite d’une ancienne décision.

Le registre local isolé reflète sa publication versionnée, pas une révocation serveur temps réel. Tests de source/index manquant, retiré ou altéré : refus fermé. PLAN devra relire une autorité fraîche au démarrage ; cette livraison ne peut certifier la fraîcheur réseau ou l’identité d’un compte.

## D7 — preuve positive et handoff

Scénarios obligatoires : réglages observés acceptés donnant le positif ; bootstrap/charge inconnue conservés hors positif ; temps inconnu sans ack puis avec ack exact ; gym global inconnu mais réalisations connues ; vraie indisponibilité/conflit/incompatibilité et retrait. Aucun nouveau bundle de fixtures négatives redondant. Le positif public n’est exporté qu’après tests du vrai producteur et validation via le registre réellement admis.

Étiquette des artefacts : `REAL_PRODUCER_SYNTHETIC_INPUT_NOT_SERVED`. Identité et faits synthétiques sont distingués des preuves d’autorité. Handoff PLAN : manifeste/version/entrypoint autoritaire, snapshot propriétaire attendu, champs réellement utilisés, explications/limites, empreintes, état de temps/permission, invalidations/arrêt/retry, erreurs et absence de transport. Pas d’API, SDK, UI, séance possédée ou activation.

## D8 — build, revues et livraison après décisions

Pas d’apply avant admission proposée revue et GO BUILD distinct. Ensuite TDD, broad ciblé selon check_scope, rejeux historiques et artefacts préservés, revue SCI et revue code séparées, CI réelle, correction en scope, PR/merge exactHEAD sous GOV-MERGE-01 puis canonique/closeout/cleanup. Aucun GO de déploiement. L’admission limitée peut être livrée pure/NOT_SERVED ; elle ne ferme ni DATA/PLAN/RELEASE ni MOB03 complet.
