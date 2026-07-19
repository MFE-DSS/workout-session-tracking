# AUREN — Asset Provenance Registry

Registre de **provenance** de tout asset visuel Auren. **Aucun asset tiers n'est ingéré à ce jour.**
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

## 6. Assets tiers
```
NONE. Aucun asset tiers n'a été accepté dans le pack source Auren.
Le premier intake tiers (subset Tabler) relève de Sb_ASSET_02.1 et exigera une entrée
de provenance complète + le texte de licence officiel conservé dans LICENSES/.
```
