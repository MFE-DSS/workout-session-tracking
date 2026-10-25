# `AUREN_VISUAL_CONTRACT` — ce que le produit doit continuer à montrer

**Statut** : actif · **Décision opérateur** : 2026-10-25 (`DA-GOV-01`)
**Gate automatique** : job CI `visual-contract`, comparaison de captures sur les fixtures de
`clients/mobile/src/ui/contract/fixtures.ts`, baselines dans `clients/mobile/visual-contract/baselines/`.
**Documents liés** :
- `AUREN_CALIBRATION_SYSTEM.md` (spec LOCKED v1) ;
- `AUREN_VISUAL_BACKBONE.md §8` (DA, roadmap) ;
- `AUREN_UI_ITERATION_PROTOCOL.md` et `CLAUDE.md §5.6–5.9` (garde-fous d'itération) ;
- gabarit de tâche visuelle : `docs/templates/VISUAL_SPRINT_TEMPLATE.md`.

---

## 0. Pourquoi

Les tests structurels protègent des invariants de code, **pas l'identité visuelle approuvée**.
DA-02.4 l'a montré : tous les tests passaient, et pourtant l'ADN horizontal du rail validé avait été
remplacé par une autre représentation. Ce contrat fixe ce qui ne doit pas bouger, et le gate le vérifie
au pixel.

## 1. Trois niveaux d'autorité

Ce sont des **métadonnées de gouvernance** : aucun code ne les déduit.

| Statut | Règle |
|---|---|
| **LOCKED** | **ne change pas visuellement sans approbation explicite de l'opérateur** |
| **CONSTRAINED** | évolue **seulement** à l'intérieur des invariants écrits ici |
| **EXPLORATION** | change librement dans le périmètre de la tranche ; n'a aucune autorité tant que l'opérateur ne l'a pas promu |

## 2. Registre

| Visual ID | Statut | Rôle | Autorité |
|---|---|---|---|
| `CALIBRATION-LINE-V1` | **LOCKED** (ADN) ; détails **CONSTRAINED** | coût relatif d'un écart à la prescription | DA-02.2 (PR #286) |
| `REFERENCE-MARKER-V1` | **LOCKED** | la prescription du moteur | DA-02.2 — `clients/mobile/src/ui/calibration/geometry.ts` |
| `ACTIVE-CURSOR-V1` | **LOCKED** | la décision de l'opérateur | DA-02.2 — `clients/mobile/src/ui/calibration/geometry.ts` |
| `FRAME-C-V1` | **LOCKED** (structure) ; composition intérieure **non verrouillée** | le module d'instrument | DA-02.3 (PR #287) — `clients/mobile/src/ui/instrument/frameGeometry.ts` (`rail`) |
| `SEMANTIC-TOKENS-V1` | **LOCKED** (sens) | `signal` = curseur / action de l'opérateur · `system` = prescription / calcul d'AUREN · `perfBelow` EASY · `ink` TARGET · `perfAbove` PUSH · `alert` HIGH COST (« coût », jamais « danger ») | `clients/mobile/src/ui/theme.ts`, `AUREN_CALIBRATION_SYSTEM §3` |
| `CALIBRATION-FIELD-V1` | **EXPLORATION**, hors chemin critique | rail vertical « en champ » : visualisation secondaire possible (plein écran, analyse), **jamais le contrôle de charge principal** | DA-02.3 ; décision opérateur DA-02.4 n° 4 |
| `INSTRUMENT-SURFACE` | **EXPLORATION** | composition Frame C + rail + lecture | à refaire en **DA-02.4B** à partir de `CALIBRATION-LINE-V1` |

---

## 3. `CALIBRATION-LINE-V1` — fiche complète

| Champ | Valeur |
|---|---|
| **Visual ID** | `CALIBRATION-LINE-V1` |
| **Statut** | LOCKED (ADN), détails CONSTRAINED |
| **Rôle sémantique** | montrer en un regard la prescription du moteur, la décision de l'opérateur et le coût relatif de l'écart (EASY · TARGET · PUSH · HIGH COST) |
| **Source d'autorité** | DA-02.2, PR #286 (`10a3c8d`). Code : `clients/mobile/src/ui/calibration/CalibrationRail.tsx`, `layout.ts`, `geometry.ts`, `ReferenceMarker.tsx`, `ActiveCursor.tsx` |
| **Baselines approuvées** | `calibration-line-320-target`, `calibration-line-390-target`, `calibration-line-390-push`, `calibration-line-390-high-cost` (`clients/mobile/visual-contract/baselines/manifest.json`) |
| **Fixtures requises** | TARGET (choix = prescription), PUSH, HIGH COST ; données du banc DA-02.2 (55–85 kg par pas de 2,5, prescription 70) |
| **Largeurs requises** | 320 et 390 |

**MUST PRESERVE**
- une **ligne de base horizontale** sur toute la largeur utile ;
- le **curseur au-dessus** de la ligne ;
- le **repère sous** la ligne ;
- une relation verticale nette entre le curseur, le repère et l'index choisi ;
- la **bande de zones**, qui fait partie du rail ;
- `signal` = le curseur de l'opérateur ; `system` = la prescription ;
- la géométrie des deux marqueurs, inchangée.

**MUST NEVER**
- remplacer le rail horizontal par des barres verticales « en champ » ;
- faire pivoter le rail ;
- retirer la ligne de base au REST ;
- retirer l'identité de la bande de zones au REST ;
- **donner de la largeur du rail à un autre module** ;
- redessiner le curseur ou le repère ;
- introduire une nouvelle couleur sémantique.

**MAY CHANGE** (CONSTRAINED)
- la densité des index mineurs ;
- la visibilité de l'échelle chiffrée ;
- la visibilité des noms de zone ;
- la typographie secondaire ;
- l'espacement autour.

Tout changement de ce type fait quand même rougir le gate : il passe par une approbation de baseline (§5).

## 4. Fiches courtes des autres éléments LOCKED

| Visual ID | MUST PRESERVE | MAY CHANGE | MUST NEVER | Fixtures / largeurs requises |
|---|---|---|---|---|
| `REFERENCE-MARKER-V1` | 6u × 4u ; fente de 1u = un index ; paroi de 2,5u ; encoche de 1u × 0,6u ; angles droits ; posé sous la ligne | sa couleur seulement via le token `system` | arrondi, flèche, pin, triangle ; couleur codée en dur | couvert par les 4 baselines de `CALIBRATION-LINE-V1` ; fixture isolée à ajouter |
| `ACTIVE-CURSOR-V1` | 6u × 10u ; même fente, même paroi, même largeur que le repère ; seul porteur du `signal` plein | — | pastille ronde, poignée SaaS, flèche ; perte de la fente | couvert par les 4 baselines ; fixture isolée à ajouter |
| `FRAME-C-V1` | rectiligne ; bord bas = rail de montage d'1u ; deux marques de registration d'1u ; trait secondaire de 0,35u ; marge ≥ 2u | la composition intérieure (DA-02.4B) | arrondi générique, ombre, dégradé, texture, décor | **baseline à enregistrer** (320 × 180, 390 × 220, à vide) |
| `SEMANTIC-TOKENS-V1` | le **sens** de chaque rôle (§2) | une valeur, **seulement** avec une mesure de contraste (`CLAUDE.md §5.4`) | un rôle détourné : `alert` = interdit, `signal` hors action de l'opérateur | — |

## 5. Protocole de test visuel

Pour chaque composant protégé :
1. ouvrir la fixture (`?fixture=<id>` sur le build `EXPO_PUBLIC_GALLERY=contract`) ;
2. être dans l'état exact de la fixture, sans mouvement (mouvement réduit) ;
3. capturer ;
4. comparer à la baseline approuvée, **tolérance zéro pixel** (seul le bruit de couleur est toléré) ;
5. échouer sur toute différence.

**Un échec n'est pas automatiquement un bug : il signifie REVUE VISUELLE REQUISE.**
- **Si le changement n'était pas voulu**, on corrige le code ; la baseline ne bouge pas.
- **S'il était voulu, seul l'opérateur l'approuve.** Les étapes :
  1. `bash clients/mobile/visual-contract/run.sh approve` ;
  2. mise à jour de `manifest.json` (`sha256`, `approved_by`, `approved_on`) ;
  3. avant / après présenté.
- Le gate **n'écrit jamais** une baseline (`updateSnapshots: 'none'`).
- `tests/test_visual_contract_governance.py` rougit si un PNG change sans son entrée de manifeste.

**Environnement figé** : image `mcr.microsoft.com/playwright:v1.63.0-noble`, épinglée par empreinte, en `linux/amd64`, identique en local (`run.sh`) et en CI. Chromium, polices, plateforme, viewport, langue, fuseau et mouvement réduit sont fixés. Une différence est donc un changement visuel, pas un environnement.

## 6. Décisions de l'opérateur sur DA-02.4 (2026-10-25)

1. On repart du **rail en ligne DA-02.2**, en pleine largeur.
2. **REST garde la ligne et la bande.** On retire surtout les nombres secondaires et les noms inutiles, **jamais l'ADN**.
3. **La profondeur vient de la relation mécanique** curseur au-dessus → ligne → repère dessous, **pas d'un second rectangle sombre**.
4. Le rail vertical « en champ » sort du chemin critique (EXPLORATION, usage secondaire possible).
5. **La valeur est souveraine, au-dessus, sans prendre un pixel de largeur au rail.**
6. **180 × 120** : un instrument compact spécifique.
7. DA-02.4 est **rejeté**. On ne garde que le **principe** REST / ADJUSTING / COMMITTED, le **correctif des noms de zone** et les **mesures** ; la composition, jamais. Le code retenu sera revu à part.

**Chemin critique** : DA-GOV-01 Visual Contract → DA-02.4B Horizontal Instrument Surface → Recessed Window → Numeric Readout system → Logo.
