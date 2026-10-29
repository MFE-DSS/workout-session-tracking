# `AUREN_CANONICAL_MANNEQUIN_V1_SPEC` — intake et spécification de production

**Statut** : actif · **Décision opérateur** : 2026-10-29 (`DA-05.0`)
**Registre** : `design/auren/source/mannequin/auren_mannequin_v1_source.yaml` · garde `tests/test_auren_mannequin_v1.py`
**Documents liés** : `AUREN_VISUAL_BACKBONE.md §8` (DA, roadmap) · `AUREN_VISUAL_CONTRACT.md` (§20–21, BodyMap) ·
`design/auren/source/bodymap/auren_bodymap_mapping.yaml` (les 11 zones)

> L'opérateur : « Treat the approved 5-view pack as the canonical visual source. » · « Do not redesign the
> mannequin. Do not introduce new stylistic language. »

---

## 0. Ce que le pack est, et ce qu'il n'est pas

| | |
|---|---|
| **Le pack de cinq vues** | la **référence visuelle canonique** du seul humain articulable d'AUREN. Approuvé, figé, **jamais redessiné**. |
| **Sa provenance** | généré par IA (Midjourney, opérateur, 2026-10-29). `AUREN_VISUAL_BACKBONE §8.2` est fermé : **« jamais d'IA comme source finale (IA = moodboard) »**. Le pack est donc la référence, **pas** la source finale. |
| **L'asset de production** | la **reconstruction vectorielle** des cinq vues (§5), faite sur la référence. C'est elle qui entre un jour dans l'app ; `§8.2` le dit aussi : « un **mannequin vectoriel commun** articulé ». |
| **Ce qui n'entre pas dans le dépôt** | les rasters : aucun raster n'est permis sous `design/auren/`, et le dépôt est public. Ils sont identifiés par sha256 dans le registre. |

Statuts : `canonical-visual-reference-accepted` · `vector-reconstruction-required` · `runtime_authorization: blocked` ·
`legal_review: waived-by-operator` — droits d'usage **déclarés complets par l'opérateur**, qui a généré les vues
lui-même (2026-10-29) · `professional_anatomical_review: not-claimed`.

---

## 1. Spécification de l'asset

### 1.1 Rôle

Un **mannequin d'exécution neutre**, unique, articulable, qui montre **le geste** d'un exercice et **où** il se
passe sur le corps. Il est l'amont de toute illustration d'exercice d'AUREN : une seule silhouette, réutilisée
partout, jamais un nouveau personnage par écran.

### 1.2 Usages permis

- illustrer un exercice : postures de **début** et de **fin**, au **même cadrage** (`§8.2`) ;
- porter le **matériel** (banc, barre, Smith, poulies) sans le traverser ;
- **localiser** une région du corps, avec la même grammaire que le BodyMap : zone mise en avant en `system`,
  contexte en ossature silencieuse (`AUREN_VISUAL_CONTRACT §20`) ;
- planches éducatives et fiches d'exercice, une fois la reconstruction vectorielle validée.

### 1.3 Usages interdits

- toute **revendication d'effet** : activation musculaire, recrutement, pourcentage, EMG, intensité,
  récupération, blessure (`AUREN_VISUAL_BACKBONE §5`) ;
- un **visage identifiable**, une ressemblance avec une personne réelle, une expression ;
- un détail **génital** ou sexualisé ; la région pelvienne reste un volume neutre ;
- une **seconde anatomie** concurrente du master BodyMap pour la localisation fine : le mannequin montre le
  geste, le master reste l'autorité des 11 zones ;
- un rendu **photoréaliste** cuit (ombres, reflets, textures de peau, sueur) ; une couleur hors des tokens ;
- l'usage d'un raster du pack **comme** illustration de production.

### 1.4 Invariants visuels (observés sur les cinq vues, à préserver)

| Invariant | Valeur |
|---|---|
| Morphologie | homme athlétique, sec, musculature lisible, **non** culturiste |
| Posture | **A-pose neutre** : bras écartés du tronc, paumes vers les cuisses, jambes droites, pieds parallèles et à plat, poids réparti |
| Surface | volume **monochrome** sombre, sans vêtement, sans accessoire, sans cheveux |
| Teinte du corps | médiane mesurée `#1A1E24` — à normaliser sur un **token** (§3) ; elle est déjà au voisinage de `plate` (`#191C22`) et de la silhouette du BodyMap (`ink3` à 0,16 sur `field` = `#1F2124`) |
| Tête | crâne lisse, traits à peine indiqués ; à **neutraliser** encore à la reconstruction (§4) |
| Échelle | la **même** dans les cinq vues (§3) |

