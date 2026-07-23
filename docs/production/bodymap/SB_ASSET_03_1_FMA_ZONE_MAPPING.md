# SB_ASSET_03.1 — Mapping FMA → zones Auren

**Cycle** : `Sx_ASSET_03` (amendé SOURCE-REUSE-FIRST) · **Build** : `Sb_ASSET_03.1` · **Date** : 2026-07-23
**Source** : index officiels DBCLS, release **4.0**, téléchargés et hachés (cf. registre de provenance).

> **Aucun FMA ID n'est inventé.** Tous proviennent des index officiels réellement téléchargés.

---

## 1. Correction : le modèle d'identifiants n'est pas celui annoncé

La spec initiale supposait que `isa_parts_list_e.txt` fournissait le mapping des fichiers OBJ. **C'est faux**,
vérifié sur les données :

| Fichier officiel | Contenu | Type d'ID |
|---|---|---|
| `isa_parts_list_e.txt` | `concept id → representation id → nom` (2 905 lignes) | **`BP####`** |
| `isa_element_parts.txt` | `concept id → nom → element file id` (**29 549 lignes**) | **`FJ####`** |
| `partof_element_parts.txt` | équivalent hiérarchie PART-OF (17 943 lignes) | `FJ####` |
| Archives OBJ 4.0 | noms de fichiers | **`FJ####`** |

**Recouvrement `isa_parts_list_e.txt` ↔ noms d'OBJ : 0.** Le fichier opérant est **`isa_element_parts.txt`**,
absent de la liste de la spec, identifié via le listing officiel du répertoire `LATEST/`.

**Preuves de volumétrie** : archive IS-A **2 234 OBJ** · archive PART-OF **1 258 OBJ** · mapping IS-A
**29 549 lignes** · **2 905** concepts FMA · **2 234** element file ids distincts (= exactement le nombre
d'OBJ de l'archive IS-A).

**Aucune correspondance `BP → FJ` n'a été fabriquée** : elle n'existe pas dans les données, et le mapping
passe directement par le **concept FMA**.

## 2. Convention de latéralité
Suffixe **`M`** = côté **gauche** du sujet (miroir) ; sans suffixe = côté **droit**. Vérifié sur les entrées
nommées (`right pectoralis major` → `FJ1464`, `left pectoralis major` → `FJ1464M`).

Coordonnées BodyParts3D constatées : **X** gauche/droite (**+X = gauche du sujet**), **Y** vertical
(**−Y = tête**, **+Y = pieds**), **Z** profondeur (**−Z = antérieur**, **+Z = postérieur**).

## 3. Mapping retenu — 55 maillages

| Zone Auren | FMA ID | Nom officiel | Element files | Vue | Rôle |
|---|---|---|---|---|---|
| `pecs` | FMA34699 | abdominal part of pectoralis major | FJ1446 / FJ1446M | front | géométrie de zone |
| `pecs` | FMA34687 | clavicular part of pectoralis major | FJ1447 / FJ1447M | front | géométrie de zone |
| `pecs` | FMA34696 | sternocostal part of pectoralis major | FJ1464 / FJ1464M | front | géométrie de zone |
| `delt_lat` | FMA34678 | acromial part of deltoid | FJ1467 / FJ1467M | front + back | géométrie de zone |
| `delt_lat` | FMA34677 | clavicular part of deltoid | FJ1468 / FJ1468M | front + back | géométrie de zone |
| `delt_post` | FMA34679 | spinal part of deltoid | FJ1513 / FJ1513M | back | géométrie de zone |
| `upper_back` | FMA32555 | ascending part of trapezius | FJ1520 / FJ1520M | back | **functional-aggregate** |
| `upper_back` | FMA32557 | descending part of trapezius | FJ1521 / FJ1521M | back | **functional-aggregate** |
| `upper_back` | FMA32556 | transverse part of trapezius | FJ1554 / FJ1554M | back | **functional-aggregate** |
| `upper_back` | FMA13379 | rhomboid major | FJ1536 / FJ1536M | back | **functional-aggregate** |
| `upper_back` | FMA13380 | rhomboid minor | FJ1537 / FJ1537M | back | **functional-aggregate** |
| `biceps` | FMA37683 | long head of biceps brachii | FJ1478 / FJ1478M | front | géométrie de zone |
| `biceps` | FMA37682 | short head of biceps brachii | FJ1512 / FJ1512M | front | géométrie de zone |
| `triceps` | FMA37694 | lateral head of triceps brachii | FJ1477 / FJ1477M | back | géométrie de zone |
| `triceps` | FMA37692 | long head of triceps brachii | FJ1479 / FJ1479M | back | géométrie de zone |
| `triceps` | FMA37693 | medial head of triceps brachii | FJ1480 / FJ1480M | back | géométrie de zone |
| `quads` | FMA22430 | rectus femoris | FJ1433 / FJ1433M | front | géométrie de zone |
| `quads` | FMA22431 | vastus lateralis | FJ1442 / FJ1442M | front | géométrie de zone |
| `quads` | FMA22432 | vastus medialis | FJ1443 / FJ1443M | front | géométrie de zone |
| `posterior` | FMA45887 | long head of biceps femoris | FJ1395 / FJ1395M | back | **functional-aggregate** |
| `posterior` | FMA45893 | short head of biceps femoris | FJ1444 / FJ1444M | back | **functional-aggregate** |
| `posterior` | FMA22357 | semitendinosus | FJ1436 / FJ1436M | back | **functional-aggregate** |
| `posterior` | FMA22438 | semimembranosus | FJ1435 / FJ1435M | back | **functional-aggregate** |
| `posterior` | FMA22314 | gluteus maximus | FJ1418 / FJ1418M | back | **functional-aggregate** |
| `calves` | FMA45959 | lateral head of gastrocnemius | FJ1394 / FJ1394M | front + back | géométrie de zone |
| `calves` | FMA45956 | medial head of gastrocnemius | FJ1397 / FJ1397M | front + back | géométrie de zone |
| `calves` | FMA22542 | soleus | FJ1437 / FJ1437M | front + back | géométrie de zone |
| **base** | **FMA7163** | **skin** | **FJ2810** | front + back | **base silhouette** (`body-*-base`) |

