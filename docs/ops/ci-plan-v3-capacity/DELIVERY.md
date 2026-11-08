# CI PLAN V3 — capacité de la suite complète

9 novembre 2026. **CANDIDATE / validation en cours, pas CLOSED.**
Base canonique `31b89f98985044a9ee40d75610d387976ff26d7c`.
[Design](../../../openspec/changes/ci-plan-v3-capacity/design.md),
[autorisation](../../../openspec/changes/ci-plan-v3-capacity/BUILD_AUTHORIZATION.md).

## Brainstorming / Options / Risques / Choix retenu

Les runs canoniques/closeout PLAN ont répété un shutdown runner, avec 20/46 MiB
disponibles et swap nul dans les premières traces. Moins de workers ne réduit
pas le cumul de tests par VM ; lots de processus neufs seraient un autre
mécanisme. Réutiliser le sharder existant avec cinq runners est le choix borné,
six seulement si cinq n’atteint pas la marge HEALTHY existante de 4096 MiB.
Le nombre de fichiers n’est pas une preuve de mémoire disponible.

## Changement et invariants

Constante et matrice passent ensemble de trois à cinq. Le message de verdict
réutilisé dérive aussi le nombre via la CLI existante. Partition par fichier,
round-robin, unique exclusion test_v1_acceptance.py, deux workers, timeouts,
classe de runner, coverage app, contrôles sécurité et noms protégés inchangés.
L’agrégateur dérive toujours le nombre attendu et échoue si un artefact manque.
Shadow reuse reste désactivé ; aucun produit/SCI/mobile/migration/visuel modifié.

## Preuves avant publication

Garde de capacité reproduite RED `3 >= 5`, puis 184 tests CI passants, deux
avertissements de dépendances. Partition réelle : 418 fichiers → 84/84/84/83/83.
Ruff concernés passant, budget 260 ≤ 548, spec protocol et OpenSpec strict15/15.
Revue fraîche code : aucun Critical/Important/Minor, readiness distante non
certifiée. Full local du tier CI_INFRA via run_local_sweep.sh réussi : 418/418 fichiers, 202 lots, deux adaptations 4→2→1, pic 1805 MiB sous budget 1869 MiB ; exit 0. Aucun fichier sauté.

Actionlint local avec analyse shell relève SC2046 sur la commande find inchangée
de lint ; même avertissement reproduit au HEAD de base. Syntaxe actionlint sans
scan shell valide, configuration distante error/error inchangée. Ce constat ne
remplace pas le check lint requis de la PR.

## Gates distantes encore ouvertes

Tous les contrôles PR/canonique, tests complets et couverture combinée ; chaque
shard doit montrer deux workers effectifs, série CI_RESOURCE numérique non vide,
minMemAvailable ≥ 4096 MiB, swap et durée. Si cinq insuffisant, vérifier six
avant merge ; si le canonique régresse, correction six sous le même scope.
Six insuffisant ou mesures manquantes : STOP, aucune gate affaiblie.

Après preuve canonique, synchroniser le closeout PLAN #380 sans force-push et
préserver les ajouts au registre. Les runs annulés gardent leur état réel.
Activation/déploiement/DATA/RELEASE restent séparés.
