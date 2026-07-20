# AUREN — Icon Vendor Due Diligence (Sx_ASSET_02)

**Type** : recherche source-officielle — **DOCS-ONLY** (0 SVG/licence importé)
**Date d'accès** : **2026-07-20** (toutes les données ci-dessous relevées à cette date via sources primaires).
**Méthode** : API GitHub + pages officielles (`healthicons.org/about`). **Aucun** agrégateur / CDN / Iconify /
npm mirror / blog utilisé comme source juridique. Les liens tiers n'ont servi qu'à *découvrir* la source.

> Ce document établit **OFFICIAL LICENSE EVIDENCE RECORDED AT ACCESS DATE**, **PAS** `LEGAL CLEARANCE
> COMPLETE`. Aucun texte de licence n'est copié ici ; la copie officielle + vérification blob a lieu au build
> `Sb_ASSET_02.1`.

---

## 1. Tabler Icons

| Champ | Valeur (relevée 2026-07-20) |
|---|---|
| Source officielle | `https://github.com/tabler/tabler-icons` · `https://tabler.io/icons` |
| Dernière release stable | **`v3.45.0`** (publiée **2026-07-17T00:10:23Z**) |
| Tag (objet annoté) | `refs/tags/v3.45.0` → tag object SHA `64bfab222b4626fafb2301358dd41d3f3f3d84b2` |
| **Commit SHA du tag** | **`975920ff99c12c4dc9e3fe61a03738330600f9b2`** |
| Licence déclarée | **MIT** — © **Paweł Kuna**, 2020-2026 · `LICENSE` unique à la racine, couvrant les icônes |
| SPDX | `MIT` |
| Structure (au tag) | `icons/outline/` + `icons/filled/` |
| **Nombre d'icônes outline** | **5112** (`git/trees` recursive, non paginé) |
| Nombre d'icônes filled | 1054 |
| Format SVG réel (échantillon `outline/player-play.svg`) | `viewBox="0 0 24 24"`, `fill="none"`, `stroke="currentColor"`, `stroke-width="2"` |
| Métadonnées | commentaire d'en-tête `tags: […]` + `category:` par fichier (aliases exploitables) |
| Stabilité | projet mature (v3.x), releases mensuelles, licence stable MIT |

**Compatibilité contrat Auren** : la balise `<svg>` outline Tabler v3.45.0 est **déjà** `viewBox 0 0 24 24`,
`fill="none"`, `stroke="currentColor"`, `stroke-width="2"` — **exactement** le contrat SVG Auren
(`AUREN_STYLE_RULES.md §3`). Les commentaires d'en-tête (`tags:`/`category:`) devront être **strippés** à
l'intake (modification à déclarer dans la provenance).

**Éligibilité intake** : ✅ **ÉLIGIBLE** (MIT, source officielle, version+commit épinglables, format
compatible). Aucune conclusion juridique absolue : copie du `LICENSE` officiel + comparaison blob au build.

## 2. Health Icons

| Champ | Valeur (relevée 2026-07-20) |
|---|---|
| Source officielle | `https://healthicons.org` · `https://github.com/resolvetosavelives/healthicons` |
| Branche par défaut | `main` |
| **Tags / releases** | **AUCUN** (0 tag, 0 release) → épinglage **par commit SHA** obligatoire |
| **Dernier commit `main`** | **`891ace7addf4deb7a8b1ce8292d5906064fab36a`** (2025-09-04T11:18:13Z) |
| Structure | `public/icons/svg/{outline,filled}/…` (catégories : body, specialties, …) |

### 2.1 Distinction licence — POINT CRITIQUE (§8/§18)
Health Icons applique **deux licences distinctes** — ne **jamais** écrire « Health Icons = MIT » :

| Objet | Licence | Source |
|---|---|---|
| **Les icônes (assets SVG)** | **CC0 1.0 (domaine public)** | `healthicons.org/about` : « To the extent possible under law, Health Icons has waived all copyright and related or neighboring rights to icons ». |
| **Le code du site / repository** | **MIT** — © 2021 Resolve to Save Lives | fichier `LICENSE` du repo (couvre le *code*, pas les assets) |
| Packages React/React Native | npm (termes non détaillés sur about) | non pertinent (0 dépendance runtime autorisée) |

> **Le `license.spdx_id: MIT` renvoyé par l'API GitHub désigne le CODE du repo, PAS les icônes.** Les icônes
> sont **CC0**. La provenance d'un futur intake Health Icons doit porter `license_spdx: CC0-1.0` pour les
> fichiers d'icônes, avec référence à la page about + au fichier de licence assets officiel (à copier au build).

**Éligibilité intake** : ✅ éligible **CC0** pour les icônes SPÉCIFIQUEMENT si un concept corporel/mesure est
absent de Tabler ET améliore la compréhension sans médicaliser (cf. spec §Health Icons). **Épinglage par
commit SHA** (pas de tag). Verdict d'usage : voir la spec — **HEALTH ICONS NOT REQUIRED FOR P0** (Tabler +
texte couvrent le P0).

## 3. Risques
- **Health Icons sans tag** → dépendance à un commit SHA nu (moins lisible qu'un tag) : mitigé par
  l'épinglage explicite du SHA + comparaison blob au build.
- **Confusion licence** (MIT repo vs CC0 assets) → mitigée par la distinction ci-dessus, à re-vérifier à
  l'intake sur la source officielle.
- **Métaphores médicalisantes** Health Icons → filtrées par les règles anti-médicalisation de la spec.
- **Métadonnées Tabler** (commentaires) à stripper → modification déclarée en provenance.
- **Version flottante** → interdite : `v3.45.0` + commit `975920ff…` épinglés.

## 4. Conclusion d'éligibilité
- **Tabler Icons v3.45.0** (commit `975920ff…`, MIT) : **ÉLIGIBLE — SOURCE PRIMAIRE candidate P0.**
- **Health Icons** (commit `891ace7a…`, icônes **CC0** / code MIT) : **ÉLIGIBLE — source SECONDAIRE
  conditionnelle**, **NOT REQUIRED FOR P0**.
- État : **OFFICIAL LICENSE EVIDENCE RECORDED AT ACCESS DATE 2026-07-20** — la clearance juridique complète
  (copie licence + blob SHA + registre) relève de `Sb_ASSET_02.1`.

## Sources (officielles / primaires, 2026-07-20)
- Tabler repo : https://github.com/tabler/tabler-icons
- Tabler release v3.45.0 : https://github.com/tabler/tabler-icons/releases/tag/v3.45.0
- Tabler LICENSE : https://github.com/tabler/tabler-icons/blob/main/LICENSE
- Health Icons about/licence : https://healthicons.org/about
- Health Icons repo : https://github.com/resolvetosavelives/healthicons
- Health Icons LICENSE (code) : https://github.com/resolvetosavelives/healthicons/blob/main/LICENSE
