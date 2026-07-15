# Human Review — Sb_UI_10.4 User-Facing Labels Auren Pass (SPIGNOS → Auren)

**Verdict** : ✅ **HUMAN REVIEW ACCEPTED**
**Date** : 2026-07-15
**Type** : revue humaine — docs-only (aucun code touché par cette revue)
**Cycle** : Sx_UI_10 (Auren Visual Migration Closeout & Rebrand Readiness)
**Build report** : [`SPRINT_Sb_UI_10_4_USER_FACING_LABELS_AUREN_PASS_REPORT.md`](SPRINT_Sb_UI_10_4_USER_FACING_LABELS_AUREN_PASS_REPORT.md)

> Chaîne validée :
> - **CODE COMPLETE** : build `7bdf4ba` (poussé).
> - **DOCS/ARBITRAGE ALIGNMENT** : `57a6d5f` (poussé, docs-only, CI légitimement skippée `paths-ignore: docs/**`).
> - **CI GREEN** : run `29416674199` — 3/3 success.
> - **HUMAN REVIEW ACCEPTED** : le présent commit `docs(review)` (séparé du code).

---

## 1. Décision

**Sb_UI_10.4 est accepté.** Les dernières surfaces user-facing documentaires migrent le nom
produit visible vers **Auren** : `/science` (lede, capture cardio, 2 titres de section,
paragraphe programmes), `/science/atlas` (lede), `/coach-report` (note garde-fous §10) et le
`<title>` accessible du diagramme SVG inline. **String-only pass** : sens scientifique,
biomécanique, logique coach report, structure SVG (`viewBox`/`role`/`aria-labelledby`/`id`s),
routes et calculs **inchangés**. Aucun manifest, icône ou asset statique.

## 2. Scope accepté (périmètre du build `7bdf4ba`)

`app/templates/science.html` · `app/templates/atlas.html` · `app/templates/coach_report.html` ·
`app/templates/_partials/science_diagram.svg` · `tests/test_science_page.py` (1 assertion
ré-orientée) · `tests/test_auren_user_facing_labels.py` (nouveau) — plus rapport/registry/roadmap.
Vérifié par `git show --name-only 7bdf4ba` : **aucun autre fichier**.

## 3. Preuves CI (run réel)

| Item | Valeur |
|---|---|
| **Run** | [`29416674199`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/29416674199) — ✅ **3/3 success** |
| `pytest + QA scripts` | ✅ success (pytest 22:55, marge large sous timeout 45) |
| `lint` (ruff budget + bandit + actionlint + shellcheck) | ✅ success (47 s) |
| `SonarCloud` | ✅ success (1 min 19) |
| **Tests** | ✅ **2164 passed**, 2 warnings — arithmétique exacte : 2152 (baseline `10.3`) + **12 dédiés** |
| Ruff budget | ✅ **543 ≤ 548** |
| Spec protocol | ✅ PASS |
| Timeout / annulation infra | Aucun — premier coup |

## 4. Résumé produit

Avec `10.1` (shell), `10.3` (auth publiques) et ce `10.4` (docs/labels), **plus aucun template
de l'application ne rend « SPIGNOS » à l'utilisateur** (guard-jalon automatisé
`test_no_template_renders_spignos_anywhere`). Le seul SPIGNOS encore rendu provient d'une
donnée seedée (§7). Le canon Sx_UI_10 est respecté : Auren = visible, SPIGNOS = interne.

## 5. Collision de sessions & arbitrage (rappel)

Le build `7bdf4ba` a été commité/poussé par une **session parallèle avant réception de l'ordre
de STOP** (course de timing, non destructeur). **Arbitrage opérateur** : une seule session
propriétaire de `10.4` ; fichier de tests **conservé** = `test_auren_user_facing_labels.py`,
doublon **supprimé** = `test_auren_user_facing_docs_strings.py`. Le rapport final a été
**réaligné dans `57a6d5f`** : renommage vers le nom canonique mandaté
(`..._USER_FACING_LABELS_...`), section §2bis collision/arbitrage, `Sb_UI_10.4b` nommé,
sentinelle précisée « exactement 1 ». Détail complet : build report §2bis.

