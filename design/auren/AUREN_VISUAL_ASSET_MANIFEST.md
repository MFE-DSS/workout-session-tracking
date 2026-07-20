# AUREN — Visual Asset Manifest

**Scaffold** : `Sb_ASSET_01.1`. Registre des assets visuels Auren — schéma normatif + entrées.
**Aucun asset produit ici** ; les entrées ci-dessous **référencent** des objets runtime existants (sans
les copier) et documentent des masters **futurs** (non créés).

---

## 1. Schéma normatif (champs obligatoires)

| Champ | Description |
|---|---|
| `id` | identifiant stable, namespacé (`auren.<domaine>.<objet>[.variant]`) — traité comme une API |
| `version` | semver de l'asset (`0.x` = pré-approbation) |
| `type` | catégorie (voir §3) |
| `status` | un des 8 statuts bornés (§2) |
| `format` | `svg` \| `png` \| `webp` (jamais WebP pour BodyMap/icônes) |
| `source_file` | chemin du fichier **source de design** (`design/auren/source/…`) — `NOT YET PRODUCED` si futur |
| `runtime_file` | chemin du fichier **servi par l'app** (`app/static/…`) — `NOT APPLICABLE` si pas intégré |
| `semantic_contract` | contrat métier (zones, rôle, mapping) — pour le BodyMap : les 11 zones |
| `surfaces` | surfaces autorisées (`session-compact`, `body-intelligence`, `pwa`, `head`, `shell`, …) |
| `accessibility` | rôle (`decorative`\|`action`), `semantic_source` (`adjacent-text`\|`aria-label`), non-color-cue |
| `license` | identifiant SPDX ou `UNKNOWN — MANUAL VERIFICATION REQUIRED` |
| `provenance` | pointeur vers `AUREN_ASSET_PROVENANCE.md` (asset_id) |
| `review` | états de revue (product/technical/accessibility/legal/anatomical/mobile) |
| `budgets` | budget de poids cible (cf. spec §Budgets) |
| `consumers` | modules/templates qui consomment l'asset |
| `deprecated_by` | id du remplaçant si `deprecated`, sinon `NONE` |

### Valeurs pour champ non connu (à distinguer strictement)
- **`NOT APPLICABLE`** — le champ n'a pas de sens pour cet asset (ex. `runtime_file` d'un master non intégré).
- **`UNKNOWN — MANUAL VERIFICATION REQUIRED`** — l'information **devrait** exister mais n'est pas établie.
- **`NOT YET REVIEWED`** / **`NOT YET PRODUCED`** — étape non atteinte (revue non faite / asset non créé).
Ne **jamais** utiliser `N/A` pour masquer un `UNKNOWN`.

## 2. Statuts autorisés (exactement 8)
| Statut | Condition |
|---|---|
| `draft` | en cours de définition, non livrable |
| `provisional` | en production/référencé mais **non finalisé** (ex. asset PWA brand-bearing avant clearance nom) |
| `human-review-required` | en attente de revue humaine (produit/design) |
| `anatomical-review-required` | BodyMap en attente de relecture anatomique/biomécanique |
| `legal-review-required` | en attente de contrôle licence/PI |
| `approved` | **toutes** les revues requises passées (voir ci-dessous) |
| `deprecated` | remplacé (`deprecated_by` renseigné) |
| `rejected` | refusé (motif documenté) |

**`approved` exige au minimum** : product review · technical review · accessibility review · license
review · mobile review (si surface mobile) · **anatomical review** (pour BodyMap). Aucun asset ne peut
être `approved` avec `license: UNKNOWN`.

## 3. Types
`anatomical-map-prototype` · `anatomical-map-master` · `brand-runtime-asset` · `functional-inline-icon-set`
· `functional-icon` · `brand-mark` · `wordmark` · `favicon` · `pwa-icon` · `maskable-icon`.

---

## 4. Entrées initiales (runtime existant — référencé, non copié)

### 4.1 BodyMap prototype
```yaml
id: auren.runtime.bodymap.prototype
version: 0.1.0
type: anatomical-map-prototype
status: provisional            # jamais 'approved' comme master final
format: svg                    # SVG inline (SSR, pas de fichier source séparé)
source_file: NOT YET PRODUCED  # le master original = Sx_ASSET_03 / OPERATOR_ASSET_03.1
runtime_file: app/templates/_partials/worked_area_body_map.html
semantic_contract:
  zones: [pecs, delt_lat, delt_post, lats, upper_back, biceps, triceps, quads, posterior, calves, core]
  unknown_state: business-neutral   # 'unknown' n'est PAS une zone anatomique
  macro_regions: [Chest, Shoulders, Back, Arms, Legs, Core]
surfaces: [session-compact, body-intelligence]
accessibility:
  role: decorative
  semantic_source: adjacent-text
  aria: aria-hidden="true" focusable="false"
license: NOT APPLICABLE          # œuvre du repository, pas de licence tierce
provenance: auren.runtime.bodymap.prototype   # cf. AUREN_ASSET_PROVENANCE.md
review: {product: passed(Sb_BODYMAP_01.1), technical: passed, accessibility: passed, anatomical: NOT YET REVIEWED, mobile: passed}
budgets: {inline: "≤12Ko cible pour le master compact optimisé"}
consumers: [exercise_card.html, body-intelligence]
deprecated_by: NONE            # sera remplacé par auren.bodymap.master après gate
note: >
  PROTOTYPE — TO REPLACE AFTER GATE. Silhouette SVG inline CSS/SSR (Sb_BODYMAP_01.1),
  mapping 11 zones → 6 macros déjà présent. Le master anatomique original reste à produire.
```

