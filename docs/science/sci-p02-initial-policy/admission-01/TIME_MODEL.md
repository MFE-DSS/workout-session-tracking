# SCI-P02-ADMISSION-01 — faisabilité temporelle1.0.0

6 novembre2026. `initial-rest-floor/1.0.0`, diagnostic isolé testé, NOT_SERVED. **Admission de la borne arithmétique seulement ; aucun modèle de durée totale ni de faisabilité positive admis.** Sources et niveau de lecture dans[EVIDENCE.md](EVIDENCE.md).

## Signaux séparés

A. Prescription : nombre de séries, répétitions et repos ; préparation spécifique à définir. On connaît les répétitions prescrites, pas leur durée. Le tempo compatible avec hypertrophie n'est pas un modèle prédictif de cadence.
B. Opérations : réglage/chargement, déplacement, attente, familiarisation. Pas de défaut en secondes ; certaines opérations peuvent chevaucher le repos, donc ne pas sommer aveuglément.
C. Exécution personnelle : durées horodatées réellement observées par événement et contexte, absentes ici. Une moyenne de laboratoire n'est pas une observation de cet utilisateur.

## Options évaluées

| Option | Décision | Justification |
|---|---|---|
| A point exact | REJECT | Composantes inconnues ; donner47min fabriquerait de la précision |
| B intervalle total | INSUFFICIENT_EVIDENCE | Borne haute non établie. Une borne de repos n'est pas un intervalle total. Aucune borne de tempo déduite des études d'efficacité |
| C classification conditionnelle | ADMIT_WITH_LIMITS | Peut réfuter un budget structurellement trop court pour cette configuration ; sinon conserve UNKNOWN |
| D calibration personnelle | PROPOSED_FUTURE | Pourrait produire des intervalles contextualisés après validation de couverture/prédiction ; pas moteur construit ni seuil d'échantillon arbitraire |

## Entrées, calcul et sens

`assess_time(session, budget_minutes, structure)` lit les slots du vrai diagnostic1.0.0 sans le modifier. Séries entières positives, repos entier positif ou absent ; budget entier positif ou absent. Il refuse zéro, booléen, fraction, infini ou NaN là où un entier est requis. Une séance vide n'a pas de preuve de faisabilité.

Sous **TRADITIONAL_SEQUENTIAL**, tous les sets d'un slot sont réalisés avant le suivant, sans exécuter un autre exercice pendant le repos :

`R_known = Σ_slots_with_known_rest max(work_sets−1,0) × rest_seconds`.

Pas de repos ajouté après la dernière série d'un slot, pas de repos entre exercices déduit. Un repos manquant ne devient pas0 : la somme est explicitement partielle. Comme le travail prend strictement du temps positif et que les autres composantes n'ont pas de durée négative, `T_total > R_known`, sous respect de cette prescription. L'égalité du budget à la borne est donc déjà insuffisante. Il ne s'agit pas d'un minimum physiologique imposé à toute autre séance.

Exemple de test, **pas une prédiction d'utilisateur** :4slots×2sets×120s +3slots×2sets×90s →750s de repos intramouvement (12,5min). Budget≤12,5min exclut cette configuration ; budget75min ne la certifie pas. La proportion mono/poly dépend de l'exercice sélectionné, pas du nom d'intention. Unilatéral, calibration et échauffement restent non chiffrés.

Superset/appairage/structure inconnue : aucune somme séquentielle applicable ; `known_rest_floor_seconds=null`, UNKNOWN. Il serait faux d'appliquer la réduction moyenne37% de la méta-analyse à ces sept exercices. Densité (travail/temps) n'établit pas une compatibilité individuelle ni une limite d'attente.

## Sortie et contrat v1

- Budget≤R_known : feasibility NOT_FEASIBLE, issue CONSTRAINT_VIOLATION, scope THIS_CONFIGURATION_ONLY. Aucune affirmation qu'aucun autre plan n'existe. Le statut global CONSTRAINT_UNSATISFIABLE demanderait d'avoir évalué toutes les configurations admises.
- Budget absent ou supérieur : feasibility UNKNOWN, issue TIME_UNCERTAIN ; jamais LIKELY_FITS ni CONFIRMED.
- Durée : UNKNOWN, bornes/model_ref null, même si le diagnostic séparé expose R_known. `Duration` v1 interdit une borne seule sous UNKNOWN et exige deux bornes justifiées sous ESTIMATED. **Cette distinction ne peut donc pas être portée comme durée chiffrée v1.** Diagnostic interne seulement ; v1 et mobile restent inchangés. Une projection future devrait être proposée/revue avant modification du schéma.

Le producteur1.0.0 reste POLICY_UNAVAILABLE, avec TIME_UNCERTAIN selon les règles existantes. L'artefact0.2.0 n'est pas chargé dans ses références approuvées. Quand une politique complète sera admise mais son contexte temporel incertain, REVIEW_REQUIRED + TIME_UNCERTAIN reste le repli v1, sans candidat démarrable. Confiance individuelle NOT_ESTIMATED ; certitude de l'arithmétique n'est pas confiance dans le temps de séance.

## Condition nécessaire d'une future faisabilité positive

Un protocole doit identifier ce qui est inclus, les horaires/pauses/échauffements, la prescription et sa structure, l'expérience et le contexte ; produire des bornes conditionnelles et leur validation, inclure une procédure quand le budget risque d'être dépassé, sans raccourcir silencieusement repos ou intentions. La préparation spécifique et la calibration doivent être réalisables dans ce protocole. Données d'exécution consenties, contrôles de qualité et dérive de contexte sont nécessaires avant une personnalisation.

Il n'est pas demandé de garantir l'absence d'une interruption arbitraire. Une estimation conditionnelle pourrait suffire à un futur READY si elle est empiriquement soutenue et son contexte applicable. Aucune étude consultée ne valide aujourd'hui cette estimation pour le bundle AUREN ; exiger une borne absolue de toute attente serait également un objectif erroné.
