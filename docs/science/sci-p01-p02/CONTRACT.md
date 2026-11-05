# SCI-P01 / SCI-P02 — contrat proposé v1.0.0

5 novembre 2026. Périmètre isolé approuvé : « Valider les contrats et tests isolés ». Ce contrat ne sert aucune route et ne valide aucune nouvelle politique de prescription. Les schémas sont générés depuis `tools/science_contracts/blueprint_first_plan_v1.py`. Leur acceptation structurelle ne remplace ni preuve scientifique, ni ownership/consentement, ni validation des règles par le producteur.

## 1. SCI-P01 : snapshot et profil d'exigences

`Blueprint.contract_version = body-training-blueprint/1.0.0`. Les clés sont obligatoires pour que l'inconnu soit explicite ; cela ne rend pas obligatoire la collecte de leurs valeurs. `snapshot_id` identifie le snapshot, pas une personne ou une décision.

`Fact[T]` : `state`, `value`, `provenance`, `conflicts`.

- KNOWN : valeur typée et source non vide ; aucun défaut issu de population ne devient une disponibilité ou mesure personnelle.
- UNKNOWN : valeur null. `KNOWN []` signifie une déclaration explicitement vide ; ce n'est pas UNKNOWN.
- CONFLICT : valeur principale null, au moins deux valeurs distinctes et deux références de source distinctes. Une référence doit identifier la version/occurrence source, pas seulement le nom vague d'une table.
- WITHHELD : donnée non utilisée, valeur null ; le payload ne transporte pas une valeur corporelle retirée derrière ce statut.

Provenance : `origin` sépare USER_REPORTED, USER_OBSERVED, DERIVED_FROM_HISTORY, POPULATION_PRIOR, PRODUCT_CONTRACT et UNKNOWN ; `acquisition` distingue DECLARED, SELF_MEASURED, DEVICE_MEASURED, EXECUTION_LOG, DERIVED et UNKNOWN. `source_ref`, `recorded_at`, `measured_at` sont séparés. Une date absente reste null. Une provenance postérieure à l'instant d'évaluation est refusée.

Ce vocabulaire local explicite les deux axes de la doctrine V2 ; il ne remplace pas les enums historiques. MEASURED du manifeste peut correspondre à une acquisition SELF_MEASURED d'origine USER_REPORTED : le système sait qu'une mesure a été déclarée, sans feindre l'avoir instrumentée lui-même. OBSERVED correspond à une observation sourcée ; INFERRED à une interprétation explicitement signalée. La **base de preuve d'une règle** (STUDY_MEASURED/DERIVED/CONVENTION/UNKNOWN dans la V2) reste dans sa règle/son registre, distincte de l'origine d'une valeur utilisateur.

### Profil `first-bodybuilding-inputs-v1-proposed`

Ce profil de suffisance est versionné séparément de la dose. Il est proposé pour des adultes dans un usage bodybuilding non clinique ; il n'est pas un questionnaire médical ni une preuve d'aptitude. Une autre population nécessite une politique distincte.

