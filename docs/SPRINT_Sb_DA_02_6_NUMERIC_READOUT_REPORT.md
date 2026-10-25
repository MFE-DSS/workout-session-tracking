# Sb_DA_02_6_NUMERIC_READOUT — la lecture chiffrée

**Statut** : build — tier `isolated` · **Branche** : `sb/da-02-6-numeric-readout`
**Base** : canonique `88bb1de` · **Commande** : « go » de l'opérateur sur l'étape suivante du chemin critique (2026-10-25)
**Gate visuel** : **« ACCEPT »** (opérateur, 2026-10-25)
**Autorité** : `AUREN_VISUAL_CONTRACT.md` (tous les Visual IDs LOCKED)

---

## 1. Brainstorming · Options · Risques · Choix retenu (`CLAUDE.md §3`)

| Question | Options | Choix | Qui |
|---|---|---|---|
| Unité | après, en petit · au-dessus, avec le libellé | **après, en petit** (actuel) | opérateur, sur croquis |
| Décimale | même taille · réduite | **même taille** (actuel) | opérateur, sur croquis |
| Taille dans un espace contraint | estimation (largeur moyenne d'un chiffre) · **mesure du rendu** | **mesure** | agent : la police de l'iPhone diffère de celle du gate ; l'estimation laissait des valeurs plus petites que possible et de tailles différentes côte à côte |
| Première image | montrer l'estimation puis corriger · **cacher jusqu'à la mesure** | **cacher** | agent : jamais une valeur affichée à la mauvaise taille |
| Où vit la règle | dans chaque écran · **une pièce partagée** | `NumericReadout` | le diagnostic du programme UI : le produit avait la décision, pas le moyen de l'appliquer |

| Risque | Parade |
|---|---|
| La refonte de la surface déplace un pixel | 27 baselines de surface / boutons / rail / cadre vertes sans approbation |
| Le gate photographie avant la mesure | le gate attend que plus aucun mesureur ne soit présent |
| Une valeur plus grande est coupée | contrôle de la capture : aucune valeur coupée sur les 8 fenêtres |

## 2. Pré-vol

| # | Point | Valeur |
|---|---|---|
| 1 | baselines qui font foi | les 35 ; 32 doivent rester identiques |
| 2 | fichiers LOCKED impliqués | `HorizontalInstrumentSurface.tsx` (la valeur passe par `NumericReadout`, rendu identique) ; `RecessedWindowFixture.tsx` (la valeur passe par `FittedReadout`) |
| 3 | invariants | tous les MUST PRESERVE des surfaces, boutons et fenêtres |
| 4 | delta permis | la taille des valeurs dans les fenêtres, mesurée |
| 5 | fichiers prévus | §4 |

## Croquis validé

Validé par l'opérateur avant le code (questions à aperçu, 2026-10-25) :

```
  D E R N I È R E
  72,5 kg          ← l'unité après, en petit ; la décimale de la même taille
```

## Inventaire — une information, une seule fois

| Élément | Information | Source (contrat de données) | Doublon ? |
|---|---|---|---|
| valeur | la donnée | `value` | non |
| unité | son unité | `unit` | non |
| étiquette (fenêtres) | ce que dit la valeur | `label` | non |

## Comparaison avec la référence validée

| Référence validée | Tranche / date | Ce qui doit survivre | Survit ? |
|---|---|---|---|
| `INSTRUMENT-SURFACE-B1` / `-B2`, `INSTRUMENT-CONTROLS-B3` | DA-02.4B | la valeur souveraine, au pixel | **oui** : 21 baselines vertes sans approbation |
| `RECESSED-WINDOW-V1` | DA-02.5 | la fenêtre ; ses valeurs au plus grand qui tient | **oui** : 5 inchangées ; 3 où la mesure trouve plus grand, réapprouvées |

## Changement unique de l'itération

- Changement : **la taille d'une valeur dans une fenêtre est mesurée, plus estimée.**
- Sans effet visible : la pièce partagée `NumericReadout` (même rendu qu'avant partout ailleurs).

## 3. Relecture du relevé de décisions (`CLAUDE.md §5.2`)

| Décision | Verdict |
|---|---|
| unité après, en petit (opérateur) | **respectée** |
| décimale même taille (opérateur) | **respectée** |
| `RECESSED-WINDOW-V1` — valeurs les plus grosses possibles, jamais coupées | **respectée**, et mieux tenue : mesurée |
| `INSTRUMENT-SURFACE-B1` — valeur souveraine en `readout` / `figure` | **respectée** au pixel |
| `CLAUDE.md §5.4` — couleur = token | **respectée** (`ink2` pour l'unité) |

## 4. Réalisation

| Fichier | Rôle |
|---|---|
| `src/ui/instrument/readoutModel.ts` (+ test) | rôles, unité 0,4, ligne 1,05, choix du rôle depuis les largeurs mesurées |
| `src/ui/instrument/NumericReadout.tsx` | `NumericReadout` (la pièce) et `FittedReadout` (mesure puis choisit) |
| `src/ui/instrument/HorizontalInstrumentSurface.tsx` | la valeur souveraine passe par `NumericReadout` |
| `src/ui/instrument/RecessedWindowFixture.tsx` | les valeurs des fenêtres passent par `FittedReadout` |
| `src/ui/instrument/windowContent.ts` (+ test) | **retirés** : l'estimation est remplacée par la mesure |
| `visual-contract/visual.spec.ts`, `review.spec.ts` | attendre la fin de la mesure avant la capture |
| `visual-contract/baselines/` | 3 baselines de fenêtre réapprouvées + manifeste |
| `tests/test_visual_contract_governance.py` | `NUMERIC-READOUT-V1` LOCKED |
| `AUREN_VISUAL_CONTRACT.md` | registre, §12 (valeurs mesurées), §13 |

## 5. Post-vol

| # | Point | Résultat |
|---|---|---|
| 1 | fichiers modifiés | §4 |
| 2 | tests structurels | tsc propre · jest **346 / 346** · gardes 11 / 11 |
| 3 | régression visuelle | **36 / 36** après approbation ; avant : 33 verts, 3 fenêtres en écart (le delta voulu) |
| 4 | avant / après | les 3 fenêtres changées, sur le tableau de revue ; identiques à l'octet aux rendus revus |
| 5 | delta voulu | valeurs mesurées dans les fenêtres : 320 paire (deux valeurs en 40), 390 et 320 en 60/40 (valeur plus grande) |
| 6 | invariants LOCKED | 32 baselines inchangées |

## 6. Incidents

- Aucun dans le périmètre.

**Verdict :** DA-02.6 est livrée et **verrouillée par l'opérateur**. AUREN pose désormais chaque chiffre d'une seule façon, et dans un espace contraint il prend la plus grande taille qui tient **réellement** sur l'appareil. Prochaine étape du chemin critique : **Logo**.
