# `design/auren/source/bodymap/` — BodyMap Design Source

## État actuel (DA-04.0, 2026-10-28)

**Le master anatomique est présent** depuis `Sb_ASSET_03.2` (2026-07-23) :

| Fichier | Rôle | sha256 |
|---|---|---|
| `auren_bodymap_master.svg` | master structuré, viewBox `0 0 240 200`, 14 IDs stables, 11 zones, 0 `zone-unknown` | `dbb57db3…` |
| `../../exports/svg/auren_bodymap_compact.svg` | export compact (≤ 12 Ko) | `8024fd4c…` |
| `auren_bodymap_source.yaml` | registre de design-source (hashes, sources, statuts) | — |
| `auren_bodymap_mapping.yaml` | contrat sémantique (Layer A) : 11 zones, 6 macros, IDs stables, 0 géométrie | — |

**Statut** :

```
ACCEPTED FOR DESIGN SOURCE / HUMAN REVIEW PENDING
NOT AUTHORIZED FOR APP INTEGRATION
```

Le gate d'intégration runtime a été **statué par DA-04.0** (`docs/SPRINT_Sb_DA_04_0_BODYMAP_INTAKE_RESOLUTION_REPORT.md`) : **il ne passe pas**. Ce qui manque, exactement :

1. **Revue anatomique** — aucune n'est enregistrée (`professional_anatomical_review: not-claimed`, provenance `reviewer: NOT YET REVIEWED`). Elle peut être professionnelle, ou une décision explicite du propriétaire qui en tient lieu, avec ses contraintes.
2. **Revue juridique** de l'œuvre dérivée CC BY 4.0 (`legal_review: required`).
3. **Surface d'attribution** dans le client qui l'affichera (`attribution_surface: not-yet-implemented`) : l'app mobile n'en a aucune.

La revue **technique** est faite et passe : `svg` / `g` / `path` seulement, une couleur `currentColor`, aucun raster, aucune police, aucune URL, aucune transformation ; tout est rendu tel quel par `react-native-svg` (`tests/test_auren_bodymap_master.py`).

## Ce qui est permis aujourd'hui

- Utiliser le master comme **source de design** : planches, recadrages et galeries de revue, **hors runtime**.
- **Jamais** : une seconde anatomie, une régénération par IA, un trait redessiné, une frontière de zone déplacée pour une composition.
- **Jamais** dans un écran de l'app (web `app/static/`, mobile `clients/mobile/`) tant que le registre dit `runtime_authorization: blocked`. L'emplacement BodyMap de la carte de série (`SESSION-CARD-R1`) reste un emplacement nommé.

## Provenance

**Œuvre dérivée sous attribution** : BodyParts3D (base + 9 zones) et Servier Medical Art (`lats`, `core`), toutes deux CC BY 4.0 — `../../LICENSES/`. `ai_usage: none`. Détail : `../../AUREN_ASSET_PROVENANCE.md`.

## Règle

```
La présence d'un fichier dans ce dossier NE signifie PAS qu'il est autorisé
dans l'app. L'intégration runtime exige que le registre passe à une
autorisation explicite (date, base de revue, hashes, contraintes), et que ce
README, la checklist d'intake et la provenance le disent aussi.
```

## Historique

- **Avant `Sb_ASSET_03.2`** (contrat `Sb_ASSET_01.2`) : ce dossier ne contenait que le contrat de mapping ; aucun master. Le master humain relevait d'`OPERATOR_ASSET_03.1`, l'intake technique de `Sb_ASSET_03.2`, l'intégration runtime de `Sb_ASSET_04.1` après l'`ASSET INTEGRATION GATE`.
- **`Sb_ASSET_03.2` (2026-07-23)** : master et compact acceptés en design source, reproductibilité vérifiée (package v2 `f45e0dbf…`).
- **DA-04.0 (2026-10-28)** : le README se contredisait (« aucun master présent », puis « master accepté ») ; un seul état est tenu ici, et le gate runtime est statué.
- Le master **ne remplace pas** le prototype runtime web (`worked_area_body_map.html`).
- Le contrat `auren_bodymap_mapping.yaml` **miroir** la vérité runtime (`ZONE_LABELS`, `_WA_ZONE_TO_REGION`) ; il ne la remplace pas. Son champ `geometry_status` dit encore `NOT YET PRODUCED` : c'est une spec versionnée épinglée par une garde, son amendement est proposé à l'opérateur (rapport DA-04.0), pas fait en silence.
