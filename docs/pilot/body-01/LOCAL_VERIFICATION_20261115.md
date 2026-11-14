# BODY — reçu local final avant publication

15 novembre 2026 — parent canonique1462482a, checkpoint407 f899b735.
Périmètre complet classé MIGRATION, sources produit et tests empreintées inchangées.

| Campagne | Couverture | Résultat |
|---|---|---|
| Runner canonique initial | 258 fichiers terminés | 4756 PASS ; arrêt mémoire sur le fichier suivant, code3 |
| Recovery Home | Tous les74nodes collectés | 74 PASS, pic301Mo |
| Training Preferences, déjà connu lourd | Tous les97nodes collectés | 97 PASS, pic294Mo |
| Queue restante | 178 fichiers complets | 3670 PASS /1ignoré, pic1105Mo |
| Union disjointe des fichiers | 438/438, énumération canonique vérifiée | **8597 PASS /1ignoré** |

La première exécution a atteint1613Mo pour un budget1600Mo. Les reprises gardent
le même watchdog et plafond, avec cwd et listes explicites dans des harnais hors
dépôt. Aucun fichier/test ajouté aux exclusions canoniques. Ce n'est pas un seul
run ininterrompu réussi. Les empreintes attestent la stabilité de tous les tests
et des78 chemins runtime/tests du diff pendant la campagne.

Mobile :100suites /1215tests PASS ; TypeScript exit0. Migration patterns,
roundtrip vide, drift et snapshot exit0. Ruff fichiers neufs PASS ; budget260≤548.
Bandit-ll :0Medium/High,8Low existants ; aucune déclaration globale d'innocuité.
Protocole et OpenSpec strict25/25 PASS avant les seules notes finales.

Revue indépendante entière et addendum ciblé sans Critical/Important ; deux
mineurs corrigés RED→GREEN, limites de snapshot conservées dans le reçu de revue.
Pixels acceptés avec réserves non bloquantes (DA08_NATIVE_ACCEPTANCE.json).
Android complet/physique, accessibilité exhaustive et release distincts.

Preuves persistantes :
`/Users/martinfeldmann/auren-review/body-da08-integration-20261114/` :
FINAL_LOCAL_RECEIPT.json, FINAL_SWEEP_COVERAGE.json, RESOURCE_CONTINUATION_PLAN.json,
FINAL_RUNTIME_SHA256.json et journaux de chaque campagne. Les données privées du
banc restent hors Git et hors ZIP public. CI du HEAD final, Sonar et merge restent
à observer ; aucun ancien run n'est réutilisé comme preuve du nouveau HEAD.
