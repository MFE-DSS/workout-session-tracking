# Sb_DA_02_7_R1_SESSION_CARD — la carte de série verticale

**Statut** : ✅ MERGÉE (`46d331c`, closeout en annexe) — tier `isolated` · **Branche** : `sb/da-02-7-r1-session-card`
**Base** : R5 (`sb/da-02-7-r5-rail-keys`) · **Commande** : « faire tous les R » (opérateur, 2026-10-25), puis la précision du 2026-10-26 sur la carte verticale et « tu prends le recommandé et boucle »
**Gate visuel** : composition décidée par l'opérateur en mots ; rendu montré dans le compte rendu final
**Autorité** : `AUREN_VISUAL_CONTRACT.md` — toutes les pièces LOCKED, réutilisées telles quelles ; nouvelle cible `SESSION-CARD-R1`

---

## 1. Brainstorming · Options · Risques · Choix retenu (`CLAUDE.md §3`)

| Question | Options | Choix | Qui |
|---|---|---|---|
| Où va l'instrument | centré au milieu (première demande R1) · **tout en bas** | **tout en bas**, touches comprises | opérateur, 2026-10-26 |
| Ce qui va au-dessus | **l'exercice, ses informations, des pièces « cockpit » d'exécution, dans le même design** | Recessed Windows dans Frame C : 60/40 (BodyMap · Dernière), paire (Repos · consigne d'exécution) | opérateur (le quoi) ; agent (la disposition, avec les pièces existantes) |
| La consigne d'exécution | inventer un contenu · **un emplacement nommé** | **emplacement nommé**, en pointillé comme le BodyMap | agent : la pièce n'est pas dessinée ; un faux contenu passerait pour une fonction |
| Le vide entre l'en-tête et l'instrument | des marges libres · **le premier module prend le reste** | **le premier module prend le reste** | agent : la leçon DA-02.4 (« du vide non intentionnel ») |
| Montage produit | sur l'écran de séance · **banc seulement** | **banc** | agent : sans bornes de zone du moteur (E7), le rail ne se dessine pas en produit |
| Largeur | marges de 20 px · **pleine largeur** | **pleine largeur** | agent : à 350 px l'instrument passe sous la densité expanded |

| Risque | Parade |
|---|---|
| Un doublon verbal / visuel | inventaire ci-dessous : la charge choisie n'est dite qu'une fois |
| Le refactor des fenêtres change leur rendu | les 8 baselines `window-*` restent identiques à l'octet |
| La carte déborde ou laisse un trou | test : les pièces remplissent l'écran exactement (844) |

## 2. Pré-vol

| # | Point | Valeur |
|---|---|---|
| 1 | baselines qui font foi | les 35 ; toutes doivent rester identiques |
| 2 | fichiers LOCKED impliqués | `RecessedWindowFixture.tsx` (extraction de `WindowModule`, type `slot` ajouté — rendu des fixtures inchangé) |
| 3 | invariants | toutes les pièces telles qu'approuvées ; instrument ≥ 360 de large |
| 4 | delta permis | une nouvelle composition, faite des pièces existantes |
| 5 | fichiers prévus | §4 |

## Croquis validé

Décrit par l'opérateur le 2026-10-26 (« tout en bas de ce cadran rectangulaire vertical, car entre, on va mettre l'exercice […] ») :

```
  SÉRIE 2 / 4 · 8 RÉPÉTITIONS
  Développé couché
  ┌──────────────┬────────────┐
  │   BodyMap    │ DERNIÈRE   │   module 60/40
  │   (attente)  │ 72,5 kg    │
  └──────────────┴────────────┘
  ┌─────────────┬─────────────┐
  │ REPOS       │ consigne    │   module en paire
  │ 2:30 min    │ (attente)   │
  └─────────────┴─────────────┘
  ┌───────────────────────────┐
  │          75 kg            │   instrument (B.1 / B.2, R2, R4)
  │  ═════════ rail ═════════ │
  │            70             │
  └───────────────────────────┘
     [ − 2,5 ]    [ + 2,5 ]       touches (B.3, R5) — sous le pouce
```

## Inventaire — une information, une seule fois

| Élément | Information | Source (contrat de données) | Doublon ? |
|---|---|---|---|
| en-tête | série, répétitions, exercice | séance (démo) | non |
| BodyMap (attente) | la zone travaillée | — (emplacement) | non |
| « Dernière » | la performance précédente | historique (démo) | non : ce n'est pas la décision |
| « Repos » | le repos prescrit | prescription (démo) | non |
| consigne d'exécution (attente) | comment bien faire | — (emplacement) | non |
| valeur de l'instrument | la charge choisie | `selectedValue` | non : dite une seule fois |
| rail, repère, « 70 » | coût de l'écart, prescription | bornes, `referenceValue` | non |
| touches | le pas voisin | `stepValues` | non |

