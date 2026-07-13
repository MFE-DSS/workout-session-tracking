# Sprint Sx_BATCH_CLOSEOUT_01 — Local Batch Closeout

**Statut** : 🟢 CLOSEOUT LIVRÉ LOCALEMENT — **NON commité, NON poussé, CI non lancée** (LOCAL BATCH MODE)
**Type** : CLOSEOUT / SYNTHÈSE — docs-only
**Date** : 2026-07-13
**HEAD de référence** : `b60e749` (aucun commit depuis le début du batch)
**Objet** : synthétiser le batch local (Sx_CAT_01 + Sx_FB_01 + Sx_SUB_01), documenter les preuves et **préparer le GO BATCH COMMIT + CI** proprement.

---

## 0. Contexte — pourquoi un batch local

Le batch a été mené en **LOCAL BATCH MODE** : avancer sur plusieurs micro-sprints
sans payer une CI complète (~25-35 min) à chacun. La CI complète est lancée **une
seule fois** à la fin, sur un batch cohérent. Rien n'a été commité, poussé ni
CI-testé pendant le batch.

---

## 1. Contenu du batch (3 sprints)

| Sprint | Type | Nature du changement | Fichiers |
|---|---|---|---|
| **Sx_CAT_01** Catalog Integrity Cleanup | **CODE (data)** | 3 corrections sémantiques `machine_slug`/`machine_family` | `data/reference_split.json` (6 lignes) + `tests/test_catalog_integrity_cleanup.py` (nouveau) |
| **Sx_FB_01** Exercise Feedback Rationalization | **VERIFY (docs)** | « already done » — objectif déjà atteint (Sb_01/Sx_04 §13) | rapport seul |
| **Sx_SUB_01** Substitution Graph Verification | **VERIFY (docs)** | « already conformant » — moteur N1/N2/N3 déjà conforme | rapport seul |

**Un seul changement fonctionnel dans tout le batch : Sx_CAT_01.** Les deux autres
sont des **vérifications** qui ont conclu que la cible était déjà en place (et qui ont
évité une régression en ne re-codant pas).

---

## 2. Working tree — état exact

```
 M data/reference_split.json                                    ← Sx_CAT_01 (code/data)
 M docs/strategy/ROADMAP_AND_NEXT_STEPS.md                      ← docs (batch)
 M docs/strategy/SPEC_REGISTRY.md                               ← docs (batch)
?? docs/SPRINT_Sx_CAT_01_CATALOG_INTEGRITY_CLEANUP_REPORT.md    ← Sx_CAT_01 report
?? docs/SPRINT_Sx_FB_01_EXERCISE_FEEDBACK_RATIONALIZATION_REPORT.md  ← Sx_FB_01 report
?? docs/SPRINT_Sx_SUB_01_SUBSTITUTION_GRAPH_VERIFICATION_REPORT.md   ← Sx_SUB_01 report
?? tests/test_catalog_integrity_cleanup.py                     ← Sx_CAT_01 test
?? docs/SPRINT_Sx_BATCH_CLOSEOUT_01_LOCAL_BATCH_CLOSEOUT_REPORT.md   ← ce closeout
```

**Diff code/data** : `data/reference_split.json` — 6 insertions / 6 suppressions
(3 exercices × { `machine_slug` → null, `machine_family` → famille corrigée }).

---

## 3. Preuves consolidées

### 3.1 Sx_CAT_01 — data-only, sûr
- **Diff strict** : seuls `machine_slug`/`machine_family` changent — aucun
  slug/code/position/set_scheme/rep_target/nom touché.
- **3 anomalies CLEAR** : push-b/E5 + catch-up-shoulders/E4 (« Tirage front câble »
  upright row épaules, mal classé dos → `shoulders-lateral-posterior`) ; legs-b/E3
  (« Leg Press pieds hauts » postérieur, mal classé quad → `legs-posterior-calves`).
- **Invariance historique** : `seed.py:81-82` snapshote ces champs à la création →
  sessions existantes inchangées, **0 migration**.
- **QA** : catalog_qa + atlas_qa **PASS** ; 9 tests dédiés verts.

### 3.2 Sx_FB_01 — déjà réalisé (pas de régression)
- `execution_quality`/`reps_target` **absents du formulaire** (retirés par Sb_01,
  acté Sx_04 §13) ; routeur ne les lit pas ; colonnes DB + export conservés ;
  **0 consumer analytique**. Re-coder = régression → **rien touché**.

### 3.3 Sx_SUB_01 — déjà conforme (impact CAT_01 nul)
- Moteur N1/N2/N3 conforme (garde anti-cross-pattern hard-enforced, bridges N3-only,
  caps/dedup) ; **41 tests substitution verts**.
- **Sx_CAT_01 = impact NUL** : substitution lit `pattern_motor`/`zone_primary`/… depuis
  `exercise_properties.json`, **jamais** `machine_family`/`machine_slug` de
  `reference_split.json` (grep 0).

---

## 4. Tests locaux (récapitulatif)

| Suite | Résultat |
|---|---|
| `test_catalog_integrity_cleanup.py` (Sx_CAT_01) | ✅ 9 passed |
| substitution (tiered + base) | ✅ 41 passed |
| substitution/substitute/catalog_pattern/launcher | ✅ 97 passed |
| broad sweep catalog/seed/launcher/library/session/BI/physique/progress/history | ✅ 785 passed |
| catalog_qa · machine_atlas_qa · catalog_pattern_qa | ✅ PASS (3 soft warnings pull-b **préexistants**, non liés au batch) |
| check_scope (batch) · ruff · spec | ISOLATED · 543 ≤ 548 · OK |

