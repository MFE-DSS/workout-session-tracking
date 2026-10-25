# Sb_DA_02_4B_1_SOVEREIGN_READOUT — lecture souveraine au-dessus du rail

**Statut** : build — tier `isolated` (`check_scope`) · **Branche** : `sb/da-02-4b-1-sovereign-readout`
**Base** : canonique `4a0255e` · **Commande** : `GO BUILD — DA-02.4B.1 — SOVEREIGN READOUT ABOVE CALIBRATION LINE` (opérateur, 2026-10-25)
**Gate visuel** : **« ACCEPT — LOCK B.1 »** (opérateur, 2026-10-25)
**Autorité** : `docs/strategy/AUREN_VISUAL_CONTRACT.md` (`CALIBRATION-LINE-V1`, `FRAME-C-V1`), gabarit `docs/templates/VISUAL_SPRINT_TEMPLATE.md`

---

## 1. Brainstorming · Options · Risques · Choix retenu (`CLAUDE.md §3`)

| Question | Options | Choix | Pourquoi |
|---|---|---|---|
| Retirer la lecture interne du rail | A — prop opt-out, défaut = rendu verrouillé · B — garder et ajouter · C — densité `compact` · D — recopier le rail | **A** (P1) | B double la valeur ; C retire la bande (MUST NEVER) ; D sort le rail du gate |
| Props ajoutées au rail | `showReadout`, `showScale`, `showZoneLabels` | **`showReadout` seule** | les deux autres servent B.2 ; les écrire maintenant serait de l'opportunisme |
| Garder Frame C avant d'y composer (G2) | baselines tout de suite · **candidats revus d'abord, puis approuvés** | **candidats** | une baseline est un acte de l'opérateur ; un candidat se capture dans la même image et au même réglage que le gate, donc ce qui est approuvé est ce qui sera comparé |
| Juger la mise en page | calcul depuis `layout.ts` · **mesure dans la page rendue** | **mesure** | le calcul donnait 71 px pour la valeur, la page en rendait 85 : le « 70 » débordait du cadre de 10,6 px |
| Place du « 70 » à 390 (D-B) | (i) sous la rangée des noms · (ii) à droite du repère · (iii) aucun | **(i)**, opérateur | seule place qui respecte « sous le repère » et la rangée des noms gardée en B.1 |

| Risque | Parade |
|---|---|
| La prop change le rendu verrouillé | les 4 baselines `calibration-line-*` restent **vertes sans approbation**, à chaque passe |
| Une baseline approuvée diffère du rendu revu | comparaison à l'octet : les 8 nouvelles baselines sont **identiques** aux captures montrées à l'opérateur |
| Un contenu sort du cadre | la capture de revue mesure valeur, rail et chiffre prescrit et **échoue** s'ils sortent du champ de contenu, ou si le rail n'en prend pas toute la largeur |
| Un candidat entre dans le gate sans approbation | garde `test_a_candidate_is_reviewed_never_compared_until_the_operator_approves_it` |
| Une garde qui lit la prose | ma première version accusait un commentaire contenant `toHaveScreenshot` ; elle cherche désormais l'**appel** `.toHaveScreenshot(` |

## 2. Pré-vol (rendu avant toute modification)

| # | Point | Valeur |
|---|---|---|
| 1 | baseline ID | `calibration-line-320-target`, `-390-target`, `-390-push`, `-390-high-cost` (le `01-DA-02.2-rail-en-ligne-REFERENCE` de la déclaration est une image de CR ; son équivalent enregistré est `calibration-line-390-target`) |
| 2 | fichiers LOCKED impliqués | `CalibrationRail.tsx` (touché, P1) ; `layout.ts`, `geometry.ts`, `ReferenceMarker.tsx`, `ActiveCursor.tsx`, `frameGeometry.ts`, `InstrumentFrame.tsx` (intouchés) |
| 3 | invariants LOCKED en jeu | ligne de base pleine largeur ; curseur au-dessus, repère dessous ; bande au REST ; **aucune largeur du rail donnée à un autre module** ; géométrie des marqueurs ; aucune couleur nouvelle |
| 4 | delta permis | position de la lecture ; espacement vertical |
| 5 | fichiers prévus | voir §4 |

## Croquis validé

Source : la déclaration de l'opérateur, citée (GO BUILD, « TARGET OF THIS ITERATION »), puis l'option (i) qu'il a choisie sur rendu.

```
                 75 kg

    ─────────────▮▮────────────────
    ═ EASY ║ TARGET ║ PUSH ═ HIGH COST ═
                 ▭
                70
```

## Inventaire — une information, une seule fois

