# Calibration/time01 — design proposé pour apply isolé

6 novembre 2026. **PROPOSED, NOT_IMPLEMENTED, NOT_ADMITTED, NOT_SERVED.** Choix techniques de l'agent, pas décisions opérateur déjà reçues. Delta : `openspec/changes/science-initial-plan-policy/calibration-time-01.md`.

**Revue opérateur reçue ensuite : « continue ».** Réalisation isolée de ce design autorisée ; NOT_ADMITTED/NOT_SERVED conservés. Les formulations proposées ci-dessous sont l'historique de la conception maintenant retenue pour build, pas une preuve d'admission scientifique.

## 1. Un producteur successeur, pas deux nouveaux rapports

`produce_v2(evaluation_request, trusted_bundle)` sera le point d'entrée pur. Il validera les entrées, composera les références scientifiques autorisées, affectera les sept intentions, évaluera calibration et temps, puis produira un vrai FirstPlanRecommendation v1 validé par validate_exchange et des diagnostics scientifiques isolés. Engine proposé `initial-policy-producer/2.0.0`, politique de travail `initial-hypertrophy-policy/0.3.0-proposed` ; numéros logiciels, pas admission biologique.

Le producteur1.0.0, ses onze fixtures, le rest-floor1.0.0, curation1.0.0 et pull1.0.0 restent identiques. Aucun import de v2 depuis app/, mobile, registry/producer v1 ou démarrage. Aucun faux APPROVED dans le bundle de production. La matrice des tests exerce v2, pas un mock renvoyant les résultats attendus.

## 2. Entrées, identité et empreinte complète

| Champ de l'enveloppe isolée proposée | Invariant |
|---|---|
| `contract_version` / `request` | `initial-plan-evaluation/1.0.0` ; FirstPlanRequest v1 inchangé, engine v2 explicite |
| `subject_ref`, `as_of`, `execution_snapshot` | Référence opaque cohérente ; aucune authentification déduite d'une string. Futur adaptateur propriétaire/consentement hors scope. Sources datées≤as_of, pas d'horloge globale |
| `context_key` | Identité canonique, réalisation/qualificatifs, appareil/contexte, signification de charge, convention total/par haltère, côté si unilatéral. Un simple nom ou slot ne suffit pas |
| `calibration_events` / `timing_bases` | Faits stricts/provenance/source_ref, IDs uniques, version et unités. Historique comparable explicitement vérifié, pas extrapolé d'un autre exercice |
| `bundle_digest` / `effective_science_digest` | Sources et politiques réellement chargées ; aucun registre approuvé fourni par JSON utilisateur |

L'empreinte interne d'évaluation porte request complet, snapshot dédupliqué/ordonné, règles, versions et digests. `request_fingerprint` du DTO v1 reste exactement decision_fingerprint(request) ; il n'est **pas** présenté comme couvrant les nouvelles observations. Sortie isolée : `{evaluation_fingerprint, request_fingerprint, recommendation_v1, calibration_by_context, time_by_session, blockers, runtime:NOT_SERVED}`. Le vérificateur d'enveloppe doit recalculer les deux empreintes et contrôler leurs liens. Mutation d'un fait, propriétaire, contexte ou bundle change l'empreinte complète.

Aucun digest/historique encodé dans un Observation.fact texte libre ; aucun nouveau champ du schéma SCI partagé. FirstPlanClient v1 n'accepte pas cette enveloppe comme une nouvelle réponse runtime : un futur adaptateur/contrat de transport coordonné sera nécessaire. Le DTO v1 inclus peut être testé avec son validateur courant sans prétendre que le client a vérifié le sidecar.

## 3. Calibration minimale et sens du résultat

**Convention opérationnelle proposée :** CALIBRATED signifie seulement « une charge/réglage effectivement essayé, accepté et comparable est disponible comme référence de départ révisable ». Cela ne signifie ni vrai2RIR mesuré, ni charge optimale, ni aptitude médicale ou zones E7 connues. Conserver `effort_sufficiency=UNKNOWN` si le signal ne permet pas davantage. La confiance de prescription reste LOW/UNKNOWN explicitée, distincte de la certitude du fait poids/répétitions.

Aucune charge proposée à froid. L'utilisateur confirme le réglage effectivement disponible pour cet exercice, ses unités/signification et les incréments si une variation est envisagée. Un inventaire de salle n'est jamais requis. L'algorithme minimal **ne calcule aucune augmentation/réduction** : une nouvelle charge exige une nouvelle sélection utilisateur et une observation. Aucun pourcentage, plus petit pas supposé, e1RM, transfert, ratio corporel ou rampe de familiarisation.

