# Human Review — Sx_CUSTOM_PROGRAM_04 User Program Persistence Spec

**Verdict** : ✅ **HUMAN REVIEW ACCEPTED / SPEC ONLY / BUILD NOT AUTHORIZED**
**Date** : 2026-07-15
**Type** : revue humaine — docs-only (aucun code touché par cette revue ni par la spec)
**Track** : `Sx_CUSTOM_PROGRAM` (01 ✅ · 02 ✅ · 03 ✅ ACCEPTED — **04 = ce document**, spec fille 3/4)
**Branche** : `spec/sx-custom-program-01-intelligent-builder` (worktree isolé, synchronisée
origin, spec commit `263810d`)
**Spec** : [`Sx_CUSTOM_PROGRAM_04_USER_PROGRAM_PERSISTENCE_SPEC.md`](strategy/Sx_CUSTOM_PROGRAM_04_USER_PROGRAM_PERSISTENCE_SPEC.md)

---

## 1. Verdict

**Sx_CUSTOM_PROGRAM_04 est acceptée** comme définition de la persistance des programmes
utilisateur avant toute matérialisation. Le statut reste **SPEC ONLY** : **aucune migration,
aucun code, aucun seed, aucune data modifiée** — `Sb_CUSTOM_PROGRAM_PERSISTENCE_*`
NOT AUTHORIZED.

## 2. Scope accepté

Persistance des **brouillons `UserProgram*`** (état wizard SSR en base) · sessions/exercices/
rep targets utilisateur · **réponses wizard** (`wizard_answers_json`, reproductibilité de la
génération déterministe) · **quality reviews** (trace versionnée, spec 03) · **ownership
utilisateur** dur · statuts · versioning · quotas · **préparation Option C sans publication**
(zéro pollution du catalogue système).

## 3. Modèle de tables accepté (5)