| Élément | Information | Source (contrat de données) | Doublon ? |
|---|---|---|---|
| valeur au-dessus (« 75 kg ») | la charge choisie, en nombre | `selectedValue`, `unit` | non |
| curseur (`signal`) | où est le choix sur l'échelle de coût | `selectedPosition` | non : position, pas nombre |
| repère (`system`) | où est la prescription | `referencePosition` | non |
| chiffre sous le repère (« 70 ») | la prescription, en nombre | `referenceValue` | **oui en PUSH et HIGH COST à 390**, avec le « 70 » de l'échelle chiffrée : accepté par l'opérateur jusqu'à B.2 |
| bande de zones | le coût relatif de chaque plage | `low/targetLow/targetHigh/highCost Boundary` | non |
| segment d'écart | l'écart choix → prescription | dérivé des deux positions | non : le delta chiffré est retiré (D-A) |
| échelle chiffrée (390) | la valeur des index majeurs | `stepValues` | voir le « 70 » ci-dessus |
| noms de zone (390) | le nom de chaque plage | `ZONE_LABEL` | non : plus écrits dans une lecture |
| ~~« PRESCRIT »~~ · ~~« ±0 · TARGET »~~ · ~~« +5 »~~ | — | — | **retirés** (D-A, G3) |

En TARGET, « 70 kg » au-dessus et « 70 » dessous sont deux informations différentes (choix et prescription) qui coïncident. Ce n'est pas un doublon de source, mais l'œil lit deux fois 70.

## Comparaison avec la référence validée

