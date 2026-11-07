# Calibration/time01 — décision concrète attendue et handoff

6novembre2026. **Proposition prête pour revue, pas implémentation livrée.** Le mandat E impose de s'arrêter à la frontière d'approbation si ce spike ne possède pas son GO BUILD. L'ancien GO et les spikes clos ne sont pas révoqués ou rouverts.

## Une décision de portée

Approuver [le delta OpenSpec](../../../../openspec/changes/science-initial-plan-policy/calibration-time-01.md) et DESIGN.md pour réaliser **le producteur successeur isolé**, les DTO d'évaluation/calibration/temps hors schéma partagé, sources/bundles dédiés, tests déterministes et fixtures réellement générées. Conventions visibles : réglage opérationnel observé ≠ vrai RIR ; aucun ajustement kg automatique ; réemploi comparable reconfirmé ; temps conditionnel par composantes/structure, hypothèses étiquetées ; anciens comportements/pins conservés.

Ce GO autoriserait ensuite implémentation→revues→CI→publication/merge sous GOV-MERGE-01, sans nouvelle autorisation routinière. Il n'autoriserait ni API/UI/acquisition persistée, ni modification E0/catalogue/v1/rail, ni activation/déploiement. Aucune politique temporelle ou sélection non soutenue n'est admise par le simple GO de réalisation.

Après GO : relire le canonique courant et comparer les37sources pinées ; adapter le plan au diff réel avant apply, signaler tout conflit d'autorité, ne pas réécrire les anciens pins/rejeux pour masquer une dérive. Le plan d'implémentation détaillé et le TDD viennent ensuite, pas avant l'approbation de ce design.

## Restent des gates de preuve, pas des questions déjà réglées à redemander

| Gate | Preuve/livrable qui la ferme |
|---|---|
| Définition opérationnelle de calibration | Revue de la procédure/définition limitée et sorties de transitions ; aucune prétention de précision d'effort non validée |
| Temps positif pour la population/contexte cible | Composantes/bornes et protocole réellement applicables ; validation ou conventions produit explicitement acceptées avec limites ; aucun défaut en secondes inventé |
| Sélection/projection effectives | Assemblage versionné curation/pull, contexte de réalisation G17, affectation globale et exposition15zones vérifiées ; aucune reclassification historique |
| Intégrité de décision | Empreinte complète sur observations/bundle en plus de request_fingerprint v1 ; vérificateur de l'enveloppe ; anciens rejeux conservés |
| Admission complète / vrai READY | Toutes politiques effectives réellement admises, tous budgets/candidats/contraintes/protocole de départ soutenus ; sortie générée par le vrai producteur et validate_exchange, jamais autorité de test promue |

## Préparation de SCI-P02-INITIAL-POLICY-ADMISSION

Après le build/revue autorisé, reprendre cette table gate par gate : importer les sorties réelles des dix familles Phase D, figer digests/versions et distinguer données utilisateur suffisantes de politiques suffisantes. Si le temps reste sans base positive validée, en faire le bloqueur précis ; ne pas exiger une charge connue pour tout READY si un protocole de calibration admis et temporalisé suffit. Aucun nouveau chantier d'exposition par muscle sauf candidat effectivement bloquant.

Handoff mobile actuel : FirstPlanClient/v1 restent inchangés, producteur runtime NOT_SERVED. Le nouveau sidecar n'est pas un transport mobile servi et son empreinte n'est pas vérifiée implicitement par ce client. Un futur adaptateur et ses ownership/consentements/contrats de transport doivent être coordonnés séparément dans OpenSpec.

## Vérification de cette passe

Sources canoniques inventoriées/pinées avant toute implémentation ; recherche primaire indépendante réalisée en lecture seule. [Revue de construction](BUILDER_REVIEW.md) : trois ambiguïtés résolues en conventions proposées, contrôle final « nothing important left ». Aucun nouveau test fonctionnel, code review d'implémentation, CI, commit/push/merge ou admission READY de ce spike n'est revendiqué. Base canonique :8e987c6 ; les preuves CI de cette base ne sont pas des tests des fonctions proposées. Contrôles documentaires de cette proposition consignés après leur exécution.

Contrôles réalisés : **check_scope DOCS ; check_spec_protocol passant**. Pas de sweep Python/mobile, Ruff ou autre test de produit pour ce diff documentaire, conformément au verdict local.49cas de construction spécifiés ne sont pas49tests passants. Le worktree et ses dix fichiers de proposition restent disponibles pour la revue ; aucune fusion de build anticipée.

## Actualisation après la décision et réalisation

Les sections précédentes conservent la proposition historique. L'opérateur a confirmé « Valider le build isolé proposé » : le build est autorisé. Voir désormais [DELIVERY.md](DELIVERY.md) et le [paquet d'admission préparé](INITIAL_POLICY_ADMISSION.md) pour le comportement réellement implémenté et ses limites. La proposition documentaire initiale n'est plus le statut courant ; la politique reste distinctement NOT_ADMITTED/NOT_SERVED, sans READY.
