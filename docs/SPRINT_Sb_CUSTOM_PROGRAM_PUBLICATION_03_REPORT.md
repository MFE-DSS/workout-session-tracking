# SPRINT Sb_CUSTOM_PROGRAM_PUBLICATION_03 — Accès & lancement des séances publiées (RAPPORT)

**Base canonique :** `c606448` · **Branche :** `sb/custom-program-publication-03` · **Tier :** SHARED_CODE (**zéro migration**)
**Spec :** [`Sb_CUSTOM_PROGRAM_PUBLICATION_03_SPEC.md`](strategy/Sb_CUSTOM_PROGRAM_PUBLICATION_03_SPEC.md)
**Livré sous le protocole agentique** (`CLAUDE.md §4`) : `GO BUILD` → autonome jusqu'à `PR GREEN / MERGE PENDING`.

## 1. Ce qui change

Le propriétaire peut enfin **accéder à ses séances publiées et les lancer** depuis l'UI de son programme possédé. PUBLICATION_01 les matérialisait en `WorkoutTemplate` `catalog_section="user"` **exclus du catalogue global** — elles existaient donc sans porte de lancement. Ici : un CTA **« Démarrer cette séance »** par séance publiée + une route `POST /programs/{id}/sessions/{sid}/start`, et une **garde de propriété** ajoutée au chemin `create_session` par slug. Le catalogue global `/library` **continue d'exclure** les templates `user`.

## 2. Brainstorming / Options / Risques / Choix retenu (CLAUDE.md §3)

**Préflight = pas de conflit.** `Sx_CUSTOM_PROGRAM_05 §14` décrit exactement le modèle demandé : accès **propriétaire uniquement**, résolu par `UserProgram (owner) → UserProgramSession → published_template_id`, sans `WorkoutTemplate.user_id`, `/library` inchangé. Build direct.

| Option | Verdict |
|---|---|
| **A** — lancement via le **contexte programme possédé** (route dédiée `/programs/{id}/sessions/{sid}/start`) + garde de propriété sur le chemin slug existant | ✅ **RETENU** — respecte spec §14 (propriété côté programme), zéro migration, zéro `user_id`, `session_builder` réutilisé |
| **B** — exposer les templates `user` dans `/library` filtrés par propriétaire | ✗ affaiblit la garde d'exclusion `/library` (interdit explicite) ; mélange catalogue partagé et artefacts privés |
| **C** — ajouter `WorkoutTemplate.user_id` pour porter la propriété côté template | ✗ interdit explicite + migration + duplique une propriété qui vit déjà côté programme |

