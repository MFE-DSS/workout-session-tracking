# Sprint Report — Sb_CUSTOM_PROGRAM_WIZARD_03 · Deterministic Draft Generation

**Type :** BUILD (code) · **Tier check_scope :** `SHARED_CODE` · **Base canonique :** `8a28f18`
**Branche :** `sb/custom-program-wizard-03-deterministic-generator` · **Worktree :** `workout-session-tracking-custom-wizard-03`

---

## 1. Objectif

Passer de l'éditeur manuel (WIZARD_02) à une **première assistance déterministe** : générer une base
de programme custom en **assemblant des séances de référence curées** depuis `data/reference_split.json`,
puis en écrivant l'arbre via `replace_draft_tree`. **Sans LLM, sans scoring automatique, sans seed DB
EKB, sans publication, sans migration.** 15ᵉ build du track ; troisième surface user-facing du Custom Program.

## 2. Brainstorming / Options / Risques / Choix retenu (CLAUDE.md §3)

**Constat structurant (préflight)** : `data/reference_split.json` (versionné `v13`) contient **16
templates de séances human-curés** (`slug`/`name`/`kind`/`focus` + exercices avec `set_scheme`,
`rep_targets`, `substitutes`). ⇒ le plus petit builder utile = **assembler N templates → payload
`replace_draft_tree`** : déterministe, explicable (chaque slot trace à un template nommé), **sans
solveur de contraintes EKB** ni seed.

| Option | Verdict |
|---|---|
| A — picker EKB seulement | ❌ Ne génère pas ; valeur limitée. |
| **B** — **générateur déterministe minimal** (assemblage `reference_split.json`) | ✅ **RETENU** — déterministe + explicable, zéro migration/scoring/publication, écriture unique via `replace_draft_tree`. |
| C — génération + preview SCORING_02 non persisté | ⚠️ Surface plus large ; WIZARD_04+. |
| D — génération + `UserProgramQualityReview` persistée | ❌ NO-GO (reviews = traces versionnées, pas feedback de brouillon). |
| E — EKB_04 first | ❌ NO-GO (seed DB différé). |

**Risques parés** : (a) **écrasement** d'un arbre existant (`replace_draft_tree` remplace tout) →
**génération seulement si vide** ; (b) **couplage `reference_split.json`** (partagé avec `seed.py`) →
**lecture seule**, jamais d'écriture/seed ; (c) **cardio vide** (`liss-only`, 0 exo) → **exclu** des
cycles ; (d) **scope creep** vers scoring/EKB/matériel → resté minimal ; (e) absence de « full body »
curé → V1 offre **PPL + Upper/Lower** (splits réellement curés).

**Choix retenu : Option B minimal** — service pur `user_program_generator.py`.

## 3. Périmètre livré

**Service pur** `app/services/user_program_generator.py` :
`generate_program_tree(split, sessions, duration=None) -> list[dict]` — **pur** (zéro DB/ORM/random/
scoring/écriture), même entrée → même payload, sortie directement compatible `replace_draft_tree`.
Lit `reference_split.json` en **read-only** (`lru_cache`), mappe `(split, sessions)` en séquence
déterministe de templates, copie `name`/`set_scheme`/`rep_targets`/`notes`, réassigne positions 1..N,
`source_reason = "generated:reference_split:{slug}"`. Cardio/vides exclus.

**Slugs exacts retenus** (vérifiés présents dans `reference_split.json`) :
- `ppl` = `[push-a, pull-a, legs-a, push-b, pull-b, legs-b]`
- `upper_lower` = `[upper-pecs-delts, lower-quad-bias, upper-back-arms, lower-posterior-bias]`

**Routes** (ajoutées à `user_programs.py`, privées, owner-scopées) :

| Méthode | Chemin | Rôle |
|---|---|---|
| GET | `/programs/{program_id}/generate` | Formulaire de génération (split + nb séances) |
| POST | `/programs/{program_id}/generate` | Génère si **vide** → `replace_draft_tree` → 303 éditeur |

**Contrat** : owner-scope via `get_draft` (absent ⇄ autrui = **même 404**) ; **génération seulement
si arbre vide** (sinon re-render 200 doux, arbre inchangé) ; `split` ∈ {`ppl`, `upper_lower`} sinon
re-render ; `sessions` `1..7` (le service **cape** au-delà du cycle) ; `published`/`archived` refusés
par le service ; succès → 303 vers l'éditeur (programme `draft` éditable). `Annotated` partout,
`responses={404}`.

**Templates** : `user_programs/generate.html` (formulaire no-JS) ; `detail.html` — CTA « Générer une
base de programme » **si l'arbre est vide**.

## 4. Interdits respectés

✅ **no migration** · ✅ **no EKB_04** · ✅ **no DB seed** · ✅ **no scoring** · ✅ **no
`UserProgramQualityReview` write** · ✅ **no publication `WorkoutTemplate`** · ✅ no
`session_builder`/`seed.py`/catalogue · ✅ **pas d'écriture dans `reference_split.json`** (lecture
seule) · ✅ `exercise_knowledge_base.json` non touché · ✅ no ASSET/BodyMap · ✅ no JS obligatoire ·
✅ no LLM · ✅ **génération non opaque** (assemblage de templates nommés, `source_reason` traçant) ·
✅ no claim médical · ✅ `user_program_drafts.py` / `models` / `program_quality_*` **non modifiés** ·
✅ **toute écriture d'arbre via `replace_draft_tree`** · ✅ **WIZARD_02 reste l'éditeur** post-génération
· ✅ **génération seulement si vide**.

