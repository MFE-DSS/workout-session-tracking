## Context
Le producteur REL-03 existant archive le Git exact, résout `python:3.11.14-slim` en digest avant le build amd64, conserve la même archive Docker sous AES-GCM dans la garde privée et publie uniquement la metadata. Une approbation humaine `APPROVE_QA_IMAGE <SHA>` est vérifiée dans le run exact ; GOV-MERGE-01 ne la remplace pas.

Le Docker local ne répond pas : version/info dépassent chacun 12 s ; desktop status dépasse 5 s. Des processus Desktop sont présents. Ni disponibilité du daemon, ni build, ni arrêt/redémarrage ne sont revendiqués.

## Brainstorming / Options / Risques / Choix retenu
1. Réutiliser l'ancienne image et monter le source : rejeté, ne satisfait pas l'identité du paquet.
2. Construire localement avec REL-03 : autorisé en préparation, indisponible tant que le daemon ne répond pas ; une émulation ARM ne suffit de toute façon pas à la qualification CPU native.
3. Réutiliser PREPARE_IMAGE et un banc natif neuf sur l'hôte existant : retenu sous GO opérationnel exact, sans nouveau fournisseur ni service exposé. Risques : archive privée, ressources de l'hôte partagé, différence des dépendances reconstruites ; bornes et refus explicites dans OPERATIONAL_DELTA.md.

## Decisions
- Source de paquet figée à `1ac401f44b8af9444a8521b30cd47b7201fd1c8e`, sauf changement relu imposant une nouvelle décision. Les documents de préparation ne sont pas du code à incorporer pour simuler une nouvelle image produit.
- L'image n'est connue qu'après build : imageID/config digest, digest de base, manifeste éventuel et archive réelle sont acquis, jamais préremplis. Docker save peut ne pas fournir de RepoDigest OCI de distribution : conserver NOT_ISSUED_BY_DOCKER_SAVE si absent, avec manifeste/config/archive réellement vérifiés.
- Ne monter aucun source sur `/opt/auren` ou bundle sur `/opt/science`. Leurs octets proviennent exclusivement de l'image. Le harness externe ne fait qu'appeler le produit ; aucune substitution de worker/projection. Les sondes instrumentées sont séparées des mesures nominales.
- Profil et digest attendu créés depuis un contrôle d'attestation de confiance, pas depuis HTTP ni depuis un fichier modifiable par UID10001. Examiner parents jusqu'à `/`, ACL effectives, mountinfo, image/config/volume et absence de symlink. Root/hôte/Docker/éditeur autorisé du profil restent hors du modèle d'un acteur non privilégié.
- Les profils de test portant QUALIFIED pour exercer le garde sont des FIXTURES SYNTHÉTIQUES, non une admission opérationnelle. Un profil proposé de déploiement sera émis seulement après campagne et lié au digest d'un reçu de qualification indépendant ; aucune activation implicite.
- La passerelle admet déjà `/api/mobile/v1/me/muscle-observed-load`. En revanche `_child_environment` ne transmet aucun des trois paramètres SCI ; `_load_config` et `load_feature_config` ont des schémas fermés. Une variable Docker seule ne suffit pas. Aucune extension de ce lanceur n'est appliquée dans cette préparation.
- Prouver le bootstrap réel avec SCI désactivé, puis le lecteur dans un conteneur de qualification séparé de la même image et avec HTTP canonique. Cette seconde preuve ne vaut pas qualification d'un futur raccordement bootstrap activé. L'activation doit inclure ce raccordement autorisé, ses tests et son rollback avant de pouvoir recevoir YES.

## Risks / Trade-offs
L'image de base résolue et les dépendances installées peuvent différer du banc historique malgré le même tag Python. Mesurer Python/SQLite et le lock effectif ; conserver HOLD à toute différence non qualifiée. Les 500/501 restent des refus attendus, pas des objectifs de capacité à rendre verts. Le finding Sonar S8707 reste ouvert ; ni montage ro ni digest ne certifie à lui seul les parents et montages du futur service.
