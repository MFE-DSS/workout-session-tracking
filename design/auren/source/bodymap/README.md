# `design/auren/source/bodymap/` — BodyMap Design Source

**État actuel** : ce dossier contient **le contrat de mapping uniquement**
([`auren_bodymap_mapping.yaml`](auren_bodymap_mapping.yaml)). **Aucun master anatomique n'est présent.**

## Contenu autorisé aujourd'hui
- `auren_bodymap_mapping.yaml` — contrat sémantique versionné (Layer A), YAML 1.2 en syntaxe JSON-compatible
  (lu par la stdlib `json`, sans PyYAML). 0 géométrie.
- `README.md` — ce fichier.

## Ce qui n'est PAS ici (et pourquoi)
- **Aucun master anatomique / SVG / PNG / géométrie / path / coordonnée.** Aucun asset ne peut entrer sans
  **intake** (cf. [`../../AUREN_ASSET_INTAKE_CHECKLIST.md`](../../AUREN_ASSET_INTAKE_CHECKLIST.md)).
- Le futur **master humain** appartient à `OPERATOR_ASSET_03.1` (production humaine + validation anatomique).
- L'**intake technique** (optimisation, IDs, budgets) appartient à `Sb_ASSET_03.2`.
- L'**intégration runtime** appartient à `Sb_ASSET_04.1`, **après** franchissement de l'`ASSET INTEGRATION
  GATE`.

## Règle
```
La présence d'un fichier dans ce dossier NE signifie PAS qu'il est autorisé
dans app/static/. L'intégration runtime exige le franchissement de
l'ASSET INTEGRATION GATE (humaine / anatomique / juridique / mobile).
```

Le contrat `auren_bodymap_mapping.yaml` **miroir** la vérité runtime (`ZONE_LABELS`, `_WA_ZONE_TO_REGION`),
il ne la **remplace pas** dans `Sb_ASSET_01.2`.

## Master BodyMap accepté (Sb_ASSET_03.2, 2026-07-23)
- **`auren_bodymap_master.svg`** — master structuré (sha256 `dbb57db3…`), viewBox `0 0 240 200`, 14 IDs
  stables, 11 zones, 0 `zone-unknown`. Export compact : `../../exports/svg/auren_bodymap_compact.svg`
  (sha256 `8024fd4c…`, ≤ 12 Ko).
- **`auren_bodymap_source.yaml`** — registre de design-source (hashes, sources CC BY 4.0, statut).
- **Œuvre dérivée sous attribution** : BodyParts3D (base + 9 zones) + Servier Medical Art (`lats`, `core`),
  toutes deux CC BY 4.0 — cf. `../../LICENSES/`. `ai_usage: none`.
- **ACCEPTED FOR DESIGN SOURCE / HUMAN REVIEW PENDING** · **NOT AUTHORIZED FOR APP INTEGRATION.**
- Le master **ne remplace pas** le prototype runtime (`worked_area_body_map.html`) : le remplacement exigera
  le franchissement de l'`ASSET INTEGRATION GATE` (`Sx_ASSET_04`+).
