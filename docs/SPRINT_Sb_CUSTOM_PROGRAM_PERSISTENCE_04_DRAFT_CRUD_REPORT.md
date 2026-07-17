# Sprint Sb_CUSTOM_PROGRAM_PERSISTENCE_04 — Draft CRUD Repository Service — BUILD

**Statut** : 🟢 **PATCH COMPLETE / REVIEW PENDING** (non commité, non poussé, CI non lancée)
**Type** : CODE BUILD — **premier build de service** du track (changement de nature : zéro migration)
**Date** : 2026-07-17
**Specs** : `Sx_CUSTOM_PROGRAM_04` §6/§8 (statuts, ownership, soft delete) + `03` §10 + `05` (frontières)
**Branche** : `sb/custom-program-persistence-04-draft-crud` (worktree dédié, base `007c428` — origin, le canonique local divergé du repo principal a été évité)
**Préflight** : ✅ GO PATCH validé (patron services CRUD de domaine relevé : commit interne, exception de domaine)

---

## 0. Étape 0 — Brainstorming / Options / Risques / Choix retenu

| Décision | Choix |
|---|---|
| Forme | module service fonctionnel `app/services/user_program_drafts.py` (convention repo — pas de classe repository) + `UserProgramDraftError` |
| Transactions | **commit interne aux mutations** (patron squad/challenge/readiness, 16 précédents) ; lectures pures ; rollback + erreur lisible sur IntegrityError |
| « Delete » | **= archive (soft)** ; aucun hard delete exposé (OQ-PERS-A réservée) ; ré-archivage → refus explicite |
| Édition d'arbre | **remplacement complet** (`replace_draft_tree`) — le geste V1 de wizard/cartes ; s'appuie sur delete-orphan |
| Statuts | éditable = `draft`/`validated` ; `validated` édité → repasse `draft` (spec 04 §6) ; `published`/`archived` → refus (le nouveau cycle = ère publication) |
| Ownership | `user_id` requis partout ; inexistant et non-possédé **indistinguables** (zéro fuite d'existence) |
| Quotas | **non appliqués** — `PERSISTENCE_05` (hardening), documenté |

## 1. Patch appliqué

| Fichier | Nature |
|---|---|
| `app/services/user_program_drafts.py` | **nouveau** (~210 l.) — 6 fonctions : `create_draft` / `get_draft` (arbre eager) / `list_drafts` / `rename_draft` / `replace_draft_tree` / `archive_draft` ; frontières dures documentées en tête de module |
| `tests/test_user_program_drafts.py` | **nouveau** — 12 tests |

**Aucune migration, aucun modèle modifié, aucun snapshot, aucun endpoint/UI.**

## 2. Incident de build (résolu, documenté honnêtement)

Premier run : 11/12 — `test_replace_tree_purges_old_children` rouge sur **UNIQUE
(program, position)** : l'unit of work SQLAlchemy émettait les INSERT des nouvelles séances
avant les DELETE des anciennes. **Fix minimal** : `sessions.clear()` + `db.flush()` avant
d'attacher le nouvel arbre (les deletes atteignent la DB d'abord), commenté dans le code.
Re-run : **12/12**.

## 3. Tests exécutés

| Suite | Résultat |
|---|---|
| Dédiés (`test_user_program_drafts.py`) | **12/12** (après le fix ci-dessus) |
| Adjacents/sentinelles (3 schémas UserProgram + wipe-guard + ownership + auth_scope_isolation) | **67/67** |
| **Broad sweep ciblé** (`user_program or ownership or auth or seed or schema or migration`) | **192 passed / 0 échec** (1:50) |
| ruff (2 fichiers neufs) | clean |
| `check_ruff_budget` | **543 ≤ 548** |
| `check_spec_protocol` | PASS |
| `check_scope` | **ISOLATED** (service leaf, non importé par l'app) — conforme au préflight ; **pas de full sweep local requis à ce tier** (contrat anti-overcheck) ; CI complète via PR = source de vérité |

Couverture notable : cross-user sur les 3 mutations → « introuvable » (même erreur que
l'inexistant) · purge d'orphelins vérifiée par comptages exacts · positions séquentielles
validées · soft delete prouvé (row conservée) · `validated` → `draft` à l'édition ·
`published`/`archivé` verrouillés.

## 4. Risques résiduels

Service non branché (aucun consommateur avant wizard — pattern fondation) · quotas absents
(volontaire, `PERSISTENCE_05`) · vocabulaire de statut non contraint en DB (inchangé).

## 5. Confirmations de périmètre

✅ **Aucune migration** (head inchangé `n5o0i6j7l98`) · ✅ aucun endpoint/UI/wizard/scoring/
EKB/publication · ✅ `session_builder`/seed/catalogue/modèles intacts · ✅ chantier UI et
branche spec non touchés.

---

## Verdict

**Verdict :** 🟢 **Sb_CUSTOM_PROGRAM_PERSISTENCE_04 — PATCH COMPLETE / REVIEW PENDING.**

Le premier service du track existe : CRUD de brouillon owner-scoped, sans fuite d'existence,
soft-delete-only, règles de statut de la spec 04 appliquées, remplacement d'arbre robuste
(purge prouvée). 12 dédiés + 67 sentinelles + 192 broad sweep verts. Prochaines étapes :
GO COMMIT → PR (CI 3/3) → merge sur GO. **`PERSISTENCE_05` (QA/quotas hardening) et le reste
de la queue restent NOT AUTHORIZED.**
