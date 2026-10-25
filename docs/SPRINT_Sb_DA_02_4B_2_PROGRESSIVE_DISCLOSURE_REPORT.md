# Sb_DA_02_4B_2_PROGRESSIVE_DISCLOSURE — l'instrument au repos

**Statut** : build — tier `isolated` · **Branche** : `sb/da-02-4b-2-progressive-disclosure`
**Base** : canonique `347c81b` · **Commande** : « go » de l'opérateur sur DA-02.4B.2 (2026-10-25), périmètre fixé par le GO BUILD de B.1 (« B.2 IS EXPLICITLY OUT OF SCOPE » : la liste de ce qui revient à B.2)
**Gate visuel** : **« ACCEPT »** (opérateur, 2026-10-25)
**Autorité** : `AUREN_VISUAL_CONTRACT.md` (`CALIBRATION-LINE-V1`, `FRAME-C-V1`, `INSTRUMENT-SURFACE-B1`)

---

## 1. Brainstorming · Options · Risques · Choix retenu (`CLAUDE.md §3`)

| Question | Options | Choix | Qui |
|---|---|---|---|
| Que garde le repos ? | garder le « 70 » · le cacher aussi | **garder** | opérateur |
| Où est le « 70 » quand les noms sont cachés (390) ? | fixe · remonte au repos | **fixe, pas de saut** | opérateur |
| Retour au repos | 1,5 s après le dernier geste · dès qu'on lâche | **1,5 s** | opérateur |
| Où vit l'état | dans la surface · **contrôleur séparé, minuterie injectée** + hook mince | **séparé** | agent : la surface reste pure et ses fixtures restent déterministes ; le contrôleur se teste sans rendu |
| État par défaut de la surface | `rest` · **`adjusting`** | **`adjusting`** | agent : c'est le rendu B.1, donc ses 6 baselines n'ont pas à changer — preuve que rien n'a bougé |
| Animation du passage | fondu · **immédiat** | **immédiat** | agent : un seul changement par itération ; un fondu serait un second objet à juger |

| Risque | Parade |
|---|---|
| Les nouvelles props changent le rendu verrouillé | 12 baselines vertes **sans approbation** |
| Quelque chose saute quand les noms apparaissent | `referenceTop` et la hauteur de pile calculés sur le rail complet dans les deux états ; testé (6 cas) et mesuré (« 70 » à y 187,2 dans les deux) |
| Le retour au repos coupe un glissé | chaque geste relance le délai ; testé avec minuterie simulée |

## 2. Pré-vol

| # | Point | Valeur |
|---|---|---|
| 1 | baselines qui font foi | les 12 existantes ; les 6 `surface-*` deviennent l'état réglage |
| 2 | fichiers LOCKED impliqués | `CalibrationRail.tsx` (`showScale`, `showZoneLabels`, autorisés en P1) ; `HorizontalInstrumentSurface.tsx` (`presentation`) |
| 3 | invariants | ligne et bande au repos ; aucune largeur cédée ; aucune géométrie touchée ; même libellé d'accessibilité |
| 4 | delta permis | au repos seulement : échelle chiffrée et noms de zone masqués |
| 5 | fichiers prévus | §4 |

## Croquis validé

Validé par l'opérateur avant le code (questions à aperçu, 2026-10-25) :

```
REST                         ADJUSTING

        75 kg                        75 kg

 ───────▮▮──────────          ───────▮▮──────────
 ═══ bande de zones ═══       ═══ bande de zones ═══
       ▭                       55 60 65 70 75 80 85
                              EASY TARGET PUSH HIGH COST
       70                            70     ← même place
```

## Inventaire — une information, une seule fois

