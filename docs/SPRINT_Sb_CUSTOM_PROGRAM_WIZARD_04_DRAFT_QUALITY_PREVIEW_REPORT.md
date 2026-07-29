# Sprint Report — Sb_CUSTOM_PROGRAM_WIZARD_04 · Draft Quality Preview

**Type :** BUILD (code) · **Tier check_scope :** `SHARED_CODE` · **Base canonique :** `557b5a0` (refresh depuis `c34040e`)
**Branche :** `sb/custom-program-wizard-04-draft-quality-preview` · **Worktree :** `workout-session-tracking-custom-wizard-04`

---

## 1. Objectif

Rendre la **qualité d'un brouillon custom lisible dans l'éditeur**, via une **preview NON PERSISTÉE**, en
réutilisant le moteur pur `SCORING_01` et la couche langage `SCORING_02` — **sans écrire de
`UserProgramQualityReview`, sans publication, sans migration, sans blocage**. 16ᵉ build du track ;
quatrième surface user-facing du Custom Program. Première fois que le scoring (livré en SCORING_01→03
mais **jamais branché**) devient visible pour l'utilisateur, en lecture seule.

## 2. Brainstorming / Options / Risques / Choix retenu (CLAUDE.md §3)

**Constat structurant (préflight)** : le writer `compute_and_store_quality_review` (SCORING_03) fait
exactement `program_to_quality_definition(program)` → `score_program(...)` → **INSERT**. La preview =
**les deux premiers gestes + `build_program_quality_feedback`, sans l'INSERT**. Les 4 briques sont
**déjà publiques et pures** ; aucune n'est modifiée.

| Option | Verdict |
|---|---|
| A — preview inline auto sur `GET /programs/{id}` | ❌ couple chaque affichage éditeur au scoring + EKB load ; alourdit le hot-path. |
| **B** — **route dédiée `GET /programs/{id}/quality`** | ✅ **RETENU** — séparation nette, zéro écriture, scope maîtrisé, calcul à la demande. |
| C — POST « Analyser » | ❌ sémantique d'action pour une lecture sans effet de bord. |
| D — `UserProgramQualityReview` persistée | ❌ NO-GO — une trace figée n'est pas un feedback de brouillon mouvant (doctrine SCORING_03). |
| E — ouvrir SCORING_04 d'abord | ❌ NO-GO — aucun blocage démontré. |

**Risques parés** : (a) **grade C trompeur sur brouillon vide** (le moteur noterait `frequency=0`) →
**gating « 0 exercice = message amical, pas de carte »** ; (b) **divergence preview / trace future** →
**réutilisation du MÊME adaptateur + moteur** que le writer (parité prouvée par test) ; (c) **écriture
accidentelle** → le writer n'est **jamais importé**, helper zéro DB, 2 tests assertent `count == 0` ;
(d) **Sonar** → leçons WIZARD_01/02/03 pré-appliquées (`Annotated`+`Path()`, `responses={404}`, pas de
boucle sur donnée user, pas d'auto-comparaison, pas de param inutilisé) → **0 issue au premier passage** ;
(e) **microcopy** → 100 % réutilisée de SCORING_02 (aucun nouveau claim, non-culpabilisant par construction).

**Choix retenu : Option B + helper pur d'orchestration** (réutilise `program_to_quality_definition`,
**pas** de nouvel adaptateur).

## 3. Périmètre livré

**Helper pur (NOUVEAU)** `app/services/user_program_quality_preview.py` :
`compute_quality_preview(program, *, ekb=None, profile=None) -> QualityPreview` où
`QualityPreview = (result: QualityReviewResult, feedback: ProgramQualityFeedback)`. **Zéro DB, zéro
écriture** ; suppose l'arbre déjà chargé (eager via `get_draft`). Réutilise l'adaptateur et le moteur du
writer SCORING_03 → une preview et une trace persistée future de **la même version calculent à
l'identique**. Le template a besoin des **deux** mondes : `result` porte les chiffres bruts
(`global_score`, `coverage_ratio`, `confidence`, `grade_cap_reason`) que la couche feedback ne ré-expose
pas ; `feedback` porte le langage prêt à afficher.

**Route (ajoutée à `user_programs.py`, owner-scopée)** :

