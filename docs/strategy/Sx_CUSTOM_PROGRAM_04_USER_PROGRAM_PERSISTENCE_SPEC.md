# Sx_CUSTOM_PROGRAM_04 — User Program Persistence Spec

**Type :** SPEC ONLY / DATA MODEL / PERSISTENCE DESIGN
**Date :** 2026-07-15
**Statut :** ⚪ SPEC DRAFT OPENED — pending human review · **BUILD NOT AUTHORIZED**
**Track :** `Sx_CUSTOM_PROGRAM` (01 ✅ · 02 ✅ · 03 ✅ ACCEPTED — ce document = spec fille 3/4)
**Branche :** `spec/sx-custom-program-01-intelligent-builder` (worktree isolé)
**Autorisations :** aucune migration · aucun seed · aucun code `app/` · aucun changement `data/`

---

## 1. Verdict / statut

**SPEC ONLY.** Ce document définit la persistance des programmes utilisateur (`UserProgram*`)
**avant toute matérialisation** en `WorkoutTemplate`. **Rien n'est buildé** :
`Sb_CUSTOM_PROGRAM_PERSISTENCE_*` NOT AUTHORIZED, aucune migration, aucun seed, aucun code
`app/`, aucun changement `data/`. La publication/matérialisation est **hors de cette spec**
(renvoyée à `Sx_CUSTOM_PROGRAM_05`).

## 2. Rôle de la persistance

