# Sprint Report — Sb_CUSTOM_PROGRAM_WIZARD_02 · Draft Tree Editor

**Type :** BUILD (code) · **Tier check_scope :** `ISOLATED` · **Base canonique :** `3a3a1d4`
**Branche :** `sb/custom-program-wizard-02-draft-tree-editor` · **Worktree :** `workout-session-tracking-custom-wizard-02`

---

## 1. Objectif

Rendre **éditable** un programme custom draft déjà créé par WIZARD_01 : enrichir la page détail
`/programs/{program_id}` en **éditeur SSR no-JS** permettant d'ajouter/supprimer des séances et des
exercices (avec rep targets simples) et de valider le brouillon — **sans générateur, sans scoring,
sans publication, sans migration**. 14ᵉ build du track ; deuxième surface user-facing du Custom Program.

## 2. Brainstorming / Options / Risques / Choix retenu (CLAUDE.md §3)

**Constat structurant (préflight)** : le service `replace_draft_tree(db, user_id, program_id,
sessions_payload)` **existe déjà, testé**, et reconstruit **tout l'arbre** server-side en appliquant
quotas (7 séances / 10 exercices), positions séquentielles, règles de statut (draft/validated
éditables ; `validated`→`draft` à l'édition ; `published`/`archived` refusés) et owner-scope. WIZARD_02
n'est donc que la **couche route/UI** par-dessus.

| Option | Verdict |
|---|---|
| A — form global `replace_tree` | ⚠️ Service idéal mais **UX no-JS lourde** (arbre nested dans un seul form). |
| **B** — actions SSR granulaires **sur `replace_tree`** | ✅ **RETENU** — UX mobile naturelle, réutilise le service testé, **zéro migration, zéro nouveau service**. |
| C — service-only | ❌ Insuffisant après WIZARD_01. |
| D — wizard guidé + génération | ❌ Trop tôt = WIZARD_03+. |
| E — EKB-first (rouvrir EKB_04) | ❌ Interdit. |

**Risques parés** : (a) **staleness des positions** en édition concurrente → brouillon mono-utilisateur,
adressage par position documenté ; (b) `replace_draft_tree` **recrée les ids enfants** à chaque action
→ sans impact (aucune réf externe aux ids) ; (c) **scope creep** vers EKB/génération → resté texte
libre manuel ; (d) **couplage WIZARD_03** faible (même service, `source_reason="manual"` distingue).

**Choix retenu : Option B** — actions granulaires déléguant à `replace_draft_tree`.

## 3. Périmètre livré

**Routes** (ajoutées à `app/routers/user_programs.py`, toutes privées `CurrentUser`, owner-scopées) :

| Méthode | Chemin | Action |
|---|---|---|
| GET | `/programs/{program_id}` | **Éditeur** (détail enrichi : arbre + forms) |
| POST | `/programs/{program_id}/sessions` | Ajouter une séance (`name`) |
| POST | `/programs/{program_id}/sessions/{position}/delete` | Supprimer la séance |
| POST | `/programs/{program_id}/sessions/{position}/exercises` | Ajouter un exercice (`exercise_name`, `sets`, `min_reps`, `max_reps`) |
| POST | `/programs/{program_id}/sessions/{session_position}/exercises/{exercise_position}/delete` | Supprimer l'exercice |
| POST | `/programs/{program_id}/validate` | Valider le brouillon (`validate_draft`) |

**Contrat** : owner-scope via `get_draft` (absent ⇄ autrui = **même 404 `Programme introuvable`**) ;
succès mutation → **303** vers l'éditeur ; erreur service/quota/statut ou validation de form →
**re-render 200** avec message doux ; `published`/`archived` refusés par le service ; `validated`
repasse `draft` à l'édition.

**Helpers créés (dans le router, aucun nouveau service)** : `_tree_to_payload(program)`,
`_resequence(payload)`, `_append_session`, `_delete_session`, `_append_exercise`, `_delete_exercise`,
`_validate_exercise_form`, `_render_editor`, `_owned_or_404`, `_redirect_to_editor`. Les règles
métier profondes (quotas/positions/statuts) restent **owned par `replace_draft_tree`** — jamais
dupliquées.

**Ajout d'exercice** : `rep_targets = [{min_reps, max_reps}] × sets`, `set_scheme = f"{sets}x {min}-{max}"`,
`source_reason="manual"`. Bornes de form : `sets 1..6`, `min_reps`/`max_reps` `1..50`, `min ≤ max`,
`exercise_name` requis ≤ 255.

**Template** : `app/templates/user_programs/detail.html` enrichi en éditeur no-JS (arbre + forms
d'ajout/suppression + bouton valider), **gating par statut éditable** (forms masqués si
`published`/`archived`), message si arbre vide, hint « éditer un validé le repasse en brouillon ».

## 4. Interdits respectés

✅ **no migration** · ✅ **no new service** (`user_program_drafts.py` non modifié) · ✅ **no scoring** ·
✅ **no `UserProgramQualityReview` write** · ✅ **no publication `WorkoutTemplate`** · ✅ no
`session_builder`/seed/catalogue · ✅ no EKB_04 · ✅ no ASSET/BodyMap/`static/assets/auren` · ✅ no JS
obligatoire · ✅ no LLM/générateur · ✅ no claim médical · ✅ `app/models/user_program.py` /
`program_quality_*` **non modifiés** · ✅ `app/main.py` **non touché** (router déjà monté par WIZARD_01).

## 5. Tests

`tests/test_user_programs_editor_http.py` — **27 tests** (dont 4 paramétrés) : auth 303/login ×3 ·
éditeur rend l'arbre vide · ajout séance position 1 · trim · nom vide → re-render · **quota 7** → 8ᵉ
refusée · suppression séance + re-séquençage · ajout exercice + rep_targets + `source_reason=manual` ·
form invalide (nom espaces / sets 0 / min 0 / min>max) → re-render sans row · **quota 10** → 11ᵉ
refusé · suppression exercice + re-séquençage · **owner-scope** mutation autrui → 404 · absent → même
404 · `published`/`archived` → édition refusée · `validated` édité → repasse `draft` · validate complet
→ `validated` · validate vide → erreur douce · **aucune `UserProgramQualityReview`** · **aucun
`WorkoutTemplate`** · éditeur sans scoring · non-régression WIZARD_01.

Non-régression : `test_user_programs_http.py` (19) + `test_user_program_drafts.py` (12) + engine/feedback/reviews (58) **inchangés**.

## 6. Checks

- **check_scope = `ISOLATED`** (router feuille + template + tests ; service/model/main non touchés).
- **ruff** : `All checks passed` ; **budget 543 ≤ 548**. **check_spec_protocol** : PASS.
- **Full sweep local** exécuté (router user-facing modifié) — voir appendice.
- La **CI réelle (3 jobs)** au push reste la source de vérité de non-régression globale.

## 7. Suite
- **WIZARD_03+** = générateur déterministe (spec 01 §11), liaison EKB (lecture/sélection), branchement
  éventuel du scoring/feedback sur le flow. Aucun n'est ouvert par ce build.

## Verdict

**Verdict :** 🟢 **Sb_CUSTOM_PROGRAM_WIZARD_02 — PATCH COMPLETE / REVIEW PENDING.**

Un programme custom draft est désormais **constructible manuellement** par l'utilisateur — séances,
exercices, rep targets, validation — via un éditeur SSR no-JS owner-scopé, en déléguant toute la
persistance au service testé, sans générateur, sans scoring, sans publication et sans migration.

---

## Appendice post-merge (closeout 2026-07-28)

- **Commit build** : `5fd1f52` (6 fichiers, +962/−39) sur `sb/custom-program-wizard-02-draft-tree-editor`,
  base `3a3a1d4`.
- **Fix Sonar** : `65e7043` (`app/routers/user_programs.py` seul, +4/−1).
- **PR #37 MERGED** — merge **`790fedb`** sur le canonique (via `--merge --admin`, garde
  `--match-head-commit`, bypass du **seul** gate en échec = `new_coverage 0.0 %`, artefact structurel ;
  pas de squash).
