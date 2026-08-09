# SPRINT Sb_MORPHO_PROFILE_01 — Pure Morphology Profile Layer (RAPPORT)

**Base canonique :** `351a86c` · **Branche :** `sb/morpho-profile-01` · **Tier :** ISOLATED (**module pur neuf · 0 migration · 0 DB**)
**Spec :** [`Sx_MORPHO_PROGRAM_01_SPEC.md`](strategy/Sx_MORPHO_PROGRAM_01_SPEC.md) (§1, §2, §3, §5) — 1ᵉʳ build de la file.
**Livré sous le protocole agentique** (`CLAUDE.md §4`) : `GO BUILD` → autonome jusqu'à `PR GREEN / MERGE PENDING`.

## 1. Ce qui est livré

La **couche de profil de morphologie PURE** : faits corporels bruts → **descripteurs de morphologie interprétés avec confiance**, en séparant strictement **FACT** et **INFERENCE**. Aucune génération de programme, aucun slot, aucune substitution, aucune migration, aucune photo.

## 2. Brainstorming / Options / Risques / Choix retenu (CLAUDE.md §3)

**Préflight** : lecture du patron pur `program_quality_engine.py` (frozen dataclasses, déterministe, 0 I/O) + confirmation des conditions d'arrêt.

| Option | Verdict |
|---|---|
| **A** — **module pur** (`MorphologyFacts` → `MorphologyDescriptor`), patron `program_quality_engine` | ✅ **RETENU** — 0 DB, 0 migration, déterministe, testable, aucune dépendance generator/substitution |
| **B** — brancher sur `BodyMeasurement` (lecture DB) dès ce build | ✗ ajouterait une dépendance DB + colonnes manquantes (wingspan/ape) → tentation de migration ; hors scope (persistance = build ultérieur) |
| **C** — inclure les priorités/slots dès maintenant | ✗ interdit (génération/slots = builds suivants) ; violerait « no program generation » |

**Conditions d'arrêt — toutes levées** :
- `BodyMeasurement`/`body_consents` insuffisants ? → **non pertinent** : la couche est **pure** (input model), elle **ne lit pas** la DB → **aucune migration**.
- Migration DB requise ? → **non** (module pur).
- Stockage de données perso ambigu ? → **non** : Martin = **fixture dogfood privée** (tests only), 0 photo, 0 template global.
- Specs Body Intelligence en conflit ? → **non** (réconcilié par `Sx_MORPHO_PROGRAM_01`, garde-fou strict).
- Toucher generator/substitution/session_builder ? → **non** (module autonome).

**Risques traités** :
1. **Fuite médicale / pseudo-précision** → garde-fou strict : `GUARDED_NOT_DEDUCTIBLE` (fémur/humérus/insertions/posture/dyskinésie/%BF/diagnostic) **jamais produits** ; `guarded_not_deductible()` renvoie `not_deductible`. Ape index = **tag de levier borné**, jamais une longueur osseuse. *Testé (#guarded, #ape, #value-claims).*
2. **Confusion FACT/INFERENCE** → deux couches, une INFERENCE cite toujours son evidence et ne réémet jamais un id de FACT. *Testé.*
3. **Fabrication de valeurs** → une entrée absente ⇒ descripteur **omis**, jamais inventé. *Testé.*
4. **Données perso** → fixture privée sous `tests/fixtures/dogfood/`, auto-identifiée « private », jamais runtime/global. *Testé.*

## 3. Fichiers touchés (3 + docs)

| Fichier | Changement |
|---|---|
| `app/services/morphology_profile.py` (**neuf, pur**) | `MorphologyFacts`/`BodyObservation` (entrée), `MorphologyDescriptor` (sortie), `build_morphology_profile()`, `guarded_not_deductible()`, vocabulaires fermés + garde-fou strict + seuils bornés |
| `tests/fixtures/dogfood/martin_morphology.py` (**neuf, privé**) | fixture dogfood Martin (2026-08-09) — **test-only, jamais global/runtime** |
| `tests/test_morphology_profile.py` (**neuf**) | 16 tests |
| docs | rapport + registry + roadmap |
| **generator / substitution / session_builder / models / migrations** | **aucun** |

## 4. Modèle livré

- **FACT** (measured) : chaque mesure numérique fournie (taille, envergure, taille, poitrine, cuisse, mollet) + ape index (`measured` si fourni, `derived` si = envergure − taille).
- **INFERENCE** : `longiligne_athletic_build` (derived, proxy) · `slightly_positive_ape_index_not_extreme` · `favorable_shoulder_to_waist_structure` (derived, **proxy** chest/waist + observation claviculaire) · `narrow_waist_pelvis_relative` (derived) · `quads_relatively_strong` / `calves_relative_lag` / `lats_acceptable_not_weak` (inferred, observations opérateur) · `lateral_delts` / `upper_chest` / `rear_delts_upper_back` `_priority_candidate` (inferred, **candidats** — jamais des priorités appliquées).
- **Confidence** : `measured` / `derived` / `inferred` / `not_deductible` (§2 de la spec).
- **not_deductible** : `guarded_not_deductible()` + `GUARDED_NOT_DEDUCTIBLE` (refus testable).

## 5. Tests

`tests/test_morphology_profile.py` — **16 passés** : FACT layer/measured · INFERENCE cite l'evidence & ne fabrique pas de FACT · entrée absente → omise · schéma complet · ape index measured/derived + seuil non-extrême · ratio→derived / observation→inferred · **descripteurs gardés jamais produits** · `guarded_not_deductible` refus + rejet clé non-gardée · value ne revendique jamais posture/fémur/diagnostic · déterminisme · **fixture Martin → 10 descripteurs requis** · candidats = candidates (pas des priorités) · fixture marquée privée.

**Broad sweep ciblé** (body_intelligence + inputs + body_profile + measurements + profile_metrics + bi01 guardrails + profile↔BI link + morphology) : **138 passés** (0 régression).

## 6. Interdits tenus

0 génération de programme · 0 sélection d'exercice · 0 slot · 0 changement de substitution · **0 migration** · 0 stockage de photo · 0 traitement d'image · 0 diagnostic médical · 0 posture/pathologie · 0 fémur/insertion/dyskinésie · 0 donnée Martin en template global · 0 exposition `/library` · 0 changement du cycle Custom Program · 0 EKB_04 · 0 runtime ASSET.

## 7. Validation

check_scope **ISOLATED** · `check_spec_protocol` PASS · `check_ruff_budget` **543 ≤ 548** · `ruff check` fichiers neufs **clean**. CI PR = filet.

## Verdict

**Verdict :** 🟢 **Sb_MORPHO_PROFILE_01 — PATCH COMPLETE / PR PENDING.** Couche de profil de morphologie **pure et déterministe** : FACT/INFERENCE séparés, confidence à 4 niveaux, garde-fou **strict** (`not_deductible` testable, 0 posture/médical), fixture Martin **privée** produisant les 10 descripteurs requis. **0 génération/slot/substitution/migration.** Merge = GO humain.

---