**Risques traités** :
1. **Fuite cross-utilisateur par slug** — *défaut préexistant découvert*. `POST /sessions` résolvait un template par slug **sans garde de propriété** : un template `user` d'autrui, bien qu'exclu du listing, restait **joignable par slug**. → Garde ajoutée (`is_owned_published_template`) : template `user` non possédé → 404 ; **système inchangé**. *Testé (#owned/#foreign/#system).*
2. **Programme archivé lançable** — l'archivage (soft-delete, spec 04 §8) pose `archived_at` mais **laisse `status='published'`** et **ne coupe pas** `published_template_id`. Un garde sur `status` seul aurait laissé un programme soft-supprimé lançable (UI **et** POST direct). → `archived_at IS NULL` porté par **les deux requêtes du service ET le CTA**. *Testé (CTA + POST 404 archivé).*
3. **Mutation d'artefact** — le service est **READ-ONLY** : aucune `WorkoutTemplate` ni `UserProgram` (statut/`current_version`) mutée ; seule une `WorkoutSession` est créée. *Testé (#nomutate).*
4. **Fuite d'existence** — absent / foreign / non-publié / archivé renvoient le **même 404** indistinct.

## 3. Fichiers touchés (4 + docs)

| Fichier | Changement |
|---|---|
| `app/services/user_program_launch.py` (**neuf**) | `resolve_owned_published_template` (eager-load), `is_owned_published_template` (reverse-lookup), `LaunchNotFound` ; les deux requêtes exigent `archived_at IS NULL` ; **zéro mutation** |
| `app/routers/user_programs.py` | imports + `POST /programs/{id}/sessions/{sid}/start` → `resolve_owned_published_template` → `instantiate_session` → 303 (`LaunchNotFound` → 404) |
| `app/routers/sessions.py` | `create_session` : `responses={404}` + garde propriété pour `catalog_section="user"` (`is_owned_published_template`) ; système inchangé |
| `app/templates/user_programs/detail.html` | CTA « Démarrer cette séance » par séance **ssi** `status=published` **et** non archivé **et** `session.published_template_id` |
| `tests/test_user_program_launch.py` (**neuf**) | 15 tests (service + HTTP) |
| docs | spec + rapport + registry/roadmap |

## 4. Interdits tenus

Aucune exposition catalogue globale · aucun partage/public · aucun navigateur d'historique de versions · **aucune nouvelle table** · **aucun `WorkoutTemplate.user_id`** · **aucune migration** (head Alembic inchangé) · **aucune réécriture de `session_builder`** (instanciation existante réutilisée) · aucune refonte du cycle PUBLICATION_01/02 · zéro EKB/ASSET/BodyMap · **aucun affaiblissement des gardes d'exclusion `/library`** (listing + `/library/{slug}` → 404 revérifiés).

## 5. Tests

`tests/test_user_program_launch.py` — **15 passés** :
- **Service** : résolution possédée+publiée OK (eager-load) · foreign & séance manquante → `LaunchNotFound` · brouillon non publié → `LaunchNotFound` · reverse-lookup possédé vrai / foreign faux.
- **HTTP CTA** : publié affiche le CTA · draft/validated/archivé ne l'affichent pas (+ POST start archivé → 404).
- **HTTP start** : le propriétaire démarre une séance publiée (303 + une `WorkoutSession` créée) · foreign & séance manquante → 404 · non-authentifié → `/login` · lancement ne mute ni template ni programme.
- **create_session** : template `user` possédé OK · template `user` foreign → 404 · template **système** inchangé (303).
- **/library** : exclut les templates `user` (listing) · `/library/{user_slug}` → 404.

**Broad sweep ciblé** (session_* + user_program* + library* + catalog* = 46 fichiers) : **673 passés**.

## 6. Validation

check_scope **SHARED_CODE** · `check_spec_protocol` PASS · `check_ruff_budget` **543 ≤ 548** · `ruff check` fichiers touchés **clean** (le `C901` sur `session_detail` est **préexistant** — fonction non touchée par ce sprint). Full sweep local non systématique (SHARED_CODE) — la CI PR parallélisée est le filet de vérité du blast radius.

## Verdict

**Verdict :** ✅ **Sb_CUSTOM_PROGRAM_PUBLICATION_03 — MERGED + CANONICAL CI GREEN.** Le propriétaire accède & lance ses séances publiées **par le contexte programme possédé** ; garde de propriété ajoutée au chemin slug (**fermeture d'un défaut cross-utilisateur préexistant**) ; archivé non lançable ; **zéro migration / table / `user_id` / réécriture `session_builder`** ; `/library` inchangé.

---

## Appendice post-merge (closeout)

- **Merge** : PR **#56 MERGED** 2026-08-08, build `56f206f` + fix Gitar `ac454b9`, merge commit **`bc0f68f`** sur `claude/sprint-reporting-fitness-app-V7Qr6` via `--merge --match-head-commit ac454b9` — **sans squash, sans `--admin`** (gate `CLEAN`, **0 thread non résolu**). `GO BUILD` → autonome jusqu'à PR GREEN ; `GO MERGE` → merge + closeout (protocole `CLAUDE.md §4`).
- **CI PR #56** : 5 checks verts (lint · pytest+QA · Gitar · SonarCloud · SonarCloud Code Analysis).
- **CI canonique** : run **`31256743949`** 3/3 GREEN sur `bc0f68f` — `pytest + QA scripts` (dont drift Alembic · schema snapshot · migration patterns/roundtrip · perf budget), `lint`, `SonarCloud`.
- **Sonar** : gate PR **OK**, delta `total: 0`, `new_coverage` **97.1 %** (524 lignes neuves), `new_violations` **0** ; fichiers neufs `app/services/user_program_launch.py` + `tests/test_user_program_launch.py` = **0 issue** sur main.
- **Thread Gitar** (qualité) : `db.add(session)` redondant dans la route de lancement (`instantiate_session` stage déjà, `create_session` idem) → **vérifié réel, corrigé in-scope** (`ac454b9`), comportement inchangé (15/15 tests reverts verts), thread **auto-résolu**.
- **Gate main-branch = ERROR préexistant** : dette repo accumulée (période *new code* `previous_version` depuis 2026-04-10) — 20 bugs / 6 vulns / 724 code smells au total ; **PUBLICATION_03 y contribue 0** (prouvé par le gate PR delta 0 + 0 issue sur les fichiers neufs). La **CI canonique 3/3** reste la source de vérité de non-régression (`CLAUDE.md §2`).
- **Nettoyage branche/worktree** : `sb/custom-program-publication-03` + worktree `workout-session-tracking-publication-03` **conservés** — suppression = **GO humain séparé** (jamais en autonomie, `CLAUDE.md §4`).