**Total : 55 maillages** (54 musculaires + 1 surface cutanée), **0 manquant**.

## 4. Exclusions délibérées

| Élément | Décision | Motif |
|---|---|---|
| `vastus intermedius` (FJ1441 / FJ1441M) | **exclu** de `quads` | muscle **profond**, entièrement masqué par le droit fémoral en silhouette : l'inclure n'ajouterait rien de visible et suggérerait une profondeur non représentée |
| Toute structure profonde, organe, squelette | **exclus** | le rendu ne contient que des structures **superficielles** |
| `zone-unknown` | **inexistant** | `unknown` est un **état**, jamais une géométrie |

## 5. Zones sans référent dans BodyParts3D 4.0

```
LATISSIMUS DORSI IN BODYPARTS3D 4.0 PACKAGES INSPECTED: NOT FOUND
RECTUS ABDOMINIS IN BODYPARTS3D 4.0 PACKAGES INSPECTED: NOT FOUND
```

Recherche brute (`grep -ic`) sur **les trois index officiels téléchargés** (`isa_parts_list_e.txt`,
`isa_element_parts.txt`, `partof_element_parts.txt`) : **0 occurrence** de `latissimus`, **0 occurrence**
de `abdominis`.

**Portée du constat** : il concerne **uniquement** les archives officielles **4.0** téléchargées et les index
officiels inspectés, dont les hashes sont enregistrés. Il ne dit **rien** des autres releases ni de
l'historique du projet.

**Conséquence** : `lats` et `core` sont dérivées de **Servier Medical Art (CC BY 4.0)** — cf. registre de
provenance et procédure reproductible. Le contrat à **onze zones reste inchangé** ; aucune fusion de `lats`
dans `upper_back` n'a été faite.

## 6. Partitions graphiques déclarées

Aucune partition graphique d'un maillage unique n'a été opérée : chaque zone regroupe des **maillages FMA
entiers et distincts**. Les regroupements `upper_back` et `posterior` sont des **agrégats fonctionnels
Auren**, déclarés comme tels, et **ne prétendent pas** isoler un faisceau ou une insertion.

Pour `lats` et `core`, la géométrie est une **simplification Auren d'une planche Servier**, déclarée comme
telle — **pas** une structure FMA distincte.

## Verdict

**Verdict :** **FMA MAPPING COMPLETE — 11/11 zones représentées.** 55 maillages BodyParts3D 4.0 mappés par
**FMA ID officiel** via `isa_element_parts.txt` (le véritable index, la spec en désignait un autre — corrigé
sur pièces), **0 ID inventé**, **0 manquant**. Base silhouette = **FMA7163 `skin`**, confirmée dans l'index.
Deux zones (`lats`, `core`) sans référent dans les packages 4.0 inspectés sont dérivées de **Servier
Medical Art CC BY 4.0** et déclarées comme telles. Agrégats fonctionnels (`upper_back`, `posterior`) assumés ;
vaste intermédiaire délibérément exclu ; aucune structure profonde, aucun organe, aucun squelette ;
**aucun `zone-unknown`**.
