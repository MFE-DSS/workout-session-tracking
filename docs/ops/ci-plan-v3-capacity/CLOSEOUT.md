# CI PLAN V3 — closeout de capacité

9 novembre 2026. **CODE MERGED / CANONICAL PENDING / CLOSEOUT DRAFT**.
Cette archive documentaire ne transforme pas une étape en cours en réussite.

## Livraison vérifiée

PR381 HEAD `48ec5ec939e4a11aaef6cb4f95804bdf817c7387`, merge
`3fcf0911da816cd1158aecb9cff14dc810eb0afe`, base31b89f9 ; commit de merge,
garde du SHA, aucune nouvelle autorisation de merge, aucun bypass/force-push.
CI PR42536619908 completed/success, onze jobs. 7924 backend passants,3 ignorés ;
69 suites/749 mobiles+TypeScript. Le seul cas supplémentaire est la partition
à six dans un test existant : tous les anciens tests sont conservés.

| Shard | Tests passants | Ignorés | Échantillons | Minimum disponible MiB | Workers |
|---|---:|---:|---:|---:|---:|
| 1 | 1659 | 0 | 44 | 6312 | 2 |
| 2 | 1716 | 2 | 47 | 4439 | 2 |
| 3 | 1493 | 1 | 35 | 7820 | 2 |
| 4 | 1501 | 0 | 49 | 4684 | 2 |
| 5 | 1555 | 0 | 31 | 7241 | 2 |

Chaque commande effective montre pytest -n 2 ; swap libre minimal3071MiB pour
chaque série, durées pytest de368,03 à581,40s. Tous les minima observés dépassent
4096MiB. Cinq suffisants sur cette PR ; six non utilisé. Les échantillons ne
constituent pas une garantie universelle contre tout futur shutdown.

Les cinq artefacts data ont été combinés ; coverage.xml téléchargé,186classes,
15826lignes valides/14687couvertes,92,8%. Comparaison avec l’artefact réel de
PR379 : mêmes fichiers et comptes de lignes, aucune omission ni baisse.
SonarPR381 : OK, zéro bug/vulnérabilité/hotspot/smell nouveau,92,8% app.
Les états et seuils n’ont pas changé.

Local : CI_INFRA full borné exit0,418/418fichiers,202lots,adaptations4→2→1,
pic1805MiB sous budget1869. RED3≥5 puis184CItests verts, Ruff/budget260≤548,
spec/OpenSpec15/15. Revue fraîche sans Critical/Important/Minor. L’avertissement
actionlint local préexistant est documenté dans DELIVERY ; check lint réel vert.

## Canonique et archive

Run42537647816 sur le merge3fcf091 : en cours à la préparation. La PR de
maintenance reste draft et ne fusionne qu’après preuve de ce canonique et de
son propre HEAD. Si cinq insuffisant au canonique, correction six dans le scope
approuvé avant toute clôture. Les deux tâches archivées encore ouvertes portent
le suivi canonique et la reprise de PLAN, pas des invariants supprimés.

Archive : openspec/changes/archive/2026-11-09-ci-plan-v3-capacity ; spec
delivery/ci-runner-capacity. Ce closeout ne change aucun code CI/app/SCI/mobile,
aucune migration, politique DATA, activation ou baseline. Pas de sweep local
répété pour cette maintenance documentaire ; contrôles DOCS applicables.

Après succès distant : reprendre PLAN#380 sur le canonique frais, vérifier son
HEAD et son canonique, puis cleanup uniquement sans travail unique. Le reçu
vivant de maintenance et la passation finale portent les résultats ultérieurs,
sans réécrire les verdicts annulés des anciens runs.

## Décisions et limites

Le « continue » opérateur après proposition concrète est le GO du correctif
borné ; s’il était mal interprété, aucun produit n’est activé et le diff reste
reviewable. Les jugements distants non fournis par le reviewer restent des gates
réelles ; la cause kernel/service antérieure reste inconnue. Pas de changement
d’algorithme/workers/cache/runner ni sept shards sans autre scope. Les gardes
structurelles antérieures sont conservées après inspection de l’agrégateur réel ;
leur dette reste distincte, compensée ici par tests et artefacts réels.
Aucun mineur de revue différé. Preuves hors worktree :
/private/tmp/auren-plan-v3-runtime-review-evidence/.
