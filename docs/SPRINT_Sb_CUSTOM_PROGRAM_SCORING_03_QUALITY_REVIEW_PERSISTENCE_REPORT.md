# Sprint Sb_CUSTOM_PROGRAM_SCORING_03 — Quality Review Persistence — BUILD

**Statut** : 🟢 **PATCH COMPLETE / REVIEW PENDING** (non commité, non poussé, CI non lancée)
**Type** : CODE BUILD — **migration additive + service de persistance** (Option B opérateur) ; premier build scoring touchant la DB
**Date** : 2026-07-23
**Specs** : `Sx_CUSTOM_PROGRAM_03` §4 (modèle de sortie) · §9-C (trace figée) · §10 (scoring sur brouillon) · §15 (queue : SCORING_03 = persistance)
**Branche** : `sb/custom-program-scoring-03-persistence` (worktree dédié, base `141ebd4`)
**Alembic** : head `n5o0i6j7l98` → **`o6p1j7k8m09`**
**Préflight** : ✅ GO PATCH validé — Option B, migration autorisée, `coverage_ratio` FLOAT

---

## 0. Étape 0 — Brainstorming / Options / Risques / Choix retenu

| Décision | Options | Choix retenu |
|---|---|---|
| Déclencheur | A service explicite · B explicite sans branchement · C auto dans `validate_draft` · D différer | **B** (arbitrage opérateur) — `validate_draft` reste pur et idempotent ; y greffer une écriture DB créerait un effet de bord caché et casserait son idempotence |
| Schéma | suffisant · migration | **migration additive minimale** — 3 champs du moteur n'ont aucune colonne (voir §2) |
| Champs manquants | fourrer dans un JSON existant · colonnes dédiées | **colonnes dédiées** — les glisser dans `subscores_json` ferait mentir le nom de la colonne |
| Feedback SCORING_02 | persisté · non persisté | **non persisté** — fonction pure du résultat, reconstructible ; le stocker figerait une microcopy évolutive |
| Idempotence | erreur · skip doux · nouvelle version forcée | **skip doux** (`created=False`) — re-scorer une version est légitime, pas fautif |
| `working_sets` | parser `set_scheme` · compter les rep_targets | **compter les `rep_targets` non-warmup** — `set_scheme` est du texte libre non contractuel |

## 1. Patch appliqué

| Fichier | Nature |
|---|---|
| `migrations/versions/20260723_add_quality_review_runtime_fields.py` | **nouveau** — revision **`o6p1j7k8m09`** (revises `n5o0i6j7l98`), ADD COLUMN ×3, guard `_column_exists` par colonne, downgrade symétrique |
| `app/models/user_program.py` | **modifié** — 3 colonnes ORM + import `Float` + docstring actant l'extension du réceptacle ; **listener `before_update` conservé intact** |
| `app/services/program_quality_reviews.py` | **nouveau** (~230 l.) — adaptateur ORM→payload + écriture insert-only owner-scopée |
| `tests/test_program_quality_reviews.py` | **nouveau** — **19 tests** |
| `data/schema_snapshot.sql` | **régénéré** (exigence tier MIGRATION) |

**Zéro modification** de `validate_draft`, `program_quality_engine.py`, `program_quality_feedback.py` · zéro API/UI/wizard · zéro publication `WorkoutTemplate` · zéro seed · zéro EKB.

## 2. Migration : les 3 colonnes et leur justification

```
ADD COLUMN user_program_quality_reviews.confidence       VARCHAR(16) NULL
ADD COLUMN user_program_quality_reviews.coverage_ratio   FLOAT       NULL
ADD COLUMN user_program_quality_reviews.grade_cap_reason TEXT        NULL
```

Le réceptacle de `PERSISTENCE_03` reflète **exactement** la spec 03 §4. Le moteur de `SCORING_01`,
écrit après, produit **3 champs supplémentaires** nés de la doctrine des gaps honnêtes (4 sous-scores
sur 8 non mesurables tant que l'EKB n'est pas curé) :

- `confidence` et `coverage_ratio` dépendent de l'état de **l'EKB au moment du scoring** — un EKB
  futur enrichi donnerait d'autres valeurs : **non dérivables après coup** ;
- `grade_cap_reason` explique **pourquoi** un grade est plafonné à B.

**Sans ces colonnes, une trace figée portant « B » se lirait comme un B pleinement mesuré** — la trace
serait trompeuse. L'invariance historique exige une trace fidèle : d'où la migration.

**Non stockés volontairement** : `disclaimer` (constante du moteur) · le feedback `SCORING_02`
(fonction pure, reconstructible à tout moment).

**Conformité** : additive-only · aucune table · aucun DROP/RENAME en upgrade · aucun backfill ·
downgrade symétrique · idempotent.

## 3. Contrat final du service

```
compute_and_store_quality_review(db, user_id, program_id, *, ekb=None,
                                 profile=None, computed_at=None) -> StoredQualityReview
program_to_quality_definition(program) -> ProgramDefinition
get_quality_review(db, user_id, program_id, version) -> UserProgramQualityReview | None
```
`StoredQualityReview(review, created: bool)` · exception de domaine `QualityReviewError`.