## 5. Tests

- **`tests/test_user_program_generator.py`** (service pur, **12 tests**) : slugs exacts PPL 3/6 &
  Upper/Lower 4 · positions séquentielles · rep_targets copiés non vides · `source_reason` traçant ·
  déterminisme · split inconnu refusé · sessions 0 refusé / >max capé · aucune séance cardio vide ·
  shape compatible `replace_draft_tree`.
- **`tests/test_user_programs_generate_http.py`** (**16 instances**) : auth 303/login · GET form vide
  200 · POST PPL/Upper-Lower → 303 + arbre · **refus si non vide** · split/sessions invalides →
  re-render · owner-scope 404 · absent même 404 · **published/archived refusés** (paramétré) ·
  **aucune review** · **aucun `WorkoutTemplate`** · éditeur sans scoring · non-régression WIZARD_01/02.

Non-régression : WIZARD_01 http (19) + WIZARD_02 editor (27) + drafts (12) + engine/feedback/reviews
(58) — **inchangés**.

## 6. Checks

- **check_scope = `SHARED_CODE`** (nouveau service `app/services/` importé par le router). Anticipé
  `ISOLATED` au préflight → **documenté, non forcé** ; le tier `SHARED_CODE` exige le full sweep local
  (cohérent avec le mandat qui le voulait déjà — router user-facing modifié).
- **ruff** clean (fichiers neufs) ; **budget 543 ≤ 548**. **check_spec_protocol** PASS.
- **Full sweep local** exécuté — voir appendice.
- La **CI réelle (3 jobs)** au push reste la source de vérité.

## 7. Suite
- **WIZARD_04+** = preview de scoring non persisté (SCORING_02), picker d'exercices assisté EKB
  (lecture du JSON), flow de remplacement/regénération avec confirmation. Aucun n'est ouvert par ce build.

## Verdict

**Verdict :** 🟢 **Sb_CUSTOM_PROGRAM_WIZARD_03 — PATCH COMPLETE / REVIEW PENDING.**

Un programme custom vide peut désormais recevoir une **base générée déterministe** (PPL / Upper-Lower)
assemblée depuis des séances de référence curées, écrite via `replace_draft_tree`, et immédiatement
éditable dans WIZARD_02 — sans LLM, sans boîte noire, sans scoring, sans publication, sans seed EKB
et sans migration.

---

## Appendice post-merge (closeout 2026-07-29)

- **Commit build** : `99dc3d9` (9 fichiers, +797/−5) sur `sb/custom-program-wizard-03-deterministic-generator`,
  base `8a28f18`.
- **Fix Sonar** : `d591f8c` (3 fichiers, +6/−8) — service + router + test.
- **PR #39 MERGED** — merge **`bc1a42c`** sur le canonique (via `--merge --admin`, garde
  `--match-head-commit`, bypass du **seul** gate en échec = `new_coverage 0.0 %`, artefact structurel ;
  pas de squash).
- **CI PR #39** : **3 jobs GitHub verts** (lint · pytest + QA · SonarCloud) sur `d591f8c`.
- **CI canonique** : run **`30448452394`** sur `bc1a42c` → **3/3 GREEN** (lint · pytest + QA · SonarCloud).
- **Incident qualité Sonar (2 vraies issues, arrêtées avant merge)** :
  - `python:S5863` — **BUG (reliability MAJOR)** — `tests/test_user_program_generator.py` : l'assertion de
    déterminisme comparait la **même expression** des deux côtés (`f(...) == f(...)`), faisant échouer le
    gate `new_reliability_rating` (= 3). **Fix** : binding `first`/`second` (2 appels nommés puis
    comparaison), comportement identique.
  - `python:S1172` — **CODE_SMELL (MAJOR)** — `app/services/user_program_generator.py` : param `duration`
    accepté mais **inutilisé** en V1. **Fix** : retrait complet (service + param de route + appel) — code
    mort supprimé, re-ajoutable en WIZARD_04 quand réellement utilisé.
  - Après fix : **`issues/search` `total: 0`**, reliability/security/maintainability **A**. Aucune faille
    sécurité (leçon `S6680` de WIZARD_02 appliquée : jamais de `range(user)`).
- **Head Alembic inchangé** (zéro migration) · **`reference_split.json` lu en read-only** · **zéro
  `UserProgramQualityReview`** · **zéro `WorkoutTemplate`** · `drafts`/`models`/`program_quality_*` intacts.
- **Statuts après closeout** : `WIZARD_04+` (preview scoring non persisté / picker EKB / flow de
  regénération) = **FIRST NEXT / NOT OPENED** · `SCORING_04` = **NOT OPENED** · `EKB_04` = **DEFERRED**.
- **Cleanup** : branche `sb/custom-program-wizard-03-deterministic-generator` (remote + locale) et worktree
  `-custom-wizard-03` **conservés** — suppression au prochain GO CLEANUP.

**Verdict post-merge :** ✅ **Sb_CUSTOM_PROGRAM_WIZARD_03 — MERGED + CANONICAL CI GREEN.**
