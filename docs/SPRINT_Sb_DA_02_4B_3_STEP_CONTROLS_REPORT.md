# Sb_DA_02_4B_3_STEP_CONTROLS — les commandes − / +

**Statut** : build — tier `isolated` · **Branche** : `sb/da-02-4b-3-step-controls`
**Base** : canonique `a8cd2a9` · **Commande** : brief opérateur `DA-02.4B.3 — STEP CONTROLS` (2026-10-25)
**Gate visuel** : **« ACCEPT »** (opérateur, 2026-10-25), boutons gardés tels que définis ; allure cockpit différée
**Autorité** : `AUREN_VISUAL_CONTRACT.md` (`CALIBRATION-LINE-V1`, `FRAME-C-V1`, `INSTRUMENT-SURFACE-B1`, `-B2`)

---

## 1. Brainstorming · Options · Risques · Choix retenu (`CLAUDE.md §3`)

| Question | Options | Choix | Qui |
|---|---|---|---|
| Placement | P1 sous le cadre · P2 sur le rail bas du cadre · P3 aux marques de registration | **P1** | opérateur, sur croquis tracés par-dessus le rendu B.2 exact. Mesure décisive : la bande basse de Frame C fait 18,4 px (390) / 13,8 px (320), donc la zone tactile de P2 / P3 sortait du cadre de toute façon |
| Taille et place | 104 × 44 aux extrémités (croquis) · **beaucoup plus gros, vers le centre, grisés** | **137 × 68 / 112 × 68, paire centrée, fond `line`** | opérateur |
| Chemin d'un appui | nouveau rappel + nouvel état · **le rappel du glissé, `onSelectPosition`** | **le même rappel** | agent : un seul chemin, la divulgation B.2 et son délai s'appliquent sans seconde machine d'état (exigence du brief) |
| Le pas | calculé (± 2,5) · **lu dans les `steps` / `stepValues` fournis** | **lu** | brief : « the domain remains authoritative » ; l'écart affiché est lu dans les valeurs, même irrégulières (testé) |
| Aux bornes | bouton masqué · **bouton inactif** | **inactif** | agent : la géométrie ne bouge jamais ; il s'éteint (glyphe `ink3`, sans pas) |
| Où vivent les baselines | réécrire B.2 · **nouveau Visual ID** | **`INSTRUMENT-CONTROLS-B3`** | brief |

| Risque | Parade |
|---|---|
| Les boutons poussent ou rognent l'instrument | sous le cadre ; 15 baselines verrouillées vertes sans approbation ; mesure : rail 371 / 305 px |
| Ils bougent d'un état à l'autre | géométrie fonction de la largeur seule ; mesuré identique dans les 12 états |
| Annonces d'accessibilité en double | les boutons disent leur action, le rail seul dit la valeur |
| Collision de nom de fichier | `stepControls.ts` et `StepControls.tsx` ne diffèrent que par la casse (système de fichiers du Mac) : module pur renommé `stepModel.ts` |

## 2. Pré-vol

| # | Point | Valeur |
|---|---|---|
| 1 | baselines qui font foi | les 15 existantes, aucune ne doit bouger |
| 2 | fichiers LOCKED impliqués | aucun modifié : `HorizontalInstrumentSurface` et le rail sont utilisés tels quels |
| 3 | invariants | rail pleine largeur ; rien à côté du rail ; Frame C, marqueurs, lecture, chiffre prescrit, divulgation inchangés |
| 4 | delta permis | placement, zone tactile, traitement des glyphes, câblage, accessibilité, réveil de la divulgation |
| 5 | fichiers prévus | §4 |

## Croquis validé

Choisi par l'opérateur sur le tableau de croquis (P1), puis ajusté par lui :

```
┌─ Frame C · instrument B.2 (inchangé) ───────────┐
│                     75 kg                        │
│  ─────────────────────▮▮──────────────────────── │
│  ═══════════════ bande de zones ═══════════════  │
│                       ▭                          │
│                       70                         │
└━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┘
        ┌──────────────┐  ┌──────────────┐
        │   −   2,5    │  │   +   2,5    │      ← gros, gris, centrés
        └──────────────┘  └──────────────┘
```

## Inventaire — une information, une seule fois

| Élément | Information | Source (contrat de données) | Doublon ? |
|---|---|---|---|
| glyphe « − » / « + » | le sens du réglage | direction du bouton | non |
| « 2,5 » | de combien un appui déplace la charge | écart entre deux `stepValues` voisins | non : nulle part ailleurs (l'échelle donne des valeurs, pas l'écart) |
| instrument B.2 au-dessus | valeur, position, prescription, coût | inchangé (§8, §10) | non |

## Comparaison avec la référence validée

