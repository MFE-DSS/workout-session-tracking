# Sb_DA_05_1_EXECUTION_SCREEN — l'écran d'exercice réel, avec sa zone

**Date :** 2026-10-31
**Branche :** `sb/da-05-1-execution-screen` (base canonique `fec77bb`, après DA-04.4)
**Verdict :** voir la fin du rapport.

## 0. Commande et décisions de l'opérateur

- Chemin critique : « avance sur ton critical path […] il faut plutôt qu'on converge vers la fin de la préparation
  de l'application » ; DA-05.1 redéfinie (écran d'exercice réel, pièces verrouillées).
- Première planche (le module verrouillé ne tenait pas) : « je vais prendre ta recommandation » (BodyMap au repos,
  exercice suivant), avec : moins de texte ; « La dernière fois […] l'afficher pour quand c'est nécessaire, pas
  systématique » ; ⇄ et ⋯ « mieux insérés » ; « les cases avec le poids, tu peux réduire un peu » ; « quand tu
  insères le truc des pectoraux […] c'est bien ».
- Seconde planche (série avec / sans zone, recommandé : avec) : « go ».

## 1. Brainstorming · Options · Risques · Choix retenu (`CLAUDE.md §3`)

| Option | Pour | Contre |
|---|---|---|
| A — module dans l'espace restant de l'écran actuel | aucune autre pièce ne bouge | ~95 px libres : le module n'est pas dessiné, il reste un vide |
| B — module de 158 px, consigne raccourcie | se lit bien | « Passer cette série » sort de l'écran (30–67 px) |
| C — zone au repos, pour l'exercice suivant | l'écran de série plein n'est pas touché ; on prépare la machine suivante | — retenue par l'opérateur |
| C + série avec zone, après la réduction du texte | plus de vide (~200 px libérés), zone toujours visible | — **retenue** (« go ») |

