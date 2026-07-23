# SB_ASSET_03.1 — Manifeste des artefacts externes

> ```
> PACKAGE V1: HISTORICAL / SUPERSEDED
> CURRENT PACKAGE: V2 — see SB_ASSET_03_1_REPRODUCIBILITY_CLOSURE.md
> ```
> Le package v1 (`098d1b42…`) décrit ci-dessous a **bloqué à l'intake** (`NON-REPRODUCIBLE OUTPUT`). Il est
> **conservé comme preuve historique**. Le package courant est le **v2 déterministe** (`f45e0dbf…`),
> auto-descriptif et rejouable — cf. `SB_ASSET_03_1_REPRODUCIBILITY_CLOSURE.md`. Master et compact
> **inchangés**.

**Cycle** : `Sx_ASSET_03` (amendé SOURCE-REUSE-FIRST) · **Build** : `Sb_ASSET_03.1` · **Date** : 2026-07-23

> **Aucun de ces artefacts n'est committé.** Ils vivent dans un espace de travail **hors de tout dépôt et
> worktree Git**, conservé pour `Sb_ASSET_03.2`. Ce document en donne l'inventaire et les empreintes.

---

## 1. Package d'intake

| Champ | Valeur |
|---|---|
| Nom | `auren_bodymap_sb_asset_03_1_intake_package.zip` |
| Taille | **14 495 063 o** (~13,8 Mio) |
| **SHA-256** | `098d1b4276d79b771a3ccd97307811160812485dcbe610513d682568678738b1` |
| Entrées | **60** |

### Contenu
```
master/      auren_bodymap_master_proto.svg · auren_bodymap_compact.svg
             auren_bodymap_compact_raw.svg
procedure/   auren_bodymap_derivation.blend · render_manifest.json
             assembly_report_master.json · assembly_report_compact.json
             tooling-gate-resolved.md
             scripts/  (8 scripts Python stdlib)
provenance/  selected_meshes.json · topology_report.json
             official-pages.sha256 · bodyparts3d_lic_2026-07-23.html
             license-revalidation.md · acquisition-reachability.md
validation/  validation_report.json
review/      fma-zone-coverage.md · servier-pptx-verdict.md
previews/    32 PNG · previews_manifest.json
```

### Exclusions délibérées
`acquisition/archives/*.zip` (198 Mo d'OBJ BodyParts3D) · `SMART-Muscles.pptx` · `renders/raw/*.bmp`
(104 Mo) · `selected-meshes/**` (55 OBJ).

**Motif** : ces sources restent dans l'espace d'acquisition **avec leurs SHA-256** (cf. registre de
provenance). Les embarquer redistribuerait des archives tierces sans nécessité — la procédure est rejouable
à partir de leurs empreintes et des URL officielles.

## 2. Artefacts principaux

| Artefact | Taille (o) | SHA-256 |
|---|---:|---|
| `auren_bodymap_master_proto.svg` | 59 620 | `dbb57db333863434442b476277170017db442d83e2eced6e7191266ee9ecfa73` |
| `auren_bodymap_compact.svg` | **8 615** | `8024fd4ced62ca2010808bf85f94c3eaca4d334dde2b7c3b7683c3e5a4676c9a` |

## 3. Arborescence de l'espace externe

```
acquisition/      archives (BodyParts3D ×2, Servier ×2) · indexes ×3
                  official-pages · source-checksums
selected-meshes/  55 OBJ répartis en 10 dossiers de zone
blender/          scripts (8 .py) · scene (auren_bodymap_derivation.blend)
renders/          raw (13 BMP) · contrôles visuels PNG
vector/           working (traces intermédiaires) · canonical · compact
previews/         32 SVG + 32 PNG
review/           couverture FMA · verdict PPTX Servier · revue multi-sources
manifests/        7 JSON (meshes, topologie, rendus, assemblages, validation,
                  previews, package)
logs/             gate d'outillage · revalidation de licence · accessibilité
```

## 4. Rapports machine-lisibles

| Fichier | Contenu |
|---|---|
| `selected_meshes.json` | 55 maillages : zone, FMA ID, nom officiel, element file, membre d'archive, octets, SHA-256, côté |
| `topology_report.json` | métriques par maillage + paires en intersection |
| `render_manifest.json` | système de coordonnées, bbox, centre, `ortho_scale`, résolution, 13 rendus |
| `assembly_report_master.json` / `_compact.json` | paramètres Potrace, cadre, viewBox, transformation Servier |
| `validation_report.json` | 40 contrôles master + 41 compact, avec détails |
| `previews_manifest.json` | 32 previews + les 6 cas `primary + secondary` retenus |
| `intake_package_manifest.json` | 60 entrées hachées individuellement |

## 5. Traçabilité

Chaque coordonnée du prototype remonte à une source sous licence : les archives officielles hachées et la
planche Servier hachée. Les scripts embarqués rejouent la chaîne **sans réseau** dès lors que les archives
sont réacquises depuis leurs URL officielles.

## Verdict

**Verdict :** **PACKAGE D'INTAKE PRODUIT ET HACHÉ.** `auren_bodymap_sb_asset_03_1_intake_package.zip`,
**14 495 063 o**, **60 entrées hachées individuellement**, SHA-256 `098d1b42…`. Contient master, compact,
scène Blender, 8 scripts stdlib, provenance, topologie, validation, revues et **32 previews**. Archives
sources et rendus intermédiaires **délibérément exclus** mais **hachés au registre de provenance**. **Aucun
artefact binaire n'est committé** ; l'espace externe est conservé intact pour `Sb_ASSET_03.2`.
