# SCI-P01 / SCI-P02 — audit de départ et preuve scientifique

5 novembre 2026. Base90da846 ; branche `spec/sci-p01-p02-blueprint-first-plan`. Audit de fichiers et appels de fonctions pures, sans lecture d'un compte réel. Le [relevé reproductible](audit_repo.json) épingle SHA-256, résultats et18 gabarits. Le manifeste recopié est identique au blob de la PR353 à2ba9fd4 ; la base canonique ne le contenait pas encore. Le code mobile de cette PR n'est pas une dépendance exécutée.

## État réellement servi

| Surface / autorité | Inputs et sorties actuels | Limite pour SCI-P01/02 |
|---|---|---|
| `training_preferences.get_training_preferences` | Cadence1–7 ; priorités ordonnées aux6axes radar ; familles et objets concrets nullable, absence≠vide | Ni expérience, ni temps disponible utilisateur, ni nouvel objectif ; pas de doctrine de sufficience du premier plan |
| `User` / `BodyMeasurement` / `body_profile` | Profil taille/poids non datés ; mesures corporelles datées/partielles ; consentement et retrait | Un poids User ne devient pas une mesure datée. `created_at` d'une mesure n'est pas `measured_at`. Une saisie n'est pas automatiquement une mesure instrumentale observée par AUREN |
| `user_program_generator.generate_program_tree` | Assemble PPL ou upper/lower depuis reference_split ; tronque le cycle au nombre de séances demandé | Une demande1séance PPL produit Push, pas un plan corps entier. Pas de critère de durée ou de validation scientifique globale ; aucune supériorité intrinsèque de PPL démontrée par cet assemblage |
| `morpho_program_generator.generate_program` / `slot_intent` | Intentions, candidats préférés/replis, trous de couverture/disponibilité/distinctivité ; déterministe | Un ensemble de slots n'est pas une semaine dosée. Ses noms d'intentions ou descripteurs ne prouvent pas une faiblesse anatomique. Ne pas réinjecter une priorité radar comme un diagnostic morphologique |
| `weekly_volume_budget` | Budget11 zones ; somme des baselines héritées148 ; tolérance produit±2 par zone ; cadence ne modifie pas les bandes | 148est une somme de cibles par zone, **pas148séries physiques prescrites ni un besoin physiologique individuel**. La littérature ne valide pas ces11valeurs exactes |
| `weekly_planner` / `weekly_capacity_allocator` / `weekly_set_allocation` | Allocation réelle de séries et répétitions ; capacité souple8exercices/24séries par séance issue de la forme du catalogue ; sources de reps nommées | Pas d'input de temps, d'expérience ou de réponse individuelle. Limites de capacité héritées≠capacité de récupération mesurée. Les replis de prescription sont des conventions |
| `weekly_plan_materialization` + `user_programs._weekly_plan_proposal` / route de création du plan | Proposé dans le web ; matérialisation explicite en brouillon ; statuts ready/partial/constraint_unmet/blocked | READY ici est une complétude de matérialisation historique, **pas READY du futur premier plan scientifique**. Ne pas renommer silencieusement son sens |
| `mobile_read_models.mission_read_model` / `recommendation_v3` | Une mission courante READY/RESUME/NO_MISSION, raisons, alternatives ; reprise prioritaire | Ni contrat de Blueprint ni semaine personnalisée complète. NO_MISSION ne décrit pas automatiquement les champs utilisateur manquants |
| `equipment_model` / `environment_resolution` / `environment_activation` | Exigences conjonctives, alias explicites, feasible/not_feasible/unknown ; substitution autorisée et adaptation | Contexte d'objets absent : porte historique inerte/NON_APPLICABLE au démarrage, pas preuve de faisabilité. Familles génériques≠objets présents. Aucun inventaire n'est requis par le futur contrat |
| `data/sci/exercise_catalogue.json` / `sci_identity` / `sci_exposure` |107 fiches,84CANONICAL et23LEGACY_ALIAS ;15 zones ; identités stables et crédits séparés ;106exigences RESOLVED,1UNKNOWN | Les fiches/identités sont déjà disponibles, mais leur existence ne valide pas une semaine. La chaîne hebdomadaire servie utilise encore11 zones et `set_contribution` ; aucune conversion11→15 implicite |
| PR353 `.../training-preferences/declarations` | Adaptateur JSON de cadence/priorités/familles et consommateur natif, hors base canonique et non déployés lors de l'audit | Source future compatible, pas endpoint SCI-P01/02 déjà servi. Pas de nouvelle ressource `/training-environment` livrée |

