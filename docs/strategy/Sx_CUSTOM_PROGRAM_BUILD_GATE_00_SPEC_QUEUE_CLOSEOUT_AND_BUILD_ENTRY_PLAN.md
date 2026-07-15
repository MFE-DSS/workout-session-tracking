# Sx_CUSTOM_PROGRAM_BUILD_GATE_00 — Spec Queue Closeout & Build Entry Plan

**Type :** BUILD GATE / CLOSEOUT / OPERATIONAL PLAN — docs-only
**Date :** 2026-07-15
**Statut :** ⚪ DRAFT OPENED — pending human review · **BUILD STILL FORBIDDEN**
**Track :** `Sx_CUSTOM_PROGRAM` — spec queue 01→05 ✅ **COMPLETE** (5/5 HUMAN REVIEW ACCEPTED)
**Branche :** `spec/sx-custom-program-01-intelligent-builder` (worktree isolé)
**Rôle :** convertir la spec queue acceptée en **plan d'entrée de build opérationnel** —
sans rien ouvrir. Ce document est la porte : tout build passe par elle, sur GO opérateur
séparé.

---

## 1. Verdict

- **Spec queue `Sx_CUSTOM_PROGRAM_01→05` : COMPLETE** — les 5 specs sont HUMAN REVIEW
  ACCEPTED (01 architecture, 02 EKB, 03 scoring, 04 persistence, 05 instantiation compat),
  toutes poussées sur `origin/spec/sx-custom-program-01-intelligent-builder`.
- **Build toujours NOT AUTHORIZED** — aucun `Sb_CUSTOM_PROGRAM_*` n'est ouvert par ce gate.
- **Prochaine frontière = décision opérateur séparée**, build par build, à commencer
  obligatoirement par `LAUNCH_01` (§4-5).

## 2. Architecture verrouillée (rappel exécutif)

| Décision | Source |
|---|---|
| **Option C hybride** (A rejetée naïve, B repli documenté) | spec 01 §8-9 |
| **`UserProgram*` = source de vérité d'édition** (5 tables, statuts, quotas, soft delete) | spec 04 |
| **`WorkoutTemplate` custom = artefact de publication** (matérialisation 1 session → 1 template) | spec 05 §6 |
| **Versions immuables** — édition post-publication = nouveau cycle, jamais de mutation en place | specs 04 §6-7 / 05 §3 |
| **Slugs namespacés** `up{user_id}-{slug_base}-v{n}`, collision système impossible | spec 05 §5 |
| **Scoring explicable** — moteur pur/déterministe/versionné, grade hybride plafonné, jamais opaque, C publiable avec avertissement | spec 03 |
| **EKB structurée** — noms historiques invariants + `variant_group`, taxonomie 18 champs, JSON canonique d'abord | spec 02 |
| **Pas de chemin parallèle de lancement** — `instantiate_session(WorkoutTemplate)` inchangé, overload/history/stats hérités | spec 05 §2/§7/§11 |

## 3. Ce qui n'est PAS encore buildé (état zéro exhaustif)

