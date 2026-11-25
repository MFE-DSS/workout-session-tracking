# Fichiers et changements proposés — aucun apply

Première tranche **backend uniquement**, une PR après admission et GO distincts. Développement futur au canonique frais dans un worktree isolé, en préservant le brouillon dirty0d4fcfa. Ne pas appliquer ses fichiers produit anciens comme patch. La garde de scope future devra classer le vrai diff ; prévision shared_code (mobile_api/config et garde SCI), aucune migration ni CI infra.

## Créations produit proposées
- `app/services/muscle_observed_load/__init__.py` : package sans effet de bord.
- `app/services/muscle_observed_load/contracts.py` : paramètres, DTO stricts et erreurs publiques, aucune dépendance de writer.
- `app/services/muscle_observed_load/limits.py` : limites immuables et compteur de budgets.
- `app/services/muscle_observed_load/sqlite_source.py` : transaction propre, requêtes/bytes/ownership/graphe bornés, pas de ORM eager.
- `app/services/muscle_observed_load/provenance.py` : validation d’épisode/contexte/source, aucune réparation.
- `app/services/muscle_observed_load/projection.py` : **seul nouvel importeur direct** des sci_catalogue/sci_identity/sci_exposure existants ; fold purement descriptif/P07.
- `app/services/muscle_observed_load/worker.py` : point d’entrée isolé, OSlimits avant imports lourds ; pas app.main/DDL.
- `app/services/muscle_observed_load/supervisor.py` : slot/Popen/pipe bornés et cleanup, réponse validée.
- `app/routers/mobile_muscle_observed_load.py` : seule nouvelle route GET négociée.
- `data/sci/readiness_bodymap_projection.v1.json` : copie du mapping P07 admis avec version/digest, **pas un BodyMap SVG ni mutation de géométrie**.

## Modifications partagées exactes proposées
- `app/routers/mobile_api.py` : import et montage du seul router, au voisinage training_history ; aucune mutation de handlers existants.
- `app/config.py` : flag `muscle_observed_load_enabled=False` et `muscle_observed_load_profile_path: str = ""` et `muscle_observed_load_profile_sha256: str = ""`, références de profil technique qualifié, absentes par défaut ; aucun secret. Pas d’activation réelle dans le code ou les réglages.
- `tests/test_sci_exposure.py` : remplacer l’interdiction absolue par exception exacte projection.py seulement, avec test rejetant tout autre consommateur ; aucune suppression de garde ni import d’allocation admis.
- `docs/strategy/Sx_SCI_V2_CATALOGUE_INTEGRATION_01_SPEC.md` : addendum descriptif borné de consommation sous admission, sans promouvoir SCI à l’allocation.
- `docs/strategy/AUREN_PRODUCT_SCIENCE_DEPENDENCIES.md` : reçu d’admission P07/consommation après décision, sans admettre P09/récupération.
- `openspec/specs/mobile/feature-migration-map/inventory.yaml` : une entrée backend GET, destination native future NON RECETTÉE ; status REWRITE_NATIVE, pas une capacité native livrée.
- `docs/strategy/SPEC_REGISTRY.md` et ce seul change : décisions/tests/reçus/closeout.
- `docs/science/sci-readiness-01/ADMISSION.md` et `docs/pilot/sci-readiness-01/` : acte reçu et preuves futures, aucun acte fictif.

Tests nouveaux exacts : `tests/test_muscle_observed_load_contract.py`, `test_muscle_observed_load_sqlite.py`, `test_muscle_observed_load_provenance.py`, `test_muscle_observed_load_projection.py`, `test_muscle_observed_load_worker.py`, `test_mobile_muscle_observed_load.py`. Aucune dépendance/conftest/app.main/database modifiée ; helpers nouveaux dans tests uniquement si nécessaires, à expliciter au diff.

## Lectures seulement / interdictions
Pas d’édition de sci_exposure/sci_identity/sci_catalogue existants, SetLog/modèles/migrations, writers SET/FINISH, contrôle V3, recommandations/recovery, BODY/NUT ou clients/mobile. Ne pas appeler owned_binding/guard_owner ou load_ledger dans la nouvelle lecture. Pas de fix des quatre scopes historiques ; leur ordre01→04→02→03 reste recommandé, GO séparés.

Aucun écran/asset natif, palette, primitive, signature/APK/OTA, Dockerfile, workflow, service OVH, secret ou DATA. Une exigence non réalisable dans cette liste impose un scope amendé avant apply, pas un fichier partagé supplémentaire opportuniste.

## Préflight des leases
Inventaire lu sur10worktrees AUREN existants : aucun diff observé sur mobile_api/config/importguard/inventaire au relevé ; plusieurs anciens worktrees ont des deltas de SPEC_REGISTRY.md, qui doivent être réconciliés append-only au parent réel. Aucune réservation de fichier n’est accordée par ce constat. Au GO : re-fetch, inspecter PR/branches et activité réelle, confirmer leases des deux fichiers produit partagés, de l’inventaire et des contrats/gardes ; si conflit, continuer les fichiers neufs indépendants sans PR concurrente. Aucun reset/stash/prune/force ou autre worktree modifié.

La PR future ne doit pas transporter tout le diff de préparation SCI01 ni un autre change : elle contient BUILD01, son acte d’entrée exact et son mapping admis seulement. La préparation scientifique précédente reste préservée séparément ; aucun GO de publication documentaire ou d’implémentation n’est déduit de son état local.
