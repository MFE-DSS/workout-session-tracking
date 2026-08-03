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

## Appendice post-merge (closeout — à compléter)

- Commit · PR # · **`coverage` réel post-fix (API)** · `new_coverage` sur code neuf · merge commit ·
  CI canonique · confirmation « plus de bypass `--admin` requis ».