| Champ | Valeur nécessaire à la suffisance de ce profil ? | Utilité / source canonique / absence |
|---|---|---|
|objective|Oui ; HYPERTROPHY, fixé par le produit ou confirmé par l'utilisateur|Le domaine AUREN est acquis. Ne pas proposer un objectif multisport. Sous-objectifs esthétiques ou recomposition ne déclenchent pas une nouvelle formule de dose dans v1 |
|population_scope|Oui ; ADULT_NON_CLINICAL explicitement sourcé|La recherche d'ancrage concerne des adultes sans indication clinique. Le produit doit définir son éligibilité ; aucune date de naissance ou absence de maladie n'est devinée |
|sessions_per_week|Oui ; entier1–7 déclaré|Source existante training_preferences ; borne structurelle de semaine, pas optimum scientifique. Aucune cadence inférée de l'historique |
|session_budgets_minutes|Oui ; un entier positif par séance|Disponibilité réellement déclarée ; pas de source serveur utilisateur existante. Une cible de durée d'un programme n'est pas ce fait. Liste alignée sur la cadence quand les deux sont connus |
|limitations|Oui ; réponse explicite, éventuellement liste vide|NONE_REPORTED s'exprime KNOWN[] ; absence de réponse=UNKNOWN. Vocabulaire et résolution des limitations restent à approuver côté producteur. Pas de diagnostic médical depuis la gêne déclarée |
|experience|Progressif ; inconnu possible seulement avec politique de démarrage adaptée|REPORTED_UNTRAINED/REPORTED_TRAINING/RETURNING_AFTER_BREAK sont des états descriptifs, sans seuil d'années inventé. Pas de champ persistant équivalent dans User/TrainingPreferences. Historique et familiarité peuvent guider la calibration ; pas de charge prédite par catégorie |
|height_cm|Non universellement bloquant|User.height_cm ou mesure identifiée ; date inconnue conservée. Peut contextualiser suivi/proxy ou réglage ergonomique confirmé ; ne détermine pas dose, bras de levier osseux ou exercice optimal |
|weight_kg|Non universellement bloquant|BodyMeasurement.weight_kg avec measured_at et consentement applicable. Utile pour suivi longitudinal et contexte d'exercices au poids du corps ; aucune conversion en charge initiale ou séries/kg |
|legacy_weight_kg|Jamais une mesure datée implicite|User.weight_kg isolé, measured_at obligatoirement null. Ne pas l'exporter dans weight_kg avec une date fabriquée. Sa présentation native reste une décision produit/données distincte |
|declared_priorities|Facultatif, ordre conservé|Six axes canoniques de training_preferences, sans doublons. Souhait déclaré, pas déficit anatomique ni critère unique ; aucune obligation de remplir les6axes |
|excluded_exercise_ids|Facultatif ; strict si connu|Identités canoniques interdites par l'utilisateur. Une sélection ne peut les contourner au nom d'une priorité. Pas de nouvel endpoint de préférences d'exercices créé ici |
|observations|Facultatif|Tendance de mesure, tendance d'exécution ou rapport fonctionnel, avec Fact et interprétation OBSERVED/INFERRED. Aucun champ « faiblesse déclarée=observation objective » |
|environment|Pas d'inventaire requis|Description de contexte, objets éventuellement connus et confirmations d'exercices en contexte. Inconnu reste inconnu ; ne pas transformer un nom de chaîne de salles en liste complète |

Le profil corporel reste progressif : le manifeste rend taille/poids utiles dès l'entrée, mais les sources revues ne justifient pas d'en faire des prérequis universels de prescription. Cette décision de suffisance ne supprime pas les mesures ni les consentements du produit.

Un ratio dérivé ou un descripteur morphologique existant ne constitue pas une faiblesse musculaire objectivement établie. `morphology_profile` utilise notamment des heuristiques de ratio/seuil et des « priority_candidate » : elles ne sont pas admises comme observations cliniques ou prédicteurs individuels de réponse dans ce premier plan. Une observation à utiliser doit décrire sa mesure/performance, son contexte, son incertitude et sa méthode ; la causalité ne se déduit pas d'une corrélation temporelle.

## 2. SCI-P02 : entrée déterministe

`FirstPlanRequest` contient contrat/version, `as_of` explicite, profil d'exigences, Blueprint, références de politiques et versions. Les références de dose, temps, sélection et projection taxonomique peuvent être absentes ; `Policies.state` ne les rend pas approuvées par déclaration.

`ReferenceSnapshot` est fourni par le **producteur de confiance**, jamais par un corps de requête utilisateur : version du catalogue, IDs canoniques et intentions existantes, références de preuves, objets valides, exercices réellement sans matériel et IDs des politiques approuvées. Le validateur exige ce contexte ; aucun IO ou accès à une DB n'est caché dans les DTO. Le futur adaptateur doit construire ce contexte depuis des sources versionnées autoritaires.

Les15 zones de la V2 et la politique `sci-exposure-credit-v1` sont nommées explicitement. Les DTO ne projettent pas le budget11 zones en15 zones. Une politique de projection doit être fournie et revue avant READY ; un nom tel que `posterior` ne passe pas pour une des15 zones.

### Identité et répétabilité

