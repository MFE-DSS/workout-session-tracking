# AUREN — intégration autorisée, arrêt Sonar canonique et reprise

> Rapport historique de reprise. État de livraison actuel : [GOV-SONAR-01 / CI-01](GOV_SONAR_01_DELIVERY_2026-11-03.md).

Date : 3 novembre 2026. **Verdict : BLOCKED — closeout incomplet.**
**Rapport historique de l’arrêt avant GOV-SONAR-01.** Depuis, la politique temporaire a été autorisée et
fusionnée, puis CI-01 fusionnée après son sweep final complet. Voir le
[livrable GOV et l’état actuel](GOV_SONAR_01_DELIVERY_2026-11-03.md) ; les faits ci-dessous restent ceux de l’arrêt.
Ce rapport remplace les statuts de livraison du CR et du préflight précédents pour les étapes exécutées après GO.

## Autorisation et périmètre

L’opérateur a confirmé **« Oui, GO MERGE pour ce périmètre »** : fusion de #346 puis #347 par commits de merge,
validations, closeout et rebase MOB-02, sans démarrer son implémentation. Cette autorisation est enregistrée ;
aucun nouveau GO identique n’est à redemander pour la même séquence. Le blocage Sonar ci-dessous doit être
résolu avant de poursuivre cette séquence.

## État réellement atteint

| Élément | État |
|---|---|
| CODX-00 #346 | **MERGED**, par commit de merge, garde sur HEAD `7d70c2f359bc5e41eb17947756a207d2716cfeed` |
| Canonique actuelle | **`60bea5d28eeaecc1eba1c71aefe7186793c4098a`** |
| CI canonique | Run **41691072708**, événement push, **8/8 jobs Actions réussis** |
| Qualité externe canonique | **SonarCloud Code Analysis : FAILURE ; Quality Gate ERROR** sur cette même révision |
| CI-01 #347 | **OPEN, non mergée**, nouveau HEAD publié **`5d675b6e69217bb0bbc52bdcd925f68cf879c5c8`** |
| Nouvelle base CI-01 | `60bea5d…`, intégrée par merge sans réécriture ; conflit du registre résolu en conservant les deux entrées |
| Nouvelle CI PR CI-01 | Run **41692608283**, en cours au dernier contrôle ; mobile, lint, visuel, attestation et shard 2 verts ; shards 1 et 3 encore en cours |
| MOB-02 | HEAD **`8c0f4d7c1cfb3d011646617d0138714e94c2673d`**, base `fcfbcd766c0d2e19feb15850897d51e03aca5570` ; rebase final non effectué, build non démarré |
| Archives / nettoyage / protection | Aucun archivage, aucune suppression, aucune modification de protection |

