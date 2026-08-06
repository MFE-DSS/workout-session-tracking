# SPRINT Sb_CUSTOM_PROGRAM_PUBLICATION_01 — Publication N-templates (RAPPORT)

**Base canonique :** `83a7d58` · **Branche :** `sb/custom-program-publication-01`
**Tier :** MIGRATION · **Révision Alembic :** `p7q2k8l9n10` (down `o6p1j7k8m09`)
**Spec :** [`Sb_CUSTOM_PROGRAM_PUBLICATION_01_SPEC.md`](strategy/Sb_CUSTOM_PROGRAM_PUBLICATION_01_SPEC.md)
**Statut :** 🟡 **PATCH COMPLETE / REVIEW PENDING** (aucun commit — PATCH ONLY)

---

## 1. Brainstorming / Options / Risques / Choix retenu (CLAUDE.md §3)

**Conflit initial tranché par l'opérateur.** Le préflight recommandait un
template unique aplati ; la relecture de `Sx_CUSTOM_PROGRAM_05 §6` (citée dans le
docstring de `UserProgramSession`) l'a **invalidé** : la spec versionnée impose
**un `WorkoutTemplate` par séance** (N par programme), slug
`up{uid}-{base}-v{n}-s{position}`, lien côté `UserProgram*`.

| Option | Mécanisme | Verdict |
|---|---|---|
| **A-minimal** — N templates, un par séance ; lien `published_template_id`+`template_slug_snapshot` **sur la séance** | conforme spec 05 §6, migration additive côté enfant | ✅ **RETENU (décision opérateur)** |
| B — amender la spec vers un template aplati | contredit un contrat versionné ; nécessite un amendement docs | ✗ écarté |
| C — restreindre au mono-séance | conforme mais ampute la fonctionnalité | ✗ écarté |

**Risques identifiés & traités :**
1. `compute_and_store_quality_review` **refuse un statut non-scorable** → gel de
   qualité appelé **avant** le passage `published` (pendant `validated`), puis
   re-load de l'arbre (le writer commit et expire la session). *Testé (#11).*
