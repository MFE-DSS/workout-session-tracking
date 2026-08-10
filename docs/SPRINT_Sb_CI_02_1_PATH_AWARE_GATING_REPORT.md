# SPRINT Sb_CI_02_1_PATH_AWARE_GATING — CI consciente du périmètre (RAPPORT)

**Base canonique :** `3b7b2d0` · **Branche :** `sb/ci-02-1-path-aware-gating` · **Tier :** **CI_INFRA**
(`check_scope` le confirme : touche `.github/` + `scripts/` → full sweep local **obligatoire** +
**validation sur CI réelle impérative**, `CLAUDE.md §1`).
**Livré sous** DELIVERY AUTONOMY ENVELOPE + `CLAUDE.md §4` (skill `auren-sprint-from-spec`).

## 1. Problème

Le trigger `pull_request` rejoue **l'intégralité** du pipeline pytest/QA/coverage même quand une PR
ne change que de la documentation ou de l'outillage opérateur. Coût observé le 2026-08-10 :
la PR **#70** (218 lignes, uniquement `docs/templates/` + `.claude/skills/`) a payé
**12 min 31 s** de pytest pour du contenu qui **ne peut pas** atteindre le runtime. Sur une journée
de sprints enchaînés par injection de prompts, ce coût est payé à chaque itération.

## 2. Correction d'audit assumée (avant conception)

