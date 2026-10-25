# Sb_DA_02_5_RECESSED_WINDOW — la sous-zone de l'instrument

**Statut** : build — tier `isolated` · **Branche** : `sb/da-02-5-recessed-window`
**Base** : canonique `96a324e` · **Commande** : brief opérateur `DA-02.5 — RECESSED WINDOW` (2026-10-25)
**Gate visuel** : **« ACCEPT — LOCK W1 »** (opérateur, 2026-10-25)
**Autorité** : `AUREN_VISUAL_CONTRACT.md` (tous les Visual IDs LOCKED inchangés)

---

## 1. Brainstorming · Options · Risques · Choix retenu (`CLAUDE.md §3`)

| Question | Options | Choix | Qui |
|---|---|---|---|
| Forme de la fenêtre | W1 Inset (contour fin, une coupure, une marque) · W2 Slot (fente d'1u × 1,5u dans le bord haut) · W3 Rail recess (aucun contour, rail interne d'1u) | **W1** | opérateur : « le plus neutre avec les contours », un cadre fermé autour de l'information |
| Taille des valeurs | taille fixe · **le plus grand rôle existant qui tient** | **le plus grand qui tient** | opérateur : « les valeurs les plus grosses possibles » ; agent : sans nouvelle taille, `readout` → `figure` → `exercise` |
| Profondeur | ombre, dégradé · **géométrie et valeur seules** | aplat `field` sur la face `plate`, trait `line` | brief |
| Hiérarchie parent / enfant | même trait que Frame C · **plus fin et plus sourd** | 0,25u en `line` contre 0,35u en `ink3` | brief : « the child may never visually outweigh the parent » |
| Deux fenêtres | collées · **2u de châssis entre elles** | 2u | agent : le châssis visible entre les deux dit « une machine » |

| Risque | Parade |
|---|---|
| Une fenêtre déborde de Frame C ou en chevauche une autre | mesuré dans la page sur les 24 puis 8 rendus ; testé (jest) |
| Une valeur poussée au maximum est coupée | contrôle de la capture : largeur de défilement ≤ largeur visible pour chaque valeur |
| Une fenêtre ressemble à une carte SaaS | aucun arrondi (test), aucune ombre, aucune couleur sémantique (test) |
| Les primitives verrouillées bougent | 27 baselines vertes sans approbation |

## 2. Pré-vol

| # | Point | Valeur |
|---|---|---|
| 1 | baselines qui font foi | les 27 existantes, aucune ne doit bouger |
| 2 | fichiers LOCKED impliqués | aucun modifié ; Frame C utilisé tel quel comme parent |
| 3 | invariants | Frame C, rail, marqueurs, surfaces, boutons, tokens intouchés |
| 4 | delta permis | nouvelle géométrie `RecessedWindow`, sa galerie, ses fixtures, tests, docs |
| 5 | fichiers prévus | §4 |

## Croquis validé

Choisi par l'opérateur sur le tableau des trois candidats rendus, puis confirmé sur le rendu W1 aux valeurs agrandies :

```
┌─ Frame C ───────────────────────────────────────────┐
│ ┌──────────────────────────┐  ┌───────────────┐    │
│ │                          │  │ DERNIÈRE      │    │  ← deux fenêtres 60/40,
│ │        [ BodyMap ]       │  │ 72,5 kg       │    │    2u de châssis entre elles
│ │                          │  │               │    │
│ ▮──────────────────────────┘  ▮───────────────┘    │  ← une marque par fenêtre
│ ▮                                               ▮ │
└━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┘
```

## Inventaire — une information, une seule fois

| Élément | Information | Source (contrat de données) | Doublon ? |
|---|---|---|---|
| fenêtre | une sous-zone de l'instrument | aucune (structure) | non : ne porte aucun état |
| étiquette (« Dernière », « Repos ») | ce que dit la valeur | contenu de démonstration | non |
| valeur + unité | la donnée | contenu de démonstration | non |
| gabarit BodyMap | la place de la future BodyMap | aucune (gabarit) | non |

Contenus de démonstration seulement : aucun écran produit ne monte encore de fenêtre.

## Comparaison avec la référence validée

| Référence validée | Tranche / date | Ce qui doit survivre | Survit ? |
|---|---|---|---|
| `FRAME-C-V1` | DA-02.3 | la structure du parent | **oui** : composant intouché, baselines vertes |
| tous les Visual IDs LOCKED | DA-02.2 → DA-02.4B.3 | tout | **oui** : 27 baselines vertes sans approbation |