Familiarisation : événement explicite de préparation/réalisation contrôlée, charge choisie/confirmée par l'utilisateur, tentative non maximale et arrêt libre ; aucune quantité universelle de séries, répétitions, séances ou minutes. C'est une convention de procédure, pas preuve de précision RIR. Les essais préparatoires restent distincts des séries de travail. Pas de test à l'échec imposé pour « vérifier » le RIR.

Événements proposés : `CONTEXT_CONFIRMED`, `FAMILIARIZATION_STARTED`, `FAMILIARIZATION_CONFIRMED`, `ATTEMPT_OBSERVED`, `SETTING_ACCEPTED`, `CONCERN_REPORTED`, `EQUIPMENT_UNAVAILABLE`. Tentative : event_id/sequence/horodatage/source, réglage réel, reps observées, completion/success explicites, technique et gêne déclarées KNOWN/UNKNOWN, RIR facultatif déclaré. Horodatages conscients du fuseau ; aucun fuseau d'un fait inconnu inventé. Ne pas convertir completed=true du journal en succès technique. SETTING_ACCEPTED référence une tentative précise et le contexte courant ; une déclaration de poids seule ne suffit pas.

La familiarisation confirmée est une précondition de CALIBRATED, pas son seul fait d'avoir démarré. La tentative observée peut aussi fournir cette familiarisation **si** une confirmation explicite et sourcée dit qu'elle a servi à pratiquer/valider la réalisation ; aucune déduction depuis completed ou le nombre de séances. Elle garde le rôle CALIBRATION_TRIAL, ne devient pas rétroactivement une série de travail. Cela n'impose ni une série supplémentaire ni un nombre universel d'essais. Pour un mouvement réellement familier, une confirmation actuelle sourcée de familiarité/réglage peut établir cette précondition ; son absence maintient pending.

| État conceptuel interne | Condition / transition déterministe |
|---|---|
| INSUFFICIENT_DATA | Identité/contexte/provenance/comparabilité manquants ; conflit explicite → diagnostic conflictuel. Valeur illégale → erreur de validation, pas faux inconnu |
| UNAVAILABLE | Exercice/appareil explicitement indisponible dans le contexte courant. Aucun ancien réglage ne contourne ce fait |
| NEEDS_CALIBRATION | Contexte connu, aucune tentative acceptée comparable ; aucune charge kg de repli |
| CALIBRATION_IN_PROGRESS | Familiarisation/essai commencé, incomplet, ou nouvelle vérification nécessaire ; réglage observé distinct d'une recommandation |
| CALIBRATED | Familiarisation confirmée, tentative complète/comparable, reps dans la plage prescrite, pas de gêne/technique préoccupante/échec dans cet épisode, signaux requis connus et acceptation utilisateur actuelle de ce réglage. Effort subjectif non transformé en mesure |

Une gêne préoccupante, technique incertaine ou tentative échouée empêche une calibration positive automatique ; `automatic_next_action=NONE`, réglage recommandé null et motif de revue, sans diagnostic ni seuil de douleur. La donnée exécutée reste enregistrable par le domaine existant ; cela n'invente pas une interdiction du rail. Les signaux UNKNOWN requis n'équivalent pas à « aucun problème ». Une préoccupation plus récente invalide le résultat opérationnel courant, jamais le fait historique.

**Priorité de reprise proposée :** un épisode ayant une préoccupation/échec reste bloqué pour toute calibration positive automatique, même si un SETTING_ACCEPTED ou une tentative ultérieure y arrive. Pas d'événement de « guérison » ni de reprise automatique dans ce protocole minimal. Une reprise exige un **nouvel épisode** lié au précédent, et un `restart_basis_ref` explicitant la revue/décision humaine ; les motifs non résolus restent bloquants et les anciennes tentatives ne qualifient pas ce nouvel épisode. Le build vérifiera l'existence/cohérence de cette base, sans inventer une autorisation clinique. En l'absence d'une règle de revue admise/applicable : résultat de reprise INSUFFICIENT_DATA, aucune suggestion automatique. La politique clinique ou d'évaluation technique nécessaire pour lever une préoccupation n'est pas construite ici. Cette convention conservatrice est proposée à l'acceptation, pas une conclusion expérimentale de santé.

Concrètement, `restart_basis_ref` doit appartenir à un registre de règles de revue réellement admises du bundle de confiance, avec même sujet/contexte et liste des événements examinés ; une string fournie par l'appelant n'est pas une autorité. Ce registre de reprise est **vide par défaut dans cette version**. Une reprise après épisode bloqué est donc explicitement non prise en charge positivement tant que sa politique manque. Le snapshot de confiance doit déclarer sa complétude pour la chaîne des épisodes ; omission/inconnu de cette provenance empêche de certifier l'absence d'une préoccupation antérieure. Rien ici n'authentifie un futur client non fiable ou ne remplace l'adaptateur propriétaire.

