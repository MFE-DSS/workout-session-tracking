# Sb_DA_04_2_BODYMAP_ALL_ZONES — une image par zone, des séances qui s'en déduisent

**Date :** 2026-10-29
**Branche :** `sb/da-04-2-all-zones` (base canonique `20d0581`, après DA-04.1)
**Verdict :** voir la fin du rapport.

## 0. Commande et décisions de l'opérateur

- « je veux avancer et qu'on boucle […] faire toutes les images sur tous les muscles de tous les entraînements ».
- Sur la planche DA-04.2 : « Ok, très bien. Donc, push A, les 4 zones, full body, 7 zones », et la règle :
  « de manière agnostique, tu associes les images à des zones de travail. Ces zones de travail sont après exploitées
  par des exercices comme muscles principaux ou secondaires […] Et après, les exercices sont ajoutés dans les
  programmes. C'est vraiment cette approche qu'il faut avoir de manière agnostique pour résoudre les zones. »

## 1. Brainstorming · Options · Risques · Choix retenu (`CLAUDE.md §3`)

| Option | Pour | Contre |
|---|---|---|
| A — une image par programme (Push A, Pull A…) | rapide à montrer | couple l'image au programme : chaque programme nouveau = une image nouvelle ; contraire à la règle de l'opérateur |
| B — une caméra par zone ; le panneau d'une séance **dérivé** de ses exercices | agnostique ; 11 images servent tous les programmes, présents et futurs | il faut une règle de grille pour N zones |
| C — le triptyque à trois fenêtres pour toute séance (trois zones « principales ») | une seule forme | choisir trois zones parmi quatre ou sept est une décision métier cachée ; Push A en a quatre |

**Choix : B.** La grille garde la grammaire de T1 : fenêtres égales, trois par ligne au plus.

**Risques** : un panneau composé à la main (→ dérivé par `sessionZones`) ; une fenêtre plus large qu'en T1 qui
agrandirait la géométrie (→ trois par ligne au plus) ; la zone d'un exercice prise à l'ancien classifieur (→ panneaux
de la planche faits avec le résolveur canonique ; la bascule du modèle de lecture mobile est une tranche serveur
séparée).

## 2. Pré-vol

| # | Point | Valeur |
|---|---|---|
| 1 | baselines qui font foi | les 51 du contrat, dont les 5 de `PUSH-A-BODYMAP-TRIPTYCH-V1` (inchangées) |
| 2 | fichiers LOCKED impliqués | `PUSH-A-BODYMAP-TRIPTYCH-V1` : ses trois caméras et T1 réutilisés tels quels (3 zones = exactement T1) |
| 3 | invariants | master intouché ; zone en `system` ; contexte en ossature ; aucune revendication |
| 4 | delta permis | huit caméras, la grille à N zones, la dérivation, de nouvelles fixtures |
| 5 | fichiers prévus | §4 |

## Croquis validé

```
 zone → image        exercice → zones              séance → panneau (dérivé)
 ┌────┐ ┌────┐       « Écarté arrière… » → delt_post   Push A : pecs, delt_lat, delt_post, triceps
 │pecs│ │lats│ …     « Chest Press »     → pecs        ┌──────┬──────┐
 └────┘ └────┘       …                                 │ pecs │ d.lat│   fenêtres égales,
 11 caméras,                                           ├──────┼──────┤   trois par ligne au plus
 aucune ne connaît                                     │d.post│ tri  │
 un programme                                          └──────┴──────┘
```

## Inventaire — une information, une seule fois

| Élément | Information | Source (contrat de données) | Doublon ? |
|---|---|---|---|
| fenêtre de zone | où se situe la zone | caméra `presetForZone(zone)` | non |
| libellé de fenêtre | le nom de la zone | `label_fr` du contrat de mapping | non : le dessin dit **où**, le mot dit **quoi** |
| panneau de séance | quelles zones la séance travaille | zones principales de ses exercices | non : une zone n'apparaît qu'une fois même si plusieurs exercices la travaillent |

## Comparaison avec la référence validée

| Référence validée | Tranche / date | Ce qui doit survivre | Survit ? |
|---|---|---|---|
| `PUSH-A-BODYMAP-TRIPTYCH-V1` | DA-04.1 / 2026-10-29 | les trois caméras, T1, le traitement | **oui** : 5 baselines inchangées ; 3 zones = `triptychLayout` (test) |
| planche DA-04.2 | 2026-10-29 | les 13 rendus gouvernés | **oui** : identiques à l'octet aux captures revues |
| 46 baselines antérieures | DA-02 → DA-03 | tout | **oui** |

