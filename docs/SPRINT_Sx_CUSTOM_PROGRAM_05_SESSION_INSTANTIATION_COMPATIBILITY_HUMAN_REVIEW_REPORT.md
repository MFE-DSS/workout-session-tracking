# Human Review — Sx_CUSTOM_PROGRAM_05 Session Instantiation Compatibility Spec

**Verdict** : ✅ **HUMAN REVIEW ACCEPTED / SPEC ONLY / BUILD NOT AUTHORIZED**
**Date** : 2026-07-15
**Type** : revue humaine — docs-only (aucun code touché par cette revue ni par la spec)
**Track** : `Sx_CUSTOM_PROGRAM` (01 ✅ · 02 ✅ · 03 ✅ · 04 ✅ — **05 = ce document, spec
fille 4/4 : cette acceptance CLÔT la spec queue 01→05**)
**Branche** : `spec/sx-custom-program-01-intelligent-builder` (worktree isolé, synchronisée
origin, spec commit `b61f4c9`)
**Spec** : [`Sx_CUSTOM_PROGRAM_05_SESSION_INSTANTIATION_COMPATIBILITY_SPEC.md`](strategy/Sx_CUSTOM_PROGRAM_05_SESSION_INSTANTIATION_COMPATIBILITY_SPEC.md)

---

## 1. Verdict

**Sx_CUSTOM_PROGRAM_05 est acceptée.** Les contrats de compatibilité entre `UserProgram*` et
le moteur de séance existant sont actés. Le statut reste **SPEC ONLY** : **aucune migration,
aucun code, aucun seed, aucune data modifiée** — toute la build queue (`LAUNCH_*` incluse)
reste NOT AUTHORIZED.

## 2. Scope accepté

Compatibilité `UserProgram*` ↔ moteur de séance existant · publication future comme artefact
`WorkoutTemplate` custom protégé · **préservation de `session_builder`** (zéro modification
V1) · **préservation overload / history / stats / KPIs** (héritage sans modification =
critère de réussite) · **pas de chemin parallèle de lancement V1** (le launch passe par le
chemin catalogue standard).

## 3. Option C confirmée (définitivement, à l'échelle du track)

`UserProgram*` = source de vérité d'édition · `WorkoutTemplate` custom = artefact de
publication · édition post-publication = **nouvelle version** · **versions publiées
immuables** · **jamais de mutation en place d'un template publié**.

## 4. Wipe-guard seed (accepté comme contrat critique #1)

- **Danger identifié comme critique** : `seed_reference_split()` (`seed.py:58-60`) =
  DELETE intégral sans filtre des 3 tables catalogue à chaque bump de version — toute row
  custom serait détruite.
- **Garde obligatoire AVANT toute première publication** — ordre non négociable.
- **Test obligatoire** : un bump de version seed **ne détruit jamais** un template custom
  (fixture bump-survie : custom intact, système reconstruit).
- **Aucune modification du seed dans cette spec** — le wipe-guard sera l'unique modification
  du seed, dans son build dédié.
- **`Sb_CUSTOM_PROGRAM_LAUNCH_01` devra commencer par ce sujet** — premier build candidat du
  track, strictement antérieur à tout le reste.

## 5. Slugs custom (accepté)

