# SCI-P02-CANDIDATE-CURATION-01 — vérifications

6 novembre2026. Base7e295c0 ; pas de résultat distant anticipé.

## Local exécuté

- `check_scope` : **ISOLATED** (trois nouveaux fichiers Python feuilles, aucune importation par le runtime), broad scientifique ciblé requis ; aucun full sweep local.
- TDD initial :18échecs/1réussite avant implémentation,19réussites après ; jeu de sources incomplet reproduit rouge puis garde ajoutée (22réussites). Important de revue : UNKNOWN ajouté à AVAILABLE+UNAVAILABLE masquait le conflit ; régression observée rouge, test de sous-ensemble corrigé, **24tests curation passants**.
- Broad scientifique16modules : **446passants,1ignoré**, deux avertissements de dépendances existants. Curation, admission antérieure, producteur, contrats, génération/rulings/validation/lecture du catalogue, identité/exposition/any_of, intentions/couverture, weekly planner, convergence épistémique et page science.
- Ruff des nouveaux fichiers passe ; budget **264≤548** ; Bandit ciblé, protocole documentaire et OpenSpec strict **8/8** passent. Gitleaks du bundle documentaire : aucune fuite. Aucun secret ou identifiant QA consulté.
- CLI curation :40candidats/sept intentions et matrice/fixtures reproduits ; CLI producteur :onze sorties historiques reproduites ; CLI admission antérieure :audit reproduit. Sources scientifiques et politiques historiques inchangées ; aucune modification catalogue/E0/crédit/objets/schémas/producer/mobile.
- Les tests garantissent digest et pool exacts, séparation UNKNOWN/MINOR/NONE, absence de score/charge/temps, invalidation régionale hors configuration, contexte inconnu/conflit/exclusions/limitations, latéralité, absence de choix par défaut et aucune READY. Ils ne certifient pas la science.

## Revues distinctes

Revue de code indépendante : un Important identifié et corrigé RED→GREEN (conflit à trois états). Relecture du correctif : **aucun Critical/Important restant**,23tests et fixtures rejoués. Aucun autre Minor signalé dans cette tranche ; le Minor historique du diagnostic de temps reste hors périmètre.

Revue scientifique fraîche, différente des auteurs de recherche et du relecteur code : **CURATION_PARTIALLY_ADMITTED, aucun Critical/Important**. Primaires presse/extension2026, mollets2023, deltoïde2025 et anatomie2008 vérifiés en texte intégral. Aucun candidat supplémentaire à retenir ; manque vertical et choix du prochain spike confirmés. Minor documentaire appliqué : correction Plotkin2026 vérifiée (don de matériel/COI, enregistrement rétrospectif, pas de changement annoncé des résultats), limite explicitée dans EVIDENCE.md. Aucun code ou paramètre scientifique modifié suite à cette remarque. Le contrôle final a ensuite reproduit rouge une syntaxe d’ID incompatible dans le seul patch E0 proposé ; IDs réservés EV-C1/EV-C2 corrigés sans modifier E0 ni les claims. Test de syntaxe canonique et absence de collision ajouté ;24tests curation puis446broad passants.

## Publication

Le HEAD exact, la PR, les runs et verdicts Sonar sont consignés dans le reçu de PR après exécution, puis dans le closeout vérifié. Sonar demeure consultatif selon GOV-SONAR-01 ; aucun seuil ou état d’issue n’est modifié. `sonar.sources=app` : la couverture app ne mesure pas la couverture des outils isolés de curation.

**NOT_SERVED / READY_NOT_PRODUCED**. Aucun API/UI, producteur lié, prescription, déploiement ou recette appareil. La clôture de cette opération ne ferme pas le change scientifique global, PLAN ou MOB03.

Premier HEAD entièrement analysé `3d2a7c9` : [PR362](https://github.com/MFE-DSS/workout-session-tracking/pull/362), [CI42217150825](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/42217150825), completed/success,9jobs ;7383backend/3ignorés et54suites/676mobile+TypeScript. Sonar externe ERROR/Major : un nouveau S5778 dans le test de bundle falsifié,0bug/vulnérabilité/hotspot, couverture app93.8%. Correction minimale : préparation `request()` sortie de `pytest.raises`, même appel testé et mêmes exigences. Le verdict de ce HEAD ne vaut pas validation du HEAD corrigé. Aucun seuil/état d’issue changé. L’ancien run706c9ab a été annulé uniquement car remplacé par ce HEAD, puis arrêté via force-cancel après arrêt normal bloqué ; aucun résultat de ce run obsolète ne sert de gate.

## Clôture vérifiée de la seule opération de curation

- PR[#362](https://github.com/MFE-DSS/workout-session-tracking/pull/362), HEAD **ae0169137da3e5e91075ce9fd9f3b1d556dcb2d6**, merge **1c48301bb855733a610d376ba6d58219a00fe5c4** ; méthode merge et garde du SHA, base7e295c0 vérifiée. Aucun bypass, force-push ou déploiement.
- [CI PR42220266909](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/42220266909) : completed/success,9jobs ; **7383backend passants,3ignorés**,54suites/676mobile+TypeScript, QA/lint/sécurité/visuel réussis.
- Sonar PR final : **Quality Gate OK**,0nouvelle issue ouverte/0nouveau code smell,0bug/vulnérabilité/hotspot, couverture app93.8%. S5778 du HEAD précédent clos par analyse après déplacement de la préparation hors pytest.raises ; mêmes exigences, aucun seuil/état d'issue changé. Les outils restent hors sonar.sources=app.
- Après cette correction de test seulement : **124tests producteur/contrats/admission/curation passants**, Ruff/budget264≤548/protocole passants ; aucune nouvelle logique ou décision scientifique après les revues sans Critical/Important.
- [CI canonique42222587746](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/42222587746) : **completed/success,9jobs**, mêmes7383backend/3ignorés et676mobile+TypeScript. Les shards ont réellement rejoué les tests ; aucune configuration de réutilisation modifiée.
- Analyse Sonar canonique liée au SHA1c48301 : **Quality Gate ERROR**, conditions Bugs Blocker, Code smells Critical et Vulnerabilities Minor ; couverture app93.8%, nouvelle94.0%. Les6constats de type vulnérabilité ouverts consultés sont les imports externes Bandit B110/B112 de juin2026 dans cinq fichiers app inchangés par cette opération. Aucun nouveau défaut de sécurité confirmé par ce diff ; ce relevé limité ne vaut pas audit global. GOV-SONAR-01 reste consultatif, sans changement de seuil/état d'issue ; la réévaluation avant exposition/production reste distincte.

Closeout limité à CURATION_PARTIALLY_ADMITTED : aucune fermeture du change global, PLAN ou MOB03. État runtime NOT_SERVED, READY_NOT_PRODUCED. Prochain spike unique : SCI-P02-PULL-EXPOSURE-RESOLUTION-01, sans GO BUILD implicite. Le statut définitif de publication de ce closeout sera porté dans sa PR après ses contrôles ; nettoyage ensuite limité aux branches/worktree de cette opération sans travail unique. Worktrees produit/science antérieure et preuves QA préservés.