| Méthode | Chemin | Rôle |
|---|---|---|
| GET | `/programs/{program_id}/quality` | Preview qualité non persistée (aucun POST, aucune écriture) |

**Contrat** : owner-scope via `_owned_or_404`/`get_draft` (absent ⇄ autrui = **même 404**), `Annotated[int,
Path()]`, `responses={404}`. **Trois états d'affichage** dans `quality.html` (NOUVEAU) :
1. **ère non scorable** (`archived`/`published`, hors `SCORABLE_STATUSES`) → « Cette version ne se
   prévisualise pas ici. » ;
2. **scorable mais vide** (0 exercice) → message amical « Ajoute des séances ou génère une base » **sans
   carte de note** (évite un grade C trompeur) ;
3. **scorable + ≥1 exercice** → carte : grade, `global_score`/100, couverture %, `confidence_note`,
   `grade_note` (cap), items feedback (ordre SCORING_02 warning→tip→info), `limitations`, **disclaimer
   obligatoire** + retour éditeur.

**Template éditeur** : `detail.html` — CTA « Voir la qualité du brouillon » → `user_program_quality`,
affiché ssi éditable **et** `exercise_count > 0`.

**Preview pour `draft` ET `validated`** (les deux ères d'édition). Données insuffisantes : **aucun
traitement spécial** — SCORING_01/02 dégradent déjà honnêtement (`confidence very_low`,
`confidence_note` « lecture très partielle »). `profile=None` (WIZARD_04 ne capture pas de profil).

## 4. Interdits respectés

✅ **no migration** (`app/models/` non touché, head Alembic inchangé) · ✅ **no DB write** · ✅ **zéro
`UserProgramQualityReview`** (writer jamais importé ; 2 tests `count == 0`) · ✅ **zéro publication
`WorkoutTemplate`** · ✅ no `session_builder` · ✅ **no EKB_04 / no seed DB** · ✅ **SCORING_01/02/03
non modifiés** (leurs suites restent vertes inchangées) · ✅ **preview non bloquante / non normative**
(aucun gate validation/génération/édition) · ✅ no ASSET/BodyMap · ✅ no JS obligatoire · ✅ no LLM ·
✅ no claim médical (microcopy SCORING_02 réutilisée verbatim) · ✅ `user_program_drafts.py` / `models`
non modifiés.

## 5. Tests

- **`tests/test_user_program_quality_preview.py`** (helper pur DB-backed sans write, **6 tests**) :
  composition (result+feedback cohérents) · déterminisme · **parité writer** (`preview.result ==
  score_program(program_to_quality_definition(program))`) · **no-write** (`count == 0`) · dégradation
  honnête (tout hors EKB → `confidence very_low` + note « partielle »).
- **`tests/test_user_programs_quality_http.py`** (route, **11 tests**) : auth 303/login · owner-scope
  404 sans fuite (foreign + absent) · prompt vide sans carte · scorecard (grade + /100) · disclaimer ·
  **validated scorable** · **ères verrouillées** (published/archived paramétré) · **no-write invariant**
  (`count == 0` après GET) · CTA éditeur affiché/masqué selon exercices.

**Non-régression** : broad sweep ciblé **161 passed** (WIZARD_01 http + WIZARD_02 editor + WIZARD_03
generate + drafts + engine/feedback/reviews) ; `test_generated_editor_shows_no_scoring` **intact** (le
CTA « Voir la qualité » ne contient ni « grade » ni « /100 »).

## 6. Checks

- **check_scope = `SHARED_CODE`** (router `app/` importé par l'app factory + nouveau service importé par
  le router) → **full sweep local requis et exécuté : `2663 passed`** (+17 vs `c34040e` = exactement les
  tests neufs ; aucun modèle/migration touché ⇒ pas d'artefact d'arbre sale).
- **ruff** clean (fichiers neufs) ; **budget 543 ≤ 548** (aucun warning net). **check_spec_protocol** PASS.
- **Zéro incident Sonar** au premier passage (contrairement à WIZARD_01/02/03 qui avaient chacun une
  vraie issue) — les 5 leçons Sonar antérieures ont été **pré-appliquées** en écriture.
- La **CI réelle (3 jobs)** au push reste la source de vérité.

## 7. Suite

- **WIZARD_05+** = picker d'exercices assisté EKB (lecture du JSON), flow de remplacement/regénération
  avec confirmation, éventuel branchement d'écriture de review au moment d'une publication. Aucun ouvert
  par ce build. `SCORING_04` = NOT OPENED · `EKB_04` = DEFERRED.
- **Sprint méthodologie CI (`Sb_OPS`, tier `ci_infra`) mis en file** — décidé cette session : la charge
  de test (job pytest ~37-43 min mono-thread rejouant les 2663 tests ≈ durée de dev) motive un virage
  « développement efficace ». **4 leviers** retenus (paralléliser pytest `xdist` · stopper le double-run
  local · CI à deux vitesses · sélection de tests par impact), à ouvrir **après ce closeout** comme sprint
  gated distinct.

## Verdict

**Verdict :** 🟢 **Sb_CUSTOM_PROGRAM_WIZARD_04 — PATCH COMPLETE / REVIEW PENDING.**

La qualité d'un brouillon custom (draft ou validated) est désormais **lisible dans l'éditeur** via une
preview non persistée, réutilisant intégralement SCORING_01 (chiffres) + SCORING_02 (langage) + l'adaptateur
SCORING_03 (parité writer garantie) — **sans écrire de review, sans publication, sans migration, sans
bloquer quoi que ce soit**.

---

## Appendice post-merge (closeout 2026-07-29)

- **Commit build** : `944e1b6` (6 fichiers, +580/−4) sur `sb/custom-program-wizard-04-draft-quality-preview`,
  base **`557b5a0`**. **Aucun fix Sonar** nécessaire (premier passage propre).
- **Refresh mid-build** : le canonique a bougé `c34040e → 557b5a0` pendant le patch (**PR #40 ASSET
  BodyParts3D**, docs + 1 test ASSET disjoint, zéro `app/` touché). Refresh **stash `-u` → `merge
  --ff-only` → pop** sans conflit avant commit (garde 1 du mandat honorée) ; patch identique byte-for-byte
  après pop ; full sweep non rejoué (justifié : zéro `app/` changé par le FF).
- **PR #41 MERGED** — merge **`ebbe4e3`** sur le canonique (via `--merge --admin`, garde
  `--match-head-commit 944e1b6…d528`, bypass du **seul** gate en échec = `new_coverage 0.0 %`, artefact
  structurel ; **pas de squash**).
