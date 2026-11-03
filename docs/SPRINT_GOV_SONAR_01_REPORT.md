# GOV-SONAR-01 — politique temporaire Sonar

Date : 3 novembre 2026. Branche : `sb/gov-sonar-01-advisory`. Base : `60bea5d`.
Change : `sonar-advisory-mvp`. **Verdict : politique intégrée et protection appliquée ; archive dans cette clôture.**

## Brainstorming / Options / Risques / Choix retenu — avant le diff normatif

L’opérateur fournit l’arbitrage : Sonar **ADVISORY / NON-BLOCKING**, **TEMPORARY — MVP DEVELOPMENT**.
Les choix ne sont pas réouverts. La proposition prépare une PR propre à la gouvernance.

| Option | Décision / risque |
|---|---|
| Maintenir Sonar obligatoire malgré arrêt de l’abonnement | Écarté par l’opérateur |
| Sonar consultatif, scanner et vrais résultats conservés | Retenu ; suivi transparent des alertes et revue avant élargissement |
| Désactiver automatiquement le scan | Décision séparée à proposer si indisponibilité/coût ; non appliquée |
| Réduire les autres gates ou requalifier toute dette | Interdit |

Le changement documentaire aligne contrats et contexte OpenSpec. Aucun comportement produit, migration,
baseline ou workflow n’est changé. La protection est proposée, pas annoncée configurée.

## État inspecté

- Canonique `60bea5d28eeaecc1eba1c71aefe7186793c4098a`, CODX-00 #346 mergée.
- CI-01 #347 HEAD `5d675b6e69217bb0bbc52bdcd925f68cf879c5c8`, base canonique exacte, ouverte/CLEAN.
- Run PR `41692608283` : 9 jobs et tous les checks externes verts au contrôle frais.
- Protection : `pytest + QA scripts` et `SonarCloud`, app_id 15368 ; `strict=false` ; règles actives `[]`.
- Sonar canonique : ERROR ; Actions 8/8 succès ; incident détaillé dans la policy, sans audit exhaustif revendiqué.
- Le nouveau sweep CI-01 est lancé depuis le début dans `/private/tmp/auren-ci01-gov-full-sweep.log` ;
  tant qu’il n’est pas terminé, aucune validation complète n’est revendiquée.

## Périmètre interdit

Code produit, seuils Sonar, auto-résolution d’issues, scan supprimé, sécurité affaiblie, baseline, build MOB-02.
Le GO MERGE #347 reste acquis ; le nouveau changement GOV-SONAR-01 nécessite sa propre décision de merge.

## Validation de la proposition

`check_scope` : **ISOLATED**, aucun full sweep local requis pour ce diff documentaire/configuration.
Ruff fichiers neufs : sans objet, aucun Python modifié ; budget **264 ≤ 548**. Protocole documentaire OK,
OpenSpec strict **5/5**, `git diff --check` OK. Tests ciblés et broad sweep des consommateurs de gouvernance
(spec protocol, classification de scope, actions/runtime et stabilité CI, protocole UI, tokens) : **139 passants**.
Le diff de `.github/`, `app/`, `tests/` et des baselines est **vide** : aucun contrôle existant modifié.

Revue indépendante à contexte neuf : un constat P2 corrigé, la tâche 3.3 doit suivre le HEAD/base effectifs
après intégration GOV, pas figer 60bea5d. Le sweep 5d675b6/60bea5d n’est donc pas une preuve de rebase futur.
Aucune modification de code n’a été nécessaire pour cette correction documentaire.

Preuve CI-01 relue : run `41692608283`, étapes **Bandit sécurité**, **pip-audit runtime**, **Gitleaks**,
**spec protocol**, **auth scope matrix** et **drift requirements** toutes `success`. Backend, Jest/types
et visuel sont verts. Cela vérifie l’activité des contrôles, pas une évaluation complète de sécurité.

Le payload proposé `docs/strategy/GOV_SONAR_01_REQUIRED_CHECKS_PROPOSED.json` n’a pas été envoyé à GitHub.
Il conserve QA, propose lint/visuel et mobile après CI-01 ; une relecture fraîche doit préserver tout autre
check apparu entre-temps. Aucune protection configurée n’est revendiquée.

## Livraison et archivage — relevé de clôture du 2026-11-03

Les sections intermédiaires précédentes sont historiques. Les archives sont portées par cette clôture,
livrée via PR protégée sans push direct ni bypass. Les SHA et CI de la clôture documentaire sont relevés
dans la remise opérateur et les métadonnées de livraison après intégration. Aucun GO BUILD MOB-02 donné.

GOV-SONAR-01 #348 est mergée par `cc80ddd`, sous GO explicite ; CI canonique `41706456907` : 8/8 jobs
Actions réussis. **TEMPORARY — MVP DEVELOPMENT**, Sonar **ADVISORY / NON-BLOCKING**. Son vrai ERROR
est conservé sur `cc80ddd` puis `edd7351` : scores de sévérité 25>9, 20>14 et 10>9. Aucun seuil ni état d’issue
modifié, scanner et workflows inchangés ; sa désactivation serait une décision séparée.

La protection phase A puis B a été appliquée et relue : QA conservé, lint/visuel ajoutés, puis exactement
`mobile checks (Jest + TypeScript)` après vérification canonique CI-01. Les quatre checks ont app_id 15368 ;
strict=false et les autres réglages sont inchangés. Les snapshots sont conservés hors dépôt public.
Bandit, Gitleaks, audit des dépendances, backend, Jest/types, visuel et scope/protocole restent obligatoires.
OpenSpec strict reste obligatoire localement ; aucun faux job CLI OpenSpec n’est annoncé dans GitHub.

Les comptes bruts Sonar sont stables dans les analyses inspectées, aucune issue créée identifiée dans
l’intervalle initial ; cela n’est ni une absence de toute vulnérabilité ni un audit de sécurité exhaustif.
Les issues existantes ne sont pas déclarées collectivement inoffensives. La revue sécurité/qualité reste
obligatoire avant bêta élargie, paiements, photos/mesures sensibles ou production.

Le change est archivé sous `openspec/changes/archive/2026-11-03-sonar-advisory-mvp`, 8/8 tâches.
Le diff de gouvernance et le bilan complet sont dans `GOV_SONAR_01_DELIVERY_2026-11-03.md`.

Contrôle de la clôture : `check_scope` ISOLATED ; **142 tests ciblés/broad sweep passants**,
budget Ruff264≤548, protocole documentaire et OpenSpec strict3/3 passent ; aucun Python neuf,
Ruff nouveaux fichiers sans objet. Diff de code/workflow/baseline vide ; aucun full sweep local additionnel
requis pour ce diff de clôture. Les archives et les cinq fichiers de specs vivantes ont été comparés par SHA-256.
