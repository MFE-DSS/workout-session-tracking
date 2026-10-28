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
| `NUMERIC-READOUT-V1` | **LOCKED** (2026-10-25, « ACCEPT » DA-02.6) | une seule façon de poser un chiffre : rôle, unité, décimale, taille mesurée | DA-02.6 — `NumericReadout.tsx`, `readoutModel.ts` (§13) ; ses baselines sont celles des surfaces et des fenêtres qui l'utilisent |
| `SESSION-CARD-R1` | **LOCKED** (cible, banc seulement — 2026-10-26) | la carte de série verticale : l'exercice, ses fenêtres d'information, et **tout en bas** l'instrument de charge avec ses touches | DA-02.7 R1 — `SessionSetCard.tsx` (§17) ; jamais monté sur l'écran de séance tant que le moteur ne fournit pas les bornes de zone (E7) |
| `AUREN-MARK-V1` | **LOCKED** (2026-10-27, « ACCEPT » DA-03.2) | la marque du fabricant : le curseur de l'opérateur au-dessus du repère du système, un axe de visée, le vide entre eux | DA-03.2 — `design/auren/source/brand/mark/`, `AurenMark.tsx`, `markGeometry.ts` (§18) ; asset `provisional` tant que le nom n'est pas dégagé |
| `AUREN-APP-ICON-V1` | **LOCKED** (2026-10-27 ; révisée le 2026-10-28, DA-03.3b : « le défaut proposé en monochrome ») | l'icône de l'app : `AUREN-MARK-V1` à 54 %, en une seule encre `ink` sur `field` ; le verre et les apparences sont ceux du système | DA-03.3 — `clients/mobile/assets/AurenAppIcon.icon` (Icon Composer), gate `visual-contract/app-icon/` (§19) |
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
| **Baselines approuvées** | `surface-390x290-target`, `surface-390x290-push`, `surface-390x290-high-cost`, `surface-320x210-target`, `surface-320x210-push`, `surface-320x210-high-cost` |
| **Largeurs requises** | 390 × 290 (cadre u = 4, rail u = 6), 320 × 210 (cadre u = 3, rail u = 4,5) — depuis R2 (§15) |

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
| R1 | dans la séance, la surface **centrée au milieu de la carte**, en plus grand ; précisé le 2026-10-26 : le poids et les boutons **tout en bas** d'une carte verticale, l'exercice et ses pièces d'information au-dessus | nouvelle cible `SESSION-CARD-R1` (banc) ; l'intégration produit attend E7 | ✅ DA-02.7 R1, composition cible (§17) |
| R2 | le rail **un peu plus haut**, posé **plus bas**, pour mieux voir ses index | `INSTRUMENT-SURFACE-B1` / `-B2`, `INSTRUMENT-CONTROLS-B3` → nouvelles baselines ; `CALIBRATION-LINE-V1` inchangé (option ajoutée, défaut intact) | ✅ DA-02.7 R2, option B retenue (§15) |
| R3 | des boutons **+ / −** comme second moyen de régler, en plus du glissé | `INSTRUMENT-SURFACE` (élément ajouté) ; le rail porte déjà `onIncrement` / `onDecrement` | ✅ DA-02.4B.3, acceptée (§11) |
| R5 | les boutons − / + **plus « cockpit »**, dans la DA de l'instrument (opérateur, à l'acceptation de B.3) | `INSTRUMENT-CONTROLS-B3` (LOCKED) → nouvelle baseline | ✅ DA-02.7 R5, allure **Rail** retenue (§16) |
| R4 | la **surbrillance de la zone** traversée plus contrastée, pour savoir où l'on est | `CALIBRATION-LINE-V1` (LOCKED : opacité des zones inactives) → nouvelle baseline | ✅ DA-02.7 R4, variante V1 retenue (§14) |
| B.2 | divulgation progressive REST / ADJUSTING (déjà prévue) | `INSTRUMENT-SURFACE` + props `showScale` / `showZoneLabels` | ✅ DA-02.4B.2, acceptée (§10) |

## 10. `INSTRUMENT-SURFACE-B2` — divulgation progressive (2026-10-25)

**Décisions de l'opérateur** (croquis validé avant le code) :
- au repos, le chiffre prescrit **reste** ; seuls l'échelle chiffrée et les noms de zone se retirent ;
- le « 70 » est **fixe** : même place dans les deux états, aucun saut sous le doigt ;
- retour au repos **1,5 s après le dernier geste** ; chaque geste relance le délai.

