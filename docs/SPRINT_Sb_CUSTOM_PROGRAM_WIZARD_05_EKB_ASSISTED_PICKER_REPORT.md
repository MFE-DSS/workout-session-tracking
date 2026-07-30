# Sprint Report — Sb_CUSTOM_PROGRAM_WIZARD_05 · EKB-Assisted Exercise Picker

**Type :** BUILD (code) · **Tier check_scope :** `ISOLATED` · **Base canonique :** `1c4604d`
**Branche :** `sb/custom-program-wizard-05-ekb-picker` · **Worktree :** `workout-session-tracking-sb-custom-program-wizard-05`

---

## 1. Objectif

Ajouter au picker d'exercices de l'éditeur de brouillon une **assistance EKB en lecture seule** : un
`<datalist>` no-JS des 103 noms canoniques + métadonnées, pour améliorer l'**hygiène de nom** (un
exercice ajouté à la main devient reconnu par le scoring/WIZARD_04) et peupler optionnellement les
colonnes dénormalisées déjà existantes, **sans restreindre la saisie libre**. 17ᵉ build du track ;
cinquième surface user-facing du Custom Program.

## 2. Brainstorming / Options / Risques / Choix retenu (CLAUDE.md §3)

**Constat (préflight)** : le moteur résout l'EKB par `exercise_name` (`ekb.lookup`), donc un nom
approximatif tombe « hors EKB ». Le plus petit incrément utile = un picker de **noms canoniques**.

| Option | Verdict |
|---|---|
| **A** — picker `<datalist>` EKB + enrichissement dénormalisé optionnel | ✅ **RETENU** — additif, non bloquant, zéro perte, colonnes/contrats déjà en place. |
| B — régénération gardée sur programme non vide | ⏸️ **DIFFÉRÉ WIZARD_06** — `replace_draft_tree` écrase tout → risque de perte, surface de confirmation, hors « smallest ». |
| C — A + B | ❌ scope trop large pour un WIZARD unitaire. |

**Risques parés** : (a) **coupling → shared_code** si on touchait `program_quality_engine.py` (importé par 3 modules) → **lecteur autonome** `@lru_cache`, engine **non modifié**, tier reste ISOLATED ; (b) **datalist ne contraint pas** → intentionnel (fallback `manual` non bloquant préservé) ; (c) **gaps EKB (null)** → segments omis à l'affichage (jamais « None »), colonnes nullable ; (d) **aliases** → non résolus V1 (un alias retombe en texte libre, sans dégât) ; (e) **mutation du cache** → vues renvoient des copies fraîches.

**Choix retenu : Option A** — nouveau service isolé read-only + wiring router + datalist.

## 3. Périmètre livré

- **NEW** `app/services/user_program_exercise_catalog.py` — `picker_options()` (103 entrées triées,
  shape `{name, zone_primary, movement_pattern, equipment_family}`) + `enrich(name)` (4 champs
  dénormalisés pour match exact, sinon `{}`). `@lru_cache`, lecture seule du JSON, zéro ORM/DB, copies
  fraîches, n'importe pas le moteur.
- **MOD** `app/routers/user_programs.py` — import du catalog ; `picker_options` dans le contexte commun
  `_render_editor` ; `**enrich(exercise_name)` fusionné en tête du dict de `_append_exercise` (les clés
  contrat gagnent : nom verbatim, `source_reason="manual"`).
- **MOD** `app/templates/user_programs/detail.html` — `list="ekb-exercises"` sur l'input + un
  `<datalist>` page-level (labels métadonnées, nulls filtrés via `| select`).

## 4. Interdits respectés

✅ no migration · ✅ **EKB lu en JSON, aucune table DB** (EKB_04 reste DEFERRED) · ✅
`program_quality_engine.py` **non modifié** · ✅ `data/exercise_knowledge_base.json` **non modifié** ·
✅ no JavaScript · ✅ no `<select>` contraignant · ✅ **fallback texte libre** préservé · ✅ no
regeneration change (B → WIZARD_06) · ✅ **zéro `UserProgramQualityReview`** · ✅ no `WorkoutTemplate` ·
✅ no LLM · ✅ no claim médical · ✅ `user_program_drafts.py` / `models` non modifiés · ✅ owner-scope /
404-no-leak / quotas / statuts **inchangés**.

## 5. Tests

- **NEW** `tests/test_user_program_exercise_catalog.py` (**12 unit**) : count 103 · tri déterministe ·
  noms == clés EKB · shape · nulls honnêtes · enrichissement exact (`Adduction assise` → `variant_key`
  /`movement_pattern`/`equipment_family`, `variant_group` null) · inconnu → `{}` · casse → `{}` · alias
  → `{}` · stabilité · **immutabilité du cache**.