### 4.2 Assets PWA (brand-bearing, provisoires)
Motif commun : **Brand-bearing asset — professional name clearance open.** `type: brand-runtime-asset` /
`brand-mark` / `favicon` / `pwa-icon` / `maskable-icon`. `status: provisional`. Non supprimés, en
production.

| id | runtime_file | type | status | format | source_file |
|---|---|---|---|---|---|
| `auren.runtime.pwa.mark` | `app/static/icons/auren-mark.svg` | brand-mark | provisional | svg | NOT YET PRODUCED |
| `auren.runtime.pwa.favicon` | `app/static/icons/favicon.svg` | favicon | provisional | svg | NOT YET PRODUCED |
| `auren.runtime.pwa.apple-touch` | `app/static/icons/apple-touch-icon.png` | pwa-icon | provisional | png | NOT YET PRODUCED |
| `auren.runtime.pwa.icon.192` | `app/static/icons/icon-192.png` | pwa-icon | provisional | png | NOT YET PRODUCED |
| `auren.runtime.pwa.icon.512` | `app/static/icons/icon-512.png` | pwa-icon | provisional | png | NOT YET PRODUCED |
| `auren.runtime.pwa.maskable.512` | `app/static/icons/icon-maskable-512.png` | maskable-icon | provisional | png | NOT YET PRODUCED |

- **provenance** : recolorés/générés par `Sb_UI_10.2` (glyphe haltère existant recoloré `#f25f3a`→`#C8A24B`,
  PNG rasterisés via `sips`). `license: NOT APPLICABLE` (repository-authored). `review.legal: NOT YET
  REVIEWED` (nom Auren brand-bearing).
- **surfaces** : `pwa`, `head`, `manifest`. `accessibility.role: decorative` (favicon/mark) ; l'apple-touch
  et les PNG portent le nom via le manifest.
- **Note** : il n'existe **pas** de `maskable-192` dans le runtime (seulement maskable-512) — non inventé.

### 4.3 Icônes inline du shell
```yaml
id: auren.runtime.shell.inline-icons
version: 0.1.0
type: functional-inline-icon-set
status: provisional
format: svg                    # SVG inline (base.html : bottom nav + rail)
source_file: NOT YET PRODUCED  # le subset gouverné = Sx_ASSET_02 / Sb_ASSET_02.1
runtime_file: app/templates/base.html
surfaces: [shell]
accessibility: {role: decorative, aria: aria-hidden="true" focusable="false", label_source: adjacent-text}
license: NOT APPLICABLE
provenance: auren.runtime.shell.inline-icons   # repository-authored (Sb_UI_03.1)
review: {product: passed(Sb_UI_03.x), technical: passed, accessibility: passed}
budgets: {inline: "≤2Ko par icône cible"}
consumers: [base.html bottom-nav, base.html rail]
deprecated_by: NONE            # subset Tabler/custom gouverné = Sx_ASSET_02+
note: >
  repository-authored (dessinées à la main en Sb_UI_03.1) ; upstream provenance = NOT APPLICABLE.
  Le subset iconographique gouverné (Tabler vendored + custom) sera défini par Sx_ASSET_02.
```

## 5. Masters futurs (documentés, NON créés)
| id (futur) | type | statut d'entrée | produit par |
|---|---|---|---|
| `auren.bodymap.master` | anatomical-map-master | `NOT YET PRODUCED` → `anatomical-review-required` | `OPERATOR_ASSET_03.1` + `Sb_ASSET_03.2` |
| `auren.brand.wordmark` | wordmark | `NOT YET PRODUCED` — brand-bearing, provisional until clearance | build futur conditionnel au nom |
| `auren.icons.vendor.tabler.<name>` | functional-icon | **INGÉRÉ (Sb_ASSET_02.1)** → voir §5ter (`legal-review-required`, non `approved`) | `Sb_ASSET_02.1` ✅ |

**Aucun** de ces fichiers n'existe (pas de faux master). Le champ `status: approved` **n'apparaît sur
aucune entrée** de ce manifest initial.

## 5bis. Governance and semantic contracts (Sb_ASSET_01.2)
Ces objets sont des **contrats**, pas des assets graphiques : ils **ne comptent pas** dans l'inventaire des
assets visuels produits (0 SVG/PNG). Statut `provisional` (jamais `approved`).

