# Sb_CUSTOM_PROGRAM_PUBLICATION_02 — Nouveau cycle d'édition post-publication (SPEC)

**Cycle :** Custom Program · **Amont :** `Sx_CUSTOM_PROGRAM_04 §6-7` + `Sx_CUSTOM_PROGRAM_05 §6-7` + PUBLICATION_01
**Tier :** SHARED_CODE (service importé par le router ; **aucune migration**) · **Statut :** PR PENDING

---

## 1. Objectif

PUBLICATION_01 rend une version **immuable**. Un programme publié n'est plus éditable. PUBLICATION_02 donne la suite du cycle de vie : **démarrer un nouveau cycle d'édition** — le programme publié **redevient un brouillon modifiable**, à la **version suivante**, sans jamais toucher l'artefact publié.

## 2. Préflight — conflit de spec tranché (Option A)

Le libellé initial de la mission (« créer une **copie** draft, l'original **reste publié** ») **contredisait** les specs versionnées. Relecture :

- **Spec 04 §6** : *« `published` édité = nouveau cycle : l'édition d'un programme publié **repasse le `UserProgram` en `draft` avec `current_version + 1`** ; l'artefact publié v{n} n'est jamais modifié en place »*.
- **Spec 05 §6-7** : *« édition post-publication = nouvelle version (`current_version + 1`, **retour `draft`**) »*.
- **OQ-PERS-D / OQ-LAUNCH-D** : *« table de versions dédiée ? **non V1** — `current_version` suffit »*.

**Choix retenu (opérateur) : Option A — versioning mono-row spec-compliant.** **Le même** `UserProgram` transite `published → draft (+1)` ; **pas de copie**, **pas de 2ᵉ row**, **pas de table de versions**, **pas de migration**. L'original ne « reste pas publié » — il **devient** le brouillon v{n+1} (c'est le sens même du versioning des specs).

## 3. Comportement (contrat)

| Statut avant | Action |
|---|---|
| `published` | **nouveau cycle** : même row → `status=draft`, `current_version += 1` (une fois), liens de séance effacés |
| `draft` / `validated` | **déjà éditable** → aucun changement, aucun incrément (`incremented=False`) — garde aussi le double-submit |
| `archived` | **refus doux** (désarchiver d'abord) — aucun incrément |

Sur un `published` :
- `id` **inchangé** ; `status` → `draft` ; `current_version` **+1 exactement** ;
- l'arbre (sessions/exercises/rep_targets) est **conservé** — il devient le brouillon édité via WIZARD/éditeur existants ;
- chaque `UserProgramSession.published_template_id` **et** `template_slug_snapshot` sont **effacés** (c'étaient les liens v{n}) ;
- les `WorkoutTemplate` v{n} **ne sont ni mutées ni supprimées** — artefacts catalogue immuables (leur archivage à la re-publication v{n+1} = territoire PUBLICATION_01, **hors périmètre** ici) ;
- **aucune** `UserProgramQualityReview` écrite (qualité gelée à la publication seulement).

**Anti double-incrément** : seul `published` incrémente ; après le 1ᵉʳ appel le statut est `draft`, donc un re-POST retombe dans la branche « déjà éditable » → jamais deux incréments.

**Owner-scope** : absent OU d'un autre utilisateur → **même** `VersioningNotFound` (→ 404), sans fuite d'existence.

## 4. Surface

- Service `app/services/user_program_versioning.py` : `start_new_edit_cycle(db, user_id, program_id) -> NewCycleResult`.
- Route `POST /programs/{id}/new-version` (owner-scopée) : succès → `303` vers l'éditeur (le brouillon retourné) ; archivé → refus doux ré-affiché ; absent/foreign → 404.
- CTA `detail.html` **uniquement** pour `status=published` (« Créer une nouvelle version modifiable »).

## 5. Périmètre interdit (non-goals)

Pas de **copie** / 2ᵉ row · pas de **table de versions** · **aucune migration** · aucune mutation/suppression de `WorkoutTemplate` · pas d'unpublish · **aucun archivage** dans ce sprint · pas de `session_builder` · pas d'EKB_04 · pas d'ASSET/BodyMap · pas de réécriture de PUBLICATION_01 au-delà d'un import réutilisable · pas d'écriture de quality review.

## 6. Limites assumées

- **Concurrence** : deux POST simultanés lisant `published` avant commit pourraient tous deux incrémenter. Négligeable en SSR mono-utilisateur ; le double-submit **séquentiel** (re-submit du formulaire) est garanti sans double incrément (statut `draft` après le 1ᵉʳ). Un verrou optimiste relève d'un durcissement séparé.
- **Templates v{n} orphelins** : après le nouveau cycle, plus aucun `published_template_id` ne pointe vers les templates v{n} (liens effacés). Elles survivent comme templates catalogue `user` ; leur archivage propre est déclenché à la **re-publication v{n+1}** (spec 05, PUBLICATION_01).
