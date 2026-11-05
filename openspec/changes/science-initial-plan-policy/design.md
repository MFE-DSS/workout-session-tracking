# Politique initiale SCI-P02 — design pour revue

5 novembre 2026. Version `initial-hypertrophy-policy/0.1.0-proposed`. **Non implémenté, non servi, non approuvé.** [Audit/evidence](../../../docs/science/sci-p02-initial-policy/EVIDENCE_AND_AUDIT.md), [tests](test-specification.md), [décisions](../../../docs/science/sci-p02-initial-policy/DECISIONS_AND_HANDOFF.md).

## Brainstorming / Options / Risques / Choix retenu

1. Admettre tous les gabarits hérités : rapide, mais PPL tronqué, dose24séries/séance, cardio imposé et absence de durée justifiée. Écarté.
2. Optimiser personnellement volume et physique dès le premier plan : exige des observations/réponses individuelles absentes ; risque de pseudo-précision. Différé.
3. Producteur initial isolé, déterministe et borné ; conventions visibles et sorties de revue tant que contexte/temps ne sont pas justifiés : **proposition retenue pour revue**, conforme au mandat. L'opérateur n'a pas encore approuvé les paramètres ci-dessous.

## 1. Autorités et architecture

Le manifeste canonique v1 reste directeur ; les contrats `body-training-blueprint/1.0.0`, `first-plan-request/1.0.0`, `first-plan-recommendation/1.0.0` sont inchangés. Le producteur proposé `produce(request, *, bundle, references)` serait une fonction pure dans un nouveau module dédié. Il utilise `decision_fingerprint`, `input_assessment` et `validate_exchange` existants ; pas de copie de leurs règles.

Le bundle scientifique de confiance contient des registres séparés dose, temps, sélection, attribution15zones et preuves ; jamais transmis comme autorité dans un JSON utilisateur. Un identifiant déclarant APPROVED ne suffit pas : vérifier l'appartenance aux références approuvées, leur contenu/hashes et leur revue. Tout bundle manquant/non approuvé rend POLICY_UNAVAILABLE, même si les données utilisateur sont suffisantes.

L'archétype proposé est neuf (`initial-full-body-seven-intents-v1-proposed`), sans prescription héritée. Aucun des18gabarits actuels n'est admis automatiquement ; ils restent utilisés par leurs parcours historiques. Les preuves de split/full-body ne démontrent pas une supériorité propre au nouveau design.

## 2. Inputs nécessaires et données progressives

**Scientifiquement défendable :** un travail de résistance peut soutenir l'hypertrophie sans connaître poids/taille, mais aucune étude ne fixe tous les champs obligatoires d'une application. **Contrat opérationnel v1 existant :** objectif HYPERTROPHY, population ADULT_NON_CLINICAL explicitement déclarée, cadence, un budget par séance et réponse sur les limitations (KNOWN[] si aucune rapportée). Ce profil n'est ni examen médical ni preuve d'aptitude. Propriétaire, consentement et origine du snapshot relèvent de l'adaptateur futur.

Poids/taille restent facultatifs : pas de charge initiale calculée depuis anthropométrie, pas de date inventée pour User.weight_kg. Expérience UNKNOWN reste UNKNOWN, sans catégorie « débutant » induite ; le démarrage utilise une calibration et n'annonce aucune dose optimale personnelle. Une expérience déclarée/historique ne déclenche pas un multiplicateur arbitraire. Priorités facultatives = souhaits, pas faiblesse ni preuve causale.

Population hors champ : rejet structurel/admission en amont, car v1 ne représente que ADULT_NON_CLINICAL ; ne pas forger une sortie de revue sur un Blueprint invalide. Limitations non résolues dans une requête v1 valide : revue, sans diagnostic. Une limitation déclarée n'est pas automatiquement une impossibilité de s'entraîner ; ne rendre NO_FEASIBLE_PLAN que si une contrainte explicite et vérifiable élimine effectivement tous les plans du périmètre admis. Les nouveaux inputs ne sont pas persistés dans cette tranche.

## 3. Proposition chiffrée de démarrage, à approuver

Ceci est une **convention initiale proposée**, ancrée dans des plages de pratique étudiées ; pas un minimum biologique, optimum individuel, ni politique déjà admise. Les études ne prouvent pas la combinaison exacte de tous ces choix.

| Paramètre proposé | Valeur / règle | Nature et justification | Gate |
|---|---|---|---|
| Cadence admise au premier build | 2 ou3séances déclarées/semaine | Sous-ensemble de livraison borné ; pas seuil physiologique. Les autres cadences connues sont à revoir, pas « données manquantes » | D1 |
| Répartition | Même couverture corps entier à chaque occurrence, ordre fixé ; variation seulement après politique distincte | Simplicité/reproductibilité ; pas supériorité intrinsèque sur split à volume égal | D1 |
| Travail | 2séries de travail par intention et occurrence | Point de départ proposé dans les plages multi-séries ; pas héritage des148cibles/24séries ni minimum efficace établi | D2 |
| Répétitions | 8–12 par série | Plage pratique issue de recommandations historiques, pas exclusivité hypertrophique ni RM mesuré | D2 |
| Effort | cible2.0RIR, charge null, CALIBRATION_REQUIRED | Convention à faire revoir ; étude1–2RIR chez sujets entraînés ne valide pas sa précision chez un novice. Aucune charge %poids/1RM prédite | D2 |
| Repos | 120s pour polyarticulaire ; 90s pour isolation | Durées de départ proposées, non optimum universel ; jamais raccourcies pour faire entrer artificiellement le plan | D2 |
| Priorités | Ordre des accessoires déjà présents/tie-break, sans ajout de séries ni retrait de couverture | Préférence explicite ; aucune analyse de points faibles. Si priorité non couverte directement, le dire | D3 |

