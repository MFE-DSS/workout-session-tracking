# SPRINT Sb_MORPHO_DOGFOOD_01 — Generated Program through the Real Custom Program Cycle (RAPPORT)

**Base canonique :** `8d9631c` · **Branche :** `sb/morpho-dogfood-01` · **Tier :** **DB_WRITE / RUNTIME_FLOW** (classé par l'opérateur ; `check_scope` disait ISOLATED — **remonté**, full sweep exécuté)
**Spec :** `Sx_MORPHO_PROGRAM_01_SPEC` (déc. 4/12 : Martin = fixture dogfood privée, version dérivée via le cycle existant) — **5ᵉ et dernier build** de la file morpho.
**Livré sous le protocole agentique + DELIVERY AUTONOMY ENVELOPE** : `GO BUILD` → autonome jusqu'à `PR GREEN / MERGE PENDING`. **Pas de merge.**

## 1. Ce qui est livré

La **preuve de bout en bout** que le programme morphologie généré traverse le **cycle Custom Program réel** — `draft → validate → quality preview → publish → séance lançable` — **sans changer une seule sémantique de cycle de vie**, et sans exposer un programme privé dans le catalogue public ou `/library`.

Deux artefacts seulement, tous deux **additifs** :
- **`app/services/morpho_program_draft_mapper.py`** (neuf, **pur**) : `GeneratedProgram` → la charge utile que `replace_draft_tree` consomme **déjà**. Aucune écriture, aucun ORM, aucune donnée Martin.
- **`tests/fixtures/dogfood/martin_program.py`** (étendu, **privé/test-only**) : identité de programme de Martin (titre/slug/focus) + `martin_draft_tree()`.

**Le cycle n'est ni contourné ni réimplémenté** : les tests appellent les services existants (`create_draft`, `replace_draft_tree`, `validate_draft`, `compute_quality_preview`, `publish_user_program`, `resolve_owned_published_template`, `start_new_edit_cycle`) et le lancement passe par la vraie route `POST /programs/{id}/sessions/{sid}/start`.

## 2. Brainstorming / Options / Risques / Choix retenu (CLAUDE.md §3)

**Préflight (obligatoire, 3 explorations parallèles)** : modèles `UserProgram`/`Session`/`Exercise`/`RepTarget` (colonnes exactes, contraintes, quotas), contrat de `replace_draft_tree`, règles de `validate_draft`, publication/freeze/versioning, préview vs writer qualité, garde d'ownership au lancement, mécanisme d'exclusion `/library`, fixtures et idiomes de test existants, pins Alembic/snapshot.

**Verdict de préflight — aucune condition d'arrêt** : le cycle existant suffit (`draft/validated/published` + `archived_at`), **0 nouvel état**, **0 nouvelle table**, **0 migration** (aucun modèle touché → les pins Alembic/snapshot restent verts), et 8 exercices en 1 séance tiennent dans les quotas (`MAX_EXERCISES_PER_SESSION=10`, min 1 séance).

| Option | Verdict |
|---|---|
| **A** — mapper **pur** `GeneratedProgram → draft tree` + pilotage par les **services existants** | ✅ **RETENU** — additif, 0 sémantique changée, testable, miroir exact du précédent `user_program_generator` |
| **B** — service d'orchestration « générer et publier » | ✗ créerait une **publication silencieuse** (interdit) et un second chemin de cycle de vie |
| **C** — nouveau modèle/table pour les programmes générés | ✗ condition d'arrêt (nouvelle table/migration) ; inutile, le modèle existant représente tout |

**Choix de structure** : **une seule séance** (« Full Body — Morphotype Priority ») portant les 8 slots — c'est la **plus petite structure valide** (`validate_draft` exige ≥ 1 séance, ≥ 1 exercice/séance, ≥ 1 rep_target/exercice). Aucun PPL inventé. Le mapper ne scinde en séances supplémentaires que si le générateur dépassait un jour le quota par séance.

**Choix des volumes** : le moteur morpho **ne prescrit aucun volume** (`SlotSelection` porte un exercice et une intention, jamais de séries/reps). Conformément à la spec (« from existing morphotype program or deterministic defaults »), chaque intention hérite du volume de **son homologue E1-E8 du programme catalogue mergé** (latéraux `4x 12-20` = priorité n°1, quadriceps `2x 6-10` = dose minimale…), table déclarée dans le mapper et **pinnée par test contre `reference_split.json`**. Repli `3x 8-12` (convention du repo) pour une intention inconnue.

**Risques traités** :
1. **Publication silencieuse** → le mapper ne publie rien ; publication uniquement par appel explicite du service, et le test `test_draft_publication_is_still_refused` prouve qu'un draft généré **n'échappe pas** à la validation. *Testé.*
2. **Écriture pendant la préview qualité** → `compute_quality_preview` est pur ; test comptant les lignes `UserProgramQualityReview` **avant/après** (inchangé). *Testé.*
3. **Fuite dans `/library` / le catalogue** → publication en `catalog_section="user"` (mécanisme existant) ; tests : liste `/library` sans le programme, détail par slug **404**, et **compte de templates non-`user` inchangé** après publication. *Testé.*
4. **Perte d'identité/ordre d'exercice** → tests d'égalité stricte nom+position draft↔généré, puis template publié↔généré. *Testé.*
5. **Fabrication d'exercice** → `exercise_name` est NOT NULL ; les slots sans exercice sont **abandonnés et signalés** (`unmappable_slots`), jamais inventés. *Testé sur un cas de starvation.*
6. **Données Martin hors fixture** → test asserting qu'aucune **valeur d'identité** (titre/slug/focus/source) n'apparaît dans le code livré. *Testé.*
7. **Régression versioning** → `start_new_edit_cycle` → v2, liens gelés annulés, republication → slugs `-v2-s1`. *Testé.*

## 3. Fichiers touchés (2 + docs)

| Fichier | Changement |
|---|---|
| `app/services/morpho_program_draft_mapper.py` (**neuf, pur**) | `generated_program_to_draft_tree` · `mapped_selections` · `unmappable_slots` · `_INTENT_PRESCRIPTION` (volumes E1-E8) · `SOURCE_REASON_PREFIX = "generated:morpho"` |
| `tests/fixtures/dogfood/martin_program.py` (**privé, étendu**) | `MARTIN_PROGRAM_TITLE` / `MARTIN_PROGRAM_SLUG` / `MARTIN_SESSION_FOCUS` / `martin_draft_tree()` |
| `tests/test_morpho_dogfood.py` (**neuf**) | 24 tests |
| docs | ce rapport + registry + roadmap |
| **modèles / migrations / publication / launch / session_builder / substitution / générateur morpho / catalogue / EKB** | **aucun** |

## 4. Preuve de cycle de vie (dogfood)

`mpg1-eadcab6e2d104c45` → **1 séance / 8 exercices distincts**, ordre de slot préservé, chaque exercice portant `source_reason = generated:morpho:{intent_id}` et le `rationale` de l'intention en `notes` :

| Pos | Exercice | Volume | Intention |
|---|---|---|---|
| 1 | Élévations latérales câble | 4x 12-20 | `lateral_delt_priority` |
| 2 | Chest Press machine | 3x 6-10 | `upper_chest_primary_press` |
| 3 | Face pull câble | 3x 12-20 | `rear_delt_upper_back_accessory` |
| 4 | Mollets assis machine | 4x 8-12 | `calves_gastrocnemius_priority` |
| 5 | Calf press leg press | 3x 12-20 | `calves_soleus_priority` |
| 6 | Rowing chest-supported | 3x 8-12 | `upper_back_depth_row` |
| 7 | Leg extension câble unilatéral | 2x 6-10 | `quad_minimum_effective_dose` |
| 8 | Back extension 45° (bias ischios) | 2x 6-10 | `posterior_chain_hinge` |

Traversée vérifiée : draft (8 exercices) → `validated` → préview qualité (**0 écriture**) → `published` (1 séance → **1 template `user`**, codes `E1..E8`, `published_template_id` + `template_slug_snapshot` gelés, **exactement 1** trace qualité) → **lancement propriétaire 303** vers `/sessions/{id}` → **non-propriétaire refusé** → `/library` **n'expose rien** → nouveau cycle v2 + republication **inchangés**.

## 5. Limites connues du dogfood (constats honnêtes, hors périmètre)

1. **Gastrocnémien / soléaire inversés mécaniquement.** Le slot gastrocnémien reçoit « Mollets assis machine » (assis, genoux fléchis = biais soléaire) et le slot soléaire « Calf press leg press ». Cause : la taxonomie `muscle_group` n'a qu'une valeur `calves` — le couplage maximum ne peut pas distinguer les deux mécaniques. **Non corrigé ici** : cela exigerait un changement de comportement du générateur (condition d'arrêt explicite de la mission). **Correctif recommandé** : affiner la taxonomie (`calves_gastrocnemius` / `calves_soleus`) dans un build dédié, sur GO.
2. **Le temps de repos n'est pas représentable.** La couche draft (`UserProgramExercise`) **n'a aucun champ `rest`** — pas plus que le catalogue. Le repos de la mission est donc **omis, pas inventé**.
3. `archive_draft` positionne `archived_at` sans écrire `status="archived"` (comportement **préexistant**, documenté en `PUBLICATION_04`) : tout consommateur doit tester `archived_at`. Le dogfood n'archive pas et ne s'y appuie pas.

## 6. Interdits tenus

**0 nouvel état de cycle de vie** · **0 nouvelle table / migration / colonne** (pins Alembic + snapshot verts sans intervention) · **0 exposition catalogue global** · **0 exposition `/library`** · **0 `WorkoutTemplate.user_id`** · **0 expansion EKB** · **0 modif `substitution.py`** · **0 changement de comportement du générateur morpho** · **0 publication silencieuse** · **0 réécriture `session_builder`** · **0 donnée Martin de production** · **0 photo / donnée corporelle sensible** · **0 revendication médicale** · **0 refonte UI**.

## 7. Validation

check_scope **ISOLATED** (**traité DB_WRITE/RUNTIME_FLOW**, full sweep exécuté) · `check_spec_protocol` PASS · `check_ruff_budget` **543 ≤ 548** · `ruff` clean · **24 tests dédiés** · **full sweep parallélisé 2959 passés, 0 échec**.

**Incident local capté par le full sweep (corrigé in-scope).** Trois tests purs ont d'abord échoué **sous xdist uniquement**, en
`ModuleNotFoundError: No module named 'app.services.morpho_program_draft_mapper'`. Cause : ils faisaient un import
`app.*` **local à la fonction** sans utiliser la fixture `client` — or `conftest.client` **purge tous les modules `app.*`
de `sys.modules`** ; après qu'un test `client` du même worker a purgé, un ré-import local d'un module **neuf** échoue
(dépendant de l'ordre, donc invisible en séquentiel et en exécution isolée). **Correctif** : hisser les imports des
modules **purs** au niveau module — convention déjà suivie par les fichiers de tests purs voisins (`test_slot_intent`,
`test_morpho_program_generator`, `test_martin_program`) ; les services DB/cycle **restent** en import local, car ils
*doivent* être ré-importés après purge. Bénéfice annexe : **identité de module unique** partagée avec la fixture (plus
de risque de double instance de `SlotSelection`). *Le sur-check de tier a de nouveau payé : `check_scope` annonçait
ISOLATED.*

## Verdict

**Verdict :** ✅ **Sb_MORPHO_DOGFOOD_01 — MERGED + CANONICAL CI GREEN.** Le programme morphologie généré **entre dans le cycle Custom réel** par les services existants, reste **privé** (aucune exposition catalogue/`/library`), préserve **identité et ordre** des 8 exercices, et **ne change aucune sémantique** de validation/publication/versioning/lancement. **Dernier build de la file `Sx_MORPHO_PROGRAM_01`.**

---

## Appendice post-merge (closeout)

- **Merge** : PR **#68 MERGED** 2026-08-10, build `4d5ee02`, merge commit **`84d54e6`** via
  `--merge --match-head-commit 4d5ee02` — **sans squash, sans `--admin`** (gate `CLEAN`,
  `MERGEABLE`, **0 thread**, head épinglé).
- **CI canonique** : run **`31397026757`** (`push`) **3/3 GREEN** sur `84d54e6`
  (lint · pytest + QA · SonarCloud).
- **Sonar** : gate PR **OK** (`new_coverage` **96.9 %**, 0 smell/bug/vuln/duplication) ;
  `app/services/morpho_program_draft_mapper.py` = **0 issue** sur main ; coverage main **91.5 %**.
- **Aucun thread de revue** sur la PR.
- **File `Sx_MORPHO_PROGRAM_01` : COMPLÈTE** — spec + profil + slot intent + générateur + programme
  Martin + couverture du pool + dogfood du cycle réel, tous mergés avec CI canonique verte.
- **Suites identifiées (sur GO, non ouvertes)** : affiner la taxonomie mollets
  (`calves_gastrocnemius` / `calves_soleus`) pour lever l'inversion mécanique documentée en §5 ;
  la représentation du temps de repos reste hors modèle.
- **Cleanup** : branche `sb/morpho-dogfood-01` + worktree `workout-session-tracking-morpho-dogfood`
  supprimés au closeout (cleanup explicitement inclus par l'opérateur).
