# SCI-RUNTIME-01 — livraison du correctif sélectif

26 novembre2026 — Europe/Paris. **ENGINEERING VERIFIED LOCALLY / PR CI PENDING.** Parent9ef96e39aac400bc53583f62aecafc09f4dda1e3 ; GO exact [enregistré](../../../openspec/changes/sci-runtime-01/BUILD_AUTHORIZATION.md).

## Comportement et verdicts

Le lecteur conserve et atteste les octets entiers du catalogue ; seule la chaîne au chemin `records[*].exercise_operational.curation.notes` reste opaque pendant la lecture complète. Les autres champs gardent4096octets, les budgets128fichiers/16Mio et la validation grammaticale complète sont conservés. Les quatre consommateurs emploient la même vue ; aucun rôle, alias, exécution canonique, source SCI ou digest n'est remplacé. `bounded_json` conserve son refus générique de4302>4096.

| Objet | Verdict / portée |
|---|---|
| Catalogue | PASS local : source canonique entière,107records et toutes données non éditoriales conservés |
| Parité SCI | PASS local :109résolutions nom/alias, rôles bruts, V2 et bundleV3/inventory2 ; budget partagé sous les limites |
| Sécurité des chemins | HOLD opérationnel : parcours d'inspection par descripteurs testé contre symlinks, traversal, permissions non fiables et faux digest ; ACL/mounts/profil réels non qualifiés |
| Runtime Linux exact | HOLD : Docker ne répond pas, aucune cible fidèle exécutée ; Mac3.11.14/SQLite3.50.4 ne qualifie pas Linux |
| Lecteur global | NOT_QUALIFIED, toujours désactivé ; aucune route QA rendue opérationnelle |
| Livraison | CI/PR/merge à renseigner après leurs résultats réels |

Le harness `python -m tools.muscle_observed_load_qualification` est un outil de **préqualification** : inventaire réel, lecture d'autorité sûre depuis des descripteurs et témoins enfant Linux bornés. Il termine avec code2/HOLD et n'exporte aucun profil opérationnel QUALIFIED. Les métriques HTTP/SQL/CPU/RSS/concurrence non exécutées restentNULL ; la campagne complète du protocole demeure nécessaire. Il ne modifie ni loader produit, source, base, flag, service ou configuration de VPS.

## Vérification effectivement exécutée

- RED2tests catalogue absente → GREEN31tests ; parité complète réelle ensuite. RED2tests harness absent → GREEN.
- Lecteur/API complet local :124PASS,3LinuxSKIP ; broadconsommateursSCI186PASS/1skip existant. PythonQA3.11.14 surDarwin. Avertissement existant Starlette/httpx conservé, pas de dépendance modifiée pour le masquer.
- ScopeSHARED_CODE ; Ruff fichiers touchés PASS, budget260≤548, Bandit des2nouveaux modules PASS, protocole/OpenSpec strict PASS. Pas de full sweep local systématique ; CI globale obligatoire à venir.
- Scan optionnel Gitleaks répertoire entier :1signal historique, identifiant d'issueSonar dans SONAR_AUDIT_01_REPORT.md:197, source inchangée ; pas un credential. Aucun ignore/règle ajouté. Scan du delta et range Git conservé comme gate séparée.
- Revue indépendante du diff entier : aucunCritical/Important.300cas différentiels et6escapes opaques passants chez le reviewer ; il ne prétend pas avoir rejoué les124/186tests.

Mineurs différés : métadonnées du parent immédiat non ajoutées à la liste d'inventaire bien qu'il soit contrôlé ; ancien commentaire/port synthétique de test désormais inutilisé pour le catalogue. Aucun fail-open ou masquage de la vraie lecture constaté.

Les rulings et leurs coûts figurent dans [le ledger](../../../openspec/changes/sci-runtime-01/IMPLEMENTATION_LEDGER.md) : livraison partielle autorisée, campagne cible non acquise, loader historique hors scope, gates CI et closeout à vérifier séparément. L'alerte Sonar13 n'est ni fermée ni dismissée. Aucun certificat global de sécurité.

## Prochaine opération

Publier ce seul scope après les contrôles locaux finaux, vérifier les quatre checks protégés au HEAD exact, puis appliquer GOV-MERGE-01. L'activation/DATA/OVH/APK/OTA reste exclue. Après livraison, la prochaine opération runtime sera la campagne sur une cible Linux jetable fidèle et autorisée, sans modifier QA.

Les preuves privées sont dans `/Users/martinfeldmann/auren-review/sci-runtime-01-evidence-20261126/` ; le [reçu de préparation](QUALIFICATION_RECEIPT.md) reste historique et ne remplace pas ce reçu de livraison.