`user_programs` (status, `current_version`, `slug_base`, caches grade, `published_template_id`
FK nullable préparatoire) · `user_program_sessions` (position/name/kind/focus/durée cible) ·
`user_program_exercises` (**`exercise_name` = nom EKB invariant** + `variant_key`/
`variant_group` + copies dénormalisées equipment/pattern + `source_reason` d'explicabilité) ·
`user_program_rep_targets` (min/max/technique, `is_warmup` préparé défaut false) ·
`user_program_quality_reviews` (**une trace figée par version**, unique `(program, version)`,
`scoring_version` pinnée, rows jamais réécrites). FK explicites (CASCADE intra-arbre user,
SET NULL vers catalogue), uniques de position, index `(user_id, status)` / `(user_id,
updated_at)`.

## 4. Décision Option C

| Contrat | Décision |
|---|---|
| **`UserProgram*` = source de vérité d'édition** | ✅ acté |
| `WorkoutTemplate` custom = **futur artefact de publication** (spec 05) | ✅ acté |
| **Aucune matérialisation, aucune publication dans cette spec** | ✅ contraignant |
| `published_template_id` = **préparatoire seulement** (FK nullable SET NULL, non utilisée avant spec 05) | ✅ acté |
| `WorkoutTemplate` jamais source de vérité des brouillons ni du score | ✅ (cohérent spec 03 §10) |

## 5. Statuts acceptés

`draft` → `validated` (récap wizard) → `published` (**transition réalisée uniquement par les
builds de la spec 05**) ; `draft/validated/published → archived` ; dé-archiver = retour
`draft`. **Édition post-publication = nouveau cycle** (`current_version + 1`, retour `draft`) —
**jamais de modification en place d'un artefact publié**. Mutation d'une row `quality_reviews`
existante : interdite.

## 6. Versioning

`current_version` (départ 1) · **une review par version** (unique) · publication future **par
version** (slug `up{user_id}-{slug_base}-v{n}`) · **versions publiées immuables** (contrat dur
#3 du parent) · **historique passé préservé** (snapshots + FK SET NULL, mécanique éprouvée du
catalogue — les séances loggées sur v{n} restent intactes).

## 7. Ownership / isolation

`user_id` **NOT NULL** obligatoire · **aucun partage V1, aucun programme global V1** ·
**isolation inter-user stricte** (filtre `user_id` systématique, pattern Sb_26.7, tests
d'isolation à livrer avec les builds) · **soft delete / archivage recommandé**
(`archived_at` ; hard delete = OQ-PERS-A, réservé à un flux explicite futur) · **quotas V1
proposés** (10 programmes actifs / 5 versions / 7 sessions / 10 exercices — valeurs exactes à
confirmer en build/spec fille si nécessaire, OQ-PERS-E).

## 8. Compatibilités validées

- **EKB (spec 02)** : `exercise_name` invariant (jamais renommé), `variant_key` recommandé,
  `variant_group` pour redondance/remplacement ; copies dénormalisées, l'EKB reste la
  référence ; gap signalé par QA, jamais corrigé silencieusement.
- **Scoring (spec 03)** : reviews tracées par version, `assumptions_json`/`missing_data_json`
  persistés ; caches `quality_grade`/`quality_score_json` = affichage seulement ; **scoring
  non bloquant** (aucune transition dépendante du grade).
- **Future librairie** : grade et statut affichables depuis les caches.
- **Future publication** : `slug_base`, versioning, `published_template_id` **préparés** —
  toute la mécanique de matérialisation (mapping, wipe-guard, filtres, codes de slot,
  archivage catalogue) **renvoyée à `Sx_CUSTOM_PROGRAM_05`**.

## 9. Contraintes de migration futures (actées)

**Additive-only** (5 tables neuves, **zéro table existante modifiée**) · **une migration par
build**, jamais groupées · FK explicites avec politique `ON DELETE` documentée · index
user/status/version · **pas de seed** (aucune donnée système dans ces tables) · tests
rollback/roundtrip + snapshot/drift à prévoir (gates `check_migration_*`, tier `migration`).

## 10. Risques acceptés (spec §14, R1-R8)

Modèle trop large (bordé : 5 tables minimales, le reste = V2/OQ) · JSON trop opaque (JSON =
payloads seulement, le requêté = colonnes) · duplication avec `WorkoutTemplate` (rôles
disjoints actés) · édition post-publication (nouveau cycle obligatoire) · suppression
destructrice (soft delete par défaut) · quotas absents (quotas V1 posés) · fuite inter-user
(user_id dur + tests dédiés) · scoring désynchronisé (cache ≠ vérité, trace figée).

## 11. Open questions (OQ-PERS-A → OQ-PERS-J)

Statut : **questions à trancher en review de spec 05 / builds, pas des décisions finales** —
positions par défaut : **soft delete** · statut `validated` **conservé** · `published_template_id`
en **colonne V1** (table de versions dédiée si multi-artefacts requis) · **pas de
`user_program_versions` V1** (rouverte en spec 05 si la matérialisation l'exige) · quotas
10/5/7/10 · **grade C publiable confirmé par défaut** (décision finale wizard/spec 05) ·
scoring **à chaque édition** · **colonnes dénormalisées** plutôt que JSON pour les métadonnées
requêtées · **partage/copie hors V1** (aucun champ préparé) · `ekb_version` en colonne
additive sur la trace (recommandé, tranché en review).

## 12. Queue suivante

| Élément | Statut |
|---|---|
| **`Sx_CUSTOM_PROGRAM_05` — Session Instantiation Compatibility Spec** | 🔵 **NEXT SPEC CANDIDATE** (SPEC ONLY, sur GO explicite) — dernière spec fille : matérialisation, **wipe-guard seed**, filtres reco/librairie, slugs/codes de slot |
| `Sb_CUSTOM_PROGRAM_*` (builds parent) | ❌ **NOT AUTHORIZED** |
| `Sb_CUSTOM_PROGRAM_PERSISTENCE_01→05` | ❌ **NOT AUTHORIZED** |
| `Sb_CUSTOM_PROGRAM_EKB_*` / `SCORING_*` | ❌ NOT AUTHORIZED |
| Migrations / seed / data / app code | ❌ toujours interdits |

---

## Verdict

**Verdict :** ✅ **Sx_CUSTOM_PROGRAM_04 User Program Persistence Spec — HUMAN REVIEW ACCEPTED /
SPEC ONLY / BUILD NOT AUTHORIZED.**

La persistance `UserProgram*` est actée comme direction : 5 tables minimales (source de vérité
d'édition, Option C), statuts et transitions avec **nouveau cycle obligatoire post-publication**,
versions publiées immuables, ownership dur + soft delete, quotas V1, trace scoring figée par
version, compatibilités EKB/scoring/publication préparées. **Publication et matérialisation
restent intégralement renvoyées à `Sx_CUSTOM_PROGRAM_05`** (next spec candidate, sur GO).
Les 10 OQ restent ouvertes. Aucun code touché ; repo principal UI non touché.
