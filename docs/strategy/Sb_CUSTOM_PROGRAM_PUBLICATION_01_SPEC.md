# Sb_CUSTOM_PROGRAM_PUBLICATION_01 — Publication d'un programme custom (SPEC)

**Cycle :** Custom Program · **Amont :** `Sx_CUSTOM_PROGRAM_05_SESSION_INSTANTIATION_COMPATIBILITY_SPEC.md` §6
**Tier :** MIGRATION · **Statut :** PATCH COMPLETE / REVIEW PENDING

---

## 1. Objectif

Matérialiser un `UserProgram` **validé** en modèles de séance lançables. Un
programme validé cesse d'être une intention éditable et devient un ou plusieurs
`WorkoutTemplate` que le propriétaire lance comme n'importe quelle séance du
catalogue — via le `session_builder` existant, **sans le modifier**.

## 2. Contrat de matérialisation (spec 05 §6 — N templates, PAS un aplati)

- **UNE `UserProgramSession` → UN `WorkoutTemplate`.** Un programme de N séances
  matérialise **N templates** (jamais un conteneur unique aplati).
- Slug de chaque template : **`up{user_id}-{slug_base}-v{current_version}-s{position}`**,
  tronqué de façon déterministe pour tenir dans `WorkoutTemplate.slug` (64).
  Seul `slug_base` est tronqué ; les parties d'identité (`up{uid}`, `-v{n}`,
  `-s{pos}`) survivent toujours, et un tiret pendant laissé par la troncature
  est retiré.
- `catalog_section = "user"` sur chaque template — la section réservée que le
  wipe-guard du seed (`seed_reference_split`) **refuse de recréer et ne supprime
  jamais** : les templates utilisateur **survivent à un reseed**.
- Le **lien programme→template vit côté séance** (migration PUBLICATION_01) :
  `user_program_sessions.published_template_id` (FK `workout_templates.id`,
  `ON DELETE SET NULL`) + `user_program_sessions.template_slug_snapshot`
  (slug figé, trace historique étanche).
- Exercices copiés en ordre de position stable, codes catalogue **`E1..En`** et
  positions séquentielles neuves ; **séries de travail** copiées (`is_warmup`
  exclus — les échauffements restent générés à l'instanciation par le
  `session_builder`, parité catalogue), ré-indexées `1..N`.

## 3. Cycle de vie (spec 04 §6-7)

| État programme | Publication |
|---|---|
| `draft` | **Refus doux** : « validez d'abord ». Aucun template créé. |
| `archived` | **Refus doux** : « désarchivez d'abord ». Aucun template créé. |
| `validated` | Matérialise N templates + fige la qualité + passe `published`. |
| `published` | **Idempotent** : renvoie les templates existants, zéro duplicata. |

- **Gel de qualité une seule fois** : `compute_and_store_quality_review` est
  appelé **pendant que le programme est encore `validated`** (ce writer refuse
  un statut non-scorable), **avant** le passage à `published`. Idempotent :
  une re-publication ne re-score pas.
- **Aucun écrasement silencieux** : une collision de slug remonte un refus doux,
  jamais un 500, jamais un template système muté.
- **Owner-scope sans fuite** : un programme absent OU appartenant à autrui lève
  le **même** `PublishNotFound` (→ 404), comme les autres services custom.

## 4. Migration (additive-only)

Deux colonnes nullable sur `user_program_sessions` (revision `p7q2k8l9n10`,
down_revision `o6p1j7k8m09`) :

- `published_template_id INTEGER NULL` — FK `workout_templates.id`, `ON DELETE SET NULL`, indexée.
- `template_slug_snapshot VARCHAR(64) NULL`.

Aucun backfill (les séances jamais publiées restent `NULL`). Downgrade
symétrique. `ON DELETE SET NULL` (et non CASCADE) : supprimer une template
publiée ne détruit jamais la séance-source — le programme reste la vérité
éditable, la template son artefact.

## 5. UI (SSR, sans JavaScript)

- `GET /programs/{id}/publish` — page de confirmation/état : nombre de séances,
  slugs futurs (ou figés si déjà publié), avertissement d'immutabilité, refus doux.
- `POST /programs/{id}/publish` — matérialise ; succès à 200 (état publié
  ré-affiché, idempotent au re-submit).
- CTA « Publier ce programme » sur `detail.html` **uniquement** pour `validated`.
- `/library` partagée **exclut** `catalog_section="user"` (listing + `/library/{slug}` → 404).

## 6. Périmètre interdit (non-goals)

- **PAS** de template unique aplati ; **PAS** de restriction mono-séance.
- **PAS** de `WorkoutTemplate.user_id` ; **PAS** de table `PublishedUserProgram`.
- **PAS** de `user_programs.published_template_id` (le lien vit côté séance).
- **PAS** de modification du `session_builder`, du générateur, des drafts, du
  moteur de qualité, de l'EKB (JSON ou EKB_04), d'ASSET/BodyMap, de LLM.
- **PAS** de flux unpublish/delete/share, ni d'édition-nouvelle-version.
- Réécriture de `seed.py` interdite (hors tests).

## 7. Limites assumées

- **Collision de slug par troncature** : `slug_base` étant unique par
  utilisateur et le slug étant namespacé par version + position, une collision
  n'est possible qu'entre deux `slug_base` du **même** utilisateur partageant
  leurs ~49 premiers caractères. La contrainte d'unicité sur `WorkoutTemplate.slug`
  protège l'intégrité (remontée en refus doux `IntegrityError`, jamais un 500),
  mais l'auto-suffixage de désambiguïsation est hors V1.
- **`published_template_id` singulier par séance** : une séance pointe UNE
  template. Une re-publication en nouvelle version (slug `-v{n+1}-`) relèverait
  du flux édition-nouvelle-version, explicitement différé.
