# AUREN — Muscle Focus Plate Template (`Sx_ASSET_03B`)

**Type** : gabarit conceptuel de plaque — **DOCS-ONLY**. **Gabarit** (valeurs `<...>` à compléter au futur
build) ; ne décrit aucune plaque existante et ne produit aucune géométrie. `ASSET INTEGRATION GATE: BLOCKED`.
**Référence normative** : [`../../strategy/Sx_ASSET_03B_MUSCLE_FOCUS_TECHNICAL_SURFACE_SYSTEM_SPEC.md`](../../strategy/Sx_ASSET_03B_MUSCLE_FOCUS_TECHNICAL_SURFACE_SYSTEM_SPEC.md) §7-§10.

> Le **contrat d'IDs figé** de chaque plaque sera tranché au build `Sb_ASSET_03B.1`. Ce gabarit **prépare** sa
> forme, il ne la fige pas. Il réutilise le modèle 4-layers (`Sx_ASSET_01 §4`) et la convention d'IDs enfants
> du master global (`geom-<zone>-<view>-<side>-<index>`).

## Descripteur de plaque (à remplir au build)

```yaml
plate_id: <plate-region-<key> | plate-muscle-<zone>>
level: <2-regional | 3-muscle>
mode: <muscle-heads | grouped-honest>      # grouped-honest pour upper_back, posterior
zone_codes: [<un ou plusieurs des 11 codes ; JAMAIS un nouveau code>]
macro: <chest | shoulders | back | arms | legs | core>
views: [front, back, <lateral?>, <section?>]
viewbox_local: "<figé et documenté par famille — crop du master (N2) ou artefact neuf (N3)>"
contract_version: <semver — bump obligatoire à toute évolution incompatible>
source_refs: [<sources CC BY / PD utilisées — cf. source strategy>]
attribution_required: <true — CC BY perpétuelle>
ai_usage: <NONE | {role: style|composition, declared: true}>   # jamais géométrie
non_medical: true
scored: false                               # une plaque n'introduit AUCUN score ni donnée
```

## Modules (pile) — activer selon le niveau

| # | Module | ID racine (indicatif) | N2 | N3 |
|---|---|---|---|---|
| 1 | Clean anatomical view | `geom-<key>-<view>-<side>-<i>` | ✔ | ✔ |
| 2 | View selector | `view-<front|back|lateral|section>` | front/back | 4 vues |
| 3 | Depth / layer toggle | `layer-toggle` | — | ✔ |
| 4 | Technical overlay | `overlay-insertion` · `overlay-fiber` · `overlay-contraction` | — | ✔ |
| 5 | Insertion / origin markers | `mark-<zone>-origin|insertion-<i>` | — | ✔ |
| 6 | Fiber-direction indicators | `overlay-fiber` (vecteurs schématiques) | — | ✔ |
| 7 | Contraction / ROM indicator | `overlay-contraction` (non médical) | — | ✔ |
| 8 | Exercise link | `overlay-exercise` (clé EKB) | liste | interactif |
| 9 | Text caption (a11y) | hors surface (label FR + fonction + disclaimer) | ✔ | ✔ |
| 10 | State / legend | légende non-couleur (principal/synergiste/adjacent) | ✔ | ✔ |
| 11 | Provenance micro-module | attribution CC BY | ✔ | ✔ |

Sous-heads intra-zone (labels d'affichage, **Layer B**, jamais un code) : `part-<zone>-<label>`
(ex. `part-pecs-clavicular`, `part-pecs-sternocostal`, `part-biceps-long`, `part-triceps-lateral`).

## États (projettent sur les 5 états figés — Layer C)

| État plaque | Sens | Projection runtime |
|---|---|---|
| `clean` | géométrie seule | états zone standards |
| `overlay-on` | couche technique visible | additive, `aria-hidden` par défaut sinon |
| `exercise-highlighted` | un exercice met en avant ses rôles | principal→`primary` · synergiste→`secondary` · adjacent→`neutral`+annotation |

**Jamais distingué par la seule teinte** (héritage `§7` du contrat). Aucune couleur métier codée en dur ;
couleur = tokens runtime (Auren Terminal).

## Variantes mobile / desktop

- **360px** : clean + caption + un accordéon ; overlays/coupe/comparative **repliés** ; vues front/back
  (lateral/section derrière « plus ») ; exercices en liste ; plaque N3 = sheet plein écran.
- **Desktop** : overlays dépliables/juxtaposables, 4 vues, comparative, overlay exercice interactif.

## Garde-fous de remplissage (durs)

- **Aucune 12ᵉ zone** ; `zone_codes` ⊆ les 11 codes.
- **Aucun score / aucune donnée** introduits par une plaque.
- **Non médical** : vecteurs (pas histologie), ROM (pas EMG), caption sobre, zéro claim d'activation.
- **Fidélité de forme** obligatoire (cf. spec §16 : convergence pectorale, ancrage osseux deltoïdien,
  insertion ischiatique, largeur/épaisseur dos, corset transverse).
- **Zéro** valeur `approved` / `legally-cleared` / `anatomically-validated-professionally` / `runtime-ready`.
- **Attribution CC BY perpétuelle** si géométrie dérivée ; `ai_usage` déclaré (jamais géométrie).
