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
| `INSTRUMENT-SURFACE-B1` | **LOCKED** (2026-10-25, « ACCEPT — LOCK B.1 ») | Frame C + rail en ligne pleine largeur + valeur souveraine au-dessus + chiffre prescrit sous le bloc du rail | DA-02.4B.1 — `clients/mobile/src/ui/instrument/HorizontalInstrumentSurface.tsx` (§8) |
| `INSTRUMENT-SURFACE-B2` | **LOCKED** (2026-10-25, « ACCEPT » B.2) | la même surface **au repos** : échelle chiffrée et noms de zone masqués ; l'état réglage est `INSTRUMENT-SURFACE-B1` | DA-02.4B.2 — `HorizontalInstrumentSurface` (`presentation`), `disclosure.ts` (§10) |
| `INSTRUMENT-CONTROLS-B3` | **LOCKED** (2026-10-25, « ACCEPT » B.3) | les commandes − / + sous le cadre (P1) : second moyen de régler, sans précision de glissé | DA-02.4B.3 — `StepControls.tsx`, `stepModel.ts`, `InstrumentWithStepControls.tsx` (§11) |
| `RECESSED-WINDOW-V1` | **LOCKED** (2026-10-25, W1 · Inset) | la sous-zone interne d'un instrument : un champ creusé dans Frame C, pas une carte | DA-02.5 — `RecessedWindow.tsx`, `recessedWindowGeometry.ts`, `windowContent.ts` (§12) |
| `INSTRUMENT-SURFACE` | **EXPLORATION** | les itérations suivantes de la surface (§9) | partent de `INSTRUMENT-SURFACE-B1` / `-B2` / `INSTRUMENT-CONTROLS-B3` |

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
| `FRAME-C-V1` | rectiligne ; bord bas = rail de montage d'1u ; deux marques de registration d'1u ; trait secondaire de 0,35u ; marge ≥ 2u | la composition intérieure (DA-02.4B) | arrondi générique, ombre, dégradé, texture, décor | `frame-c-390x220-empty` (u = 4), `frame-c-320x180-empty` (u = 3) — approuvées le 2026-10-25 (G2), avant toute composition |
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

## 7. Décisions de l'opérateur sur DA-02.4B.1 (2026-10-25)

| # | Décision |
|---|---|
| G1 | Les 4 baselines `calibration-line-*` sont **approuvées explicitement**. Elles font autorité pour le rail DA-02.2 **seul**. La collision « 70 » et les doublons verbal-visuels qu'elles contiennent sont des propriétés **connues** du rail autonome, pas des qualités voulues |
| G2 | Frame C vide est gardé (`frame-c-*-empty`) **avant** toute composition dedans |
| G3 | Les doublons se résolvent **par la composition**, jamais en changeant le rendu par défaut du rail |
| P1 | `CalibrationRail.tsx` reçoit des props de **présentation** opt-out (`showReadout` en B.1). Défaut = rendu verrouillé, aucune sémantique ni géométrie touchée, aucune connaissance de la surface |
| P2 | Le « 2× » de DA-02.3 ne s'applique pas au rail en ligne : `u` suit la densité (4 à 390, 3 à 320) |
| D-A | Le delta chiffré est **retiré** de la surface : l'écart curseur → repère le montre |
| D-B | Le chiffre prescrit s'écrit **sous** le repère, sans mot. À 390, il passe sous la rangée des noms de zone (option (i)), seule place qui respecte à la fois D-B et la rangée gardée en B.1 |
| — | Le double « 70 » (échelle chiffrée + chiffre prescrit) en PUSH et HIGH COST à 390 est **accepté jusqu'à B.2**, qui masquera l'échelle au repos |
| Gate | **« ACCEPT — LOCK B.1 »** : les six compositions deviennent les baselines de `INSTRUMENT-SURFACE-B1` |

## 8. `INSTRUMENT-SURFACE-B1` — fiche

| Champ | Valeur |
|---|---|
| **Statut** | LOCKED |
| **Rôle sémantique** | la décision de charge en un regard : la valeur choisie d'abord, puis sa relation à la prescription sur le rail |
| **Source d'autorité** | DA-02.4B.1. Code : `HorizontalInstrumentSurface.tsx`, plus `CalibrationRail.tsx` (`showReadout={false}`) et `InstrumentFrame` (`rail`), inchangés |
| **Baselines approuvées** | `surface-390x220-target`, `surface-390x220-push`, `surface-390x220-high-cost`, `surface-320x180-target`, `surface-320x180-push`, `surface-320x180-high-cost` |
| **Largeurs requises** | 390 × 220 (u = 4), 320 × 180 (u = 3) |

