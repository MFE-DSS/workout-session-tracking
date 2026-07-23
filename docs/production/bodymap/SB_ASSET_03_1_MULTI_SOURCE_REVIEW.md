# Sb_ASSET_03.1 — Revue de cohérence multi-sources — 2026-07-23

```
MULTI-SOURCE ANATOMICAL CONSISTENCY REVIEW: COMPLETE
PROFESSIONAL ANATOMICAL REVIEW: NOT CLAIMED
```

> **Ce que cette revue est** : une vérification de **cohérence de représentation** entre sources concordantes.
> **Ce qu'elle n'est pas** : une validation médicale, une preuve clinique, une garantie d'exactitude
> anatomique. Aucun relecteur professionnel n'est intervenu et aucun n'est revendiqué.

## Sources de contrôle et lignage

| Source | Licence | Rôle | Indépendance |
|---|---|---|---|
| **OpenStax, *Anatomy and Physiology*, 1ʳᵉ éd.** | **CC BY 4.0** (pub. 2013-04-25) | contrôle A | indépendante de BodyParts3D et de Servier |
| **Sobotta, *Atlas and Text-book of Human Anatomy*, 1909** | **domaine public** | contrôle B | atlas historique distinct — indépendant d'OpenStax **et** de Servier |
| BodyParts3D 4.0 | CC BY 4.0 | **source de géométrie** (9 zones) | — ne compte pas comme son propre contrôle |
| Servier Medical Art | CC BY 4.0 | **source de géométrie** (`lats`, `core`) | — ne compte pas comme son propre contrôle |

