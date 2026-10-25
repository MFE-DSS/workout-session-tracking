# Sb_DA_02_2_CALIBRATION_PRIMITIVES — ReferenceMarker, ActiveCursor, CalibrationRail

**Statut** : build — rendu validé par l'opérateur (« c'est très bien, déjà beaucoup mieux »,
2026-10-25) · **Branche** : `sb/da-02-2-calibration-primitives` · **Base** : canonique `d87690e`
**Autorité de design** : `docs/strategy/AUREN_CALIBRATION_SYSTEM.md` (🔒 LOCKED v1) · contrat de
données `VNEXT §8.11` · primitive `AUREN_INSTRUMENTS §5.5`.
**Commande** : spec de mise en œuvre de l'opérateur du 2026-10-25 (sections 1 à 13) + deux SVG de
référence (`finallockedcursor.svg`, `finlactivecursor.svg`) ; puis trois revues de rendu.

---

## 1. Brainstorming · Options · Risques · Choix retenu (`CLAUDE.md §3`)

### 1.1 Lecture des tracés — ce qu'ils disent, ce qu'ils ne disent pas

| Mesure sur le tracé (unité = la paroi) | ReferenceMarker | ActiveCursor |
|---|---|---|
| fente / paroi | 67,3 / 91,6 ≈ **0,73** | 30,7 / 31,0 ≈ **1,0** |
| silhouette | ≈ 4,2 × 3,1 parois, semelle large | 3,0 × 10,6 parois |
| encoche basse | rectangulaire | en **courbe** (artefact de tracé) |

Les deux tracés **ne partagent ni la fente ni la paroi**. La commande exige les deux identiques : on
ne copie rien, on reconstruit sur une grille `u` commune.

### 1.2 Options

| Question | Options | Choix | Pourquoi |
|---|---|---|---|
| Forme des marqueurs | A — polygones normalisés en code · B — SVG redessinés chargés comme assets | **A** | les invariants sont **vérifiables par test** ; un asset ne l'est qu'à l'œil |
| Ce que vaut `u` | une unité abstraite · **la largeur d'un index du rail** | **index** (revue 1) | la fente fait un index : l'index qu'elle encadre la remplit exactement |
| Où sont les index | grille fixe en px · **les pas sélectionnables fournis par le domaine** | **les pas** (revue 1) | le curseur tombe toujours sur un index, jamais entre deux ; une grille fixe sert de repli sans pas |
| Où tombe le repère | dessus · **dessous** | **dessous** | la fente du curseur encadre la bande des index au-dessus de la ligne ; le repère, dessous, reçoit l'index bleu du moteur. Revue 2 : principe confirmé |
| Rail | image étirée · **mise en page calculée depuis la largeur** | **calculée** | §8 de la commande : nombre et espacement recalculés, marqueurs jamais déformés |
| Mouvement | Reanimated (dépendance neuve) · **`Animated` + `useReducedMotion` existants** | **existants** | §11 de la commande |
| Banc de rendu | intégrer le rail à l'exécution · **banc d'acceptation isolé** | **banc** | aucun service ne produit la calibration (`VNEXT §8.11`) : l'intégrer inventerait des seuils |

### 1.3 Risques

| Risque | Parade |
|---|---|
| Inventer des seuils pour remplir le rail | le composant ne reçoit que positions, pas et bornes ; le banc écrit « valeurs de démonstration » ; aucun écran produit ne monte le rail |
| `alert` lu comme « interdit » | HIGH COST = hachure + nom de zone ; la description vocale dit « coût », jamais « danger » (gardé par test) |
| Couleur seule porteuse | chaque zone a sa signature d'index **et** de bande (gardé par test) |
| Tracés recopiés à l'exécution | conservés en `design/auren/source/calibration/reference/`, gouvernés `reference-only`, jamais importés |

---

## 2. Réalisation — état final

### 2.1 La géométrie (après revue 1)