`decision_fingerprint(request)` est SHA-256 du contenu JSON canonique : clés triées, UTF-8 et séparateurs fixes ; snapshot_id événementiel exclu ; listes de limitations/exclusions/objets triées, priorités et budgets conservés dans leur ordre sémantique. `as_of` est une entrée de décision, pas une horloge implicite. Aucun identifiant d'événement, UUID aléatoire ou horodatage généré ne se substitue à cette empreinte. Changer le contexte/version change le contenu ; deux appels identiques n'impliquent pas un nouvel apprentissage.

### Pipeline normatif futur — aucune dose fabriquée

1. Valider les faits et leurs conflits ; évaluer le profil d'inputs, puis les valeurs supplémentaires réellement utilisées.
2. Résoudre les politiques et leurs versions depuis le registre de confiance ; relever les capacités manquantes du producteur.
3. Appliquer les contraintes dures avant souhaits ou départages : population d'usage, cadence, budgets, exclusions/limitations explicites, faisabilité connue.
4. Choisir uniquement parmi des archétypes dont l'admission à ce profil a été revue. Les18 gabarits hérités constituent des sources auditées, pas une liste admise sans examen.
5. Allouer le travail hebdomadaire selon la politique approuvée : séries physiques séparées des expositions par zone et rôle ; source de chaque dose/répétition/effort/repos. Pas de minimum efficace personnel ou maximum récupérable inventé.
6. Composer les intentions et candidats canoniques ; alias tracés par le résolveur, pas de doublon d'identité maquillé en variété. Un ordre final par ID stable est un départage technique, pas une supériorité physiologique.
7. Résoudre les incompatibilités ou demander une confirmation/substitution **sur l'exercice**, sans imposer un inventaire. Une confirmation passée ne vaut pas disponibilité actuelle ; la politique de validité contextuelle/temporelle reste à construire.
8. Tester la durée selon un modèle revu. Séparer budget utilisateur, estimation avec bornes et durée réellement exécutée. L'estimation doit référencer ses composantes (travail, repos, échauffement, transitions, contexte) via le modèle ; pas de durée prédite par un nombre de séries multiplié par une constante improvisée.
9. Expliquer la décision, ses sources, ce qui n'a pas été utilisé et ce qui reste inconnu. Les versions et la prescription historique devront rester conservées lors d'une future persistance ; ne pas recalculer silencieusement une ancienne recommandation.

## 3. Sortie et statuts

`FirstPlanRecommendation.contract_version = first-plan-recommendation/1.0.0`. Champs : request_fingerprint, status, engine_version, assessment, issues, used_fields, candidate_plan, confidence.

Ordre de priorité, avec **tous les bloqueurs listés** :

| Statut | Sens et action attendue |
|---|---|
|CONFLICTING_DATA|Un fait requis ou utilisé a des valeurs contradictoires ; résoudre la source, sans dernier-gagne arbitraire |
|INSUFFICIENT_DATA|Un fait requis/utilisé manque ou est non utilisable. `assessment.missing_fields` nomme exactement les faits ; aucune demande d'inventaire ou de mesure inutile pour cacher une lacune moteur |
|POLICY_UNAVAILABLE|Inputs évaluables mais dose/temps/sélection/projection ou implémentation/version moteur indisponibles/non approuvés. Ce n'est pas une insuffisance personnelle |
|CONSTRAINT_UNSATISFIABLE|Politiques disponibles, aucune solution ne respecte les contraintes dures selon une évaluation du producteur ; pas de candidat exécutable. UNKNOWN matériel ne prouve pas cette impossibilité |
|REVIEW_REQUIRED|Candidat encore incertain/incomplet, compatibilité ou durée à confirmer ; aucune activation implicite. Proposer clarification/substitution en contexte |
|READY|Plan revu, politique et moteur identifiés, cadence/budgets respectés, chaque slot résolu, prescription complète/traçable, expositions complètes et faisabilité connue au niveau requis |

`used_fields` référence les faits scalaires dont les valeurs ont été consommées. Un champ facultatif non utilisé peut rester conflictuel sans bloquer. Une absence consultée pour choisir une branche de démarrage doit rester décrite comme absence dans l'explication/limitations de politique ; elle ne constitue pas une valeur personnelle consommée. La provenance de contexte/compatibilité suit les confirmations et les références des candidats, pas un fait d'équipement inventé.