**Exclusions appliquées** : OpenStax **2e** (CC BY-NC-SA) ; Wikimedia `Muscles front and back.svg` (dérivé
d'OpenStax → **pas** un second avis) ; Z-Anatomy (dérivé de BodyParts3D → **pas** un second avis) ; toute
ressource AnatomyTOOL sans licence individualisée. *(Les planches Sobotta 1909 sont parfois hébergées par
AnatomyTOOL ; l'indépendance porte sur l'**œuvre** — atlas de 1909 — pas sur l'hébergeur.)*

## Verdicts par zone

| Zone | Géométrie | Contrôle A (OpenStax 1ʳᵉ éd.) | Contrôle B (Sobotta 1909) | Verdict |
|---|---|---|---|---|
| `pecs` | BP3D — *pectoralis major* (parties claviculaire, sternocostale, abdominale) | thorax antérieur, du sternum/clavicule à l'humérus | fig. 245 *superficial muscles of the torso, anterior view* | **PASS** |
| `delt_lat` | BP3D — parties acromiale + claviculaire du deltoïde | épaule, coiffe du moignon, visible face et dos | fig. 236 / 245 | **PASS** |
| `delt_post` | BP3D — partie spinale du deltoïde | face postérieure de l'épaule | fig. 236 *superficial muscles of the back* | **PASS** |
| **`lats`** | **Servier** (adapté) | *« broad, triangular »*, **portion inférieure du dos**, origines T7-T12, côtes 9-12, crête iliaque, insertion humérale | fig. 236 / 238 *back muscles and fascia* | **PASS** |
| `upper_back` | BP3D — trapèze (3 parties) + rhomboïdes | trapèze occupe **le haut du dos, au-dessus du grand dorsal** | fig. 236 | **PASS** — agrégat fonctionnel assumé |
| `biceps` | BP3D — chefs long + court du biceps brachial | face antérieure du bras | fig. 245 | **PASS** |
| `triceps` | BP3D — chefs latéral, long, médial | face postérieure du bras | fig. 236 | **PASS** |
| `quads` | BP3D — droit fémoral, vastes latéral et médial | face antérieure de cuisse | fig. 245 | **PASS** |
| `posterior` | BP3D — ischio-jambiers + grand fessier | face postérieure de cuisse et fessiers | fig. 236 / 238 | **PASS** — agrégat fonctionnel assumé |
| `calves` | BP3D — gastrocnémiens (2 chefs) + soléaire | jambe postérieure, visible des deux vues | fig. 236 | **PASS** |
| **`core`** | **Servier** (adapté) | *rectus abdominis* = **portion médiale** de la paroi abdominale antérieure, pubis → sternum/côtes ; **obliques externes latéraux** ; **linea alba médiale** | fig. 245 · fig. 248/249 *cross section of the abdominal muscles* | **PASS — FUNCTIONAL AGGREGATE** |

**11 PASS · 0 ADJUST · 0 BLOCKED.**

## Vérifications des deux zones à géométrie Servier

### `lats`
Citation OpenStax 1ʳᵉ éd. : le grand dorsal est *« a broad, triangular »* muscle de la **portion inférieure
du dos**, avec origines *« the thoracic vertebrae (T7 through T12), the lower vertebrae, ribs 9 through 12,
and the iliac crest »* et insertion humérale par aponévrose ; le **trapèze occupe la région supérieure du dos,
au-dessus du grand dorsal**.

**Concordance avec la géométrie produite** : deux masses latérales larges sur le dos, sous `upper_back`
(trapèze), convergeant vers la ligne médiane basse (aponévrose thoraco-lombaire), s'étendant jusqu'au niveau
de la ceinture. **Limite supérieure** sous le trapèze ✓ · **limite inférieure** au niveau lombaire/iliaque ✓ ·
**position latérale** ✓ · **vue** dos ✓.

### `core`
Citation OpenStax 1ʳᵉ éd. : le droit de l'abdomen occupe la **portion médiale** de la paroi abdominale
antérieure, du pubis au sternum et aux côtes supérieures ; les **obliques externes sont latéraux** ; la
**linea alba** est médiane.

**Concordance** : bande centrale antérieure du bas du thorax au pubis, avec extension latérale limitée
correspondant aux obliques. **Position médiale** ✓ · **limites supérieure/inférieure** ✓ · **vue** face ✓.

**Qualification honnête** : la géométrie livrée est un **agrégat fonctionnel visuel** (droit de l'abdomen +
obliques), **pas** une extraction du *rectus abdominis* — lequel est **absent de BodyParts3D 4.0**. Les
**tendinous intersections** (« six-pack ») ne sont **pas** représentées : le BodyMap localise une région, il
ne détaille pas la structure.

## Écarts relevés et décisions

| Écart | Décision |
|---|---|
| `lats` déborde légèrement sur la région lombaire haute après fermeture morphologique | **Accepté** — l'aponévrose thoraco-lombaire fait partie de l'emprise fonctionnelle du grand dorsal ; aucune fusion avec `upper_back` |
| `core` inclut une part des obliques externes | **Accepté et déclaré** — agrégat fonctionnel assumé, conforme à la décision opérateur §9 |
| `upper_back` = trapèze + rhomboïdes en une seule masse | **Accepté** — `functional-aggregate` prévu au contrat ; aucune prétention à distinguer faisceaux ou insertions |
| `posterior` = ischio-jambiers + grand fessier en une masse | **Accepté** — idem |
| Vaste intermédiaire exclu de `quads` | **Accepté** — muscle profond, invisible en silhouette ; l'inclure n'aurait rien ajouté et aurait suggéré une profondeur non représentée |

## Limites explicites
- Aucune mesure de recouvrement pixel-à-pixel n'a été faite entre les sources : la comparaison porte sur la
  **position, l'adjacence, les limites et la vue**, pas sur une superposition métrique.
- Le sujet BodyParts3D est **un** homme adulte de référence ; les proportions ne sont pas populationnelles.
- L'éditeur BodyParts3D déclare lui-même que la donnée **peut contenir des erreurs** et que certaines parties
  sont **d'origine artistique ou déformées** — raison pour laquelle ce croisement est obligatoire, et raison
  pour laquelle il **ne suffit pas** à établir une exactitude anatomique.

## Sources consultées (2026-07-23)
- OpenStax A&P 1ʳᵉ éd. — muscles de la paroi abdominale : `openstax.org/books/anatomy-and-physiology/pages/11-4-axial-muscles-of-the-abdominal-wall-and-thorax`
- OpenStax A&P 1ʳᵉ éd. — ceinture scapulaire et membre supérieur : `openstax.org/books/anatomy-and-physiology/pages/11-5-muscles-of-the-pectoral-girdle-and-upper-limbs`
- Sobotta 1909, planches (domaine public) : `commons.wikimedia.org/wiki/Category:Sobotta's_Anatomy_plates`
