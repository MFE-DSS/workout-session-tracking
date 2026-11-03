# AUREN — compte rendu Codex pour architecte / Product Owner

> Rapport historique de reprise. État de livraison actuel : [GOV-SONAR-01 / CI-01](GOV_SONAR_01_DELIVERY_2026-11-03.md).

Date : 3 novembre 2026. Périmètre : CODX-00 puis CI-01, avant MOB-02.
**Mise à jour après GO MERGE : CODX-00 fusionnée (`60bea5d`), check externe Sonar canonique rouge ;
CI-01 non fusionnée, reprise suspendue. Voir le [rapport d’arrêt et de reprise](CLOSEOUT_CODX00_CI01_MOB02_2026-11-03.md).**
Les statuts de livraison ci-dessous décrivent le point de remise antérieur au GO MERGE.
Ce document distingue préparation, code implémenté, tests locaux et CI distante. Il constitue le compte rendu
complet de l'état réellement atteint ; un état en attente ne vaut pas clôture.

Complément de préparation après revue architecturale :
[préflight intégration et MOB-02](PREFLIGHT_CODX00_CI01_MOB02_2026-11-03.md).
Il confirme les deux PR vertes et détaille le conflit de registre anticipé lors de l’intégration séquentielle,
la protection actuelle et les préconditions encore ouvertes avant apply MOB-02.

## 1. Résultat produit et décision de pilotage

La reprise s'appuie sur la canonique récente et conserve la gouvernance OpenSpec/AUREN existante.
Le client natif n'est pas redessiné dans ces sprints. L'effort porte sur son environnement de développement
et sur l'exécution systématique de ses tests et de ses types avant les évolutions de séance.

Ordre retenu par l'opérateur : **CODX-00 → CI-01 → MOB-02**, puis MOB-03 compte/onboarding, MOB-04 Mission,
MOB-05 progrès/journal, programmes/constructeur/exercices, salle/substitutions, profil, récupération,
abonnement et plateforme jusqu'à l'alpha. La voie assets reste parallèle.
STORE-00 suit les décisions de distribution ; les comptes Apple/Google seront **personnels**, créés
**par l'opérateur à l'atteinte de l'alpha**. Aucune création anticipée demandée ni réalisée.

## 2. CODX-00 — adaptation de l'agent et bonne base

**Implémenté et poussé, PR #346 verte, merge en attente de GO distinct.**

- Mise à jour des références : canonique `fcfbcd766c0d2e19feb15850897d51e03aca5570`, incluant le guide de reprise
  de la PR #345. Le vieux checkout `61ca08c` et les changements utilisateur sont préservés.
- Proposition MOB-02 originale `091110b` sauvegardée puis rebasée sans conflit : nouveau commit `8c0f4d7`.
  Le diff du dossier de proposition avant/après rebase était **vide**.
- Adaptateur officiel généré par OpenSpec 1.14.3 : six skills sous `.agents/skills/openspec-*`.
  Comparaison aux skills existantes : seules les invocations propres à Codex changent.
- Aucun contrat canonique, skill Claude personnalisée, baseline ou paramètre OpenSpec réécrit.
  Aucun AGENTS.md versionné ; aucun Spec Kit ajouté.
- Roadmap datée et registre actualisés. Les réglages personnels d'accès Codex sont locaux, ignorés par Git.

Branche : `sb/codx-00-codex-openspec`.
Commits : `11ec97d` (adaptateur et docs), `7d70c2f` (trace de revue/livraison).
PR : https://github.com/MFE-DSS/workout-session-tracking/pull/346
CI : https://github.com/MFE-DSS/workout-session-tracking/actions/runs/41668162468
Les **8 jobs** de ce run sont `completed/success`, dont trois shards pytest, QA, comparaison visuelle et
SonarCloud. Ce sont les résultats effectivement relus sur GitHub pendant le sprint.

## 3. CI-01 — logique et types mobiles vérifiés dans le pipeline

**Implémenté et poussé ; PR #347 prête pour revue, preuve GitHub négative validée et CI finale verte. Merge en attente de GO distinct.**

Un job indépendant `mobile checks (Jest + TypeScript)` a été ajouté au workflow existant :

