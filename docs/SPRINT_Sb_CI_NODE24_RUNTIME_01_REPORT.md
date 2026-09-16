# Sb_CI_NODE24_RUNTIME_01 — les actions de workflow quittent node20

**Tier `check_scope` : `CI_INFRA`** — sweep local complet **et** validation sur
CI réelle impérative.

---

## 1. Ce qui a déclenché la tranche

La CI canonique est tombée sur `actionlint`, avec ce message :

> `runtime "node20" is deprecated in GitHub Actions; removal is scheduled for`
> **`September 23rd, 2026`**

Nous sommes le **2026-09-16**.

Ce n'est **pas** une régression de l'analyseur. `reviewdog/action-actionlint@v1`
est passée de 1.74.0 à 1.75.0, et la 1.75.0 a ajouté cette vérification. La
version flottante n'est donc pas le défaut : **elle a rendu visible une échéance
réelle qu'un épinglage aurait masquée.** C'est une correction de mon propre
diagnostic initial, qui traitait le tag flottant comme le problème.

### Ce que l'échec coûtait, et qui n'était pas compté

Le job `lint` échoue à l'étape 9 sur 18. Les étapes suivantes sont `skipped` :

| Contrôle requis sauté | Nature |
|---|---|
| `shellcheck` | qualité |
| `pip-audit` sur `requirements-lock.txt` | **sécurité** |
| `gitleaks` | **sécurité** |
| protocole de spec | contrat |
| matrice de portée d'auth | **sécurité** |
| dérive `requirements.txt` ↔ lock | contrat |

⚠ **Et un septième, que je n'avais pas compté** : `SonarCloud` déclare
`needs: [test, lint]`, donc l'analyse canonique est **sautée** elle aussi.
Mesuré sur le run `35108633369` : `SonarCloud: skipped`.

---

## 2. Le défaut était INATTRAPABLE sur une PR

`reviewdog` filtre par défaut sur les **lignes modifiées**. Une PR qui ne touche
aucun fichier de workflow ne produit aucune finding, et le job passe au vert.
Seul le push canonique, qui n'a pas de diff de référence, voit le fichier
entier.

Conséquence structurelle : **le seul endroit où ce défaut peut apparaître est
celui où il est trop tard**. Il a atteint la canonique deux fois de suite
(`41c89bc`, puis `6c53cf3`) sans qu'aucune PR ne puisse l'arrêter.

C'est la partie de la tranche qui compte le plus, et elle n'est pas le bump.

---

## 3. Les versions cibles — mesurées, pas déduites

⚠ **« Prendre la version suivante » n'aurait rien corrigé.** Le `runs.using` de
chaque version a été lu dans son `action.yml` publié, via l'API GitHub, le
2026-09-16 :

| Action | Avant | Le réflexe | **Mesuré** | Retenu |
|---|---|---|---|---|
| `actions/checkout` | `@v4` | `@v5` | v5 = **node24** ✓ | **`@v5`** |
| `actions/setup-python` | `@v5` | `@v6` | v6 = **node24** ✓ | **`@v6`** |
| `actions/upload-artifact` | `@v4` | `@v5` | **v5 = node20** ✗ | **`@v6`** |
| `actions/download-artifact` | `@v4` | `@v5` | **v5 ET v6 = node20** ✗ | **`@v7`** |
| `gitleaks/gitleaks-action` | `@v2` | — | **v2 = node20** ✗ | **`@v3`** |
| `SonarSource/sonarqube-scan-action` | `@v7.1.0` | — | v7 = node24 ✓ | inchangé |
| `reviewdog/action-actionlint` | `@v1` | — | **docker** — hors sujet node | inchangé |

Deux faits que seule la mesure donne :

* `upload-artifact@v5` n'avait qu'un support **« préliminaire »** de node24 —
  ses notes de version le disent : c'est la **v6** qui bascule par défaut ;
* `sonarqube-scan-action` a fait `v5 = composite` → **`v6 = node20`** →
  `v7 = node24`. **La progression d'un runtime n'est pas monotone.**

`gitleaks-action@v2` n'était dans aucun de mes relevés initiaux : **le scan de
secrets lui-même allait cesser de partir.** Sa v3 ne change « ni entrées, ni
sorties, ni comportement » — seul le runtime bouge.

**Politique retenue : le majeur le plus BAS déjà en node24**, pour minimiser la
surface de rupture. Chaque option employée par nos workflows (`fetch-depth`,
`python-version`, `cache`, `name`, `path`, `pattern`, `merge-multiple`,
`run-id`, `github-token`, `retention-days`, `if-no-files-found`) a été vérifiée
présente dans l'`action.yml` de la version cible.