| Référence validée | Tranche / date | Ce qui doit survivre | Survit ? |
|---|---|---|---|
| rail en ligne pleine largeur | DA-02.2 (PR #286) ; baselines approuvées G1 | ligne horizontale, bande de zones, curseur dessus / repère dessous, géométrie des marqueurs | **oui** : le rail est le composant verrouillé lui-même, à 371 px (390) et 305 px (320), soit toute la largeur du champ ; ses 4 baselines restent vertes |
| Frame C | DA-02.3 (PR #287) ; baselines vides approuvées G2 | rail de montage, marques de registration, trait secondaire | **oui** : composant inchangé ; `frame-c-*-empty` vertes |

## Changement unique de l'itération

- Demande : « ONE perceptual change only: THE SELECTED VALUE MOVES ABOVE THE RAIL AND BECOMES THE SOVEREIGN READOUT. »
- Changement : la lecture passe de **sous le rail, dans le composant**, à **au-dessus du rail, composée par la surface**. Le chiffre prescrit s'écrit sous le repère, sans mot.
- Hors itération, explicitement : masquage de l'échelle et des noms (B.2), boutons + / −, surbrillance, taille en séance (R1–R4).

## 3. Relecture du relevé de décisions (`CLAUDE.md §5.2`)

Relevé applicable : `AUREN_VISUAL_CONTRACT.md` §6 (décisions DA-02.4) et §7 (décisions DA-02.4B.1).

| Décision | Verdict |
|---|---|
| §6-1 repartir du rail en ligne DA-02.2, pleine largeur | **respectée** |
| §6-2 REST garde la ligne et la bande | **respectée** : rien n'est retiré du rail (pas d'état REST en B.1) |
| §6-3 profondeur par la relation curseur / ligne / repère, pas un second rectangle | **respectée** : aucun fond ajouté |
| §6-4 rail en champ hors chemin critique | **respectée** : non utilisé |
| §6-5 valeur souveraine au-dessus, sans prendre de largeur au rail | **respectée** : mesurée |
| §6-6 180 × 120 : instrument compact dédié | **non concernée** |
| §6-7 DA-02.4 rejeté, rien de sa composition | **respectée** : la branche DA-02.4 n'est pas utilisée |
| §7 G1 4 baselines approuvées, non remplacées | **respectée** : inchangées à l'octet |
| §7 G2 Frame C gardé avant composition | **respectée** : approuvé, puis composé |
| §7 G3 doublons résolus par la composition | **respectée** |
| §7 P1 props de présentation seulement, défaut identique | **respectée** : `showReadout`, défaut prouvé par le gate |
| §7 P2 `u` suit la densité | **respectée** : 4 et 3, testés |
| §7 D-A delta retiré | **respectée** |
| §7 D-B (i) chiffre prescrit sous le bloc du rail | **respectée** |
| §7 double « 70 » accepté jusqu'à B.2 | **respectée**, signalée dans l'inventaire |
| `CLAUDE.md §5.4` couleur = token | **respectée** : `color.system`, `color.ink`, `color.ink2` ; aucun hex (scan du dossier `instrument`) |

## 4. Réalisation

| Fichier | Rôle |
|---|---|
| `src/ui/calibration/CalibrationRail.tsx` | prop `showReadout` (défaut `true`) via `railBlocks()` ; rien d'autre |
| `src/ui/instrument/HorizontalInstrumentSurface.tsx` | la composition : `surfaceLayout()` pur, testé ; rendu dans `InstrumentFrame variant="rail"` |
| `src/ui/instrument/SurfaceB1Gallery.tsx`, `index.ts` | banc appareil `EXPO_PUBLIC_GALLERY=surface-b1` : une surface à glisser, les six fixtures |
| `src/ui/contract/fixtures.ts`, `ContractFixture.tsx` | fixtures gouvernées `frame-c-*-empty` et `surface-*` |
| `src/ui/contract/candidates.ts` | les candidats de revue (vide entre deux itérations) |
| `visual-contract/review.config.ts`, `review.spec.ts`, `run.sh review` | capture de revue : même image, même réglage ; 1× pour la baseline, 2× pour la lecture ; mesure et contrôle de débordement |
| `visual-contract/baselines/` | 8 nouvelles baselines + manifeste ; les 4 du rail portent l'approbation explicite G1 |
| `tests/test_visual_contract_governance.py` | `INSTRUMENT-SURFACE-B1` LOCKED ; nouvelle garde sur les candidats |
| `AUREN_VISUAL_CONTRACT.md` | §2 registre, §4 Frame C, §7 décisions, §8 fiche B.1, §9 itérations suivantes |

## 5. Post-vol

| # | Point | Résultat |
|---|---|---|
| 1 | fichiers modifiés | §4 |
| 2 | tests structurels | `tsc` propre · jest **295 / 295** · gardes Python **11 / 11** |
| 3 | régression visuelle | `run.sh test` : **13 / 13** (12 baselines + fixture inconnue) |
| 4 | avant / après des fixtures LOCKED touchées | aucune fixture LOCKED n'a changé : les 4 du rail sont identiques ; Frame C et B.1 sont **ajoutées**, identiques à l'octet aux rendus revus |
| 5 | deltas voulus | la lecture au-dessus du rail ; le chiffre prescrit sous le bloc du rail ; plus de « PRESCRIT », de « ±0 · TARGET », de delta |
| 6 | invariants LOCKED | ligne de base pleine largeur ✓ · curseur dessus, repère dessous ✓ · bande ✓ · aucune largeur cédée ✓ · marqueurs ✓ · aucune couleur nouvelle ✓ · Frame C ✓ |

**Géométrie mesurée dans la page rendue** (px depuis le haut du cadre)

| | 390 × 220 | 320 × 180 |
|---|---|---|
| champ de contenu | 371,2 × 192,2 | 305,9 × 159,1 |
| valeur | `type.readout` · 11,4 → 82,4 | `type.figure` · 25,0 → 67,0 |
| rail (dessin + noms) | 371 de large · 94,4 → 171,2 | 305 de large · 76,0 → 121,6 |
| chiffre prescrit | 175,2 → 198,2 | 124,6 → 147,6 |
| marge basse du champ | 3,4 (+ 18,4 réservés au rail du cadre) | 18,6 |

**Rendu sur appareil** : le banc a été servi à l'iPhone (bundle iOS construit) ; le jugement produit est celui de l'opérateur, qui a accepté B.1.

## 6. Incidents dans le périmètre

- **Débordement trouvé par la mesure** : la petite unité « kg » ouvrait sa propre boîte de ligne et grandissait la ligne de la valeur (85 px au lieu de 71). Corrigé en lui donnant une hauteur de ligne égale à sa taille.
- **Installation intermittente dans le conteneur du gate** : `npm ci` sur le volume partagé échoue une passe sur deux (archives corrompues, `expo` absent). Rien n'est écrit dans ce cas ; la passe suivante réussit. **Hors périmètre**, à traiter dans une tranche d'outillage.
- **Point de montage Docker** : le conteneur laisse un dossier `node_modules` vide côté Mac ; le lien symbolique du banc appareil est retiré avant chaque passe du gate.

## 7. Après B.1 — demandes de l'opérateur

Rangées dans `AUREN_VISUAL_CONTRACT §9`, une itération chacune :
- **R1** surface centrée et plus grande dans la carte de séance ;
- **R2** rail plus haut, posé plus bas (LOCKED → baseline) ;
- **R3** boutons + / − ;
- **R4** surbrillance de la zone traversée plus contrastée (LOCKED → baseline).

Ordre proposé : B.2 (déjà prévue), puis R4, R2, R3, puis R1, l'intégration séance, qui hérite de tout le reste.

**Verdict :** DA-02.4B.1 est livrée et **verrouillée par l'opérateur**.
- Le rail DA-02.2 est intact : ses 4 baselines sont vertes, et il n'a reçu qu'une prop de présentation.
- La valeur choisie est souveraine au-dessus.
- Le chiffre prescrit est sous le repère, sans mot.
- Frame C est désormais gardé à vide.
- Les six compositions sont des baselines identiques à l'octet à ce que l'opérateur a vu.
- Prochaine étape : **DA-02.4B.2 — divulgation progressive**.
