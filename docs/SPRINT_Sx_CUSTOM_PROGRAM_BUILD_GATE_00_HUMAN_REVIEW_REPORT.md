# Human Review — Sx_CUSTOM_PROGRAM_BUILD_GATE_00 Spec Queue Closeout & Build Entry Plan

**Verdict** : ✅ **HUMAN REVIEW ACCEPTED / BUILD DECISION PENDING / LAUNCH_01 NOT OPENED**
**Date** : 2026-07-15
**Type** : revue humaine — docs-only (aucun code touché par cette revue ni par le gate)
**Track** : `Sx_CUSTOM_PROGRAM` — spec queue 01→05 ✅ COMPLETE ; ce gate en est la porte de
sortie opérationnelle
**Branche** : `spec/sx-custom-program-01-intelligent-builder` (worktree isolé, synchronisée
origin, gate commit `8df0af6`)
**Gate** : [`Sx_CUSTOM_PROGRAM_BUILD_GATE_00_SPEC_QUEUE_CLOSEOUT_AND_BUILD_ENTRY_PLAN.md`](strategy/Sx_CUSTOM_PROGRAM_BUILD_GATE_00_SPEC_QUEUE_CLOSEOUT_AND_BUILD_ENTRY_PLAN.md)

---

## 1. Verdict

- ✅ **HUMAN REVIEW ACCEPTED** — le plan d'entrée de build est acté comme gouvernance du track.
- **Spec queue `Sx_CUSTOM_PROGRAM_01→05` confirmée COMPLETE** (5/5 ACCEPTED, poussées).
- **Build toujours NOT AUTHORIZED** — cette review n'ouvre rien.
- **Prochaine frontière = décision opérateur séparée** (`GO BUILD Sb_CUSTOM_PROGRAM_LAUNCH_01`),
  soumise aux Go/No-Go criteria §5.

## 2. Architecture validée (verrouillée à l'échelle du track)

Option C hybride · `UserProgram*` = source de vérité d'édition · `WorkoutTemplate` custom =
artefact de publication · versions publiées **immuables** (édition = nouveau cycle) · slugs
**namespacés** `up{user_id}-{slug_base}-v{n}` · **EKB structurée** (noms historiques
invariants + taxonomie 18 champs) · **scoring explicable** (moteur pur/déterministe/versionné,
jamais opaque) · **pas de chemin parallèle de lancement** (`instantiate_session(WorkoutTemplate)`
inchangé, overload/history/stats hérités sans modification).

## 3. Build order accepté

1. **`Sb_CUSTOM_PROGRAM_LAUNCH_01 — Seed Wipe-Guard` — premier, obligatoire, non négociable** ;
2. `PERSISTENCE_01→03` (tables, une migration additive par build) ;
3. `EKB_01→04` (audit QA → JSON canonique → QA script → seed optionnel gaté) ;
4. `SCORING_01→04` (moteur pur → microcopy → trace → intégration) ;
5. `WIZARD_01+` (écrans SSR, édition par cartes) ;
6. `LAUNCH_02+` (colonnes catalogue → materializer → filtres → smoke → e2e dogfood).

Persistence ∥ EKB ∥ scoring peuvent s'entrelacer après le #1 ; le #6 exige tout le reste.
**Aucun build n'est ouvert par cette review** — chaque build = branche dédiée, GO explicite,
review-gated, CI complète.

## 4. Pourquoi `LAUNCH_01` d'abord (accepté)

Le **seed wipe est le risque critique** du track (`seed_reference_split()` : DELETE intégral
sans filtre des 3 tables catalogue à chaque bump de version) · **la garde doit précéder toute
création de template custom** (même en test/dogfood — sinon fenêtre de destruction
silencieuse) · **build de sécurité, pas build produit** (aucune valeur utilisateur directe,
un invariant) · **périmètre petit, testable, isolé** (un filtre sur 3 DELETE + tests).