## Changement unique de l'itération

- Demande : « This sprint introduces one new structural primitive only: `RecessedWindow`. »
- Changement : **la primitive `RecessedWindow`**, isolée, avec sa galerie. Rien d'autre.

## 3. Relecture du relevé de décisions (`CLAUDE.md §5.2`)

| Décision | Verdict |
|---|---|
| brief — pas une carte, ni tuile, ni modale, ni relief 3D, ni HUD | **respectée** |
| brief — profondeur par géométrie et hiérarchie, sans ombre / dégradé / lueur / texture | **respectée** |
| brief — tout en `u`, pas de nouvelle grille | **respectée** (tests) |
| brief — tokens `field` / `plate` / `line` / `ink3` ; pas de `signal`, `system`, couleurs de zone | **respectée** (test) |
| brief — l'enfant ne pèse jamais plus que le parent | **respectée** : 0,25u en `line` contre 0,35u en `ink3` |
| brief — Frame C non modifié | **respectée** |
| brief — aucune intégration produit | **respectée** |
| `CLAUDE.md §5.4` — couleur = token | **respectée** |
| `AUREN_VISUAL_CONTRACT §6-3` — la profondeur ne vient pas d'un second rectangle sombre **sur le rail** | **non concernée** : la fenêtre n'est pas le rail ; elle est une sous-zone, et c'est justement son rôle d'être un champ creusé |

## 4. Réalisation

| Fichier | Rôle |
|---|---|
| `src/ui/instrument/recessedWindowGeometry.ts` | géométrie W1 en `u` ; `windowLayout` (une / deux / 60-40) |
| `src/ui/instrument/RecessedWindow.tsx` | la primitive : aplat, contour coupé, marque, champ de contenu |
| `src/ui/instrument/windowContent.ts` (+ test) | le plus grand rôle de chiffre existant qui tient |
| `src/ui/instrument/RecessedWindowFixture.tsx` | F1 / F2 / F3 dans Frame C |
| `src/ui/instrument/RecessedWindowGallery.tsx`, `index.ts` | galerie `EXPO_PUBLIC_GALLERY=recessed-window` |
| `src/ui/instrument/recessedWindow.test.ts` | grille, bornes, 60/40, chevauchement, arrondi, couleurs, hiérarchie |
| `src/ui/contract/fixtures.ts`, `ContractFixture.tsx`, `candidates.ts` | 8 fixtures `RECESSED-WINDOW-V1` ; candidats vidés |
| `visual-contract/review.spec.ts` | mesure des fenêtres et contrôle « aucune valeur coupée » |
| `visual-contract/baselines/` | 8 baselines + manifeste |
| `tests/test_visual_contract_governance.py` | `RECESSED-WINDOW-V1` LOCKED |
| `AUREN_VISUAL_CONTRACT.md` | registre, §12 |

## 5. Post-vol

| # | Point | Résultat |
|---|---|---|
| 1 | fichiers modifiés | §4 |
| 2 | tests structurels | tsc propre · jest **345 / 345** (grille, bornes, 60/40, couleurs, arrondi, tailles de valeur) · gardes 11 / 11 + 605 voisines |
| 3 | régression visuelle | **36 / 36** (35 baselines + fixture inconnue) |
| 4 | fixtures LOCKED touchées | aucune ; 8 ajoutées, identiques à l'octet aux rendus revus |
| 5 | delta voulu | la primitive `RecessedWindow` |
| 6 | invariants LOCKED | tous inchangés (27 baselines vertes) |

**Limite connue** : la largeur des chiffres est estimée prudemment (la police de l'iPhone diffère de celle du navigateur du gate) ; dans les fenêtres partagées, la valeur reste en `figure` (40) là où `readout` tiendrait peut-être. Le pas suivant serait une mesure réelle sur l'appareil.

## 6. Incidents

- Aucun dans le périmètre.

**Verdict :** DA-02.5 est livrée et **verrouillée par l'opérateur**. AUREN a sa sous-zone d'instrument : un champ creusé dans Frame C, plus calme que lui, qui accueille un chiffre, une BodyMap ou deux contenus côte à côte sans devenir une carte. Prochaine étape du chemin critique : **Numeric Readout system**.