Historique de retour : même identité/réalisation, même appareil/assistance/signification et plage pertinente ; source passée exacte et confirmation utilisateur de sa comparabilité/charge disponible aujourd'hui. Aucun TTL ou seuil de désentraînement arbitraire ; sans confirmation, historique cité comme repère mais NEEDS_CALIBRATION. Ni charge d'unilatéral déduite d'un bilatéral, ni poids de pile transformé en résistance corporelle effective.

Réglages : external_load_kg peut alimenter ultérieurement HISTORY_SUPPORTED à partir du fait exact. Assistance, poids du corps sans masse externe et réglages non massiques gardent leur sémantique ; pas de conversion silencieuse en load_kg. La représentation v1 insuffisante reste un bloqueur de projection, pas une valeur0 inventée. RIR absent est permis comme fait ; il ne certifie pas l'atteinte d'une cible d'effort.

Replay : snapshot immuable, ordre par séquence/temps validé, duplicate event_id identique dédupliqué ; doublon divergent, séquence ambiguë ou fait futur rejeté. Dernier fait admissible selon ordre explicite, jamais selon ordre du dict ou horloge. Reprise par sérialisation/relecture du même snapshot, sans nouvelle observation synthétique. Aucune persistance de ce cycle ajoutée ici et aucune correction des anciennes lignes SQL.

## 4. Temps : composantes, structure et incertitude

Chaque composante possède bornes en secondes ou UNKNOWN, nature `WORK / REST / PREPARATION_CALIBRATION / SETUP_TRANSITION`, source/version, périmètre, identité/contexte, hypothèses et applicabilité. La prescription indique répétitions et repos ; elle ne donne pas la durée d'une répétition. Un historique global commencé/terminé ne sépare pas les composantes. Les valeurs de vecteurs de test sont observations synthétiques, jamais constantes de politique.

Pour une structure séquentielle supportée : somme de segments disjoints, ou durée de l'union d'intervalles observés quand les horloges sont comparables. Une installation pendant le repos est comptée une seule fois. Sans preuve de disjonction/chevauchement, pas de somme complète validée ; UNKNOWN. Supersets/structures non supportés ne reprennent ni le total séquentiel ni un multiplicateur d'étude.

Repos intramouvement prescrit : somme (sets−1)×repos ; aucune réduction des120/90s conventionnels admis pour gagner des minutes. Respecter leur champ d'application et ne pas les présenter comme minimum physiologique universel. Préparation, tentatives et opérations peuvent ajouter du temps ; aucune marge « +5min », set30s ou transition universelle.

Les historiques personnels restent des observations passées. Min/max d'échantillon ou moyenne de séance ne sont pas une borne prédictive garantie. Pour porter un intervalle futur, une base de modèle doit être revue avec protocole d'inclusion, couverture, contexte et validation prédictive ; aucun N magique, percentile, TTL ou facteur de sécurité inventé. Des hypothèses produit explicites peuvent être versionnées pour l'expérimentation, mais portent `PRODUCT_ASSUMPTION`, ne deviennent pas USER_OBSERVED et ne confèrent pas une admission scientifique par leur label.

| Ordinal interne proposé | Calcul sous bases applicables et explication requise |
|---|---|
| LIKELY_FITS | Intervalle total conditionnel complet/revu, borne haute≤budget. « likely » n'est pas une probabilité estimée ; incertitude et hypothèses conservées |
| BORDERLINE | Intervalle complet applicable, borne basse≤budget<borne haute ; pas de marge relative inventée |
| LIKELY_EXCEEDS | Borne basse applicable>budget ; ou rest-floor≥budget avec travail strictement positif. Périmètre THIS_CONFIGURATION_ONLY |
| UNKNOWN | Sinon : composante essentielle non bornée, base non applicable, familiarisation/attente inconnue ou conflit de couverture. Une borne partielle qui suffit à réfuter peut néanmoins donner LIKELY_EXCEEDS |

Durée v1 reste UNKNOWN sauf deux bornes justifiées et modèle réellement admis. Un calcul LIKELY_FITS avec entrées de laboratoire/test ou hypothèses non admises ne produit pas READY. L'absence de garantie contre toute interruption arbitraire n'est pas un blocage absolu : une estimation conditionnelle validée suffit potentiellement ; sa preuve manque encore ici.

Contrainte au planificateur : configuration/session_id, budget, composantes responsables, borne/motif, portée et actions possibles `REPLAN_WITH_ADMITTED_CONFIGURATION / REQUEST_CONTEXT / REVIEW_TIME_MODEL`. Aucun retrait automatique d'intention ou de repos. NO_FEASIBLE_PLAN seulement si toutes configurations réellement admises ont une preuve d'impossibilité ; sinon blocage de revue, pas impossibilité globale.

## 5. Composition scientifique et statut public