## Probes déterministes de la chaîne hebdomadaire existante

`build_weekly_plan(TrainingPreferencesData(...))` puis `assess_materialization`, sans DB :

| Cadence | Familles | Séances | Séries physiques | Statut historique |
|---|---|---|---|---|
| non déclarée | inconnues |0|0|blocked|
|1|inconnues|1|24|partial|
|2|inconnues|2|48|partial|
|3|inconnues|3|72|partial|
|4|inconnues|4|96|partial|
|3|liste explicitement vide|0|0|blocked|

Deux évaluations identiques rendent les mêmes objets/empreintes dans chaque probe. Cela prouve un comportement technique actuel, **pas** que ces doses conviennent à un débutant, à sa durée de séance ou à son environnement. L'inconnu n'est pas une déclaration de salle complète. L'échantillon ne constitue pas un audit de tous les cas et les statuts restent ceux de la politique héritée.

## Audit des archétypes et du catalogue de prescriptions

`reference_split.json` version2026-09-28.v15 contient18 gabarits. Le relevé JSON détaille chaque exercice et son identité scientifique résolue ; aucune identité de gabarit n'est inconnue via le résolveur canonique. L'identité résolue ne prouve ni disponibilité ni dose adaptée.

| Famille | Membres | Constat / admission proposée pour le premier plan |
|---|---|---|
|PPL|push-a/b,pull-a/b,legs-a/b|20–22séries selon gabarit ; modules de séances, pas semaine intrinsèquement validée. Une troncature de cycle peut omettre une région. Revue d'allocation/dose/effort/durée avant éligibilité |
|Upper/lower|upper-pecs-delts,upper-back-arms,lower-quad-bias,lower-posterior-bias|19–22séries selon gabarit ; biais locaux déclarés ; l'équilibre dépend des occurrences hebdomadaires. Pas d'équivalence scientifique de tous les biais |
|Court/spécialisation|short-upper,catch-up-shoulders/arms/back-width|18–20séries ; « 45 min » est un libellé, sans modèle de temps dans la donnée. Un rattrapage ne constitue pas un premier plan global |
|Full-body morphotype|full-body-morphotype-priority-v1|24séries/8exercices ; le nom ne démontre pas que le morphotype prédit ce plan. Revue de la justification et des inputs requis |
|Sans matériel|no-equipment-full-body|12séries/4exercices ; note explicite : aucun tirage sans barre n'a été inventé. Lacune de tirage à expliciter ; ne pas certifier un plan équilibré par son nom |
|Cardio/abdos|liss-only,liss-abs|Pas des archétypes initiaux complets d'hypertrophie. Ne pas détourner le premier plan vers un objectif cardio |

Le catalogue ne contient pas de durée/modèle de repos/effort individualisé attachés à ces gabarits. Le repos90s du client vient de `console_state.REST_FALLBACK_SECONDS`, une suggestion héritée, pas une mesure de durée ni une recommandation universelle d'hypertrophie.

Neuf noms ont plusieurs plages de répétitions **en considérant toutes les lignes de cibles**. Ce comptage n'est pas identique au mécanisme historique `_catalog_rep_ranges`, qui examine la première ligne de chaque occurrence : le commentaire « huit » ne doit pas être utilisé comme résultat recalculé. Le relevé conserve les plages ; aucun conflit n'est tranché ici.