- Node 22 ; dépendances installées avec `npm ci` depuis le lock existant.
- `npm test -- --ci --runInBand` : pas de watch, exécution en série.
- `npm run typecheck` : reste exécuté après un échec Jest si l'installation a réussi.
- Aucun `continue-on-error`, filtre limitant aux seuls changements mobiles, ou élargissement de permissions.
- Les jobs backend, la comparaison pixel et les triggers existants sont conservés.
- Trois gardes ciblées empêchent la disparition ou l'affaiblissement de ces vérifications.
  `actions/setup-node@v6` est inscrite dans la garde existante des runtimes, après lecture de son action.yml.

Branche : `sb/ci-01-mobile-checks`, base `fcfbcd7`.
Code propre : `eea4af1` ; sondes contrôlées : `f1a8712`, retirées du contenu final.
HEAD final sans sondes : **`764b4520c5fcd007ea53c29dce3467ef175f2ca8`**.
PR : https://github.com/MFE-DSS/workout-session-tracking/pull/347
Preuve négative : https://github.com/MFE-DSS/workout-session-tracking/actions/runs/41679982474
Run final : https://github.com/MFE-DSS/workout-session-tracking/actions/runs/41680437230
Aucun fichier métier, lock, migration, écran ou baseline ne reste modifié.
Les branches CODX-00 et CI-01 gardent chacune leur change et leur future livraison.

## 4. Preuves réellement exécutées pendant le sprint

| Vérification | Résultat |
|---|---|
| Garde CI-01 avant ajout du job | 3 échecs attendus : « Jest et TypeScript absents de la CI » |
| Gardes CI-01 + actions + shards + attestation + stabilité | **189 tests passants** après ajout du job |
| Jest mobile sous Node 22.20.0 | **32 suites / 422 tests passants** |
| TypeScript mobile | **exit 0** |
| Mutation locale Jest | Assertion volontairement fausse → **exit 1** ; fichier de preuve retiré |
| Mutation locale TypeScript | Chaîne affectée à number → **TS2322, exit 2** ; fichier de preuve retiré |
| Nouvelle exécution après retrait des mutations | **422 tests et TypeScript verts** |
| Ruff des fichiers Python touchés | Propre |
| Budget Ruff | **264 ≤ 548**, baseline inchangée |
| OpenSpec strict | **4 éléments passent** dans chacun des arbres CODX-00, CI-01 et MOB-02 |
| Protocole documentaire | OK |
| Revue indépendante CODX-00 et CI-01 | Aucun constat Important/Critical ; aucune réserve mineure restante sur le code CI-01 |
| Sweep Python complet local | **7147 tests passants, 378 fichiers / 95 lots, exit 0** ; pic 1825 Mo sous le budget 1869 Mo |

`actionlint` complet signale SC2046 à la ligne 647, **identiquement sur `fcfbcd7`**, dans une commande shell
préexistante. Le contrôle actionlint sans son intégration shellcheck passe. Ce résultat n'est pas présenté
comme un actionlint complet vert et le défaut hors périmètre n'a pas été corrigé en cascade.

La preuve GitHub négative a ensuite été réalisée sur le job `126070762071` : installation réussie,
**Jest exit 1** sur l'assertion volontaire, puis **TypeScript TS2322 / exit 2**, exécuté malgré l'échec Jest.
Les logs ont été relus. Deux causes et deux étapes distinctes dans un même run vérifient aussi la continuité
du diagnostic. Les deux fichiers de sonde sont retirés avant le run final, désormais vérifié : **9/9 jobs réussis**,
avec tous les checks externes verts, dont SonarCloud Code Analysis.
Le run de sondes continuant ses shards après collecte des deux échecs, une demande d'annulation explicite
de **ce seul run obsolète** a été acceptée par GitHub. Les logs de preuve sont conservés ; la CI complète
du HEAD final reste exigée. Une éventuelle conclusion `cancelled` du run de sondes ne serait donc pas une
annulation infra ni un échec produit non diagnostiqué.

## 5. Environnement et méthode

Un venv isolé Python **3.11.14** a été créé pour CI-01. Il utilise FastAPI **0.141.1** depuis le lock runtime.
Les **29 pins du lock** ont été comparés aux versions installées : aucun écart. `app.__file__` pointe sur le
worktree CI-01. Le venv partagé ancien, Python 3.14.7/FastAPI 0.135.3, n'a pas été modifié.

