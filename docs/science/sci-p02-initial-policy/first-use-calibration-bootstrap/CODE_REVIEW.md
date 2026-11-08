# Fresh whole-branch code review — first-use calibration bootstrap

Reviewer indépendant de l'auteur et de la revue SCI, lecture seule. 8 novembre 2026.

- Checkout : `/private/tmp/auren-sci-first-use-calibration-bootstrap`.
- Base : `d7de8aa02248c63d8914fb69f8c4c8a9fd980ee0`.
- HEAD examiné : `d5693310b8e47f2388ab0d090f070fc403704bce`.
- Portée : diff complet de la branche, modules/contrats/tests/autorité/exports/documents, plan, design, TEST_SPEC et rulings du ledger. Contrats historiques pertinents lus pour vérifier les frontières et la qualification effective.
- Contrat de revue : template `requesting-code-review/code-reviewer.md`. CLAUDE.md et STANDING_MERGE_AUTHORIZATION.md lus sur `origin/HEAD` canonique ; RTK.md absent des emplacements locaux recherchés.
- Aucun fichier, index, HEAD ou état de branche du checkout modifié. Seuls ce rapport et la reproduction voisine ont été écrits hors dépôt. Aucun patch proposé ni appliqué. Aucun sous-agent lancé.

## Strengths

- Séparation nette entre compilation candidate non autoritaire, publication isolée et résultat public ; absence d'autorité ferme les permissions physiques et la qualification.
- Revalidation récursive préservant les types natifs des modèles Pydantic copiés ; les valeurs bool/NaN/inf et les propriétaires/contextes divergents sont couverts.
- Autorité immuable, inventaire de sources et rechargement des octets sur chaque validation ; le test de dérive après chargement couvre réellement le cache d'autorité.
- Préoccupations de tout l'épisode, échecs, inconnus de qualité/gêne et prédécesseurs bloqués restent prioritaires ; aucun remapping False→null trouvé.
- Correction SCI précédente bien présente : préparation/choix postérieurs au trial et confirmation de contexte absente/postérieure ferment qualification et acceptation dans les cas couverts.
- Le bridge emploie effectivement le producteur/validateur V3 ; aucun ancien contrat, pin, SDK, API, UI ou série de travail modifié dans ce diff.

## Issues

### Critical

Aucun identifié dans ce périmètre isolé NOT_SERVED. Les permissions incorrectes ci-dessous sont néanmoins des Important à fermer avant livraison de cette autorité.

### Important I1 — des priors de population remplacent les déclarations personnelles requises

**Fichier :** `tools/science_calibration_bootstrap/evaluator.py:149` (garde population/limitations, lignes 149–155), avec le contrat `contracts.py:67`.

La garde vérifie seulement `KNOWN`, `ADULT_NON_CLINICAL` et limitations vides. Le modèle Fact historique autorise un fait KNOWN dont la provenance est `POPULATION_PRIOR`/`DERIVED`, avec dates absentes. Aucune garde de la rencontre ne vérifie ici qu'il s'agit d'une déclaration personnelle sourcée/datée.

**Reproduction exacte :** partir de `synthetic_encounter(stage='trial')` ; pour `population` et `limitations`, remplacer exclusivement la provenance par :

```python
{
    'origin': 'POPULATION_PRIOR',
    'acquisition': 'DERIVED',
    'source_ref': 'synthetic:generic-default-for-all-users',
    'measured_at': None,
    'recorded_at': None,
}
```

`validate_result(raw, evaluate(raw, load_authority()), authority)` accepte le résultat `SUPPORTED_INITIAL_EXPLORATION / TRIAL`, avec **INITIATE_TRIAL autorisé**. Le script compagnon réutilise le même objet d'autorité pour les deux appels.

**Attendu / effet :** design « adulte non clinique déclaré, réponse explicite sur limitations », protocole §1 et admission exigent des déclarations personnelles. Une valeur par défaut dérivée d'une population ne constitue ni cette déclaration ni une réponse vide explicite. Un caller raisonnable qui conserve honnêtement la provenance obtient pourtant une permission physique. Ce n'est pas le problème insoluble de l'authenticité d'un utilisateur menteur : le payload signale lui-même une source inapplicable. La correction ne doit pas imposer une nouvelle déclaration à chaque rencontre lorsqu'un snapshot personnel antérieur reste applicable.

### Important I2 — une confirmation ancienne enregistrée tard réouvre un redémarrage de familiarisation non terminé