- **INSERT-ONLY** — aucun UPDATE n'est jamais émis ; l'immutabilité reste gardée deux fois (UNIQUE
  `(program, version)` + listener `before_update` de PERSISTENCE_05).
- **Appel explicite uniquement** — aucun branchement dans `validate_draft`.
- **Owner-scopé sans fuite d'existence** — inexistant et non-possédé → même erreur « Programme introuvable ».
- **Statuts** : `draft` et `validated` scorables ; `archived` et `published` refusés avec message dédié.

## 4. Idempotence

Re-scorer une version déjà tracée **retourne la trace existante** avec `created=False`, sans écriture
ni exception. Une nouvelle trace n'apparaît qu'avec une **nouvelle `current_version`** — le passé
n'est jamais recalculé.

## 5. Mapping final (13 champs)

| Colonne | Source | Colonne | Source |
|---|---|---|---|
| `user_program_id` | `program.id` | `missing_data_json` | `result.missing_data` |
| `version` | `program.current_version` | `scoring_version` | `result.scoring_version` |
| `grade` | `result.grade` | `ekb_version` | `result.ekb_version` |
| `global_score` | `result.global_score` | **`confidence`** | `result.confidence` |
| `subscores_json` | `result.subscores` | **`coverage_ratio`** | `result.coverage_ratio` |
| `alerts_json` | `result.alerts` | **`grade_cap_reason`** | `result.grade_cap_reason` |
| `suggestions_json` | `result.suggestions` | `computed_at` | paramètre ou `datetime.now(UTC)` |
| `assumptions_json` | `result.assumptions` | | |

**Adaptateur ORM→payload** : `working_sets = len(rep_targets où is_warmup est faux)` — jamais de
parsing de `set_scheme`. C'est le seul point de contact entre l'ORM et le moteur pur (SCORING_01
avait rejeté cet adaptateur faute de consommateur ; SCORING_03 **est** ce consommateur).

## 6. Tests et checks exécutés

| Suite / check | Résultat |
|---|---|
| Dédiés (`test_program_quality_reviews.py`) | **19/19 premier coup** |
| Non-régression (engine + feedback + drafts) | **51/51** |
| `check_alembic_drift` | **OK (no diff)** |
| `check_schema_snapshot` | **OK** — conforme au nouveau head `o6p1j7k8m09` |
| `check_migration_patterns` | OK — aucun pattern dangereux injustifié |
| `check_migration_roundtrip` | **OK** — schéma identique pré/post roundtrip (downgrade réversible prouvé) |
| ruff (4 fichiers) | clean |
| `check_ruff_budget` | **543 ≤ 548** (inchangé) |
| `check_spec_protocol` | PASS |
| **`check_scope`** | **MIGRATION** (attendu) |
| **Full sweep local** | **2548 passed / 1 failed** (12:41) — l'unique échec = `test_no_model_migration_schema_touched`, garde-fou arbre-sale (`git diff HEAD`), **vert post-commit** (artefact prouvé sur PERSISTENCE_01→05) |

Couverture des 19 tests : migration ajoute les 3 colonnes (introspection réelle) · snapshot les contient ·
écriture nominale et mapping · **3 champs runtime peuplés** · JSON reparsables (dont `missing_data` = 4) ·
`computed_at` explicite honoré · **idempotence** (`created=False`, aucune 2ᵉ ligne) · nouvelle version →
nouvelle trace · **aucun update déclenché** · cross-user → « introuvable » · programme inexistant → même
erreur · `archived` refusé · `published` refusé · `draft` et `validated` acceptés · lecture owner-scopée ·
adaptateur projette l'arbre · **`working_sets` hors warmups** · programme vide et exercices inconnus sans crash.

## 6bis. Deux sentinelles d'anciens builds mises à jour (hors liste initiale, signalé)

La migration change **légitimement** le head Alembic et le schéma de
`user_program_quality_reviews` — deux sentinelles d'invariance écrites par des builds
antérieurs devenaient donc **fausses par construction**. Les laisser rouges aurait été un
mensonge documentaire ; les corriger fait partie du périmètre d'un build de migration :

- `tests/test_exercise_knowledge_base.py::test_alembic_head_unchanged` (écrit par EKB_02,
  data-only) hardcodait `n5o0i6j7l98` → mis à jour vers **`o6p1j7k8m09`** ;
- `tests/test_user_program_quality_reviews_schema.py::test_quality_reviews_table_exists_with_expected_columns`
  (écrit par PERSISTENCE_03) listait les 13 colonnes d'origine → **+3** (`confidence`,
  `coverage_ratio`, `grade_cap_reason`).

Ces deux fichiers n'étaient pas dans la liste d'autorisation initiale du mandat ; leur mise à
jour est **strictement une adaptation d'assertion** au nouveau schéma (aucune logique
modifiée), signalée ici explicitement.

## 7. Note d'exécution (piège de chemin, résolu)

