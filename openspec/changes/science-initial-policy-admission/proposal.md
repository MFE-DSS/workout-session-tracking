# SCI-P02-INITIAL-POLICY-ADMISSION — admission du système effectif

## Why

Le mandat C `SCI-P02-INITIAL-POLICY-ADMISSION/1.0.0-MANDATE` du 7 novembre 2026 autorise l'évaluation et le design. Il ne donne pas de GO BUILD fonctionnel distinct. Le canonique `2b52f4984e375faad0a1488feef1bfe3bcab01b0` contient le producteur isolé `initial-policy-producer/2.0.0`, mais aucune politique initiale admise/servie ni aucun vrai READY. Les sorties réelles, et pas seulement les rapports précédents, sont auditées dans le [dossier d'admission](../../../docs/science/sci-p02-initial-policy/admission-system-01/REPORT.md).

## What Changes

- Ouvrir un enfant borné, seul propriétaire de la **prochaine admission**, du parent `science-initial-plan-policy`, qui reste ouvert et conserve ses livraisons historiques.
- Décider C1..C6 séparément ; proposer `NOT_ADMITTED` pour le système effectif, sous revue scientifique indépendante encore requise.
- Décrire les trois corrections d'admission directement pertinentes, les tests futurs et le protocole de collecte temporelle positive.
- Proposer un contrat successeur versionné si l'on retient les prescriptions opérationnelles et la projection qualitative v2 ; aucune modification implicite des exigences READY v1.
- Remettre au PLAN les identités/versions réellement présentes et les conditions d'une future admission, sans activation.

## Capabilities

### New Capabilities

- `science/initial-policy-admission` : décision six gates, intégrité du binding, temporalité positive et frontière READY versionnée.

### Modified Capabilities

Aucune exigence canonique existante modifiée dans cette préparation. Une évolution future de `science/blueprint-first-plan` requiert sa propre revue explicite du contrat et des consommateurs dans ce change SCI ; PLAN consomme la version admise et ne la redéfinit pas.

## Impact

Écritures de cette passe exclusivement dans ce change et `docs/science/sci-p02-initial-policy/admission-system-01/`. Propriétaire science ; fichiers de code envisagés après GO dans design.md, jamais autorisés par cette liste seule. Le parent n'écrit pas une admission concurrente. PLAN possède acquisition/snapshot/transport/ownership, DATA ses politiques et RELEASE sa recette. Pas de divergence iOS/Android ici : aucun client ni transport modifié.

## Non-goals

Ni recherche musculaire générale, nouvelle curation/pull/calibration-time, réadmission des quatre pull retenus inutilisés, E0/catalogue, réécriture de v1, registre JSON d'admission, fixtures historiques, API/UI, persistance, migration, activation, READY synthétique ou déploiement. Le socle MOB03 livré n'est pas rouvert.

## Approval boundary

**APPROVED_FOR_PLANNING / ASSESSMENT_AND_DESIGN_ONLY.** Le build isolé historique de calibration-time ne vaut pas GO BUILD de ce nouvel enfant. Ce dossier propose des décisions ; son auteur n'est pas le reviewer indépendant et aucune signature scientifique n'est simulée. Le GO MERGE permanent ne donne ni ce GO BUILD ni GO DEPLOY. Une approbation fonctionnelle devra nommer les corrections, le contrat choisi et le périmètre du binding ; elle ne transformera pas un temps expérimental en preuve.

## Complete and rollback

Préparation complète quand les six gates, sources/SHA, oracles futurs, protocole temps, limites et handoff sont relus sans Important non résolu ; elle n'est pas l'admission complète. Le build ne sera COMPLETE qu'après admission réelle de toutes ses conditions, vérification du vrai producteur et intégrité des rejeux. En cas de retrait : aucune activation, conserver les versions historiques et rendre POLICY_UNAVAILABLE/NOT_SERVED ; invalider le nouveau binding sans réécrire l'historique. Aucun rollback de données n'est nécessaire pour cette préparation.

## Apply autorisé — étape1 seulement

Le 7 novembre, après remise et revue de ce design, l'opérateur a répondu « Valider uniquement ce build SCI isolé ». [BUILD_AUTHORIZATION](BUILD_AUTHORIZATION.md) borne l'apply : trois diagnostics successeurs/intégrité, registre vide, évaluateur et fixtures/tests de refus. Les descriptions DESIGN_ONLY ci-dessus retracent la phase préparatoire ; elles ne constituent pas un GO du contrat successeur, de l'admission positive ou du runtime. La présente PR livre uniquement cette étape1 avec verdict scientifique NOT_ADMITTED. Les gates positives C1..C6 et leur preuve restent explicitement ouvertes dans le parent et le handoff, jamais cochées par réussite technique.