Les sept intentions proposées ciblent : quadriceps, chaîne de hanche (ischios/glutes), presse pectorale, tirage horizontal, tirage vertical, deltoïde latéral, mollets. À2séances :28séries physiques ; à3 :42. Ce sont les sommes de la convention proposée, **pas28/42séries par muscle**, pas recommandation d'un tel volume pour chaque zone. Les crédits de participation sont calculés séparément.

Ordre canonique avant préférence : genou → presse → tirage horizontal → hanche → tirage vertical → deltoïde latéral → mollets. Les accessoires deltoïde/mollets peuvent permuter selon un souhait explicite ; les contraintes et la couverture priment. Pas de duplication d'un même exercice dans une séance ; entre séances, répétition permise pour apprendre/calibrer. Pas de direct bras/abdos imposé dans ce premier sous-ensemble ; contribution indirecte et absence de travail direct restent explicites. Pas de30min d'escalier automatiques repris du catalogue.

## 4. Intentions, candidats et comptabilité

Un registre **dédié au nouveau bundle** définira ces7intentions avec nouveaux IDs neutres. Les12intentions historiques restent intactes ; leurs noms « priority »/« minimum effective dose » ne servent pas de preuve scientifique. Les champs `intent_id` v1 sont des textes validés contre le registre producteur réel : aucun nouveau JSON Schema n'est nécessaire pour ce bundle, mais le ReferenceSnapshot et ses tests doivent inclure ses définitions effectivement approuvées.

Pour chaque intention : ensemble de zones PRIMARY autorisées, mouvement et actions articulaires autorisés, exclusions strictes, candidats tirés seulement des84identités CANONICAL actuelles. Un alias se résout avant comptage, jamais second candidat fictif. Le registre doit conserver la liste exacte des IDs admissibles et leur justification ; **pas de sélection par le seul score historique**. Le pool historique ne trouve, par exemple, aucun candidat pour trunk_core_direct et peut proposer un leg extension dans une intention décrite squat : audit de couverture, pas autorité d'admission.

Filtrage : identité résolue + fiche revue → rôle/mouvement cohérents → exclusions/limitations connues → compatibilité du contexte → distinctivité. Ordre déterministe entre candidats admissibles : confirmation contextuelle, préférence explicite compatible si présente, puis ID canonique lexical. Aucun score numérique de « qualité physiologique » ajouté. Si plusieurs choix ne satisfont pas la distinctivité, recherche d'affectation globale déterministe plutôt que glouton qui affame un slot. Le rang lexical est une convention de reproductibilité, pas un classement d'efficacité.

Le contexte peut rester sans inventaire. Une confirmation sourcée AVAILABLE de l'exercice dans le même context_ref autorise ce candidat ; elle ne prouve pas une salle complète. UNAVAILABLE l'exclut ; UNKNOWN reste à confirmer. NOT_REQUIRED n'est permis que par une vraie fiche sans exigence, jamais par equipment_required vide mais inconnu. Une substitution relance faisabilité, rôle, allocation et temps ; pas d'équivalence de dose devinée. Une confirmation d'ancien contexte présente dans la requête est rejetée par validate_exchange v1 ; le producteur ne l'ignore pas silencieusement et ne réécrit pas le request/fingerprint. Un éventuel snapshot filtré doit être construit explicitement en amont avant son empreinte. La durée de validité de cette confirmation reste une décision explicite D3, sans TTL inventé.

Attribution : calcul direct depuis `exercise_science.contributions` du catalogue15zones et `sci-exposure-credit-v1` (PRIMARY1, SECONDARY0.5, MINOR0, UNKNOWN inconnu). Ces coefficients sont la convention existante, pas des fractions physiologiques mesurées pour chaque utilisateur. Aucune projection implicite de posterior11zones vers hamstrings/glutes. Les15zones sont présentes avec rôles bruts, crédit/bornes honnêtes ; absence de rôle connu ≠ donnée inconnue. Toute attribution UNKNOWN empêche de certifier une exposition complète. Une zone à zéro connu ne signifie pas besoin nul ou faiblesse.

## 5. Temps : pas de borne fabriquée

Modèle proposé : somme des intervalles de travail + repos inter-séries + préparation/échauffement + réglage/apprentissage + transitions + marge explicitement documentée. Les rests ne sont comptés qu'aux frontières où ils existent, sans double comptage de repos/transition. Chaque composante possède unité, base, contexte d'applicabilité, borne basse/haute et version ; préciser bilatéral/unilatéral et séries préparatoires séparées des séries de travail.

