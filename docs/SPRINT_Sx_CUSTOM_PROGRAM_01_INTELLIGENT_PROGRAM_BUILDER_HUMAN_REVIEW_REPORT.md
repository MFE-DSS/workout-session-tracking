# Human Review — Sx_CUSTOM_PROGRAM_01 Intelligent Program Builder Spec

**Verdict** : ✅ **HUMAN REVIEW ACCEPTED / SPEC ONLY / BUILD NOT AUTHORIZED**
**Date** : 2026-07-15
**Type** : revue humaine — docs-only (aucun code touché par cette revue ni par la spec)
**Track** : `Sx_CUSTOM_PROGRAM` — FUTURE PRODUCT TRACK, parallèle au cycle UI/Auren
**Branche** : `spec/sx-custom-program-01-intelligent-builder` (worktree isolé
`workout-session-tracking-custom`), **rebasée sans conflit** sur la canonique avant revue
(spec commit `61258ab` → `425cce7` post-rebase)
**Spec** : [`Sx_CUSTOM_PROGRAM_01_INTELLIGENT_PROGRAM_BUILDER_SPEC.md`](strategy/Sx_CUSTOM_PROGRAM_01_INTELLIGENT_PROGRAM_BUILDER_SPEC.md)

---

## 1. Verdict

**HUMAN REVIEW ACCEPTED — SPEC ONLY.** La spec est acceptée comme direction produit et
architecture cible. **Rien n'est autorisé au build** : build, migrations, seed, code `app/`,
`tests/`, `data/`, templates, CSS, JS restent **explicitement interdits** tant qu'un GO build
dédié n'est pas donné, spec fille par spec fille.

## 2. Scope accepté

- **Custom Program Builder intelligent** — wizard guidé (durée/objectif/style/focus/matériel),
  proposition automatique déterministe, édition par cartes, validation, sauvegarde,
  réutilisation depuis la librairie.
- **Exercise Knowledge Base (EKB)** — catalogue structuré exercices/variantes fines/machines/
  patterns/muscles, consolidant le socle existant (Sx_32 `BodyZone`/`Muscle`/
  `ExerciseMuscleMapping`, `exercise_properties.json` Sb_22a, ponts inter-patterns).
- **Program Quality Scoring A/B/C** — 8 sous-scores explicables + alertes + corrections,
  4 régimes de vérité distingués (théorie générale / profil / historique réel / données
  manquantes), jamais présenté comme vérité scientifique.
- **Option C hybride** comme modèle de persistance cible (§3).
- **Branching and Integration Plan** (spec §16) — accepté comme contraignant.

## 3. Architecture validée

| Décision | Statut |
|---|---|
| **Option C hybride** : drafts `UserProgram*` isolés → publication matérialisée en `WorkoutTemplate` custom protégé (pipeline `session_builder`/overload/history intact, zéro duplication) | ✅ **acceptée comme direction cible** |
| Option A naïve (extension directe `WorkoutTemplate`) | ❌ **rejetée** (wipe par le seed `DELETE` sans filtre + pollution reco/librairie + namespace partagé) |
| Option B (tables séparées pures) | 📎 **repli documenté** (coût : abstraction `ProgramDefinition` + généralisation `overload_inputs`) |
| **Wipe-guard seed** livré + testé **avant toute matérialisation** | ✅ contrat dur #1 — obligatoire |
| **Slugs custom namespacés** (`up{user_id}-{slug}-v{n}`, format = OQ-CP-A) | ✅ contrat dur #2 |
| **Versions publiées immuables** (éditer = nouvelle version, l'ancienne archive ; protège l'identité `(template_slug_snapshot, exercise_code_snapshot)`) | ✅ contrat dur #3 |
| **Reco / librairie filtrées** (templates custom hors moteur de reco V1, section librairie dédiée) | ✅ contrat dur #4 |

## 4. Décisions produit acceptées

- Wizard **SSR / no-JS fallback** (une décision par écran, Auren Terminal).
- **Génération déterministe** : fonction pure `(wizard_answers, EKB, seed) → ProgramDefinition`,
  reproductible, explicable slot par slot.
- **Scoring explicable** : sous-scores et alertes d'abord, la lettre A/B/C n'est qu'un résumé —
  jamais un score opaque (leçon `/physique`).
- **Pas de LLM comme source de vérité** — une éventuelle couche suggestions serait une spec
  séparée, jamais autoritaire.
- **Aucun claim médical** — pas de branche blessure/pathologie, pas de promesse hormonale,
  pas d'échec systématique prescrit.
- **Grade C publiable avec avertissement** (liberté utilisateur) — accepté en principe,
  **à confirmer dans la spec fille** de scoring (`Sx_CUSTOM_PROGRAM_03`, OQ-CP-J).

