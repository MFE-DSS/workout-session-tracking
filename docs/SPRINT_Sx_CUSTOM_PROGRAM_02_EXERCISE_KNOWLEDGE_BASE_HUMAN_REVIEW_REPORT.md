# Human Review — Sx_CUSTOM_PROGRAM_02 Exercise Knowledge Base Spec

**Verdict** : ✅ **HUMAN REVIEW ACCEPTED / SPEC ONLY / BUILD NOT AUTHORIZED**
**Date** : 2026-07-15
**Type** : revue humaine — docs-only (aucun code touché par cette revue ni par la spec)
**Track** : `Sx_CUSTOM_PROGRAM` (parent `Sx_CUSTOM_PROGRAM_01` ✅ ACCEPTED)
**Branche** : `spec/sx-custom-program-01-intelligent-builder` (worktree isolé, synchronisée
origin, spec commit `cbba7d9`)
**Spec** : [`Sx_CUSTOM_PROGRAM_02_EXERCISE_KNOWLEDGE_BASE_SPEC.md`](strategy/Sx_CUSTOM_PROGRAM_02_EXERCISE_KNOWLEDGE_BASE_SPEC.md)

---

## 1. Décision

**Sx_CUSTOM_PROGRAM_02 est acceptée** comme définition de l'Exercise Knowledge Base V1 :
source structurée unique pour la génération, le remplacement d'exercices et le scoring A/B/C
du futur Custom Program Builder — **ni vérité médicale, ni couche LLM**. Le statut reste
**SPEC ONLY** : aucun build, aucune migration, aucun seed, aucun fichier `data/` ni code
applicatif n'est autorisé par cette acceptance.

## 2. Éléments acceptés

| Élément | Décision |
|---|---|
| **Audit chiffré de l'existant** (spec §3) : 53 entrées properties vs **103 noms** catalogue → **52 absents (~50 %)** ; socle Sx_32 prêt (`BodyZone` 11, `ExerciseMuscleMapping` 91 par nom, `Muscle` vide) ; 25 `machine_slug` / 8 familles ; QA scripts recensés | ✅ accepté comme état de référence |
| **Identité** : nom canonique historique = clé stable V1, **zéro renommage** ; `variant_key` + `variant_group` additifs ; canonique/variante/machine/pattern distingués | ✅ accepté (invariance des noms = contrainte #1) |
| **Taxonomie V1** : 18 champs (zone/pattern/equipment/chain/stability/fatigue_class/technical_difficulty/laterality/setup/estimated_slot_minutes/overload_compatibility/confidence…) — valeurs opératoires et indicatives | ✅ acceptée |
| **Variantes fines** : entrées distinctes reliées par `variant_group` (exemple canonique élévations latérales ×5, différenciées matériel/fatigue/setup/stabilité/latéralité) | ✅ accepté |
| **Stockage : Option C séquencée** — JSON versionné = source canonique d'abord ; seed DB **optionnel**, additive-only, gaté par acceptance dédiée (`EKB_04`) | ✅ accepté comme direction |
| **Contraintes seed** : versionné, jamais destructif (`is_active`), QA-gated, compatible wipe-guard Custom Program, tables distinctes du catalogue | ✅ contrats durs |
| **QA future** : 8 checks (couverture 103/103, substitutions connues, complétude, invariance des noms, unicité, cohérence de groupe, lexique non-médical, traçabilité no-LLM-only) | ✅ acceptée — obligatoire avant tout seed |
| **Non-goals** (spec §11) dont : catalogue système intouchable, pas de peuplement `Muscle`, pas de claims biomécaniques absolus | ✅ contraignants |

## 3. Open questions (OQ-EKB-A → OQ-EKB-I)

Statut : **acceptées comme questions à trancher dans les builds EKB / specs suivantes**, avec
leurs positions par défaut (Option C séquencée, granularité bornée aux besoins wizard V1,
**BodyZone-first / `Muscle` reste vide**, familles d'équipement génériques, cardio hors EKB V1,
abdos inclus avec `overload_compatibility` limitée, curation prudente `confidence: inferred`,
confidence par entrée V1, séparation sûre/inférée via `confidence`). **Aucune n'est une
décision build finale.**

## 4. Invariants vérifiés (cette revue et la spec)

no `app/` · no `tests/` · no `data/` (les 52 gaps sont **documentés, pas corrigés**) · no
migration · no seed · no template/CSS/JS · no fichier UI/Auren · repo principal non touché ·
diff de la spec = 3 fichiers docs (+241/-3) · `check_spec_protocol` PASS · `check_scope` DOCS.

## 5. Queue suivante

| Élément | Statut |
|---|---|
| **`Sx_CUSTOM_PROGRAM_03` — Program Quality Scoring Spec** | 🔵 **NEXT SPEC CANDIDATE** (SPEC ONLY, sur GO explicite) |
| `Sx_CUSTOM_PROGRAM_04` / `05` (Persistence / Instantiation Compat) | ⚪ après 03, dans l'ordre |
| `Sb_CUSTOM_PROGRAM_EKB_01` → `04` (audit QA read-only → JSON draft → QA script → seed optionnel) | ❌ **NOT AUTHORIZED** — chaque build sur GO explicite après acceptance |
| `Sb_CUSTOM_PROGRAM_01` → `07` (builds parent) | ❌ NOT AUTHORIZED |
| Migrations / seed | ❌ aucun autorisé |

## 6. Risques acceptés

- **Gap de couverture 52/103** : assumé jusqu'à `EKB_02` (JSON draft) — le wizard ne peut pas
  être buildé avant que la QA de couverture passe à 103/103.
- **Métadonnées inférées sans source externe** (fatigue/technicité) : curation opérateur
  conservatrice, `confidence: inferred` explicite, jamais présenté comme mesure.
- **Dérive encyclopédique** : bornée par OQ-EKB-B (variantes limitées aux besoins wizard V1).
- **Collision d'agents** : track isolé en worktree, rebase avant toute PR/build (discipline
  du parent §16 maintenue).

---

## Verdict

**Verdict :** ✅ **Sx_CUSTOM_PROGRAM_02 Exercise Knowledge Base Spec — HUMAN REVIEW ACCEPTED /
SPEC ONLY / BUILD NOT AUTHORIZED.**

L'EKB V1 est définie : identité par noms historiques invariants + `variant_group`, taxonomie
18 champs opératoires, stockage JSON-canonique-d'abord (Option C séquencée), seed futur
versionné non destructif QA-gated, 8 checks de QA obligatoires, 9 OQ instruites avec positions
par défaut. L'audit chiffré (53/103, socle Sx_32) sert d'état de référence. **Next :
`Sx_CUSTOM_PROGRAM_03 — Program Quality Scoring Spec` sur GO ; tout build EKB reste interdit.**
Aucun code touché ; repo principal UI non touché.
