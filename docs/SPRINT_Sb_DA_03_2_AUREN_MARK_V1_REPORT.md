# Sb_DA_03_2_AUREN_MARK_V1 — la marque, verrouillée

**Statut** : 🟡 PR ouverte — tier `isolated` · **Branche** : `sb/da-03-2-auren-mark-v1`
**Base** : canonique `14a6e3a` · **Commande** : décision opérateur DA-03.2, « ACCEPT — `MARK-D-HYBRID` becomes `AUREN-MARK-V1` » (2026-10-27), puis « reprends le travail »
**Gate visuel** : planches DA-03.1 et DA-03.2 revues par l'opérateur ; **« ACCEPT »** sur D
**Autorité** : `AUREN_VISUAL_CONTRACT.md` §18 (neuf) ; `ACTIVE-CURSOR-V1`, `REFERENCE-MARKER-V1` (géométrie d'origine)

---

## 1. Brainstorming · Options · Risques · Choix retenu (`CLAUDE.md §3`)

| Question | Options | Choix | Qui |
|---|---|---|---|
| Quelle marque | D (curseur sur repère) · A2 (curseur sur rail) | **D** ; A2 retiré, gardé comme historique d'exploration (non committé) | opérateur |
| Un dessin ou plusieurs | un vecteur unique · **trois dessins optiques** | **trois** : un vecteur unique forcé à 16 px perd ses fentes, à 12 px ses pièces se soudent (audit au pixel DA-03.2) | agent, mesuré ; opérateur, accepté |
| Règle de taille | celle de la planche (12 micro, 13–19 compact) · **celle de l'opérateur** | **12–15 micro · 16–19 compact · 20+ primary · rien sous 12** | opérateur — le code de la planche a été corrigé pour la suivre |
| Où vivent les sources | dans le client · **`design/auren/source/brand/mark/`** | **design/auren**, par évolution gouvernée de l'allowlist (le garde l'exige pour tout SVG) | agent |
| Couleur dans la source | `#000` · **`currentColor`** | **`currentColor`** : aucune couleur inscrite, l'encre est un token passé à l'exécution | opérateur (« do not bake color ») |
| Statut d'asset | `approved` · **`provisional`** | **`provisional`** : la clearance du nom Auren est ouverte, et `approved` exige des revues (juridique, mobile) non faites ; la **géométrie** est LOCKED, l'**asset** ne l'est pas juridiquement | agent, selon `AUREN_VISUAL_ASSET_MANIFEST §6` |
| Montage produit | sur des écrans · **fixtures du contrat seulement** | **fixtures** : l'asset integration gate est fermé ; l'ancien glyphe PWA reste en place jusqu'à l'icône (DA-03.3) | agent |

| Risque | Parade |
|---|---|
| La source et le code divergent | `tests/test_auren_mark_v1.py` : chemins identiques à l'octet ; mutation plantée (1 unité) → rouge |
| L'appelant choisit un mauvais dessin | `AurenMark` ne prend qu'une taille ; `markDrawingFor` testé à chaque borne (11, 12, 15, 16, 19, 20) |
| Une baseline « exacte » dépend quand même de l'anticrénelage | décodage des PNG : **2 couleurs exactement** (`field`, `ink`) à 12, 16, 32, 64, 128 px |
| Les composants verrouillés bougent | 37 baselines existantes identiques à l'octet |
| L'origine générative passe inaperçue | provenance : directions issues d'images Midjourney fournies par l'opérateur, géométrie refaite à neuf, à porter à la revue juridique |

## 2. Pré-vol

| # | Point | Valeur |
|---|---|---|
| 1 | baselines qui font foi | les 37 existantes, toutes inchangées ; 9 neuves |
| 2 | fichiers LOCKED impliqués | aucun modifié : la surface, la carte et les touches sont rendues telles quelles, la marque est posée dessus |
| 3 | invariants | `ACTIVE-CURSOR-V1` / `REFERENCE-MARKER-V1` (proportions héritées : mur : fente = 2,5 : 1, même largeur, fente ouverte en haut) |
| 4 | delta permis | une nouvelle entrée de contrat et ses fixtures |
| 5 | fichiers prévus | §4 |

## Croquis validé

Validé par l'opérateur sur la planche DA-03.2 (rendus 2×, sept tailles, cinq contextes, placements), 2026-10-27 :

```
   ██ ██      le curseur actif — ce que tient l'opérateur
   ██ ██
   █████
   █████
              le vide : haut d'une fente ; le rail n'est pas dessiné
   ██ ██      le repère — ce que pose le système
   █████
              un seul axe : les deux fentes alignées
```

## Inventaire — une information, une seule fois

| Élément | Information | Source (contrat de données) | Doublon ? |
|---|---|---|---|
| marque | l'identité du fabricant | — (décoratif : le nom est dit par le texte adjacent) | non |
| curseur (dans la marque) | la décision de l'opérateur | sens hérité d'`ACTIVE-CURSOR-V1` | non |
| repère (dans la marque) | la prescription du système | sens hérité de `REFERENCE-MARKER-V1` | non |

