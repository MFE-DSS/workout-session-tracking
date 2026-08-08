# Sb_CUSTOM_PROGRAM_PUBLICATION_03 — Accès & lancement des séances publiées (SPEC)

**Cycle :** Custom Program · **Amont :** `Sx_CUSTOM_PROGRAM_05 §14` (accès propriétaire) + PUBLICATION_01 (matérialisation N templates) + PUBLICATION_02 (cycle d'édition)
**Tier :** SHARED_CODE (services importés par les routers ; **aucune migration**) · **Statut :** ✅ MERGED (PR #56, merge `bc0f68f`, 2026-08-08)

---

## 1. Objectif

PUBLICATION_01 matérialise un `UserProgram` validé en **N `WorkoutTemplate` custom** (`catalog_section="user"`), délibérément **exclus du catalogue global** `/library`. Ces séances existaient donc en base **sans porte de lancement** côté propriétaire. PUBLICATION_03 ferme la boucle : **le propriétaire accède à ses séances publiées et les lance depuis l'UI de son programme possédé** — jamais via le catalogue partagé.

## 2. Préflight — modèle d'accès confirmé (pas de conflit)

Relecture `Sx_CUSTOM_PROGRAM_05 §14` :

- L'accès aux templates publiés est **privé au propriétaire**, résolu par la chaîne **`UserProgram (owner) → UserProgramSession → published_template_id`**.
- Il n'existe **pas de `WorkoutTemplate.user_id`** — la propriété vit **côté programme**, pas côté template (contrainte tenue depuis PUBLICATION_01).
- Le catalogue global `/library` **continue d'exclure** `catalog_section="user"` (listing **et** `/library/{slug}` → 404). PUBLICATION_03 **n'ajoute aucune** exposition catalogue.

Le libellé de la mission est **cohérent avec les specs versionnées** : accès propriétaire uniquement, aucun partage/public, aucun navigateur d'historique de versions. **Aucun conflit → build direct.**

## 3. Comportement (contrat)

### 3.1 Lancement depuis le programme possédé (chemin nominal)

`POST /programs/{program_id}/sessions/{session_id}/start` (owner-scopée) :

| Cas | Résultat |
|---|---|
| Séance **possédée + publiée** (`published_template_id` non nul, programme **non archivé**) | `instantiate_session` du template lié → `303` vers `/sessions/{id}` |
| Programme/séance **absent** OU **d'un autre utilisateur** OU **non publié** (`published_template_id IS NULL`) OU **archivé** | **404** indistinct (`LaunchNotFound`, zéro fuite d'existence) |

### 3.2 Garde du chemin par slug (`create_session`)

`POST /sessions` résout un `WorkoutTemplate` par slug. **Défaut préexistant fermé** : avant ce sprint, ce chemin n'avait **aucune garde de propriété** — un utilisateur authentifié pouvait lancer **le template `user` d'un autre** en devinant/soumettant son slug (les templates `user` sont exclus du listing mais restaient joignables par slug). Nouvelle règle :

| Template | Résultat |
|---|---|
| `catalog_section="user"` **possédé** (via `is_owned_published_template`, programme non archivé) | lancement autorisé (`303`) |
| `catalog_section="user"` **d'un autre / non possédé** | **404** (« Unknown template », indistinct) |
| Template **système** (toute autre `catalog_section`) | **inchangé** — lançable par tous |

### 3.3 CTA UI

`detail.html` : bouton **« Démarrer cette séance »** par séance, affiché **uniquement** si `program.status == 'published'` **et** `program.archived_at is none` **et** `session.published_template_id`. Aucun CTA sur `draft` / `validated` / `archived`.

## 4. Surface

- **Service neuf** `app/services/user_program_launch.py` (READ-ONLY, aucune mutation) :
  - `resolve_owned_published_template(db, user_id, program_id, session_id) -> WorkoutTemplate` (eager-load exercices/rep_targets pour l'instanciation) ;
  - `is_owned_published_template(db, user_id, template_id) -> bool` (reverse-lookup pour la garde slug) ;
  - `LaunchNotFound` (→ 404 indistinct).
  - Les deux requêtes exigent `UserProgram.archived_at IS NULL` (soft-delete = non lançable, spec 04 §8).
- **Route** `POST /programs/{id}/sessions/{sid}/start` dans `app/routers/user_programs.py` : `resolve_owned_published_template` → `instantiate_session(db, template, now, user_id)` → `303`.
- **Garde** dans `app/routers/sessions.py::create_session` : template `user` non possédé → 404 (`is_owned_published_template`).
- **Template** `detail.html` : CTA « Démarrer cette séance » (cf. §3.3).

## 5. Périmètre interdit (non-goals)

Pas d'exposition catalogue globale · pas de partage / accès public · pas de navigateur d'historique de versions · **aucune nouvelle table** · **aucun `WorkoutTemplate.user_id`** · **aucune migration** · **aucune réécriture de `session_builder`** (l'instanciation existante est réutilisée telle quelle) · pas de refonte du cycle de vie PUBLICATION_01/02 · pas d'EKB / ASSET / BodyMap · **aucun affaiblissement des gardes d'exclusion `/library`**.

## 6. Limites assumées & constat notable

- **Fermeture d'un défaut préexistant** : la garde de propriété sur `create_session` (§3.2) est un **durcissement de sécurité** — le chemin slug était ouvert cross-utilisateur pour les templates `user` avant ce sprint. Les templates système restent délibérément publics.
- **Instanciation réutilisée** : `instantiate_session` est appelée sans modification ; PUBLICATION_03 ne touche ni le builder ni le modèle de séance.
- **Archivé = non lançable** : cohérent avec le soft-delete (spec 04 §8) ; l'archivage ne coupant pas les liens `published_template_id`, la garde `archived_at IS NULL` est portée par les deux requêtes du service **et** le CTA — un programme soft-supprimé ne peut être lancé ni par l'UI ni par POST direct.
- **Le lancement est en lecture** côté programme/template : aucune `WorkoutTemplate` ni `UserProgram` (statut/`current_version`) n'est mutée (invariants prouvés par test). Seule une `WorkoutSession` est créée, comme pour tout template.