**MUST PRESERVE**
- tout `CALIBRATION-LINE-V1` et tout `FRAME-C-V1` ;
- le rail prend **toute** la largeur du champ de contenu ; rien ne se pose à côté ;
- la valeur choisie au-dessus, souveraine (`type.readout` à 390, `type.figure` à 320), avec son unité, tirée de `selectedValue` et `unit` seulement ;
- le chiffre prescrit sous le bloc du rail, centré sur le repère, en `system`, sans mot ;
- une information, une seule fois : pas de « PRESCRIT », pas de « ±0 · TARGET », pas de delta chiffré.

**MUST NEVER**
- réintroduire la lecture interne du rail dans la surface ;
- laisser un élément sortir du champ de contenu du cadre (la capture de revue le mesure et échoue).

## 9. Itérations suivantes demandées par l'opérateur (2026-10-25, à l'acceptation de B.1)

Chacune est **une** itération, avec son propre gate visuel. Celles qui touchent un élément LOCKED passent par une baseline approuvée.

| # | Demande (mots de l'opérateur, résumés) | Touche | Tranche |
|---|---|---|---|
| R1 | dans la séance, la surface **centrée au milieu de la carte**, en plus grand | intégration produit (écran séance) | intégration séance, après B.2 |
| R2 | le rail **un peu plus haut**, posé **plus bas**, pour mieux voir ses index | `CALIBRATION-LINE-V1` (LOCKED) → nouvelle baseline | itération dédiée |
| R3 | des boutons **+ / −** comme second moyen de régler, en plus du glissé | `INSTRUMENT-SURFACE` (élément ajouté) ; le rail porte déjà `onIncrement` / `onDecrement` | ✅ DA-02.4B.3, acceptée (§11) |
| R5 | les boutons − / + **plus « cockpit »**, dans la DA de l'instrument (opérateur, à l'acceptation de B.3) | `INSTRUMENT-CONTROLS-B3` (LOCKED) → nouvelle baseline | **finition différée**, avec les derniers détails ; B.3 reste la définition en vigueur |
| R4 | la **surbrillance de la zone** traversée plus contrastée, pour savoir où l'on est | `CALIBRATION-LINE-V1` (LOCKED : opacité des zones inactives) → nouvelle baseline | itération dédiée |
| B.2 | divulgation progressive REST / ADJUSTING (déjà prévue) | `INSTRUMENT-SURFACE` + props `showScale` / `showZoneLabels` | ✅ DA-02.4B.2, acceptée (§10) |

## 10. `INSTRUMENT-SURFACE-B2` — divulgation progressive (2026-10-25)

**Décisions de l'opérateur** (croquis validé avant le code) :
- au repos, le chiffre prescrit **reste** ; seuls l'échelle chiffrée et les noms de zone se retirent ;
- le « 70 » est **fixe** : même place dans les deux états, aucun saut sous le doigt ;
- retour au repos **1,5 s après le dernier geste** ; chaque geste relance le délai.

| Champ | Valeur |
|---|---|
| **Baselines approuvées** | `surface-390x220-target-rest`, `surface-390x220-push-rest`, `surface-390x220-high-cost-rest` (repos) ; l'état réglage reste gardé par les six `surface-*` de B.1 |
| **320 × 180** | en densité regular, le rail n'a ni échelle ni noms : le repos y est **identique à l'octet** à B.1, aucune baseline de plus |
| **Code** | `CalibrationRail.tsx` : props `showScale`, `showZoneLabels` (défaut = rendu verrouillé) ; `HorizontalInstrumentSurface` : `presentation` (défaut `adjusting` = B.1) ; `disclosure.ts` : contrôleur pur, minuterie injectée |

**MUST PRESERVE** : tout `INSTRUMENT-SURFACE-B1` ; au repos, la ligne, la bande, le curseur, le repère et le chiffre prescrit ; aucune position ne change entre les deux états.
**MUST NEVER** : retirer la ligne ou la bande au repos ; faire bouger la valeur, le rail ou le chiffre prescrit quand l'échelle apparaît ; décrire l'état autrement à l'accessibilité (même libellé dans les deux états).

## 11. `INSTRUMENT-CONTROLS-B3` — commandes − / + (2026-10-25)

**Décisions de l'opérateur** : placement **P1, sous le cadre** ; boutons **beaucoup plus gros**, **rapprochés du centre**, **grisés** pour dire qu'on peut appuyer ; « − 2,5 » / « + 2,5 ». Accepté tel quel ; l'allure plus cockpit est une finition différée (§9, R5).