## Comparaison avec la référence validée

| Référence validée | Tranche / date | Ce qui doit survivre | Survit ? |
|---|---|---|---|
| `INSTRUMENT-SURFACE-B1` / `-B2` + R2 + R4 | DA-02.4B, DA-02.7 | l'instrument entier, au pixel | **oui** : monté tel quel, 390 × 290 |
| `INSTRUMENT-CONTROLS-B3` + R5 | DA-02.4B.3, DA-02.7 | les touches | **oui** |
| `RECESSED-WINDOW-V1`, `NUMERIC-READOUT-V1` | DA-02.5 / .6 | fenêtres, valeurs mesurées | **oui** : 8 baselines `window-*` identiques |
| demande R1 initiale (« centré au milieu ») | 2026-10-25 | — | **remplacée** par la précision de l'opérateur du 2026-10-26 (tout en bas) |

## Changement unique de l'itération

- Changement : **une nouvelle composition cible — la carte de série verticale, instrument en bas.**
- Sans effet visible ailleurs : l'extraction de `WindowModule` (rendu identique).

## 3. Relecture du relevé de décisions (`CLAUDE.md §5.2`)

| Décision | Verdict |
|---|---|
| R1 précisée — poids et boutons tout en bas, pièces au-dessus | **respectée** |
| `RECESSED-WINDOW-V1` — une fenêtre n'est jamais une carte, deux fenêtres séparées de 2u | **respectée** |
| `CALIBRATION-LINE-V1` — pleine largeur, rien à côté | **respectée** |
| Aucun doublon verbal / visuel | **respectée** (inventaire) |
| `AUREN_CALIBRATION_SYSTEM` E7 — pas de rail sans bornes du moteur en produit | **respectée** : banc seulement |
| `CLAUDE.md §5.4` — couleur = token | **respectée** : aucune couleur neuve |
| `CLAUDE.md §5.3` — jamais une soustraction seule | **non concerné** : rien n'est retiré |

## 4. Réalisation

| Fichier | Rôle |
|---|---|
| `src/ui/instrument/SessionSetCard.tsx` (+ test) | la carte ; `sessionCardLayout` (le premier module prend le reste) |
| `src/ui/instrument/RecessedWindowFixture.tsx` | `WindowModule` extrait ; contenu `slot` (emplacement nommé) ; contenus de démo exportés |
| `src/ui/contract/fixtures.ts`, `ContractFixture.tsx` | `SESSION-CARD-R1`, 2 fixtures |
| `visual-contract/baselines/` | 2 baselines neuves + manifeste |
| `tests/test_visual_contract_governance.py` | `SESSION-CARD-R1` parmi les ids verrouillés |
| `AUREN_VISUAL_CONTRACT.md` | registre, §9 (R1 livrée), §17 |

## 5. Post-vol

| # | Point | Résultat |
|---|---|---|
| 1 | fichiers modifiés | §4 |
| 2 | tests structurels | jest **359 / 359** · gardes 18 / 18 |
| 3 | régression visuelle | **38 / 38** : 35 identiques à l'octet + 2 neuves |
| 4 | avant / après | les 2 cartes, dans le compte rendu final |
| 5 | delta voulu | une composition neuve |
| 6 | invariants LOCKED | 35 baselines inchangées |

## 6. Incidents

- Le libellé de l'emplacement, sur deux lignes, était aligné à gauche ; centré avant l'approbation (le BodyMap, sur une ligne, ne bouge pas).

**Verdict :** R1 est livrée comme cible. La carte se lit de haut en bas et la décision de charge est sous le pouce ; elle sera montée sur l'écran de séance quand le moteur fournira les bornes de zone (E7). Toutes les demandes R de l'opérateur sont closes.

---

## Annexe — closeout post-merge

| Élément | Valeur |
|---|---|
| PR | #308, mergée par `--merge --match-head-commit` (head `e635fbe`) sous GO MERGE permanent ; porte aussi le closeout de R4 et R2 |
| Commit de merge | `46d331c88f4f8d7aa704df0069e65d5353846ccc` |
| CI de la PR | 11 checks verts, dont `visual contract (DA-GOV-01)` sur les 37 baselines |
| CI canonique (push) | run `40310547617` : **8 jobs sur 8 verts** |
| Sonar | gate PR `OK`, 0 issue, 0 fil de revue non résolu |
| Incidents | aucun dans le périmètre |
| Nettoyage | worktrees et branches des quatre tranches (R4, R2, R5, R1) supprimés, local et distant ; ce closeout est poussé seul, docs uniquement |
