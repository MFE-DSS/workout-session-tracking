# Sx_CUSTOM_PROGRAM_05 — Session Instantiation Compatibility Spec

**Type :** SPEC ONLY / INTEGRATION CONTRACTS / MATERIALIZATION DESIGN
**Date :** 2026-07-15
**Statut :** ⚪ SPEC DRAFT OPENED — pending human review · **BUILD NOT AUTHORIZED**
**Track :** `Sx_CUSTOM_PROGRAM` (01 ✅ · 02 ✅ · 03 ✅ · 04 ✅ ACCEPTED — ce document =
**spec fille 4/4, dernière de la queue**)
**Branche :** `spec/sx-custom-program-01-intelligent-builder` (worktree isolé)
**Autorisations :** aucune migration · aucun seed · aucun code · aucune data modifiée
**Sensibilité :** ce périmètre touche, en build futur, le composant le plus dangereux du
track (le seed catalogue) et le pipeline analytique — d'où le niveau de détail des contrats.

---

## 1. Verdict / statut

**SPEC ONLY.** Ce document définit comment un programme utilisateur **validé** pourra, plus
tard, devenir **lançable** — matérialisation en `WorkoutTemplate` custom protégé — **sans
casser le pipeline existant** (session_builder, overload, history, stats, KPIs). **Rien n'est
buildé** : `Sb_CUSTOM_PROGRAM_LAUNCH_*` NOT AUTHORIZED, **aucune migration, aucun code, aucun
seed, aucune data modifiée**.

## 2. Rôle de cette spec

- Définir la **compatibilité** entre `UserProgram*` (spec 04) et le moteur de séance existant.
- Spécifier la **matérialisation future** en `WorkoutTemplate` custom **protégé**.
- **Préserver `session_builder`** tel quel (aucune abstraction imposée en V1).
- **Préserver overload / history / stats / KPIs** — tout le pipeline snapshot-based hérite
  sans modification.
- **Aucun build dans cette spec** — elle ferme la spec queue ; toute exécution passe par la
  build queue §17, chacun sur GO explicite.

## 3. Rappel Option C (contraignant, parent §9 + spec 04)

`UserProgram*` = source de vérité d'édition · `WorkoutTemplate` custom = artefact de
publication · édition post-publication = **nouvelle version** (`current_version + 1`, retour
`draft`) · anciennes versions **immuables et archivées** (`catalog_section` archivée côté
catalogue, données `UserProgram*` conservées) · **jamais de mutation en place d'un template
publié**.

## 4. Wipe-guard seed (contrat dur #1 — précisé)

- **Danger actuel (audité)** : `seed_reference_split()` (`app/services/seed.py:58-60`)
  exécute, à chaque bump de version de `reference_split.json`, un **`DELETE` intégral sans
  filtre** de `RepTarget`, `TemplateExercise`, `WorkoutTemplate`, puis reconstruit. Toute row
  custom dans ces tables serait **détruite au premier bump**.
- **Contrat futur** : les trois DELETE du seed **excluent les templates custom** — filtre par
  marqueur d'origine (§15 OQ-LAUNCH-A : `owner_user_id IS NULL` recommandé), appliqué aux
  trois niveaux (templates, template_exercises via jointure, rep_targets via jointure).
- **Garde obligatoire AVANT toute première publication** : le build wipe-guard
  (`LAUNCH_01`) précède strictement tout build de matérialisation (`LAUNCH_03`) — ordre
  non négociable dans la build queue.
- **Test obligatoire** : « un bump de version du seed **ne détruit jamais** un template
  custom » — fixture : template custom présent + bump de version + reseed → le custom
  survit intact (template + exercises + rep_targets), le système est reconstruit.
- **Aucune modification du seed dans cette spec** — le wipe-guard sera l'**unique**
  modification autorisée du seed, dans son build dédié, testée.

## 5. Slugs custom (contrat dur #2 — précisé)