La régénération du snapshot lancée par chemin absolu s'est arrêtée au head **précédent** : `alembic.ini`
porte `script_location = migrations` **relatif**, résolu contre le **cwd** — c'est-à-dire le repo principal,
pas le worktree. Corrigé en exécutant l'équivalent exact de `cd <worktree> && python -m scripts.X` en une
commande atomique (`runpy` après `chdir`). Les 4 QA migration ont été lancées de la même façon. **Variante
du piège documenté en PERSISTENCE_01** — à retenir : dans un worktree, la forme `-m` avec le bon cwd est la
seule fiable.

## 8. Risques résiduels

Service **non branché** (aucun appelant automatique — Option B assumée ; le wizard sera le consommateur) ·
extension du schéma au-delà de la spec 03 §4, assumée et justifiée (§2) · `coverage_ratio` en FLOAT :
valeur déjà arrondie à 3 décimales par le moteur, aucune imprécision observée.

## 9. Confirmations de périmètre

✅ Migration additive-only (aucune table, aucun DROP en upgrade, aucun backfill) · ✅ `validate_draft`
**intact** · ✅ moteur et couche feedback **intacts** · ✅ aucun UPDATE de trace · ✅ feedback non persisté ·
✅ zéro API/UI/wizard/publication/seed · ✅ EKB non touché.

---

## Verdict

**Verdict :** 🟢 **Sb_CUSTOM_PROGRAM_SCORING_03 — PATCH COMPLETE / REVIEW PENDING.**

La table `user_program_quality_reviews`, créée sans écrivain par PERSISTENCE_03, a désormais le sien :
insert-only, owner-scopé, idempotent, et **fidèle** — les 3 champs runtime du moteur sont stockés plutôt
que perdus, pour qu'une trace figée ne mente jamais sur sa propre fiabilité. 19 dédiés premier coup +
51 non-régression ; 4 QA migration vertes ; head `o6p1j7k8m09`. **`SCORING_04`, `WIZARD_*` = NOT OPENED ·
`EKB_04` = DEFERRED.**

---

## Appendice post-merge (closeout 2026-07-25)

- **Commit build** : `713fbcc` (10 fichiers) sur `sb/custom-program-scoring-03-persistence`,
  base `b1f0b63` (rafraîchie sur le canonique via 3-way apply, contenu ASSET préservé).
- **Fix Sonar** : `74ccc28` (`tests/test_program_quality_reviews.py` uniquement) — **2 vrais
  `python:S5778`** signalés par SonarCloud sur la PR (un appel dans un `pytest.raises` à argument
  unique), **corrigés** en hoistant les bindings `other_uid`/`uid` hors du bloc `raises`. Distinct
  de l'artefact `new_coverage` : ce sont de **vraies** issues de code, arrêtées et corrigées per contrat.
- **PR #33 MERGED** — merge **`036d91c`** sur le canonique (first-parent `ff9541a`), via
  `--match-head-commit 74ccc280…` (garde anti-push-concurrent).
- **CI PR #33 : les 3 jobs GitHub verts** (pytest+QA · lint · SonarCloud).
- **CI canonique `30135595424` sur `036d91c` : 3/3 GREEN.** Les **4 QA migration** (drift ·
  snapshot · patterns · roundtrip) pour `o6p1j7k8m09` sont **rejouées vertes sur le trunk** par le
  job `pytest + QA scripts` du run canonique.
- **Check externe « SonarCloud Code Analysis » rouge** : condition en échec **unique** =
  `new_coverage` 0.0 % < 80 %. **Artefact structurel** du repo (aucun rapport de couverture Python
  n'est envoyé à SonarCloud), identique à SCORING_01/02 et aux PR #23–#27 toutes mergées.
  **Vérification API explicite** après le fix : `issues/search` sur la PR → **`total: 0`**.
- **Head Alembic canonique passé à `o6p1j7k8m09`** (revises `n5o0i6j7l98`) — premier build scoring
  à toucher le schéma ; migration **additive-only** (ADD COLUMN ×3 nullable, downgrade symétrique,
  aucun backfill).
- **Full sweep local (check_scope MIGRATION)** : 30/30 dédiés verts ; l'unique échec
  `test_no_model_migration_schema_touched` est l'artefact **by-design** d'arbre sale pré-commit
  (garde `git diff HEAD` sur `app/models/`), **vert post-commit** — comportement identique à
  PERSISTENCE_01→05.
- **Co-existence ASSET/SCORING sur le trunk** : le canonique a intégré les commits ASSET (`ff9541a`)
  et SCORING_03 **sans conflit** (surfaces disjointes : ASSET = `docs/`, SCORING = `app/` +
  `migrations/` + `tests/` + `data/`).
- **Statuts après closeout** : `SCORING_04` = **NOT OPENED** · `WIZARD_*` = **NOT OPENED** ·
  `EKB_04` = **DEFERRED UNTIL DB CONSUMER EXISTS**.
- **Cleanup** : branche `sb/custom-program-scoring-03-persistence` (remote + locale) et worktree
  `-custom-scoring-03` **conservés** — suppression au prochain GO CLEANUP.