---

## 4. La garde qui manquait

`tests/test_ci_action_runtime.py` — elle tourne dans pytest, **donc sur chaque
PR**, et lit le fichier entier. Trois gardes :

1. **`test_no_workflow_action_runs_on_node20`** — planchers **mesurés** par
   action. Vérifiée par mutation : `checkout@v4` replanté dans
   `deploy-production.yml` → rouge, nommant le fichier et le plancher.
2. **`test_every_action_used_is_covered_by_the_guard`** — une action non
   inscrite fait échouer la garde. Sans elle, ajouter une action tierce la
   ferait passer sous le radar en silence : `PLANCHER.get(...)` rendrait `None`
   et la boucle l'ignorerait. **Elle a déjà servi** : elle a attrapé
   `SonarSource/sonarqube-scan-action`, que j'avais oubliée d'inscrire.
3. **`test_the_guard_actually_sees_the_workflows`** — elle exige explicitement
   `deploy-production.yml` dans son champ : c'est le workflow dont la panne
   coûterait le plus cher.

Une version non lisible (SHA épinglé, tag non sémantique) fait **échouer** la
garde plutôt que d'être ignorée : elle refuse de deviner et le dit.

---

## 5. Une garde retirée, et pourquoi ce n'est pas un affaiblissement

`test_a8_no_ci_action_version_was_touched` figeait cinq chaînes de version pour
exprimer *« le sprint autorité-du-lock n'a pas touché aux actions CI »*.

C'est une **sentinelle de périmètre**, pas une propriété du produit. Ce sprint
est mergé depuis le 2026-08-18 : son périmètre est immuable et **ne peut plus
régresser**. La garde ne protégeait donc plus rien — mais elle **interdisait**
la montée imposée par le retrait de node20. *Elle a bloqué la correction avant
de bloquer la panne.*

C'est la forme déjà recensée ici : **une garde épinglée à une ÉCRITURE plutôt
qu'à une PROPRIÉTÉ**. La propriété qui compte vit désormais dans la garde de
runtime, vérifiée par mesure. Ce qui reste sous le nom `A8` dit le vrai sujet du
fichier : **la CI installe depuis le lock**.

⚠ Ma première réécriture de cette garde se terminait par `or True` — un assert
qui **ne peut pas échouer**. Retiré. Une garde vacuante est pire que pas de
garde : elle occupe la place.

---

## 6. Hors périmètre, explicitement

* **Le `SC2046` de `shellcheck`** (`ci.yml:647`) reste : c'est un **warning**, et
  le job est en `fail_level: error`. Non bloquant, consigné, non corrigé — ce
  n'est pas le sujet de la tranche.
* **`reviewdog/action-actionlint@v1` reste flottante.** L'épingler aurait masqué
  cette échéance ; le tag flottant a rendu service ici. Le vrai garde-fou est la
  garde de runtime, qui ne dépend d'aucun analyseur tiers.
* **Aucun rapport de sprint historique n'est réécrit.** Seul
  `docs/SECURITY_BASELINE.md`, qui décrit la posture *courante*, est mis à jour.

---

## 7. Divergence de date, consignée sans être tranchée

| Source | Retrait de node20 |
|---|---|
| `actionlint` 1.75.0, citant le changelog GitHub | **23 septembre 2026** |
| Notes de version `gitleaks-action@v3` | **16 septembre 2026** |

Une semaine d'écart. Je ne tranche pas entre les deux : dans les deux cas
l'échéance est atteinte ou imminente, et la correction est la même.

### ⚠ Correction d'une alerte que j'avais formulée trop fort

Le déploiement de production du 2026-09-16 15:03 (`6c53cf3`) a **réussi**, avec
`actions/checkout@v4` — c'est-à-dire une action déclarée `node20`. Son log dit
pourquoi :