**Verdict : aucun gabarit n'est promu silencieusement en archétype approuvé pour le premier plan.** Ils restent utilisables par les fonctions historiques. Le prochain examen de dose doit relier une politique explicite à des profils d'usage, sans déduire un seuil biologique des habitudes du catalogue.

## Recherche limitée et statut de lecture

Ces sources cadrent les contrats, pas une nouvelle formule de prescription. Registre existant `data/sci/evidence_registry.json` réutilisé par référence ; aucune entrée historique réécrite. Les références E01–E05 ci-dessous sont des **fiches de revue du présent paquet**, pas un deuxième registre moteur.

| Fiche / registre existant | Source primaire vérifiée | Lecture / conclusion utilisable / limite |
|---|---|---|
|E01 / EV-04|[Currier et al., ACSM 2026](https://pubmed.ncbi.nlm.nih.gov/41843416/), DOI10.1249/MSS.0000000000003897 ; [annonce ACSM](https://acsm.org/science-spotlight-acsm-releases-new-position-stand-on-resistance-training/)|Résumé/notice et annonce lus ; texte intégral PMC/publisher non accessible dans cette passe. Revue de revues chez adultes en bonne santé, recherche jusqu'à octobre2024. Soutient une progression et l'importance du volume ; ne valide pas les baselines11 zones, un nombre de séries par kg ou une prédiction personnelle exacte |
|E02 / EV-01,EV-11|[Pelland et al.,2026](https://pubmed.ncbi.nlm.nih.gov/41343037/), DOI10.1007/s40279-025-02344-w, publié en ligne4décembre2025 puis volume56février2026|Résumé/notice lus ; méta-régressions volume/fréquence, effets de groupe et rendements décroissants. Ne convertit pas une moyenne ou un palier en optimum personnel ; volume et répartition doivent rester distincts |
|E03|[Ramos-Campo et al.,2024](https://pubmed.ncbi.nlm.nih.gov/38595233/), DOI10.1519/JSC.0000000000004774|Résumé PubMed complet lu ;14études/392participants, pas de différence significative split/full-body quand le volume est égalisé. Le nom d'un split ne justifie pas sa supériorité ; les contraintes de calendrier comptent |
|E04 / EV-54|[Singer et al.,2024](https://www.frontiersin.org/journals/sports-and-active-living/articles/10.3389/fspor.2024.1429789/full), DOI10.3389/fspor.2024.1429789|Sections méthodes/résultats/discussion/conclusion consultées ; petit avantage possible de repos plus longs, avec incertitude et durées d'études courtes. Aucun repos90s universel et aucune durée totale précise dérivée du seul nombre de séries |
|E05|[Robinson et al.,2024](https://pubmed.ncbi.nlm.nih.gov/38970765/), DOI10.1007/s40279-024-02069-2|Résumé/notice lus ; association exploratoire entre proximité de l'échec estimée et hypertrophie, relation exacte incertaine. Pas de charge initiale ou de RIR personnel déduit de la taille/du poids/du niveau déclaré |

Aucune revue exhaustive des prédicteurs anthropométriques n'est réalisée : **les sources consultées ne justifient pas une formule de volume ou de charge depuis taille/poids**, ce qui motive ici une règle de retenue, pas une démonstration que ces mesures n'ont aucun usage. Une proposition de prédiction anthropométrique exigerait sa propre revue. Aucune preuve concurrentielle/benchmark commercial n'entre dans ces conclusions.

## Tensions à garder visibles

- Le manifeste classe taille/poids au premier niveau de compréhension. La proposition les garde utiles/progressifs mais ne les impose pas comme bloqueurs universels d'un plan : cela demande acceptation produit, sans prétendre que la science les rend obligatoires.
- La V2 impose15 zones et la distinction preuve/origine ; la chaîne servie11 zones reste inchangée. Le contrat nouveau nomme cette dépendance au lieu de sommer des unités incompatibles.
- Un changement de politique de dose, temps ou compatibilité est un futur build scientifique ; le contrat et ses tests ne l'autorisent pas.