| Élément | Information | Source (contrat de données) | Doublon ? |
|---|---|---|---|
| valeur au-dessus | la charge choisie | `selectedValue`, `unit` | non |
| curseur | où est le choix | `selectedPosition` | non |
| repère | où est la prescription | `referencePosition` | non |
| chiffre sous le repère | la prescription, en nombre | `referenceValue` | **au repos : non** (l'échelle est masquée) ; en réglage : le double « 70 » de B.1 subsiste, accepté |
| bande de zones | le coût relatif | bornes de zone | non |
| échelle chiffrée (réglage) | les valeurs des index | `stepValues` | voir « 70 » |
| noms de zone (réglage) | le nom des plages | `ZONE_LABEL` | non |

## Comparaison avec la référence validée

| Référence validée | Tranche / date | Ce qui doit survivre | Survit ? |
|---|---|---|---|
| `INSTRUMENT-SURFACE-B1` | DA-02.4B.1, 2026-10-25 | tout, dans l'état réglage | **oui** : 6 baselines vertes sans approbation |
| `CALIBRATION-LINE-V1` | DA-02.2 | ligne, bande, marqueurs | **oui** : 4 baselines vertes ; au repos la ligne et la bande sont là |
| `FRAME-C-V1` | DA-02.3 | structure | **oui** : 2 baselines vertes |

## Changement unique de l'itération

- Demande : la divulgation progressive, réservée à B.2 par le GO BUILD de B.1.
- Changement : **au repos, l'échelle chiffrée et les noms de zone se retirent** ; ils reviennent en réglage.
- Hors itération : boutons + / − (R3), contraste de surbrillance (R4), hauteur du rail (R2), taille en séance (R1), fondu, état COMMITTED.

## 3. Relecture du relevé de décisions (`CLAUDE.md §5.2`)

| Décision | Verdict |
|---|---|
| §6-2 REST garde la ligne et la bande ; on retire les nombres secondaires et les noms, jamais l'ADN | **respectée** : c'est exactement ce que fait le repos |
| §6-5 valeur souveraine sans largeur prise au rail | **respectée** |
| §6-7 du rejet DA-02.4, ne garder que le principe REST / ADJUSTING | **respectée** : seul le principe est repris, aucun code de la branche rejetée |
| §7 P1 props de présentation, défaut identique | **respectée** : deux props, défaut prouvé par le gate |
| §7 D-B (i) chiffre prescrit sous le bloc du rail | **respectée**, et fixe |
| §8 MUST PRESERVE de B.1 | **respectée** |
| décisions B.2 (§10) : garder le « 70 », fixe, 1,5 s | **respectées** |

## 4. Réalisation

| Fichier | Rôle |
|---|---|
| `src/ui/calibration/CalibrationRail.tsx` | `showScale`, `showZoneLabels` via `railBlocks()` |
| `src/ui/instrument/disclosure.ts` (+ test) | contrôleur REST / ADJUSTING, minuterie injectée ; hook `useDisclosure` |
| `src/ui/instrument/HorizontalInstrumentSurface.tsx` (+ test) | `presentation` ; positions calculées sur le rail complet |
| `src/ui/instrument/SurfaceB1Gallery.tsx` | le glissé réveille l'état réglage ; les fixtures au repos et en réglage |
| `src/ui/contract/fixtures.ts`, `ContractFixture.tsx`, `candidates.ts` | 3 fixtures au repos gouvernées ; candidats vidés |
| `visual-contract/baselines/` | 3 baselines au repos + manifeste |
| `tests/test_visual_contract_governance.py` | `INSTRUMENT-SURFACE-B2` LOCKED |
| `AUREN_VISUAL_CONTRACT.md` | registre, §10 |

## 5. Post-vol

| # | Point | Résultat |
|---|---|---|
| 1 | fichiers modifiés | §4 |
| 2 | tests structurels | tsc propre · jest **312 / 312** (dont 4 tests du contrôleur, 7 de stabilité) · gardes 11 / 11 |
| 3 | régression visuelle | **16 / 16** (15 baselines + fixture inconnue) |
| 4 | avant / après des fixtures LOCKED | aucune modifiée ; 3 ajoutées, identiques à l'octet aux rendus revus |
| 5 | delta voulu | au repos : échelle chiffrée et noms de zone masqués |
| 6 | invariants LOCKED | ligne ✓ · bande ✓ · marqueurs ✓ · largeur ✓ · Frame C ✓ · B.1 en réglage ✓ |

**Mesuré** : « 70 » à y 187,2 au repos comme en réglage ; aucun débordement ; à 320, repos = B.1 à l'octet. **Appareil** : banc servi à l'iPhone (bundle iOS construit) ; l'opérateur a rendu « ACCEPT » sur le tableau de revue et ce banc.

## 6. Incidents

- Installation intermittente dans le conteneur du gate : connue, hors périmètre, aucune écriture quand elle échoue.

**Verdict :** DA-02.4B.2 est livrée et **verrouillée par l'opérateur**. Au repos, l'instrument ne montre que la valeur, la ligne, la bande, les deux marqueurs et le chiffre prescrit ; un doigt fait apparaître l'échelle et les noms ; rien ne bouge entre les deux. Les 12 baselines précédentes sont intactes. Prochaines étapes : **R4, R2, R3, R1** (`AUREN_VISUAL_CONTRACT §9`), une itération chacune.