> `Node 20 is being deprecated. This workflow is running with **Node 24 by
> default**. If you need to temporarily use Node 20, you can set the
> `ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION=true` environment variable.

**GitHub exécute déjà les actions `node20` sur node24.** Le pipeline n'allait
donc pas tomber « dans sept jours » comme je l'avais annoncé : il tombera quand
le repli disparaîtra, et le repli est *déjà* la voie par défaut.

Ce que ça ne change pas :

* le job `lint` est **rouge aujourd'hui**, et six contrôles requis plus
  l'analyse Sonar canonique sont sautés — ça, c'est mesuré, pas prospectif ;
* du code **construit pour node20** tourne sur node24 sans avoir été rebâti pour
  lui — c'est précisément pourquoi `gitleaks-action@v3` a reconstruit son `dist/`
  et corrigé une dépréciation `punycode` ;
* la variable de secours porte le mot `UNSECURE` dans son nom, et elle
  disparaît à l'échéance.

La tranche reste nécessaire. Mon « ça casse dans 7 jours » était **trop
catégorique**, et le log de production l'a corrigé.

---

## Verdict

**LIVRÉE.** Les deux exigences du tier `CI_INFRA` sont tenues et mesurées.

| Contrôle | Résultat |
|---|---|
| `check_scope` | `CI_INFRA` |
| `ruff` | vert |
| `check_ruff_budget` | 267 / 548 |
| `check_spec_protocol` | vert |
| Pré-scan `python:S9073` | 0 |
| `actionlint` local (1.7.12) | aucune erreur — un `SC2046` **warning** préexistant, non bloquant |
| Mutation de la garde de runtime | défaut planté, garde rouge, arbre restauré |
| Sweep local complet | **`tous les lots sont verts.`** — 332/332 fichiers, 98 lots, pic 1712 Mo / budget 2100, aucun fichier sauté, **arbre gelé** |
| **CI réelle** — impérative à ce tier | **VERTE 7/7 sur la canonique** — voir le closeout |

⚠ **L'arbre a été gelé avant ce sweep, et c'est une correction de méthode.** Les
deux sweeps précédents de la session ont mesuré un arbre qui bougeait, et le
premier de cette tranche a dû être **interrompu** parce que je l'avais modifié
en cours de route. Un sweep sert à certifier ; il ne certifie que ce qui ne
bouge pas.

---

## Closeout — post-merge

| | |
|---|---|
| PR | **#235**, mergée le 2026-09-16 |
| Méthode | `--merge` avec `--match-head-commit` — aucun squash, aucun `--admin` |
| Head de PR | `23bcc04` |
| Commit de merge | **`2b8411d`** |
| Gate Sonar (PR) | **OK** 4/4 |
| Threads de revue non résolus | **0** |

### La preuve que la tranche demandait — sur CI réelle

**Le job `lint`, 18 étapes sur 18 en succès**, avec le **même `actionlint`
1.75.0** qui faisait échouer la canonique :

| Étape | Avant (`6c53cf3`) | Après (`2b8411d`) |
|---|---|---|
| 9 · `actionlint` | **failure** | **success** |
| 10 · `shellcheck` | skipped | **success** |
| 11 · `pip-audit` | skipped | **success** |
| 12 · **`gitleaks`** | skipped | **success** |
| 13 · protocole de spec | skipped | **success** |
| 14 · matrice de portée d'auth | skipped | **success** |
| 15 · dérive du lock | skipped | **success** |

**CI canonique sur `2b8411d` : 7 jobs sur 7 verts**, dont **`SonarCloud`**, qui
était `skipped` depuis que `lint` échouait — le septième contrôle perdu est
revenu.

Les quatre familles d'actions montées ont **réellement tourné** :
`checkout@v5` et `setup-python@v6` (tous les jobs), `upload-artifact@v6`
(*Upload coverage artifact*), `download-artifact@v7` (*Download shard coverage
data*, *Download coverage report*, *Download linter reports*), `gitleaks@v3`
(étape 12). Aucune n'a été validée par raisonnement seul.

### Cinq PR dependabot fermées

`#1` `#2` `#3` `#5` `#6` proposaient les mêmes bumps depuis des mois, jamais
traitées. Fermées avec leur motif : la tranche fait le même travail avec des
versions **mesurées** — et leurs cibles différaient (`checkout@v7`,
`download-artifact@v8`) de la politique du majeur le plus bas déjà en node24 —
tout en ajoutant ce qu'aucune PR dependabot ne peut apporter : **la garde**.

⚠ `#7` (bcrypt) **reste ouverte**, conformément à la contrainte opérateur
permanente : `bcrypt 5` est incompatible avec `passlib`.

### Ce qui reste ouvert

* **`reviewdog/action-actionlint@v1` reste flottante** — délibérément : c'est
  elle qui a rendu l'échéance visible, et l'épingler l'aurait masquée. Le vrai
  garde-fou est désormais la garde de runtime, qui ne dépend d'aucun analyseur
  tiers.
* **`SC2046`** (`ci.yml`) — warning `shellcheck`, non bloquant, consigné.
* **Le tri humain** des 6 branches de juin–juillet et des worktrees.