## 6. Tests dédiés

- **Conservé** : `tests/test_auren_user_facing_labels.py` — **12 tests dédiés** (confirmés par
  `pytest --collect-only` et par le delta CI 2152 + 12 = 2164) : surfaces rendues (client réel),
  SVG title a11y, garde non-médicale coach report préservée, guard template-wide, sentinelle
  résidu, non-régression 10.1/10.3, zéro Orion.
- **Supprimé** (arbitrage) : `tests/test_auren_user_facing_docs_strings.py` (doublon transitoire
  de la session parallèle, couverture recoupée à ~80 %).

## 7. Résidu connu (pinned, hors périmètre)

`/science` rend encore **exactement 1** occurrence SPIGNOS : « …dans SPIGNOS est dérivé… »,
issue de la règle méthode seedée `plages-repetitions` (`data/method_rules.json:13` →
table `method_rules`). **Hors périmètre `10.4`** (`data/**` interdit par le mandat), découverte
**indépendamment par les deux sessions** (convergence). **Pinnée** par test sentinelle
(`assert body.count("SPIGNOS") == 1`) : elle ne peut ni croître ni disparaître silencieusement.
**Décision : ouvrir ensuite `Sb_UI_10.4b — Method Rules User-Facing Data String Pass`** sur GO
explicite (1 chaîne ; `seed_method_rules` réécrit la table à chaque boot, sans version-gate —
correction triviale et sûre).

## 8. Invariants vérifiés

| Contrainte | État |
|---|---|
| `data/**` non touché | ✅ |
| `manifest.webmanifest` / `app/static/` / icons non touchés | ✅ |
| CSS / JS non touchés | ✅ |
| routes / services / models / migrations non touchés | ✅ |
| Logique coach report / calculs / métriques inchangés | ✅ |
| Aucun renommage interne SPIGNOS (repo/modules/routes/env/tables) | ✅ |
| Aucun deploy | ✅ |
| Branche `spec/sx-custom-program-01-intelligent-builder` intacte | ✅ |
| `Sb_UI_10.2` non ouvert (BLOCKED BY ASSETS) | ✅ |
| Closeout `Sx_UI_10` non ouvert | ✅ |
| Zéro Orion | ✅ |

## 9. Warnings CI (non bloquants, préexistants, hors périmètre)

Identiques aux runs `10.1`/`10.3` : shellcheck SC2046 via reviewdog sur
`.github/workflows/ci.yml:190` (fichier non touché) + dépréciation Node.js 20 des actions
GitHub. L'annotation « exit code 1 » du log est le pas reviewdog non bloquant — job lint vert.

## 10. Décision & suite

| Élément | État |
|---|---|
| **`Sb_UI_10.4`** | ✅ **ACCEPTED** |
| **`Sb_UI_10.4b`** Method Rules User-Facing Data String Pass | 🟡 **recommandé ensuite, sur GO explicite** (non ouvert) |
| **`Sb_UI_10.2`** PWA Manifest + App Icons | ⏸️ **BLOCKED BY ASSETS** |
| Closeout `Sx_UI_10` | ⏸️ non ouvert (après `10.2`) |

---

## Verdict

**Verdict :** ✅ **Sb_UI_10.4 User-Facing Labels Auren Pass — HUMAN REVIEW ACCEPTED.**

8 chaînes produit visibles migrées SPIGNOS → Auren sur science/atlas/coach-report + SVG title
a11y, sens et logique intacts, CI réelle verte 3/3 (`7bdf4ba`, run `29416674199`, **2164
passed**), arbitrage de collision consigné et rapport réaligné (`57a6d5f`). **Plus aucun
template ne rend SPIGNOS** ; unique résidu = donnée seedée, pinnée à exactement 1, réservée à
`Sb_UI_10.4b` sur GO. Aucun code touché par cette revue. Next : `Sb_UI_10.4b` (data, trivial)
puis `Sb_UI_10.2` dès gate assets.