## 5. Open questions (OQ-CP-A → OQ-CP-J)

Statut : **acceptées comme questions à instruire dans les specs filles** — ce ne sont **pas**
des décisions build finales.

| OQ | Sujet | Position par défaut (non finale) |
|---|---|---|
| OQ-CP-A | Format namespace slug custom | `up{user_id}-{slug}-v{n}` |
| OQ-CP-B | Continuité d'historique inter-versions | non promise V1, étanchéité par version |
| OQ-CP-C | Programmes custom dans le moteur de reco | non en V1, rouverte en V2 |
| OQ-CP-D | Stockage EKB | JSON versionné + seed DB (pipeline existant) |
| OQ-CP-E | Persistance du scoring | à la volée + trace par version |
| OQ-CP-F | Quota programmes/versions par user | quota simple V1 |
| OQ-CP-G | Cardio dans le wizard V1 | 1 bloc LISS optionnel |
| OQ-CP-H | Couche suggestions LLM | hors track, spec séparée, jamais source de vérité |
| OQ-CP-I | Entrée launcher « Mes programmes » | librairie seulement V1 |
| OQ-CP-J | Publication d'un programme grade C | autorisée avec avertissement |

## 6. Branching / multi-agent

- Track **isolé dans un worktree séparé** (`workout-session-tracking-custom`) — **aucune
  concurrence** avec le chantier UI (`Sb_UI_10.4b` et suivants), **aucune modification du repo
  principal** depuis ce worktree.
- **Rebase obligatoire avant chaque PR/build** — appliqué dès cette revue : rebase sans conflit
  sur la canonique (post-`bbfbe32`), diff strictement limité aux 3 fichiers docs du track.
- Futures branches build **petites et dédiées** (une par `Sb_CUSTOM_PROGRAM_xx`), une migration
  additive-only isolée par build, CI complète pour tout build touchant models/services/session.

## 7. Queue suivante

| Élément | Statut |
|---|---|
| **`Sx_CUSTOM_PROGRAM_02` — Exercise Knowledge Base Spec** | 🔵 **prochain sprint autorisé (SPEC ONLY, sur GO)** |
| `Sx_CUSTOM_PROGRAM_03` → `05` (Scoring / Persistence / Instantiation Compat) | ⚪ après 02, dans l'ordre |
| `Sb_CUSTOM_PROGRAM_01` → `07` (builds) | ❌ **NOT AUTHORIZED** |
| Migrations | ❌ **aucune autorisée** |
| Seed | ❌ **aucun autorisé** (wipe-guard = futur build dédié, gaté) |

## 8. Invariants vérifiés (cette revue et la spec)

no `app/` · no `tests/` · no `data/` · no `migrations/` · no seed · no templates · no CSS/JS ·
no deploy · no build — le diff de la branche vs canonique = **3 fichiers docs uniquement**
(spec +567, registry +9, roadmap +15). Repo principal (worktree UI dirty) **non touché**.

## 9. Risques acceptés (documentés spec §17, R1-R10)

- **Wipe seed** (R1, critique) — mitigé par le contrat wipe-guard antérieur à toute matérialisation.
- **Pollution reco/librairie** (R2) — filtres livrés dans le même build que la matérialisation.
- **Identité historique** (R3) — versions immuables, nouveau slug par version.
- **Score A/B/C perçu comme vérité scientifique** (R5) — sous-scores d'abord, microcopy
  « indicatif », régimes de vérité affichés.
- **Collision d'agents parallèles** (R7) — worktree isolé, rebase avant PR, ce track = SPEC ONLY
  pour tout agent tiers.

## 10. Décision

| Élément | Décision |
|---|---|
| **`Sx_CUSTOM_PROGRAM_01`** | ✅ **ACCEPTED** (spec direction + architecture Option C) |
| **Next** | `Sx_CUSTOM_PROGRAM_02 — Exercise Knowledge Base Spec` (SPEC ONLY, sur GO explicite) |
| **Build** | ❌ **remains NOT AUTHORIZED** |

---

## Verdict

**Verdict :** ✅ **Sx_CUSTOM_PROGRAM_01 — HUMAN REVIEW ACCEPTED / SPEC ONLY / BUILD NOT
AUTHORIZED.** La direction produit (builder 3 couches), l'architecture cible (Option C hybride
avec 4 contrats durs) et le plan de branching multi-agent sont actés. Les 10 OQ restent des
questions de specs filles. Prochaine étape : `Sx_CUSTOM_PROGRAM_02` (EKB) sur GO ; tout build,
migration ou seed reste interdit. Aucun code touché ; repo principal UI non touché.