- **CI PR #37** : **3 jobs GitHub verts** (pytest + QA · lint · SonarCloud) sur `65e7043`.
- **CI canonique** : run **`30394952158`** sur `790fedb` → **3/3 GREEN** (pytest + QA · lint · SonarCloud).
- **Incident sécurité Sonar `pythonsecurity:S6680` (CRITICAL)** : la première analyse a signalé une
  **vraie vulnérabilité** — `for _ in range(sets)` (ligne 208) bornait une boucle sur une valeur
  `sets` user-contrôlée (flux taint form → `_append_exercise` → `range`), faisant échouer le gate
  `new_security_rating` (= 4). **Arrêt (pas de merge) + rapport**, puis correctif sur GO :
  `range(min(sets, _MAX_SETS))` (sanitizer au sink, comportement inchangé car `sets` déjà validé
  `1..6` en amont ; defense-in-depth). Après fix : **`issues/search` `total: 0`**, `new_security_rating`
  repassé **A (1)** ; seul `new_coverage` reste rouge. Distinct de l'artefact `new_coverage`.
- **Head Alembic inchangé** (zéro migration) · **aucun nouveau service** (`user_program_drafts.py`
  et le modèle intacts) · **zéro `UserProgramQualityReview`** · **zéro `WorkoutTemplate`**.
- **Statuts après closeout** : `WIZARD_03+` (génération déterministe / liaison EKB / scoring branché
  éventuel) = **FIRST NEXT / NOT OPENED** · `SCORING_04` = **NOT OPENED** · `EKB_04` = **DEFERRED**.
- **Cleanup** : branche `sb/custom-program-wizard-02-draft-tree-editor` (remote + locale) et worktree
  `-custom-wizard-02` **conservés** — suppression au prochain GO CLEANUP.

**Verdict post-merge :** ✅ **Sb_CUSTOM_PROGRAM_WIZARD_02 — MERGED + CANONICAL CI GREEN.**
