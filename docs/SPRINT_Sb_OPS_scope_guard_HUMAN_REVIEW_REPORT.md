# Human Review — Sb_OPS.scope-guard (anti-overcheck)

**Verdict** : ✅ **HUMAN REVIEW ACCEPTED**
**Date** : 2026-07-09
**Type** : revue humaine — docs-only (aucun code touché)
**Nature** : outillage OPS — garde-fou anti-overcheck (aucun changement de comportement applicatif)

---

## 1. Décision

**Sb_OPS.scope-guard est accepté.** Le garde-fou classe le diff courant en un
tier de risque **déterministe** et impose le niveau de vérification **local**
minimal suffisant — pour éviter de lancer un full sweep local de 10-15 min sur
un changement isolé (service pur, docs) qui ne peut pas régresser le reste de la
suite. La CI réelle (3 jobs au push) reste **toujours** la source de vérité ;
le garde-fou ne réduit **jamais** la CI, seulement les checks locaux redondants.

---

## 2. Preuve CI (run réel)

| Item | Valeur |
|---|---|
| **Commit** | `a43ce856e9063c67062f99ca89d991b2e13d0cd1` |
| **Run** | [`29015557948`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/29015557948) — ✅ **3/3 success** |
| `lint (ruff budget + bandit + actionlint + shellcheck)` | ✅ success |
| `pytest + QA scripts` | ✅ success |
| `SonarCloud` | ✅ success |
| Full sweep local | ✅ **1852 passed** (inclut les 9 tests garde-fou) |

---

## 3. Éléments acceptés (checklist)

| Élément | Statut |
|---|---|
| `.check-policy.json` (matrice de tiers versionnée) | ✅ accepté |
| `scripts/check_scope.py` (classifieur déterministe) | ✅ accepté |
| `tests/test_scope_guard.py` (9 tests) | ✅ accepté |
| `CLAUDE.md` (contrat d'exécution versionné) | ✅ accepté |
| Tiers `docs` / `isolated` / `shared_code` / `migration` / `ci_infra` | ✅ accepté |
| Précédence conservative (migration > ci_infra > shared_code > isolated > docs) | ✅ accepté |
| Détection **réelle d'imports** (isolated vs shared) | ✅ accepté |
| Full sweep local skippé **seulement** pour `isolated` / `docs` | ✅ accepté |
| CI réelle **jamais réduite** | ✅ accepté |
| Règle **versionnée non aliénable par prompt** | ✅ accepté |
| 9 tests garde-fou verts | ✅ accepté |
| Full sweep local 1852 passed | ✅ accepté |
| **Aucun comportement applicatif modifié** | ✅ confirmé |

---

## 4. Principe fondateur

Le point qui rend le garde-fou **fiable et non contournable par un prompt** :
il vit **dans le repo** (`.check-policy.json` + `scripts/check_scope.py` +
`CLAUDE.md`), pas dans les instructions de session. Un prompt futur ne peut pas
le désactiver ; seul un commit modifiant ces fichiers le peut.

Le **cœur intelligent** est la distinction `isolated` vs `shared_code` par
**analyse d'import réelle** : un fichier neuf que personne n'importe (ex.
`body_map_descriptor`) → `isolated` → full sweep local skippable ; un fichier
partagé (ex. `muscle_mapping.py`, importé par 7 consommateurs) → `shared_code` →
full sweep local exigé.

---

## 5. Garde-fous du garde-fou

- **Ne réduit jamais la CI réelle.** Au push, les 3 jobs tournent toujours en
  entier (sauf `paths-ignore: docs/**`, qui est la policy CI existante, pas un skip).
- **Conservative** : en cas d'ambiguïté de tier, remonte d'un cran (plus de checks).
- **Dogfood** : le garde-fou se classe lui-même en `ci_infra` (il touche
  `scripts/`), a donc exigé un full sweep local + une CI réelle — les deux verts.

---

## 6. Verdict

**Verdict :** ✅ **Sb_OPS.scope-guard — HUMAN REVIEW ACCEPTED.**

Outillage anti-overcheck livré, testé (9/9), CI réelle verte 3/3, aucun
comportement applicatif modifié. La règle est ancrée dans un `CLAUDE.md`
versionné et s'applique à tous les sprints suivants. Aucun code touché par cette
revue.