| Référence validée | Tranche / date | Ce qui doit survivre | Survit ? |
|---|---|---|---|
| `INSTRUMENT-SURFACE-B1` / `-B2` | DA-02.4B.1 / B.2 | tout | **oui** : 9 baselines vertes sans approbation ; l'instrument au-dessus des boutons est le même composant |
| `CALIBRATION-LINE-V1`, `FRAME-C-V1` | DA-02.2 / DA-02.3 | tout | **oui** : 6 baselines vertes |

## Changement unique de l'itération

- Demande : « Add explicit decrement / increment controls to the horizontal calibration instrument. »
- Changement : **deux commandes − / + sous le cadre**. Rien d'autre.
- Hors itération : allure cockpit des boutons (R5), contraste de surbrillance (R4), hauteur du rail (R2), intégration séance (R1).

## 3. Relecture du relevé de décisions (`CLAUDE.md §5.2`)

| Décision | Verdict |
|---|---|
| brief B.3 — rail pleine largeur, rien à gauche / droite du rail | **respectée** (mesurée) |
| brief B.3 — pas de pilule, d'arrondi fort, de dégradé, d'ombre, de lueur | **respectée** : rectilignes, aplat |
| brief B.3 — l'ambre reste à l'objet contrôlé | **respectée** : aucun `signal` |
| brief B.3 — pas précédent / suivant du modèle existant, aucun pas calculé | **respectée** (tests) |
| brief B.3 — l'appui réveille la divulgation, délai 1,5 s inchangé, pas de nouvelle minuterie | **respectée** : même rappel que le glissé |
| brief B.3 — nouveau Visual ID, B.2 non réécrit | **respectée** |
| `CLAUDE.md §5.4` — couleur = token, contraste mesuré | **respectée** : `line`, `plate`, `ink`, `ink2`, `ink3` ; 12,1 / 7,2 / 4,5 : 1 sur `line` |
| §6-5 aucune largeur prise au rail | **respectée** |

## 4. Réalisation

| Fichier | Rôle |
|---|---|
| `src/ui/instrument/stepModel.ts` (+ test) | `neighborStep` (pas voisin lu dans les `steps`), `stepLabel` / `stepText`, `stepControlsLayout` (largeur seule) |
| `src/ui/instrument/StepControls.tsx` | les deux boutons, accessibles, inactifs aux bornes |
| `src/ui/instrument/InstrumentWithStepControls.tsx` | l'instrument B.2 inchangé + les boutons dessous |
| `src/ui/instrument/SurfaceB1Gallery.tsx` | banc appareil : glisser ou − / + |
| `src/ui/contract/fixtures.ts`, `ContractFixture.tsx`, `candidates.ts` | 12 fixtures B.3 gouvernées ; candidats vidés |
| `visual-contract/review.spec.ts` | mesure des boutons : sous le cadre, ≥ 44 pt, séparés |
| `visual-contract/baselines/` | 12 baselines + manifeste |
| `tests/test_visual_contract_governance.py` | `INSTRUMENT-CONTROLS-B3` LOCKED |
| `AUREN_VISUAL_CONTRACT.md` | registre, §9 (R3 fait, R5 ajouté), §11 |

## 5. Post-vol

| # | Point | Résultat |
|---|---|---|
| 1 | fichiers modifiés | §4 |
| 2 | tests structurels | tsc propre · jest **322 / 322** (10 nouveaux : pas voisin, bornes, accrochage, valeurs irrégulières, libellés, géométrie) · gardes 11 / 11 |
| 3 | régression visuelle | **28 / 28** (27 baselines + fixture inconnue) |
| 4 | fixtures LOCKED touchées | aucune ; 12 ajoutées, identiques à l'octet aux rendus revus |
| 5 | delta voulu | les deux boutons sous le cadre |
| 6 | invariants LOCKED | rail 371 / 305 px ✓ · rien à côté du rail ✓ · surface B.1 / B.2 ✓ · Frame C ✓ |

**Mesuré dans la page rendue** : 390 → 137 × 68 en x 62 et 215, 8 px sous le cadre ; 320 → 112 × 68 en x 54 et 178, 6 px sous le cadre ; identique dans les 12 états. **Appareil** : banc servi à l'iPhone (bundle iOS construit).

## 6. Incidents

- Collision de casse `stepControls.ts` / `StepControls.tsx`, attrapée par `tsc` : module renommé.
- Dimensions en pixels du manifeste écrites de tête, puis corrigées en lisant les en-têtes PNG (414 × 320, 344 × 278).

**Verdict :** DA-02.4B.3 est livrée et **verrouillée par l'opérateur**. L'instrument se règle au doigt sur le rail ou par deux gros boutons sous le cadre ; un appui prend exactement le pas voisin fourni par le domaine et réveille l'échelle comme un glissé. Les 15 baselines précédentes sont intactes. Suite : R4 (exploration prête), R2, R1 ; R5 en finition.