Le registre v2 charge des sources pinées et un snapshot effectif propre (`initial-plan-effective-catalogue/1.0.0@sha256:<digest>`), conservant version/hash de chaque source canonique. Il applique seulement les admissions de la curation et le delta G17 aux réalisations qualifiées. Les quatre candidats verticaux retenus restent hors affectation ; UNKNOWN n'est jamais crédit0. Pas de réattribution de séries historiques.

G17 : disponibilité matérielle ne confirme pas trajectoire/poignée/écartement. Sans confirmation de la réalisation qualifiée, aucun vecteur nouveau effectivement utilisable. Le résolveur pull reste inchangé ; v2 trace séparément la qualification requise. Aucun dosage hypertrophique quantifié déduit du delta qualitatif.

Affectation déterministe globale distincte par intention, réutilisant match_distinct avec ordre explicite compatible/préférence confirmée puis ID ; règle de reproductibilité, pas classement biologique. Toute version de sélection reste PROPOSED jusqu'à revue/admission. Les sept intentions/cadences2/3 sont conservées ; autres cadences connues → hors champ à revoir, pas données manquantes.

Statuts v1 inchangés : conflits requis/utilisés → CONFLICTING_DATA ; manques → INSUFFICIENT_DATA ; politiques non admises → POLICY_UNAVAILABLE ; impossibilité prouvée → CONSTRAINT_UNSATISFIABLE ; autres bloqueurs → REVIEW_REQUIRED ; READY seulement si toutes gates réelles acquises. Aucun code public inventé ou champs inconnus dans used_fields. TIME_UNCERTAIN et COMPATIBILITY_UNKNOWN gardent leur sens.

Un READY v1 peut structurellement porter CALIBRATION_REQUIRED avec charge null : le schéma ne valide pas le protocole de démarrage à sa place. Notre admission doit donc prouver le parcours de calibration et sa compatibilité temporelle pour ce mode ; elle ne déclare pas qu'une charge kg doit être connue pour tout premier plan. Pour un réglage non représentable, pas de faux HISTORY_SUPPORTED. FirstPlanClient et schémas partagés restent intacts ; futur runtime demande son autorité propre.

Les bloqueurs sont déterminés par **le mode de départ**, sans exiger un « vrai RIR » mesuré :

- `OBSERVED_REFERENCE` : CALIBRATED au sens limité ci-dessus et masse externe représentable permettent HISTORY_SUPPORTED comme référence d'essai. `effort_sufficiency=UNKNOWN` est une limite de confiance, pas un bloqueur universel : cible2RIR reste une intention, jamais une mesure acquise. Toute règle voulant déduire un ajustement de l'effort inconnu reste indisponible ; ce protocole n'en exécute aucune.
- `BOOTSTRAP_PROTOCOL` : NEEDS_CALIBRATION, sans épisode actif/problème non résolu, peut porter CALIBRATION_REQUIRED/load null dans un futur READY **seulement** si le vrai registre admet le protocole d'entrée pour la population/réalisation, disponibilité et contexte requis confirmés, bornes temporelles incluant préparation/essais réellement soutenues, et toutes autres gates dose/sélection/exposition/contraintes acquises. Aucun nombre maximal d'essais inventé pour obtenir cette borne. Ces conditions ne sont pas acquises par ce dossier.
- Un épisode CALIBRATION_IN_PROGRESS, UNAVAILABLE, motif non résolu ou base de reprise absente bloque ce mode de départ ; après admission générale éventuelle, CONSTRAINT_VIOLATION explique ce blocage de protocole, sans dire que toutes séances sont impossibles. Temps de bootstrap non soutenu → TIME_UNCERTAIN. Les manques/conflicts des nouveaux faits restent dans le sidecar ; ils ne sont pas faussement déclarés champs Blueprint requis manquants.

Par défaut, bundle non admis : POLICY_UNAVAILABLE dans tous ces cas lorsque les inputs v1 sont suffisants. La distinction ci-dessus prépare une vraie admission, sans fabriquer son autorité.

## 6. Gates et préparation de l'admission suivante

Le build autorisé ultérieurement doit exercer les dix familles Phase D sur le vrai successeur et générer ses sorties non-READY/diagnostics. Sourcepins, versions et empreintes permettent le rejeu. Aucun remplacement des onze fixtures v1 par les nouveaux résultats.

Admission complète exige : définition opérationnelle de calibration acceptée et revue, admissibilité dose/sélection/projection, bases temporelles applicables avec validation ou hypothèses produit réellement acceptées, snapshot complet/fingerprint, contraintes et toutes sessions. Si une seule manque : NOT_ADMITTED, NOT_SERVED, READY_NOT_PRODUCED, avec le plus petit bloqueur identifié. Préparer SCI-P02-INITIAL-POLICY-ADMISSION comme paquet de gates après build/revue ; aucune nouvelle investigation muscle par muscle sans bloqueur de candidat démontré.
