# SCI-OPS-QUALIFY-01 — reçu de préparation, 27 novembre 2026

**Paquet source préparé, image non construite ; lecteur DISABLED, activation NO.** Le canonique frais reste `1ac401f44b8af9444a8521b30cd47b7201fd1c8e`. Aucun commit, push, build cloud, transfert, mutation distante ou changement du QA n'a été effectué dans cette passe.

## Identité et contrôles effectifs
Archive source73 318 400octets/3 367fichiers, SHA256 `7b1230ccb42986b0533d567b6f4502d6ef202922bea1019ad9e1414cdabd857b`. Empreintes individuelles et outils/lock/Dockerfile dans `PACKAGE_PREPARATION.json` et `SOURCE_FILES.json` privés. Image/config/base et versions effectives du futur conteneur restent inconnues jusqu'au build et à l'inspection.

Le build existant résout la base par digest, exporte la même image et en conserve les octets chiffrés dans la garde privée. Le commentaire de son approbation humaine effective reste propre au run/SHA. Les anciennes autorisations de déploiement n'autorisent pas une mise à jour tacite du QA.

Docker local : version/info timeout12s chacun, desktop status timeout5s ; processus présents ne prouvent pas un daemon utilisable. Aucun restart/reset/prune. Espace libre local au relevé :17,535Gio, sous le seuil20Gio du paquet proposé ; recontrôle requis avant acquisition, sinon HOLD sans purge implicite. Aucun transfert n'est lancé dans ces conditions.

Contrôles de préparation : OpenSpec strict PASS ; protocole PASS ; scope ISOLATED par présence du metadata YAML, budget Ruff260≤548 PASS ;315tests ciblés/broad des six fichiers image/custody/bootstrap/server/pipeline/proofs PASS,1warning Starlette/httpx,195,98s. Exécutés sur **Mac/Python3.11.14** : ce ne sont pas des tests du futur Linux ni de l'image à construire. Aucun Python produit neuf/modifié ; Ruff fichiers neufs non applicable. Les deux erreurs d'invocation initiales (`python` absent puis `ruff` hors PATH) ont été corrigées sans changement produit ; le log du second échec est conservé.

CI du parent relue en direct :45896913157, quatre checks protégés completed/success. SonarCloud Code Analysis failure consultatif conservé. Aucune nouvelle CI du présent paquet non publié n'est revendiquée.

Revue indépendante de la préparation :0Critical/0Important ; mineur différé : répéter les cinq noms de verdicts dans Task5 du plan, alors que le mandat, le JSON et ce reçu les détaillent déjà. Elle n'a exécuté ni campagne Linux ni opération externe.

## Cinq verdicts
| Contrôle | Verdict actuel | Limite exacte |
|---|---|---|
| CATALOGUE / SCI PARITY | PASS du candidat SCI03 antérieur ; paquet cible HOLD | Aucune nouvelle exécution catalogue sur image construite |
| EXACT DEPLOYMENT IMAGE | HOLD | Build/acquisition pas encore autorisés pour ce paquet |
| OPERATIONAL PATH TRUST | HOLD | Image, montages, profil et ACL du nouveau runtime non éprouvés |
| TARGET RUNTIME / RESOURCE LIMITS | HOLD | Campagne native du paquet exact non exécutée ; budgets inchangés |
| READER READY FOR QA ACTIVATION | NO | Qualifications précédentes manquantes et lanceur QA sans raccordement SCI |

## Sécurité et différence avec SCI03
Finding Sonar `AaIXJeDDSfdp1gNdbPO0`, pythonsecurity:S8707 : **OPEN**, relu par API le27novembre2026 à09:11:37UTC, HTTP200. Aucun statut ou seuil modifié. L'origine est le chemin local de `load_runtime_profile`, pas un chemin HTTP démontré. La preuve précédente sur montage contrôlé ne certifie pas la future chaîne de confiance ; root/hôte/Docker restent hors du modèle des remplacements non privilégiés.

Le nouveau paquet utilisera son code et son bundle **embarqués**, sans montage de remplacement sur `/opt/auren` ou `/opt/science`. Python/SQLite/dépendances seront mesurés, pas déduits de l'image historique. Les sondes CPU instrumentées resteront distinctes des exécutions nominales.

La passerelle admet le préfixe mobile SCI. Le lanceur recrée toutefois un environnement sans `MUSCLE_OBSERVED_LOAD_ENABLED`, `MUSCLE_OBSERVED_LOAD_PROFILE_PATH` et `MUSCLE_OBSERVED_LOAD_PROFILE_SHA256` ; ses configurations sont fermées. Une variable de conteneur seule n'active donc pas le lecteur. Le futur SCI-ACTIVATE-01 devra soumettre ce raccordement précis et son rollback ; aucun correctif n'est appliqué maintenant.

## Prochaine opération
Une seule décision opérationnelle maintenant : [autoriser l'image exacte et son banc isolé](OPERATIONAL_DELTA.md). Après GO, recontrôler les préconditions de ressources, puis déclencher PREPARE_IMAGE et présenter le run exact pour sa propre approbation GitHub. Aucun besoin de nouveau GO SCI, GO MERGE, APK ou OTA.

Preuves privées : `/Users/martinfeldmann/auren-review/sci-ops-qualify-01-evidence-20261127/`. Les worktrees, anciennes preuves et services existants sont préservés. Cette préparation ne ferme pas SCI-OPS-QUALIFY-01.
