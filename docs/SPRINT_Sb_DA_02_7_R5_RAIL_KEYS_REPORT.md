# Sb_DA_02_7_R5_RAIL_KEYS — les touches − / + dans la grammaire de l'instrument

**Statut** : ✅ MERGÉE (`a4a1113`, closeout en annexe) — tier `isolated` · **Branche** : `sb/da-02-7-r5-rail-keys`
**Base** : R2 (`sb/da-02-7-r2-larger-rail`, PR #306) · **Commande** : « faire tous les R » (opérateur, 2026-10-25), puis « rail ou récède […] ce que tu recommanderais, fais-le » (2026-10-26)
**Gate visuel** : allure **Rail** retenue sur le tableau de revue (rendus 2×, Rail · Recessed · Index)
**Autorité** : `AUREN_VISUAL_CONTRACT.md` — `INSTRUMENT-CONTROLS-B3` (LOCKED) ; demande R5 (§9)

---

## 1. Brainstorming · Options · Risques · Choix retenu (`CLAUDE.md §3`)

| Question | Options | Choix | Qui |
|---|---|---|---|
| Quelle allure | **Rail** (rail de montage + registrations de Frame C) · Recessed (fenêtre creusée) · Index (fente d'1u dans le bord) | **Rail** | opérateur : « ce que tu recommanderais, fais-le », « tout sauf le basique » ; recommandation de l'agent |
| Pourquoi Rail | — | la seule qui reprend la pièce la plus reconnaissable de l'instrument ; Recessed confond commande et fenêtre de lecture ; Index ajoute une fente sans fonction | agent |
| Garder un sélecteur d'allure | prop `look` · **une seule allure** | **une seule** | agent : un contrat, pas un menu |

| Risque | Parade |
|---|---|
| Le glyphe perd du contraste sur la nouvelle face | mesuré : 15,4 : 1 sur `plate` (au lieu de 12,1 sur `line`) ; inactif 5,7 : 1 (au lieu de 4,5) |
| L'appui ne se voit plus | la face descend en `field` et le rail s'allume en `ink` |
| Le reste de l'instrument bouge | 23 baselines identiques à l'octet |

## 2. Pré-vol

| # | Point | Valeur |
|---|---|---|
| 1 | baselines qui font foi | les 35 ; 23 doivent rester identiques |
| 2 | fichier LOCKED impliqué | `StepControls.tsx` (traitement seulement) |
| 3 | invariants | `INSTRUMENT-CONTROLS-B3` : place, taille, comportement, accessibilité ; aucun `signal` |
| 4 | delta permis | la face, le bord, les repères, l'état appuyé |
| 5 | fichiers prévus | §4 |

## Croquis validé

Validé par l'opérateur sur le tableau de revue (allure « rail »), 2026-10-26 :

```
  ┌──────────────┐  ┌──────────────┐
  │   −  2,5     │  │   +  2,5     │   face plate, trait ink3 sur 3 côtés
  │ ▮          ▮ │  │ ▮          ▮ │   deux registrations d'1u
  └▀▀▀▀▀▀▀▀▀▀▀▀▀▀┘  └▀▀▀▀▀▀▀▀▀▀▀▀▀▀┘   rail de montage d'1u
```

## Inventaire — une information, une seule fois

| Élément | Information | Source (contrat de données) | Doublon ? |
|---|---|---|---|
| glyphe − / + | le sens du pas | `dir` | non |
| pas affiché (« 2,5 ») | l'écart au pas voisin | `stepValues` (`neighborStep`) | non : la valeur n'est dite que dans la lecture souveraine |
| rail et registrations | l'appartenance à l'instrument | — (structure, pas donnée) | non |

## Comparaison avec la référence validée

| Référence validée | Tranche / date | Ce qui doit survivre | Survit ? |
|---|---|---|---|
| `INSTRUMENT-CONTROLS-B3` | DA-02.4B.3 | place sous le cadre, taille, paire centrée, « − 2,5 » / « + 2,5 », inactif aux bornes | **oui** : géométrie et comportement inchangés |
| `FRAME-C-V1` | DA-02.3 | le rail de montage et les registrations, leurs proportions en u | **oui** : la touche les reprend tels quels |
| surfaces, rail, cadre, fenêtres | DA-02.2 → R2 | tout | **oui** : 23 baselines identiques à l'octet |

## Changement unique de l'itération

- Changement : **les touches − / + prennent l'allure d'un petit Frame C (rail de montage, registrations).**
- Rien d'autre.

## 3. Relecture du relevé de décisions (`CLAUDE.md §5.2`)

| Décision | Verdict |
|---|---|
| B.3 — P1 sous le cadre, gros, centrés | **respectée** |
| B.3 MUST NEVER « un bouton en `signal` » | **respectée** |
| B.3 — un seul chemin de sélection, une seule minuterie | **respectée** : comportement inchangé |
| `FRAME-C-V1` — pas d'arrondi, d'ombre, de dégradé, de décor | **respectée** : rail et registrations sont la structure de Frame C |
| `CLAUDE.md §5.4` — couleur = token, contraste mesuré | **respectée** : `plate`, `field`, `ink`, `ink2`, `ink3` ; ratios documentés §16 |
| demande R5 (« plus cockpit, dans la DA de l'instrument ») | **respectée** |

## 4. Réalisation

| Fichier | Rôle |
|---|---|
| `src/ui/instrument/StepControls.tsx` | face `plate`, trait sur 3 côtés, `KeyRail` (rail + 2 registrations), état appuyé |
| `visual-contract/baselines/` | 12 baselines `controls-*` ré-approuvées + manifeste |
| `AUREN_VISUAL_CONTRACT.md` | §9 (R5 livrée), §11 (traitement), §16 |

## 5. Post-vol

| # | Point | Résultat |
|---|---|---|
| 1 | fichiers modifiés | §4 |
| 2 | tests structurels | jest **353 / 353** · gardes 18 / 18 |
| 3 | régression visuelle | 36 / 36 après approbation ; 23 identiques, 12 ré-approuvées |
| 4 | avant / après | sur le tableau de revue ; l'allure rendue est celle de la variante « rail » revue, au module R2 |
| 5 | delta voulu | traitement des touches |
| 6 | invariants LOCKED | tout le reste identique à l'octet |

## 6. Incidents

- Aucun dans le périmètre.

**Verdict :** R5 est livrée. Les touches appartiennent désormais à l'instrument : un petit Frame C monté sous le grand. Suite : **R1** (carte de séance verticale).

---

## Annexe — closeout post-merge

| Élément | Valeur |
|---|---|
| PR | #307, mergée par `--merge --match-head-commit` (head `021b639`) sous GO MERGE permanent |
| Commit de merge | `a4a11132ceaebd7308e84d36b7b11eb8658d2d39` |
| CI de la PR | 11 checks verts, dont `visual contract (DA-GOV-01)` |
| CI canonique (push) | run `40308737711` : **8 jobs sur 8 verts** |
| Sonar | gate PR `OK`, 0 issue, 0 fil de revue non résolu |
| Incidents | aucun dans le périmètre |
| Nettoyage | worktree et branche `sb/da-02-7-r5-rail-keys` supprimés (local et distant) |