## Changement unique de l'itération

- Changement : **la couche zone → image est complète (11 caméras) et le panneau de séance s'en déduit.**
- Rien d'autre : aucun écran produit ne monte le BodyMap ; le serveur n'est pas touché par cette tranche.

## 3. Relecture du relevé de décisions (`CLAUDE.md §5.2`)

| Décision | Verdict |
|---|---|
| images associées aux **zones**, de manière agnostique | **respectée** : `ZONE_PRESETS`, une caméra par zone, aucune ne nomme un programme |
| zones exploitées par les exercices (principales / secondaires) | **respectée** côté app : `sessionZones` lit la zone de chaque exercice ; la fourniture des secondaires par le serveur est la tranche suivante |
| exercices ajoutés aux programmes → panneau | **respectée** : panneau dérivé, jamais composé |
| Push A : 4 zones ; Full Body : 7 zones | **respectée** (2 × 2 ; 3 + 3 + 1) |
| §20 — master intouché, `system`, orientation avant pourcentage, rien dans le runtime web | **respectée** |
| `CLAUDE.md §5.3` — jamais une soustraction seule | **non concernée** (ajout) |
| `CLAUDE.md §5.4` — couleur = token | **respectée** (`system`, `ink3`, `field`) |

## 4. Réalisation

| Fichier | Rôle |
|---|---|
| `clients/mobile/src/ui/bodymap/viewPresets.ts` | huit caméras, `ZONE_PRESETS`, `presetForZone` |
| `clients/mobile/src/ui/bodymap/triptychLayout.ts` | `zoneGridShape`, `zoneGridHeight`, `zoneGridLayout` (3 = T1) |
| `clients/mobile/src/ui/bodymap/BodyMapTriptych.tsx` | grille à N fenêtres ; `sessionZones`, `SessionBodyMap` |
| `clients/mobile/src/ui/contract/fixtures.ts`, `ContractFixture.tsx`, `candidates.ts` | 13 fixtures `BODYMAP-ZONES-V1` ; candidats vidés |
| `clients/mobile/visual-contract/baselines/` + `manifest.json` | 13 baselines, approbation citée |
| `docs/strategy/AUREN_VISUAL_CONTRACT.md` | registre, §21 |
| `tests/test_auren_bodymap_runtime.py`, `tests/test_visual_contract_governance.py` | une caméra par zone ; identifiant LOCKED |
| `clients/mobile/src/ui/bodymap/viewPresets.test.ts` | 10 tests |

## 5. Post-vol

- 51 baselines antérieures inchangées ; 13 nouvelles identiques à l'octet aux captures revues.
- Parts de zone (préférence 35–50 %, l'orientation prime), mesurées à la taille de la carte puis de T1 :
  deltoïdes postérieurs 19 / 12 % ; dos largeur 40 / 40 % ; dos épaisseur 45 / 42 % ; biceps 18 / 14 % ;
  quadriceps 65 / 65 % ; ischios / fessiers 70 / 70 % ; mollets 72 / 72 % ; core 64 / 67 %.

## 6. Constat transmis à l'opérateur (non corrigé ici)

Le modèle de lecture mobile (`app/services/mobile_read_models.py`) donne à chaque exercice sa zone par l'ancien
classifieur, sans les corrections revues : « Rear delt fly machine (pec deck inversé) » → `pecs` au lieu de
`delt_post` ; « Relevé de jambes suspendu » → `calves` au lieu de `core`. La règle de l'opérateur (« de manière
agnostique pour résoudre les zones ») appelle le résolveur canonique, principale et secondaires : tranche serveur
séparée.

## Annexe de clôture (2026-10-29)

- Gate vérifié avant fusion : tête `7863f3f`, 11 / 11 checks verts (contrat visuel : 64 baselines identiques au
  pixel en CI), Sonar PR `OK`, 0 fil ouvert, `CLEAN`.
- PR #321 fusionnée en `--merge --match-head-commit` : **`176e2d0`** ; CI canonique `40880892913` **verte**.
- Le constat du §6 est corrigé par PR #322 (`7a3c17e`) : le plan mobile et le relevé résolvent les zones par le
  contrat canonique.

**Verdict :** `BODYMAP-ZONES-V1` **LOCKED** — 11 caméras agnostiques, panneau de séance dérivé, 13 baselines
approuvées par l'opérateur ; aucun écran produit ne le monte encore.