Mon audit précédent affirmait que « chaque push sur une PR ouverte déclenche 2 runs — on paie
double ». **C'était faux.** Le trigger `push` est restreint à `branches: [main,
claude/sprint-reporting-fitness-app-V7Qr6]` : une branche de feature ne déclenche **aucun** run
push, seulement le run `pull_request`. Preuve : les têtes de #68 et #70 ont chacune produit **un
seul** run. La déduplication de concurrency est donc **hors périmètre** de ce sprint, sur
instruction opérateur — et à raison.

## 3. Brainstorming / Options / Risques / Choix retenu (CLAUDE.md §3)

| Option | Verdict |
|---|---|
| **A** — classifieur déterministe **possédé par le repo** + gating **au niveau des étapes** | ✅ **RETENU** |
| **B** — `paths-ignore` sur le trigger `pull_request` | ✗ **casse la protection de branche** : les checks requis ne se matérialisent jamais et restent `Expected` → PR non mergeable |
| **C** — condition `if:` au niveau des **jobs** | ✗ même défaut : un job sauté ne produit pas son check requis |
| **D** — action tierce de path-filter | ✗ la logique native est ici **plus lisible et testable** ; une règle de sécurité ne doit pas dépendre d'un tiers non pinné |

**Principe de conception** : *les jobs ne disparaissent jamais ; seules les étapes coûteuses
deviennent conditionnelles.* C'est ce qui satisfait le critère « aucun check requis ne doit rester
`Expected`/`Pending` ».

**Risques traités** :
1. **Faux `NON_RUNTIME` = suite sautée à tort** (le risque grave) → **allow-list fermée à 2 préfixes**,
   défaut `RUNTIME_OR_INFRA` pour l'inconnu, le vide et l'indéterminé ; **22 tests** pinnent chaque cas.
2. **Sonar échouant faute de `coverage.xml`** → téléchargement en `continue-on-error` ; le scanner
   tourne **toujours** donc le check externe est émis. Sans code neuf, le gate **n'évalue pas**
   `new_coverage` (vérifié sur #69 et #70 : 4 conditions, aucune de couverture).
3. **Perte de couverture de sécurité sur les PR docs** → le job `lint` **n'est pas gaté du tout** :
   ruff budget, bandit, actionlint, shellcheck, pip-audit, **gitleaks**, **spec protocol**,
   auth-scope matrix tournent intégralement sur **toute** PR (~51 s).
4. **Diff indéterminé** (force-push, première poussée, SHA de base absent) → la commande shell
   retombe sur une liste vide, que le classifieur traduit en `RUNTIME_OR_INFRA`.

## 4. Ce qui est livré

| Fichier | Changement |
|---|---|
| `scripts/classify_change_scope.py` (**neuf**) | Classifieur déterministe. `NON_RUNTIME` **uniquement** si **tous** les chemins sont sous `docs/**` ou `.claude/skills/**` ; sinon `RUNTIME_OR_INFRA`. Explique son verdict dans les logs (chemins fautifs listés). Mode `--github-output`. |
| `tests/test_classify_change_scope.py` (**neuf**) | 22 tests |
| `.github/workflows/ci.yml` | Job `test` : `fetch-depth: 0` + étape **« Classify change scope »** ; **12 étapes gatées** (install, pytest, upload coverage, 8 QA) + une étape explicative `NON_RUNTIME`. Job `sonar` : téléchargement de couverture tolérant. **Jobs `lint` et `sonar` non gatés.** |
| docs | ce rapport + registry + roadmap |
| **triggers / branch protection / `deploy-production.yml`** | **inchangés** |

**Allow-list volontairement minuscule et auditable** : `docs/`, `.claude/skills/`.
**Non allow-listés à dessein** : `CLAUDE.md` (contrat d'exécution du repo), `.claude/settings.json`
(permissions de l'agent), et tout le reste. L'élargir exige un audit explicite **et** un test pinné.

## 5. Tests

`tests/test_classify_change_scope.py` — **22 passés**. Les 9 catégories demandées sont pinnées :
docs-only · skill-only · code applicatif · code de test · data/taxonomie · workflow · migration ·
fichier de dépendances · **chemin inconnu → runtime**. Plus : jeu vide → runtime · un seul fichier
runtime contamine un lot docs · `CLAUDE.md` et `.claude/settings.json` **non** allow-listés ·
préfixes trompeurs (`docsite/`, `app/docs/`, `.claude/skills_backup/`) → runtime · normalisation
(`./`, guillemets, antislash) · sortie GitHub · lecture stdin.

**Bug réel attrapé par ces tests pendant le build** : `_normalise` utilisait
`str.lstrip("./")`, qui retire **tous** les caractères de l'ensemble `{'.', '/'}` — donc
`.claude/skills/x` devenait `claude/skills/x` et **échouait à matcher**. Corrigé par un retrait
littéral du préfixe `./`. Sans le test de normalisation, le gating aurait silencieusement traité
toute PR de skills comme runtime (dégradation sûre, mais gain nul).

**Full sweep local (exigé par le tier CI_INFRA)** : **2981 passés, 0 échec** en 4 min 39 s.

## 6. Validation sur CI réelle (impérative — `CLAUDE.md §1`)

Deux exécutions réelles sur la **même** PR #71 — aucune affirmation théorique, uniquement des
durées relevées sur GitHub Actions.

### Preuve 1 — commit `RUNTIME_OR_INFRA` (`9a3760f`)

Run `31409270555`. Le classifieur a bien **décidé**, il n'a pas été contourné :

```
change-scope: RUNTIME_OR_INFRA (5 changed file(s))
  reason: 3 runtime/infra path(s), e.g.: …
```

**5 checks PASS** · `pytest + QA scripts` **12 min 45 s** — **pipeline complet rejoué**, comme
exigé (critère 3). Gate Sonar `OK`.

### Sémantique confirmée : la PR est jugée sur son **diff complet vs base**

Première tentative de preuve `NON_RUNTIME` : un commit **docs-only** poussé sur la PR #71
elle-même. Le job a quand même tourné **14 min 1 s**, et le log dit pourquoi :

```
change-scope: RUNTIME_OR_INFRA (5 changed file(s))
  reason: 3 runtime/infra path(s), e.g.:
    - .github/workflows/ci.yml
    - scripts/classify_change_scope.py
    - tests/test_classify_change_scope.py
```

**Ce n'est pas un défaut, c'est la bonne sémantique** — et la tentative de preuve était mal
conçue, pas l'implémentation. Juger au **dernier commit** permettrait à une PR contenant du code
runtime de **sauter la suite de tests** via un commit docs final : trou de sécurité réel. Le
classifieur juge donc le diff **entier** de la PR contre sa base.

**Conséquence opérationnelle** : le gain ne s'applique qu'aux PR **intégralement** non-runtime
(closeouts, specs, rapports, skills). Une PR mixte code+docs paie le pipeline complet — voulu.

### Preuve 2 — PR `NON_RUNTIME` réelle (PR #72, base = branche du sprint)

Pour exercer le chemin sans rien merger : une PR dont le **diff entier** est un fichier `docs/`,
avec pour base la branche du sprint (le workflow gaté est présent des deux côtés).
Run `31412180977` :

```
change-scope: NON_RUNTIME (1 changed file(s))
  reason: every changed path is documentation or agent tooling
```

| Check | Résultat |
|---|---|
| `pytest + QA scripts` | ✅ **8 secondes** — étape explicative exécutée, pytest + coverage + 8 QA sautés |
| `lint (…)` | ✅ **49 s**, **intégral** — gitleaks, spec protocol, ruff budget, bandit, actionlint, shellcheck, pip-audit |
| `SonarCloud` (job) | ✅ 1 min 20 s |
| **`SonarCloud Code Analysis`** (gate **externe**) | ✅ **SUCCESS** — scanner exécuté, absence de `coverage.xml` tolérée |
| `Gitar` | ✅ 32 s |

PR de preuve **fermée sans merge**, branche supprimée.

### Critères d'acceptation — tous couverts

| Critère | Verdict |
|---|---|
| 1. PR `NON_RUNTIME` complète, toutes les surfaces de check présentes | ✅ 5/5 présents et verts (PR #72) |
| 2. « SonarCloud Code Analysis » externe = SUCCESS | ✅ (PR #72) |
| 3. Un commit runtime rejoue pytest+QA+coverage complets | ✅ **12 min 45 s**, run `31409270555` |
| 4. Aucun check requis bloqué en `Expected`/`Pending` | ✅ aucun job supprimé — seules des étapes sont conditionnelles |
| 5. Sémantique du workflow de déploiement inchangée | ✅ `deploy-production.yml` non touché |

### Mesures réelles (GitHub Actions, aucune extrapolation)

| Cas | Job `test` | Contexte |
|---|---|---|
| **Avant** — PR #70 (docs + skills) | **12 min 31 s** | pipeline complet, inévitable |
| **Après** — PR #72 (`NON_RUNTIME`) | **8 s** | **≈ 94× plus rapide** sur ce cas |
| **Après** — PR #71 (`RUNTIME_OR_INFRA`) | **12 min 45 s** | inchangé, **volontairement** |

Sur une PR entièrement non-runtime, le chemin critique passe de **~14-16 min** à **~1 min 20 s**,
borné désormais par le job `sonar` et non plus par pytest.

## 7. Interdits tenus

**Aucun** testmon · **aucune** sélection de tests par impact · **aucune** réduction de la suite
runtime · **aucun** split fast/full · **aucun** remplacement des tests requis par du scheduled ·
**aucun** affaiblissement de la protection de branche · **aucune** modification des triggers ·
**aucune** dédup de concurrency (retirée du périmètre sur correction opérateur) ·
`deploy-production.yml` **intact** · gitleaks et spec protocol **toujours actifs**.

## Verdict

**Verdict :** ✅ **Sb_CI_02_1_PATH_AWARE_GATING — MERGED + CANONICAL CI GREEN.** CI consciente du
périmètre via un classifieur **déterministe, possédé par le repo, fail-safe et testé** : les jobs
ne disparaissent jamais, seules les étapes qui ne peuvent rien vérifier sont sautées. **Mesuré,
pas extrapolé** : une PR entièrement non-runtime passe de **12 min 31 s** à **8 s** sur le job
`test`, tandis qu'une PR runtime rejoue le pipeline complet à l'identique (**12 min 45 s**). La
protection de branche, la validation runtime, gitleaks, le spec protocol et le gate Sonar restent
**intacts** — aucun test retiré, aucun gate affaibli.

---

## Appendice post-merge (closeout)

- **Merge** : PR **#71 MERGED** 2026-08-10, build `9a3760f` + preuves docs `5e2f485`/`5a21be9`,
  merge commit **`3a0e193`** via `--merge --match-head-commit 5a21be9` — **sans squash, sans
  `--admin`, sans force** (gate `CLEAN`, `MERGEABLE`, **0 thread**).
- **CI canonique** : run **`31415185233`** (`push`) **3/3 GREEN** sur `3a0e193`
  (lint · pytest + QA · SonarCloud). Le merge contient du code (`ci.yml`, `scripts/`, `tests/`),
  la CI push a donc bien tourné — classée `RUNTIME_OR_INFRA` par le classifieur lui-même.
- **Gate Sonar** de la PR : `OK` (0 bug / smell / vuln / SCA neufs) ; **0 thread de revue**.
- **PR de preuve #72** : fermée sans merge, branche supprimée.
- **Cleanup** : branche `sb/ci-02-1-path-aware-gating` + worktree
  `workout-session-tracking-ci-gating` supprimés (cleanup inclus par l'opérateur).
- **Suite immédiate** : `Sb_CI_02_2_AUTH_FIXTURE_FASTPATH` — le gating ne change rien au coût
  d'une PR runtime (12 min 45 s) ; le poste dominant restant est le double bcrypt par test
  authentifié dans la fixture générique.
