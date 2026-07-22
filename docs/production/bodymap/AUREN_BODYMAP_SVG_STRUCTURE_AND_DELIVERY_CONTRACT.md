# AUREN — BodyMap SVG Structure & Delivery Contract

**Cycle** : `Sx_ASSET_03`. Contrat géométrique **normatif** du futur master (produit par `OPERATOR_ASSET_03.1`,
validé par `Sb_ASSET_03.2`). Ce document **définit** la structure ; il **ne dessine pas**.

> IDs SVG = **API figée** (`Sb_ASSET_01.2`). Toute évolution incompatible = nouvelle spec + migration de
> contrat. `zone-unknown` **interdit**.

---

## 1. Grille & viewBox (tranchés — non laissés à l'illustrateur)
| Paramètre | Valeur canonique | Justification |
|---|---|---|
| **viewBox master** | `0 0 240 200` | 2 vues (face+dos) de **100×200** logiques + gouttière 20 + marges 2×10 latérales → rendu côte-à-côte à 360 px (2×~170 px) et export compact |
| Vue **face** | centre x=**60**, plage utile x∈[10,110], y∈[10,190] | orthographique |
| Vue **dos** | centre x=**180**, plage utile x∈[130,230], y∈[10,190] | orthographique, **même échelle & même centre vertical** que la face |
| Gouttière centrale | x∈[110,130] (20 u) | séparation face/dos, aucune forme |
| Axe vertical face | x=60 · Axe vertical dos | x=180 | symétrie gauche/droite |
| Hauteur corps logique | ~180 u (y 10→190) | tête ~y10-30, tronc ~30-110, jambes ~110-190 (indicatif, non contraignant sur la stylisation) |
| Safe area | marge ≥ 8 u sur chaque bord | aucune zone rognée à 360/120/80/60 px |
| Unités | sans unité (coordonnées viewBox), **pas de px/mm dans le SVG** | scalable |

Le master contient **les deux vues dans un seul SVG** (`viewBox 0 0 240 200`). Un export compact ultérieur
(`Sb_ASSET_03.2+`) pourra recadrer/optimiser sans changer les IDs.

## 2. IDs stables obligatoires (API — figés)
**Racine & bases** :
```
auren-bodymap        (élément racine <svg> ou <g> racine)
body-front-base      (<g> silhouette de face, sans zone active)
body-back-base       (<g> silhouette de dos, sans zone active)
```
**Onze zones** (un `<g id="zone-<code>">` chacune, **unique dans tout le fichier**) :
```
zone-pecs · zone-delt_lat · zone-delt_post · zone-lats · zone-upper_back
zone-biceps · zone-triceps · zone-quads · zone-posterior · zone-calves · zone-core
```
**Interdit** : `zone-unknown` (unknown = état, pas une géométrie — cf. §4 states).

## 3. Structure des groupes (règles dures)
- Chaque `zone-<code>` = **un `<g>` unique** ; il peut contenir plusieurs sous-paths (face + dos + gauche +
  droite selon la zone).
- **Un ID stable n'apparaît qu'une fois.** Aucun enfant ne peut appartenir à deux zones. Aucun path ne fusionne
  deux codes métier. Les symétries gauche/droite **ne créent pas** de nouveaux codes.
- Les **IDs enfants sont techniques, non contractuels** : aucune logique métier n'en dépend.
- **Convention d'IDs enfants** (interne au master, ne modifie pas le Layer A) :
  ```
  geom-<zone>-<view>-<side>-<index>
    view = front | back
    side = left | right | center
    index = 1..n
  ex. geom-biceps-front-left-1 · geom-lats-back-right-1 · geom-core-front-center-1
  ```
- Quelle **vue** porte quelle zone (indicatif — l'illustrateur confirme à la production, le relecteur valide) :

| zone | face | dos | note |
|---|---|---|---|
| pecs | ✅ | — | poitrine (face) |
| delt_lat | ✅ | ✅ | épaule latérale visible des deux vues |
| delt_post | — | ✅ | arrière d'épaule (dos) |
| lats | — | ✅ | dos largeur |
| upper_back | — | ✅ | dos épaisseur (**functional-aggregate**) |
| biceps | ✅ | — | bras avant |
| triceps | — | ✅ | bras arrière |
| quads | ✅ | — | cuisse avant |
| posterior | — | ✅ | ischios/fessiers (**functional-aggregate**) |
| calves | ✅ | ✅ | mollets (arrière surtout ; visible des deux) |
| core | ✅ | — | abdos (face) |

## 4. États de présentation (5) — pilotés runtime, PAS codés dans le master
`neutral · primary · secondary · unknown · disabled`. **Aucune couleur métier dans le master** (les couleurs
= tokens runtime). Distinction **jamais par la seule couleur** :
- `primary` : remplissage plein + contour/structure.
- `secondary` : opacité réduite + contour/structure distincte.
- `neutral` : base passive.
- `unknown` : **aucune anatomie active** — silhouette neutre + texte adjacent « À qualifier » (jamais une
  erreur graphique, jamais de path inventé).
- `disabled` : contraste réduit + texte adjacent.

Le master fournit **la géométrie des zones** ; l'application des états (fill/opacity/classe) se fait au runtime
via CSS/tokens sur les `<g id="zone-*">`.

## 5. Contrat technique (validé par `Sb_ASSET_03.2`)
`fill` piloté runtime (pas de couleur figée), `stroke` `currentColor` si utilisé, `stroke-width` cohérent.
**Interdits dans le master** : `<script>` · event handler `on*` · URL externe · `xlink:href`/`href` externe ·
`<foreignObject>` · `<image>`/raster · `<text>`/police · `<filter>` · gradient · metadata supprimée · IDs
dupliqués · path partagé entre deux zones · couleur métier codée comme activation.

## 6. Livrables (remis à `OPERATOR_ASSET_03.1`)
### Canonique
`auren_bodymap_master.svg` — structure ci-dessus, viewBox `0 0 240 200`, 14 IDs stables, groupes zones.
### Source native éditable
Fichier natif original de l'outil (ex. `.svg` éditable structuré, ou format natif) — **livré dans l'archive
opérateur, pas nécessairement committé Git avant intake** ; nommé, **hashé (sha256)**, associé à l'outil+version,
référencé dans la provenance.
### Complémentaires
Registre des références · déclaration outils · déclaration composants tiers · déclaration IA · notes de
production · version + changelog · contact sheet face/dos · previews (cf. protocole de revue).
### Interdits de livraison
Uniquement des PNG · SVG aplati sans structure · IDs renommés · paths fusionnés entre zones · bitmap incorporé ·
police incorporée · script · URL externe · gradient · filtre · metadata supprimée · **source native manquante** ·
référence non déclarée.

## 7. Budgets (par artefact — cf. document dédié dans la spec §25)
- **export compact optimisé** : **≤ 12 Ko** (budget **bloquant**, réutilise le budget BodyMap connu).
- **master SVG canonique** : budget **indicatif** (structuré ≠ minifié ; pas de seuil bloquant arbitraire).
- **source native éditable** : **aucun budget** (le budget 12 Ko ne s'y applique pas).
- **preview raster** : indicatif (matériel de revue).

## 8. Gate
`auren_bodymap_master.svg` reste **NOT AUTHORIZED FOR APP INTEGRATION** pendant `Sx_ASSET_03` /
`OPERATOR_ASSET_03.1` / `Sb_ASSET_03.2`. Aucun fichier n'entre dans `app/static/` avant franchissement de
l'`ASSET INTEGRATION GATE`.
