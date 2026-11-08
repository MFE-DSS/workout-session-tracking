# Décision demandée — capacité CI PLAN

Actualisation 9 novembre 2026 : **GO BUILD reçu par « continue »**, [autorisation](BUILD_AUTHORIZATION.md). Les statuts proposés ci-dessous conservent leur instant de préparation ; vérification de capacité en cours, aucun succès distant anticipé.

8 novembre2026. **PROPOSITION LOCALE, aucun code CI modifié, aucun commit/push.**
[Design exact](design.md), [scope](proposal.md), [tâches](tasks.md),
[exigences](specs/delivery/ci-runner-capacity/spec.md). Base31b89f9.

Le code PLAN est fusionné #379 après7923backend/3skip et749mobile+TS, pixels
acceptés. Son canonique et le closeout#380 restent ouverts : deux premiers logs
montrent shutdownrunner à20/46MiB disponibles et swap0 ; les relances ciblées
présentent aussi une étapepytest annulée, sans nouveau commit. Les premiers
logs complets sont conservés ; les causes des derniers arrêts ne sont pas
encore attestées. Aucun verdict annulé n'est présenté comme passé.

## Autorisation proposée

GO BUILD CI limité au design : cinq shards, passage à six seulement si cinq
reste sous le plancherHEALTHY existant4096MiB ; arrêt au-delà. Même partition
exacte par fichiers, mêmes tests/exclusion unique, deux workers effectifs,
chaque artefact et couverture combinée complète, checks requis inchangés,
shadow reuse et sécurité inchangés. App/SCI/SDK/API/migrations/visuel inchangés.

Fichiers CI lease : ci.yml, ci_test_shards.py, tests de topologie et consommateurs
CI, documentation d'exploitation. Full local borné du tierCI_INFRA, vraie CI PR
et canonique, mesures non vides, revue code, merge sous GO permanent quand prêt.
Si cinq est insuffisant sur PR, vérifier six avant merge ; si canonique régresse,
correction six dans ce scope, sans déclarer une clôture prématurée.

## Revue

Lecteur frais distinct : aucun Important restant avant planification ; deux
précisions mineures intégrées (ordre5→6et workers réels vérifiés par logs).
OpenSpec strict15/15 et spec protocol passants ; ce sont preuves de préparation,
pas de capacité positive à5/6. Aucun nouveau diagnostic biologique ou moteur.

Ce GO est distinct parce que le [lease PLAN](../blueprint-first-session-runtime/BUILD_SCOPE.md)
exclut ces fichiers d'infrastructure et CLAUDE§6 exige
«propose → revue de l'opérateur → apply». Le GO MERGE permanent restera applicable
après ce GO de build ; aucune nouvelle approbation de merge routinière demandée.