| Champ | Valeur |
|---|---|
| **Baselines approuvées** (12 ; `adjusting` = juste après « + », un pas au-dessus) | `controls-390x220-target-rest`, `controls-390x220-push-rest`, `controls-390x220-high-cost-rest`, `controls-390x220-target-adjusting`, `controls-390x220-push-adjusting`, `controls-390x220-high-cost-adjusting`, `controls-320x180-target-rest`, `controls-320x180-push-rest`, `controls-320x180-high-cost-rest`, `controls-320x180-target-adjusting`, `controls-320x180-push-adjusting`, `controls-320x180-high-cost-adjusting` |
| **Géométrie** | sous le cadre, à 2u ; hauteur `ACTION_HEIGHT` (68) ; largeur 35 % du module chacun ; écart 4u ; paire centrée. 390 : 137 × 68 en x 62 / 215 ; 320 : 112 × 68 en x 54 / 178. **Ne dépend que de la largeur** |
| **Traitement** | fond `line`, trait `ink3` au poids secondaire de Frame C ; appui : fond `plate`, trait `ink` ; glyphe `ink` (12,1 : 1 sur `line`), pas affiché en `ink2` (7,2 : 1) ; inactif aux bornes : `ink3`, sans pas affiché. Aucun `signal` |
| **Comportement** | − / + = index précédent / suivant des `steps` fournis (`stepModel.neighborStep`), rien n'est calculé ; l'appui passe par `onSelectPosition`, le même rappel que le glissé, donc la divulgation se réveille et le délai de 1,5 s repart sans seconde minuterie |
| **Accessibilité** | boutons « Diminuer de 2,5 kilos » / « Augmenter de 2,5 kilos », inactifs aux bornes ; le rail garde son rôle ajustable et dit seul la valeur |

**MUST PRESERVE** : tout `INSTRUMENT-SURFACE-B1` / `-B2` au-dessus, inchangé ; le rail à pleine largeur ; rien à gauche ni à droite du rail ; la position des boutons dans tous les états.
**MUST NEVER** : un bouton en `signal` ; un pas calculé côté client ; un second chemin de sélection ou une seconde minuterie.

## 12. `RECESSED-WINDOW-V1` — la sous-zone de l'instrument (2026-10-25)

**Décision de l'opérateur** : parmi W1 · Inset, W2 · Slot et W3 · Rail recess (explorés sur F1 / F2 / F3 à 390 et 320), **W1** : le plus neutre, un contour fermé autour d'une information ; **les valeurs les plus grosses possibles**. W2 et W3 sont retirés du code.

| Champ | Valeur |
|---|---|
| **Rôle** | une sous-zone montée dans un InstrumentFrame (BodyMap, performance précédente, cible, récupération, substitutions, métadonnées de série, lectures secondaires) ; **jamais une carte** |
| **Baselines approuvées** | `window-390x220-f1`, `window-390x220-f2`, `window-390x220-f3-pair`, `window-390x220-f3-split`, `window-320x180-f1`, `window-320x180-f2`, `window-320x180-f3-pair`, `window-320x180-f3-split` |
| **Géométrie** (tout en `u`) | aplat `field` (plus sombre que la face `plate` du cadre) ; contour en `line` à 0,25u (Frame C : 0,35u en `ink3`) ; **une seule coupure** de 3u dans le bord haut, à 4u du bord droit ; une marque de registration d'1u × 1,6u en bas à gauche, en `ink3` ; marge intérieure 2u |
| **Disposition** | `windowLayout` : une fenêtre, deux égales, ou 60/40 ; écart de 2u (le châssis reste visible entre deux fenêtres : une machine, pas deux cartes) |
| **Valeurs** | le plus grand rôle existant qui tient (`readout` 68 → `figure` 40 → `exercise` 30, `windowContent.largestValueRole`) ; la capture de revue vérifie qu'aucune valeur n'est coupée |

**MUST PRESERVE** : plus calme que Frame C (trait plus fin, couleur plus sourde) ; lisible en monochrome ; contenu toujours dans le champ de la fenêtre ; fenêtres jamais superposées, toujours dans le champ de Frame C.
**MUST NEVER** : arrondi, ombre, dégradé, lueur, texture ; une couleur sémantique (une fenêtre ne porte aucun état) ; modifier Frame C pour loger une fenêtre ; une taille de texte hors des rôles existants.
