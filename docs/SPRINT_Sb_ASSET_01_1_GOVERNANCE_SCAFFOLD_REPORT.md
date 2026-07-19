# Sprint Sb_ASSET_01.1 — Governance Scaffold & Provenance Registry — BUILD REPORT

**Statut** : 🟢 **CODE COMPLETE — CI PENDING — HUMAN REVIEW PENDING**
**Type** : build gouvernance (scaffold `design/auren/` + test + docs) — 1er build de `Sx_ASSET`
**Date** : 2026-07-19
**Baseline** : `6167485` (spec Sx_ASSET_01 commitée)
**Worktree** : `work/sb-asset-01-1-governance-scaffold`

> **GOVERNANCE BEFORE ASSETS.** Ce build crée le **système de gestion** des assets, **pas les assets**.
> Aucun SVG/PNG/master/licence tierce produit. `Sx_UI` reste CLOSED. Gate d'intégration reste BLOCKED.

---

## 1. Baseline
HEAD local = origin = `6167485`, working tree clean, 0/0. Aucun build 01.1 préexistant (`design/auren/`
absent).

## 2. Brainstorming (§5 — conclusion)
`GOVERNANCE BEFORE ASSETS · NO THIRD-PARTY INTAKE · NO ANATOMICAL MASTER · RUNTIME ASSETS REFERENCED, NOT
COPIED · PROVENANCE UNKNOWN IS EXPLICIT · INTEGRATION GATE REMAINS BLOCKED.`
Décisions clés : 6 fichiers utiles (README/manifest/style/provenance/intake/LICENSES-README) ; dossiers
`source/exports/previews/references/tokens` **documentés dans le README, pas créés vides** (trompeurs) ;
manifest en **Markdown** (JSON tokens = build ultérieur, interdit ici) ; assets runtime **référencés** par
chemin, jamais copiés ; provenance inconnue = `UNKNOWN — MANUAL VERIFICATION REQUIRED` (jamais d'auteur
inventé) ; 0 licence tierce (aucun intake) ; tests empêchent asset non gouverné.

## 3. Inventaire runtime (audité, §17)
| Asset | Chemin exact | Format | Poids | Consumer |
|---|---|---|---|---|
| BodyMap prototype | `app/templates/_partials/worked_area_body_map.html` | SVG inline | 4490 o | exercise_card / body-intelligence |
| mark | `app/static/icons/auren-mark.svg` | SVG | 248 o | head/manifest |
| favicon | `app/static/icons/favicon.svg` | SVG | 256 o | head |
| apple-touch | `app/static/icons/apple-touch-icon.png` | PNG | 1582 o | head |
| icon-192 | `app/static/icons/icon-192.png` | PNG | 1475 o | manifest |
| icon-512 | `app/static/icons/icon-512.png` | PNG | 6567 o | manifest |
| maskable-512 | `app/static/icons/icon-maskable-512.png` | PNG | 6567 o | manifest |
| icônes inline shell | `app/templates/base.html` | SVG inline | — | bottom nav / rail |
**Note** : pas de `maskable-192` dans le runtime (seulement 512) — non inventé.

## 4. Classification
| Asset | État | Provenance |
|---|---|---|
| BodyMap prototype | **PROTOTYPE — TO REPLACE AFTER GATE** (provisional) | repository-authored (Sb_BODYMAP_01.1) |
| mark/favicon/PNG PWA | **EXISTING — PROVISIONAL** (brand-bearing) | repository-authored (Sb_UI_10.2, recoloration+sips) |
| icônes inline shell | **EXISTING — PROVISIONAL** | repository-authored (Sb_UI_03.1) — **PAS Tabler** |
| master BodyMap / wordmark | **MISSING — EXTERNAL HUMAN PRODUCTION REQUIRED** | — |
**Aucun asset supprimé/déplacé/modifié.**

## 5-13. Architecture créée + gouvernance
- **`design/auren/README.md`** : porte d'entrée (identité SPIGNOS/Auren, statut, principes, navigation,
  architecture documentée, règle « présence ≠ autorisation app/static »).
- **`AUREN_VISUAL_ASSET_MANIFEST.md`** : 16 champs normatifs · 8 statuts bornés (conditions de `approved`) ·
  valeurs `NOT APPLICABLE`/`UNKNOWN — MANUAL VERIFICATION REQUIRED`/`NOT YET REVIEWED/PRODUCED` distinguées ·
  entrées runtime (BodyMap prototype `provisional`, PWA `provisional`, inline icons `provisional`) ·
  masters futurs documentés (non créés) · **0 entrée `approved`**.
- **`AUREN_ASSET_PROVENANCE.md`** : 18 champs · `source_type`/`usage_nature` bornés · politique (0 tiers
  sans provenance complète, pas d'`approved` avec licence UNKNOWN, pas d'agrégateur) · entrées honnêtes
  (repository-authored, upstream `NOT APPLICABLE`) · **NONE tiers**.
