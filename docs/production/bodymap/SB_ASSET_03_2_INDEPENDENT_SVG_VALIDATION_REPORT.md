# SB_ASSET_03.2 — Independent SVG Validation Report

**Date** : 2026-07-23 · Fichiers issus du **replay indépendant** (package v2).

## Deux validateurs convergents
| Validateur | master | compact |
|---|---|---|
| Validateur du package (`validate_and_compact.py`) | **40/40** · 0 erreur | **41/41** · 0 erreur |
| Validateur d'intake **indépendant** (écrit pour Sb_ASSET_03.2) | **66/66** · 0 erreur | conforme (voir §méthodes) |

## Contrat vérifié (les deux fichiers)
XML bien formé · **aucun `DOCTYPE`/`ENTITY`** · PI = `xml` seul · root SVG unique · rien après la racine ·
**viewBox `0 0 240 200` exact** · **14 IDs présents une seule fois** · **11 groupes de zones** · aucune zone
supplémentaire · **0 `zone-unknown`** · 0 ID dupliqué · **0 path partagé** · **un seul parent sémantique par
path** · **convention d'IDs enfants** respectée.

## Surface sécurisée statique
0 `script` · 0 `on*` · 0 `foreignObject`/`image`/`iframe`/`audio`/`video`/`canvas`/`object`/`embed`/`use` ·
0 `xlink:href` · 0 `data:`/`javascript:` · 0 `url()` · 0 `@import` · 0 SMIL (`animate*`/`set`) · 0 `filter` ·
0 gradient · 0 `text`/`font`/`tspan` · 0 bitmap/base64 · 0 référence réseau · **0 couleur métier figée**.

## Trois méthodes géométriques (§9) — recalculées sur les fichiers du replay v2
| Méthode | master | compact |
|---|---|---|
| 1 — parseur d'intake (**points de contrôle**) | conforme | enveloppe > courbe (méthodologique) |
| 2 — **Chrome `getBBox()`** (rendu) | y[15,97 · 184,01] | y[15,89 · **184,76**] |
| 3 — **Inkscape CLI** | y 15,9706 h 168,045 | y 15,8893 h 168,871 |

**Méthodes 2 et 3 concordent au centième.** Géométrie **rendue** conforme : `y ∈ [12,188]` · safe area ≥ 8 ·
dans le viewBox · **gouttière [110,130] vide** · face et dos à **même échelle** (h 168,04) et **même centre
vertical**. La méthode 1 mesure l'enveloppe des points de contrôle (contient la courbe par construction) — son
écart est **méthodologique, pas un désaccord** ; la géométrie rendue fait foi.

## Verdict
**INDEPENDENT SVG VALIDATION: PASS.** Les deux validateurs convergent, la surface est statique-sûre, et les
trois méthodes géométriques exigées ont été exécutées sur les fichiers **rejoués** (Chrome + Inkscape
concordants).
