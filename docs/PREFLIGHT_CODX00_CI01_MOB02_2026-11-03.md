# AUREN — préflight d’intégration CODX-00 / CI-01 et préparation MOB-02

> Rapport historique de reprise. État de livraison actuel : [GOV-SONAR-01 / CI-01](GOV_SONAR_01_DELIVERY_2026-11-03.md).

Contrôle : 3 novembre 2026, vers 19:05 Europe/Paris (18:05 UTC).
Directive : préparation et revue uniquement ; designs CODX-00/CI-01 acceptés, aucune nouvelle exploration.
**Verdict : PR GREEN / MERGE PENDING ; MOB-02 n’est pas encore prête à apply.**

## 1. HEAD et checks relus sur GitHub

Canonique : `claude/sprint-reporting-fitness-app-V7Qr6`, SHA
`fcfbcd766c0d2e19feb15850897d51e03aca5570` ; elle n’a pas intégré les deux PR.

| PR | HEAD actuel | Résultat vérifié |
|---|---|---|
| [#346 CODX-00](https://github.com/MFE-DSS/workout-session-tracking/pull/346) | `7d70c2f359bc5e41eb17947756a207d2716cfeed` | OPEN, non draft, MERGEABLE/CLEAN ; 2 commits inchangés ; 8 jobs CI et tous les checks externes réussis, dont Gitar et SonarCloud Code Analysis |
| [#347 CI-01](https://github.com/MFE-DSS/workout-session-tracking/pull/347) | `764b4520c5fcd007ea53c29dce3467ef175f2ca8` | OPEN, non draft, MERGEABLE/CLEAN ; 3 commits inchangés ; 9 jobs CI et tous les checks externes présents réussis, dont SonarCloud Code Analysis |

Sources : `gh pr view` avec HEAD/base, commits, reviews, mergeability et statusCheckRollup ; API des threads.
Les deux listes de reviews et de threads sont vides. Aucune nouvelle approbation humaine n’est déduite de ces listes.
Runs verts : [CODX-00 41668162468](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/41668162468),
[CI-01 41680437230](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/41680437230).
Ce dernier est bien un événement `pull_request`, associé au HEAD `764b452…` et à `.github/workflows/ci.yml`.

## 2. Intégration séquentielle : conflit documentaire anticipé

Ordre conservé : **CODX-00 d’abord → CI-01 ensuite → closeout vérifié → rebase MOB-02**.

Chaque PR est actuellement fusionnable sur `fcfbcd7`. Cependant la simulation sans déplacement de branche :

```sh
git merge-tree --write-tree 7d70c2f359bc5e41eb17947756a207d2716cfeed 764b4520c5fcd007ea53c29dce3467ef175f2ca8
```

retourne **exit 1 : conflit de contenu dans `docs/strategy/SPEC_REGISTRY.md` uniquement**.
Les deux PR insèrent une ligne sous le même en-tête de tableau. Ce n’est pas un conflit de contrat/spec.
L’arbre temporaire avec marqueurs `fbcdde91d8974a7c606d65bb05ab8e0ab7546b1d` est un diagnostic,
**pas un commit livrable ni une nouvelle canonique**. Aucun merge/rebase réel n’a été effectué.

Résolution préparée : conserver intégralement les deux entrées, `codex-openspec-adapter` puis
`mobile-ci-checks`, avant l’entrée GOV-01 ; conserver tous les autres enregistrements et renseigner les
statuts à partir des résultats réels. Ne pas choisir globalement « ours » ou « theirs ».

Après GO MERGE avec méthode approuvée :

1. Revérifier le HEAD et les checks de #346, intégrer CODX-00 et relever le SHA canonique réellement obtenu.
2. Vérifier sa CI canonique/attestation et Sonar selon le protocole du dépôt avant la suite.
3. Préserver les mises à jour documentaires locales CI-01 avant toute remise à jour de sa branche.
   Réconcilier CI-01 avec cette canonique et résoudre le registre en conservant les deux entrées.
   Choisir une méthode sans réécriture publiée par défaut ; aucun force-push implicite.
4. Relever nouveau HEAD, merge-base et diff effectif CI-01. Exécuter `check_scope` sur ce diff, puis son
   minimum requis. Si `ci_infra` reste le verdict, le sweep local borné et la CI réelle restent requis.
   Ne pas réutiliser le vert de `764b452…` comme preuve de cette nouvelle intégration.
5. Obtenir CI et qualité externes vertes sur le nouveau candidat CI-01, puis seulement intégrer #347
   sous le GO applicable. Vérifier ensuite le HEAD canonique et son verdict final.

Le SHA résultant et la validation sur nouvelle base sont **non disponibles avant les merges autorisés**.
Le sweep de 7147 tests et les 422 tests mobiles du sprint précédent restent des preuves historiques
documentées, pas des exécutions répétées pendant ce préflight.

## 3. Check mobile requis : proposition vérifiée

Nom exact : **`mobile checks (Jest + TypeScript)`**.

| Point | Observation |
|---|---|
| Unicité | Une seule déclaration de ce nom dans `.github/workflows/`, job `mobile-checks` de `ci.yml` ; un seul check correspondant sur #347 |
| Déclenchement PR | `pull_request:` sans filtre ; `paths-ignore: docs/**` concerne seulement `push` ; run final PR observé |
| Exécution | Aucun `if` de job ni `needs` conditionnel ; Node 22, `npm ci`, Jest puis typecheck |
| Échecs | Aucun `continue-on-error` dans ce job ou ses steps ; l’échec rend le job et le workflow rouges |
| Diagnostic après Jest rouge | Typecheck conditionné par installation réussie et absence d’annulation ; les deux étapes ont effectivement échoué sur des sondes distinctes dans le run 41679982474 |
| Protection actuelle | API de protection : seuls `pytest + QA scripts` et `SonarCloud`, tous deux app_id `15368` ; `strict=false` |
| Règles supplémentaires | API des règles actives pour cette branche : `[]` |

Le workflow rouge ne suffit pas à garantir à lui seul le blocage du merge : le job mobile indépendant
n’est actuellement **pas** un check requis. La protection n’a pas été modifiée pendant cette préparation.
La lecture fonctionne ; le droit d’écriture administrateur n’a pas été testé par une mutation.
Les options existantes, notamment `strict=false` et `enforce_admins=false`, ne sont pas renforcées implicitement.

Instructions opérateur précises, à appliquer après intégration CI-01 :

1. Ouvrir [les paramètres des branches](https://github.com/MFE-DSS/workout-session-tracking/settings/branches).
2. Éditer la protection applicable à `claude/sprint-reporting-fitness-app-V7Qr6`.
3. Dans « Require status checks to pass before merging », **conserver** `pytest + QA scripts` et `SonarCloud`.
4. Ajouter exactement `mobile checks (Jest + TypeScript)`, fournisseur **GitHub Actions** (app_id `15368`).
   Conserver les autres réglages ; enregistrer.
5. Relire via API : `GET /repos/MFE-DSS/workout-session-tracking/branches/claude%2Fsprint-reporting-fitness-app-V7Qr6/protection/required_status_checks`.
   Confirmer les **trois** noms et app_id, puis sur la prochaine PR vérifier que le check mobile apparaît requis.

Ne pas ajouter ce check avant #346 : cette PR n’en contient pas la définition et pourrait rester en attente.
Sans droit administrateur, transmettre ces instructions au propriétaire du dépôt. Aucun état « protection
configurée » ne sera annoncé avant relecture effective de l’API.

## 4. Closeout après autorisation : préconditions et conservation du travail

- Mettre à jour les rapports et le registre avec les vrais SHAs de merge, CI canonique et résultats Sonar.
- Archiver `codex-openspec-adapter` et `mobile-ci-checks` selon OpenSpec/contrats du dépôt, après merges
  et satisfaction des tâches ; conserver leur déclaration `skip_specs: true` et toutes les baselines visuelles.
- Avant nettoyage, comparer commits/diffs au canonique et inventorier les fichiers non suivis/ignorés utiles.
  Les worktrees contiennent actuellement du travail unique :
  - CODX-00 : rapport, registre et tasks modifiés localement.
  - CI-01 : rapport, registre et tasks modifiés localement.
  - MOB-02 : décisions opérateur dans proposal/design et case 1.1 de tasks.
- Aucun de ces worktrees ne peut être supprimé sur la seule base d’une PR verte. Intégrer ou sauvegarder
  les documents uniques avant nettoyage ; préserver le checkout utilisateur, `grixis/` et ses réglages.

## 5. MOB-02 : état exact du change et diff

Branche : `sb/mob-02-session-native-integration`.
HEAD : **`8c0f4d7c1cfb3d011646617d0138714e94c2673d`**.
Merge-base actuel avec la canonique : **`fcfbcd766c0d2e19feb15850897d51e03aca5570`**.
Rebase sur la canonique résultant des deux merges : **pas encore effectué**.

La comparaison du dossier du change entre `backup/mob-02-proposal-091110b` et le HEAD rebasé est vide :
la proposition initiale et sa sémantique sont préservées. Les seules modifications de travail depuis ce HEAD :
`design.md` +10 lignes, `proposal.md` +15 lignes, `tasks.md` +1/−1 (décisions acceptées et case 1.1 cochée).
Diff total de travail contre la canonique : **5 fichiers, 241 insertions**, tous dans le change ; aucun build produit.
La divergence affichée avec la branche distante MOB-02 n’autorise aucun force-push.

Décisions conservées : D-MOB02-1=A (deux GET fréquence/historique, lecture seule, utilisateur authentifié,
sources canoniques, données absentes omises) ; D-MOB02-2=AUREN-MARK-V1 seule pendant la restauration du jeton.
La lecture du code confirme `restore()` → tous les états `outbox`, tandis que `outboxRows()` exclut `acked`.
Le vrai appelant est `clients/mobile/ConnectedApp.tsx` ; `onStatus` y relit actuellement `outboxRows()`.
La préparation ne transforme pas ces constats en fonctionnalités déjà corrigées.

## 6. Tâches MOB-02 restantes (IDs originaux conservés)

La tâche **1.1** est faite ; les **12** suivantes restent ouvertes :

| ID | Travail restant |
|---|---|
| 2.1 | Exécuter `check_scope` sur le build et suivre son plan de vérification |
| 2.2 | `serverStateFromOutbox`, tests purs et relecture au démarrage/à chaque statut ; série acceptée toujours reçue après relance |
| 2.3 | Envoi unique Démarrer/Reprendre, état d’attente et test du double appui |
| 2.4 | Singulier/pluriel de reprise ; information hors ligne aussi pour la reprise serveur |
| 2.5 | Marque de démarrage selon D-MOB02-2 |
| 2.6 | Substitution hors ligne/refusée explicite ; exercice d’origine restauré en cas de refus |
| 2.7 | Bilan : données sourcées ou omises selon D-MOB02-1 |
| 3.1 | GET `/api/mobile/v1/me/training-preferences` et `/api/mobile/v1/me/sessions`, lecture seule, isolation `user_id` et tests |
| 3.2 | Déploiement du canonique en production avant recette appareil, via workflow existant et autorisation applicable |
| 4.1 | Gate visuelle 77/77 ; rendu avant/après et validation opérateur avant commit UI |
| 4.2 | Passe Android sur production : relance après acceptation, double appui, refus, hors ligne, bilan ; puis iPhone |
| 4.3 | Rapport conforme aux contrats UI, décisions relues et registre ; PR |

Le rebase final et le GO BUILD MOB-02 restent des préconditions supplémentaires, pas des cases inventées
dans la proposition originale. Aucune portée MOB-03, MOB-04, MOB-05 ou ultérieure n’est ajoutée.

## 7. Plan de vérification MOB-02 requis avant apply

- **Journal complet** : fixtures persistées `acked`, `failed` et en attente, relance et transitions ; priorité
  des états et compteurs exacts, aussi bien dans l’exécution que le bilan. Tester restauration native et
  contrat de journal ; ne pas remplacer le journal complet par les seuls éléments encore à envoyer.
- **Vrai câblage ConnectedApp** : monter le consommateur réel avec frontières réseau/journal contrôlées ;
  exercer restauration au boot, callbacks de statut et accusés, props réellement reçues par les écrans.
  Les tests purs seuls ne satisfont pas 2.2. Vérifier absence de régression lors de callbacks asynchrones.
- **Démarrer/Reprendre** : double appui avant réponse → un seul appel ; attente visible, succès, erreur et
  possibilité de réessayer ; reprise locale et serveur ; singulier/pluriel.
- **Substitution** : hors ligne, envoi au retour réseau, refus explicite et restauration de l’origine,
  acceptation et suite de séance praticable. Lire la réponse canonique avant de choisir une raison affichée.
- **Lectures bilan** : authentification, isolation entre deux utilisateurs, fréquence/historique présents,
  absents, vides ou indisponibles ; valeurs sourcées ou omises, aucun défaut inventé ; aucun effet d’écriture.
- **UI/appareils** : marque seule pendant jeton lent ; comparaison aux baselines sans réapprobation ; revue
  du rendu avant commit ; repos/notification et états dégradés sur Android puis iPhone connecté avec opérateur.
- **Livraison** : tests ciblés et broad sweep selon scope, Jest/typecheck en CI, qualité externe ; aucun
  résultat appareil, déploiement ou gate visuelle revendiqué tant qu’il n’a pas été exécuté.

## 8. Validation de cette préparation et conditions de sortie

Préparation documentaire : `check_scope` classe les fichiers de rapport et décisions en **DOCS**.
Pas de full sweep ni de relance CI pour ce préflight ; les checks distants existants ont été relus sur leurs HEAD.
Résultats frais : `check_spec_protocol.py` **exit 0** dans le checkout du rapport et le worktree MOB-02 ;
`openspec validate session-native-integration --strict --no-interactive` **exit 0**, change valide ;
`git diff --check` MOB-02 **exit 0**. Aucun test produit n’est relancé pour cette préparation documentaire.

| Condition « ready to apply » | État présent |
|---|---|
| CODX-00/CI-01 intégrés et canonique vérifiée | **NON** — GO MERGE distinct non reçu |
| Change MOB-02 rebasé sur ce canonique | **NON** — cible non encore créée |
| Implémentation MOB-02 autorisée | **NON** — cette directive autorise seulement préparation/revue |
| Plan couvrant appelant réel et états dégradés | **OUI** — §7, à exécuter pendant le build |

**Conclusion de préflight : préparation terminée, apply bloqué par les préconditions explicites.**
Le prochain point opérateur est le GO MERGE distinct avec méthode d’intégration approuvée ; le GO BUILD
MOB-02 sera lui aussi explicite. Aucun merge, archive, nettoyage ou changement de protection n’est réalisé.
