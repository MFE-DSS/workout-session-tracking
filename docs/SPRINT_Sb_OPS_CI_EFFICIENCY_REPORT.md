# Sprint Report — Sb_OPS.ci-efficiency · CI Development-Efficiency Overhaul

**Type :** OPS / CI_INFRA (pipeline) · **Tier check_scope :** `CI_INFRA` · **Base canonique :** `a2e2b6d`
**Branche :** `sb/ops-ci-efficiency` · **Worktree :** `workout-session-tracking-ops-ci-efficiency`

---

## 1. Objectif

Réduire le coût des tests inter-sprints, devenu ≈ la durée de dev : le job CI `pytest + QA` tournait
**mono-thread** (~37-43 min) en rejouant l'intégralité de la suite à chaque PR, et le full sweep local
(~14 min) le doublait. **Phase 1** d'un virage « développement efficace » : **paralléliser** l'exécution
(sans retirer un seul test, sans changer le modèle de sécurité) et **alléger la redondance locale**.

## 2. Mesure initiale (avant)

- Full sweep **mono-thread** : **~834 s (13:54)** pour 2663 tests (mesuré au build WIZARD_04).
- Job CI `test` : **~37-43 min** (runs `30443591700` 37 min, `30448452394` 42 min).
- `tests/conftest.py` : chaque test a **son propre `tempfile.mkdtemp` + `test.db`** (`DATABASE_URL`
  monkeypatché par test, reset du module tree `app.*`) → **suite xdist-safe par construction**.

## 3. Brainstorming / Options / Risques / Choix retenu (CLAUDE.md §3)

**Insight** : la parallélisation (`pytest-xdist -n auto`) rend ~80 % du gain pour ~10 % du risque —
zéro test retiré, zéro changement du modèle de sécurité — et **rend largement superflus** une CI à deux
vitesses (levier 3) et une sélection par impact (levier 4), dont la valeur marginale s'effondre une fois
la suite complète ramenée à ~10-13 min.

| Levier | Verdict |
|---|---|
| **1 — xdist `-n auto`** (CI + full sweep local) | ✅ **PHASE 1 — RETENU** (gros gain, risque quasi nul, conftest déjà isolé). |
| **2 — allègement `shared_code` local** (retrait `full_sweep_local`, garde broad scoped) | ✅ **PHASE 1 — RETENU** (léger ; xdist dissout déjà la douleur du double-run). |
| 3 — CI à deux vitesses | ⏸️ **DIFFÉRÉ** — risque de régression atteignant le trunk ; marginal une fois xdist en place. |
| 4 — sélection par impact / testmon | ⏸️ **DIFFÉRÉ** — faux-négatifs de sélection ; capricieux avec cov+xdist. |

**Choix retenu : Phase 1 = leviers 1 + 2.** Leviers 3+4 différés à un sprint ultérieur, à rouvrir après
avoir **mesuré le gain xdist réel sur la CI**.

## 4. Périmètre livré

**`pyproject.toml`** : `pytest-xdist>=3.6` ajouté au groupe `dev` (aucune dépendance **runtime** touchée).

**`.github/workflows/ci.yml`** (job `test` uniquement) : `pytest-xdist` installé ; le sweep passe de
mono-thread à **`pytest -n auto --dist worksteal --ignore=tests/test_v1_acceptance.py --cov=app
--cov-report=xml --cov-report=term -q`**. **Préservés à l'identique** : `--ignore` de l'acceptance test,
coverage XML, chemin `coverage.xml` + step `sed` de préfixe pour Sonar, les 8 QA scripts, le job `lint`,
le job `sonar` et son `needs: [test, lint]`.

**`.check-policy.json`** : tier `shared_code` → **`full_sweep_local` retiré des `required_local_checks`**
(déplacé en `skip`), **`broad_sweep_scoped` conservé comme garde local obligatoire** ; `ci_note` +
`rationale` documentent que la **CI parallélisée sur PR devient le filet de vérité** du blast radius
partagé. Principe #2 mis à jour. **`migration`, `ci_infra` conservent le full sweep local obligatoire.**

**`CLAUDE.md` §1** (contrat versionné prioritaire) : table des tiers — ligne `shared_code` passe à
« broad sweep ciblé obligatoire ; full sweep local recommandé si doute, non systématique », ligne
`migration` rendue explicite (`isolated` + full sweep local + migration checks) pour ne plus dépendre de
la ligne `shared_code` ; règles d'application — le full sweep local n'est plus lancé pour `isolated`/
`docs`/`shared_code`, **commande de référence du full sweep devenue xdist** (~4 min), et **sprints
`ci_infra` doivent prouver leur effet sur une CI réelle avant merge**.

## 5. Interdits respectés

✅ **no `app/`** · ✅ **no `models/`** · ✅ **no migration** · ✅ **aucun test applicatif modifié**
(0 marqueur `serial` nécessaire — voir §7) · ✅ no seed · ✅ no `session_builder` · ✅ no EKB_04 /
SCORING_04 / WIZARD_05 · ✅ no ASSET/BodyMap · ✅ no WaveSoft/Logistics · ✅ **no CI deux vitesses**
(levier 3 différé) · ✅ **no testmon** (levier 4 différé) · ✅ aucune dépendance runtime touchée.

## 6. Protocole de validation

- **Local (dogfood du levier)** : `pytest -n auto --dist worksteal …` exécuté sur la suite réelle.
- **CI réelle IMPÉRATIVE** (tier `ci_infra`) : un changement de pipeline ne se prouve que sur GitHub —
  la PR doit montrer le job `test` parallélisé **3/3 vert** avec `coverage.xml` toujours consommée par
  Sonar. C'est le seul juge d'un changement de CI.

## 7. Résultat local (dogfood)

- **2677 passed / 0 failed** en **298.72 s (4:58)** — **~2.8×** plus rapide que le mono-thread (834 s)
  sur cette machine (4 vCPU ; gain CI ubuntu-latest attendu similaire ou supérieur).
- **`coverage.xml` produite** → compatibilité **pytest-cov + xdist** confirmée (couverture combinée
  entre workers).
- **ZÉRO échec sous parallélisme** → la suite est **entièrement xdist-safe**, **aucun marqueur `serial`
  requis** (conftest per-test-tempdir tenu). `--dist worksteal` opérationnel (aucun repli nécessaire).
- **check_scope `CI_INFRA`** · **check_spec_protocol PASS** · **ruff budget 543 ≤ 548** (aucun code
  Python touché).

## 8. Résultat CI attendu

Job `test` : **~37-43 min → ~10-13 min** (gain runner 4 vCPU) ; `lint` et `sonar` inchangés ;
`coverage.xml` toujours publiée. **À confirmer sur la CI réelle de la PR** avant tout merge.

## Verdict

**Verdict :** 🟢 **Sb_OPS.ci-efficiency — PATCH COMPLETE / REVIEW PENDING.**

La CI et le full sweep local sont désormais **parallélisés** (`-n auto`, ~2.8× local prouvé, zéro perte de
couverture, zéro test retiré, zéro `serial`), et la politique locale `shared_code` s'appuie sur la CI
parallélisée comme filet plutôt que de doubler systématiquement le sweep. **Leviers 3 (CI deux vitesses)
et 4 (sélection par impact) explicitement différés.** La preuve définitive appartient à la **CI réelle**.

---

## Appendice post-merge (closeout — à compléter)

- Commit build · PR # · merge commit · CI PR (job `test` parallélisé) · durée CI avant/après réelle ·
  Sonar `total: 0` + `coverage.xml` reçue · CI canonique · statuts leviers 3/4 (DEFERRED).