**Gate actuelle : aucune source du dépôt ne justifie toutes les bornes hautes nécessaires.** Ni 90s de timer, ni titre45min, ni protocole de laboratoire ne borne l'attente aux machines d'une salle réelle. Le bundle temps reste non approuvé jusqu'à un protocole et des observations explicites ou une autre convention de planification documentée/revue avec ses limites. Aucun « +5min » ou set=30s sans base. Sans politique de temps admise : POLICY_UNAVAILABLE selon la priorité v1, avec TIME_UNCERTAIN explicite si pertinent ; jamais READY. Si une politique est approuvée mais ses bases ne couvrent pas ce contexte : Duration UNKNOWN et REVIEW_REQUIRED/TIME_UNCERTAIN. La borne est une estimation conditionnelle, pas garantie de finir malgré toute interruption.

Budget déclaré trop court : d'abord vérifier si toute configuration admise échoue sous des bornes valides. Sinon revoir plutôt que prétendre impossibilité. Ne pas supprimer silencieusement une intention ou le repos pour réussir. Le plan initial à dose réduite sous contrainte temporelle demande une version/politique dédiée, pas un repli implicite.

## 6. États, confiance et READY

Ordre identique au validateur v1 : conflit utilisé/requis → CONFLICTING_DATA ; manque requis → INSUFFICIENT_DATA ; politique non approuvée → POLICY_UNAVAILABLE ; impossibilité prouvée → CONSTRAINT_UNSATISFIABLE ; blocage de revue → REVIEW_REQUIRED ; sinon READY. Codes existants seulement, notamment COMPATIBILITY_UNKNOWN, TIME_UNCERTAIN, CATALOG_GAP, CONSTRAINT_VIOLATION. Conflit facultatif inutilisé reste signalé sans devenir un manque artificiel.

`individual_response=NOT_ESTIMATED` dans tous les cas. La faible confiance est portée par les limitations/preuves et `feasibility=UNKNOWN/MIXED`, sans score0–100 ni nouvel enum LOW. Si elle concerne une condition obligatoire de faisabilité/temps/dose, le plan reste à revoir. Une source de groupe ne devient pas probabilité individuelle de succès.

La première vraie fixture READY ne sera **générée que par le producteur réel testé**, après bundle dose/sélection/attribution/temps approuvé, Blueprint suffisant, candidats tous CONFIRMED/NOT_REQUIRED, contraintes résolues, exposition complète et durée haute≤budget. Pas de recopie du `future_protocol_example` de test ni de policy_ref fictive ajoutée au registre pour passer.

## 7. Version, reproductibilité et frontière mobile

Version proposée de politique0.1.0-proposed ; aucune version d'engine livrée. Une version1.0.0 ne sera figée qu'après build/revue. Empreinte d'entrée = `decision_fingerprint(request)` existant ; as_of explicite, pas d'horloge globale, hasard, locale, ordre de dictionnaire ou état SQL. Le request.version.engine et la sortie doivent correspondre au véritable producteur. Artefacts figés : hashes catalogue/crédit, bundle/politiques/preuves, sources et sortie de décision. Les entrées identiques sous mêmes références donnent des sorties identiques. Changement de référence exige nouvelle version, jamais réécriture d'une décision historique.

Pour FirstPlanClient de PR3530ee7ba3 : un futur adaptateur de confiance peut envelopper la sortie v1 dans `{owner_id, kind:'result', result}` ; `.verify` doit appliquer le fingerprint et validate_exchange avec références autoritaires. Ce wrapper n'appartient pas à la décision scientifique pure. Pending/unavailable/rejected de transport restent distincts des6statuts métier ; aucune API ni auth simulée dans ce build scientifique. Test de parité consommateur sur fixture générée, coordonnées par OpenSpec après disponibilité ; aucun fichier mobile partagé édité en parallèle.

## 8. Frontière d'exécution

Ce dossier est le résultat autorisé en l'absence de GO BUILD distinct. Après acceptation : plan d'implémentation, TDD, producteur/fixtures isolés, broad ciblé selon check_scope, revue indépendante, CI réelle, merge sous GO permanent si readiness acquise. Le moteur de production et le raccordement mobile/API conservent leurs propres gates. Le manque du modèle de temps peut être livré comme blocage réel du producteur ; il ne sera pas masqué par une fixture READY de démonstration.

## Revue de construction — clarifications intégrées

Relecture indépendante terminée : pas de décision substantielle manquante hors D1–D5 ; aucun READY artificiel demandé. Deux écarts de formulation avec v1 corrigés sans changement de schéma : confirmation d’un autre contexte rejetée par le validateur (pas ignorée) ; population hors enum rejetée en amont (pas sortie métier inventée). Priorité POLICY_UNAVAILABLE avant revue de temps maintenue tant que le bundle temps n’est pas admis. Aucun test/producteur exécuté par le relecteur.