- **MOD** `tests/test_user_programs_editor_http.py` (**+11 WIZARD_05**) : datalist rendu + `list=` ·
  option canonique présente · label sans « None » · POST nom EKB → 303 + **colonnes dénormalisées
  peuplées** + `source_reason` manual · POST texte libre → 303 + **verbatim** + colonnes null ·
  owner-scope 404 · **quota 10 inchangé** · statut archivé refusé · **intégration WIZARD_04** (nom EKB
  reconnu `coverage_ratio > 0` ; texte libre hors agrégats sans erreur) · **zéro review persistée**.

**Validation ciblée** : `test_user_program_exercise_catalog.py` + `test_user_programs_editor_http.py`
→ **50 passed**.

## 6. Checks

- **check_scope = `ISOLATED`** (angle mort du classifieur sur l'import router parenthésé, cohérent
  WIZARD_01→04) → broad sweep `test_user_programs_*` + `test_program_quality_*` lancé quand même.
- ruff clean (fichiers neufs/modifiés) · budget respecté · check_spec_protocol PASS.
- EKB JSON hash **inchangé** · aucune migration · engine **non modifié**.

## 7. Suite

- **WIZARD_06** = régénération gardée sur programme non vide (confirmation avant écrasement).
- **Gouvernance actée (docs-only, sans scope d'implémentation)** : `SCORING_04` **SUPERSEDED**
  (re-score→WIZARD_04, publish→LAUNCH_03, activation sous-scores→curation EKB préalable) · `EKB_04`
  (seed DB) **DEFERRED** (aucun consommateur DB ; le picker lit le JSON) · `Sb_OPS` leviers 3+4
  **DEFERRED** (gate pytest complet préservé ; sélection par impact neutralisée par le conftest ;
  runner plus gros = piste optionnelle séparée).

## Verdict

**Verdict :** 🟢 **Sb_CUSTOM_PROGRAM_WIZARD_05 — PATCH COMPLETE / REVIEW PENDING.**

Le picker EKB read-only aligne la saisie manuelle sur les noms canoniques (donc sur le scoring),
peuple les colonnes dénormalisées sur match exact, et **préserve la saisie libre** — sans migration,
sans consommateur DB, sans toucher le moteur, sans JS. La régénération gardée est réservée à WIZARD_06.

---

## Appendice post-merge (closeout 2026-07-30)

- **Commit build** : `5a85941` (9 fichiers, +566/−1) sur `sb/custom-program-wizard-05-ekb-picker`,
  base `1c4604d`.
- **Fix Sonar** : `4badb0f` (1 fichier, +8/−2) — voir incident ci-dessous.
- **PR #43 MERGED** — merge **`097bf48`** sur le canonique (via `--merge --admin`, garde
  `--match-head-commit 4badb0f…fe74`, bypass du **seul** gate résiduel = `new_coverage 0.0 %`, artefact ;
  pas de squash).
- **CI PR #43** : après fix, **3 jobs GitHub verts** (`pytest + QA` **parallélisé** · `lint` ·
  `SonarCloud`) sur `4badb0f` ; job `test` = 11 min 50 s.
- **CI canonique** : run **`30530864581`** (push) sur `097bf48` → **3/3 GREEN** ; job `test` = **11 min
  43 s** (pipeline xdist Sb_OPS.ci-efficiency, vs ~37 min avant).
- **Sonar** : `issues/search total: 0` (après fix) ; `new_reliability_rating` = **A** ; seul
  `new_coverage` rouge (artefact structurel, non bloquant).
- **Incident qualité Sonar (1 vraie régression, arrêtée avant merge)** :
  - `python:S5863` ×2 — **BUG (reliability)** — `tests/test_user_program_exercise_catalog.py:100-101` :
    le test de stabilité comparait `f() == f()` (auto-comparaison), faisant passer
    `new_reliability_rating` à 3. **Fix** `4badb0f` : bindings distincts `first_*`/`second_*` (2 appels
    nommés puis comparaison), sémantique identique. Après fix : `total: 0`, reliability A. **Leçon S5863
    déjà rencontrée en WIZARD_03 — à pré-appliquer systématiquement aux tests de déterminisme/stabilité.**
- **Head Alembic inchangé** (zéro migration) · **EKB JSON inchangé** (`afa91ca6…`) ·
  `program_quality_engine.py` non modifié · **zéro `UserProgramQualityReview`** persistée.
- **Statuts après closeout** : `WIZARD_06` (régénération gardée sur programme non vide) = **FIRST NEXT /
  NOT OPENED** · `SCORING_04` = **SUPERSEDED** · `EKB_04` = **DEFERRED** · `Sb_OPS` leviers 3+4 =
  **DEFERRED**.
- **Cleanup** : branche `sb/custom-program-wizard-05-ekb-picker` (remote + locale) et worktree
  `-sb-custom-program-wizard-05` supprimés au GO CLEANUP.

**Verdict post-merge :** ✅ **Sb_CUSTOM_PROGRAM_WIZARD_05 — MERGED + CANONICAL CI GREEN.**
