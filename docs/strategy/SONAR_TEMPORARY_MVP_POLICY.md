# GOV-SONAR-01 — SonarCloud consultatif

**TEMPORARY — MVP DEVELOPMENT** · Décision opérateur : 3 novembre 2026.
SonarCloud : **ADVISORY / NON-BLOCKING**, après arrêt de l’abonnement payant.
Cette policy prend effet sur la canonique après livraison de son changement de gouvernance ; sa proposition
et son application GitHub sont deux états distincts. Elle est commune à iOS et Android.

## Contrôles obligatoires conservés

| Contrôle | Exécution / preuve attendue |
|---|---|
| Jest mobile | `npm test -- --ci --runInBand`, job CI-01 `mobile checks (Jest + TypeScript)` |
| Types mobiles | `npm run typecheck` dans le même job, erreurs bloquantes |
| Backend | shards pytest et agrégat `pytest + QA scripts`, règles de scope/attestation existantes conservées |
| Visuel | `visual contract (DA-GOV-01)`, comparaison aux baselines approuvées, aucune auto-approbation |
| OpenSpec | `openspec validate --all --strict --no-interactive` obligatoire avant livraison ; gate locale, aucun job CLI OpenSpec actuellement présent en CI |
| Scope/protocole | `check_scope` local ; classification CI et `check_spec_protocol.py` existants |
| Sécurité statique | Bandit `-ll`, Gitleaks, `pip-audit -r requirements-lock.txt --strict` et leurs conditions d’application actuelles |
| Autres gardes | Ruff/budget, actionlint/shellcheck, auth scope matrix, drift des dépendances et migrations applicables restent actifs |

Tout échec d’un contrôle obligatoire bloque. Une faille de sécurité confirmée, un secret exposé ou une action
destructive reste un arrêt dur. Aucun de ces contrôles n’est remplacé par Sonar, ni supprimé par cette policy.
La CI complète et les checks exacts doivent être relus ; `check_scope` continue de dicter les vérifications locales.

## Résultats Sonar conservés

Le scanner automatique reste inchangé. Conserver son résultat réel et les liens de scan/gate ; écrire
`Quality Gate ERROR` lorsqu’il vaut ERROR, jamais « vert » par convention. Un échec ou une indisponibilité
Sonar seuls ne bloquent pas sous cette policy, mais sont consignés séparément des contrôles obligatoires.
Ne modifier ni seuils ni sévérités, ne pas auto-résoudre d’issues, ne pas déclarer toute dette inoffensive.
Si le scan est indisponible ou occasionne des coûts inutiles, sa désactivation est une décision séparée,
avec patch/documentation explicites ; aucun changement de compte ou de licence n’est effectué ici.
Les commentaires historiques REQUIRED du workflow ne sont pas une configuration de protection ; cette
policy remplace leur ancienne règle de livraison sans modifier le résultat du scanner.

## Protection proposée et vérification

État observé : branche `claude/sprint-reporting-fitness-app-V7Qr6`, checks requis `pytest + QA scripts`
et `SonarCloud`, app_id GitHub Actions **15368**, `strict=false`, aucun ruleset actif.

| Nom exact | Avant (API) | Après proposé |
|---|---|---|
| `pytest + QA scripts` | Requis | **Conservé requis** |
| `SonarCloud` | Requis | **Consultatif, retiré des requis** |
| `SonarCloud Code Analysis` | Pas requis | Consultatif, résultat externe conservé |
| `lint (ruff budget + bandit + actionlint + shellcheck)` | Actif en CI, pas requis par protection | **Ajouter requis** |
| `visual contract (DA-GOV-01)` | Actif en CI, pas requis par protection | **Ajouter requis** |
| `mobile checks (Jest + TypeScript)` | Vérifié sur #347, pas encore sur canonique | **Ajouter requis après intégration/vérification CI-01** |

Préparer puis appliquer seulement sous autorisation applicable :

