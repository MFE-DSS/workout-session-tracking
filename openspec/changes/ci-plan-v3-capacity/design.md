# Design soumis — cinq shards, six seulement sur preuve de besoin

Actualisation 9 novembre 2026 : **GO BUILD reçu par « continue »**, [autorisation](BUILD_AUTHORIZATION.md). Les statuts proposés ci-dessous conservent leur instant de préparation ; vérification de capacité en cours, aucun succès distant anticipé.

**PROPOSED / NO_GO_BUILD — 8 novembre2026.** Autorité d'apply absente ; le GO
PLAN contrôlé ne lease pas les fichiers CI. CLAUDE§6 impose revue avant apply.

## Brainstorming / Options / Risques / Choix retenu

1. Moins de workers : ne réduit pas le cumul de tests par VM, mécanisme déjà
   documenté dans ci_test_shards.py ; conserver2 évite une régression non mesurée.
2. Lots de processus neufs par VM : mémoire bornée mais nouveau mécanisme de
   couverture/agrégation et plus de code. À réserver si le sharding existant
   échoue dans la limite autorisée.
3. Sharder existant5,6si nécessaire : proposition retenue par l'agent, à approuver.
   Même ensemble de tests, moins de fichiers par VM ; seule la capacité change.
   Réduit le travail par machine, augmente le nombre de runners. N'implique
   aucune souscription ou taille de machine nouvelle.

Le candidat5ramène418fichiers à84/84/84/83/83, proche des82/81/81du dernier
scale historique sain. Le coût par fichier varie : aucune marge positive n'est
inférée de ce seul compte. Six est une extension bornée si5ne remonte pas au
plancherHEALTHY existant4Gio ; au-delà, nouvelle décision.

## Delta exact autorisable

- scripts/ci_test_shards.py : DEFAULT_SHARDS5puis6si preuve insuffisante, motif
  daté ajouté. Algorithme, signatures et EXCLUDED inchangés.
- .github/workflows/ci.yml : matrice explicite1..5, éventuellement1..6 ; la garde
  structurelle la compare à DEFAULT_SHARDS. Message «les3shards non exécutés»
  dérivé de --shard-count pour ne pas ajouter une copie de ce chiffre.
- tests/test_ci_shard_topology.py : minimum de capacité suit la valeur réellement
  admise ; les invariants ancrés sur tests/ et l'exclusion exacte restent stricts.
  Aucun test diminué pour faire passer une couverture partielle.
- Agrégateur inchangé : expected dérivé, fichier manquant dur, tous artefacts
  combinés en UNE coverage.xml. Attestation/tree-policy inchangée ; nouvelle
  topologie doit être réellement testée, shadow reuse reste désactivé.

Aucun changement app/contrats/SDK/API/migration/fixtures produit ou baseline.
Les chemins CI ci-dessus ne figurent pas dans les manifestes SCI consultés.

## Preuves et règle d'itération

TDD : garder la garde de capacité rouge avec3avant modification, puis verte
avec candidat. Vérifier matrice incomplète/dupliquée, artefact manquant,
EXCLUDED élargi et partition complète non circulaire. Les modules existants
ci_runner_stability, ci_shard_topology et ci_canonical_attestation sont le broad.

TierCI_INFRA : check_scope, Ruff/budget/spec/OpenSpec, full local via
scripts/run_local_sweep.sh seulement, vrais checks CI. Pas de script CI sur Mac.
Revue code fraîche avant livraison, merge commit au HEAD gardé sous GO permanent.

CI PR puis canonique : tous tests, checks obligatoires et artefacts complets ;
extraire les sériesCI_RESOURCE de chaque shard, nombre d'échantillons>0,
minMemAvailable>=4096MiB et swap/timing explicites ; commande effective
`pytest -n 2` confirmée dans chaque log, pas seulement variable supposée.
Mesure vide ou nombre de workers non prouvé = pas de verdict.
Comparer ensemble/compte des tests et couverture combinée à la base7923/3skip
(en tenant compte de tout test CI ajouté, sans en retirer). Le périmètre de
couverture app reste inchangé ; comparer le résultat et expliquer toute variation,
pas de seuil modifié.

Si5passe les tests mais reste sous4096MiB sur la PR, passer à6et vérifier son
nouveau HEAD avant tout merge. Si5était acceptable sur PR mais échoue seulement
sur le canonique, conserver la gate ouverte et livrer la correction6par PR sous
ce même scope autorisé. Aucun CLOSED avant PR et canonique acceptables.
Si6échoue, diagnostiquer/rapporter sans agrandir silencieusement.
Pas de changement de cache, concurrence par worker, timeout ou classe de runner.

## Coordination et reprise de PLAN

PR379 reste une livraison code contrôlée, pas CLOSED. PR380 reste draft jusqu'à
un canonique complet réussi. Après intégration du correctif CI, synchroniser
sa branche avec le canonique frais sans force-push, préserver les deux ajouts
SPEC_REGISTRY, vérifier le nouveau HEAD complet puis son canonique. Les anciens
runs annulés restent annulés, jamais réétiquetés verts. Aucun critère DATA,
appareils physiques, activation ou déploiement clos par ce correctif.

## Relecture de faisabilité

Lecteur frais distinct,8novembre2026 : mécanisme actuel compatible5/6, aucun
Important restant avant planification ; GO CI distinct requis. Deux précisions
mineures intégrées : capacité insuffisante sur PR=>6avant merge, et preuve des
workers effectifs par log. Ce ne sont pas des résultats de build/CI positive.
