# AUREN — GOV-SONAR-01, proposition et readiness CI-01

Date : 3 novembre 2026. **TEMPORARY — MVP DEVELOPMENT**.
Décision opérateur : Sonar **ADVISORY / NON-BLOCKING**, abonnement payant arrêté.
**État : GOV et CI-01 intégrées et vérifiées ; protection finale appliquée et relue ; clôture documentaire en préparation.**

## 1. Diff de gouvernance proposé

[PR #348](https://github.com/MFE-DSS/workout-session-tracking/pull/348),
[diff reviewable](https://github.com/MFE-DSS/workout-session-tracking/pull/348/files).
Branche `sb/gov-sonar-01-advisory`, HEAD **`d3a6a5d1c0d22702e00698ac928e5f38a0881117`**,
base canonique **`60bea5d28eeaecc1eba1c71aefe7186793c4098a`**.

GO explicite reçu : **« GO MERGE #348 + protection proposée »**. PR #348 fusionnée par commit de merge
**`cc80dddebe8f9b72a6302a54a5436153c7bc2561`**. Sa CI PR `41703410132` et tous ses checks externes sont
verts ; aucun thread non résolu ni conflit. CI canonique GOV : `41706456907`, **8/8 jobs Actions réussis**.
Sonar sur `cc80ddd` reste **ERROR consultatif**, analyse `6a442318-ed52-4c6c-9419-c30b80b9d10d`.

- `CLAUDE.md §4` et protocole de livraison : Sonar est relevé avec son vrai statut, seul son caractère
  bloquant est retiré ; les échecs des autres contrôles et les failles confirmées restent bloquants.
- Policy normative `docs/strategy/SONAR_TEMPORARY_MVP_POLICY.md` : incident, contrôles, protection,
  réévaluation obligatoire avant bêta externe élargie, paiements, photos/mesures sensibles ou production.
- Contexte `openspec/config.yaml`, change `sonar-advisory-mvp`, rapport et registre alignés.
- Protection phases A et B appliquée et relue par API après intégration CI-01 vérifiée : les quatre checks
  fonctionnels/sécurité sont requis. Scanner automatique et workflows **inchangés**.
  Une désactivation du scan serait une décision distincte, documentée en cas de coût/indisponibilité.

Pas de produit, migration, baseline ou code de test changé. Les commentaires historiques REQUIRED du
workflow sont distingués de la nouvelle règle normative ; ils ne sont pas une configuration de protection.
La proposition ne suppose ni éligibilité Sonar OSS ni disponibilité CodeQL. Une revue future pourra retenir
l’un de ces outils ou une chaîne équivalente vérifiée.

## 2. Checks requis avant / après

Protection avant/après relue via API : `strict=false`, app_id **15368** ; tous les autres paramètres inchangés.

| Check exact | Avant réel | Après phases A et B vérifiées |
|---|---|---|
| `pytest + QA scripts` | Requis | **Conservé requis** |
| `SonarCloud` | Requis | **Retiré des requis, consultatif — vérifié** |
| `SonarCloud Code Analysis` | Pas requis | Consultatif, résultat externe visible |
| `lint (ruff budget + bandit + actionlint + shellcheck)` | Actif, pas requis par protection | **Requis — vérifié** |
| `visual contract (DA-GOV-01)` | Actif, pas requis par protection | **Requis — vérifié** |
| `mobile checks (Jest + TypeScript)` | Vérifié sur #347, pas requis | **Requis — phase B appliquée et relue après vérification canonique** |

Les gates locales `check_scope` et OpenSpec strict restent obligatoires. La CLI OpenSpec n’est actuellement
pas appelée dans le workflow : son obligation locale n’est pas présentée comme une automatisation GitHub.
`spec protocol` est bien exécuté en CI dans lint.

Instructions opérateur : GitHub → Settings → Branches → protection de
`claude/sprint-reporting-fitness-app-V7Qr6` → Required status checks. Retirer uniquement Sonar, préserver
QA et tous les autres noms présents à cet instant, ajouter lint/visuel puis mobile après disponibilité.
Conserver app_id et autres paramètres ; relire protection et rulesets par API après enregistrement.
Le fichier `docs/strategy/GOV_SONAR_01_REQUIRED_CHECKS_PROPOSED.json` de #348 fournit le payload final
pour `required_status_checks`, à réconcilier avec une lecture fraîche, pas à appliquer aveuglément.
L’API indique `admin=true` ; le PATCH limité à `required_status_checks` a réussi sous GO explicite, puis
une lecture indépendante de la protection complète a confirmé les trois checks et les autres paramètres.
Snapshots : `/private/tmp/auren-gov-sonar-protection/before.json`, `phase-a.json` et `phase-b.json`.
La phase B conserve les trois checks existants et ajoute exactement le mobile. Les quatre noms et app_id
ont été confirmés par une lecture indépendante de la protection complète ; les autres paramètres sont inchangés.

## 3. Sonar réel inchangé

Canonique **`60bea5d…`**, run Actions **41691072708 : 8/8 succès**,
check externe **SonarCloud Code Analysis : FAILURE**, **Quality Gate ERROR** confirmé de nouveau.

| Condition | Valeur | Seuil | Statut |
|---|---:|---:|---|
| `new_coverage` | 93,9 % | minimum 80 % | OK |
| `new_duplicated_lines_density` | 0,0 % | maximum 3 % | OK |
| `new_bugs_severity` | 25 | maximum 9 | **ERROR** |
| `new_code_smells_severity` | 20 | maximum 14 | **ERROR** |
| `new_vulnerabilities_severity` | 10 | maximum 9 | **ERROR** |

Période Sonar `previous_version` depuis le 10 avril. Totaux avant/après les analyses inspectées :
**8 bugs, 6 vulnérabilités, 439 code smells, couverture 93,8 %**, tous inchangés.
**0 issue non résolue créée identifiée depuis 18:09 UTC** dans la recherche effectuée.
**Aucune évaluation exhaustive de sécurité n’a été réalisée** ; les issues existantes ne sont pas
collectivement déclarées faux positifs ou inoffensives. Aucun seuil, état d’issue ou résultat modifié.

## 4. Preuve des contrôles conservés

CI-01 run **41692608283**, HEAD **`5d675b6e69217bb0bbc52bdcd925f68cf879c5c8`**, base **`60bea5d…`** :
**9/9 jobs réussis et checks externes verts**, relus après leur achèvement.
Mobile Jest/TypeScript, trois shards backend, agrégat QA et régression visuelle passent.
Les étapes du job lint **Bandit sécurité**, **Gitleaks**, **pip-audit runtime**, **spec protocol**,
**auth scope matrix** et **drift requirements** ont été inspectées individuellement : toutes `success`.
Le diff GOV de `.github/`, `app/`, `tests/` et des baselines est **vide**.

Validation de GOV : scope **ISOLATED**, **139 tests ciblés/broad sweep des consommateurs de gouvernance**,
budget **264 ≤ 548**, protocole documentaire OK, OpenSpec strict **5/5**, diff sans erreur.
Revue indépendante : constat documentaire P2 corrigé pour imposer la base effective, pas un SHA figé.
CI propre de GOV : run **41703410132**, **8/8 jobs et tous les checks externes verts**.

## 5. Readiness #347 et sweep complet

PR #347 : nouveau candidat **`8ff28089916b0a18b21cd30f33e55ece892cbd8d`**, base canonique
**`cc80dddebe8f9b72a6302a54a5436153c7bc2561`**. Nouvelle CI PR **41707470720**, **9/9 jobs réussis**,
checks externes verts, HEAD/base inchangés, CLEAN et aucun thread non résolu.
Le GO MERGE par commit de merge est conservé. Aucun GO BUILD MOB-02 implicite.

Le sweep `5d675b6 / 60bea5d` est **terminé : 7147 tests, 378/378 fichiers, 149 lots, exit 0**.
Deux adaptations 4→2→1, aucun fichier sauté ; pic des lots réussis 1471 Mo, budget 1600 Mo. Les tentatives
interrompues par le garde avaient atteint 1779 puis 1676 Mo. Journal : `/private/tmp/auren-ci01-gov-full-sweep.log`.
Cette preuve est désormais historique : la canonique a changé après intégration GOV.

La branche CI-01 intègre GOV sans force-push ; le conflit de registre conserve les trois entrées.
Diff de `.github/`, `app/`, `tests/` et `clients/mobile` entre les deux candidats : **vide**.
Malgré cela, la validation finale **CI_INFRA** est relancée depuis le début sur l’arbre de `8ff2808` :
`/private/tmp/auren-ci01-final-base-sweep.log`, **terminé : 7147 tests, 378 fichiers, 149 lots, exit 0**.
Deux adaptations 4→2→1, aucun fichier sauté ; pic des lots réussis **1546 Mo / budget 1600 Mo** ; tentatives
arrêtées par le garde à **1606 puis 1670 Mo** avant relecture des mêmes fichiers.
Contrôles frais : 189 gardes, 422 tests mobiles, typecheck, Ruff/budget et OpenSpec strict **6/6** passent.
Ni les 208 fichiers interrompus ni un ancien sweep ne sont substitués à cette nouvelle exécution.

Les logs de la CI finale confirment **77 tests visuels passés** et les étapes sécurité/protocole toutes réussies.
PR #347 fusionnée sous GO enregistré : **`edd7351040b911bc1a749715a238870d94966fcf`** ; arbre identique à
`8ff2808` vérifié par diff vide. CI canonique **41711441173** : **tous les huit jobs hors Sonar réussis**,
dont backend/QA, mobile, lint et visuel. Sonar consultatif sur ce même SHA reste **ERROR**, analyse
`4f5e161b-db46-48f4-802a-be71cdb904f1`, révision exacte `edd7351`, datée 20:35:55 UTC.
Le scanner Actions était encore en fin d’exécution au relevé de cette analyse ; son état n’est pas fabriqué vert.
La phase B mobile requis est appliquée et relue.

## 6. Blockers de merge restants

**Aucun blocker de merge CI-01 restant : #347 est fusionnée et ses gates obligatoires sont vérifiées.**
Reste le closeout documentaire par PR protégée (aucun push direct/bypass), la publication des archives,
le contrôle canonique de cette clôture et le rebase final MOB-02. Son implémentation attend un GO BUILD distinct.

L’erreur Sonar seule n’est plus le blocage visé par l’arbitrage : les préconditions de livraison et la
cohérence de la politique versionnée ont été traitées. #347 est fusionnée ; aucune archive, suppression ou
rebase final MOB-02 n’est encore revendiqué dans ce document.
