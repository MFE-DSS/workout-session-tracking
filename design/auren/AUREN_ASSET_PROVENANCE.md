# AUREN — Asset Provenance Registry

Registre de **provenance** de tout asset visuel Auren. **FIRST THIRD-PARTY DESIGN-SOURCE INTAKE RECORDED :
Tabler Icons v3.45.0 / MIT / HUMAN-LEGAL REVIEW PENDING** (Sb_ASSET_02.1 — cf. §5.5).
Les entrées ci-dessous couvrent les objets runtime existants (repository-authored).

---

## 1. Champs du registre
| Champ | Description |
|---|---|
| `asset_id` | id du manifest |
| `author` | auteur réel (personne/équipe) ou `UNKNOWN — MANUAL VERIFICATION REQUIRED` |
| `owner` | **gardien opérationnel du repository OU titulaire de droits revendiqué** — *n'est pas* une preuve de propriété intellectuelle juridiquement démontrée (voir `ip_ownership_status`) |
| `ip_ownership_status` | état de la propriété intellectuelle : `not-legally-reviewed` \| `verified` \| `unknown` \| `not-applicable`. **Jamais `verified` sans revue juridique aboutie.** |
| `source_project` | projet/bibliothèque d'origine (si tiers) |
| `source_version` | version de la source |
| `source_type` | voir §2 |
| `access_date` | date de récupération de la source tierce |
| `source_reference` | URL/référence **officielle** de la source |
| `license_spdx` | identifiant SPDX ou `UNKNOWN` |
| `license_text_location` | chemin du texte de licence conservé dans `LICENSES/` |
| `attribution_required` | `yes`/`no`/`UNKNOWN` |
| `usage_nature` | voir §3 |
| `modifications` | description des modifications apportées |
| `tooling` | outils utilisés (sips, illustrateur, …) |
| `reviewer` | validateur |
| `review_date` | date de validation |
| `evidence` | preuve (commit, capture, note) |
| `status` | état de vérification |

## 2. `source_type` (valeurs autorisées)
`original-auren` · `vendor` · `adaptation` · `reference-only` · `repository-authored` · `unknown`.

## 3. `usage_nature` (valeurs autorisées)
`runtime-integration` · `vendored-copy` · `modified-derivative` · `reference-only` · `production-tooling`.

