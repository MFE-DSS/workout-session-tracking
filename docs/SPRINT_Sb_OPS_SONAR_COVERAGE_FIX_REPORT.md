# Sprint Report — Sb_OPS.sonar-coverage-fix · Repair SonarCloud Coverage Reporting

**Type :** OPS / CI_INFRA (pipeline) · **Tier check_scope :** `CI_INFRA` · **Base canonique :** `5a85d67`
**Branche :** `sb/ops-sonar-coverage-fix` · **Worktree :** `workout-session-tracking-ops-sonar-coverage-fix`

---

## 1. Objectif

Réparer le reporting de couverture SonarCloud, **cassé à 0.0 %** depuis le bump du scanner
(`Sb_OPS.sonar-java21`), qui forçait un **bypass `--admin` à chaque merge de code** (le gate
`new_coverage 80%` étant structurellement rouge). But : gate coverage **significatif**, plus de bypass,
et Sonar qui **mesure enfin** les ~2677 tests.

## 2. Cause racine (vérifiée par API + reproduite en local)

- **API `measures/component`** : `coverage=0.0`, `lines_to_cover=6456`, `uncovered_lines=6456`
  (100 % non couvert), `new_coverage=0.0` — Sonar ne mappe **aucune** ligne.
- **Reproduction locale** : `coverage.xml` (pytest-cov, `source=["app"]`, chemins **absolus**) émet
  `<source>/…/app</source>` + `filename="config.py"`. Le step CI `sed 's|filename="|filename="app/|g'`
  → `filename="app/config.py"`. Le scanner moderne (`sonarqube-scan-action@v7.1.0`, Java 21)
  **concatène `<source>` + `filename`** → `…/app/app/config.py` → **double `app/`, aucun chemin ne
  résout → 0 %**. Le `sed` (correct pour l'ancien scanner) **sur-préfixe** depuis le bump.

## 3. Options / Choix retenu

| Option | Mécanisme | Verdict |
|---|---|---|
| **A** — `relative_files=true` (`[tool.coverage.run]`) **+ retrait du `sed`** | chemins relatifs propres, résolus déterministe par Sonar | ✅ **RETENU** — format recommandé Sonar, robuste au scanner |
| B — retrait du `sed` seul (chemins absolus) | dépend du comportement scanner | ⚠️ fallback CI si A échoue |
| C — `sonar.sources=.` | élargit l'analyse | ✗ effet de bord |

## 4. Périmètre livré

- **`pyproject.toml`** : `relative_files = true` dans `[tool.coverage.run]`.
- **`.github/workflows/ci.yml`** : **suppression** du step « Prefix coverage paths with app/ » (`sed`).
- **Zéro** `app/`, zéro test applicatif, zéro migration — pipeline + config coverage uniquement.

## 5. Vérification locale (forme du XML)

Probe `pytest --cov=app --cov-report=xml` avec la nouvelle config → `<source>` passe de `/…/app`
(absolu) à **`app` (relatif)**, `filename="config.py"` inchangé. Sonar résout `<source>`+`filename` =
**`app/config.py`** → matche `sonar.sources=app`. **La forme est correcte** ; plus de `sed`, plus de
double-préfixe.

## 6. Validation — non-locale, itérative sur CI réelle (impératif ci_infra)

La résolution de chemins Sonar **n'existe qu'au scan réel**. Le **seul juge** = la CI de la PR : après
push, vérifier par `measures/component?…&pullRequest=N` que **`coverage > 0`** (et `new_coverage`
reflète les tests). Si A ne résout pas → bascule sur B **sur la même PR sans merge**, jusqu'à
`coverage > 0`. **Pas de merge tant que la couverture ne remonte pas.**

## 7. Risques

1. **Forme XML sous `relative_files`** → confirmée localement, à revalider sur CI (format Sonar recommandé).
2. **Gate qui serre après réparation** : `new_coverage` deviendra un **vrai** chiffre ; s'il est < 80 %
   sur du code neuf peu testé, le gate bloquera légitimement (comportement **voulu**). À surveiller au
   1er merge post-fix — possible ajustement du seuil ou couverture ciblée, hors scope de ce fix.
3. Le `sed` masquait peut-être un 2ᵉ souci → révélé par la boucle CI.

## Verdict

**Verdict :** 🟢 **Sb_OPS.sonar-coverage-fix — PATCH COMPLETE / REVIEW PENDING.**

`relative_files=true` + retrait du `sed` produisent un `coverage.xml` à chemins relatifs que Sonar résout
déterministe (forme confirmée en local). La preuve définitive (`coverage > 0` sur le scan réel)
appartient à la **CI de la PR**, seule capable de valider la résolution de chemins Sonar.

---

## Appendice post-merge (closeout 2026-08-05)

- **Commit build** : `62df735` (3 fichiers, +89/−10) sur `sb/ops-sonar-coverage-fix`, base `5a85d67`.
- **PR #47 MERGED** — merge **`cc3978e`** sur le canonique (via `--merge`, **SANS `--admin`** — gate
  `mergeStateStatus: CLEAN` ; pas de squash ; garde `--match-head-commit`). Première PR de code du
  cycle Custom Program mergée **sans bypass admin** grâce au coverage réparé.
- **CI PR #47** : **5 checks verts** — `pytest + QA` · `lint` · `SonarCloud` · `Gitar` · **`SonarCloud
  Code Analysis`** (le gate externe, **rouge à chaque PR avant ce fix**, désormais **vert**).
- **CI canonique** : run **`30996238572`** (push) sur `cc3978e` → **3/3 GREEN** (job `test` xdist
  **11 min 41 s**).
- **Preuve de couverture (API `measures/component`)** :
  - **PR #47** : `coverage = 91.1 %` (vs 0.0 % avant).
  - **Trunk `cc3978e` (post-scan canonique)** : **`coverage = 91.1 %`**, `uncovered_lines` **6456 → 662**
    / `lines_to_cover` 7432. **Aucun retour à 0.0 %.**
- **Sonar issues** : delta PR #47 = **`total: 0`** (P0 n'ajoute aucune ligne `app/`). La baseline trunk
  (~15 issues accumulées, la plus ancienne `Web:S7930` du 2026-07-17) est **pré-existante, hors scope**.
- **Effet** : le gate `new_coverage 80%` devient **significatif** sur les futures PR de code ; **plus de
  `--admin` systématique** si le code neuf est testé (toujours le cas). Le fix (`relative_files=true` +
  retrait du `sed`) est **prouvé sur CI réelle**, PR **et** trunk.
- **Cleanup** : branche `sb/ops-sonar-coverage-fix` (remote + locale) et worktree `-ops-sonar-coverage-fix`
  supprimés au closeout.

**Verdict post-merge :** ✅ **Sb_OPS.sonar-coverage-fix — MERGED + CANONICAL CI GREEN + COVERAGE
0.0 % → 91.1 %.**