### 1.5 Usages en aval attendus

1. `DA-05.0` (suite) : reconstruction vectorielle des cinq vues, puis **articulation** (pivots, §5.4).
2. `DA-05.1` : **preuve Smith incliné**, début et fin, mannequin + matériel au même cadrage.
3. Gate `DA-01` final : « BodyMap et exercice **de la même machine** ».
4. Puis : familles d'exercices → les 7 Push A → bibliothèque de matériel → autres planches → les 58 mouvements.
5. Communication de **région du corps** : les masses du mannequin portent les **11 codes de zone** du BodyMap
   (§5.3), pour qu'une zone mise en avant sur une carte de séance et sur une illustration d'exercice soit la même.

---

## 2. Convention de nommage

```
auren_mannequin_v<MAJEUR>_<vue>.<ext>
```

| Vue | Nom canonique | Fichier opérateur d'origine | Orientation |
|---|---|---|---|
| face | `auren_mannequin_v1_front.png` | `mannequin_front_v1.png` | vers l'observateur |
| profil | `auren_mannequin_v1_profile.png` | `mannequin_profile_v1.png` | regarde vers la **gauche** de l'image |
| ¾ face | `auren_mannequin_v1_three_quarter_front.png` | `mannequin_3q_front_v1.png` | tourné vers la **droite** de l'image |
| ¾ dos | `auren_mannequin_v1_three_quarter_back.png` | `mannequin_3q_back_v1.png` | de dos, tourné vers la **droite** de l'image |
| dos | `auren_mannequin_v1_back.png` | `mannequin_back_v1.png` | de dos |

- Identifiant d'asset : `auren.mannequin.canonical.v1` ; une vue : `auren.mannequin.canonical.v1.<vue>`.
- La reconstruction vectorielle garde **les mêmes noms**, en `.svg`.
- Une vue en miroir n'est **pas** une vue nouvelle : elle se dérive à l'exécution (`profile` → profil droit),
  jamais un fichier de plus.
- **Dos retenu** : `mannequin_back_v1.png` (identique au pixel à l'image jointe par l'opérateur) ; le candidat
  voisin `mannequin-dos-2.png` n'est **pas** retenu.

---

## 3. Règles de cadrage

Mesurées sur le pack (registre, `measured_framing`), elles deviennent la norme :

