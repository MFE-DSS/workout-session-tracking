# Sb_CUSTOM_PROGRAM_WIZARD_05 — EKB-Assisted Exercise Picker (SPEC)

**Statut :** ✅ VALIDATED (build in progress) · **Base canonique :** `1c4604d` · **Tier :** ISOLATED

## 1. Problème

Dans l'éditeur de brouillon custom (WIZARD_02), le champ d'ajout d'exercice est un **texte libre**.
Un nom saisi à la main qui ne correspond pas **exactement** à un nom canonique de l'EKB
(`data/exercise_knowledge_base.json`) tombe « hors EKB » au scoring : le moteur
(`program_quality_engine._aggregate`) résout chaque slot par `ekb.lookup(exercise_name)`, donc un nom
approximatif est **exclu des agrégats de zone/pattern** et n'apparaît pas dans la preview qualité
(WIZARD_04). L'utilisateur n'a aucun moyen de connaître les noms canoniques reconnus.

## 2. Solution

Un **picker en lecture seule** : un `<datalist>` HTML (no-JS) listant les **103 noms canoniques** de
l'EKB avec leurs métadonnées (zone / pattern / équipement), lié au champ existant via `list=`. La
saisie manuelle **reste libre** (le champ demeure `type="text"`), mais l'autocomplétion aligne les noms
sur ceux que l'EKB reconnaît → l'exercice devient reconnu par le scoring/WIZARD_04. En bonus, quand le
nom saisi **matche exactement** une entrée EKB, les colonnes dénormalisées déjà présentes de
`UserProgramExercise` (`variant_key`, `variant_group`, `equipment_family`, `movement_pattern`) sont
**peuplées** au moment de l'écriture d'arbre.

## 3. Décisions verrouillées

- **Source EKB** : `data/exercise_knowledge_base.json` (lecture seule, version-pinnée `_version`).
- **Options** : les **103 noms canoniques** (le moteur reconnaît covered *et* gap).
- **Aliases** : **NON résolus en V1** (`_aliases` ignoré — un alias tombe en texte libre).
- **Matching** : **match canonique EXACT** uniquement — aucune normalisation casse/accents/espaces.
- **UI** : `<datalist>` HTML (pas `<select>`), **une seule instance page-level**.
- **Fallback texte libre** : **obligatoire et non bloquant**.
- **Enrichissement dénormalisé** : **activé** (4 colonnes déjà existantes, `replace_draft_tree` les
  persiste déjà, `_tree_to_payload` les round-trip déjà — zéro migration).

## 4. Périmètre livré

- **Service pur read-only** `app/services/user_program_exercise_catalog.py` (`@lru_cache`, aucun ORM,
  aucune DB, aucune écriture) : `picker_options()` (liste triée `{name, zone_primary, movement_pattern,
  equipment_family}`, nulls honnêtes) et `enrich(name)` (4 champs dénormalisés pour un match exact,
  sinon `{}`). N'importe **pas** le moteur de score (surface isolée).
- **Router** `app/routers/user_programs.py` : `picker_options` injecté dans le contexte commun de
  `_render_editor` ; `enrich(exercise_name)` fusionné (spread en tête, les clés contrat gagnent) dans le
  dict d'exercice de `_append_exercise` ; `source_reason` reste `"manual"`, nom verbatim.
- **Template** `app/templates/user_programs/detail.html` : `list="ekb-exercises"` sur l'input + un
  `<datalist id="ekb-exercises">` page-level (labels métadonnées, segments null omis — jamais « None »).

## 5. Non-goals (frontières dures)

- **Pas de migration** — les 4 colonnes dénormalisées existent déjà sur `UserProgramExercise`.
- **Pas de consommateur DB de l'EKB** — le picker lit le **JSON**, pas une table. **EKB_04 (seed DB)
  reste DEFERRED** (aucun consommateur DB n'existe).
- **Pas de modification du moteur de score** (`program_quality_engine.py`) ni du JSON EKB.
- **Pas de JavaScript**, pas de `<select>` contraignant, pas de refonte visuelle de l'éditeur.
- **Pas de changement de régénération** — la **régénération gardée sur programme non vide** est
  **réservée à WIZARD_06** (risque de perte de données via `replace_draft_tree`).
- **Pas de LLM**, pas de claim médical, pas d'écriture de `UserProgramQualityReview`.

## 6. Contrats préservés

Chemins de route, noms de paramètres form, owner-scope, 404 sans fuite d'existence, quotas 7/10,
statuts éditables `draft`/`validated`, transitions de validation, persistance des reviews, comportement
de génération — **tous inchangés**. Le GET reste read-only ; le POST n'introduit **aucune nouvelle
classe d'écriture DB** (l'enrichissement passe par l'écriture d'arbre existante).

## 7. Réservé (non ouvert)

- **WIZARD_06** — régénération gardée sur programme non vide (confirmation avant écrasement).
- Résolution des `_aliases` (V2 du picker), filtrage serveur / requête SQL de l'EKB (déclencherait
  EKB_04).
