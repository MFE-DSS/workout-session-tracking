# Sprint Sb_CUSTOM_PROGRAM_PERSISTENCE_05 — QA/Quotas Hardening — BUILD

**Statut** : 🟢 **PATCH COMPLETE / REVIEW PENDING** (non commité, non poussé, CI non lancée)
**Type** : CODE BUILD — hardening du service de brouillon (**zéro migration** : le modèle est
touché mais **aucun changement de schéma**, prouvé par les 4 checks QA)
**Date** : 2026-07-18
**Specs** : `Sx_CUSTOM_PROGRAM_04` §6 (transition `draft → validated`) + §9 (quotas V1) +
`Sx_CUSTOM_PROGRAM_03` §9-C (invariance des traces de scoring)
**Branche** : `sb/custom-program-persistence-05-hardening` (worktree dédié, base `a1fe5a6` — origin canonique post-closeout 03+04)
**Préflight** : ✅ GO PATCH validé (tier MIGRATION accepté d'avance : `app/models/` touché
sans colonne — les checks QA font foi)

---

## 0. Étape 0 — Brainstorming / Options / Risques / Choix retenu

| Décision | Options considérées | Choix retenu |
|---|---|---|
| Support des quotas | constantes applicatives versionnées · config DB · table settings | **Constantes versionnées** dans le service (spec 04 §9) — un quota V1 est une règle produit, pas une donnée ; changement = commit review-able |
| Quota « versions publiées » (5) | l'appliquer dès maintenant · le différer | **Différé à l'ère publication** — il n'a de sens qu'au moment de publier ; l'appliquer ici serait du code mort non testable |
| Comptage des actifs | `len(list_drafts(...))` · `COUNT` SQL owner-scoped | **`COUNT` SQL** (`archived_at IS NULL`) — pas de chargement d'objets pour un garde-fou |
| Transition `validated` | flag sur `rename`/`replace` · fonction dédiée | **`validate_draft` dédiée et idempotente** — c'est le geste « récap accepté » du futur wizard ; complétude **minimale** (≥1 séance, ≥1 exercice/séance, ≥1 plage/exercice), pas de pseudo-scoring (le sens = `SCORING_01+`) |
| Invariance des reviews | trigger SQL · listener SQLAlchemy `before_update` | **Listener applicatif** — zéro changement de schéma (un trigger = migration, refusé) ; l'unique `(program, version)` bloque déjà les doublons, le listener ferme la mutation in-place |
| Ton des messages | — | **Doux et actionnables, jamais culpabilisants** (« en archiver un libère une place ») — contrat produit du track |

Risque principal identifié au préflight : toucher `app/models/user_program.py` classe le
diff en tier MIGRATION alors que le build est zéro-schéma. Accepté : les 4 checks QA
migration servent précisément de preuve d'invariance.

## 1. Patch appliqué

| Fichier | Nature |
|---|---|
| `app/services/user_program_drafts.py` | **modifié** — 3 constantes de quota (`MAX_ACTIVE_PROGRAMS = 10`, `MAX_SESSIONS_PER_PROGRAM = 7`, `MAX_EXERCISES_PER_SESSION = 10`) ; quota actifs dans `create_draft` (COUNT owner-scoped) ; quotas séances/exercices dans `replace_draft_tree` ; nouvelle fonction `validate_draft` (idempotente, owner-scoped sans fuite d'existence, complétude minimale) ; import `func` ; docstring de module mise à jour |
| `app/models/user_program.py` | **modifié** — listener `before_update` sur `UserProgramQualityReview` (ValueError « immuable ») ; import `event`. **Aucune colonne, aucun index, aucune contrainte — zéro schéma** |
| `tests/test_user_program_hardening.py` | **nouveau** — **13 tests** |

**Aucune migration (head inchangé `n5o0i6j7l98`), aucun snapshot régénéré, aucun endpoint/UI/wizard/scoring/EKB.**

## 2. Tests et checks exécutés

| Suite / check | Résultat |
|---|---|
| Dédiés (`test_user_program_hardening.py`) | **13/13 premier coup** |
| Sentinelles track (drafts 12 + 3 schémas 29 + wipe-guard 10) | **51/51** → total run **64/64** |
| ruff (3 fichiers touchés) | clean |
| `check_ruff_budget` | **543 ≤ 548** |
| `check_spec_protocol` | PASS |
| `check_alembic_drift` (`python -m`) | **OK (no diff)** — le listener n'induit aucun drift |
| `check_schema_snapshot` (`python -m`) | **OK** — snapshot conforme au head `n5o0i6j7l98`, non régénéré |
| `check_migration_patterns` (`python -m`) | OK |
| `check_migration_roundtrip` (`python -m`) | OK |
| `check_scope` | **MIGRATION** (attendu : modèle touché) — battery complète exécutée en conséquence |
| **Full sweep local** | **2351 passed / 1 failed (13:45)** — l'unique échec = `test_no_model_migration_schema_touched`, le garde-fou arbre-sale (`git diff HEAD`) qui fire par design sur le modèle non commité ; **prouvé vert post-commit** (voir appendice) — même artefact que `PERSISTENCE_02` |

Couverture notable : bornes exactes des 3 quotas (10ᵉ programme OK / 11ᵉ refusé ; 7 séances
OK / 8 refusées ; 10 exercices OK / 11 refusés) · message doux vérifié (« libère une place ») ·
l'archivage libère une place · quota par user (l'autre user n'est pas bloqué) ·
`validate_draft` : transition, refus programme vide / séance sans exercice / exercice sans
plage, idempotence, `published`/archivé verrouillés, cross-user → « introuvable » ·
INSERT d'une review permis, UPDATE in-place → ValueError, la row d'origine prouvée intacte.

## 3. Risques résiduels

Service toujours non branché (consommateur = wizard futur — pattern fondation) · vocabulaire
de statut non contraint en DB (inchangé, connu) · l'invariance des reviews est **applicative**
(un UPDATE SQL brut la contournerait — hors surface de l'app, et la doctrine additive-only
interdit le trigger qui la rendrait absolue) · quota « versions publiées » (5) différé à
l'ère publication, documenté dans le service.

## 4. Confirmations de périmètre

✅ **Zéro migration** (head `n5o0i6j7l98` inchangé, snapshot intact) · ✅ aucun endpoint/UI/
wizard/scoring/EKB/publication · ✅ `session_builder`/seed/catalogue intacts · ✅ chantier UI
et branche spec non touchés · ✅ messages produit doux, jamais culpabilisants.

---

## Verdict

**Verdict :** 🟢 **Sb_CUSTOM_PROGRAM_PERSISTENCE_05 — PATCH COMPLETE / REVIEW PENDING.**

Le service de brouillon est durci : les 3 quotas V1 de la spec 04 §9 sont appliqués aux
bornes exactes avec des messages doux, la transition `draft → validated` existe (complétude
minimale, idempotente, sans fuite d'existence), et les traces de scoring gelées sont
immuables au niveau applicatif — le tout **sans toucher au schéma** (prouvé par les 4 checks
QA). 13 dédiés + 51 sentinelles verts premier coup. Prochaines étapes : GO COMMIT → PR
(CI 3/3) → merge sur GO. **`EKB_01`/`SCORING_01` et le reste de la queue restent NOT
AUTHORIZED.**