Le plan candidat porte archétype/révision, sessions/slots, prescription par slot, durée, comptabilité physique et exposition15 zones. Un candidat matériel UNKNOWN ne peut pas porter une faisabilité CONFIRMED. NOT_REQUIRED exige que le catalogue confirme réellement l'absence d'exigence externe ; ce n'est pas le repli d'une exigence inconnue. Une confirmation AVAILABLE/UNAVAILABLE exige une origine USER_REPORTED ou USER_OBSERVED, une acquisition DECLARED/DEVICE_MEASURED/EXECUTION_LOG, une source et une date d'enregistrement. Le contexte matériel connu ne peut pas provenir d'un prior de population ni d'une convention produit. Des confirmations AVAILABLE et UNAVAILABLE dans le contexte courant restent un conflit à résoudre : aucune compatibilité CONFIRMED/NOT_REQUIRED ne peut le masquer. Les alternatives ont leur propre ID, contexte, verdict et provenance ; le consommateur ne transforme pas une alternative UNKNOWN/UNAVAILABLE en choix garanti.

Chaque slot conserve l'intention, le sélectionné et les alternatives, la règle de substitution, la prescription et sa raison. Futur démarrage/substitution : garder planifié, proposé et exécuté distincts ; pas de transfert de charge entre exercices non justifié ; utiliser les gardes canoniques de série déjà effectuée, propriétaire et pending/refus/confirmé. Les DTO ne modifient aucune de ces règles.

`work_sets`, reps, RIR, repos et charge nullable ont des sources explicites. CALIBRATION_REQUIRED n'est pas une charge connue ; null ne veut pas dire0kg ou échec imposé. Sans effort/repos soutenus par politique et temps modélisé, aucun READY. Une constante héritée conservée pour un exemple n'est pas promue en politique approuvée.

L'exposition sépare raw_primary_sets/raw_secondary_sets/unknown_role_sets et credited_sets/bound. UNKNOWN ne devient jamais0 ; un rôle inconnu empêche EXACT. Les15lignes exactes sont requises quand exposure_complete est affirmé. La vérification du contenu des rôles, des crédits appliqués et de toutes les contraintes reste une obligation du producteur : un DTO valide n'est pas un audit scientifique de ses déclarations.

## 4. Confiance et preuve

Aucune probabilité personnelle, récupération en%, note globale ou nombre décoratif. `confidence.individual_response = NOT_ESTIMATED` au premier plan. `feasibility` est opérationnelle et sourcée, distincte du niveau de preuve général. `evidence_refs` pointe les entrées du registre existant et `limitations` nomme les inconnus. La certitude d'une étude et l'adéquation d'une prescription individuelle ne sont pas interchangeables.

Des inputs supplémentaires peuvent améliorer la résolution de contraintes ; ils n'augmentent pas automatiquement une confiance physiologique. Perdre une donnée ne crée aucune preuve. Aucune interprétation anatomique, médicale ou psychologique depuis une priorité choisie.

## 5. Validation et limites d'intégration

Les JSON Schemas sont autonomes pour la **structure**. Les invariants transversaux (empreinte, références, statuts, sommes, provenance contextuelle et READY) sont vérifiés par `validate_exchange` avec ReferenceSnapshot. Un client qui n'exécute que JSON Schema ne doit pas certifier ces garanties transversales ; elles doivent être appliquées par le futur producteur serveur.

Les 8 fixtures contiennent uniquement des données synthétiques et un extrait historique explicitement non validé. `sufficient` peut légitimement rendre POLICY_UNAVAILABLE. Il n'existe volontairement aucune fixture affirmant READY pour un vrai plan ou une politique réellement approuvée dans cette passe. Ce manque est une dépendance du moteur, pas un défaut masqué par un faux exemple. Les branches futures font partie du schéma et de leurs gardes ; elles devront obtenir une fixture READY depuis le vrai producteur avant intégration mobile.

Aucune route SCI n'est servie. Aucun stockage Blueprint ou recommandation, migration, UI ou algorithme de prescription n'est ajouté. Les lieux de persistance et permissions des futurs champs devront être proposés par l'API/architecte. Le moteur conserve sa responsabilité ; l'interface présente le résultat et les inconnus.