**Risques** : un écran mesuré faux (→ banc aux insets d'iPhone, contrôle des marges) ; une action poussée sous
l'indicateur d'accueil (→ contrôle au banc, 9 / 9) ; une information perdue en retirant du texte (→ la charge cible
reste sur le cadran, la fourchette sur la ligne de série, la dernière fois revient dès qu'elle diffère) ; une fenêtre
écrasée (→ non dessinée sous 110).

## 2. Pré-vol

| # | Point | Valeur |
|---|---|---|
| 1 | baselines qui font foi | les 65 du contrat |
| 2 | fichiers LOCKED impliqués | `BODYMAP-ZONES-V1` (fenêtre réutilisée), `NUMERIC-READOUT-V1` (« Dernière »), `RECESSED-WINDOW-V1` / Frame C (module) — tous réutilisés tels quels |
| 3 | invariants | zone du plan, jamais choisie par l'écran ; fait absent non dessiné ; cibles ≥ 44 ; actions au-dessus de l'indicateur |
| 4 | delta permis | l'écran d'exécution, le bouton icône, le cadran |
| 5 | fichiers prévus | §4 |

## Croquis validé

```
 SÉRIE                                   REPOS (avant un nouvel exercice)
 ✕   EXERCICE 1 / 7   •••                ✕   EXERCICE 1 / 7 · REPOS   •••
 Incline Smith Press            ⇄        ✓ Série 3 · 52,5 kg × 11  enregistrée
 Série 1 sur 3 · objectif 6–10 reps          ( 1:00 )  anneau 140
 ┌ PECTORAUX ─────────────────────┐      ┌ PECTORAUX ──────┬ DERNIÈRE ┐
 │        zone (≤ 150, ≥ 110)     │      │  zone suivante  │ 57,5 kg   │
 └────────────────────────────────┘      └─────────────────┴───────────┘
 [S1 en cours] [S2] [S3]                 Exercice suivant · 2 / 7 — Chest Press — 3 × 8–12
 │ Consolider la charge actuelle         [ Machine prise ? Remplacer › ]
 [ CHARGE 52,5 kg ] [ REPS 11 ]          [ −15 s ] [ +15 s ]
 [ Valider la série ]  Passer            [ Commencer maintenant ]
```

## Inventaire — une information, une seule fois

| Élément | Information | Source (contrat de données) | Doublon ? |
|---|---|---|---|
| fenêtre de zone (série) | où travaille l'exercice | `exercise.zone` (résolveur canonique) | non |
| fenêtre de zone + « Dernière » (repos) | où travaillera l'exercice suivant, sa dernière charge | `nextEx.zone`, `nextEx.previous` | non : « Dernière » n'est pas sur l'écran de série |
| intention | ce que le moteur demande | `guidance.intent_label` | non : cible chiffrée et justification retirées (cadran, ligne de série) |
| « La dernière fois » | la séance précédente | `previous` | **seulement si la charge du cadran diffère** |
| « Commencer maintenant » | l'action | — | sous-titre retiré : le nom est le titre du panneau |

## Comparaison avec la référence validée

| Référence validée | Tranche / date | Ce qui doit survivre | Survit ? |
|---|---|---|---|
| `BODYMAP-ZONES-V1` / `BODYMAP-MIT-BODY-V1` | DA-04.2–04.3 | caméras, traitement, zone en `system` | **oui**, fenêtres réutilisées telles quelles |
| `SESSION-CARD-R1` (module 60/40) | DA-02.7 | la grammaire du module | **oui**, même module, pleine largeur |
| écran d'exécution N0 (R6, R8, R10) | vNext | première fois = référence ; ⇄ à chaque série ; « Passer » à part | **oui** |
| 65 baselines | DA-02 → DA-04.3 | tout | **oui**, identiques au pixel |

## Changement unique de l'itération

- Changement : **l'écran d'exercice réel reçoit sa zone, et s'allège.**
- Rien d'autre : pas de serveur, pas de donnée, pas de règle d'entraînement ; MISSION ne reçoit que l'icône ⋯.

## 3. Relecture du relevé de décisions (`CLAUDE.md §5.2`)

| Décision | Verdict |
|---|---|
| opérateur 2026-10-31 — zone au repos pour l'exercice suivant | **respectée** |
| opérateur — moins de texte ; « La dernière fois » seulement si nécessaire | **respectée** (`showsLastTime`, testée) |
| opérateur — ⇄ / ⋯ mieux insérés | **respectée** : icônes dessinées, alignées |
| opérateur — cadrans plus petits | **respectée** |
| opérateur — série avec zone (« go ») | **respectée** |
| §21–§22 — zone du plan, jamais choisie ; fait absent non dessiné | **respectée** |
| aucun doublon verbal-visuel | **respectée** (inventaire) |
| R6 / R8 / R10 (vNext) | **respectées** |
| cible tactile 44 | **respectée** (icônes 44, touches 52) |
| `CLAUDE.md §5.3` — jamais une soustraction seule | **respectée** : le texte retiré part avec la zone qui occupe sa place |
| `CLAUDE.md §5.4` — couleur = token | **respectée** (`ink2`, `system`, tokens existants) |

## 4. Réalisation

| Fichier | Rôle |
|---|---|
| `clients/mobile/src/ui/ExecutionScreen.tsx` | zone en série (`SetZone`) et au repos (`ZoneModule`), intention seule, règle de la dernière fois, anneau 140, action sans doublon, icônes |
| `clients/mobile/src/domain/lastTime.ts` (+ test) | `lastLoadKg`, `showsLastTime` |
| `clients/mobile/src/ui/components.tsx` | `IconButton` dessiné (`close` · `more` · `swap`), `ValueDial` réduit |
| `Mission` / `Complete` / `Resume` / `Quiet` screens | même icône ⋯ |
| `clients/mobile/src/ui/contract/ExecutionScreenFixture.tsx`, `fixtures.ts`, `ContractFixture.tsx`, `candidates.ts` | l'écran réel gouverné, insets d'iPhone injectés ; candidats vidés |
| `clients/mobile/visual-contract/review.spec.ts` | contrôle des insets et des actions sur écran entier |
| `clients/mobile/visual-contract/baselines/` + manifeste | 6 baselines, approbation citée |
| `tests/test_visual_contract_governance.py` | identifiant `EXECUTION-SCREEN-V1` |
| `docs/strategy/AUREN_VISUAL_CONTRACT.md` (registre, §24), `AUREN_VISUAL_BACKBONE.md`, `SPEC_REGISTRY.md` | contrat et suivi |

## 5. Post-vol

- 65 baselines inchangées ; 6 neuves, identiques à l'octet aux captures de la planche revue.
- Banc : 9 / 9 écrans gardent leurs actions au-dessus de l'indicateur d'accueil, aux insets d'iPhone.
- Mesure fausse attrapée en route : un `SafeAreaProvider` dans le cadre de revue web re-mesurait les insets sur la
  fenêtre du navigateur (marge basse 508 px) ; corrigé par injection des contextes et contrôle des marges.

## Annexe de clôture (2026-10-31)

- Premier passage : PR `CONFLICTING` avec la clôture #329 (même ligne du registre) — aucune CI n'était partie ;
  fusion du canonique dans la branche, conflit résolu en gardant les deux lignes (`6ea6070`).
- Gate vérifié avant fusion : tête `6ea6070`, 10 / 10 checks verts (contrat visuel : 71 baselines identiques au
  pixel en CI), Sonar PR `OK`, 0 fil ouvert, `CLEAN`.
- PR #330 fusionnée en `--merge --match-head-commit` : **`d87f03b`** ; CI canonique `41208489688` **verte**.

**Verdict :** `EXECUTION-SCREEN-V1` **LOCKED** — l'écran d'exercice réel porte sa zone en série et celle de
l'exercice suivant au repos, avec moins de texte ; 6 baselines approuvées par l'opérateur.