Aucune donnée n'est affichée par la marque ; elle n'ajoute aucune information aux écrans où elle est posée.

## Comparaison avec la référence validée

| Référence validée | Tranche / date | Ce qui doit survivre | Survit ? |
|---|---|---|---|
| planche DA-03.2, `MARK-D-HYBRID` | 2026-10-26 / 27 | géométrie durcie, trois dessins | **oui** : chemins identiques à ceux de la planche (une seule correction : la règle de taille, pour suivre l'opérateur) |
| `ACTIVE-CURSOR-V1`, `REFERENCE-MARKER-V1` | DA-02.2 | proportions, sens | **oui** : mur : fente 2,5 : 1, même largeur, même axe |
| toutes les surfaces verrouillées | DA-02 → R1 | tout | **oui** : 37 baselines identiques à l'octet |

## Changement unique de l'itération

- Changement : **la marque `AUREN-MARK-V1` existe et est verrouillée** (sources, composant, contrat, 9 baselines).
- Rien d'autre : aucun écran produit ne la porte encore.

## 3. Relecture du relevé de décisions (`CLAUDE.md §5.2`)

| Décision | Verdict |
|---|---|
| « do not redesign the geometry » | **respectée** : chemins de la planche, à l'octet |
| trois maîtres optiques, règle 12–15 / 16–19 / 20+, rien sous 12 | **respectée** (testée) |
| pas de rail dans la marque | **respectée** (deux primitives, garde) |
| monochrome d'abord, pas de couleur dans la géométrie | **respectée** (`currentColor`, garde) |
| deux couleurs = expression contextuelle | **respectée** : `cursorColor` / `markerColor` optionnels, aucune baseline en deux couleurs |
| l'appelant ne choisit pas le dessin | **respectée** : `AurenMark` ne prend qu'une taille |
| baselines : monochrome, inverse, 12, 16, 32, 64, Frame C, carte, lancement | **respectée** (9) |
| `CLAUDE.md §5.4` — couleur = token | **respectée** : `field`, `ink`, `ink3` |
| `AUREN_VISUAL_ASSET_MANIFEST §6` — brand-bearing = `provisional` | **respectée** |

## 4. Réalisation

| Fichier | Rôle |
|---|---|
| `design/auren/source/brand/mark/mark-{primary,compact,micro}.svg` + `README.md` | les trois maîtres, sans couleur, et la règle |
| `clients/mobile/src/ui/brand/markGeometry.ts` (+ test) | géométrie d'exécution, `markDrawingFor`, `MARK_MIN_SIZE` |
| `clients/mobile/src/ui/brand/AurenMark.tsx` | le seul composant : taille + encre, rien sous 12 px |
| `clients/mobile/src/ui/brand/MarkPlacementFixture.tsx` | fixtures du contrat (échantillons, Frame C, carte, lancement) |
| `clients/mobile/src/ui/contract/fixtures.ts`, `ContractFixture.tsx` | `AUREN-MARK-V1`, 9 fixtures |
| `visual-contract/baselines/` | 9 baselines neuves + manifeste |
| `tests/test_auren_mark_v1.py` | sources = exécution, aucune couleur, grille entière, règle de taille |
| `tests/test_auren_asset_governance.py` | évolution gouvernée : les trois SVG de la marque, et rien d'autre sous `source/brand/` |
| `tests/test_visual_contract_governance.py` | `AUREN-MARK-V1` parmi les ids verrouillés |
| `design/auren/AUREN_VISUAL_ASSET_MANIFEST.md`, `AUREN_ASSET_PROVENANCE.md`, `README.md` | entrée `auren.brand.mark.v1`, provenance, statut |
| `AUREN_VISUAL_CONTRACT.md` | registre, §18 |

## 5. Post-vol

| # | Point | Résultat |
|---|---|---|
| 1 | fichiers modifiés | §4 |
| 2 | tests structurels | jest **387 / 387** · gardes visuelles et d'assets **49 / 49** · mutation de la source plantée : rouge |
| 3 | régression visuelle | **47 / 47** (37 identiques à l'octet + 9 neuves + le test de fixture inconnue) |
| 4 | exactitude | les 6 échantillons décodés : 2 couleurs exactement, aucun pixel d'anticrénelage |
| 5 | delta voulu | une entrée de contrat neuve |
| 6 | invariants LOCKED | 37 baselines inchangées |

## 6. Incidents

- La règle de taille codée pour la planche (12 px seul en micro) différait de celle de l'opérateur (12–15 px) ; le code suit la décision.

**Verdict :** `AUREN-MARK-V1` est verrouillée : une marque faite des deux pièces du produit, exacte au pixel de 12 à 128 px, sans couleur inscrite. Suite du chemin critique : **DA-03.3 — App icon**.