| Invariant partagé | Valeur |
|---|---|
| unité `u` | **la largeur d'un index du rail** |
| fente de visée | `1u` |
| paroi | `2,5u` |
| largeur hors tout | `6u`, **identique** |
| encoche basse | `1u × 0,6u`, centrée |
| axe · angles | `x = 0` · droits |

| Objet | Silhouette | Fente |
|---|---|---|
| `ActiveCursor` | `6u × 10u`, massif, corps plein sous la fente | `4u`, exactement la bande des index |
| `ReferenceMarker` | `6u × 4u`, bas et plat | `2u`, reçoit l'index bleu |

### 2.2 Le rail (après revues 1 à 3)

| Couche | Ce qu'elle montre |
|---|---|
| ligne de base | 2 px, `ink2` ; chaque plage la recouvre de sa couleur |
| index | un par pas, **exactement `u` de large** ; majeurs un sur deux à partir de la prescription ; signature par zone : EASY courts · TARGET normaux · PUSH affirmés · HIGH COST inclinés + hachure intermédiaire |
| bande de zone | sous la ligne, `2,2u` : EASY points · TARGET aplat · PUSH tirets serrés · HIGH COST hachure à 45° ; la zone du curseur pleine, les autres à 50 % |
| bornes | un trait vertical à chaque frontière de plage |
| index de prescription | `system`, de la ligne jusqu'au fond de la fente du repère |
| segment d'écart | prescription → curseur, `signal` à 55 %, animé avec le curseur |
| échelle chiffrée | étendu seulement : la valeur sous chaque index majeur (texte de l'app, jamais dans un asset) |
| noms de zone | étendu seulement, centrés sous leur plage (TARGET garde son nom même étroit) |
| lecture | à gauche « PRESCRIT » + valeur en `system` ; à droite écart · zone, puis la valeur choisie en grand chiffre |
| densités | compact `u = 2` (ligne + index majeurs + marqueurs) · régulier `u = 3` · étendu `u = 4` |

### 2.3 Interaction

Glisser le curseur ou toucher le rail : le rail rend la **position du pas le plus proche**
(`onSelectPosition`), l'appelant décide de ce qu'elle vaut. Boutons ± 2,5 dans le banc. VoiceOver :
rôle `adjustable`, actions incrément / décrément. Mouvement : 240 ms ; aucun mouvement pendant un
glissé (le doigt est déjà le mouvement) ni en mouvement réduit.

### 2.4 Fichiers

| Fichier | Rôle |
|---|---|
| `clients/mobile/src/ui/calibration/geometry.ts` | la grille commune |
| `ReferenceMarker.tsx` · `ActiveCursor.tsx` | `{size = u, color = token, testID}` ; `system` / `signal` par défaut |
| `layout.ts` | mise en page pure depuis la largeur ; zones, pas, index, bande, bornes, échelle ; mots (`describeRail`, delta) |
| `CalibrationRail.tsx` | le rendu, le glissé, la lecture, l'accessibilité |
| `CalibrationGallery.tsx` + `index.ts` | banc d'acceptation, monté seulement par `EXPO_PUBLIC_GALLERY=calibration` |
| `calibration.test.ts` | 33 tests |
| `design/auren/source/calibration/` | les deux tracés à l'octet près + README ; provenance `reference-only` ; garde de gouvernance étendue |

---

## 3. Revues de rendu (`CLAUDE.md §5.1`)

| Revue | Demande de l'opérateur | Fait |
|---|---|---|
| 1 | curseur plus large et plus massif ; tomber pile sur l'intervalle ; index = largeur du creux ; repère resserré à la largeur du curseur ; glisser au doigt | paroi 2,5u, `u` = un index, pas sélectionnables, largeur commune 6u, glissé aimanté |
| 2 | « on bouge avec l'un, on transforme dans l'autre » → puis « c'est très bien comme ça » | principe repère fixe + curseur mobile conservé |
| 3 | rail « faiblement dans ce qu'on veut » : le revaloriser au maximum | échelle de densité relevée, ligne affirmée, bande de zone à motifs, bornes, échelle chiffrée, lecture hiérarchisée |
| verdict | « c'est très bien, déjà beaucoup mieux » ; le curseur « exacerbé », aspect « vitesse, vaisseau, voiture » apprécié | — |

## 4. Vérifications

| Porte | Résultat |
|---|---|
| `check_scope` | **ISOLATED** |
| Client | `tsc` propre · **140 tests jest** dont 33 du Calibration System |
| Gouvernance des assets | `test_auren_asset_governance` + `test_auren_bodymap_master` : 48 verts |
| ruff · budget | propres |

## 5. Relecture des décisions (`CLAUDE.md §5.2`)

| Décision | Verdict |
|---|---|
| `AUREN_CALIBRATION_SYSTEM §1` structure | respectée — la bande et les bornes sont la « structure des ranges » du §10 |
| §2 quatre zones, TARGET une plage | respectée |
| §3 couleurs ; jamais la couleur seule | respectée — signature d'index **et** de bande |
| §4 repère posé par l'instrument, fixe | respectée |
| §5 curseur : seul porteur du `signal` plein | respectée — segment d'écart à 55 % |
| §6 le segment matérialise l'écart | respectée |
| §7 trois densités, jamais étiré | respectée |
| §8 une transition de 200 à 280 ms | respectée (240 ms) |
| §9 accessibilité | respectée — description vocale, rôle ajustable, tracés masqués |
| §10–11 aucune couleur, texte, valeur, lueur, dégradé, relief dans les assets | respectée — géométrie en code, échelle en texte d'app, aplats seulement |
| §12 gate | 1, 2, 4, 5 gardées par test ; 3, 6, 7, 8 jugées par l'opérateur sur le rendu |
| `VNEXT §8.11` le client interpole, ne décide pas | respectée — aucun écran produit ne monte le rail |
| `AUREN_VISUAL_BACKBONE §8.2` aucune couleur neuve | respectée |

## 6. Écarts à la commande, nommés

| Point de la commande | Écart | Motif |
|---|---|---|
| §3 proportions (`5u × 3u`, `3u × 6u`, paroi `1u`, encoche `0,7u`) | `6u × 4u`, `6u × 10u`, paroi `2,5u`, encoche `1u × 0,6u` | revue 1 de l'opérateur ; les invariants (fente, paroi, axe communs) sont tenus |
| §4 `size` | `size` = l'unité `u` en px | les deux objets et le rail partagent la même unité |
| §6 interface | + `steps`, `stepValues`, `referenceValue`, `width`, `onSelectPosition`, `onIncrement`, `onDecrement`, `testID` | pas sélectionnables, glissé, accessibilité, tests |
| §7 EASY « sparse ticks » | EASY = index **courts** + bande à **points** | chaque pas est désormais un index : on ne peut plus en sauter |
| §6 bornes | `lowBoundary` = début d'EASY ; en dessous, aucune zone | interprétation, documentée dans le type |
| §12 asset `calibration-rail-master.svg` | non reçu | le rail est construit depuis la spec ; s'il arrive, il fait foi |

## 7. Ce qui n'est pas fait — volontairement

- **Aucun écran produit ne monte le rail** : aucun service ne produit encore position, pas ni bornes
  (`VNEXT §8.11`, couche E7 du moteur).
- **Mode monochrome de l'application** : noté par l'opérateur (« l'app sera majoritairement
  monochrome »), sujet distinct.

**Verdict :** `DA-02.1` et `DA-02.2` sont livrés en code : repère, curseur et rail sur une seule
grille, invariants gardés par 33 tests, rendu validé par l'opérateur. Le rail attend sa donnée (couche
E7) pour entrer dans un écran. Prochaine étape de la roadmap DA : `DA-02.3 — Instrument Frame`.