| Champ | Valeur |
|---|---|
| **Baselines approuvées** | `surface-390x290-target-rest`, `surface-390x290-push-rest`, `surface-390x290-high-cost-rest` (repos) ; l'état réglage reste gardé par les six `surface-*` de B.1 |
| **320 × 210** | en densité regular, le rail n'a ni échelle ni noms : le repos y est **identique à l'octet** à B.1, aucune baseline de plus |
| **Code** | `CalibrationRail.tsx` : props `showScale`, `showZoneLabels` (défaut = rendu verrouillé) ; `HorizontalInstrumentSurface` : `presentation` (défaut `adjusting` = B.1) ; `disclosure.ts` : contrôleur pur, minuterie injectée |

**MUST PRESERVE** : tout `INSTRUMENT-SURFACE-B1` ; au repos, la ligne, la bande, le curseur, le repère et le chiffre prescrit ; aucune position ne change entre les deux états.
**MUST NEVER** : retirer la ligne ou la bande au repos ; faire bouger la valeur, le rail ou le chiffre prescrit quand l'échelle apparaît ; décrire l'état autrement à l'accessibilité (même libellé dans les deux états).

## 11. `INSTRUMENT-CONTROLS-B3` — commandes − / + (2026-10-25)

**Décisions de l'opérateur** : placement **P1, sous le cadre** ; boutons **beaucoup plus gros**, **rapprochés du centre**, **grisés** pour dire qu'on peut appuyer ; « − 2,5 » / « + 2,5 ». Accepté tel quel ; l'allure plus cockpit est venue ensuite (R5, §16).

| Champ | Valeur |
|---|---|
| **Baselines approuvées** (12 ; `adjusting` = juste après « + », un pas au-dessus) | `controls-390x290-target-rest`, `controls-390x290-push-rest`, `controls-390x290-high-cost-rest`, `controls-390x290-target-adjusting`, `controls-390x290-push-adjusting`, `controls-390x290-high-cost-adjusting`, `controls-320x210-target-rest`, `controls-320x210-push-rest`, `controls-320x210-high-cost-rest`, `controls-320x210-target-adjusting`, `controls-320x210-push-adjusting`, `controls-320x210-high-cost-adjusting` |
| **Géométrie** | sous le cadre, à 2u ; hauteur `ACTION_HEIGHT` (68) ; largeur 35 % du module chacun ; écart 4u ; paire centrée. 390 : 137 × 68 en x 62 / 215 ; 320 : 112 × 68 en x 54 / 178. **Ne dépend que de la largeur** |
| **Traitement** (depuis R5, §16) | chaque touche est un petit Frame C : face `plate`, trait `ink3` au poids secondaire de Frame C sur trois côtés, **rail de montage d'1u** en bas et **deux marques de registration d'1u × 1,6u** posées dessus, en `ink3` ; appui : la face descend en `field`, trait, rail et marques passent en `ink` ; glyphe `ink` (15,4 : 1 sur `plate`), pas affiché en `ink2` (9,1 : 1) ; inactif aux bornes : `ink3` (5,7 : 1), sans pas affiché. Aucun `signal` |
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
| **Valeurs** | le plus grand rôle existant qui tient, **mesuré** depuis DA-02.6 (`FittedReadout`, §13) ; la capture de revue vérifie qu'aucune valeur n'est coupée |

**MUST PRESERVE** : plus calme que Frame C (trait plus fin, couleur plus sourde) ; lisible en monochrome ; contenu toujours dans le champ de la fenêtre ; fenêtres jamais superposées, toujours dans le champ de Frame C.
**MUST NEVER** : arrondi, ombre, dégradé, lueur, texture ; une couleur sémantique (une fenêtre ne porte aucun état) ; modifier Frame C pour loger une fenêtre ; une taille de texte hors des rôles existants.

## 13. `NUMERIC-READOUT-V1` — la lecture chiffrée (2026-10-25)

**Décisions de l'opérateur** : l'unité **après** la valeur, en petit (actuel) ; la partie décimale **de la même taille** que l'entier (actuel). Gate DA-02.6 : **« ACCEPT »** sur la taille mesurée.