- **`AUREN_STYLE_RULES.md`** : positionnement biomécanique non médical · palette Auren Terminal (0 nouvelle
  couleur, currentColor) · contrat SVG icônes · interdits · anatomie · taxonomie 11 zones · accessibilité.
- **`AUREN_ASSET_INTAKE_CHECKLIST.md`** : identification/provenance/technique/sémantique/a11y/revues/verdict
  (l'intake ≠ autorisation d'intégration runtime).
- **`LICENSES/README.md`** : procédure licences · **0 licence tierce** (« No third-party asset has been
  accepted ») · interdits (reconstruction/agrégateur/faux MIT.txt).

## 14. Tests ajoutés
`tests/test_auren_asset_governance.py` (**21 tests, stdlib only**) : scaffold présent · manifest (16 champs,
8 statuts, valeurs UNKNOWN distinctes, **0 asset approved**, BodyMap prototype/provisional, PWA provisional,
gate nom mentionné, référence-not-copy) · provenance (18 champs, UNKNOWN explicite, 0 tiers, pas d'upstream
inventé) · LICENSES (README seul, 0 licence, pas de faux) · **sécurité : 0 binaire/asset sous
`design/auren/`** (svg/png/webp/ico/jpg/gif/font/blend/fig) · **0 master interdit** · assets runtime
toujours en place (référencés, non déplacés).

## 15. Fichiers créés/modifiés
Créés : `design/auren/README.md` · `AUREN_VISUAL_ASSET_MANIFEST.md` · `AUREN_STYLE_RULES.md` ·
`AUREN_ASSET_PROVENANCE.md` · `AUREN_ASSET_INTAKE_CHECKLIST.md` · `LICENSES/README.md` ·
`tests/test_auren_asset_governance.py` · ce rapport. Modifiés : `SPEC_REGISTRY.md` ·
`ROADMAP_AND_NEXT_STEPS.md` · `AUREN_ASSET_PROGRAM_ROADMAP.md`. **Closeout Sx_UI non modifié.**

## 16-17. Absence d'assets / dépendances
**0** SVG/PNG/WebP/ICO/JPEG/font/YAML/JSON produit. **0** dépendance installée (test = stdlib only ; pas
de SVGO/resvg/Node/Blender). `design/auren/` = **uniquement du Markdown** (+ dossier LICENSES avec README).

## 18. Scope
`design/auren/` (6 md) · `tests/test_auren_asset_governance.py` · docs (rapport + registry + roadmap +
program roadmap). **Aucun** `app/**`/`data/**`/`migrations/**`/`.github/**`/asset/binaire/Custom/métier.
check_scope = **ISOLATED** (le script connaît `design/` : les `.md` y sont traités comme docs, le test
neuf = isolated ; **pas de blocage, scope guard non modifié**).

## 19. Garde-fous
ruff clean · budget **543 ≤ 548** · spec_protocol PASS · check_scope ISOLATED. Tests adjacents PWA/BodyMap/
auren : **43 verts** (assets runtime non touchés). Broad sweep ciblé (asset_governance/pwa/bodymap/auren/
manifest/scope/descriptor) : **263 passed, 0 failed** (81s).

## 20. Éléments différés
`Sb_ASSET_01.2` (taxonomie/mapping YAML + tests IDs) · `Sx_ASSET_02` (iconographie/Tabler) · `Sb_ASSET_02.1`
(vendored intake + licence) · `Sx_ASSET_03`/`OPERATOR_ASSET_03.1`/`Sb_ASSET_03.2` (BodyMap master) ·
`Sx_ASSET_04`/`04.1` (intégration) · `05` (closeout). **Aucun** ouvert ici.

## 21. Statut
🟢 **CODE COMPLETE — CI PENDING — HUMAN REVIEW PENDING.**

---

## Verdict

**Verdict :** 🟢 **Sb_ASSET_01.1 CODE COMPLETE (CI + human review pending).** Le scaffold de gouvernance
`design/auren/` est en place : **README** (porte d'entrée, « présence ≠ autorisation app/static »),
**manifest** (16 champs, 8 statuts bornés, **0 entrée `approved`**, valeurs UNKNOWN distinctes),
**provenance** (18 champs, entrées repository-authored honnêtes, **NONE tiers**), **style rules** (non
médical, Auren Terminal, contrat SVG, taxonomie 11 zones), **intake checklist**, **LICENSES/README** (0
licence tierce). Les assets runtime (BodyMap prototype, PWA, icônes inline) sont **référencés sans être
copiés/déplacés/modifiés** et classés `provisional`/prototype. **21 tests dédiés** (stdlib only) empêchent
un asset non gouverné (0 binaire sous `design/auren/`, 0 master, 0 faux `approved`, assets runtime en
place). **0 asset/SVG/PNG/licence tierce/dépendance/fichier `app/**`/Custom/changement métier.** `Sx_UI`
reste CLOSED ; **`ASSET INTEGRATION GATE: BLOCKED`** inchangé.

**Prochaine étape** (séparée, non commencée) : `GO VALIDATE — Sb_ASSET_01.1 Governance Scaffold &
Provenance Registry`.
