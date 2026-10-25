# `AUREN_CALIBRATION_SYSTEM` — spécification de design, **LOCKED v1**

**Statut** : 🔒 LOCKED v1 — verrouillé par l'opérateur le 2026-10-25 (`DA-02.1 — Calibration Rail`).
**Portée** : client mobile (`clients/mobile`) ; s'applique à toute surface qui montre une décision
de charge face à une prescription.
**Autorité** : ce texte est la décision opérateur. Il ne se modifie que par un nouvel arbitrage
opérateur consigné ici (v2), jamais en cours de tranche.
**Documents liés** :
- `AUREN_VISUAL_BACKBONE §8` : direction Allocator et roadmap DA ;
- `Sx_AUREN_MOBILE_EXPERIENCE_VNEXT_SPEC §8.11` : le contrat de données ;
- `AUREN_INSTRUMENTS §5.5` : la primitive dans l'ontologie du produit.

---

## 0. Rôle

Le Calibration System matérialise une décision centrale d'AUREN :

> **une prescription existe ; l'utilisateur peut s'en écarter ; l'interface lui montre
> immédiatement le coût relatif de cet écart.**

Ce n'est **ni** une barre de progression, **ni** une jauge de danger, **ni** un score
physiologique.

Trois primitives :

1. `CalibrationRail`
2. `ReferenceMarker`
3. `ActiveCursor`

Le moteur calcule la recommandation et les zones. **Le composant visuel ne déduit aucune vérité
biomécanique ou médicale.**

---

## 1. Calibration Rail — LOCKED

### 1.1 Structure

Le rail se compose **uniquement** de :

- une ligne de base horizontale ;
- des graduations mineures ;
- des graduations majeures ;
- des zones sémantiques ;
- un `ReferenceMarker` fixe ;
- un `ActiveCursor` mobile.

**Supprimés définitivement** : code-barres · texture décorative · vis · métal · faux relief ·
nombres intégrés à l'asset · flèches génériques · dégradés pré-rendus.

Le composant doit fonctionner **parfaitement en monochrome**.

### 1.2 Sémantique

La position sur le rail représente **l'écart normalisé entre la décision actuelle et la
prescription de référence calculée par AUREN.**

Le rail **ne représente pas directement des kilogrammes**. La valeur affichée peut être
`72.5 KG`, mais la position du curseur est déterminée par un **modèle normalisé envoyé par le
moteur** (`VNEXT §8.11`).

---

## 2. Les zones du rail — quatre, pas une de plus

| Zone | Sens | Jamais | Couleur (token) | Signature sans couleur |
|---|---|---|---|---|
| **EASY** | décision sensiblement moins coûteuse que la prescription — *easier than prescribed* | « mauvais », « sous-entraînement », « échec » | `perfBelow` `#B7A3F0` | graduations espacées, points courts |
| **TARGET** | l'enveloppe dans laquelle la prescription est respectée — **une plage, jamais un point** | — | `ink` `#F5F3EE` dominant ; son repère, le `ReferenceMarker`, en `system` `#7CCBF5` (information du moteur, pas action de l'utilisateur) | graduations régulières, la référence |
| **PUSH** | au-dessus de la prescription, dans une enveloppe raisonnable — *above prescription / increased demand* | « correct », « mieux », « réussite » | `perfAbove` `#6FD69A` | graduations plus affirmées |
| **HIGH COST** | écart important : coût attendu nettement supérieur à la prescription — *resource heavy* | « danger », « risque de blessure », « interdit » | `alert` `#FF8A7A` | hachure terminale ou graduations diagonales |

**L'utilisateur peut choisir HIGH COST volontairement. AUREN montre le prix ; il ne bloque pas la
décision.**

---

## 3. Couleurs

Principe fondamental : **la position du curseur et la zone sont deux informations différentes.**

