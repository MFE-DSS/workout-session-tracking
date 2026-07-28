# Sprint Report — Sb_CUSTOM_PROGRAM_WIZARD_01 · Custom Program Creation Entry Flow

**Type :** BUILD (code) · **Tier check_scope :** `ISOLATED` · **Base canonique :** `805b8a9`
**Branche :** `sb/custom-program-wizard-01-entry-flow` · **Worktree :** `workout-session-tracking-custom-wizard-01`

---

## 1. Objectif

Ouvrir le **premier flow utilisateur** du track Custom Program : rendre la **création d'un
programme personnel** accessible depuis le navigateur, via un flow SSR minimal et contrôlé,
**sans** casser le modèle existant. 13ᵉ build du track ; premier à exposer une surface HTTP+UI
pour `UserProgram` (jusqu'ici modèle + service + migrations seulement, jamais atteignable par un
utilisateur).

Le service de drafts (`app/services/user_program_drafts.py`) était déjà **owner-scopé et
quota-gardé** ; WIZARD_01 n'ajoute qu'une **couche SSR fine** par-dessus, en clonant le patron
`squads` (GET formulaire → POST → 303 redirect-after-post).

## 2. Brainstorming / Options / Risques / Choix retenu (CLAUDE.md §3)

**Options évaluées (préflight) :**

| Option | Description | Verdict |
|---|---|---|
| A | Service-only (parse/intake → payload, zéro route) | ❌ Le service existe déjà ; sans route, aucune entrée utilisateur. |
| **B** | **SSR minimal** (écran « Créer » + POST → draft minimal) | ✅ **RETENU** — plus petite surface user-facing, idiomatique SSR/no-JS, clone `squads`. |
| C | API JSON minimal | ❌ Hors-idiome (app SSR/no-JS). |
| D | Wizard guidé complet multi-step | ❌ Exige le générateur déterministe (spec 01 §11) + `wizard_answers_json` (migration) + 6 écrans. = WIZARD_02+/03+. |
| E | Différer, faire EKB_04 | ❌ `EKB_04` reste `DEFERRED` ; WIZARD ouvert par l'opérateur. |

**Contrainte structurante découverte au préflight :** la table racine `UserProgram` ne porte
**aucune colonne** pour durée/séances/split/objectif/matériel/contraintes (docstring PERSISTENCE_01 :
*« wizard payloads … arrive in later, separately gated builds »*). ⇒ la **plus petite entrée
persistable = le titre seul** (slug dérivé serveur). Tout le reste exigerait une migration ⇒ hors
périmètre « très petit ».

**Risques identifiés & parés :**
- *Dead-end UX* (draft vide non éditable) → message explicite « L'édition détaillée arrive dans le
  prochain lot » ; aucune promesse de programme lançable.
- *Scope creep vers la génération* → rester **manuel** ; générateur déterministe = WIZARD_03+.
- *Couplage publication future* (spec 05 §5, slug `up{uid}-{slug_base}-v{n}`) → dérivation slug
  soignée (ASCII, lowercase, tirets, ≤64) dès maintenant.
- *Régression entrypoint* (`app/main.py` touché) → full sweep local malgré le tier ISOLATED.

**Choix retenu : Option B**, création **manuelle** d'un draft vide, zéro migration/scoring/publication.

## 3. Périmètre livré

**Routes (SSR, sous `entra`… non — auth cookie signé `CurrentUser`) :**

| Méthode | Chemin | Nom | Rôle |
|---|---|---|---|
| GET | `/programs` | `user_programs_list` | Librairie owner-scopée (archivés exclus) + CTA « Créer un programme » |
| GET | `/programs/new` | `user_program_new` | Formulaire titre (no-JS) |
| POST | `/programs` | `user_program_create` | `create_draft(title)` → 303 vers le détail |
| GET | `/programs/{program_id}` | `user_program_detail` | Récap minimal owner-scopé |