**Fichier :** `tools/science_calibration_bootstrap/evaluator.py:71` (lignes 71–78), consommé par `can_trial` à la ligne 249.

`_familiar` exige que la séquence de confirmation soit après la dernière séquence STARTED, mais ne compare pas leur occurrence réelle. Le contrat impose l'ordre des enregistrements, pas l'ordre des mesures ; une confirmation ancienne saisie tard est donc interprétée comme achèvement d'une nouvelle familiarisation.

**Reproduction exacte :** partir de `synthetic_encounter(stage='trial')`, garder contexte/choix/préparation. Ajouter un `FAMILIARIZATION_STARTED`, séquence 2, réellement à **11:02:30**, enregistré à **11:03**. La confirmation d'origine devient séquence 3, réellement à **11:02**, enregistrée à **11:04**. Toutes les dates sont le `2026-11-07` en UTC ; aucun essai n'a encore été observé.

Le vrai évaluateur et son validateur retournent **SUPPORTED_INITIAL_EXPLORATION / TRIAL / INITIATE_TRIAL autorisé**. Aucune confirmation de familiarisation n'est pourtant survenue après le dernier redémarrage réel à 11:02:30.

**Attendu / effet :** la logique de redémarrage doit conserver son invalidation de l'ancienne familiarisation même lorsque les faits sont enregistrés tard. Une séquence de saisie ne peut remplacer la confirmation réellement applicable. C'est précisément une permission physique indue issue d'une chronologie explicitement représentée, sans changement de setup inventé ni hypothèse clinique supplémentaire.

### Important I3 — l'acceptation d'un ancien réglage est offerte malgré son remplacement courant et ne peut qualifier

