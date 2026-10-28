# `design/auren/source/bodymap/` — BodyMap Design Source

## État actuel (DA-04.0b, 2026-10-28)

**Le master anatomique est présent** depuis `Sb_ASSET_03.2` (2026-07-23) :

| Fichier | Rôle | sha256 |
|---|---|---|
| `auren_bodymap_master.svg` | master structuré, viewBox `0 0 240 200`, 14 IDs stables, 11 zones, 0 `zone-unknown` | `dbb57db3…` |
| `../../exports/svg/auren_bodymap_compact.svg` | export compact (≤ 12 Ko) | `8024fd4c…` |
| `auren_bodymap_source.yaml` | registre de design-source (hashes, sources, statuts, décision, contraintes) | — |
| `auren_bodymap_mapping.yaml` | contrat sémantique (Layer A) : 11 zones, 6 macros, IDs stables, 0 géométrie | — |

**Statut** :

```
ACCEPTED FOR DESIGN SOURCE / HUMAN REVIEW PENDING
AUTHORIZED FOR AUREN INTERNAL BUILDS WITH CONSTRAINTS
PUBLIC RELEASE NOT AUTHORIZED
```

**Décision du propriétaire** (Martin Feldmann, 2026-10-28) : `ACCEPT_INTERNAL_P0_WITH_CONSTRAINTS`, voie (b)
du rapport DA-04.0. Base : les deux sources sont sous CC BY 4.0, qui autorise l'adaptation sous
attribution. C'est un compromis de gouvernance, **pas un avis juridique**.

**Portée** : les builds **internes** de l'app mobile AUREN (client de développement, distribution interne).
**Jamais** le runtime web (inscription ouverte), **jamais** une publication sur un store public.

**Contraintes** (registre, `runtime_constraints`) :

1. Attribution visible des **deux** sources dans un écran « À propos / Licences », chacune marquée
   **adaptée** — texte exact dans le registre (`attribution_fr`, `license_url`).
2. La mention, avec l'attribution : *Visualisation non médicale — revue anatomique professionnelle non
   réalisée.*
3. Aucune revendication d'activation, de recrutement, d'intensité, de pourcentage, de récupération ou de
   risque.
4. Géométrie intouchée : des **caméras** (viewBox) sur le master, jamais une anatomie redessinée ou
   régénérée.
5. **Diffusion publique bloquée** jusqu'à une revue anatomique professionnelle et une revue juridique
   externe (`missing_for_public_release`).

Reste à faire avant tout montage dans un écran produit : la **surface d'attribution** du client mobile
(`attribution_surface: not-yet-implemented`, `missing_for_runtime`). Elle est livrée avec `DA-04.1`.

## Rôle du BodyMap V1 (verrouillé par l'opérateur, 2026-10-28)

```
BodyMap V1 = localisation fonctionnelle
```

Il répond à : **où se situe principalement cette famille musculaire ?**
Il ne répond **pas** à : quelle structure anatomique précise travaille, et dans quelle proportion.

Il sert le triptyque Push A, la carte de séance, le résumé de zones, l'historique, la sélection visuelle.
L'illustration anatomique riche (détail d'exercice, fiche éducative, biomécanique) relève d'**Anatomy V2** :
même taxonomie, mêmes 11 IDs, géométrie nettement plus nette — backlog hors chemin critique
(`AUREN_VISUAL_BACKBONE §8.4`). Le master **n'est pas** remplacé par une génération IA en attendant : ce
serait perdre la traçabilité anatomique.

## Ce qui est permis aujourd'hui

- Utiliser le master comme **source de design** : planches, recadrages, galeries de revue.
- L'afficher dans les **builds internes** de l'app mobile, sous les contraintes ci-dessus, en caméras
  (viewBox) sur le master.
- **Jamais** : une seconde anatomie, une régénération par IA, un trait redessiné, une frontière de zone
  déplacée pour une composition.
- **Jamais** dans le runtime web (`app/static/`, gabarits Jinja).

## Provenance

**Œuvre dérivée sous attribution** : BodyParts3D (base + 9 zones) et Servier Medical Art (`lats`, `core`),
toutes deux CC BY 4.0 — `../../LICENSES/`. `ai_usage: none`. Détail : `../../AUREN_ASSET_PROVENANCE.md`.

## Règle

```
La présence d'un fichier dans ce dossier NE signifie PAS qu'il est autorisé
dans l'app. Toute autorisation runtime est portée par le registre (date, base
de revue, hashes, portée, contraintes), et ce README, la checklist d'intake et
la provenance la disent aussi (garde : tests/test_auren_bodymap_master.py).
```

## Historique

- **Avant `Sb_ASSET_03.2`** (contrat `Sb_ASSET_01.2`) : ce dossier ne contenait que le contrat de mapping ; aucun master. Le master humain relevait d'`OPERATOR_ASSET_03.1`, l'intake technique de `Sb_ASSET_03.2`, l'intégration runtime de `Sb_ASSET_04.1` après l'`ASSET INTEGRATION GATE`.
- **`Sb_ASSET_03.2` (2026-07-23)** : master et compact acceptés en design source, reproductibilité vérifiée (package v2 `f45e0dbf…`).
- **DA-04.0 (2026-10-28)** : le README se contredisait (« aucun master présent », puis « master accepté ») ; un seul état est tenu ici. Gate runtime statué : OUTCOME B — NOT AUTHORIZED FOR APP INTEGRATION (technique passe ; manquaient revue anatomique, revue juridique, surface d'attribution).
- **DA-04.0b (2026-10-28)** : l'opérateur choisit la voie (b) — `ACCEPT_INTERNAL_P0_WITH_CONSTRAINTS`, builds internes seulement, diffusion publique bloquée. Le contrat de mapping cesse de dire `geometry_status: NOT YET PRODUCED`.
- Le master **ne remplace pas** le prototype runtime web (`worked_area_body_map.html`).
- Le contrat `auren_bodymap_mapping.yaml` **miroir** la vérité runtime (`ZONE_LABELS`, `_WA_ZONE_TO_REGION`) ; il ne la remplace pas.