`/programs/new` est **déclaré avant** `/programs/{program_id}` (contrat d'ordre de route).
**Garde de conflit vérifiée** : aucune route `/programs` préexistante (le catalogue système est
`/library`, `pages.py`) — **pas de shadowing**.

**Fichiers :**
- **Neufs** : `app/routers/user_programs.py` · `app/templates/user_programs/{list,new,detail}.html` ·
  `tests/test_user_programs_http.py` · ce rapport.
- **Modifiés minimaux** : `app/main.py` (1 import + 1 `include_router` + commentaire) ·
  `app/templates/base.html` (lien secondaire « Mes programmes » dans le menu topbar **et** le rail
  « Plus », là où vivent Squads/Classement — aucun changement des 4 onglets primaires) ·
  `docs/strategy/SPEC_REGISTRY.md` · `docs/strategy/ROADMAP_AND_NEXT_STEPS.md`.

## 4. Contrats

**Entrée** (`POST /programs`) : `title = Form(...)`, trim, `1..128` caractères. `slug_base` **dérivé
serveur** (`_slugify` : NFKD → ASCII, lowercase, runs non-sûrs → tiret, borné 64, fallback
`"programme"`) — **jamais demandé** à l'utilisateur ; collision même user → message de service
(pas de suffixe automatique en WIZARD_01).

**Sortie** : succès → **303** vers `/programs/{id}` ; titre vide/espaces/trop long, quota, collision →
**re-render 200** avec message doux. Non authentifié → **303 /login**. Programme d'autrui ou absent →
**même 404 indistinct** (`get_draft` renvoie `None` dans les deux cas ; aucune fuite d'existence).

**Quota réutilisé** : `MAX_ACTIVE_PROGRAMS = 10` (déjà appliqué dans `create_draft`).

## 5. Interdits respectés

- ✅ **no migration** — les tables `user_programs*` existent déjà (4 migrations appliquées) ; création par titre = zéro schéma.
- ✅ **no scoring** — le moteur `program_quality_engine`/`feedback`/`reviews` n'est pas branché ni importé.
- ✅ **no review write** — aucune `UserProgramQualityReview` écrite (test dédié) ; une review reste un artefact **de publication** (spec 03 §9-C).
- ✅ **no publication** — aucun `WorkoutTemplate` créé (test dédié) ; `session_builder` intact.
- ✅ **no EKB_04** · ✅ **no ASSET / BodyMap** · ✅ **no `app/static/assets/auren`** · ✅ **no JS obligatoire** · ✅ **no LLM/générateur** · ✅ **no claim médical**.
- ✅ `user_program_drafts.py`, `app/models/user_program.py`, `program_quality_*` **non modifiés**.

## 6. Tests

`tests/test_user_programs_http.py` — **19 tests** (fixture `client` authentifiée) :
auth 401→303/login (liste/new/POST) · GET liste/new 200 · POST 201→303 owner=user · redirect détail ·
trim titre · slug dérivé · **collision slug** re-render · **quota 10** → 11ᵉ refusé · titre vide →
re-render sans row · **liste owner-scopée** · détail autre user → **404** · détail absent → **même 404** ·
**archivé exclu** de la liste · **aucune review écrite** · **aucun `WorkoutTemplate` créé** · OpenAPI
expose les 4 routes.

Non-régression : `test_user_program_drafts.py` (12/12), `test_program_quality_engine/feedback/reviews`
(58/58) — inchangés.

## 7. Checks

- **check_scope = `ISOLATED`** (le garde traite `main.py`/templates comme des feuilles : rien
  n'importe l'entrypoint). Anticipé `SHARED_CODE` au préflight — documenté, non forcé. Full sweep
  local **non requis** par le tier, mais **exécuté quand même** car `app/main.py` est touché
  (« remonter d'un cran », CLAUDE.md §1).
- **ruff** : `All checks passed` sur les fichiers neufs ; **budget 544 ≤ 548** (delta −4).
- **check_spec_protocol** : PASS.
- **Full sweep local** : voir appendice (aucun modèle/migration touché ⇒ pas d'artefact d'arbre sale).
- La **CI réelle (3 jobs)** au push reste la source de vérité de non-régression globale.

## 8. Suite

- **WIZARD_02** = édition de l'arbre (cartes / `replace_draft_tree`) : séances, exercices, rep targets.
- **WIZARD_03+** = génération déterministe (spec 01 §11) et/ou branchement du scoring/feedback sur
  le flow, si décidé plus tard. Aucun n'est ouvert par ce build.

## Verdict

**Verdict :** 🟢 **Sb_CUSTOM_PROGRAM_WIZARD_01 — PATCH COMPLETE / REVIEW PENDING.**

La création d'un programme custom est enfin atteignable par l'utilisateur, par un flow SSR minimal,
owner-scopé, quota-gardé, sans générateur, sans scoring, sans publication et sans migration. Le
service de drafts a désormais sa première porte d'entrée produit.

---

## Appendice post-merge (closeout 2026-07-27)

- **Commit build** : `613b639` (10 fichiers, +658) sur `sb/custom-program-wizard-01-entry-flow`,
  base `805b8a9` — **rafraîchie en cours de route** sur le canonique `c70bdb0` (closeout ASSET 03B.1
  poussé entre-temps) via stash → FF → stash pop : **merge automatique propre** des 2 docs stratégie
  partagés (ajouts WIZARD_01 et ASSET 03B.1 coexistent, zéro conflit).
- **Fix Sonar** : `f0059d9` (`app/routers/user_programs.py` seul, +3/−1) — **2 vraies issues
  `python:S...`** remontées par SonarCloud sur la PR : `python:S8410` (MINOR, param Form → `Annotated[str, Form()]`)
  et `python:S8415` (MAJOR, documenter la réponse 404 via `responses={404: ...}`). **Corrigées sans
  changement de comportement** (19 tests dédiés inchangés). Distinct de l'artefact `new_coverage`.
- **PR #35 MERGED** — merge **`e82d3e1`** sur le canonique, via `gh pr merge --merge --admin`
  (bypass du **seul** gate en échec = `new_coverage 0.0 %`, artefact structurel non bloquant ;
  pas de squash, branche non supprimée).
- **CI PR #35** : **3 jobs GitHub verts** (pytest + QA · lint · SonarCloud) sur `f0059d9`.
- **CI canonique** : run **`30258235301`** sur `e82d3e1` → **3/3 GREEN** (pytest + QA · lint ·
  SonarCloud). Le job `lint` a passé (`success`) malgré une annotation reviewdog non bloquante
  (shellcheck SC2046 sur `.github/workflows/ci.yml`, fichier hors périmètre WIZARD_01).
- **Vérification Sonar** : `issues/search` sur la PR (contenu = `f0059d9`, identique au mergé) →
  **`total: 0`** (S8410 + S8415 résolues) ; quality gate ERROR **uniquement** sur `new_coverage`,
  ratings reliability/security/maintainability = A, duplication 0 %, hotspots 100 %.
- **Head Alembic inchangé** (zéro migration) — WIZARD_01 est un flow HTTP/SSR pur sur la
  persistance existante.
- **Statuts après closeout** : `WIZARD_02` (édition arbre/cartes via `replace_draft_tree`) =
  **FIRST NEXT / NOT OPENED** · `WIZARD_03+` (génération déterministe / scoring branché) =
  **NOT OPENED** · `SCORING_04` = **NOT OPENED** · `EKB_04` = **DEFERRED**.
- **Cleanup** : branche `sb/custom-program-wizard-01-entry-flow` (remote + locale) et worktree
  `-custom-wizard-01` **conservés** — suppression au prochain GO CLEANUP.

**Verdict post-merge :** ✅ **Sb_CUSTOM_PROGRAM_WIZARD_01 — MERGED + CANONICAL CI GREEN.**
