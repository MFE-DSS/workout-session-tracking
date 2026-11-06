# SCI-P02-CANDIDATE-CURATION-01 — vérifications

6 novembre2026. Base7e295c0 ; pas de résultat distant anticipé.

## Local exécuté

- `check_scope` : **ISOLATED** (trois nouveaux fichiers Python feuilles, aucune importation par le runtime), broad scientifique ciblé requis ; aucun full sweep local.
- TDD initial :18échecs/1réussite avant implémentation,19réussites après ; jeu de sources incomplet reproduit rouge puis garde ajoutée (22réussites). Important de revue : UNKNOWN ajouté à AVAILABLE+UNAVAILABLE masquait le conflit ; régression observée rouge, test de sous-ensemble corrigé, **23tests curation passants**.
- Broad scientifique16modules : **445passants,1ignoré**, deux avertissements de dépendances existants. Curation, admission antérieure, producteur, contrats, génération/rulings/validation/lecture du catalogue, identité/exposition/any_of, intentions/couverture, weekly planner, convergence épistémique et page science.
- Ruff des nouveaux fichiers passe ; budget **264≤548** ; Bandit ciblé, protocole documentaire et OpenSpec strict **8/8** passent. Gitleaks du bundle documentaire : aucune fuite. Aucun secret ou identifiant QA consulté.
- CLI curation :40candidats/sept intentions et matrice/fixtures reproduits ; CLI producteur :onze sorties historiques reproduites ; CLI admission antérieure :audit reproduit. Sources scientifiques et politiques historiques inchangées ; aucune modification catalogue/E0/crédit/objets/schémas/producer/mobile.
- Les tests garantissent digest et pool exacts, séparation UNKNOWN/MINOR/NONE, absence de score/charge/temps, invalidation régionale hors configuration, contexte inconnu/conflit/exclusions/limitations, latéralité, absence de choix par défaut et aucune READY. Ils ne certifient pas la science.

## Revues distinctes

Revue de code indépendante : un Important identifié et corrigé RED→GREEN (conflit à trois états). Relecture du correctif : **aucun Critical/Important restant**,23tests et fixtures rejoués. Aucun autre Minor signalé dans cette tranche ; le Minor historique du diagnostic de temps reste hors périmètre.

Revue scientifique fraîche, différente des auteurs de recherche et du relecteur code : **CURATION_PARTIALLY_ADMITTED, aucun Critical/Important**. Primaires presse/extension2026, mollets2023, deltoïde2025 et anatomie2008 vérifiés en texte intégral. Aucun candidat supplémentaire à retenir ; manque vertical et choix du prochain spike confirmés. Minor documentaire appliqué : correction Plotkin2026 vérifiée (don de matériel/COI, enregistrement rétrospectif, pas de changement annoncé des résultats), limite explicitée dans EVIDENCE.md. Aucun code ou paramètre scientifique modifié suite à cette remarque.

## Publication

Le HEAD exact, la PR, les runs et verdicts Sonar sont consignés dans le reçu de PR après exécution, puis dans le closeout vérifié. Sonar demeure consultatif selon GOV-SONAR-01 ; aucun seuil ou état d’issue n’est modifié. `sonar.sources=app` : la couverture app ne mesure pas la couverture des outils isolés de curation.

**NOT_SERVED / READY_NOT_PRODUCED**. Aucun API/UI, producteur lié, prescription, déploiement ou recette appareil. La clôture de cette opération ne ferme pas le change scientifique global, PLAN ou MOB03.