| Règle | Valeur |
|---|---|
| **Rôles** | `readout` 68 · `figure` 40 · `exercise` 30 (`NUMERAL_ROLES`), du plus grand au plus petit ; **jamais une taille nouvelle** |
| **Ligne** | boîte de ligne = 1,05 × la taille |
| **Unité** | après la valeur, précédée d'une espace, à 0,4 × la taille, graisse 700, `ink2` ; sa boîte de ligne = sa taille : **elle n'agrandit jamais la ligne** (leçon DA-02.4B.1) |
| **Décimale** | même taille que l'entier ; séparateur français (`formatValue`) |
| **Chiffres** | tabulaires ; agrandissement d'accessibilité plafonné (`NUMERAL_FONT_SCALE_CAP`) |
| **Taille dans un espace contraint** (`FittedReadout`) | la valeur est posée une fois dans chaque rôle, sans contrainte et invisible ; le plus grand rôle dont la largeur **mesurée** tient (et dont la ligne tient, étiquette comprise) l'emporte ; la valeur n'est montrée qu'une fois la mesure faite ; le gate attend la fin de la mesure |
| **Qui l'utilise** | la valeur souveraine de l'instrument (`HorizontalInstrumentSurface`, rendu identique au pixel) ; les valeurs des Recessed Windows (taille mesurée) |

**MUST PRESERVE** : une valeur n'est jamais coupée ; un même contenu dans des fenêtres voisines prend la même taille quand elle tient (mesure, pas estimation) ; aucune image à la mauvaise taille.
**MUST NEVER** : une taille de chiffre hors des trois rôles ; une unité plus grosse que 0,4 × la valeur ; une décimale réduite ou surélevée ; une estimation de largeur à la place de la mesure.

## 14. R4 — la zone traversée se détache (DA-02.7, 2026-10-26)

**Décision de l'opérateur** : « la surbrillance, je la trouve très légère […] l'idée, c'est vraiment qu'on voit très bien le rail, qu'on voit bien aussi les index […] on va dire que c'est OK » ; puis « tu prends le recommandé et boucle ». Variante retenue : **V1**.

| Règle | Avant (DA-02.2) | Après (R4 V1) |
|---|---|---|
| bande d'une zone **inactive** | opacité 0,5 | opacité **0,35** (`INACTIVE_ZONE_OPACITY.band`) |
| index et nom d'une zone **inactive** | opacité 0,45 | opacité **0,30** (`INACTIVE_ZONE_OPACITY.mark`) |
| zone **active** (celle du curseur) | opacité 1 | opacité 1 (inchangé) |

Aucune couleur neuve, aucun token modifié : seul l'écart entre la zone active et les autres grandit. La géométrie du rail, des marqueurs et de la bande est inchangée.

**Baselines ré-approuvées** (25) : les 4 de `CALIBRATION-LINE-V1`, les 9 de `INSTRUMENT-SURFACE-B1` / `-B2`, les 12 de `INSTRUMENT-CONTROLS-B3` — toutes portent le rail. `FRAME-C-V1` et `RECESSED-WINDOW-V1` ne bougent pas.

**Noté pour plus tard (opérateur)** : les **proportions** des zones EASY / TARGET / PUSH / HIGH COST dépendent de l'incrément de charge de chaque exercice ; elles viendront du moteur, pas du dessin. Les fixtures gardent les bornes de démonstration (55–85 kg, pas de 2,5, prescription 70).

## 15. R2 — un rail plus grand, posé plus bas (DA-02.7, 2026-10-26)

**Décision de l'opérateur** : « le rail plus grand qui descend, oui, là, tu peux partir sur le B u6 sans hésiter ». Option **B** retenue parmi A (u = 5, module 260) et B (u = 6, module 290).

| Règle | Avant (B.1) | Après (R2 B) |
|---|---|---|
| grille du rail dans la surface | celle de sa densité (4 à 390, 3 à 320) | **1,5 ×** celle-ci (`SURFACE_RAIL_SCALE`) : **6** à 390, **4,5** à 320 |
| grille de Frame C | 4 / 3 | 4 / 3 (inchangée) |
| écart valeur → rail | 3 unités du rail | **4** unités du rail |
| module | 390 × 220 · 320 × 180 | **390 × 290 · 320 × 210** |

Tout grandit avec la grille du rail — index, bande, curseur, repère — sans rien redessiner : les marqueurs gardent leurs proportions (6u × 10u, 6u × 4u). Le rail garde toute la largeur du champ.

