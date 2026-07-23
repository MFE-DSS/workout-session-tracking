# NOTICE — Servier Medical Art (source complémentaire de dérivation du BodyMap)

**Licence** : Creative Commons Attribution 4.0 International (**CC BY 4.0**) — voir [`CC-BY-4.0.txt`](CC-BY-4.0.txt).
**Revalidée le** : 2026-07-23 sur `https://smart.servier.com/`.

## Attribution obligatoire (texte exact)
```
Image adapted from Servier Medical Art, licensed under CC BY 4.0
```

## Portée dans le BodyMap Auren
- **2 zones** : `lats` (grand dorsal, vue dos) et `core` (paroi abdominale antérieure, agrégat fonctionnel),
  dérivées de la planche vectorielle **« Musculature »** de `SMART-Muscles.pptx`
  (sha256 `ad8e04e0b98f99d9196ef3966c2228137e18ed0afda9a85996d2e4116cb66d68`).
- Motif : `latissimus dorsi` et `rectus abdominis` sont **absents de BodyParts3D 4.0** (constat sur les trois
  index officiels).

## Modifications déclarées
Conversion DrawingML → SVG, **sélection déterministe** de 117 (`lats`) / 157 (`core`) chemins par identifiants
exacts, masque monochrome avec fermeture morphologique (suppression du détail fibrillaire), vectorisation
(Potrace 1.16), **alignement par transformation uniforme** sur la base BodyParts3D, mise au contrat SVG.
**Œuvre dérivée sous attribution.**

## Ce qui n'est pas revendiqué
Aucun endossement de Les Laboratoires Servier. Aucune revue anatomique professionnelle. Aucune clairance
juridique. La géométrie `core` est un **agrégat fonctionnel visuel**, pas une extraction du grand droit.

## Nature de la source
Le pack `SMART-Muscles.pptx` a été vérifié `SERVIER PPTX CONTENT: EDITABLE VECTOR` (3 361 chemins DrawingML
natifs) — la géométrie provient des chemins vectoriels d'origine, sans dérivation raster.
