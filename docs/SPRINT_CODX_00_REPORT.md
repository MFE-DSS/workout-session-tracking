# CODX-00 — reprise Codex/OpenSpec et bonne base

Date : 2026-11-03. Branche : `sb/codx-00-codex-openspec`.
Change : `openspec/changes/codex-openspec-adapter`.
État de livraison : **MERGÉE #346, archive dans cette clôture**. Les sections de préparation décrivent
l'état initial ; l'annexe de livraison en fin de rapport porte le résultat le plus récent.

## 1. Commande opérateur et Brainstorming / Options / Risques / Choix retenu

L'opérateur fournit un plan de reprise explicite : bonne base, adaptateur officiel, aucun code produit immédiat,
pas de second framework, puis CODX-00 → CI-01 → MOB-02. Les options sont donc bornées par cette commande.

| Sujet | Options considérées | Choix / risque |
|---|---|---|
| Base | Modifier le vieux checkout ; reprendre la canonique dans un worktree | Worktree isolé, vieux checkout intact |
| Proposition MOB-02 | Recréer ; merger toute l'histoire ; rejouer le commit sauvegardé | Sauvegarde puis rebase du seul commit de proposition ; vérifier le diff exact |
| Adaptateur | Copier des skills à la main ; générateur officiel | `openspec init --tools codex --no-animation`, sans `--force` |
| Gouvernance | Spec Kit en plus ; OpenSpec existant | OpenSpec et contrats AUREN, selon décision opérateur |
| CI | Mélanger avec CODX-00 ; tranche dédiée | CI-01 sur branche séparée, proposition avant apply |
| Stores | Créer maintenant ; attendre l'alpha | Réponse opérateur : comptes personnels créés par lui à l'alpha ; aucune démarche anticipée |

## 2. SHA de départ, remise à niveau et préservation

