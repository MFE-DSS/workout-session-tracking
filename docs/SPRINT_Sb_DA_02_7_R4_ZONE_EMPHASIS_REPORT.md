# Sb_DA_02_7_R4_ZONE_EMPHASIS — la zone traversée se détache

**Statut** : 🟡 PR ouverte — tier `isolated` · **Branche** : `sb/da-02-7-r4-zone-emphasis`
**Base** : canonique `4d0e469` · **Commande** : « faire tous les R » (opérateur, 2026-10-25), puis « tout ça, c'est validé, tu prends le recommandé et boucle qu'on avance » (2026-10-26)
**Gate visuel** : variante **V1** retenue sur le tableau de revue (opérateur : « on va dire que c'est OK » ; « tu prends le recommandé »)
**Autorité** : `AUREN_VISUAL_CONTRACT.md` — `CALIBRATION-LINE-V1` (LOCKED) ; demande R4 (§9)

---

## 1. Brainstorming · Options · Risques · Choix retenu (`CLAUDE.md §3`)

| Question | Options | Choix | Qui |
|---|---|---|---|
| Comment faire ressortir la zone du curseur | changer la couleur des zones · épaissir la bande active · **faire reculer les zones inactives** | **faire reculer les inactives** | agent : aucune couleur neuve, aucune géométrie neuve ; l'ADN du rail (largeur, bande, dessus / dessous) ne bouge pas |
| De combien | **V1** bande 0,35 · index 0,30 · V2 bande 0,25 · index 0,20 | **V1** | opérateur, sur le tableau (« le rail et ses index doivent rester très visibles ») ; V2 éteignait trop les index |
| Où vit la règle | deux nombres en dur · **une constante nommée** | `INACTIVE_ZONE_OPACITY` | agent : la valeur est relue par le contrat |

| Risque | Parade |
|---|---|
| Les index des zones inactives deviennent illisibles | V1 garde 1,8 à 2,6 : 1 sur la face `plate` ; V2 rejetée pour cette raison |
| Le changement touche plus que le rail | seules les 25 baselines qui portent le rail changent ; Frame C et fenêtres (10) restent identiques à l'octet |
| Une baseline approuvée diffère du rendu revu | les nouvelles baselines 390 sont identiques à l'octet aux candidats `r4-v1-*` revus |

## 2. Pré-vol

| # | Point | Valeur |
|---|---|---|
| 1 | baselines qui font foi | les 35 ; 10 doivent rester identiques (Frame C, fenêtres) |
| 2 | fichier LOCKED impliqué | `CalibrationRail.tsx` (opacité des zones inactives seulement) |
| 3 | invariants | `CALIBRATION-LINE-V1` MUST PRESERVE (ligne, curseur au-dessus, repère dessous, bande, sémantique, marqueurs) |
| 4 | delta permis | l'opacité des zones inactives (bande, index, noms) |
| 5 | fichiers prévus | §4 |

## Croquis validé

Validé par l'opérateur sur le tableau de revue (rendus 2×, V1 et V2, REST et ADJUSTING, TARGET / PUSH / HIGH COST), 2026-10-26 :

```
  ░░░░ EASY ░░░░|████ TARGET ████|░░░ PUSH ░░░|░ HIGH COST ░
                       ▲ curseur dans TARGET : seule sa zone à pleine opacité
  bande inactive 0,35 · index / noms inactifs 0,30 (au lieu de 0,5 / 0,45)
```

## Inventaire — une information, une seule fois

| Élément | Information | Source (contrat de données) | Doublon ? |
|---|---|---|---|
| bande de la zone active | la zone où tombe le choix | `selectedZone` (dérivée de `selectedPosition` et des bornes) | non |
| bandes des zones inactives | le reste de l'échelle de coût | `zones` | non |
| index | les pas de charge | `positions` | non |

Aucun élément ajouté ni retiré : seule l'opacité change.

## Comparaison avec la référence validée

| Référence validée | Tranche / date | Ce qui doit survivre | Survit ? |
|---|---|---|---|
| `CALIBRATION-LINE-V1` | DA-02.2 (PR #286) | ligne, bande, curseur au-dessus / repère dessous, géométrie des marqueurs | **oui** : seule l'opacité des zones inactives change |
| `INSTRUMENT-SURFACE-B1` / `-B2`, `INSTRUMENT-CONTROLS-B3` | DA-02.4B | la composition (valeur, rail, prescrit, commandes) | **oui** : même géométrie, la zone du curseur ressort |
| `FRAME-C-V1`, `RECESSED-WINDOW-V1` | DA-02.3 / DA-02.5 | tout | **oui** : 10 baselines identiques à l'octet |

## Changement unique de l'itération

- Changement : **les zones où n'est pas le curseur reculent** (bande 0,5 → 0,35 ; index et noms 0,45 → 0,30).
- Rien d'autre.

## 3. Relecture du relevé de décisions (`CLAUDE.md §5.2`)

| Décision | Verdict |
|---|---|
| `CALIBRATION-LINE-V1` MUST NEVER « introduire une nouvelle couleur sémantique » | **respectée** : aucune couleur neuve |
| `CALIBRATION-LINE-V1` MUST NEVER « retirer l'identité de la bande de zones au REST » | **respectée** : la bande reste entière, motifs compris |
| `CALIBRATION-LINE-V1` MUST PRESERVE (ligne, marqueurs, dessus / dessous) | **respectée** |
| `AUREN_VISUAL_CONTRACT §6` n° 2 — REST garde la ligne et la bande | **respectée** |
| `SEMANTIC-TOKENS-V1` | **respectée** : mêmes rôles, mêmes tokens |
| `CLAUDE.md §5.4` — couleur = token | **respectée** : opacité sur les tokens existants |
| demande R4 (« la zone où l'on est, plus contrastée ») | **respectée** : rapport actif / inactif ≈ 4,2 : 1 (au lieu de ≈ 3 : 1) |

## 4. Réalisation

| Fichier | Rôle |
|---|---|
| `src/ui/calibration/CalibrationRail.tsx` | `INACTIVE_ZONE_OPACITY` (bande 0,35 · index et noms 0,30) |
| `visual-contract/baselines/` | 25 baselines ré-approuvées + manifeste (sha256, `approved_by`, `approved_on`) |
| `AUREN_VISUAL_CONTRACT.md` | §9 (R4 livrée), §14 (règle et note de l'opérateur) |
| `AUREN_VISUAL_BACKBONE.md §8.4`, `SPEC_REGISTRY.md` | état de la roadmap |

## 5. Post-vol

| # | Point | Résultat |
|---|---|---|
| 1 | fichiers modifiés | §4 |
| 2 | tests structurels | voir la PR (tsc, jest, gardes) |
| 3 | régression visuelle | 36 / 36 après approbation ; avant : 11 verts, 25 en écart (le delta voulu) |
| 4 | avant / après | sur le tableau de revue ; baselines 390 identiques à l'octet aux candidats revus |
| 5 | delta voulu | opacité des zones inactives |
| 6 | invariants LOCKED | 10 baselines inchangées ; géométrie du rail inchangée |

## 6. Incidents

- Aucun dans le périmètre.

**Note de l'opérateur pour plus tard** : les proportions des zones EASY / TARGET / PUSH / HIGH COST dépendent de l'incrément de charge de chaque exercice ; elles viendront du moteur. Les fixtures gardent les bornes de démonstration.

**Verdict :** R4 est livrée. La zone où tombe le choix se lit d'un coup d'œil, le rail et ses index restent visibles. Suite : **R2** (rail plus grand, u = 6), puis R5 et R1.
