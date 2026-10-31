# Sb_COMPLETE_SESSION_ZONES — la fin de séance montre les zones travaillées

**Date :** 2026-10-31
**Branche :** `sb/complete-zones` (base canonique `d557e45`, après MISSION)
**Verdict :** voir la fin du rapport.

## 0. Commande et décisions de l'opérateur

- « continue sur le chemin critique » : après MISSION et l'exécution, la fin de séance.
- Planche COMPLETE : « OK ».

## 1. Brainstorming · Options · Risques · Choix retenu (`CLAUDE.md §3`)

| Option | Pour | Contre |
|---|---|---|
| A — garder les pastilles « Séries par zone » | aucun changement | seul écran de la séance sans le langage verrouillé |
| B — **le panneau BodyMap, séries faites dans l'étiquette** | même pièce que MISSION et l'exécution ; le compte reste lisible | un écran plus long (il défile déjà) |
| C — panneau + intensité par couleur selon le volume | lecture rapide | revendication d'intensité interdite (§20–21) |

**Choix : B.** **Risques** : glisser vers une lecture d'intensité (→ un compte en chiffres, jamais une couleur
graduée) ; compter des séries non faites (→ `zonesDone` ne lit que `done`, testé) ; rendre un écran défilant tronqué
(→ cadre de revue haut).

## 2. Pré-vol

| # | Point | Valeur |
|---|---|---|
| 1 | baselines qui font foi | les 75 du contrat |
| 2 | fichiers LOCKED impliqués | `BODYMAP-ZONES-V1` (panneau réutilisé) |
| 3 | invariants | séries faites, comptées ; zone une fois ; aucune intensité |
| 4 | delta permis | la carte « Séries par zone » |
| 5 | fichiers prévus | §4 |

## Croquis validé

```
 … records · ce que tu as fait · ton programme …
 SÉRIES PAR ZONE
 ┌ PECTORAUX · 9 ─────┬ DELTOÏDES LATÉRAUX · 6 ┐
 ├ DELTOÏDES POST. · 3┼ TRICEPS · 3 ───────────┤
 └────────────────────┴────────────────────────┘
 toutes / 0 · prochaine séance · [ Voir ma prochaine séance ]
```

## Inventaire — une information, une seule fois

| Élément | Information | Source (contrat de données) | Doublon ? |
|---|---|---|---|
| panneau BodyMap | où la séance a travaillé | zones principales du plan, séries `done` | non : remplace les pastilles qui le disaient |
| « · 9 » dans l'étiquette | combien de séries par zone | `zonesDone` | non : le total reste « 21 séries sur 21 prévues » |

## Comparaison avec la référence validée

| Référence validée | Tranche / date | Ce qui doit survivre | Survit ? |
|---|---|---|---|
| `BODYMAP-ZONES-V1` | DA-04.2 | panneau dérivé, fenêtres égales | **oui** |
| 75 baselines | DA-02 → MISSION | tout | **oui**, identiques au pixel |

## Changement unique de l'itération

- Changement : **« Séries par zone » devient le BodyMap de la séance.**
- Rien d'autre sur l'écran.

## 3. Relecture du relevé de décisions (`CLAUDE.md §5.2`)

| Décision | Verdict |
|---|---|
| image → zone, exercice → zones (agnostique) | **respectée** |
| §20–21 — aucune intensité, aucun effet | **respectée** (compte de séries faites) |
| moins de texte (opérateur) | **respectée** : les pastilles partent, l'image les remplace |
| `CLAUDE.md §5.3` — jamais une soustraction seule | **respectée** |
| `CLAUDE.md §5.4` — couleur = token | **respectée** (aucune couleur neuve) |
| aucun doublon verbal-visuel | **respectée** |

## 4. Réalisation

| Fichier | Rôle |
|---|---|
| `clients/mobile/src/ui/CompleteScreen.tsx` | le panneau à la place des pastilles |
| `clients/mobile/src/ui/bodymap/zonesDone.ts` (+ test) | `zonesDone`, `zonePanelPresets` |
| `clients/mobile/src/ui/contract/CompleteScreenFixture.tsx`, `fixtures.ts`, `ContractFixture.tsx`, `candidates.ts` | écran gouverné (séance jouée dans le réducteur, cadre haut) |
| `clients/mobile/visual-contract/review.spec.ts` | écran défilant : capturé, sans mesure de hauteur |
| `clients/mobile/visual-contract/baselines/` + manifeste | 2 baselines |
| `tests/test_visual_contract_governance.py` | `COMPLETE-SCREEN-V1` |
| contrat (registre, §26), backbone, registre des specs | suivi |

## 5. Post-vol

- 75 baselines inchangées ; 2 neuves, identiques à l'octet aux captures revues.
- 407 tests mobiles verts (dont 4 neufs).

**Verdict :** `COMPLETE-SCREEN-V1` **LOCKED** — les trois écrans d'une séance parlent le même langage.