| Objet | Token, toujours |
|---|---|
| `ActiveCursor` (décision de l'utilisateur) | `signal` `#FFB23E` |
| `ReferenceMarker` (prescription du moteur) | `system` `#7CCBF5` |
| EASY · TARGET · PUSH · HIGH COST | `#B7A3F0` · `#F5F3EE` · `#6FD69A` · `#FF8A7A` |

La couleur n'est **jamais** le seul moyen de distinguer les zones : chaque zone porte aussi une
variation de graduation, de densité ou de hachure.

> Note de cohérence (relecture `CLAUDE.md §5.2`). Les quatre valeurs sont déjà des tokens mesurés
> de `clients/mobile/src/ui/theme.ts` : `perfBelow` et `perfAbove` (R13, 7,73 : 1 et 9,56 : 1 sur
> `plate`), `ink`, `alert`. `perfBelow` et `perfAbove` gardent **le même sens** qu'au bilan
> (en dessous / au-dessus de la prescription). `alert` reçoit ici le sens « coût élevé », **pas
> « erreur »** : sa présence sur le rail ne doit jamais se lire comme un refus. Aucun nouveau
> token n'est nécessaire.

---

## 4. `ReferenceMarker`

**Fonction** : indiquer **la prescription calculée par AUREN.** Il ne bouge pas quand
l'utilisateur modifie la charge ; il ne change que si le moteur fournit une nouvelle prescription.

**Géométrie interdite** : flèche vers le haut · épingle de carte · triangle massif · chevron
standard · curseur de slider conventionnel.

**Direction recherchée** : un repère métrologique, un index de calibration :

- petit index supérieur ou inférieur ;
- axe vertical court ;
- interruption précise de la ligne de base ;
- éventuellement une encoche géométrique ;
- silhouette identifiable à 12–16 px.

```
      ▾                    ╱╲
──────┼──────        ─────┼──────
```

Le symbole doit paraître **posé par l'instrument**, pas manipulé par l'utilisateur.

**Couleur** : au repos, `system` `#7CCBF5` en présence faible. Quand il coïncide avec l'`ActiveCursor`,
il **reste visible par sa géométrie**, même sous l'ambre.

---

## 5. `ActiveCursor`

**Fonction** : représenter **la décision actuellement contrôlée par l'utilisateur** — l'objet en
vol. C'est la **seule** primitive du rail autorisée à porter pleinement `signal` `#FFB23E`.

**Géométrie** : plus matériel que le `ReferenceMarker`, mais extrêmement simple :

- petit bloc ou curseur étroit ;
- une entaille centrale alignée avec la graduation ;
- éventuellement une légère extension au-dessus du rail ;
- silhouette symétrique ou quasi symétrique ;
- aucune icône.

```
     ┌─┐                    │
─────┤│├─────         ─────▰───────
     └─┘
```

**Interdits** : pastille ronde iOS classique · poignée de SaaS · flèche.

---

## 6. La relation référence / curseur

La relation compte plus que les objets isolés. Le segment entre `ReferenceMarker` et
`ActiveCursor` **matérialise l'écart**.

```
Prescription respectée          Légère surcharge               High Cost

           ▾                              ▾                             ▾
───────────▰───────────        ───────────┼━━━━▰──────        ───────────┼━━━━━━━━━━━━▰
          70 KG                              72.5 KG                                   80
                                             +2.5                                 HIGH COST
                                             PUSH
```

Quand la prescription est respectée, le curseur masque partiellement le repère, qui reste
identifiable.

---

## 7. Responsive — trois densités

| Densité | Largeur | Contenu | Usage |
|---|---|---|---|
| **Compact** | 160–239 px | ligne de base · graduations majeures seulement · repère · curseur · aucune légende permanente | cartes secondaires, aperçus |
| **Regular** | 240–359 px | ligne de base · graduations majeures et mineures · coloration contextuelle · valeur · delta | console d'exercice |
| **Expanded** | 360 px et plus | tout Regular · libellés EASY / TARGET / PUSH / HIGH COST si utiles · contexte dernière séance / référence | — |

**Le dessin n'est jamais étiré comme une image** : le nombre et l'espacement des graduations
sont recalculés pour chaque largeur.

---

## 8. Mouvement

Un changement de charge provoque **une seule** transition de **200 à 280 ms** : le curseur se
déplace et le segment parcouru se révèle en même temps.

**Interdits** : pulsation permanente · boucle de balayage · lueur qui respire · toute animation
pendant une série.

Mouvement réduit (`prefers reduced motion`) : position finale immédiate, ou fondu discret.

---

## 9. Accessibilité

Les zones restent compréhensibles **sans couleur**. Au minimum : couleur **et** géométrie ou motif
**et**, quand c'est nécessaire, un libellé contextuel. La couleur ne peut jamais être le seul
vecteur de sens.

---

## 10. Assets à produire

| Fichier | Contenu | Couleur |
|---|---|---|
| `calibration-rail-master.svg` | ligne de base, graduations, structure des zones — **ni repère ni curseur intégrés** | — |
| `reference-marker.svg` | le repère | monochrome, token injecté à l'exécution |
| `active-cursor.svg` | le curseur | monochrome, token injecté à l'exécution |
| `range-hatch-high-cost.svg` *(optionnel)* | la hachure HIGH COST, seulement si elle est plus propre en motif SVG que générée en code | monochrome |

> Note d'intégration : les graduations étant **recalculées** à chaque largeur (§7), le rail du
> client se génère en code (`react-native-svg`) **à partir des proportions** du master. Le master
> fixe la grammaire (épaisseurs, rapport mineure / majeure, motifs de zone) ; il n'est jamais
> étiré.

---

## 11. Interdictions — dans les SVG, jamais

Couleur sémantique fixe · texte · valeurs · unités · lueur · raster · dégradé · animation · ombre ·
interprétation médicale.

---

## 12. Gate d'acceptation

Le système n'est validé que si **les huit** conditions tiennent :

1. le rail est reconnaissable en monochrome ;
2. `ReferenceMarker` et `ActiveCursor` se distinguent sans couleur ;
3. la cible du moteur et la décision de l'utilisateur se comprennent en quelques secondes ;
4. les quatre zones restent compréhensibles en niveaux de gris ;
5. le composant reste lisible à environ 180 px ;
6. aucune partie ne ressemble à un slider mobile générique ;
7. aucun élément ne suggère « rouge = interdit » ;
8. le système garde la sensation d'instrument AUREN.

Ce gate s'ajoute au rendu exposé à l'opérateur (`CLAUDE.md §5.1`) : il ne le remplace pas.

---

## 13. Ce qui n'est pas encore décidé — dépendances nommées

| Question | Propriétaire | Tant que ce n'est pas tranché |
|---|---|---|
| **Les bornes des zones** (où finit TARGET, où commence HIGH COST) et la **normalisation** de l'écart | le moteur scientifique — `Sx_AUREN_SCIENTIFIC_ENGINE_V2_SPEC`, couche **E7 Autorégulation** (livrable `LOAD_AUTOREGULATION_MODEL.md`) | **le rail n'est pas dessiné.** Ni le client ni la présentation n'inventent de seuil (§0 : le visuel ne déduit rien) |
| La variable de décision : **charge seule**, ou charge **et** répétitions | idem | contrat v1 sur la charge (`VNEXT §8.11`) ; les répétitions restent dans le readout |
| La géométrie finale de `ReferenceMarker` / `ActiveCursor` | `DA-02.2` (agent designer de l'opérateur) | les croquis du §4–5 sont la direction, pas l'asset |