**Aucune table** `user_program*` · **aucune migration** · **aucun seed** (ni EKB, ni
wipe-guard) · **aucune data** (`exercise_knowledge_base.json` inexistant ; gap 52/103
documenté, non corrigé) · **aucun service** (ni repository CRUD, ni materializer) · **aucun
wizard** (aucun écran, aucune route) · **aucun scoring engine** (`PROGRAM_QUALITY_SCORING_VERSION`
n'existe pas dans le code) · **aucun materializer**. Le repo applicatif est **strictement
identique** à l'état pré-track sur ce périmètre.

## 4. Ordre de build recommandé

| # | Build | Objet | Spec source |
|---|---|---|---|
| 1 | **`Sb_CUSTOM_PROGRAM_LAUNCH_01` — Seed Wipe-Guard** | sécurité seed + tests bump-survie | 05 §4 |
| 2 | `Sb_CUSTOM_PROGRAM_PERSISTENCE_01` — table `user_programs` | migration additive 1/3 | 04 §5 |
| 3 | `Sb_CUSTOM_PROGRAM_PERSISTENCE_02` — sessions/exercises/rep_targets | migrations additives | 04 §5 |
| 4 | `Sb_CUSTOM_PROGRAM_PERSISTENCE_03` — quality_reviews | migration additive | 04 §5 / 03 §9 |
| 5 | `Sb_CUSTOM_PROGRAM_EKB_01→04` | audit QA → JSON canonique 103 entrées → QA script → seed DB optionnel | 02 §14 |
| 6 | `Sb_CUSTOM_PROGRAM_SCORING_01→04` | moteur pur → microcopy → persistance trace → intégration | 03 §15 |
| 7 | `Sb_CUSTOM_PROGRAM_WIZARD_01+` | écrans SSR, draft CRUD branché, édition par cartes | 01 §6 |
| 8 | `Sb_CUSTOM_PROGRAM_LAUNCH_02+` | colonnes catalogue → materializer → filtres → launch smoke → e2e dogfood | 05 §17 |

Chaque build : branche dédiée, une migration max, review-gated, CI complète, GO explicite.
L'ordre 2-6 peut s'entrelacer (persistence ∥ EKB ∥ scoring sont indépendants) ; **le #1 ne
se négocie pas** et le #8 exige tout le reste.

## 5. Pourquoi `LAUNCH_01` d'abord

- **Le risque critique du track est le wipe par `seed.py`** : `seed_reference_split()`
  supprime intégralement les 3 tables catalogue à chaque bump de version — toute row custom
  serait détruite (spec 05 §4, audit chiffré spec 01 §7).
- **La garde doit exister avant toute possibilité de créer des templates custom** — même en
  test, même en dogfood ; sinon une fenêtre de destruction silencieuse existe.
- **C'est un build de sécurité, pas un build produit** — aucune valeur utilisateur directe,
  uniquement l'invariant « le seed ne détruit jamais du custom ».
- **Périmètre petit, testable, isolé** : un filtre sur 3 DELETE + une batterie de tests —
  le build idéal pour ouvrir un track métier en confiance.

## 6. Pré-périmètre futur de `LAUNCH_01` (cadrage, non ouvert)

- **Audit `app/services/seed.py`** (124 lignes) — l'unique fichier de code du périmètre.
- **Identifier le DELETE destructif** : `seed_reference_split()` l.58-60
  (`delete(RepTarget)`, `delete(TemplateExercise)`, `delete(WorkoutTemplate)` — sans filtre).
- **Protéger les futurs templates custom** : filtre d'origine aux 3 niveaux
  (`owner_user_id IS NULL` recommandé — OQ-LAUNCH-A/B ; les enfants par jointure).
  Note d'ordonnancement : si le marqueur retenu exige la colonne `owner_user_id`, `LAUNCH_01`
  embarque cette unique migration additive-only (fusion partielle avec `LAUNCH_02`) ou
  s'appuie sur un critère sans schéma (préfixe slug `up%`) — **tranché à l'ouverture du
  build**, jamais improvisé en cours.
- **Tests futurs obligatoires** :
  1. un template custom **survit** à un reseed (bump de version) ;
  2. ses `TemplateExercise` custom **survivent** ;
  3. ses `RepTarget` custom **survivent** ;
  4. les templates **système restent intégralement reconstruits** (16 templates, contenu
     conforme au JSON) ;
  5. **aucun custom ne pollue** la reco ni le catalogue système (pré-assertion des filtres
     spec 05 §9, au niveau atteignable par ce build).

## 7. Branching plan futur

- **Ne pas coder sur la branche spec** (`spec/sx-custom-program-01-intelligent-builder`
  reste docs-only, à jamais).
- Future branche dédiée : **`sb/custom-program-launch-01-seed-wipe-guard`**.
- **Base : canonique propre et à jour** (fetch + vérification 0 divergence avant création).
- **Rebase obligatoire** avant PR/CI finale.
- **CI complète obligatoire** (seed = code partagé ⇒ jamais de skip).
- **Aucune concurrence avec UI/Auren** : worktree dédié, vérification qu'aucun agent ne
  travaille sur `seed.py` au moment de l'ouverture (§8).

## 8. Go / No-Go criteria pour autoriser `LAUNCH_01`

| Critère | Exigence |
|---|---|
| Canonique | **clean**, 0 divergence local/origin au préflight |
| Concurrence | **aucun autre agent sur `seed.py`** (vérification explicite au préflight, leçon des collisions du 2026-07-15) |
| Périmètre | **seed + tests + docs uniquement** — tout autre fichier = STOP |
| Migration | **aucune** (sauf décision explicite `owner_user_id`, §6 — alors une seule, additive-only) |
| Rollback | **mental clair** : revert du commit = retour exact à l'état antérieur (pas d'état intermédiaire) |
| check_scope | attendu **shared_code** si `seed.py` touché — full sweep local assumé |
| CI | **3/3 obligatoire** avant toute review |

**No-Go** si l'un manque : rapporter et attendre.

## 9. Risques

| Risque | Parade |
|---|---|
| Casse du seed système (les 16 templates ne se reconstruisent plus) | test #4 §6 + full sweep + CI ; le filtre n'exclut que le custom, jamais le système |
| Cascade delete involontaire (enfants custom supprimés par jointure mal filtrée) | tests #2-3 §6 sur l'arbre complet |
| Custom rows orphelines (template custom détaché de son `UserProgram`) | hors périmètre LAUNCH_01 (aucun custom ne peut encore exister) ; contrat repris par le materializer |
| Confusion `catalog_section='user'` vs futur flag | OQ-LAUNCH-A tranchée **à l'ouverture** du build, documentée dans son rapport |
| Tests insuffisants (garde crue vérifiée mais non prouvée) | matrice §6 minimale obligatoire + fixture bump réel de version |

## 10. Décision finale

| Élément | État |
|---|---|
| **`Sx_CUSTOM_PROGRAM_BUILD_GATE_00`** | ⚪ **DRAFT OPENED** (ce document) |
| Build | ❌ **STILL FORBIDDEN** — ce gate n'ouvre rien |
| **Prochaine commande possible, séparée** | **`GO BUILD Sb_CUSTOM_PROGRAM_LAUNCH_01`** (opérateur uniquement, critères §8 vérifiés au préflight) |

## Non-goals

Pas d'ouverture de `LAUNCH_01` ni d'aucun build · pas de code `app/` ni `tests/` · pas de
`data/` · pas de migration · pas de seed · pas de template/CSS/JS · pas d'UI/Auren · pas de
PR/merge · pas de deploy · pas de modification du repo principal.

---

*Build gate docs-only. La spec queue est close ; la porte de build est définie et fermée.
Elle ne s'ouvre que par GO opérateur explicite, `LAUNCH_01` en premier.*