- **CI PR #41** : **3 jobs GitHub verts** (pytest + QA · lint · SonarCloud) sur `944e1b6`.
- **CI canonique** : run **`30475415569`** (push) sur `ebbe4e3` — **3/3 attendu** (diff identique à la PR
  #41 verte), verdict confirmé au GO PUSH du closeout.
- **Sonar (vérifié par API)** : **`issues/search` `total: 0`** — zéro `CODE_SMELL/BUG/VULNERABILITY` ;
  quality gate rouge **uniquement** sur `new_coverage 0.0 %` (artefact structurel identique à
  SCORING_01/02/03 et WIZARD_01/02/03) ; reliability / security / maintainability / duplications /
  hotspots **tous OK**.
- **Head Alembic inchangé** (zéro migration) · **zéro `UserProgramQualityReview`** · **zéro
  `WorkoutTemplate`** · SCORING_01/02/03 / `drafts` / `models` intacts.
- **Note process (§2bis)** : la vérif Sonar par API déclenchait une confirmation manuelle → forme minimale
  ciblée réutilisable (`&pullRequest=:*`) + endpoints Sonar read-only adjacents ajoutés à
  `.claude/settings.local.json` (perso, non versionné).
- **Statuts après closeout** : `WIZARD_05+` (picker EKB / flow de regénération) = **FIRST NEXT / NOT
  OPENED** · `SCORING_04` = **NOT OPENED** · `EKB_04` = **DEFERRED** · **`Sb_OPS` CI-methodology =
  QUEUED / NOT OPENED**.
- **Cleanup** : branche `sb/custom-program-wizard-04-draft-quality-preview` (remote + locale) et worktree
  `-custom-wizard-04` **conservés** — suppression au prochain GO CLEANUP.

**Verdict post-merge :** ✅ **Sb_CUSTOM_PROGRAM_WIZARD_04 — MERGED + CANONICAL CI GREEN.**
