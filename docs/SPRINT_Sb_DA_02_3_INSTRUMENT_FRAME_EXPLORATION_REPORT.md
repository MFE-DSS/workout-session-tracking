# Sb_DA_02_3_INSTRUMENT_FRAME_EXPLORATION — quatre langages de conteneur

**Statut** : exploration — **choix de l'opérateur : C · Rail-mounted** (2026-10-25, « plus descriptif,
le plus simple ») ; mode « champ » du rail en revue (`CLAUDE.md §5.1`) ·
**Branche** : `sb/da-02-3-instrument-frame` (sur `sb/da-02-2-calibration-primitives`, PR #286)
**Commande** : brief opérateur `DA-02.3 — INSTRUMENT FRAME` du 2026-10-25 (deux versions, la seconde fait foi).
**Grille** : `u` = largeur d'un index du `CalibrationRail` (DA-02.2), sans autre système d'unités.

---

## 1. Brainstorming · Options · Risques · Choix retenu (`CLAUDE.md §3`)

| Question | Options | Choix | Pourquoi |
|---|---|---|---|
| Comment dessiner un cadre | image ou SVG figé étiré · **géométrie paramétrique en code** | **code** | le brief interdit l'étirement ; les invariants (`u`, rectilinéarité, marges) deviennent testables |
| Quel `u` pour une taille donnée | `u` fixe · **celui du rail à cette largeur** (`densityFor` → `UNIT`) | **celui du rail** | un rail monté dans le cadre et le cadre partagent alors exactement la même unité |
| Couleur | nouveaux tons de cadre · **trois rôles sur les tokens existants** : châssis `plate`, structure `ink3`, champ `field` | **tokens existants** | critère 10 : aucune couleur neuve |
| API | abstraction définitive · **composant mince `variant` + `children`** | **mince** | le brief : ne rien figer avant le choix de l'opérateur |
| Test « rendu sans plantage » | ajouter `react-test-renderer` · **appeler le composant (sans hook) et parcourir l'arbre** | **parcours** | « aucune dépendance ajoutée » ; le rendu réel est vérifié par le banc web (0 erreur de page) |

**Choix retenu** : quatre candidats paramétriques, une galerie isolée, aucun choix automatique.

| Risque | Parade |
|---|---|
| Le cadre concurrence le contenu | structure en `ink3` seulement, aucun aplat clair ; le contenu ne touche jamais la structure (≥ 2u, gardé par test) |
| Glisser vers la card SaaS | aucun arrondi (gardé par test), aucune ombre ; une seule idée structurelle par candidat |
| Toucher le Calibration System verrouillé | **aucune ligne de `clients/mobile/src/ui/calibration/` modifiée** dans cette tranche |

---

## 2. Les quatre candidats

Traits : principal `0,6u`, secondaire `0,35u` ; marge intérieure ≥ `2u`, mesurée depuis le **bord**
du trait, pas depuis son axe.

| | Idée structurelle | Construction en `u` |
|---|---|---|
| **A — Recessed** | un champ en retrait, quatre renforts d'angle, une rupture du contour | contour `0,6u` ; retrait `1,5u` (champ `field`) ; renforts en L `2,5u × 0,75u` ; rupture de `2u` sur le bord haut |
| **B — Indexed** | une encoche d'indexation = la fente des marqueurs ; un bord interrompu | encoche `1u` de large (= `SLOT`), `1,5u` de profondeur, posée à `6u` du bord (= une largeur de marqueur) ; rupture de `3u` sur le bord bas |
| **C — Rail-mounted** | le bord bas est un rail de montage, deux marques de registration | rail `1u` d'épaisseur (= un index) ; deux marques `1u × 1,6u` (= des index) ; le reste en trait secondaire |
| **D — Asymmetric faceplate** | une épine renforcée à gauche qui tourne dans l'angle ; une interruption à droite | épine `1u` sur toute la hauteur + retour `5u` en haut ; rupture de `4u` au milieu du bord droit ; champ de contenu > 80 % de la largeur |

## 3. Comparatif — observations, pas une décision

Lu sur le banc (390 px, écran à trois modules) et aux trois tailles.

| Critère du brief | A | B | C | D |
|---|---|---|---|---|
| 1. intentionnel en monochrome | oui | oui | oui | oui |
| 2. parenté avec le CalibrationRail | **faible** (aucun élément en `u` visible) | **forte** (l'encoche EST la fente) | **forte** (rail et marques EN index) | moyenne (épaisseur `1u`) |
| 3. pas une card SaaS | le plus proche d'une card (cadre fermé + coins) | oui | oui | oui |
| 4. accueille des instruments différents | oui | oui | oui ; le rail bas réserve `2,6u` en bas | oui, le plus grand champ |
| 5. ne concurrence pas l'objet actif | oui | oui | oui | l'épine est le trait le plus présent des quatre |
| 6. plusieurs instances sans bruit | calme | calme | empilés : une cadence de rails horizontaux | empilés : une colonne d'épines, rythme fort |
| à 180 × 120 | lisible | l'encoche fait 2 px : **à peine visible** | lisible | lisible |
| 7–10. paramétrique · `u` · aucun raster · aucune couleur neuve | oui | oui | oui | oui |

## 4. Observation hors périmètre — pour l'opérateur

Dans le rail monté (fixture B), l'étiquette d'échelle de la prescription (« 70 ») passe **sous l'index
bleu** de la référence, en densité étendue. C'est le Calibration System verrouillé : **non modifié ici**.
Correctif possible (ne pas imprimer l'échelle sous l'index de prescription, sa valeur étant déjà dans
« PRESCRIT ») : à décider par l'opérateur dans une tranche dédiée.

## 4bis. Revue opérateur — le choix, et le rail en champ

**Choix : C · Rail-mounted.** Les autres variantes restent dans le banc pour comparaison ; l'API sera
durcie sur C dans une tranche suivante.

**Le rail comme fond du cadre.** Demande : « le rail devrait reprendre complètement la case […] presque
en style background […] et on bouge le curseur dessus, comme si on réglait un métronome digital ».
Réalisé en **mode champ**, nouveau composant, **sans modifier le rail verrouillé** :

| Élément | Mode champ (`CalibrationField`, `fieldLayout.ts`) |
|---|---|
| index | une **barre pleine hauteur** par pas, `1u` de large, pendue depuis le haut |
| zone sans couleur | **longueur** de barre (EASY 50 % · PUSH 80 % · TARGET 100 %) + inclinaison HIGH COST ; bornes de plage en filets pleine hauteur |
| allocation | les barres de la prescription au choix sont **allumées**, les autres à 28 % |
| curseur | en haut, sa fente pince la barre choisie ; déplacement **par crans**, sans glissement (métronome numérique) |
| repère | en bas, sa fente pince la barre de prescription (`system`) |
| lecture | une ligne : prescrit à gauche, valeur (24 pt) · écart · zone à droite |
| **échelle** (revue 2 : « deux fois plus gros, plus cockpit, bien occuper la place ») | `u` du champ = **2 ×** `u` du rail (`FIELD_SCALE`) : barres, curseur et repère doublés |
| noms de zone | EASY · TARGET · PUSH · HIGH COST en 13 pt sous leurs plages, la zone active dans sa couleur ; **jamais superposés** (`packLabels` : une plage étroite emprunte la place de ses voisines) ; masqués sous 180 px de haut, les barres gardent la place |
| écran de séance (banc) | readout 130 px, **champ 340 px**, ± un cran, puis le rail en ligne et la BodyMap pour comparaison |

Le **rail en ligne verrouillé** (`CalibrationRail`, DA-02.2) n'est pas touché ; le champ est un second
rendu des mêmes primitives (`CalibrationField`, `fieldLayout.ts`).

## 5. Réalisation

| Fichier | Rôle |
|---|---|
| `clients/mobile/src/ui/instrument/frameGeometry.ts` | la géométrie pure des quatre candidats (segments, blocs, champ de contenu) |
| `InstrumentFrame.tsx` | `InstrumentFrame { width, height, variant, u?, children }` + `InstrumentFrameA…D` |
| `InstrumentFrameGallery.tsx` + `index.ts` | banc isolé, monté seulement par `EXPO_PUBLIC_GALLERY=frame` |
| `frameGeometry.test.ts` · `InstrumentFrame.test.ts` | 112 tests |
| `clients/mobile/src/ui/calibration/fieldLayout.ts` · `CalibrationField.tsx` | le rail en champ (fichiers neufs ; `layout.ts`, `CalibrationRail.tsx`, `geometry.ts` non modifiés) |
| `fieldLayout.test.ts` | 10 tests |

## 6. Vérifications

| Porte | Résultat |
|---|---|
| Client | `tsc` propre · **274 tests jest** dont 122 neufs (112 cadres, 10 champ) |
| Tests exigés par le brief | géométrie en `u` (épaisseurs, encoche = `SLOT`, rail = un index) · aucun arrondi · trois tailles · rendu sans plantage × 4 variantes × 3 tailles × 4 contenus · aucune couleur codée en dur (sources scannées) · aucun paquet importé hors de ceux du client |
| Banc web | 0 erreur de page |
| Calibration System | **aucune modification** des fichiers verrouillés (`git diff` vide sur `layout.ts`, `geometry.ts`, `CalibrationRail.tsx`, les marqueurs) ; le champ est ajouté à côté |

## 7. Relecture des décisions (`CLAUDE.md §5.2`)

| Décision | Verdict |
|---|---|
| `AUREN_VISUAL_BACKBONE §8.2` aucune couleur neuve · aucun décor gratuit | respectée |
| `§8.4` DA-02.3 après DA-02.2, gate DA-01 | respectée — le gate est le jugement de l'opérateur sur ce banc |
| `AUREN_CALIBRATION_SYSTEM` (verrouillé) | non concerné — non modifié |
| Brief : aucun écran produit, aucun choix automatique | respectée |

**Verdict :** quatre langages de conteneur paramétriques sur la grille `u`, tous conformes aux critères
mécaniques (7 à 10). **L'opérateur a choisi C · Rail-mounted**, et le rail y devient le fond du cadre
(mode champ, deux fois l'échelle du rail, réglage par crans). Prochaine tranche : durcir l'API sur C,
puis construire les autres instruments dans ce langage.