> **Tous en LOCAL.** La CI GitHub réelle reste la source de vérité de non-régression
> globale — elle sera lancée au GO BATCH COMMIT.

---

## 5. Plan de commit recommandé (au GO BATCH COMMIT)

Le batch mélange un changement de **code** (Sx_CAT_01) et des **docs**. Deux stratégies :

### Option recommandée — **2 commits** (code puis docs)
1. **Commit 1 (code)** — Sx_CAT_01 :
   ```
   git add data/reference_split.json tests/test_catalog_integrity_cleanup.py \
           docs/SPRINT_Sx_CAT_01_CATALOG_INTEGRITY_CLEANUP_REPORT.md
   # message: fix(catalog): correct 3 semantic machine_family/machine_slug inconsistencies
   ```
   → **déclenche la CI** (data + test = code). C'est le commit qui doit être validé 3/3.
2. **Commit 2 (docs)** — vérifications + registry/roadmap + closeout :
   ```
   git add docs/SPRINT_Sx_FB_01_*.md docs/SPRINT_Sx_SUB_01_*.md \
           docs/SPRINT_Sx_BATCH_CLOSEOUT_01_*.md \
           docs/strategy/SPEC_REGISTRY.md docs/strategy/ROADMAP_AND_NEXT_STEPS.md
   # message: docs(batch): record FB_01/SUB_01 verifications + batch closeout
   ```
   → **CI skipped** (docs-only, `paths-ignore: docs/**`).

**Avantage** : la CI ne tourne qu'une fois, sur le seul changement de code (Sx_CAT_01).
Le commit docs est gratuit (skip). Séparation claire code/docs dans l'historique.

### Alternative — 1 commit unique
Tout dans un `feat(catalog): ...` — CI se déclenche (code présent), les docs sont
embarquées. Plus simple mais mélange code + 3 rapports dans un seul commit.

**Recommandation : 2 commits** (code isolé, CI ciblée sur Sx_CAT_01).

---

## 6. Checklist pré-commit (à exécuter au GO)

- [ ] `git status` = les 8 fichiers du batch, rien d'autre
- [ ] `python scripts/check_scope.py` (tier attendu : ISOLATED — data + test isolés)
- [ ] `python scripts/check_ruff_budget.py` (543 ≤ 548)
- [ ] `python scripts/check_spec_protocol.py` (OK)
- [ ] `python scripts/catalog_qa.py` + `machine_atlas_qa.py` (PASS)
- [ ] restaurer `docs/strategy/SPIGNOS_CATALOG_QA_REPORT.md` si régénéré (timestamp)
- [ ] **PAS** de `[skip ci]` sur le commit code (CLAUDE.md)
- [ ] après push : `gh run watch` → CI 3/3 (timeout 45 baseline)

---

## 7. Chemins interdits (tout le batch)

✅ Aucun touché sur l'ensemble du batch : `app/models/**`, `migrations/**`,
`schema_snapshot.sql`, `routers/**`, `templates/**`, `seed.py`, `muscle_mapping.py`,
`machine_atlas.py`, `substitution.py`, `catalog_qa.py`, `catalog_pattern_qa.py`,
`exercise_properties.json`, `cross_pattern_substitutions.json`, `static/**`,
`requirements*`, deploy/nginx/prod config. **Seuls** `reference_split.json` (Sx_CAT_01)
et `test_catalog_integrity_cleanup.py` = code.

---

## 8. Limites & suite

- Le batch ne contient **qu'un** changement fonctionnel (Sx_CAT_01) — volontairement
  minimal et sûr. Les 2 vérifications ont confirmé que d'autres cibles étaient déjà
  atteintes (pas de sur-ingénierie).
- **Soft warnings pull-b** (3, cross-pattern curated → bridges) : cleanup candidate
  **futur**, non bloquant, hors batch.
- Pistes ouvertes (hors batch) : nettoyage CSS inline `/history`, `Sx_UI_08.3` SW/offline,
  **CI optimization / pytest-xdist** (le timeout monte 25→35→45, run à 32:11), dogfooding
  terrain Sx_DOGFOOD_01 (pending), activation BI (deferred until dogfood + GO).

---

## 9. Recommandation finale

**GO BATCH COMMIT + CI complète** (stratégie 2 commits, §5). Le batch est cohérent,
minimal, vérifié localement, périmètre propre. Un seul changement de code à sécuriser
via la CI (Sx_CAT_01). Les vérifications FB_01/SUB_01 et ce closeout partent en commit
docs (CI skipped).

---

## Verdict

**Verdict :** 🟢 **Sx_BATCH_CLOSEOUT_01 — CLOSEOUT LIVRÉ (batch local prêt pour commit).**

Le batch local contient **un** changement de code (Sx_CAT_01 : 3 corrections
`machine_slug`/`machine_family`, data-only, sûr, historique préservé) + **deux
vérifications** (Sx_FB_01 already-done, Sx_SUB_01 already-conformant, aucun code
touché). Tests locaux verts (9 + 41 + 97 + 785), QA PASS, périmètre propre, HEAD
`b60e749` inchangé. **Recommandation : GO BATCH COMMIT + CI** en 2 commits (code
Sx_CAT_01 déclenche la CI ; docs skipped). Rien commité/poussé/CI dans ce sprint.
