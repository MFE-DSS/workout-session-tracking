# `AUREN-MARK-V1` — design source (`DA-03.2`)

Autorité visuelle : `docs/strategy/AUREN_VISUAL_CONTRACT.md` §18 (🔒 LOCKED, opérateur, 2026-10-27).
Statut d'asset : `provisional` (`AUREN_VISUAL_ASSET_MANIFEST.md`, entrée `auren.brand.mark.v1`) — le nom
Auren reste en clearance externe ; la marque n'est montée sur **aucun** écran produit.

## Une marque, trois dessins optiques

| Fichier | Grille | Taille de rendu | Exact au pixel à |
|---|---|---|---|
| `mark-primary.svg` | 32 | **20 px et plus** | 32 · 64 · 128 |
| `mark-compact.svg` | 16 | **16 à 19 px** | 16 |
| `mark-micro.svg` | 12 | **12 à 15 px** | 12 |
| — | — | **moins de 12 px : la marque n'est pas rendue** | — |

Ce sont trois tailles optiques **d'une seule marque**, pas trois marques. L'appelant ne choisit jamais
le dessin : `AurenMark` (`clients/mobile/src/ui/brand/AurenMark.tsx`) le prend dans la taille
demandée, et ne rend rien sous 12 px.

## Ce qui la forme

- le **curseur actif**, tenu par l'opérateur (en haut, haut et massif) ;
- le **repère de référence**, posé par le système (en bas, bas et plat) ;
- **un seul axe de visée** : les deux fentes sont alignées ;
- **le vide entre eux** — haut d'une fente. Le rail n'est **pas** dessiné : il est ce vide.

Proportions héritées de `ActiveCursor` / `ReferenceMarker` (`clients/mobile/src/ui/calibration/geometry.ts`) :
mur : fente = 2,5 : 1, même largeur pour les deux pièces, fentes ouvertes en haut. Écart, proportions
des fentes, rapport mur / fente, alignement, silhouette et nombre de primitives (2) ne changent
**qu'après un nouvel arbitrage explicite de l'opérateur**.

## Couleur

Monochrome d'abord : les fichiers ne portent **aucune couleur** (`currentColor`), l'encre est
injectée à l'exécution, toujours un token existant. Le traitement en deux couleurs — curseur en
`signal`, repère en `system` — est une **expression de marque / d'icône d'application**, contextuelle ;
ce n'est ni la géométrie canonique ni un traitement obligatoire.

La géométrie de ces fichiers et celle du composant sont vérifiées identiques par
`tests/test_auren_mark_v1.py`.