## 5. Go / No-Go criteria acceptés (préflight obligatoire de LAUNCH_01)

| Critère | Exigence |
|---|---|
| Canonique | clean, 0 divergence local/origin |
| Concurrence | **aucun agent sur `seed.py`** (vérification explicite — leçon des collisions du 2026-07-15) |
| Branche | build **dédiée** (`sb/custom-program-launch-01-seed-wipe-guard`) |
| Périmètre | **seed + tests + docs uniquement** — tout autre fichier = STOP |
| Migration | **aucune** (le choix du marqueur custom pouvant l'exiger = STOP explicite, §6) |
| CI | **complète 3/3 obligatoire** |
| check_scope | **`shared_code` probable** si `seed.py` touché — full sweep assumé |
| Rollback | **mental clair** : revert du commit = état antérieur exact |

**No-Go si l'un manque** : rapporter et attendre.

## 6. Pré-périmètre `LAUNCH_01` (accepté)

Audit `app/services/seed.py` (124 l.) · identifier le DELETE destructif (l.58-60) · protéger
les futurs templates custom (filtre d'origine aux 3 niveaux, enfants par jointure) · **tests
obligatoires** : survie template custom au reseed · survie `TemplateExercise` custom · survie
`RepTarget` custom · **reconstruction intégrale des templates système** · anti-pollution
catalogue/reco (au niveau atteignable par ce build) · **aucun schema change sauf STOP
explicite** — si le marqueur retenu (OQ-LAUNCH-A/B : `owner_user_id` vs préfixe slug `up%`)
exige une colonne, la décision est tranchée à l'ouverture du build avec l'opérateur, jamais
improvisée en cours.

## 7. Branching (accepté)

**Jamais de code sur la branche spec** (elle reste docs-only à perpétuité) · future branche
build dédiée : **`sb/custom-program-launch-01-seed-wipe-guard`** · base : **canonique propre
et à jour** (fetch + 0 divergence au préflight) · **rebase obligatoire** avant CI finale ·
**aucune concurrence UI/Auren** (worktree dédié, vérification seed.py §5).

## 8. Invariants vérifiés (cette revue et le gate)

no `app/` · no `tests/` · no `data/` · no migrations · no seed · no templates/CSS/JS · no
repo principal · no build · no deploy · aucune branche build créée · diff du gate = 3
fichiers docs (+156) · `check_spec_protocol` PASS · `check_scope` DOCS.

## 9. Décision finale

| Élément | Décision |
|---|---|
| **Build gate** | ✅ **ACCEPTED** — gouvernance de build du track actée |
| **`Sb_CUSTOM_PROGRAM_LAUNCH_01`** | reste **NOT OPENED** (FIRST BUILD CANDIDATE) |
| **Prochaine commande possible, séparée** | **`GO BUILD Sb_CUSTOM_PROGRAM_LAUNCH_01`** — opérateur uniquement ; déclenche le préflight Go/No-Go §5 avant toute ligne de code |
| Tout le reste (`Sb_*`, migrations, seed, data, app code) | ❌ interdit sans override explicite |

---

## Verdict

**Verdict :** ✅ **Sx_CUSTOM_PROGRAM_BUILD_GATE_00 — HUMAN REVIEW ACCEPTED / BUILD DECISION
PENDING / LAUNCH_01 NOT OPENED.**

La spec queue 01→05 est confirmée COMPLETE et convertie en plan de build gouverné : ordre
contraignant (wipe-guard d'abord), Go/No-Go criteria préflight, branching isolé, pré-périmètre
LAUNCH_01 cadré avec ses 5 tests obligatoires. **Rien n'est buildé, rien n'est ouvert** — la
porte existe, elle est fermée, et seule une commande opérateur séparée
(`GO BUILD Sb_CUSTOM_PROGRAM_LAUNCH_01`) peut l'ouvrir. Aucun code touché ; repo principal
UI non touché.
