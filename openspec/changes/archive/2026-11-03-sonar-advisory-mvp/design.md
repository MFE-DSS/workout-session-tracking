# Design — GOV-SONAR-01

## Context

Voir `proposal.md`. Observé : `SonarCloud` est requis par la protection, `SonarCloud Code Analysis` ne l’est pas ;
les seuls autres checks requis sont `pytest + QA scripts`. Aucun ruleset actif. Le scanner est un job terminal,
aucun contrôle fonctionnel/sécurité ne dépend de lui. Ses verdicts restent visibles même si son nom n’est plus requis.
Les commentaires historiques du workflow ne constituent pas la politique normative.

## Goals / Non-Goals

**Goals:** rendre l’arbitrage temporaire explicite et cohérent dans les contrats, sans masquer les résultats.
**Non-Goals:** modifier le workflow, le produit, une baseline, une sévérité Sonar ou l’état des issues.
Gouvernance commune iOS/Android ; aucune divergence de plateforme.

## Decisions

- Une policy normative dédiée, référencée par `CLAUDE.md §4`, le protocole et OpenSpec, porte les gates
  obligatoires, l’incident et les déclencheurs de réévaluation ; les rapports historiques sont conservés.
- Retirer le nom Sonar de la protection, conserver les autres, puis ajouter les jobs fonctionnels/sécurité
  existants vérifiés. Le scanner reste inchangé : ses erreurs ne sont ni converties ni cachées.
- Ne pas ajouter une nouvelle dépendance/CI dans ce changement documentaire. La validation OpenSpec stricte
  reste obligatoire en local ; son absence d’automatisation GitHub est documentée.
- Payload de protection limité à `required_status_checks`, conservant `strict=false` et app_id existant.
  Sa préparation est séparée de son application ; droits administrateur et relecture API nécessaires.
- Préparer GOV-SONAR-01 dans une PR distincte. Le GO MERGE existant vise #346/#347 ; il ne fusionne pas
  automatiquement la nouvelle PR de gouvernance. La décision de politique est fournie, son diff est soumis.

## Risks / Trade-offs

- [Perdre de vue une alerte] → joindre les erreurs Sonar exactes aux comptes rendus ; une faille confirmée
  reste un arrêt dur ; aucune évaluation exhaustive de sécurité revendiquée.
- [Confondre gates contractuelles et protection GitHub] → tableau avant/après et relecture API ; pas de faux
  nom de check OpenSpec à ajouter tant qu’il n’existe pas.
- [Scanner coûteux/non disponible après arrêt de l’abonnement] → proposer sa désactivation dans une décision
  séparée ; aucun changement de compte, licence ou scan automatique ici.
- [Protéger le mobile avant sa présence sur la canonique] → n’ajouter ce nom qu’après CI-01 intégrée et vérifiée.

## Migration Plan

Revue du diff normatif → PR GOV-SONAR-01/GO MERGE propre → intégration vérifiée → revalidation complète de
CI-01 selon sa base effective → merge #347 autorisé → protection actualisée et relue → closeout/rebase MOB-02.
Un retour au mode REQUIRED exige une nouvelle décision versionnée, sans effacer les résultats de la période MVP.