**Fichier :** `tools/science_calibration_bootstrap/evaluator.py:267` (garde d'offre ACCEPT_EXACT_SETTING, lignes 258–279).

Cette garde accepte n'importe quelle confirmation de contexte antérieure au trial ; elle ignore la dernière confirmation de réglage. La qualification réelle, via `calibrate_for_admission`, exige au contraire que le dernier contexte confirmé conserve le réglage essayé. L'invariant annoncé au commentaire lignes 255–256 (« offer acceptance only when this exact episode would qualify after a real acceptance action ») est donc encore faux pour un contexte modifié.

**Reproduction exacte :** partir de `synthetic_encounter(stage='observed')` (trial de 40). Ajouter un `CONTEXT_CONFIRMED` séquence 4, à **11:04**, réglage **45** ; conserver le choix d'origine 40, qui est maintenant périmé relativement au ledger. L'évaluateur public, validé par `validate_result`, offre toujours **ACCEPT_EXACT_SETTING** pour le trial de 40. Ajouter ensuite une vraie `SETTING_ACCEPTED` séquence 5, à **11:05**, référençant exactement ce trial de 40 : le résultat reste **OBSERVED**, sans qualification.

**Attendu / effet :** le caller reçoit une action qu'il peut accomplir correctement mais qui ne satisfait pas la transition annoncée ; le nouveau réglage explicitement confirmé n'est pas pris en compte par l'offre. Ce n'est pas une fausse qualification finale — cette dernière reste fermée — mais un parcours d'acceptation incohérent, dans la même catégorie que M1 reclassé Important par le ruling du ledger. Le cas antérieurement fermé « contexte absent » reste fermé ; ceci est le cas distinct « contexte désormais remplacé ».

### Minor M1 — une observation existante redevient une phase de familiarisation si le choix courant manque

**Fichier :** `tools/science_calibration_bootstrap/evaluator.py:225` (retour anticipé avant la recherche des trials).

Partir de `synthetic_encounter(stage='observed')`, puis `raw['setting_choice'] = None`. Le vrai évaluateur/validateur retourne **SUPPORTED_INITIAL_EXPLORATION / FAMILIARIZE**, alors que l'épisode conserve son ATTEMPT_OBSERVED courant et non préoccupant.

Le contrat/handoff dit « OBSERVED reste OBSERVED jusqu'à satisfaction exacte C3 » et les manques doivent bloquer seulement les actions qui les consomment. La permission de nouvel essai est bien fermée et aucun fait source n'est effacé ; l'état/phase public sous-représente cependant l'activité réellement déjà observée. Le résultat devrait conserver cette distinction lorsqu'il demande de réacquérir un choix courant.

## Reproductions et vérifications

Script autonome adjacent : `reproduce_code_review.py`. Il utilise exclusivement les données synthétiques publiées, le vrai loader, le vrai évaluateur et la recomputation canonique ; aucun mock, monkeypatch, autorité de test ou mutation du dépôt.

Exécution depuis le checkout :

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. /Users/martinfeldmann/workout-session-tracking-mob02/.venv/bin/python /private/tmp/auren-sci-first-use-calibration-bootstrap-review-evidence/reproduce_code_review.py
```

Sortie effectivement observée :

```text
I1: SUPPORTED_INITIAL_EXPLORATION TRIAL INITIATE_TRIAL allowed from population priors
I2: SUPPORTED_INITIAL_EXPLORATION TRIAL INITIATE_TRIAL allowed without completion after restart
I3: ACCEPT_EXACT_SETTING allowed for 40 after current confirmation changed to 45; actual acceptance remains OBSERVED
M1: SUPPORTED_INITIAL_EXPLORATION FAMILIARIZE despite retained actual ATTEMPT_OBSERVED
```

`check_scope.py` exécuté avant les vérifications : **ISOLATED**. Aucun full sweep local. Les trois modules nouveaux ont été exécutés avec `PYTHONDONTWRITEBYTECODE=1`, pytest `-p no:cacheprovider` : **61 passed, 2 warnings in 6.77s**. Les avertissements concernent les dépréciations anyio/pytest et starlette/httpx. Le test d'exports reproductibles fait partie de ces 61 tests. Le broad 612/19 modules indiqué par le controller n'a pas été relancé par cette revue. HEAD final relu identique ; `git status --short` vide.

## Recommendations

Fermer I1–I3 dans une passe consolidée, avec les contre-exemples ci-dessus comme régressions. Garder les invariants communs aux permissions et à la qualification afin qu'une action d'acceptation proposée corresponde à une qualification réellement atteignable. Une mise à jour des sources/pins/exports devra accompagner toute modification du bundle admis. Aucun correctif implémenté dans cette revue.

## Declined to judge

- Authenticité d'identité, exhaustivité d'un ledger volontairement omis, véracité d'une déclaration USER_REPORTED ou d'un setup falsifié : responsabilités PLAN/DATA explicites ; le moteur pur ne peut les établir. Les provenances explicitement inapplicables et contradictions présentes ont bien été jugées.
- Retrait distant/offline de l'autorité et révocation serveur : publication isolée NOT_SERVED, aucun mécanisme réseau dans ce scope ; la dérive locale/cached authority est couverte.
- Protection contre remplacement arbitraire du code exécuté, monkeypatch d'un processus ou modification simultanée de la politique et de ses ancres de confiance : hors du modèle d'un loader local ; ses vérifications de publication/sources réellement présentes ont été jugées.
- Innocuité clinique, efficacité biologique, capacité d'un novice à choisir seul son réglage et nouvelle enquête anatomique : revue SCI séparée, explicitement hors mandat de revue code ; aucun avis clinique émis.
- Activation, collecte réelle, disponibilité d'assistance, UI/API/SDK/persistance et six autres accompagnements initiaux : hors scope autorisé, demeurent absents.
- Les libellés historiques PROPOSED/NO_GO_BUILD dans les documents de préparation : conservation historique contextualisée par BUILD_AUTHORIZATION, DELIVERY et l'actualisation du registre ; pas de nouveau constat doublonnant SCI M2.
- GitHub, CI réelle, protections de branche, merge/closeout et nettoyage : controller responsable ; aucun résultat distant ou droit de fusion certifié ici.

## Assessment

**Ready to merge? With fixes — avis technique sur le code uniquement.** Trois Important restent ouverts sur les permissions et la cohérence du parcours malgré les 61 tests verts. Les frontières d'isolation et la non-régression des contrats historiques sont bien conservées ; cet avis ne certifie ni la science générale, ni la CI distante, ni la readiness GitHub.

## Résolution par l'implémenteur après cette revue
I1–I3 fermés dans une passe de corrections, avec neuf cas rouges puis dix verts incluant un témoin, et suite nouvelle71/71 verte. Le rapport ci-dessus conserve les constats du HEADd569331 ; il n'est pas une nouvelle revue du correctif. Broad et CI du HEAD corrigé sont suivis dans DELIVERY/closeout. M1 reste mineur différé, sans perte de fait ou permission d'essai ; aucune claim de recette utilisateur.
