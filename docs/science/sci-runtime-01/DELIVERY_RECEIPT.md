# SCI-RUNTIME-01 — livraison du correctif sélectif

26 novembre2026 — Europe/Paris. **CODE CANONICAL GREEN / CLOSEOUT IN_VERIFICATION / OPERATIONAL HOLD.** Parent9ef96e39aac400bc53583f62aecafc09f4dda1e3 ; GO exact [enregistré](../../../openspec/changes/archive/2026-11-26-sci-runtime-01/BUILD_AUTHORIZATION.md).

## Comportement et verdicts

Le lecteur conserve et atteste les octets entiers du catalogue ; seule la chaîne au chemin `records[*].exercise_operational.curation.notes` reste opaque pendant la lecture complète. Les autres champs gardent4096octets, les budgets128fichiers/16Mio et la validation grammaticale complète sont conservés. Les quatre consommateurs emploient la même vue ; aucun rôle, alias, exécution canonique, source SCI ou digest n'est remplacé. `bounded_json` conserve son refus générique de4302>4096.

| Objet | Verdict / portée |
|---|---|
| Catalogue | PASS local : source canonique entière,107records et toutes données non éditoriales conservés |
| Parité SCI | PASS local :109résolutions nom/alias, rôles bruts, V2 et bundleV3/inventory2 ; budget partagé sous les limites |
| Sécurité des chemins | HOLD opérationnel : parcours d'inspection par descripteurs testé contre symlinks, traversal, permissions non fiables et faux digest ; ACL/mounts/profil réels non qualifiés |
| Runtime Linux exact | HOLD : Docker ne répond pas, aucune cible fidèle exécutée ; Mac3.11.14/SQLite3.50.4 ne qualifie pas Linux |
| Lecteur global | NOT_QUALIFIED, toujours désactivé ; aucune route QA rendue opérationnelle |
| Livraison code | PR448 HEAD7bd1a69f00080780eafcda0f9c6f5450dd1831b1 ; merge5f53394687a9cd656db4cc068a16cae625cfa8e1 ; CI PR45808999852 SUCCESS ; CIcanon45812177491 completed/success11jobs |

Le harness `python -m tools.muscle_observed_load_qualification` est un outil de **préqualification** : inventaire réel, lecture d'autorité sûre depuis des descripteurs et témoins enfant Linux bornés. Il termine avec code2/HOLD et n'exporte aucun profil opérationnel QUALIFIED. Les métriques HTTP/SQL/CPU/RSS/concurrence non exécutées restentNULL ; la campagne complète du protocole demeure nécessaire. Il ne modifie ni loader produit, source, base, flag, service ou configuration de VPS.

## Vérification effectivement exécutée

- RED2tests catalogue absente → GREEN31tests ; parité complète réelle ensuite. RED2tests harness absent → GREEN.
- Source actuelle réellement modifiée :114/128fichiers partagés et3243128/16777216octets ; aucune hausse de budget. Vues Legacy/V2/V3 sans port catalogue synthétique.
- Lecteur/API complet local :124PASS,3LinuxSKIP ; broadconsommateursSCI186PASS/1skip existant. PythonQA3.11.14 surDarwin. Avertissement existant Starlette/httpx conservé, pas de dépendance modifiée pour le masquer.
- ScopeSHARED_CODE ; Ruff fichiers touchés PASS, budget260≤548, Bandit des2nouveaux modules PASS, protocole/OpenSpec strict PASS. Pas de full sweep local systématique ; CI PR réelle45808999852 completed/success,11jobs :9023backendPASS/3ignorés,140suites1610mobiles+TypeScript,77visuels. Le shard5 exécute le worker/catalogue,1920PASS sans skip surPython3.11.18 ; ce n'est pas la qualification3.11.14.
- Scan optionnel Gitleaks répertoire entier :1signal historique, identifiant d'issueSonar dans SONAR_AUDIT_01_REPORT.md:197, source inchangée ; pas un credential. Aucun ignore/règle ajouté. Scan du delta et range Git conservé comme gate séparée.
- Revue indépendante du diff entier : aucunCritical/Important.300cas différentiels et6escapes opaques passants chez le reviewer ; il ne prétend pas avoir rejoué les124/186tests.

Mineurs différés : métadonnées du parent immédiat non ajoutées à la liste d'inventaire bien qu'il soit contrôlé ; ancien commentaire/port synthétique de test désormais inutilisé pour le catalogue. Aucun fail-open ou masquage de la vraie lecture constaté.

Les rulings et leurs coûts figurent dans [le ledger](../../../openspec/changes/archive/2026-11-26-sci-runtime-01/IMPLEMENTATION_LEDGER.md) : livraison partielle autorisée, campagne cible non acquise, loader historique hors scope, gates CI et closeout à vérifier séparément. L'alerte Sonar13 n'est ni fermée ni dismissée. Aucun certificat global de sécurité.

## Prochaine opération

Livrer l'archive/closeout documentaire après CIcanonique code45812177491 completed/success11jobs (9023backend/3ignorés,1610mobiles+TS,77visuels). La PR448 a été fusionnée par commit de merge gardé auHEAD exact, sans thread bloquant ni bypass. SonarPR448 ERRORconsultatif :19smells,0bug/0vuln/0hotspot,coverage91,8%,nouvelle93,45238095238095%. Aucun état/règle/seuil changé. L'activation/DATA/OVH/APK/OTA reste exclue. Après livraison, la prochaine opération runtime sera la campagne sur une cible Linux jetable fidèle et autorisée, sans modifier QA.

Les preuves privées sont dans `/Users/martinfeldmann/auren-review/sci-runtime-01-evidence-20261126/` ; le [reçu de préparation](QUALIFICATION_RECEIPT.md) reste historique et ne remplace pas ce reçu de livraison.

Sonar canoncode5f533946, analyse90e77d75-798e-4b25-9874-711a03538259 : ERRORconsultatif,9bugs/9vulnérabilités/768smells/0hotspot,coverage91,8%,nouvelle91,76158940397352%. Ces métriques globales comprennent la dette historique ; aucune innocence globale ni issue fermée n'est déduite. PR448 nouvelle0bug/0vuln.