Sources : [PR #346](https://github.com/MFE-DSS/workout-session-tracking/pull/346),
[PR #347](https://github.com/MFE-DSS/workout-session-tracking/pull/347),
[CI canonique CODX-00](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/41691072708),
[nouvelle CI PR CI-01](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/41692608283),
[Sonar canonique](https://sonarcloud.io/dashboard?id=MFE-DSS_workout-session-tracking&branch=claude%2Fsprint-reporting-fitness-app-V7Qr6).

## Blocage exact : verdict externe Sonar, distinct des jobs Actions

`CLAUDE.md §4` et `AGENTIC_DELIVERY_PROTOCOL.md §4` exigent la vérification Sonar après merge.
La livraison ne peut donc pas être déclarée close sur la seule couleur du workflow Actions.

- Workflow : `41691072708`, conclusion `success`.
- Job scanner : `SonarCloud`, ID **126118089386**, conclusion `success` ; aucun step Actions en échec.
- Check externe du même SHA : **`SonarCloud Code Analysis`, conclusion `failure`**.
- API `qualitygates/project_status`, branche canonique explicite : **`status: ERROR`**.
- API `project_analyses/search` : analyse **`9f30706f-ad36-41d6-91e0-468446be5388`**,
  datée **2026-11-03 18:25:15 UTC**, révision exacte **`60bea5d…`**.

| Condition Sonar canonique | Valeur | Seuil | Verdict |
|---|---:|---:|---|
| `new_coverage` | 93,9 % | minimum 80 % | OK |
| `new_duplicated_lines_density` | 0,0 % | maximum 3 % | OK |
| `new_bugs_severity` | 25 | maximum 9 | **ERROR** |
| `new_code_smells_severity` | 20 | maximum 14 | **ERROR** |
| `new_vulnerabilities_severity` | 10 | maximum 9 | **ERROR** |

La période de nouveau code est **`previous_version`, depuis le 10 avril 2026**.
Les valeurs en échec sont des métriques de sévérité, pas les nombres bruts d’issues.
C’est un échec de qualité externe, ni un échec pytest ni une annulation infra.

## Qualification et hypothèse

L’historique Sonar compare l’analyse de 13:33:36 UTC (`8a216577…`) à celle de 18:25:15 UTC (`60bea5d…`) :

| Mesure globale | Avant | Après |
|---|---:|---:|
| Coverage | 93,8 % | 93,8 % |
| Bugs | 8 | 8 |
| Vulnérabilités | 6 | 6 |
| Code smells | 439 | 439 |

La recherche des issues non résolues créées depuis 18:09 UTC renvoie **0 résultat**.
La PR CODX-00 avait **0 issue Sonar**, coverage 93,8 % et gate OK.
CODX-00 ne modifie aucun code métier ; la réconciliation CI-01 ne change ni le job mobile ni ses gardes
par rapport au HEAD précédent. Les baselines restent intactes.

**Hypothèse :** la gate de branche évalue une dette déjà présente dans sa longue période `previous_version`,
tandis que la gate PR évalue le delta. Les totaux stables étayent cette hypothèse ; ils ne permettent pas de
contourner la gate et ne constituent pas une analyse complète des issues. Le job utilise
`SonarSource/sonarqube-scan-action@v7.1.0` sans attente explicite du verdict de qualité : un scan réussi peut
donc coexister avec un check externe rouge.

**Plus petite suite proposée :** diagnostic Sonar/CI borné, séparé de MOB-02, pour inventorier les conditions
et issues concernées, confronter période de nouveau code et contrat canonique, puis proposer un correctif
ou un arbitrage explicite. Aucun patch produit, rebaselining, changement de seuil, résolution massive d’issues
ou bypass appliqué.

## Vérification CI-01 après changement de base

`check_scope` sur les neuf fichiers effectifs donne **CI_INFRA**. Résultats frais :

- Gardes CI/runtime/shards/attestation/stabilité : **189 tests passants**.
- Mobile sous Node 22.20.0 : **32 suites / 422 tests passants**, TypeScript **exit 0**.
- Ruff : propre ; budget **264 ≤ 548**. Premier lancement du budget sans `ruff` dans PATH ; relance avec
  PATH du venv réussie, sans changement de code.
- Protocole documentaire : OK ; OpenSpec strict : **5/5** ; `git diff --check` : OK.
- Full sweep borné **arrêté volontairement au STOP Sonar** : **52 lots, 208/378 fichiers passés sans échec** ;
  driver terminé par SIGTERM, exit **143**. **Ce n’est pas un full sweep réussi** ; les 7147 tests du sprint
  précédent ne le remplacent pas. Journal : `/private/tmp/auren-ci01-revalidation-sweep.log`.

La nouvelle CI PR reste lancée et n’a pas été annulée. Même si elle devient verte, le blocage canonique
et la validation locale incomplète restent à traiter avant merge CI-01.

## Préservation et reprise exacte

Les documents locaux CODX-00/CI-01 et les trois fichiers de décisions MOB-02 ont été sauvegardés dans
**`/private/tmp/auren-closeout-backup-20261103/`**, avec patches Git, avant réconciliation.
CI-01 est poussée sans force-push. Son premier transport était bloqué dans `git-credential-osxkeychain` ;
seul notre push a été arrêté, puis il a réussi via le helper GitHub CLI existant, sans changement de
configuration globale ni de credential.

Worktrees, branches, configurations locales et environnements sont préservés. Le vieux checkout utilisateur,
ses changements et `grixis/` sont intacts. Aucun déploiement n’est effectué.

Après résolution et vérification du sujet Sonar canonique :

1. Revérifier le SHA canonique, ses checks externes et l’absence de nouvelle dérive.
2. Reprendre la validation CI-01 selon `check_scope` et obtenir CI PR/qualité externe verte sur le HEAD final.
3. Fusionner #347 sous le GO déjà reçu, puis vérifier CI et Sonar canoniques.
4. Mettre à jour rapports/registre et archiver les deux changes après satisfaction de leurs gates.
5. Rebaser MOB-02 sur le canonique vérifié, préserver les décisions et comparer la proposition avant/après.
6. Vérifier les travaux uniques avant nettoyage ; mettre à jour le préflight final MOB-02.

Les **12 tâches MOB-02** et le plan de test du vrai `ConnectedApp` et des états dégradés restent ceux du
[préflight précédent](PREFLIGHT_CODX00_CI01_MOB02_2026-11-03.md), sans changement de sémantique.
D-MOB02-1=A, D-MOB02-2=AUREN-MARK-V1 seule, journal complet, refus/hors ligne et gates Android/iPhone conservés.
Le GO BUILD MOB-02 reste non donné. Le check mobile est toujours proposé comme requis, protection inchangée.