**`CALIBRATION-LINE-V1` inchangé** : le rail reçoit une option `gridUnit` dont le défaut est la grille de sa densité ; ses 4 baselines restent identiques à l'octet. `FRAME-C-V1` et `RECESSED-WINDOW-V1` aussi.

**Baselines remplacées** (21) : les `surface-*` et `controls-*` passent de 390x220 / 320x180 à 390x290 / 320x210. À 320, la règle est la même (1,5 ×) ; la hauteur 210 laisse une respiration voisine de celle de 390 (≈ 17 px au-dessus et au-dessous, contre ≈ 15 px).

## 16. R5 — les touches − / + dans la grammaire de l'instrument (DA-02.7, 2026-10-26)

**Décision de l'opérateur** : « rail ou récède […] ou peut-être index […] ce que tu recommanderais, fais-le » ; « tout sauf le basique ». Allure **Rail** retenue parmi Rail · Recessed · Index (même place, même taille pour les trois).

**Pourquoi Rail** : c'est la seule des trois qui reprend la pièce la plus reconnaissable de l'instrument — le rail de montage et les registrations de Frame C. La touche se lit comme un module monté sur la même machine, pas comme un bouton d'interface. Recessed aurait confondu une commande avec une fenêtre de lecture ; Index ajoutait une fente sans fonction.

