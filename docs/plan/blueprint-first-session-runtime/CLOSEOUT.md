# PLAN V3 — closeout du seul runtime contrôlé

9 novembre2026. **CODE MERGED / SUCCESSOR CANONICAL VERIFIED / CLOSEOUT HEAD PENDING.**
La CI de capacité a été corrigée dans son scope distinct et vérifiée ; ce
closeout synchronisé attend les contrôles de son nouveau HEAD et le canonique
final. Les documents gardent leur instant de publication ; le reçu vivant porte
les résultats et cleanup ultérieurs réellement observés.

## Reprise après l’incident CI

Les runs42526541847 (canonique code31b89f9) et42527005736 (ancien HEADd6b902f
de ce closeout) terminent **cancelled**, après shutdowns répétés du shard2.
Leur état n’est pas réécrit comme PASS. Les premières traces indiquaient20/46MiB
disponibles,swap0 ; la cause kernel/service exacte reste non certifiée. Les
diagnostics bornés n’ont pas établi de fuite monotone de démarrage applicatif.

Correctif CI autorisé séparément : PR381 HEAD48ec5ec939e4a11aaef6cb4f95804bdf817c7387,
merge3fcf0911da816cd1158aecb9cff14dc810eb0afe. Cinq shards, deux workers,
tests/exclusion/couverture/checks identiques ; seul cas supplémentaire : test
de partition six. CI PR42536619908 et canonique42537647816 réussies, onze jobs
chacune,7924backend/3skip et749mobile+TS. Tous les shards ont une série réelle,
workers2 et minima>=4096MiB ; plus bas4439PR/4440canonique. Aucun six nécessaire.
[Closeout CI](../../ops/ci-plan-v3-capacity/CLOSEOUT.md), archive fusionnée
PR382/ebbf877c725263e9d51f3b4e5cfa59e8f70c7502, canonique42539004312 en suivi.

Le canonique successeur vérifie réellement le code PLAN inchangé avec la CI
corrigée. L’attestation WOULD_FULL est en SHADOW MODE, pas de réutilisation
activée. Couverture PR : mêmes186fichiers/15826lignes/14687couvertes que379 ;
canonique14686couvertes,92,8% arrondi. Unique ligne de différence : commands.py:110,
seconde relecture idempotente après verrou ; variation compatible avec un autre
ordonnancement de concurrence, pas une cause certifiée ni un fichier omis.
Tous les tests passent, aucun seuil ajusté ou code app réécrit pour la mesure.

Sonar canonique exact3fcf091 : ERROR consultatif,8bugs/542smells/8entrées de
vulnérabilité/0hotspot,couverture92,8%/nouvelle92,85%. Les huit entrées sont six
imports Bandit historiques et les deux B404/B603 du worker PLAN analysées plus
bas ; aucun état/seuil modifié, pas d’audit sécurité global. SonarPR381/382 OK,
zéro nouvelle issue sur leurs diffs. Les contrôles de ce HEAD final et du
canonique final sont encore requis ; ce relevé n’en anticipe pas les résultats.

## Livraison acquise

PR[379](https://github.com/MFE-DSS/workout-session-tracking/pull/379),
HEAD7f4bd3f7cd81461e2f74b5debb70e813e910e599,
merge31b89f98985044a9ee40d75610d387976ff26d7c, baseb4a4242 vérifiée.
CI[42523124371](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/42523124371)
completed/success, neuf jobs : **7923backend passants, trois ignorés,
69suites/749tests mobiles+TypeScript**, QA/migrations/perf/sécurité/visuel et
15fichiers de tests modifiés joués seuls passants. Canonique code
[42526541847](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/42526541847)
cancelled sur31b89f9 ; le successeur corrigé ci-dessus est la preuve canonique, sans faux PASS de cet ancien run.

Huit rendus natifs bruts comparés aux références ; G1 et pixels acceptés avant
commit. La vraie app de test isolée a créé/repris/journalisé/clôturé une séance
possédée, conservé les types et résolu une correction concurrente avec refus
historique distinct. A/B isolés. Pas d'appareil physique, déploiement ou donnée
personnelle. Voir [preuves](TEST_EVIDENCE.md) et [UI](UI_REVIEW.md).

Le full local borné a couvert418fichiers, deux adaptations mémoire ; son exit1
initial est conservé (référence Alembic et ancien guard gitdiffHEAD). Référence
exacte mise à jour sans relâcher l'assertion, guard inchangé ;38tests des deux
modules repassés sur le vrai HEAD propre avant push. Tous les autres lots verts,
CI finale globale7923passants. Pas de full local redondant de maintenance.

## Sonar réel, avertissements conservés

PR379 : **QualityGate ERROR consultatif**,0bug/0hotspot,43smells dont17Critical
(5S1192/12S3776), deux diagnostics externes Bandit Minor B404/B603 dans packaging.py.
Couverture app92,8%, nouvelle82,9%. Les deux alertes concernent import/appel
subprocess : interpréteur fixe, -I, worker privé/manifeste/sources vérifiés, sans
shell ni sélection d'exécutable par corps client ; données JSON uniquement sur
stdin, timeout20s et erreurs privées. Réponses techniques aux deux threads
automatiques, aucun défaut d'exécution de commande non fiable confirmé sur ce
chemin, sans certification sécurité globale. Issues et seuils inchangés ;
GOV-SONAR-01 consultative, faille confirmée resterait un arrêt obligatoire.
Les autres remarques de qualité sont conservées, pas de refactor massif pour
masquer le critical path. Réévaluation avant exposition sensible/production.

Connecteur merge : erreur de liaison d'arguments sans effet, état ouvert relu,
puis API standard gh merge avec garde du SHA, sans admin/squash/force-push.
Les deux threads automatiques restent traités comme diagnostics consultatifs
avec réponse, pas demandes de changement de code non satisfaites. Leur état
Sonar n'a pas été modifié pour permettre la fusion.

## Périmètre et suites

Archive préparée du seul build contrôlé, sous autorisation BUILD_SCOPE reçue.
[Traçabilité complète](../../../openspec/changes/archive/2026-11-08-blueprint-first-session-runtime/CONTROLLED_CLOSEOUT_TRACEABILITY.md) ; critères
externes DATA, T25/RELEASE, activation/déploiement, six autres rencontres et
PLAN01–07/MOB03 globaux restent OPEN dans les propositions canoniques.
Aucun nouveau GO BUILD ou activation déduit de ce closeout.

[Passation agent](AGENT_HANDOFF.md), [matrice/rollback](CONTROLLED_RUNBOOK.md),
[graphe DATA](DATA_BOUNDARY.md). Checkout opérateur61ca08c, préparations ARCH et
QA MOB02 préservés. Preuves/ledger sous
/private/tmp/auren-plan-v3-runtime-review-evidence/ ; nettoyage limité aux
branches/worktree de cette livraison après intégration vérifiée et zéro travail
unique. Ce nettoyage n'est pas encore revendiqué à la rédaction.