2. Slug > 64 → **troncature déterministe** du seul `slug_base`. *Testé (#8, unit + intégration).*
3. Collision de slug → contrainte d'unicité + `IntegrityError` capturé en **refus
   doux**, jamais un 500 ni un template écrasé. *Limite assumée (spec §7).*
4. FK sur SQLite → `batch_alter_table` (pattern éprouvé `36be39e26189`), scanné
   propre par `check_migration_patterns` (drops uniquement en `downgrade`).

## 2. Fichiers touchés

**Ajoutés (5)**

| Fichier | Rôle |
|---|---|
| `migrations/versions/20260806_add_user_program_session_publication_links.py` | migration additive (2 colonnes + FK + index) |
| `app/services/user_program_publish.py` | matérialiseur `publish_user_program` |
| `app/templates/user_programs/publish.html` | page SSR de confirmation/état |
| `tests/test_user_program_publish.py` | 17 tests service (couvre les 20 points) |
| `tests/test_user_programs_publish_http.py` | 12 tests HTTP |

**Modifiés (5)**

| Fichier | Changement |
|---|---|
| `app/models/user_program.py` | `UserProgramSession` : `published_template_id` + `template_slug_snapshot` |
| `data/schema_snapshot.sql` | régénéré (colonnes + FK + index) |
| `app/routers/user_programs.py` | import service + GET/POST `/publish` + helper de rendu |
| `app/templates/user_programs/detail.html` | CTA « Publier » (validated) / « Voir la publication » (published) |
| `app/routers/pages.py` | `/library` exclut `catalog_section="user"` (listing + `/library/{slug}` → 404) |

**Tests-gardiens mis à jour (2) — ⚠️ hors liste autorisée, nécessités par la migration mandée :**

| Fichier | Pourquoi la migration le déclenche |
|---|---|
| `tests/test_user_program_children_schema.py` | épinglait le **jeu exact de colonnes** de `user_program_sessions` **et** « zéro FK vers le catalogue » — les 2 colonnes + la FK `published_template_id`→`workout_templates` (décision HARD du mandat, spec 05 §6) invalident les deux assertions. Mise à jour : jeu de colonnes étendu + FK de publication explicitement whitelistée (le reste de l'invariant « zéro FK catalogue/EKB » reste strict). |
| `tests/test_exercise_knowledge_base.py` | `test_alembic_head_unchanged` est une **sentinelle qui suit le head courant** (son commentaire le dit). Nouveau head `p7q2k8l9n10` → assertion mise à jour. Échoue en CI sinon. |

Ces deux mises à jour ne changent aucune logique produit : elles **rendent des tests
de schéma fidèles au schéma approuvé**. Signalées explicitement car hors de la liste
de fichiers du mandat.

**Non touchés** (interdits tenus) : `session_builder.py` · `seed.py` (hors tests) ·
générateur/drafts · moteur de qualité · EKB (JSON/EKB_04) · ASSET/BodyMap ·
`SPEC_REGISTRY.md`/`ROADMAP` (hors liste autorisée — reportés au closeout) ·
`tests/test_worked_area_descriptor.py` (voir §6bis).

## 3. Schéma (résumé)

`user_program_sessions` gagne :
- `published_template_id INTEGER NULL` — FK `workout_templates.id` `ON DELETE SET NULL`, index `ix_user_program_sessions_published_template_id` ;
- `template_slug_snapshot VARCHAR(64) NULL`.

Additive-only, aucun backfill, downgrade symétrique. **Zéro** colonne sur
`user_programs`, **zéro** `WorkoutTemplate.user_id`, **zéro** nouvelle table.

## 4. Comportement service (`publish_user_program`)

Owner-scope → refus doux (draft/archived) → idempotence (published renvoie
l'existant) → sinon (`validated`) : gel de qualité (1×, encore scorable) → re-load
→ N templates `catalog_section="user"` (slug tronqué, codes `E1..En`, séries de
travail ré-indexées) → lien posé sur chaque séance → `status="published"` →
commit (collision = refus doux). Jamais de mutation d'un template système.

## 5. Comportement router/template

- `GET /publish` : page SSR (nb séances, slugs futurs/figés, avertissement
  d'immutabilité). `POST /publish` : succès 200 (état publié ré-affiché).
- Refus doux (draft/archived/collision) → 200 + message ; foreign/absent → 404.
- CTA détail visible **uniquement** en `validated`.
- `/library` : `user` rejoint `archived` dans le skip du listing ; `/library/{slug}`
  d'une template `user` → 404.

## 6. Tests

- `test_user_program_publish.py` — **17 passés** (N templates, lien+snapshot,
  `catalog_section`, slug, troncature, `E1..En`, copie exos/séries, qualité 1×,
  refus draft/archived, idempotence, foreign/absent 404, survie reseed,
  `session_builder` inchangé, colonne côté séance, EKB non mutée).
- `test_user_programs_publish_http.py` — **12 passés** (auth, GET résumé,
  owner-scope 404, POST validated, refus doux draft/archived, idempotence,
  foreign 404, CTA détail, `/library` exclusion listing + détail 404).
- **Régression ciblée** — generate/editor/quality_preview/quality_reviews/
  session_builder : **110 passés** ; seed_wipe_guard/library/catalog : **63 passés**.

## 6bis. Un faux-échec assumé : `test_no_model_migration_schema_touched`

`tests/test_worked_area_descriptor.py::test_no_model_migration_schema_touched`
échoue **en local uniquement**. Il asserte que **`git diff --name-only HEAD`**
(donc les changements **non commités** du working-tree) ne touche ni `app/models/`
ni `migrations/` ni `data/schema_snapshot.sql`. En mode **PATCH ONLY** (mandat : ne
pas committer), mon diff non commité les touche → l'assertion casse.

Ce n'est **pas une régression de code** : dès que le patch est commité, `git diff HEAD`
redevient vide et le test repasse vert (la CI, qui tourne sur du code commité, le
verra vert). Il est donc **laissé inchangé** (c'est un garde-fou correct d'un autre
sprint) et **désélectionné** du full sweep local, avec cette justification.

## 7. Migration QA (les 4)

| Check | Résultat |
|---|---|
| `check_alembic_drift` | **OK (no diff)** |
| `check_schema_snapshot` | **OK (matches head)** |
| `check_migration_patterns` | **OK (no unjustified patterns)** |
| `check_migration_roundtrip` | **OK (schema identical pre/post)** |

## 8. Checks de scope / hygiène

- `check_scope` → **MIGRATION** ✓ (touches migrations/models/schema).
- `check_spec_protocol` → **OK**.
- `check_ruff_budget` → **OK** (544 ≤ 548 baseline, delta −4).
- `ruff check` sur les fichiers touchés → **All checks passed!**.
- **Full sweep local** (tier MIGRATION l'exige) — `pytest -n auto --dist worksteal
  --ignore=tests/test_v1_acceptance.py` : **2774 passés / 1 désélectionné (§6bis)**
  en ~5 min. (Le 1er passage avait 4 échecs : 3 = mises à jour de tests-gardiens
  ci-dessus, 1 = artefact working-tree §6bis.)

## Verdict

**Verdict :** 🟡 **Sb_CUSTOM_PROGRAM_PUBLICATION_01 — PATCH COMPLETE / REVIEW PENDING.**

Publication spec-05-§6-conforme : N templates (un par séance), slug versionné
tronqué, lien côté séance, gel de qualité une fois, idempotence, refus doux,
survie reseed, compatibilité native `session_builder`. Migration additive,
4/4 QA verts. **Aucun commit, aucun push, aucune PR** — en attente d'un GO explicite.