| Règle | Valeur |
|---|---|
| **Toile** | carrée **1 : 1**, 1024 × 1024 px pour la référence ; la reconstruction vectorielle garde un viewBox carré |
| **Hauteur du corps** | **91,8 %** de la toile (938–942 px sur 1024) — identique dans les cinq vues, tolérance ± 0,5 % |
| **Haut du crâne** | y = 38–40 px (3,8 %) |
| **Ligne du sol** | y = 978–980 px (95,6 %) : **la même pour les cinq vues** ; les pieds posent dessus |
| **Centrage optique** | l'axe du corps (milieu du bassin, entre les pieds) sur x = 512 ; mesuré : boîte du corps décalée de −20 à +10 px selon la vue — **à normaliser à 0** sur l'axe du bassin, pas sur la boîte (un bras écarté ne déplace pas l'axe) |
| **Fond** | **uni et neutre**, une seule valeur pour les cinq vues ; mesuré : cinq blancs légèrement différents (`#F0F2F6` à `#F2F5F8`) — à normaliser. En production, le fond est **celui de l'écran** (`field`) : la reconstruction vectorielle n'a **pas de fond** |
| **Lumière** | aucune lumière cuite dans la reconstruction ; le volume se lit par les filets (§5.2) |

---

## 4. Règles de simplification anatomique

1. **Seules les grandes masses superficielles** sont gardées, chacune comme **une** forme :
   deltoïdes · pectoraux · trapèze · grand dorsal · fessiers (grand fessier) · quadriceps · mollets ;
   et, parce que les 11 zones du BodyMap les nomment : biceps, triceps, sangle abdominale, ischio-jambiers.
2. **Aucun muscle inventé** : pas de structure absente de la référence, pas de faisceau détaillé.
3. **Aucune striation de culturiste** : la référence montre des abdominaux très découpés ; la reconstruction les
   réduit au **contour du grand droit** (une forme, au plus une ligne médiane) — pas de « tablette ».
   Même règle pour les dentelés, les veines, les fibres.
4. **Visage** : neutralisé — volume du crâne, aucune expression, aucun trait identifiable (yeux, bouche, nez
   ramenés à rien ou au strict profil).
5. **Mains et pieds** : silhouettes simplifiées, doigts groupés ; orteils non détaillés.
6. **Bassin** : volume neutre continu, sans détail génital.
7. **Symétrie** : face et dos symétriques gauche / droite ; les ¾ et le profil suivent la référence.

---

## 5. Guide de reconstruction vectorielle

### 5.1 À reconstruire **fidèlement**

- la **silhouette extérieure** de chaque vue (contour du corps), à l'échelle du §3 ;
- les **proportions** : hauteur, longueur des segments, largeur d'épaules et de bassin, position de
  l'entrejambe (mesurée à 49,8 % de la hauteur depuis les pieds sur la vue de face) ;
- la **posture** A-pose : angle des bras, appui, orientation de chaque vue (§2) ;
- les **frontières des grandes masses** du §4.1, là où la référence les montre.

### 5.2 À **simplifier**

- le modelé : remplacé par des **aplats** et des **filets** (la grammaire du BodyMap : silhouette calme,
  masses en ossature fine) — aucune ombre, aucun dégradé ;
- les détails du §4.3–4.6.

### 5.3 À **normaliser**

- **échelle et centrage** : §3, au pixel près entre les cinq vues ;
- **couleur** : uniquement des **tokens** de `clients/mobile/src/ui/theme.ts` passés à l'exécution
  (`currentColor`), jamais une couleur inscrite dans la géométrie ;
- **structure du fichier** : un groupe par masse, **identifié par le code de zone du BodyMap**
  (`zone-pecs`, `zone-delt_lat`, `zone-delt_post`, `zone-lats`, `zone-upper_back`, `zone-biceps`,
  `zone-triceps`, `zone-quads`, `zone-posterior`, `zone-calves`, `zone-core`) — aucun code nouveau ;
  un groupe `body-<vue>-base` pour la silhouette ;
- **sous-ensemble SVG** : celui que `react-native-svg` rend tel quel (`svg`, `g`, `path` ; attributs `id`,
  `viewBox`, `fill`, `d`), comme le master BodyMap.

### 5.4 Préparer l'articulation

Les pivots sont posés **à la reconstruction**, sur la référence, et nommés une fois pour toutes :
`neck`, `shoulder_l/r`, `elbow_l/r`, `wrist_l/r`, `hip_l/r`, `knee_l/r`, `ankle_l/r`, et le **centre du bassin**
(origine du mannequin). Chaque segment est un groupe séparé qui tourne autour de son pivot ; les zones restent
attachées à leur segment.

---

## 6. Note de roadmap aval

- Ce mannequin est **en amont** de `DA-05.0` (reconstruction + articulation) et de `DA-05.1` (preuve Smith
  incliné) ; il sert ensuite l'**intégration du matériel**, les **vues d'exercice** (début / fin, même cadrage)
  et la **communication de région du corps** (les 11 zones, en `system`).
- Il ne remplace **pas** le master BodyMap : le BodyMap localise une zone sur un corps statique ; le mannequin
  montre un **geste**. La question du gate `DA-01` — « BodyMap et exercice de la même machine » — se juge sur la
  teinte, les filets, le traitement de zone et les codes de zone partagés.
- Prochaine étape commandable : **la reconstruction vectorielle de la vue de face**, rendue et soumise à
  l'opérateur avant les quatre autres.

---

## MUST PRESERVE / MUST NEVER

**MUST PRESERVE** : les cinq vues approuvées comme référence ; leur échelle, leur sol, leur centrage ; la posture
A neutre ; la morphologie athlétique non culturiste ; le monochrome sombre ; les 11 codes de zone.
**MUST NEVER** : redessiner ou régénérer le mannequin ; introduire un nouveau langage graphique ; utiliser un
raster du pack comme illustration de production ; un visage identifiable ; un détail génital ; une striation de
culturiste ; une revendication d'effet ; une couleur hors des tokens ; un raster sous `design/auren/`.