- Stocker les **brouillons du wizard** (état d'avancement, réponses) — le wizard est SSR :
  l'état vit en base, jamais côté client (parent §6).
- Stocker la **structure d'un programme utilisateur** : sessions, exercices, rep targets.
- Stocker les **réponses du wizard** (`wizard_answers_json`) — entrée reproductible du moteur
  de génération déterministe.
- Stocker les **reviews de qualité** (trace versionnée, spec 03 §9 Option C).
- **Préparer** la publication future (`slug_base`, `published_template_id`,
  `current_version`) **sans la réaliser**.
- **Ne jamais polluer le catalogue système** : aucune écriture dans `workout_templates` /
  `template_exercises` / `rep_targets` dans ce périmètre.

## 3. Modèle Option C (rappel contraignant, parent §9)

- **`UserProgram*` = source de vérité d'édition** — wizard, édition par cartes, scoring,
  statuts, versions vivent ici.
- **`WorkoutTemplate` custom = artefact de publication futur** (spec 05) — régénéré par
  version publiée, jamais édité en place.
- **Aucune publication ni matérialisation dans cette spec** — pas de wipe-guard, pas de
  filtres reco/librairie ici (contrats durs du parent, portés par la spec 05 et ses builds).
- **`WorkoutTemplate` ne devient jamais source de vérité des brouillons** ni du score
  (spec 03 §10).

## 4-5. Tables cibles et champs proposés

Conventions repo : PK `id` int, timestamps timezone-aware, `*_json` en `Text` (SQLite),
FK explicites `ON DELETE` documenté, index nommés.

### `user_programs`

| Champ | Type | Notes |
|---|---|---|
| `id` | PK int | |
| `user_id` | FK `users.id`, **NOT NULL**, `ON DELETE CASCADE` | ownership dur (§8) |
| `title` | String(128) NOT NULL | libellé libre user |
| `slug_base` | String(64) NOT NULL | base du futur slug publié `up{user_id}-{slug_base}-v{n}` (parent, OQ-CP-A) ; dérivé du titre, figé à la création |
| `status` | String(16) NOT NULL, default `draft` | `draft` / `validated` / `published` / `archived` (§6) |
| `current_version` | int NOT NULL, default 1 | incrémenté à chaque nouveau cycle de publication (§7) |
| `wizard_answers_json` | Text nullable | réponses wizard (reproductibilité génération) |
| `quality_grade` | String(1) nullable | cache d'affichage du dernier scoring (`A`/`B`/`C`) |
| `quality_score_json` | Text nullable | cache d'affichage du dernier `QualityReview` (brouillon) — la **trace** de publication vit dans `user_program_quality_reviews` |
| `published_template_id` | FK `workout_templates.id` **nullable**, `ON DELETE SET NULL` | **préparé, non utilisé avant spec 05** ; pointe l'artefact de la version courante publiée |
| `created_at` / `updated_at` | DateTime tz | |
| `archived_at` | DateTime tz nullable | suppression logique (§8) |

Index : `(user_id, status)`, `(user_id, updated_at)`.

### `user_program_sessions`

| Champ | Type | Notes |
|---|---|---|
| `id` | PK | |
| `user_program_id` | FK NOT NULL `ON DELETE CASCADE` | |
| `position` | int NOT NULL | unique `(user_program_id, position)` |
| `name` | String(128) NOT NULL | ex. « Push A » |
| `kind` | String(16) NOT NULL default `strength` | `strength` / `cardio` (aligné catalogue) |
| `focus` | String(128) NOT NULL default `""` | |
| `duration_target_minutes` | int nullable | budget déclaré (réalisme durée, scoring) |
| `notes` | Text nullable | |

### `user_program_exercises`

| Champ | Type | Notes |
|---|---|---|
| `id` | PK | |
| `user_program_session_id` | FK NOT NULL `ON DELETE CASCADE` | |
| `position` | int NOT NULL | unique `(user_program_session_id, position)` |
| `exercise_name` | String(255) NOT NULL | **nom canonique EKB = invariant historique** (§11) |
| `variant_key` | String(128) nullable | optionnel mais recommandé (EKB §4) |
| `variant_group` | String(128) nullable | redondance/remplacement |
| `equipment_family` | String(64) nullable | copie dénormalisée EKB (filtre matériel) |
| `movement_pattern` | String(64) nullable | copie dénormalisée EKB |
| `set_scheme` | String(255) NOT NULL | ex. « 3x 8-12 » (format catalogue) |
| `notes` | Text nullable | |
| `source_reason` | String(255) nullable | explicabilité génération (« pattern push requis par le split ») ou `manual` |

### `user_program_rep_targets`

| Champ | Type | Notes |
|---|---|---|
| `id` | PK | |
| `user_program_exercise_id` | FK NOT NULL `ON DELETE CASCADE` | |
| `set_index` | int NOT NULL | unique `(user_program_exercise_id, set_index, is_warmup)` |
| `min_reps` / `max_reps` | int NOT NULL | ranges exploitables overload (spec 03 `overload_compatibility`) |
| `technique` | String(8) nullable | aligné `RepTarget.technique` catalogue |
| `is_warmup` | bool NOT NULL default false | V1 : les warmups restent générés à l'instanciation (comme le catalogue) — champ préparé, défaut false partout (OQ-PERS-H) |

### `user_program_quality_reviews`

| Champ | Type | Notes |
|---|---|---|
| `id` | PK | |
| `user_program_id` | FK NOT NULL `ON DELETE CASCADE` | |
| `version` | int NOT NULL | unique `(user_program_id, version)` — une trace par version publiée |
| `grade` | String(1) NOT NULL | |
| `global_score` | int nullable | |
| `subscores_json` / `alerts_json` / `suggestions_json` / `assumptions_json` / `missing_data_json` | Text | modèle `QualityReview` (spec 03 §4) |
| `scoring_version` | int NOT NULL | `PROGRAM_QUALITY_SCORING_VERSION` pinnée |
| `computed_at` | DateTime tz NOT NULL | |

**Rows jamais réécrites** (doctrine d'invariance : trace figée par version, pattern
Sb_24.1/Sx_30). Note : `ekb_version` (spec 03 §4) sera portée par `subscores_json` ou une
colonne additive future — tranché en review (OQ-PERS-I implicite dans OQ-PERS-H… non : cf.
OQ-PERS ci-dessous, question dédiée).

## 6. Statuts et transitions

| Statut | Sens |
|---|---|
| `draft` | en construction (wizard en cours ou édition) — scoring recalculé à chaque édition |
| `validated` | l'utilisateur a validé le récap (fin du wizard) — prêt à publier, encore éditable (retour à `draft` implicite à la première édition) |
| `published` | une version matérialisée existe (spec 05) — l'artefact publié est immuable |
| `archived` | retiré de la librairie active — données conservées (suppression logique) |

**Transitions autorisées** :
- `draft → validated` (récap accepté) ;
- `validated → published` (**réalisée seulement par les builds de la spec 05**) ;
- `draft/validated/published → archived` ;
- **`published` édité = nouveau cycle** : l'édition d'un programme publié repasse le
  `UserProgram` en `draft` avec `current_version + 1` ; **l'artefact publié v{n} n'est
  jamais modifié en place** (il sera archivé côté catalogue lors de la publication v{n+1},
  mécanique spec 05).

Transitions interdites : `archived → published` direct (dé-archiver = retour `draft`) ;
toute mutation d'une row `quality_reviews` existante.

## 7. Versioning

- `current_version` sur `user_programs` ; démarre à 1.
- **Une quality review par version** (`unique (user_program_id, version)`), écrite au moment
  de la publication de cette version (spec 03 §9-C).
- **Publication par version** (spec 05) : slug `up{user_id}-{slug_base}-v{n}` ; **versions
  publiées immuables** (contrat dur #3 du parent).
- **Édition après publication = nouveau cycle** (§6) — jamais de mutation de l'existant.
- **Historique passé préservé** : les séances loggées sur v{n} restent intactes
  (snapshots + FK `SET NULL`, mécanique éprouvée du catalogue).

## 8. Ownership et isolation

- `user_id` **NOT NULL** — tout programme a un propriétaire.
- **Aucun programme partagé V1, aucun programme global V1** — pas de row sans owner, pas de
  visibilité croisée.
- **Aucune lecture par un autre user** : toute requête filtre `user_id` (pattern
  `_load_session` / discipline Sb_26.7 scope-auth ; tests d'isolation type
  `test_auth_scope_isolation` à prévoir dans les builds).
- **Quotas** (§9) appliqués à la création/publication.
- **Suppression logique** (`archived_at`) plutôt que destructrice — le hard delete éventuel
  est une OQ (OQ-PERS-A), par défaut réservé à un futur flux RGPD-like explicite.

## 9. Quotas V1 (proposition)

| Quota | Valeur V1 proposée | Justification |
|---|---|---|
| Programmes **actifs** (non archivés) par user | **10** | assez pour expérimenter, borne le bloat librairie/reco future |
| Versions publiées **conservées** par programme | **5** (les plus anciennes archivées côté catalogue, données `UserProgram*` conservées) | borne la croissance de templates matérialisés (risque R10 parent) |
| Sessions par programme | **7** | > aucun split réaliste hebdo ; borne l'UI cartes |
| Exercices par session | **10** | cohérent catalogue système (max 7 constaté) + marge ; borne durée/scoring |

Anti-bloat : les quotas sont des **constantes applicatives versionnées** (pas de config DB),
dépassement → message doux non culpabilisant + suggestion d'archiver. Valeurs exactes =
OQ-PERS-E.

## 10. Compatibilité avec le scoring (spec 03)

- Scoring **recalculable à la volée** sur brouillon (aucune écriture requise pour afficher).
- **Trace persistée** dans `user_program_quality_reviews` à la publication (§5, §7).
- `quality_grade` / `quality_score_json` sur `user_programs` = **cache d'affichage** du
  dernier calcul (librairie future) — jamais la vérité (la trace et le recalcul le sont).
- `assumptions_json` / `missing_data_json` **persistés dans la trace** (auditabilité).
- **Scoring non bloquant par défaut** : aucun statut ni transition ne dépend du grade
  (grade C publiable avec avertissement — OQ-SCORE-C, reconfirmée OQ-PERS-F).

## 11. Compatibilité avec l'EKB (spec 02)

- `exercise_name` = **nom canonique EKB, invariant historique** — jamais renommé ; c'est lui
  qui deviendra `exercise_name_snapshot` à l'instanciation des séances (spec 05).
- `variant_key` optionnel mais recommandé ; `variant_group` porté pour la redondance
  (scoring) et le remplacement (édition) — copies dénormalisées au moment de l'édition,
  **l'EKB reste la référence**.
- **Pas de renommage EKB** ; une entrée user pointant un nom absent de l'EKB est signalée
  par la QA (gap), jamais corrigée silencieusement.

## 12. Compatibilité future avec la publication (spec 05)

**Préparé ici** : `published_template_id` (FK nullable SET NULL), `slug_base`,
`current_version`, statuts/transitions. **Non défini ici** (renvoyé à
`Sx_CUSTOM_PROGRAM_05`) : mécanique de matérialisation (mapping vers
`WorkoutTemplate`/`TemplateExercise`/`RepTarget`), **wipe-guard seed**, filtres
reco/librairie, archivage des versions côté catalogue, codes de slot (E1..E7), lancement de
séance. Aucun build de publication ne peut s'ouvrir avant l'acceptance de la spec 05.

## 13. Contraintes de migration futures

- **Additive-only** (contrat CLAUDE.md) — 5 tables neuves, **zéro** modification de table
  existante dans ce périmètre (le `published_template_id` est une FK d'une table neuve vers
  une table existante : additive).
- **Une migration par build**, jamais groupées (`PERSISTENCE_01` → `_03`, §17).
- **FK explicites** avec politique `ON DELETE` documentée (CASCADE intra-arbre user,
  SET NULL vers le catalogue).
- **Index** : `(user_id, status)`, `(user_id, updated_at)`, uniques de position et de
  version (§5).
- **Pas de seed** (aucune donnée système dans ces tables).
- **Tests migration** : rollback/roundtrip + snapshot/drift (gates `check_migration_*`
  existants, tier `migration` du scope-guard).

## 14. Risques

| # | Risque | Mitigation |
|---|---|---|
| R1 | Modèle trop large (sur-ingénierie V1) | 5 tables minimales ; tout le reste (partage, tags, historique de versions détaillé) = V2/OQ |
| R2 | JSON trop opaque (`wizard_answers`, `subscores`) | JSON réservé aux payloads d'affichage/reproductibilité ; tout ce qui est requêté (status, version, grade) = colonne |
| R3 | Duplication conceptuelle avec `WorkoutTemplate` | rôles disjoints actés (§3) : édition vs artefact ; la matérialisation est unidirectionnelle |
| R4 | Édition post-publication corrompant l'artefact | transitions §6 : nouveau cycle obligatoire, artefact immuable |
| R5 | Suppression destructrice | `archived_at` logique par défaut ; hard delete = OQ-PERS-A |
| R6 | Quotas absents → bloat | quotas V1 §9, constantes versionnées |
| R7 | Fuite inter-user | `user_id` NOT NULL + filtre systématique + tests d'isolation dédiés |
| R8 | Scoring désynchronisé (cache mensonger) | cache = affichage seulement ; recalcul à chaque édition ; trace figée par version |

## 15. Open questions

| OQ | Question | Position par défaut proposée |
|---|---|---|
| OQ-PERS-A | Soft delete ou hard delete ? | **soft** (`archived_at`) ; hard delete réservé à un flux explicite futur |
| OQ-PERS-B | Statut `validated` utile ou trop complexe ? | **conservé** (marque la fin du wizard, utile UX récap) ; fusion avec `draft` si la review le juge superflu |
| OQ-PERS-C | `published_template_id` dans `user_programs` ou table de versions dédiée ? | **colonne V1** (pointe la version courante) ; table `user_program_versions` si l'historique multi-artefacts devient requis |
| OQ-PERS-D | Faut-il `user_program_versions` séparée dès V1 ? | **non V1** — `current_version` + trace reviews suffisent ; rouverte en spec 05 si la matérialisation l'exige |
| OQ-PERS-E | Quotas exacts V1 ? | 10 programmes / 5 versions / 7 sessions / 10 exercices (§9) |
| OQ-PERS-F | Grade C publiable confirmé ? | **oui, avec avertissement** (aligné OQ-CP-J / OQ-SCORE-C) — décision finale au wizard/spec 05 |
| OQ-PERS-G | Scoring recalculé à chaque édition ou seulement à la validation ? | **à chaque édition** (feedback immédiat, moteur pur peu coûteux) ; dégradable si perf |
| OQ-PERS-H | JSON vs colonnes normalisées pour les métadonnées d'exercice (`equipment_family`, `movement_pattern`) ? | **colonnes dénormalisées** V1 (filtres + lisibilité SQL) ; `is_warmup` préparé mais défaut false partout V1 |
| OQ-PERS-I | Partage / copie de programme en V2 ? | **hors V1** (aucun champ préparé) ; V2 dédiée si le dogfood le demande |
| OQ-PERS-J | Où pinner `ekb_version` dans la trace ? | colonne additive sur `quality_reviews` recommandée (traçabilité requêtable) — tranché en review |

## 16. Acceptance criteria (cette spec)

- [ ] 5 tables cibles définies avec champs, FK, uniques et index (§4-5).
- [ ] Statuts et transitions définis, y compris le nouveau cycle post-publication (§6).
- [ ] Versioning défini (versions publiées immuables, trace par version) (§7).
- [ ] Ownership/isolation définis (user_id dur, aucune lecture croisée, soft delete) (§8).
- [ ] Quotas V1 proposés et justifiés (§9).
- [ ] Compatibilités scoring/EKB/Option C préparées (§10-12), **publication renvoyée à 05**.
- [ ] Contraintes de migration futures posées (additive-only, une par build) (§13).
- [ ] Build toujours interdit ; registry/roadmap mis à jour.

## 17. Build queue proposée (aucune n'est ouverte par cette spec)

| Build | Objet | Gate |
|---|---|---|
| `Sb_CUSTOM_PROGRAM_PERSISTENCE_01` | Migration additive `user_programs` (+ modèle + tests migration) | spec 04 acceptée |
| `Sb_CUSTOM_PROGRAM_PERSISTENCE_02` | Migrations `user_program_sessions` / `_exercises` / `_rep_targets` (une par build si le review l'exige) | 01 |
| `Sb_CUSTOM_PROGRAM_PERSISTENCE_03` | Migration `user_program_quality_reviews` | 01 + spec 03 acceptée (fait) |
| `Sb_CUSTOM_PROGRAM_PERSISTENCE_04` | Repository/service **draft CRUD minimal** (create/read/update/archive, isolation user, quotas) — aucun endpoint UI | 01-03 |
| `Sb_CUSTOM_PROGRAM_PERSISTENCE_05` | QA + scope hardening (tests isolation inter-user, quotas, transitions, invariance reviews) | 04 |

## 18. Non-goals

Pas de build · pas d'UI/wizard (builds parent) · pas de migration ni seed **exécutés** ·
pas de publication/matérialisation (spec 05) · pas de wipe-guard ici (spec 05) · pas de
partage inter-user · pas de programme global/système · pas de modification du catalogue ni
d'aucune table existante · pas de LLM · pas de claim médical.

---

*Spec draft — build, migrations, seed et code applicatif explicitement non autorisés.
Prochaine décision : human review de ce document. Spec suivante :
`Sx_CUSTOM_PROGRAM_05 — Session Instantiation Compatibility Spec` (matérialisation,
wipe-guard, filtres, slugs, codes de slot).*