| id | type | status | source_file | note |
|---|---|---|---|---|
| `auren.contract.body-zone-taxonomy` | semantic-contract | provisional | `design/auren/AUREN_BODY_ZONE_TAXONOMY.md` | 11 zones + labels FR + 6 macros + IDs SVG. Acceptance tracked by Sb_ASSET_01.2 human review. No runtime integration authorization. |
| `auren.contract.body-zone-mapping` | semantic-contract | provisional | `design/auren/source/bodymap/auren_bodymap_mapping.yaml` | Contrat machine-lisible (YAML 1.2 / JSON-compatible, stdlib `json`). 0 géométrie. Miroir de `ZONE_LABELS` + `_WA_ZONE_TO_REGION`, ne les remplace pas. Acceptance tracked by Sb_ASSET_01.2 human review. No runtime integration authorization. |

- `type: semantic-contract` (nouveau) — distinct des types d'assets graphiques (§3). Aucun contrat n'a de
  `runtime_file` (ils ne sont **pas** servis par l'app) ni de géométrie.
- **`BODYMAP COMPACT MACROS ARE NOT RADAR_AXES`** : le contrat documente explicitement la séparation
  présentation (6 macros) vs analytics (`RADAR_AXES`), non modifiés.
- Aucun master futur n'est passé `source_file: existing` — les masters restent `NOT YET PRODUCED` (§5).

## 5ter. Functional icon subset — Tabler P0 (Sb_ASSET_02.1)

Premier **intake tiers** de la source de design. **Tabler Icons v3.45.0** (commit `975920ff…`), **MIT**.
Icônes SVG **outline** vendored dans `design/auren/source/icons/vendor/tabler/v3.45.0/outline/`. **Aucune**
`status: approved` ; **HUMAN REVIEW PENDING** ; `runtime_file: NOT APPLICABLE` (0 intégration app).

| id | source_file | semantic_contract | surfaces | a11y role | source_bytes | status |
|---|---|---|---|---|---|---|
| `auren.icons.vendor.tabler.arrows-exchange` | `source/icons/vendor/tabler/v3.45.0/outline/arrows-exchange.svg` | `auren.icon.action.substitute` | exercise-card·session-console·history-row | decorative | 268 | `legal-review-required` |
| `auren.icons.vendor.tabler.player-play` | `source/icons/vendor/tabler/v3.45.0/outline/player-play.svg` | `auren.icon.action.timer-start` | rest-timer·session-console | action | 244 | `legal-review-required` |
| `auren.icons.vendor.tabler.player-pause` | `source/icons/vendor/tabler/v3.45.0/outline/player-pause.svg` | `auren.icon.action.timer-pause` | rest-timer·session-console | action | 397 | `legal-review-required` |
| `auren.icons.vendor.tabler.rotate` | `source/icons/vendor/tabler/v3.45.0/outline/rotate.svg` | `auren.icon.action.timer-reset` | rest-timer·session-console | action | 260 | `legal-review-required` |
| `auren.icons.vendor.tabler.chevron-down` | `source/icons/vendor/tabler/v3.45.0/outline/chevron-down.svg` | `auren.icon.action.expand` | exercise-card·program-card·history-row | decorative | 237 | `legal-review-required` |
| `auren.icons.vendor.tabler.chevron-up` | `source/icons/vendor/tabler/v3.45.0/outline/chevron-up.svg` | `auren.icon.action.collapse` | exercise-card·program-card·history-row | decorative | 238 | `legal-review-required` |
| `auren.icons.vendor.tabler.bulb` | `source/icons/vendor/tabler/v3.45.0/outline/bulb.svg` | `auren.icon.information.guidance` | exercise-card·session-console | decorative | 395 | `legal-review-required` |
| `auren.icons.vendor.tabler.alert-triangle` | `source/icons/vendor/tabler/v3.45.0/outline/alert-triangle.svg` | `auren.icon.information.warning` | form-feedback·session-console·exercise-card | decorative | 409 | `legal-review-required` |
| `auren.icons.vendor.tabler.check` | `source/icons/vendor/tabler/v3.45.0/outline/check.svg` | `auren.icon.status.completed` | form-feedback·history-row·session-console | decorative | 240 | `legal-review-required` |
| `auren.icons.vendor.tabler.menu-2` | `source/icons/vendor/tabler/v3.45.0/outline/menu-2.svg` | `auren.icon.action.menu` | secondary-nav | action | 285 | `legal-review-required` |

Champs communs par entrée : `version: 0.1.0` · `type: functional-icon` · `format: svg` · `license: MIT`
· `provenance: <asset_id>` (cf. `AUREN_ASSET_PROVENANCE.md`) · `review: {product: NOT YET REVIEWED,
technical: automated checks passed, accessibility: NOT YET REVIEWED, legal: NOT YET REVIEWED, mobile:
NOT YET REVIEWED}` · `budgets: {source_bytes: <réel>, maximum: 2048}` · `consumers: NOT YET INTEGRATED` ·
`deprecated_by: NONE`. Preuves complètes (blob SHA, sha256) : `source/icons/auren_icon_subset.yaml`.

## 6. Gate & nom
`ASSET INTEGRATION GATE: BLOCKED PENDING HUMAN / ANATOMICAL / LEGAL / MOBILE APPROVALS`. Nom Auren =
**WORKING PRODUCT NAME · EXTERNAL PROFESSIONAL CLEARANCE OPEN** — les assets brand-bearing restent
`provisional`.