| Objet | SHA / chemin |
|---|---|
| Ancien checkout fourni, inchangé | `61ca08c2e553d4e527d10f0c45f1e93da2dbc751` |
| Canonique observée avant fetch dans l'audit précédent | `fdafcf23eb98cd98d378d9b2d75e045229f1b1f3` |
| Canonique actualisée par `git fetch origin` | `fcfbcd766c0d2e19feb15850897d51e03aca5570` (PR #345, onboarding Codex) |
| CODX-00 départ / fin HEAD | `fcfbcd766c0d2e19feb15850897d51e03aca5570` — modifications non commitées |
| Proposition MOB-02 initiale | `091110b`, préservée sous `backup/mob-02-proposal-091110b` |
| MOB-02 après rebase | `8c0f4d7c1cfb3d011646617d0138714e94c2673d` |
| Worktree CODX-00 | `/private/tmp/auren-codx-00` |
| Worktree CI-01 | `/private/tmp/auren-ci-01`, branche `sb/ci-01-mobile-checks`, HEAD `fcfbcd7` |
| Worktree MOB-02 | `/Users/martinfeldmann/workout-session-tracking-mob02` |

Le rebase est passé **sans conflit**. Avant consignation des décisions, cette commande a rendu un diff vide :

```sh
git -C /Users/martinfeldmann/workout-session-tracking-mob02 diff backup/mob-02-proposal-091110b HEAD -- openspec/changes/session-native-integration
```

Diff commité MOB-02 contre canonique après rebase : **5 fichiers, 216 insertions**, tous dans le dossier du change.
La coque MOB-01 finale est maintenant dans la base de MOB-02. Aucun push forcé, aucun push tout court.
La branche rebasée ne doit pas être poussée aveuglément sur son ancien upstream ; une nouvelle branche de
livraison peut préserver l'historique distant lorsque CODX-00 et CI-01 auront été intégrés.

Le checkout initial, ses deux documents d'audit, `.claude/settings.json`, AGENTS.md et `grixis/` sont préservés.
Aucun worktree tiers nettoyé. Aucun commit de livraison créé ; seul le commit de proposition a été recréé par rebase.

## 3. Périmètre livré localement

- Six skills officielles : apply-change, archive-change, explore, propose, sync-specs, update-change, sous
  `.agents/skills/openspec-*`. La CLI utilise des skills pour Codex, sans commandes de prompts personnalisées.
- Change CODX-00 avec proposal, design, tasks et `skip_specs: true` : aucune exigence produit à inventer pour
  une adaptation d'outillage. Ligne ajoutée au registre.
- [Roadmap opérateur](strategy/AUREN_MOBILE_CRITICAL_PATH_2026_11_03.md), incluant STORE-00 et la voie assets.
- Proposition CI-01 complète dans son propre worktree ; aucun workflow modifié.
- MOB-02 : annexes explicites de décisions dans proposal/design, tâche 1.1 cochée. D-MOB02-1=A, lectures serveur
  sans migration, ownership authentifié, aucune donnée absente inventée ; D-MOB02-2=marque seule, sans texte.
  Ces trois modifications documentaires sont **non commitées**, séparées du diff CODX-00 et du rebase.

## 4. Revue du diff généré et contrats

Juste après `openspec init`, `git status --short` ne montrait que `?? .agents/`.
Une comparaison brute aux skills Claude a échoué : le générateur adapte les noms d'invocation aux outils.
La comparaison suivante a vérifié, pour les six fichiers, que **seules les invocations** `/opsx:*` deviennent les
formes `$openspec-* (Codex) or /openspec-* (other agents)`. Aucun texte de workflow réinterprété à la main.

Commande de préservation exécutée, sortie vide, exit 0 :

```sh
git diff --exit-code HEAD -- CLAUDE.md .claude/skills openspec/config.yaml openspec/specs clients/mobile app .github
```

Les skills personnalisées existantes et les contrats sont intacts. Aucun AGENTS.md créé ni versionné dans CODX-00.
La présence des fichiers est prouvée ; le rechargement du catalogue de skills de l'application Codex lors d'une
prochaine session n'a pas été testé. Les instructions générées ont été lues directement dans cette session.

## 5. Vérifications réellement exécutées

Les commandes ci-dessous sont exécutées depuis le worktree indiqué. Python désigne ici l'exécutable absolu
`/Users/martinfeldmann/workout-session-tracking/.venv/bin/python` ; aucun environnement produit n'a été modifié.

| Worktree | Commande | Résultat observé |
|---|---|---|
| CODX-00 | `openspec init --tools codex --no-animation` | Six skills créées, config existante conservée |
| CODX-00 | `python scripts/check_scope.py` | ISOLATED (nouveaux fichiers d'outillage/docs, métadonnée YAML) ; pas de full sweep |
| CI-01 | `python scripts/check_scope.py` | ISOLATED pour la proposition seule ; le futur workflow sera `ci_infra` |
| MOB-02 | `python scripts/check_scope.py` | DOCS pour les trois fichiers de décisions |
| CODX-00 | `python scripts/check_ruff_budget.py` avec le bin du venv en PATH du processus | 264 ≤ 548, exit 0 ; aucune baseline modifiée |
| CI-01 | Même commande de budget | 264 ≤ 548, exit 0 |
| CODX-00 | `openspec validate --all --strict --no-interactive` | 4 éléments passent, zéro échec ; `skip_specs` accepté |
| CI-01 | Même commande OpenSpec | 4 éléments passent, zéro échec |
| MOB-02 | Même commande OpenSpec | 4 éléments passent, zéro échec |
| MOB-02 | `python scripts/check_spec_protocol.py` | OK |
| CODX-00 et CI-01 | `python scripts/check_spec_protocol.py` après écriture des artefacts | OK dans les deux arbres |

La vérification du budget utilise un sous-processus Python dont PATH commence par le bin du venv, car `ruff`
n'est pas dans le PATH shell standard. Version lue par chemin absolu : ruff 0.15.12.

Les vérifications propres à ces fichiers sont la comparaison du générateur et la validation des changes ; aucun
fichier Python/TypeScript produit n'a changé, donc aucun test applicatif ciblé ni broad sweep de consommateurs
n'a de changement à mesurer. Pas de nouveau test miroir pour les six fichiers générés. Ruff nouveaux fichiers :
sans objet (aucun nouveau Python). Le protocole documentaire passe après écriture du rapport.

Vérification de provenance Python exécutée dans MOB-02 :

```sh
/Users/martinfeldmann/workout-session-tracking/.venv/bin/python -c 'import app,sys,importlib.metadata as m; print("python",sys.version.split()[0]); print("app",app.__file__); print("FastAPI",m.version("fastapi"))'
```

Résultat : **app du bon worktree**, mais **Python 3.14.7 / FastAPI 0.135.3**, contre **Python 3.11 en CI et
FastAPI 0.141.1 dans le lock**. Environnement backend reproductible à préparer avant le build CI-01/MOB-02.
Ne pas recycler cette preuve de chemin comme preuve de conformité au lock.

## 6. CI réelle, sécurité et visuel

**Aucun nouveau run CI lancé pendant CODX-00.** Aucun résultat historique présenté comme exécuté aujourd'hui.
Pas de publication, compte externe, secret, migration, seed, baseline ou donnée de production modifiés.
Aucune UI changée : pas de capture nouvelle requise par cette tranche. MOB-02 garde ses gates Android/iPhone.
Ni Jest, ni tsc, ni build mobile, ni sweep Python complet exécutés pendant cette configuration.

## 7. STORE-00 et décisions restantes

Réponse opérateur reçue pendant le travail : comptes Apple/Google **personnels**, créés **par lui à l'alpha**.
Identifiant définitif, contrat d'effacement, URL/contenu confidentialité et stratégie OTA restent à préparer.
Aucune demande de création de compte avant l'alpha.

Les deux décisions produit MOB-02 sont closes. Restent : revue/livraison CODX-00, revue avant apply CI-01,
environnement Python verrouillé, preuve CI réelle CI-01, puis build MOB-02 et preuves appareil.

## Verdict de préparation, avant le GO de reprise

**⏳ ATTENDRE — revue de livraison CODX-00 et proposition CI-01.** La préparation locale et la remise à niveau
sont réalisées ; aucune clôture de livraison ni autorisation de merge n'est revendiquée.
Le prochain apply substantiel doit respecter `CLAUDE.md §6` : « proposal → relecture opérateur → apply ».

## Annexe d'exécution — reprise autorisée le 2026-11-03

Après présentation du diff et des propositions, l'opérateur demande : « ok donc continue sur ton critical path ».
La livraison CODX-00 et le build CI-01 sont donc repris, sans autorisation de merge implicite.
Les résultats des sections précédentes décrivent la préparation antérieure ; les nouveaux résultats seront
consignés ici séparément. Les permissions Codex personnelles (réseau, worktrees, revue automatique) sont
locales et ignorées par Git ; elles ne font pas partie de cette PR.

**État courant :** vérifications et revue avant commit/push/PR, puis CI réelle ; merge réservé à l'opérateur.

Revue indépendante (agent à contexte neuf) : aucun constat Important/Critical. Son unique remarque mineure
sur la coexistence du verdict initial et de cette annexe est levée en datant explicitement le verdict initial.
Contrôles rejoués sur cette reprise : scope ISOLATED, OpenSpec strict 4/4, spec protocol OK, diff --check vide.

### Livraison locale et arrêt du push

Commit de l'adaptateur : **`11ec97d`**, créé après contrôles et revue indépendante.
La commande `git push -u origin sb/codx-00-codex-openspec` a été **refusée avant exécution par la revue
automatique** : elle exige une autorisation PUSH distincte avant export du contenu au dépôt distant.
Une demande explicite couvrant les branches CODX-00 et CI-01 et leurs PR, sans merge, a été envoyée à l'opérateur.
Aucun push, aucune PR, aucun run CI nouveau ni merge n'a donc été réalisé à ce stade.
La tâche 3.2 reste ouverte parce qu'elle inclut la CI réelle, pas seulement la soumission du diff.

La précédente limite Python a été résolue **dans le worktree CI-01 uniquement** : venv Python 3.11.14,
FastAPI 0.141.1 installé depuis le lock. Le vieux venv partagé n'est pas modifié.

### Résultat de livraison après GO PUSH explicite

L'opérateur a ensuite donné « GO PUSH + PR pour CODX-00 et CI-01 ».
Branche poussée au **`7d70c2f359bc5e41eb17947756a207d2716cfeed`** ;
[PR #346](https://github.com/MFE-DSS/workout-session-tracking/pull/346) ouverte.
[Run 41668162468](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/41668162468) :
**8 jobs completed/success**. `gh pr checks` confirme aussi tous les checks externes verts, dont
`SonarCloud Code Analysis`. Aucun merge et aucune archive effectués.

**Verdict de livraison : PR GREEN / MERGE PENDING.** Les présents statuts de clôture sont préparés localement
pour la suite du protocole après décision de merge ; ils ne modifient pas le HEAD déjà validé de la PR.

## Livraison et archivage — relevé de clôture du 2026-11-03

Les sections intermédiaires précédentes sont historiques. Les archives sont portées par cette clôture,
livrée via PR protégée sans push direct ni bypass. Les SHA et CI de la clôture documentaire sont relevés
dans la remise opérateur et les métadonnées de livraison après intégration. Aucun GO BUILD MOB-02 donné.

CODX-00 #346 est mergée par `60bea5d` ; CI canonique `41691072708` : 8/8 jobs Actions réussis.
Le Quality Gate Sonar ERROR réel a été consigné puis rendu consultatif par GOV-SONAR-01 #348 (`cc80ddd`),
sans changement de seuil ni requalification automatique des issues.

L’adaptateur officiel, les six skills et la roadmap sont livrés. Aucun code produit, baseline ou Spec Kit ajouté.
Le change est archivé sous `openspec/changes/archive/2026-11-03-codex-openspec-adapter`, 7/7 tâches.
Les quatre fichiers de l’archive sont identiques aux entrées contrôlées avant déplacement ; les specs vivantes
sont inchangées. Les décisions MOB-02 sont sauvegardées, la proposition existante sera rebasée après clôture.

Contrôle de la clôture : `check_scope` ISOLATED ; **142 tests ciblés/broad sweep passants**,
budget Ruff264≤548, protocole documentaire et OpenSpec strict3/3 passent ; aucun Python neuf,
Ruff nouveaux fichiers sans objet. Diff de code/workflow/baseline vide ; aucun full sweep local additionnel
requis pour ce diff de clôture. Les archives et les cinq fichiers de specs vivantes ont été comparés par SHA-256.