## 4. Politique
- **Aucun asset tiers** ne peut entrer dans `design/auren/source/` ni dans `app/static/` **sans entrée de
  provenance complète** (auteur, licence SPDX, texte de licence conservé, date d'accès, source officielle).
- **Aucun asset** ne peut recevoir `status: approved` (manifest) avec `license_spdx: UNKNOWN`.
- **Aucune** provenance inconnue n'est présentée comme vérifiée. Provenance non déterminable →
  `status: manual-verification-required`.
- **Aucune** source juridique via un agrégateur : la licence est vérifiée sur la **source officielle** au
  moment de l'intake réel.
- **`owner` ≠ propriété juridique prouvée.** Le champ `owner` désigne le **gardien opérationnel** du
  repository (ou un titulaire de droits *revendiqué*), jamais une PI juridiquement démontrée. La preuve
  juridique est portée par `ip_ownership_status`, qui reste **`not-legally-reviewed`** tant qu'aucune revue
  juridique n'a abouti. `IP OWNERSHIP NOT LEGALLY VERIFIED` est l'état par défaut des entrées repository.

## 5. Entrées initiales (runtime existant)

### 5.1 BodyMap prototype
```yaml
asset_id: auren.runtime.bodymap.prototype
author: repository (Sb_BODYMAP_01.1)
owner: MFE-DSS/workout-session-tracking — OPERATIONAL REPOSITORY CUSTODIAN
ip_ownership_status: not-legally-reviewed   # IP OWNERSHIP NOT LEGALLY VERIFIED
source_project: NOT APPLICABLE
source_version: NOT APPLICABLE
source_type: repository-authored
access_date: NOT APPLICABLE
source_reference: internal — app/templates/_partials/worked_area_body_map.html
license_spdx: NOT APPLICABLE        # œuvre du repo
license_text_location: NOT APPLICABLE
attribution_required: no
usage_nature: runtime-integration
modifications: SVG inline CSS/SSR, mapping 11 zones → 6 macros (décoratif)
tooling: hand-authored (Jinja/SVG)
reviewer: operator (Sb_BODYMAP_01.1 human review accepted)
review_date: 2026-07-14
evidence: docs/SPRINT_Sb_BODYMAP_01_1_INLINE_BODYMAP_HUMAN_REVIEW_REPORT.md
status: verified-repository-authored
```

### 5.2 Assets PWA (mark/favicon/icons)
```yaml
asset_id: auren.runtime.pwa.mark  (+ favicon, apple-touch, icon-192/512, maskable-512)
author: repository (Sb_UI_10.2)
owner: MFE-DSS/workout-session-tracking — OPERATIONAL REPOSITORY CUSTODIAN
ip_ownership_status: not-legally-reviewed   # IP OWNERSHIP NOT LEGALLY VERIFIED (brand-bearing — cf. legal_note)
source_type: repository-authored     # glyphe haltère existant recoloré, pas d'import tiers
source_reference: internal — app/static/icons/*  ; docs/SPRINT_Sb_UI_10_2_..._REPORT.md
license_spdx: NOT APPLICABLE
attribution_required: no
usage_nature: runtime-integration
modifications: recoloration #f25f3a→#C8A24B (SVG) ; rasterisation PNG via sips (dimensions exactes)
tooling: sips (macOS), hand-edited SVG
reviewer: operator (Sb_UI_10.2 human review accepted)
review_date: 2026-07-15
evidence: docs/SPRINT_Sb_UI_10_2_PWA_MANIFEST_APP_ICONS_AUREN_HUMAN_REVIEW_REPORT.md
status: verified-repository-authored
legal_note: >
  BRAND-BEARING — le glyphe/mark porte l'identité produit Auren dont le nom est en
  EXTERNAL PROFESSIONAL CLEARANCE OPEN. Statut manifest = provisional jusqu'à clearance.
```

### 5.3 Icônes inline du shell
```yaml
asset_id: auren.runtime.shell.inline-icons
author: repository (Sb_UI_03.1)
owner: MFE-DSS/workout-session-tracking — OPERATIONAL REPOSITORY CUSTODIAN
ip_ownership_status: not-legally-reviewed   # IP OWNERSHIP NOT LEGALLY VERIFIED
source_project: NOT APPLICABLE       # PAS Tabler/Health Icons — dessinées à la main dans le repo
source_type: repository-authored
source_reference: internal — app/templates/base.html
license_spdx: NOT APPLICABLE
attribution_required: no
usage_nature: runtime-integration
modifications: SVG inline currentColor (nav/rail)
tooling: hand-authored
reviewer: operator (Sb_UI_03.1/.2/.3 human reviews accepted)
review_date: 2026-07-16
evidence: docs/SPRINT_Sb_UI_03_*_HUMAN_REVIEW_REPORT.md
status: verified-repository-authored
note: >
  upstream provenance = NOT APPLICABLE (création originale). Le futur subset gouverné
  (Tabler vendored) fera l'objet d'un intake tiers complet en Sb_ASSET_02.1.
```

### 5.4 Contrats sémantiques (Sb_ASSET_01.2 — non graphiques)
```yaml
asset_id: auren.contract.body-zone-taxonomy (+ auren.contract.body-zone-mapping)
author: repository (Sb_ASSET_01.2)
owner: MFE-DSS/workout-session-tracking — OPERATIONAL REPOSITORY CUSTODIAN
ip_ownership_status: not-legally-reviewed   # IP OWNERSHIP NOT LEGALLY VERIFIED
source_project: NOT APPLICABLE       # contrat interne, miroir de ZONE_LABELS / _WA_ZONE_TO_REGION
source_type: repository-authored
license_spdx: NOT APPLICABLE
attribution_required: no
usage_nature: reference-only          # contrat design, PAS servi par l'app (0 runtime_file)
modifications: taxonomie 11 zones + 6 macros + IDs SVG (Markdown + YAML JSON-compatible) ; 0 géométrie
tooling: hand-authored (Markdown/JSON-YAML)
reviewer: NOT YET REVIEWED            # acceptance = Sb_ASSET_01.2 human review (séparée)
review_date: NOT APPLICABLE
evidence: docs/SPRINT_Sb_ASSET_01_2_BODY_ZONE_TAXONOMY_MAPPING_REPORT.md
status: provisional
note: >
  Contrat sémantique, pas un asset graphique. Miroir de la vérité runtime, ne la remplace pas.
  Aucune autorisation d'intégration runtime.
```

### 5.5 Subset iconographique Tabler P0 (Sb_ASSET_02.1) — PREMIER INTAKE TIERS
```yaml
# Champs communs à toutes les entrées ci-dessous
author: Tabler Icons contributors / attribution according to official MIT LICENSE
owner: UPSTREAM RIGHTS HOLDER AS DECLARED BY OFFICIAL LICENSE — NOT AUREN IP OWNERSHIP
ip_ownership_status: not-legally-reviewed
source_project: tabler/tabler-icons
source_version: v3.45.0
vendor_tag: v3.45.0
vendor_commit: 975920ff99c12c4dc9e3fe61a03738330600f9b2
access_date: 2026-07-20
source_reference: official GitHub repository (https://github.com/tabler/tabler-icons) + pinned tag/commit
source_type: vendor
license_spdx: MIT
license_text_location: design/auren/LICENSES/tabler-MIT.txt
license_local_sha256: b740a1d46122672da62833e97f7e7c8a13fa85cbc7445b584b297cc00dde93db
attribution_required: yes
usage_nature: modified-derivative   # commentaire d'en-tête retiré
modifications: upstream metadata XML comment removed; LF/final newline normalized; geometry and functional SVG attributes unchanged
tooling: git object extraction + transparent stdlib normalization (no SVGO/resvg)
reviewer: NOT YET REVIEWED
review_date: NOT APPLICABLE
status: official-source-recorded / human-legal-review-required
```

| asset_id | semantic_id | upstream_path | upstream_blob_sha | upstream_sha256 | local_sha256 |
|---|---|---|---|---|---|
| `auren.icons.vendor.tabler.arrows-exchange` | `auren.icon.action.substitute` | `icons/outline/arrows-exchange.svg` | `721498aad6eefa7795af38c50d7990dc4ed81ddf` | `b37e7394c5fbeb57fd63…` | `b6e118f2c7b47a624964…` |
| `auren.icons.vendor.tabler.player-play` | `auren.icon.action.timer-start` | `icons/outline/player-play.svg` | `bb84dbe9e4166071e66414ab6ce1a3b12cc6fd5a` | `0178cf0262ec89422d63…` | `635b17e8ab5d04da3e90…` |
| `auren.icons.vendor.tabler.player-pause` | `auren.icon.action.timer-pause` | `icons/outline/player-pause.svg` | `b2a2a253d45357d8d3dceebbb84a8dc08050eda6` | `d7ad7676cd255ce1032a…` | `d0b40a7a745f9083e36d…` |
| `auren.icons.vendor.tabler.rotate` | `auren.icon.action.timer-reset` | `icons/outline/rotate.svg` | `abc20f17dfe83cbf7d5065f62c922a34217ae54d` | `795d0fb5a27b04d34378…` | `98e321e256a58222ceb3…` |
| `auren.icons.vendor.tabler.chevron-down` | `auren.icon.action.expand` | `icons/outline/chevron-down.svg` | `8650685dc264b07d6a93c11c3efa40ac2a39c327` | `06bd20b8cbe565b97046…` | `aef395a3cdd9fd8de602…` |
| `auren.icons.vendor.tabler.chevron-up` | `auren.icon.action.collapse` | `icons/outline/chevron-up.svg` | `194897aea5092cde42532d7984e3bbd56a588edc` | `bfe732786b05d90a0e48…` | `a60e86e1f61a67f28ebd…` |
| `auren.icons.vendor.tabler.bulb` | `auren.icon.information.guidance` | `icons/outline/bulb.svg` | `b6577b33d7f502a1c4c211da3252e3ccb0b7f7fd` | `3617f3cd3f835b03b9d8…` | `dacbb19c084baafb6ac0…` |
| `auren.icons.vendor.tabler.alert-triangle` | `auren.icon.information.warning` | `icons/outline/alert-triangle.svg` | `8d9332ef3ad33b78200e5df0dba04be9c06fdbb7` | `fc82f02dc9702293cb86…` | `fa52e1980826c8fa3cf9…` |
| `auren.icons.vendor.tabler.check` | `auren.icon.status.completed` | `icons/outline/check.svg` | `6e9114c4255cc68b82c6193418d1f02297edb8bf` | `fe359b27c74ed0f4f72b…` | `9c2121aef5a60a02a3bf…` |
| `auren.icons.vendor.tabler.menu-2` | `auren.icon.action.menu` | `icons/outline/menu-2.svg` | `277dd841bddb1b972a32186a2740079375cb7358` | `a0080a4db00a4168cfea…` | `30db8248598fa11626ad…` |

`selected_by`: `Sx_ASSET_02` spec (commit `fe97adc`). **Aucune** de ces 10 entrées n'utilise `verified`,
`approved` ou `legal-clearance-complete`. Preuves complètes : `source/icons/auren_icon_subset.yaml`.

## 6. Assets tiers
```
TABLER ICONS v3.45.0 (MIT) — PREMIER ET SEUL intake tiers à ce jour (Sb_ASSET_02.1, §5.5) :
10 SVG outline, source de design uniquement, HUMAN-LEGAL REVIEW PENDING, 0 app/static.
Licence officielle conservée : design/auren/LICENSES/tabler-MIT.txt (byte-identique).

HEALTH ICONS : ABSENT (aucun fichier, aucune licence ingérée — NOT REQUIRED FOR P0).
CUSTOM GLYPHS : ABSENT (CUSTOM GLYPH TRACK: NOT REQUIRED).
Tout nouveau vendor exigera une nouvelle entrée de provenance complète + licence officielle.
```
