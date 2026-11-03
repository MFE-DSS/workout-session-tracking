# GOV-MERGE-01 — GO MERGE permanent

**Statut : ACTIF sur décision opérateur du 3 novembre 2026, révocable à tout moment.**
**Dépôt :** `MFE-DSS/workout-session-tracking` uniquement.

L'opérateur demande : « autoriser les go merge […] dès que c'est succès […] tu fais le merge directement ».
Cette décision autorise l'enregistrement, le commit, le push, la PR et l'intégration de cette
configuration, ainsi que les merges suivants dans les périmètres de travail déjà approuvés.

## Brainstorming / Options / Risques / Choix retenu

Les GO par PR multiplient les interruptions. Une fusion sans contrôles expose aux régressions.
Le choix retenu applique l'autorisation permanente demandée aux seules PR prêtes d'un travail
autorisé : aucun contrôle n'est supprimé et aucune nouvelle fonctionnalité n'est autorisée ici.
Plan borné : aligner le contrat et le protocole, enregistrer le rappel local Codex,
vérifier le diff puis la CI réelle, intégrer avec garde sur le HEAD, vérifier le canonique.

## Règle d'exécution

Après le GO BUILD d'un périmètre, l'agent poursuit sans nouveau GO jusqu'au merge,
au closeout et au nettoyage de ses seuls éléments sans travail unique. Sont incluses
les PR de correction dans ce périmètre et de closeout nécessaires à sa livraison.
Un GO MERGE ponctuel supplémentaire n'est plus demandé.

Avant chaque merge, vérifier sur le HEAD final et la base canonique actuelle :

- validations locales complètes exigées par `check_scope`, adaptées si la base effective change ;
- CI réelle et contrôles obligatoires réussis, selon les règles existantes de déclenchement ;
- PR `MERGEABLE`, sans conflit ni revue ou thread bloquant, et validations humaines requises obtenues ;
- périmètre conforme aux specs et au GO BUILD, absence de condition d'arrêt dur.

Méthode autorisée : **commit de merge**, avec garde du SHA attendu du HEAD.
Si le HEAD ou la base change avant l'intégration, revérifier la readiness avant de fusionner.
`UNSTABLE` n'est admissible que pour Sonar consultatif non requis conformément à GOV-SONAR-01 ;
ses résultats réels, y compris ERROR, restent consignés.
Les quatre checks requis actuels restent : `pytest + QA scripts`,
`lint (ruff budget + bandit + actionlint + shellcheck)`, `visual contract (DA-GOV-01)` et
`mobile checks (Jest + TypeScript)`. Les autres contrôles applicables restent actifs.

## Périmètre interdit

Aucun bypass de protection, `--admin`, force-push, squash, affaiblissement de gate ou de test.
Les arrêts sécurité, données, secrets et conflits de spec restent obligatoires.
Les validations visuelles du contrat UI restent requises avant livraison.
Ce GO ne vaut ni GO BUILD d'un nouveau périmètre (notamment MOB-02), ni autorisation de déploiement.
Les permissions gérées par l'environnement restent applicables ; ce document ne les désactive pas.

## Compte rendu

Après intégration, consigner PR, HEAD vérifié, SHA de merge, validations et CI canonique,
résultat Sonar réel, nettoyage et éléments préservés. Rapporter les blocages concrets ;
ne pas demander à nouveau une autorisation déjà enregistrée pour la même action.
