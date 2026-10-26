# Sb_DA_02_7_R2_LARGER_RAIL — un rail plus grand, posé plus bas

**Statut** : 🟡 PR ouverte — tier `isolated` · **Branche** : `sb/da-02-7-r2-larger-rail`
**Base** : R4 (`sb/da-02-7-r4-zone-emphasis`, PR #305) · **Commande** : « faire tous les R » (opérateur, 2026-10-25), puis « tu peux partir sur le B u6 sans hésiter » (2026-10-26)
**Gate visuel** : option **B** retenue sur le tableau de revue (u = 6, module 390 × 290)
**Autorité** : `AUREN_VISUAL_CONTRACT.md` — `INSTRUMENT-SURFACE-B1` / `-B2`, `INSTRUMENT-CONTROLS-B3` (LOCKED) ; demande R2 (§9)

---

## 1. Brainstorming · Options · Risques · Choix retenu (`CLAUDE.md §3`)

| Question | Options | Choix | Qui |
|---|---|---|---|
| Comment agrandir le rail | changer `UNIT` (tous les rails) · forcer la densité · **une grille propre à la surface** | **une grille propre à la surface** (`gridUnit`, défaut = densité) | agent : `CALIBRATION-LINE-V1` reste intact au pixel ; seule la surface dessine plus grand |
| De combien | A : u = 5, module 260 · **B : u = 6, module 290** | **B** | opérateur, « sans hésiter » |
| La règle à 320 | une valeur fixe · **la même règle, 1,5 ×** | **1,5 ×** (u = 4,5), module 210 | agent : une seule règle pour toutes les largeurs ; hauteur choisie pour la même respiration qu'à 390 |
| Frame C | grandir avec le rail · **garder sa grille** | **garder sa grille** | agent : `FRAME-C-V1` est verrouillé ; son trait et sa marge ne bougent pas |
| Nom de l'option | `unit` · **`gridUnit`** | `gridUnit` | agent : `unit` est déjà l'unité de charge (« kg ») du rail ; le même nom aurait écrasé l'un par l'autre en passant les props |

| Risque | Parade |
|---|---|
| Le rail de démonstration change aussi | 4 baselines `calibration-line-*` identiques à l'octet (gate vert sans approbation) |
| La pile ne tient plus dans le cadre | test : la pile tient avec au moins 2 unités de cadre au-dessus et au-dessous, pour chaque fixture |
| Un demi-pixel à 320 (u = 4,5) | la grille produisait déjà des fractions (1,2u, 0,8u à u = 3) ; rendu vérifié à l'œil |

## 2. Pré-vol

| # | Point | Valeur |
|---|---|---|
| 1 | baselines qui font foi | les 35 ; 14 doivent rester identiques (rail seul, Frame C, fenêtres) |
| 2 | fichiers LOCKED impliqués | `layout.ts` / `CalibrationRail.tsx` (option `gridUnit`, défaut intact) ; `HorizontalInstrumentSurface.tsx` |
| 3 | invariants | `CALIBRATION-LINE-V1`, `FRAME-C-V1` ; B.1 (valeur au-dessus, prescrit sous le bloc) ; B.2 (rien ne bouge entre repos et réglage) ; B.3 (commandes sous le cadre) |
| 4 | delta permis | taille du rail dans la surface, écart valeur → rail, hauteur du module |
| 5 | fichiers prévus | §4 |

## Croquis validé

Validé par l'opérateur sur le tableau de revue (option B, 390 × 290, rendus 2×), 2026-10-26 :

```
  ┌──────────────────────────────┐
  │           77,5 kg            │   valeur : même rôle (68)
  │                              │   écart : 4 unités du rail
  │  ▌▌ ▌ ▌ ▌ ██ ▌▌ ▐█▌ ╱╱╱      │   rail : grille 6 (au lieu de 4)
  │  55  60  65  70  75  80  85  │
  │  EASY   TARGET  PUSH  HIGH…  │
  │              70              │
  └──────────────────────────────┘   module 390 × 290 (au lieu de 220)
```

## Inventaire — une information, une seule fois

| Élément | Information | Source (contrat de données) | Doublon ? |
|---|---|---|---|
| valeur | la charge choisie | `selectedValue`, `unit` | non |
| rail (curseur) | la même charge, sur l'échelle de coût | `selectedPosition` | non : position, pas chiffre |
| repère + chiffre sous le bloc | la prescription | `referencePosition`, `referenceValue` | non |
| échelle, noms de zone (réglage) | les pas, les zones | `stepValues`, bornes | non |

Aucun élément ajouté ni retiré : seules les tailles changent.

## Comparaison avec la référence validée

| Référence validée | Tranche / date | Ce qui doit survivre | Survit ? |
|---|---|---|---|
| `CALIBRATION-LINE-V1` | DA-02.2 + R4 | le rail lui-même | **oui** : 4 baselines identiques à l'octet ; la surface l'agrandit sans le redessiner |
| `INSTRUMENT-SURFACE-B1` / `-B2` | DA-02.4B.1 / .2 | valeur au-dessus, rail pleine largeur, prescrit sous le bloc, rien ne bouge entre les états | **oui** (tests de pile et de « pas de saut » verts) |
| `INSTRUMENT-CONTROLS-B3` | DA-02.4B.3 | − / + sous le cadre, même géométrie | **oui** : la géométrie ne dépend que de la largeur |
| `FRAME-C-V1`, `RECESSED-WINDOW-V1` | DA-02.3 / .5 | tout | **oui** : 10 baselines identiques à l'octet |

## Changement unique de l'itération

- Changement : **le rail de la surface est dessiné sur une grille 1,5 × plus grande, et le module grandit pour le loger.**
- Rien d'autre.

## 3. Relecture du relevé de décisions (`CLAUDE.md §5.2`)

| Décision | Verdict |
|---|---|
| `CALIBRATION-LINE-V1` MUST NEVER « donner de la largeur du rail à un autre module » | **respectée** : pleine largeur du champ |
| `CALIBRATION-LINE-V1` MUST NEVER « redessiner le curseur ou le repère » | **respectée** : mêmes proportions en u |
| `FRAME-C-V1` (structure) | **respectée** : grille et trait du cadre inchangés |
| B.1 — valeur souveraine au-dessus, prescrit sans mot | **respectée** |
| B.2 — « fixe, pas de saut » | **respectée** (test) |
| `AUREN_VISUAL_CONTRACT §6` n° 5 — la valeur ne prend pas de largeur au rail | **respectée** |
| `CLAUDE.md §5.4` — couleur = token | **non concerné** : aucune couleur touchée |
| demande R2 (« plus haut, plus bas ») | **respectée** : rail 1,5 × plus haut, posé 4 unités sous la valeur |

## 4. Réalisation

| Fichier | Rôle |
|---|---|
| `src/ui/calibration/layout.ts`, `CalibrationRail.tsx` | option `gridUnit` (défaut : la grille de la densité) |
| `src/ui/instrument/HorizontalInstrumentSurface.tsx` | `SURFACE_RAIL_SCALE = 1,5` ; écart valeur → rail 4 |
| `src/ui/contract/fixtures.ts` | modules 390 × 290 et 320 × 210 |
| `src/ui/instrument/SurfaceB1Gallery.tsx` | le banc appareil aux mêmes tailles |
| `calibration.test.ts`, `HorizontalInstrumentSurface.test.ts` | défaut intact ; grille 6 / 4,5 ; pile qui tient avec marge |
| `visual-contract/baselines/` | 21 baselines remplacées (nouveaux noms) + manifeste |
| `AUREN_VISUAL_CONTRACT.md` | §8, §10, §11 (noms), §9 (R2 livrée), §15 |

## 5. Post-vol

| # | Point | Résultat |
|---|---|---|
| 1 | fichiers modifiés | §4 |
| 2 | tests structurels | jest **353 / 353** · gardes 18 / 18 |
| 3 | régression visuelle | 36 / 36 ; 14 baselines identiques à l'octet, 21 neuves |
| 4 | avant / après | sur le tableau de revue (option B) ; les rendus approuvés portent aussi l'opacité R4, donc ne sont identiques à l'octet à aucun rendu revu seul — dit dans le manifeste |
| 5 | delta voulu | taille du rail, hauteur du module |
| 6 | invariants LOCKED | `CALIBRATION-LINE-V1`, `FRAME-C-V1`, `RECESSED-WINDOW-V1` inchangés |

## 6. Incidents

- Collision de nom évitée : l'option s'appelait d'abord `unit`, déjà pris par l'unité de charge ; renommée `gridUnit` avant tout rendu.

**Verdict :** R2 est livrée. Le rail de l'instrument est 1,5 × plus grand, posé plus bas, ses index se lisent mieux ; le rail seul et le cadre restent tels qu'approuvés. Suite : **R5** (boutons allure Rail), puis R1.