Namespace réservé `up{user_id}-…` · format **`up{user_id}-{slug_base}-v{n}`** · collision
système **impossible par construction** (+ assertion QA au build) · version **immuable par
publication** (slug jamais réutilisé ni réécrit) · **ancien slug archivé, jamais réécrit**
(l'historique reste résoluble pour toujours via `template_slug_snapshot`).

## 6. Matérialisation future (mapping accepté)

`UserProgram` (version validée) → `WorkoutTemplate` · **1 `UserProgramSession` → 1
`WorkoutTemplate`** (le modèle existant = 1 template : 1 séance lançable ; N sessions =
N templates liés côté `UserProgram*` ; schéma de slug multi-sessions = OQ-LAUNCH-E) ·
`UserProgramExercise` → `TemplateExercise` (codes figés §8) · `UserProgramRepTarget` →
`RepTarget` (condition d'existence de l'overload) · **`UserProgramQualityReview` reste côté
user program — jamais une source catalogue** · **publication idempotente à spécifier en
build** (clé = slug versionné, statut posé en dernier).

## 7. Contrats `session_builder` (acceptés, non négociables)

`instantiate_session()` **continue de recevoir un `WorkoutTemplate`** · snapshots
(`template_slug_snapshot`, `exercise_code_snapshot`, `exercise_name_snapshot`) **préservent
l'historique** · `template_exercise_id` **existe** (condition overload) · `rep_targets`
**existent** (condition set scheme + cibles) · **pas d'abstraction `ProgramDefinition` dans
`session_builder` en V1** (`ProgramDefinition` reste l'interface interne
génération→matérialisation).

## 8. Codes exercice / slots (acceptés)

Codes **`E1..En` figés par version publiée** · réorganisation = **nouvelle version** ·
**continuité inter-version non promise V1** (documentée, jamais masquée — même trade-off que
le catalogue système entre versions de seed) · **historique étanche par
`template_slug_snapshot`** (la garde d'identité Sb_30.bugfix hérite sans modification :
aucune contamination inter-versions possible dans last_time/overload/history) · **aucune
réécriture de snapshots passés** (interdit absolu).

## 9. Filtres reco / librairie (acceptés comme contrat dur #4)

La reco **ne doit pas ingérer silencieusement** les templates custom (exclusion V1 ;
réintégration = décision V2 dédiée) · librairie : section **« Mes programmes » séparée**,
jamais mélangée aux sections système · **launcher système inchangé V1** (immunisé par
construction) · **`catalog_section='user'` ou équivalent à confirmer** (OQ-LAUNCH-A, position
par défaut : `owner_user_id` FK nullable pour la sécurité + section pour l'affichage) ·
**tests anti-pollution obligatoires** (reco, sections système, launcher).

## 10. Publication / idempotence (accepté)

Publier un `validated` **crée une version matérialisée** · relancer la même publication **ne
duplique pas** (converge) · édition après publication → **version suivante** · **ancien
template custom archivé** automatiquement à la publication v{n+1} · **rollback logique en cas
d'échec partiel à spécifier en build** (`LAUNCH_03` ; exigence posée : transaction unique ou
reprise idempotente, jamais d'état publié à moitié visible).

## 11. Overload / history / analytics (accepté)

Overload **fonctionne nativement** via `template_exercise` + `rep_targets` · stats **restent
keyées snapshots** · history / export / KPIs **sans chemin parallèle** · **tests futurs
bout-en-bout obligatoires** (`LAUNCH_06` : publier → lancer → logger → vérifier
last_time/overload/history/KPIs/export).

## 12. Sécurité / isolation utilisateur (accepté)

Un utilisateur **ne peut lancer que ses templates custom** (ownership-gated) · **programme
non publié = non lançable** · **programme archivé** : invisible, historique conservé ·
**pas de partage V1** · **pas de programme global user-created V1** · tests d'isolation
dédiés (pattern `test_ownership`/`test_auth_scope_isolation`).

## 13. Build queue verrouillée

| Build | Statut |
|---|---|
| **`Sb_CUSTOM_PROGRAM_LAUNCH_01` — seed wipe-guard + tests** | 🔵 **FIRST BUILD CANDIDATE, NOT OPENED** — obligatoire en premier si un build est autorisé plus tard |
| `LAUNCH_02` → `LAUNCH_06` | ❌ fermés (ordre de la spec §17 contraignant) |
| `PERSISTENCE_*` / `EKB_*` / `SCORING_*` / `Sb_CUSTOM_PROGRAM_01→07` | ❌ fermés |
| **Aucun build n'est autorisé par cette review.** | — |

## 14. Risques acceptés (avec mitigations actées)

Seed wipe (wipe-guard premier + test bump-survie) · pollution reco/librairie (filtres +
tests anti-pollution dans le même lot que la matérialisation) · mutation accidentelle d'un
template publié (nouveau cycle obligatoire, immuabilité) · collisions de slug (namespace par
construction + QA) · idempotence publication (clé slug, convergence) · échec partiel de
matérialisation (transaction/reprise, statut posé en dernier) · fuite inter-user
(ownership-gated + tests) · surcharge de templates custom (quotas spec 04 + archivage auto).

## 15. Open questions (OQ-LAUNCH-A → OQ-LAUNCH-K)

Statut : **à trancher en décision de build / review des builds** — `catalog_section='user'`
vs flag origin · `owner_user_id` template seulement (défaut) ou aussi exercises · idempotence
(clé slug, défaut) · table de versions vs `current_version` (défaut colonne) · continuité
inter-version des slots (non promise) + schéma slug multi-sessions · custom dans reco V2 ou
jamais · launcher « Mes programmes » V1 ou librairie seulement (défaut librairie) · archivage
auto des anciennes versions (défaut oui) · échec à mi-chemin (défaut transaction unique) ·
droits d'accès sur template custom lancé (défaut : lecture tierce interdite V1).

## 16. Décision finale de spec queue

| Élément | Décision |
|---|---|
| **`Sx_CUSTOM_PROGRAM_01 → 05`** | ✅ **SPEC QUEUE COMPLETE** — les 5 specs sont HUMAN REVIEW ACCEPTED |
| Build | ❌ **remains NOT AUTHORIZED** |
| **Prochaine frontière** | **décision opérateur séparée de build** (GO/override explicite, build par build) |
| Premier build potentiel si autorisé | **`Sb_CUSTOM_PROGRAM_LAUNCH_01 — seed wipe-guard`** (obligatoirement en premier) |

---

## Verdict

**Verdict :** ✅ **Sx_CUSTOM_PROGRAM_05 Session Instantiation Compatibility Spec — HUMAN
REVIEW ACCEPTED / SPEC ONLY / BUILD NOT AUTHORIZED.**

Les contrats de lançabilité sont actés : wipe-guard seed critique en premier, slugs
namespacés immuables, matérialisation 1 session → 1 template (reviews jamais côté catalogue),
`session_builder` inchangé V1, codes figés par version, historique étanche par slug
versionné, filtres reco/librairie + tests anti-pollution, publication idempotente, lancement
ownership-gated. **La spec queue `Sx_CUSTOM_PROGRAM` 01→05 est COMPLETE.** La prochaine
frontière du track est une décision de build opérateur distincte — premier candidat :
`Sb_CUSTOM_PROGRAM_LAUNCH_01` (wipe-guard). Aucun code touché ; repo principal UI non touché.
