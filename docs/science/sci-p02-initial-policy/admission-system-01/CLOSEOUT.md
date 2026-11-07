# SCI admission étape1 — closeout borné

7 novembre2026. **Code fusionné ; admission positive NOT_ADMITTED / runtime NOT_SERVED / READY_NOT_PRODUCED.** Le closeout documentaire est proposé et reste soumis à ses contrôles et à la vérification canonique. Aucun succès distant ultérieur n'est anticipé ici ; le reçu vivant de publication est consigné dans les PR de cette livraison.

## Livraison du code vérifiée
- PR[#369](https://github.com/MFE-DSS/workout-session-tracking/pull/369), HEAD64c4c0fb0071c8481725c80546c9ccfbdf7b0a79, merge5e94cfa81e6b3a4ec5ceedbcbe90c95de464b854 ; base2b52f49. Méthode merge, garde du SHA, aucun bypass/force-push.
- [CI PR42366063678](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/42366063678) completed/success, neuf jobs : **7580backend passants, trois ignorés ;54suites/676mobiles +TypeScript**, lint/sécurité, visuel, QA et scan Sonar réussis. Ancien run42365756718 obsolète annulé (puis force-cancel du run uniquement après annulation standard restée en cours) pour libérer son remplaçant ; jamais compté comme preuve du correctif. Aucun contrôle du HEAD final annulé ou contourné.
- Local final : **363tests broad ciblés/13modules**, dont38nouveaux ; deux avertissements de dépendances. Ruff neuf/budget264≤548, Bandit, protocole, OpenSpec9/9, Gitleaks sans fuite, liens et rejeux des18nouvelles/12v2 vérifiés. ISOLATED, aucun full sweep local.
- Revues code/science distinctes : un Important code reproduit puis corrigé en une passe (unitaire +évaluateur rouges→verts, contrôle positif de vraie reconfirmation). Aucune autre Important résiduelle ; aucun second audit global revendiqué. Handoff actuel complété comme prévu.

## Sonar réel
PR369 : QualityGateERROR/Major, **cinq nouveaux CODE_SMELL python:S5778**, tous de structure de tests d'exception ; zéro bug/vulnérabilité/hotspot, couverture app93.8%, new_coverage non retournée. Cette mesure app ne mesure pas les modules isolés tools/. Dette de structure des cinq tests différée, aucun seuil/issue/gate changé. GOV-SONAR-01 consultatif conservé. Analyse canonique du SHA de merge à relever dans le reçu vivant après son exécution ; aucune réutilisation du verdict PR comme verdict canonique. Une faille confirmée resterait un arrêt dur.

## Archive et critères conservés
Archive locale produite par OpenSpec sans skip de validation : `openspec/changes/archive/2026-11-07-science-initial-policy-admission/`. Neuf exigences ajoutées à `openspec/specs/science/initial-policy-admission/spec.md`, limitées à l'évaluation négative et ses frontières d'autorité. Les tâches positives de l'archive restent non cochées et sont reprises sans réduction par [la proposition positive réservée](../../../proposals/science-initial-policy-positive-admission.md). Le parent `science-initial-plan-policy` demeure ouvert. Les quatre autres paquets A–F restent dans leur espace documentaire, sans nouveau GO.

Ce closeout est de maintenance du scope approuvé, pas une deuxième PR fonctionnelle chevauchante. L'archive ne transforme aucun critère positif en PASS. Les tâches de publication/cleanup postérieures à ce fichier reçoivent leur preuve après exécution dans les PR vivantes ; une case administrative en attente au moment du commit ne vaut pas faux résultat fonctionnel.

## Capacités et prochaine dépendance
Evaluateur `initial-policy-admission-evaluator/1.0.0`, résultat `initial-policy-admission-result/1.0.0`, diagnostics calibration/temps `1.1.0-isolated`. Registre livré vide ;14décisions NOT_ADMITTED et4rejets d'intégrité depuis vrai code sur faits synthétiques. Aucun plan, endpoint, SDK mobile, UI, migration, politique de rétention, donnée privée ou activation. Code et artefacts historiques restent inchangés.

La prochaine science porte sur protocole initial/admission effective des candidats, choix de projection/contrat READY et **base temporelle positive applicable** (modèle ou convention bornée réellement admis). Le protocole de collecte est prêt ; ni grand budget, réglage connu, LIKELY_FITS expérimental ni tests verts ne fournissent cette preuve. PLAN attend ensuite snapshot/transport/adaptateur et handoff possédés. DATA attend D-POL01..05/BODY applicables ; RELEASE garde cible/builds/appareils/GO distincts. MOB03 complet reste ouvert.

## Choix techniques consignés
- Exécution native sous GO déjà reçu, sans nouvelle revue routinière de plan ; risque si mauvais bornage : revue de scope avant intégration.
- Worktree SCI distinct pour préserver les quatre autres paquets et une PR par change ; les liens sont suivis à l'archive.
- Bootstrap de confiance = code loader versionné et pins, pas signature d'autorité ; hash du loader au manifeste d'artefacts distinct pour éviter autoréférence. Toute évolution passe revue/CI.
- Préparation/publication du closeout peut avancer pendant la vérification canonique, mais sa fusion reste bloquée jusqu'aux verdicts réellement réussis ; aucun état de réussite anticipé.

## Publication et conservation
[Run canonique du code42367593268](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/42367593268), SHA5e94cfa81e6b3a4ec5ceedbcbe90c95de464b854 : en cours à la préparation de ce fichier ; verdict final et Sonar seront relus/consignés avant merge du closeout. Le reçu vivant donnera ensuite HEAD/CI/merge/canonique du closeout et preuve de cleanup. Branches/worktrees avec travail unique, notes de revue et QA MOB02 préservés ; seuls les éléments SCI intégrés sans travail unique seront nettoyés après preuves. Aucun identifiant QA lu, aucun déploiement.