L'installation npm initiale élevée a utilisé Node 25 et émis des avertissements d'engine. Les tests et le
typecheck ont ensuite été exécutés avec le chemin explicite de Node **22.20.0**. Le lock reste intact.

Vérifications pilotées par `check_scope` : CODX-00 outillage isolé ; CI-01 **ci_infra** impose un sweep local
complet et une validation GitHub réelle avant merge. Aucun `pytest -n auto`, script CI sur le poste, build Xcode,
déploiement ou réapprobation de baseline exécuté.
Le sweep local obligatoire a été exécuté **une seule fois** ; son journal couvre environ **71 minutes**
(horodatages du fichier, 4251 secondes). C'est le coût mesuré de cette vérification sur ce poste, pas la durée
promise pour les prochains sprints. La règle des tests ciblés/broad sweep reste applicable aux tiers qui
n'exigent pas un full sweep ; aucune policy n'a été changée pour accélérer ce résultat.

## 6. MOB-02 — reprise préservée et décisions closes

Les décisions de l'opérateur sont consignées en annexes explicites de la proposition et du design :

- **D-MOB02-1 = A** : deux GET mobiles pour fréquence déclarée et historique nécessaire au bilan ; lecture seule,
  ownership par utilisateur authentifié, réutilisation des sources canoniques, aucune migration ni valeur inventée.
- **D-MOB02-2** : AUREN-MARK-V1 seule pendant la restauration du jeton, sans texte, nouveau logo ni animation imposée.

Le build MOB-02 n'a pas commencé. Ses exigences de reprise des accusés persistés (`restore().outbox`, pas
seulement `outboxRows()`), de preuve du vrai consommateur `ConnectedApp`, de double appui, de substitution
refusée/hors ligne et de recette Android puis iPhone restent intégralement requises.
La passe iPhone de MOB-01 et le retour testeur de PLAT-01 restent aussi à fermer avant archive de ces changes.

## 7. Autorisations et limites de livraison

Le premier push CODX-00 a été refusé par la revue automatique faute d'un GO PUSH distinct.
L'opérateur a ensuite donné **« GO PUSH + PR pour CODX-00 et CI-01 »**. Le push CODX-00 et l'ouverture de sa PR
ont été réalisés avec cette autorisation ; aucun contournement du refus et **aucun merge** effectué.

La validation d'une PR, son merge, l'archive du change et le déploiement sont des états distincts.
Aucun résultat de rapport antérieur n'est présenté ici comme exécuté pendant ce sprint.

## 8. Livraison finale et prochain pas

| Sprint | État de livraison vérifié | Ce qui reste |
|---|---|---|
| CODX-00 | **PR GREEN / MERGE PENDING**, PR #346, HEAD `7d70c2f`, 8 jobs CI et tous les checks externes verts, dont Quality Gate Sonar | GO MERGE distinct, intégration canonique, closeout/archivage |
| CI-01 | **PR GREEN / MERGE PENDING**, PR #347 prête pour revue, HEAD `764b452`, run `41680437230` : 9/9 jobs et tous les checks externes verts ; preuves négatives GitHub vérifiées | GO MERGE distinct, intégration après CODX-00, closeout/archivage ; décision sur le nouveau check requis |
| MOB-02 | Proposition préservée/rebasée, décisions produit acceptées, aucun build commencé | Reprendre après intégration du socle ; tests de consommateur réel et recettes Android/iPhone |

La PR CI-01 est sortie du brouillon après lecture des résultats finaux ; aucun thread de revue non résolu
n'a été relevé. Aucun merge, archive, déploiement ni écriture de données produit n'a été effectué.

**Décision de protection à soumettre :** ajouter le check exact **`mobile checks (Jest + TypeScript)`** aux checks
requis, la validation du run étant acquise. Le job fait échouer son workflow, mais l'agent n'a pas modifié la protection de
branche pour rendre ce nouveau nom requis.

Les mises à jour de statut des rapports/registres de sprint sont préparées localement dans leurs worktrees,
à versionner avec le suivi de livraison. Les HEAD ci-dessus sont ceux réellement poussés et observés ; les
statuts documentaires locaux ne constituent pas un nouveau HEAD validé par la CI.

**Prochaine action technique :** après GO MERGE distinct, intégrer CODX-00 puis CI-01 et remettre la branche
MOB-02 sur cette canonique, en conservant
sa proposition et ses décisions. Le prochain build produit demeure MOB-02.