| Règle | Avant (B.3) | Après (R5 Rail) |
|---|---|---|
| face | `line` | `plate` (celle de Frame C) |
| bord | trait `ink3` sur 4 côtés | trait `ink3` sur 3 côtés + rail d'1u en bas |
| repères | — | 2 marques d'1u × 1,6u sur le rail, à 2u des bords |
| appui | face `plate`, trait `ink` | face `field` (la touche s'enfonce), trait, rail et marques en `ink` |
| contraste du glyphe | 12,1 : 1 | 15,4 : 1 |

Géométrie, comportement et accessibilité **inchangés** (§11). **Baselines ré-approuvées** : les 12 `controls-*`. Les 23 autres restent identiques à l'octet.

## 17. `SESSION-CARD-R1` — la carte de série verticale (DA-02.7, 2026-10-26)

**Décision de l'opérateur** : « la partie avec le poids et les boutons, c'est tout en bas de ce cadran rectangulaire vertical, car entre, on va mettre l'exercice, les infos de l'exercice, du cockpit sur comment bien le faire, d'autres pièces avec ce même design » ; « tu prends le recommandé et boucle ».

| Champ | Valeur |
|---|---|
| **Statut** | LOCKED comme **cible** ; banc seulement : l'écran de séance ne dessine pas le rail sans les bornes de zone du moteur (E7) |
| **Baselines approuvées** | `session-card-390x844-push-rest`, `session-card-390x844-push-adjusting` |
| **Lecture, de haut en bas** | en-tête (série, répétitions, exercice) · module 60/40 (BodyMap · « Dernière ») · module en paire (« Repos » · consigne d'exécution) · **instrument** (`INSTRUMENT-SURFACE-B1` / `-B2`, 390 × 290) · **touches** (`INSTRUMENT-CONTROLS-B3`) |
| **Géométrie** (`sessionCardLayout`) | barre d'état 48 · en-tête 72 · écart 8 entre modules · paire 120 · instrument 290 + touches · indicateur d'accueil 34 ; le premier module prend le reste (188 à 844) : **aucun vide non voulu** |
| **Largeur** | pleine largeur : avec des marges de 20 px, l'instrument tomberait à 350, sous la densité expanded (360) |
| **Pièces non dessinées** | la consigne d'exécution est un **emplacement nommé** en pointillé, comme le BodyMap : jamais un faux contenu |

**MUST PRESERVE** : l'instrument et ses touches **en bas**, sous le pouce ; les pièces d'information **au-dessus**, en Recessed Windows dans Frame C ; chaque pièce verrouillée telle quelle (aucune n'est redessinée pour la carte) ; une information une seule fois (la charge choisie n'est dite que par l'instrument ; « Dernière » est la performance précédente, pas la décision).
**MUST NEVER** : monter la carte sur l'écran de séance avec des bornes inventées ; une marge latérale qui fait passer l'instrument sous 360 ; un emplacement en pointillé présenté comme une fonction livrée.

## 18. `AUREN-MARK-V1` — la marque (DA-03.2, 2026-10-27)

**Décision de l'opérateur** : « ACCEPT — `MARK-D-HYBRID` becomes `AUREN-MARK-V1` » ; A2 retiré du chemin critique (historique d'exploration seulement) ; « do not redesign the geometry ».

**Ce qui la forme** — et pourquoi : la marque est faite des deux pièces que le produit a déjà approuvées, avec leur sens.
- en haut, le **curseur actif** (`ACTIVE-CURSOR-V1`) : ce que tient l'opérateur, sa décision ;
- en bas, le **repère de référence** (`REFERENCE-MARKER-V1`) : ce que pose le système, la prescription ;
- **un seul axe de visée** : les deux fentes alignées, la décision juste au-dessus de la prescription ;
- **le vide entre eux**, haut d'une fente. **Le rail n'est pas dessiné** : il est ce vide.

| Champ | Valeur |
|---|---|
| **Statut** | LOCKED (géométrie) · asset `provisional` (`AUREN_VISUAL_ASSET_MANIFEST` §5quater : clearance du nom ouverte) · monté sur **aucun** écran produit |
| **Sources** | `design/auren/source/brand/mark/mark-primary.svg` (grille 32), `mark-compact.svg` (grille 16), `mark-micro.svg` (grille 12) ; sans couleur (`currentColor`) |
| **Exécution** | `AurenMark` (`clients/mobile/src/ui/brand/AurenMark.tsx`) : l'appelant donne une taille et une encre, **jamais** le dessin ; `markDrawingFor` choisit |
| **Baselines approuvées** | `mark-v1-128-paper`, `mark-v1-128-inverse`, `mark-v1-12-micro`, `mark-v1-16-compact`, `mark-v1-32-primary`, `mark-v1-64-primary`, `mark-v1-frame-c-390x290`, `mark-v1-session-card-390x844`, `mark-v1-splash-390x844` |
| **Garde** | `tests/test_auren_mark_v1.py` (sources = géométrie d'exécution, aucune couleur, grille entière, règle de taille) ; `markGeometry.test.ts` (sélection, axe, écart, proportions) |

**Règle de taille optique** — trois tailles d'**une seule** marque, pas trois marques :

| Taille rendue | Dessin | Exact au pixel à |
|---|---|---|
| **20 px et plus** | `mark-primary` | 32 · 64 · 128 |
| **16 à 19 px** | `mark-compact` | 16 |
| **12 à 15 px** | `mark-micro` | 12 |
| **moins de 12 px** | **rien n'est rendu** | — |

Pourquoi trois dessins : une fente d'un pixel centrée tombe sur un demi-pixel. Le dessin de grille 32 forcé à 16 px perd ses fentes ; forcé à 12 px, ses deux pièces se soudent et l'écart disparaît (audit au pixel, DA-03.2). Chaque dessin est donc recalé sur sa propre grille ; à 16 px la marque fait 7 px de large et son axe se décale d'un demi-pixel (correction d'asymétrie permise).

**Géométrie verrouillée** (grille 32) : murs : fente = **2,5 : 1** (celui d'`ActiveCursor`) ; les deux pièces ont **la même largeur** et **le même axe** ; écart = **une fente** ; fentes à 6 / 14 et 3 / 7 de leur pièce (même proportion) ; **deux primitives**.

**Couleur** : monochrome. Toute encre est un token existant passé à l'exécution. Le traitement deux couleurs — curseur en `signal`, repère en `system` — n'est employé sur **aucune** surface de marque depuis le 2026-10-28 (DA-03.3b, l'opérateur : « je préfère la version contraste, sans la couleur orange-bleuâtre »). Dans l'instrument, `signal` et `system` gardent leur sens (`SEMANTIC-TOKENS-V1`) : là, ce n'est pas de la marque, c'est la lecture.

**MUST PRESERVE** : l'écart, les proportions des fentes, le rapport mur / fente, l'alignement, la silhouette, le nombre de primitives — **aucun ne change sans un nouvel arbitrage explicite de l'opérateur** ; la règle de taille ; la marque sans texte adjacent n'a pas de nom (rôle décoratif, le nom est dit par le texte).
**MUST NEVER** : rendre la marque sous 12 px ; laisser l'appelant choisir le dessin ; ajouter un rail, un cercle, un écusson, une lettre ; inscrire une couleur dans la géométrie ; remettre le traitement deux couleurs sur une surface de marque sans nouvel arbitrage ; un dégradé, une ombre, une lueur, un relief.

## 19. `AUREN-APP-ICON-V1` — l'icône de l'app (DA-03.3, 2026-10-27 ; révisée DA-03.3b, 2026-10-28)

**Décision de l'opérateur** :
- le 2026-10-27, « ACCEPT I2 — SEMANTIC » (curseur `signal` sur repère `system`) ; I3 retiré ;
- **révisée le 2026-10-28 (DA-03.3b)**, avant le partage du compte rendu final : « je préfère la version contraste, sans la couleur orange-bleuâtre », puis, devant la planche I1 / I2, « ouais parfait […] le défaut proposé en monochrome ».

**I1 remplace I2** : la même marque, à la même échelle et au même centrage, en une seule encre. I2 reste dans l'historique (PR #312), il n'est pas une icône concurrente.

**Composition** — la marque n'est jamais redessinée pour remplir le carré :

| Couche | Contenu | Token |
|---|---|---|
| 0 | le fond | `field` |
| 1 | la marque : curseur actif au-dessus du repère de référence, une seule couche | `ink` |

`AUREN-MARK-V1` `mark-primary`, **24 px par unité de grille sur 1024** (marque à **54 %** de la hauteur), jamais étirée, centrée horizontalement, **remontée de 16 px** (centre optique). Le large vide latéral est **voulu**. Aucun repère de registration, aucun rail, aucune géométrie décorative.

| Champ | Valeur |
|---|---|
| **Source** | `clients/mobile/assets/AurenAppIcon.icon` — document Icon Composer : `icon.json` (un groupe) + une couche SVG plate `mark.svg` (deux pièces en `ink`), opaque, sans effet |
| **Matière** | retenue : ombre neutre à 0,35, aucune translucidité ajoutée ; masque, Liquid Glass, ombres, reflets et apparences sont **rendus par le système**, jamais inscrits dans les SVG |
| **Intégration** | `app.json` → `ios.icon` ; Expo prebuild copie le document et règle `ASSETCATALOG_COMPILER_APPICON_NAME = AurenAppIcon` ; `actool` le compile (`CFBundleIconName = AurenAppIcon`, repli PNG pour les iOS antérieurs) |
| **Replis plats** (même composition, sans verre) | Android adaptatif (avant-plan, fond, monochrome : marque à 54 % de la zone **visible**), icône racine Expo, favicon Expo, pack PWA web |
| **Baselines approuvées** (rendues par `ictool`, identiques à l'octet aux rendus I1 de la planche DA-03.3 ; réapprouvées le 2026-10-28) | `app-icon-v1-default`, `app-icon-v1-dark`, `app-icon-v1-mono`, `app-icon-v1-clear-light`, `app-icon-v1-clear-dark`, `app-icon-v1-tinted-light`, `app-icon-v1-tinted-dark` (1024) ; `app-icon-v1-default-60pt`, `app-icon-v1-default-40pt`, `app-icon-v1-default-29pt` (@3x) |
| **Gate** | `python3 scripts/check_app_icon.py check` : le moteur d'Apple, tolérance **zéro pixel** (rendu déterministe), **macOS + Xcode seulement** — ailleurs il refuse au lieu de passer ; `tests/test_auren_app_icon_v1.py` (CI) vérifie le document, la configuration et les empreintes |

**Comportement monochrome** (autoritaire) : l'icône est en une encre dans toutes les apparences ; le curseur et le repère restent **deux pièces distinctes par la seule géométrie** — fentes alignées, écart central visible. Les apparences sombre, mono, clear et teintée sont recolorées par le système ; seule l'apparence par défaut porte le choix de l'opérateur au pixel.

**Limites de l'outil, dites** : avec `ictool` 1.2, Mono est identique à l'octet à Clear light ; Clear est rendu sur un fond neutre, sans fond d'écran.

**Web — le favicon** : dans un onglet de 16 px, l'icône entière réduite mettrait la marque sous 12 px (interdit). Le favicon porte donc **la marque à son dessin de 16 px** (`mark-compact`) sur `field`, en `ink` : la même marque, à sa taille optique.

**MUST PRESERVE** : la géométrie de `AUREN-MARK-V1` ; l'échelle 54 % et le décalage optique ; une seule encre ; les effets côté système.
**MUST NEVER** : remplir le vide latéral pour le remplir ; ajouter des repères, un rail, un cadre ; inscrire du verre, une ombre, un flou ou un reflet dans les couches ; remettre `signal` / `system` dans l'icône ou ses replis (garde `test_the_icon_carries_no_signal_or_system`) ; maintenir I2 comme icône concurrente.