- **Namespace réservé** : préfixe `up` + user id — aucun slug système existant ou futur ne
  commence par `up{digits}-` (vérifié : les 16 slugs système actuels n'y ressemblent pas ;
  la QA du build l'assertera).
- **Format recommandé** : `up{user_id}-{slug_base}-v{n}` (aligné parent OQ-CP-A + spec 04
  `slug_base`).
- **Collision impossible par construction** avec les slugs système ; contrainte `UNIQUE`
  existante de `workout_templates.slug` conservée.
- **Version immuable par publication** : un slug publié n'est **jamais réutilisé ni
  réécrit** ; v{n+1} = nouveau slug.
- **Ancien slug archivé, jamais réécrit** — l'historique des séances loggées sur v{n} reste
  résoluble par `template_slug_snapshot` pour toujours.

## 6. Matérialisation future (mapping)

| Source (spec 04) | Cible catalogue | Notes |
|---|---|---|
| `UserProgram` (version validée) | `WorkoutTemplate` | slug §5, `name` = title (+ suffixe version si utile UX), `kind` porté par les sessions (§ ci-dessous), marqueur custom (§15 OQ-LAUNCH-A), `catalog_section` custom (§9) |
| `UserProgramSession` | **un `WorkoutTemplate` par session** | le modèle existant = 1 template : 1 séance lançable (pas de conteneur multi-séances). Un programme de N sessions matérialise **N templates** partageant un préfixe de slug (`up{uid}-{base}-v{n}-s{position}` — détail exact tranché en review, OQ-LAUNCH-K implicite dans OQ-LAUNCH-E) ; le lien programme→templates vit côté `UserProgram*` |
| `UserProgramExercise` | `TemplateExercise` | `code` = slot figé (§8), `name` = `exercise_name` (nom EKB invariant → deviendra `exercise_name_snapshot`), `set_scheme`, `machine_slug`/`machine_family` si portés, `substitutes_json` V1 = vide ou dérivé EKB (OQ-LAUNCH-H) |
| `UserProgramRepTarget` | `RepTarget` | min/max/technique par set_index — **condition d'existence de l'overload** |
| `UserProgramQualityReview` | **rien** | reste trace côté `UserProgram*` — **jamais une source catalogue** (spec 03 §10) |

## 7. Contrats `session_builder` (non négociables)

- `instantiate_session()` **continue de recevoir un `WorkoutTemplate`** — la matérialisation
  produit des rows catalogue standard, donc **zéro modification de `session_builder` en V1**
  (Option C acceptée ⇒ **pas d'abstraction `ProgramDefinition` dans `session_builder`** ;
  `ProgramDefinition` reste l'interface interne génération→matérialisation, parent §11/§15).
- `template_slug_snapshot` **préserve l'historique** — figé à l'instanciation, résout la
  version exacte du programme pour toujours.
- `exercise_code_snapshot` / `exercise_name_snapshot` **restent cohérents** — copiés depuis
  `TemplateExercise.code`/`.name` matérialisés, comme pour le système.
- `template_exercise_id` **existe** (FK réelle vers la row matérialisée) — condition de
  l'overload (`build_overload_input_for_exercise` exige `se.template_exercise` non NULL).
- `rep_targets` **existent** — condition du set scheme prescrit et des cibles overload.

## 8. Codes exercice / slots (contrat dur #3 appliqué)

- Codes **`E1..En` figés par version publiée** — attribués à la matérialisation dans l'ordre
  des positions, jamais modifiés ensuite.
- **Réorganisation = nouvelle version** (nouveau cycle spec 04 §6) — jamais de re-code en
  place.
- **Continuité inter-version non promise V1** : « E2 de v2 » n'est pas garanti être « E2 de
  v1 » — même trade-off que le catalogue système entre versions de seed ; documenté, jamais
  masqué.
- **Historique étanche par `template_slug_snapshot`** : la garde d'identité existante
  (Sb_30.bugfix : même template + même code + même politique de substitution) fonctionne
  telle quelle — chaque version étant un slug distinct, **aucune contamination
  inter-versions** possible dans last_time/overload/history.
- **Aucune réécriture de snapshots passés** — interdit absolu (invariance historique,
  contrainte #1 du repo).

## 9. Filtres reco / librairie (contrat dur #4 — précisé)

- **Reco** : `recommendation._load_templates()` charge aujourd'hui tout sauf `archived` —
  le build des filtres **exclut les templates custom** du moteur de reco V1 (OQ-CP-C parent :
  réintégration éventuelle = décision V2 dédiée).
- **Librairie** : section **« Mes programmes »** séparée des sections système
  (`CATALOG_SECTIONS`), filtrée par owner — jamais mélangée à « Programmes principaux ».
- **Launcher système inchangé V1** (BRANCH_TREE hardcodé par slugs système = immunisé par
  construction ; entrée « Mes programmes » = OQ-LAUNCH-G).
- **`catalog_section` custom** : valeur réservée (`user`) ou flag d'origine — tranché en
  OQ-LAUNCH-A ; dans tous les cas les surfaces système filtrent.
- **Tests dédiés obligatoires** : absence de pollution — un template custom publié
  n'apparaît ni dans la reco, ni dans les sections système de la librairie, ni dans le
  launcher.

## 10. Publication / idempotence

- Publier un `UserProgram` en statut `validated` **crée la version matérialisée** (N
  templates + exercises + rep_targets) puis pose `published_template_id` + statut
  `published` + trace `quality_reviews` (spec 03 §9-C, spec 04 §7).
- **Idempotence** : relancer la même publication (même programme, même version) **ne
  duplique pas** — clé naturelle = slug versionné unique ; re-run détecte l'existant et
  converge (no-op ou complétion).
- **Édition après publication** → version suivante (spec 04 §6) ; la publication v{n+1}
  **archive** l'artefact v{n} (`catalog_section` archivée, invisible librairie, historique
  intact via snapshots + FK SET NULL).
- **Rollback en cas d'échec partiel** : à spécifier en build (`LAUNCH_03`) — exigence posée
  ici : soit transaction unique (tout-ou-rien), soit reprise idempotente ; **jamais** d'état
  publié à moitié visible (statut `published` posé en dernier).

## 11. Overload / history / analytics (héritage sans modification)

- **Overload fonctionne nativement** : FK `template_exercise` réelle + `rep_targets` réels
  (§7) — la politique de substitution et la garde d'identité existantes s'appliquent sans
  changement.
- **Stats keyées snapshots** (`last_time_by_exercise_code`, deltas) — héritent par slug
  versionné.
- **History** : `/history` et l'exercise history detail restent consultables (identité
  `(template_slug_snapshot, exercise_code_snapshot)`).
- **Export / KPIs** : aucun chemin parallèle requis (keyés snapshots).
- **Tests futurs bout-en-bout obligatoires** (`LAUNCH_06`) : publier → lancer → logger →
  vérifier last_time / overload hint / history / KPIs / export sur un programme custom réel.

## 12. Sécurité / isolation user

- Un user **ne peut lancer que ses propres templates custom** — `create_session` (ou sa
  garde amont) vérifie l'ownership du template custom résolu par slug ; les templates
  système restent lançables par tous (comportement actuel).
- **Programme non publié = non lançable** (les brouillons n'existent pas au catalogue).
- **Programme archivé** : invisible en librairie, **historique conservé** (séances passées
  intactes).
- **Pas de partage V1, pas de programme global user-created V1** (spec 04 §8).
- Tests d'isolation dédiés (pattern `test_auth_scope_isolation` / `test_ownership`).

## 13. Contraintes migrations / builds futurs

**Additive-only** (colonnes custom sur les tables catalogue = ADD COLUMN nullable ;
`owner_user_id` FK nullable — NULL = système) · **une migration par build** · **wipe-guard
avant publication** (ordre de la build queue, non négociable) · **filtres reco/librairie
dans le même build que la matérialisation** (`LAUNCH_03`+`LAUNCH_04` livrés avant tout
lancement réel ; aucun template custom publiable tant que les filtres ne sont pas verts) ·
**CI complète obligatoire** (models/services/session touchés ⇒ jamais de skip) · **tests
seed / reco / launch / overload / history** exigés build par build.

## 14. Non-goals

Pas de migration · pas de seed · pas de code · pas d'UI · pas de wizard (builds parent) ·
pas de scoring (spec 03) · pas de génération (parent §11) · pas de PR/merge · pas de deploy ·
pas de partage inter-user · pas de modification de `session_builder`/`overload_*`/`stats`/
`kpis` (l'héritage sans modification est précisément le critère de réussite).

## 15. Open questions

| OQ | Question | Position par défaut proposée |
|---|---|---|
| OQ-LAUNCH-A | `catalog_section='user'` vs flag `origin`/custom | **`owner_user_id` FK nullable (NULL = système) + `catalog_section='user'`** — le flag d'ownership porte la sécurité, la section porte l'affichage |
| OQ-LAUNCH-B | `owner_user_id` sur `WorkoutTemplate` seulement ou aussi `TemplateExercise` | **template seulement** (les enfants suivent par FK CASCADE ; le wipe-guard filtre par jointure) |
| OQ-LAUNCH-C | Idempotence de publication | clé = slug versionné unique ; re-run converge, jamais de doublon |
| OQ-LAUNCH-D | Table de versions dédiée ou `current_version` | `current_version` V1 (aligné OQ-PERS-C/D) ; table dédiée si multi-artefacts requis |
| OQ-LAUNCH-E | Continuité inter-version des slots + schéma de slug par session (`-s{position}`) | continuité non promise V1 ; format multi-sessions tranché en review |
| OQ-LAUNCH-F | Custom dans la reco : V2 ou jamais | **V2 au plus tôt**, décision dédiée avec ses propres gardes |
| OQ-LAUNCH-G | Launcher « Mes programmes » V1 ou librairie seulement | **librairie seulement V1** (aligné OQ-CP-I) |
| OQ-LAUNCH-H | `substitutes_json` des templates custom V1 | vide V1 (pas de substitution custom) ou dérivé EKB `variant_group` — tranché en review |
| OQ-LAUNCH-I | Archivage automatique des anciennes versions | **oui, à la publication v{n+1}** (quota 5 versions, spec 04 §9) |
| OQ-LAUNCH-J | Échec de publication à mi-chemin | transaction unique recommandée (SQLite le permet) ; statut `published` posé en dernier ; reprise idempotente en secours |
| OQ-LAUNCH-K | Droits d'accès sur template custom lancé | lancement filtré par ownership (§12) ; lecture du template custom par un tiers : interdite V1 |

## 16. Acceptance criteria (cette spec)

- [ ] Wipe-guard défini (danger chiffré, contrat de filtre, ordre de build, test obligatoire).
- [ ] Slugs définis (namespace, format, immuabilité, archivage).
- [ ] Matérialisation décrite (mapping 5 sources → catalogue, reviews jamais côté catalogue).
- [ ] Compatibilité `session_builder` définie (zéro modification V1, 5 contrats).
- [ ] Filtres reco/librairie définis + launcher inchangé + tests anti-pollution.
- [ ] Idempotence/rollback de publication cadrés ; sécurité/isolation définies.
- [ ] Tests futurs listés (seed, reco, launch, overload, history, bout-en-bout).
- [ ] Build toujours interdit ; registry/roadmap mis à jour.

## 17. Build queue proposée (aucune n'est ouverte par cette spec)

| Build | Objet | Gate |
|---|---|---|
| `Sb_CUSTOM_PROGRAM_LAUNCH_01` | **Seed wipe-guard + tests** (unique modification du seed, filtre custom aux 3 DELETE, test bump-survie) | spec 05 acceptée — **précède strictement tout le reste** |
| `Sb_CUSTOM_PROGRAM_LAUNCH_02` | Colonnes custom catalogue **additive-only** (`owner_user_id` nullable, section/index) | LAUNCH_01 |
| `Sb_CUSTOM_PROGRAM_LAUNCH_03` | **Materializer** service pur/idempotent (mapping §6, transaction, statut posé en dernier) | LAUNCH_02 + specs 04 builds persistence livrés |
| `Sb_CUSTOM_PROGRAM_LAUNCH_04` | **Filtres reco/librairie** (+ section « Mes programmes », tests anti-pollution) — livré avant tout lancement réel | LAUNCH_03 |
| `Sb_CUSTOM_PROGRAM_LAUNCH_05` | **Launch custom program smoke** (create_session ownership-gated, snapshots, page séance) | LAUNCH_04 |
| `Sb_CUSTOM_PROGRAM_LAUNCH_06` | **Overload/history end-to-end + dogfood** (publier → lancer → logger → vérifier last_time/overload/history/KPIs/export) | LAUNCH_05 |

---

*Spec draft — build, migrations, seed et code applicatif explicitement non autorisés.
Cette spec **clôt la spec queue du track** (01→05). Prochaine décision : human review de ce
document ; ensuite, toute ouverture de build (`Sb_CUSTOM_PROGRAM_*`) exige un GO/override
opérateur explicite, build par build, wipe-guard en premier.*