1. Relire protection et rulesets avant mutation ; préserver tout autre check apparu entre-temps et ses app_id.
2. Éditer la protection de la branche dans les paramètres GitHub. Retirer uniquement le check Sonar ;
   conserver tous les autres ; ajouter lint et visuel existants. Aucun bypass, ni changement implicite de strict/admins.
3. Après CI-01 intégrée et vérifiée, ajouter le nom exact mobile, fournisseur GitHub Actions.
4. Relire `GET /repos/MFE-DSS/workout-session-tracking/branches/claude%2Fsprint-reporting-fitness-app-V7Qr6/protection/required_status_checks`
   et les règles actives ; confirmer les noms/app_id et, sur la PR suivante, leur caractère requis.

Sans droits administrateur, transmettre ces étapes au propriétaire. La réussite des lectures ne prouve pas
le droit d’écriture ; aucune protection n’est déclarée appliquée avant relecture. Ne pas ajouter un nom de
check OpenSpec inexistant : son obligation contractuelle locale n’est pas une automatisation GitHub.

Payload final proposé : `GOV_SONAR_01_REQUIRED_CHECKS_PROPOSED.json` dans ce dossier, pour le seul endpoint
`required_status_checks`, **après CI-01 intégrée et vérifiée**. Avant CI-01, omettre uniquement l’entrée mobile.
Ce snapshot de proposition doit être réconcilié avec une lecture fraîche avant écriture : ne pas supprimer
un autre check ajouté entre-temps, ni remplacer ses app_id. Les autres paramètres de protection restent intacts.

## Incident de référence, sans requalification de la dette

Canonique **`60bea5d28eeaecc1eba1c71aefe7186793c4098a`**, CODX-00 #346.
Run Actions **41691072708 : 8/8 succès**. Check externe **SonarCloud Code Analysis : FAILURE**, gate **ERROR**.
Analyse Sonar **9f30706f-ad36-41d6-91e0-468446be5388**, révision exacte, 3 novembre à 18:25:15 UTC.

| Condition de gate | Valeur | Seuil | Résultat |
|---|---:|---:|---|
| `new_coverage` | 93,9 % | minimum 80 % | OK |
| `new_duplicated_lines_density` | 0,0 % | maximum 3 % | OK |
| `new_bugs_severity` | 25 | maximum 9 | **ERROR** |
| `new_code_smells_severity` | 20 | maximum 14 | **ERROR** |
| `new_vulnerabilities_severity` | 10 | maximum 9 | **ERROR** |

Période : `previous_version`, depuis le 10 avril 2026. Valeurs de sévérité distinctes des totaux bruts.
Les analyses de 13:33:36 et 18:25:15 UTC montrent les mêmes totaux : **8 bugs, 6 vulnérabilités,
439 code smells, couverture 93,8 %**. La recherche des issues non résolues créées depuis 18:09 UTC renvoie
**0 résultat dans cet intervalle inspecté** ; cela ne prouve pas l’absence de toute vulnérabilité nouvelle.
**Une évaluation exhaustive de sécurité n’a PAS été réalisée.** Aucune issue existante n’est classée
collectivement comme faux positif ou inoffensive. La policy change le caractère bloquant, pas le diagnostic.

## Réévaluation obligatoire

Une revue sécurité et qualité est requise **avant chacun** des événements suivants : élargir l’accès à des
bêta-testeurs externes ; activer des abonnements payants ; introduire photos de progression ou mesures
physiques sensibles ; publier en production. Cette revue est une gate préalable, pas une tâche à reporter
après lancement. Elle examine les issues, les accès/données et la couverture de la chaîne de contrôle.
Elle peut retenir Sonar OSS gratuit si éligibilité vérifiée, CodeQL si disponible, ou une chaîne équivalente
vérifiée. Ni éligibilité ni couverture de sécurité équivalente ne sont présumées dans ce changement.
Sa décision de sortie/révision de la politique est versionnée ; l’historique des verdicts est conservé.

## Non-goals

Pas de produit/MOB-02, migration, baseline, baisse de seuil, auto-résolution, scan supprimé ou bilan sécurité exhaustif.
