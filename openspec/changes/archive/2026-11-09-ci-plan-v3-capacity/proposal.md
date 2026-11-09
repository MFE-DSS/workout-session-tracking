# CI-PLAN-V3-CAPACITY — capacité des runners, couverture intégrale

Actualisation 9 novembre 2026 : **GO BUILD reçu par « continue »**, [autorisation](BUILD_AUTHORIZATION.md). Les statuts proposés ci-dessous conservent leur instant de préparation ; vérification de capacité en cours, aucun succès distant anticipé.

8 novembre2026. **PROPOSED / NO_GO_BUILD.** Base31b89f98985044a9ee40d75610d387976ff26d7c.
Le code PLAN est intégré par PR379 ; son closeout380 reste draft, bloqué par la
CI canonique. Ce change indépendant ne modifie aucun comportement app/SCI.

## Why

La PR379 a passé7923tests backend, trois ignorés, tous les checks requis. Son
shard2 a néanmoins fini avec59Mo de mémoire disponible et swap épuisé. La CI
canonique42526541847 et la PR380/42527005736 ont ensuite reçu un shutdown du
runner dans le même shard, avec20/46Mo disponibles et swap0. Une relance ciblée
a été autorisée sans nouveau commit ; l'étape pytest canonique est de nouveau
annulée. Aucun échec d'assertion n'a été relevé dans les logs disponibles avant
ces arrêts. La pression mémoire est observée ; la cause système détaillée n'est
pas certifiée. Le résultat annulé n'est jamais converti en PASS.

Le sharder documente déjà que réduire les workers ne réduit pas le cumul mémoire
du même nombre de tests par machine. Sa partition par fichiers accepte5/6 ;
l'agrégateur dérive son compte. Les trois shards actuels répartissent418fichiers
en lots de140/139/139fichiers sur trois VM, un shard par VM. La suite historique saine
était à82/81/81fichiers ; cinq shards donneraient84/84/84/83/83. Cette comparaison
motive le candidat ; elle ne prouve pas sa capacité avant CI réelle.

## What changes, après GO seulement

Candidat5shards,6uniquement si les mesures réelles montrent que5reste sous la
borneHEALTHY existante4096MiB. Garder2workers explicites par runner, round-robin
par fichier, exclusion unique test_v1_acceptance, partition exacte, artefacts de
chaque shard et rapportcoverage.xml combiné unique. Aucun skip, seuil abaissé,
cache activé ou variable de dépôt modifiée.

Lease : .github/workflows/ci.yml, scripts/ci_test_shards.py,
tests/test_ci_shard_topology.py et tests CI consommateurs si une assertion doit
suivre la capacité minimale admise ; docs/ops et append au SPEC_REGISTRY.
Ni app/mobile/data/migrations ni anciennes sources SCI pinées.

## Impact et limites

Le check requis pytest + QA scripts garde son nom et attend tous les shards.
Workers/maxRAM/timeouts, sécurité/mobile/visuel/OpenSpec et shadow reuse inchangés.
CI_INFRA : full local borné et vraie CI obligatoires. Mesures non vides PR et
canonique sur chaque shard, tests complets et couverture combinée vérifiée.
Si6ne suffit pas, STOP/rapport ; pas de7+, modification d'algorithme ou runner
payant implicite. Aucun déploiement.
