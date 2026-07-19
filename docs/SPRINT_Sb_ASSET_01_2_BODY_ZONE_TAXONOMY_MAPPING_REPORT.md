# Sprint Sb_ASSET_01.2 — Body Zone Taxonomy & Mapping Contract — BUILD REPORT

**Statut** : 🟢 **CODE COMPLETE — CI PENDING — HUMAN REVIEW PENDING**
**Type** : build contrat sémantique (design + tests + docs) — 2ᵉ et dernier build de `Sx_ASSET_01`
**Date** : 2026-07-19
**Baseline** : `7da5334` (revue Sb_ASSET_01.1 acceptée)
**Worktree** : `work/sb-asset-01-2-body-zone-contract`

> **SEMANTIC CONTRACT ONLY.** Ce build matérialise la taxonomie 11 zones, le mapping 6 macros et les IDs SVG
> stables comme **contrat versionné testable** — **aucune géométrie**, **aucun runtime modifié**, **aucune
> validation anatomique** (un contrat sémantique n'est pas une validation anatomique).

---

## 1. Baseline
HEAD local = origin = `7da5334`, clean. Aucun build 01.2 équivalent (3 livrables absents ; 0 commit grep).

## 2. Worktree & 3. Collisions
Worktree isolé sur `7da5334`. Anti-collision : `origin` contrôlé avant modif/commit/FF/push (stable
`7da5334`). Aucun rebase/reset/amend/force-push ; aucun worktree Custom touché.

## 4. Brainstorming (§5 — conclusion)
```
SEMANTIC CONTRACT ONLY · ELEVEN ZONES EXACTLY · UNKNOWN IS NOT ANATOMY · SIX VISUAL MACROS
ANALYTICS RADAR AXES UNTOUCHED · STABLE SVG IDS · NO GEOMETRY · NO APP WIRING
NO NEW DEPENDENCY · INTEGRATION GATE REMAINS BLOCKED
```
Décisions clés : source de vérité = `ZONE_LABELS` (le contrat **miroir**, ne remplace pas) ; labels FR
**dans** le contrat (testés en parité) ; mapping = `_WA_ZONE_TO_REGION` ; `RADAR_AXES` **intouché** (modèle
analytics distinct) ; `unknown` = état de qualification, pas une zone ; IDs SVG figés (API) ; Layer A métier
ici / Layer B géométrique futur ; géométrie inconnue = `NOT YET PRODUCED` ; format **YAML JSON-compatible**
lu par `json` stdlib (pyyaml seulement transitif dans le lock → **non garanti** → pas de nouvelle dépendance) ;
parité via import `ZONE_LABELS` + `ast.literal_eval` du littéral Jinja ; garde binaire → **garde évolutive
allowlistée** ; `owner` nuancé via `ip_ownership_status`.

## 5. Sources runtime auditées (§6)
| Contrat | Source actuelle | Nature | Reste runtime ? | Consommé par le contrat |
|---|---|---|---|---|
| 11 codes | `app/services/muscle_mapping.py#ZONE_LABELS` | métier | oui | miroir vérifié (parité) |
| labels FR | `ZONE_LABELS` | présentation métier | oui | enregistrés + parité |
| 6 macros | `_partials/worked_area_body_map.html#_WA_ZONE_TO_REGION` | présentation compacte | oui | miroir vérifié (parité) |
| axes radar | `RADAR_AXES` / `RADAR_AXIS_ORDER` | analytics | oui | **non** (séparation documentée) |
| descriptor | `body_map_descriptor.build_body_map_descriptor` | contrat d'échange | oui | invariants seulement |
| IDs SVG futurs | spec Sx_ASSET | API design | futur | oui (figés) |

## 6. Macros visuelles ≠ radar analytics (§7)
`BODYMAP COMPACT MACROS ARE NOT RADAR_AXES`. BodyMap **fusionne** `lats`+`upper_back`→`back` et isole
`core` ; `RADAR_AXES` **sépare** `back_width`(lats)/`back_thickness`(upper_back), plie le bas en `lower`, et
**n'a pas** de `core`. Documenté dans le contrat, la taxonomie et un test dédié pour empêcher une fusion
future. **0 modification** de `RADAR_AXES`/`RADAR_AXIS_ORDER`/scores/agrégations/Body Intelligence.

## 7. Taxonomie 11 zones (§9)
`pecs · delt_lat · delt_post · lats · upper_back · biceps · triceps · quads · posterior · calves · core`,
labels FR **identiques** à `ZONE_LABELS`, ordre canonique.

## 8. Labels
Enregistrés dans `AUREN_BODY_ZONE_TAXONOMY.md` + `label_fr` du YAML ; **parité testée** contre `ZONE_LABELS`.

## 9. `unknown` (§9)
`code: unknown · nature: qualification-state · anatomical_zone: false · label: À qualifier · visual: neutral`.
**Pas** une 12ᵉ zone · **pas** de `zone-unknown` · 0 anatomie active · jamais compté dans la couverture 11
zones · jamais auto-converti.

## 10. Zones agrégées (§10)
`upper_back` (dos épaisseur) et `posterior` (ischios/fessiers/chaîne postérieure) marquées
`semantic_kind: functional-aggregate` — ne prétendent **pas** distinguer muscles/faisceaux unitaires. Le
futur BodyMap reflète la granularité de la donnée, jamais davantage.

## 11. 6 macros (§13)
`chest · shoulders · back · arms · legs · core`. Chaque zone dans **exactement une** macro ; union = 11
zones. `compact_render_views` décrit le **prototype compact existant**, pas une décision anatomique finale.

## 12. Différence radar
Voir §6. Table comparative dans la taxonomie ; `RADAR_AXES` intouché (test de garde).

## 13. IDs SVG stables (§14)
`auren-bodymap · body-front-base · body-back-base · zone-<11 codes>`. 1 ID/zone · 0 `zone-unknown` · 0 ID
genré · 0 alias/renommage/path fusionné · unicité. API figée → évolution incompatible = nouvelle spec +
migration.

## 14. États (§15) & variantes (§17)
États (5, sans couleur) : `neutral · primary · secondary · unknown · disabled`. Variantes (3, **aucune
produite**) : `male_neutral_v1 · female_neutral_v1 · neutral_abstract_v1` ; `geometry_status: NOT YET
PRODUCED` ; 0 code métier dépendant d'une variante ; 0 genre encodé dans les codes ; 11 IDs identiques entre
variantes.

## 15. Absence de géométrie
Le YAML ne contient **aucun** path/polygon/coordonnée/activation/pourcentage/EMG/origine/insertion. Testé
(clés interdites dans les entrées de zone + scan des valeurs sérialisées).

## 16. Format YAML (§11.1)
YAML 1.2 en **syntaxe JSON-compatible**, lu par `json.loads` (stdlib). **PyYAML non ajouté** (absent de
`requirements.txt`/`pyproject.toml`, seulement transitif dans `requirements-lock.txt` → non garanti).

## 17. Parité runtime (§23)
- zones ↔ `ZONE_LABELS` (import direct) ✅
- `label_fr` ↔ `ZONE_LABELS[code]` ✅
- mapping ↔ `_WA_ZONE_TO_REGION` via `ast.literal_eval` du littéral Jinja isolé (pas de rendu HTML) ✅
- descriptor : `build_body_map_descriptor` ne produit que les 11 codes connus ou `unknown` ✅
Le contrat **miroir** la vérité runtime, ne devient **pas** une seconde source divergente. 0 service modifié.

## 18. Dette 1 — `owner` nuancé (§20) — RÉSOLUE
`AUREN_ASSET_PROVENANCE.md` : champ `owner` redéfini (« gardien opérationnel du repository OU titulaire
revendiqué — pas une preuve de PI »), **Option A** appliquée : nouveau champ `ip_ownership_status`
(`not-legally-reviewed | verified | unknown | not-applicable`). Les 3 entrées runtime + l'entrée contrats
portent `owner: … — OPERATIONAL REPOSITORY CUSTODIAN` + `ip_ownership_status: not-legally-reviewed` +
`IP OWNERSHIP NOT LEGALLY VERIFIED`. **Aucun `verified`** dans ce sprint. Verrouillé par test.

## 19. Dette 2 — garde temporelle (§21) — RÉSOLUE
`tests/test_auren_asset_governance.py` : garde binaire **permanente** (svg/png/… toujours interdits) ;
garde structurée **évolutive** via **allowlist exacte** (`design/auren/source/bodymap/auren_bodymap_mapping.yaml`) ;
tout autre `.yaml/.yml/.json` toujours refusé. Documenté dans le test :
*The zero-asset binary guard is permanent. The zero-structured-file guard was specific to Sb_ASSET_01.1.
Structured contract files are allowed by explicit allowlist. Future SVG intake requires Sb_ASSET_02.1 /
Sb_ASSET_03.2 to evolve the guard.* SVG **non** autorisés ; YAML/JSON **non** autorisés globalement.

## 20. Tests ajoutés
- `tests/test_auren_body_zone_contract.py` (**29 tests**, stdlib only) : parsing json · 11 zones/ordre/unicité ·
  parité labels · unknown non-anatomie · 6 macros/union/appartenance unique · parité `_WA_ZONE_TO_REGION` ·
  séparation `RADAR_AXES` + radar intouché · IDs (set exact/1 par zone/0 unknown/0 genré/unicité) · 5 états ·
  3 variantes non produites · 0 géométrie · owner IP non prouvée · allowlist · descriptor parité.

## 21. Tests réorientés
- `tests/test_auren_asset_governance.py` : 21 → **23 tests** (garde binaire permanente conservée + 2 nouveaux :
  `test_structured_files_only_via_allowlist`, `test_allowlisted_contract_present_and_binary_free`).
- **Fix docs pré-existant** : `SPRINT_Sb_ASSET_01_1_..._HUMAN_REVIEW_REPORT.md` (commit `7da5334`) portait
  `**Verdict** :` (marqueur non reconnu par `check_spec_protocol`) — sa CI avait été légitimement skippée
  (docs-only `paths-ignore`), donc le bug dormait. Ce build réactive la CI (ajout `tests/`) : corrigé en
  `**Verdict :**` (marqueur standard du repo). **Aucun test masqué** — correction de syntaxe de marqueur, le
  verdict existait déjà.

## 22. Résultats locaux
- `test_auren_body_zone_contract.py` : **29 passed** · `test_auren_asset_governance.py` : **23 passed**.
- Suites adjacentes (muscle mapping, bodyzone foundation, worked-area BodyMap, descriptors, Body
  Intelligence, scoring, profile, recommendation, coach report, PWA, scope, spec protocol) : **broad sweep
  ciblé 273 passed, 0 failed**.
- ruff **clean** · budget **543 ≤ 548** · check_spec_protocol **PASS** · check_scope **ISOLATED**.

## 23. Scope
`design/auren/` (taxonomie + source/bodymap README+YAML + 4 maj README/manifest/provenance/style) · 2 tests
(1 neuf + 1 réorienté) · docs (rapport + registry + roadmap + program roadmap + fix marqueur review 01.1).
`DESIGN CONTRACT + TESTS + DOCS · NO RUNTIME APPLICATION CHANGE`.

## 24. Absence d'asset
0 SVG/PNG/WebP/ICO/JPEG/font/master/géométrie/path/coordonnée/token JSON/licence tierce/subset Tabler/config
SVGO-resvg. `design/auren/source/bodymap/` = README + **contrat** YAML uniquement.

## 25. Absence d'app / analytics changes
`app/services/muscle_mapping.py`, `app/services/body_map_descriptor.py`,
`app/templates/_partials/worked_area_body_map.html` = **byte-identiques**. 0 `app/`/`data/`/`migrations/`/
`.github/`/`requirements*`/`pyproject.toml`. `RADAR_AXES`/`RADAR_AXIS_ORDER` **intouchés**.

## 26. Gate d'intégration
`ASSET INTEGRATION GATE: BLOCKED PENDING HUMAN / ANATOMICAL / LEGAL / MOBILE APPROVALS` — inchangé.

## 27. Éléments différés
`Sx_ASSET_02` (iconographie) · `Sb_ASSET_02.1` (vendored Tabler + licence) · `Sx_ASSET_03` /
`OPERATOR_ASSET_03.1` / `Sb_ASSET_03.2` (BodyMap master) · `Sx_ASSET_04` / `04.1` (intégration) · `05`
(closeout). **Aucun** ouvert ici. `Sx_ASSET_01` socle **complet** (01.1 + 01.2) après cette revue.

## 28. Statut
🟢 **CODE COMPLETE — CI PENDING — HUMAN REVIEW PENDING.**

---

## Verdict

**Verdict :** 🟢 **Sb_ASSET_01.2 CODE COMPLETE (CI + human review pending).** Le contrat sémantique Body Zone
est livré : taxonomie 11 zones (parité `ZONE_LABELS`), mapping 6 macros (parité `_WA_ZONE_TO_REGION`), IDs SVG
stables figés, `unknown` séparé (non-anatomie), séparation explicite avec `RADAR_AXES` (intouché), 0 géométrie,
YAML JSON-compatible sans nouvelle dépendance. Les **2 dettes** de la revue 01.1 sont **résolues** (`owner`
nuancé via `ip_ownership_status: not-legally-reviewed` ; garde binaire → garde évolutive allowlistée). **29 +
23 tests dédiés** + broad sweep **273 verts**. **0 changement runtime/analytics** (services + template
byte-identiques ; `RADAR_AXES` intouché). `ASSET INTEGRATION GATE` reste **BLOCKED** ; `Sx_UI` reste CLOSED.

**Prochaine étape** (séparée, non commencée) : `GO VALIDATE — Sb_ASSET_01.2 Body Zone Taxonomy & Mapping
Contract`.
