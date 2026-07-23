# Sprint Sb_ASSET_03.1-fix — Reproducibility Closure & Package Reissue — REPORT

**Statut** : 🟢 **COMPLETE — REPRODUCIBILITY GAP CLOSED**
**Type** : CORRECTIF DE PIPELINE — **DOCS-ONLY côté Git** (0 SVG/ZIP/PNG/OBJ/`.blend` committé)
**Date** : 2026-07-23 · **Baseline** : `34e059c` (= origin, vérifié)

---

## 1. Point de départ — l'échec est conservé

```
FIRST INTAKE:
BLOCKED — NON-REPRODUCIBLE OUTPUT

ROOT CAUSE:
INCOMPLETE EXECUTABLE BUILD GRAPH
```

Le verdict de `Sb_ASSET_03.2` est **accepté sans réserve**. Le package v1, l'espace `Sb_ASSET_03.1` et les
preuves d'intake sont **conservés intacts**. **L'histoire du premier échec n'est pas réécrite.**

## 2. Les six causes, et leur traitement

| # | Cause racine | Traitement |
|---|---|---|
| 1-3 | `servier_masks.py` consommait `servier_<zone>_raw.svg` sans producteur ; sélection ad hoc | **`extract_servier_regions.py`** + configuration à sélecteurs exacts |
| 4 | `BASE` absolu dans les scripts | **`pipeline_context.py`** + relocalisation des 8 scripts concernés |
| 5 | manifeste externe au ZIP | **manifeste embarqué**, règle de non-circularité vérifiée |
| 6 | décompte « 8 scripts » faux | **convention de comptage déclarée** : 14 fichiers `.py` |

## 3. Le maillon manquant, scripté et prouvé

**Sélecteurs exacts récupérés**, jamais reconstruits par heuristique : **117 IDs** pour `lats`, **157** pour
`core`, en ordre document, extraits des artefacts validés. La région de bounding box initiale est conservée
en configuration sous `historical_region_filter`, **marquée non utilisée**.

Gardes du script : SHA-256 du PPTX vérifié **avant** extraction · refus si formes converties ≠ **3 361** ·
refus sur sélecteur absent ou dupliqué · ordre stable · aucun choix interactif · refus d'écriture hors
workspace.

**Parité byte-identique, rejouée depuis le PPTX :**

| Sortie | SHA-256 | Verdict |
|---|---|---|
| `servier_slide3.svg` | `789fb3af…d459e188` | **identique** ✅ |
| `servier_lats_raw.svg` | `dc04a017…114bca1b` | **identique** ✅ |
| `servier_core_raw.svg` | `fe01dc94…4950e96b` | **identique** ✅ |

## 4. Pipeline relocalisable

`pipeline_context.py` centralise racines, garde d'appartenance au workspace, création bornée de dossiers,
résolution d'exécutables (`shutil.which` + surcharges explicites) et codes d'erreur — évitant dix
relocalisations divergentes.

**Audit statique final : 14/14 scripts propres** — `0` `/Users/` · `0` nom de compte · `0` `BASE` absolu ·
`0` `shell=True` · `0` réseau · `0` `eval`/`exec` · `0` `__import__` dynamique · `0` suppression récursive ·
`0` secret · `0` chemin Homebrew ou `/Applications` obligatoire.

Exception consignée : `__import__("mathutils")` — **argument littéral**, équivalent d'un import statique,
module fourni par Blender.

## 5. Graphe de build explicite

```
BUILD GRAPH:
COMPLETE / NO ORPHAN INPUTS
```

`pipeline_graph.json` déclare pour chaque étape script, entrées, sorties, configuration, outils et
dépendances. Le contrôleur prouve : aucune entrée orpheline, aucune sortie à deux producteurs, aucun cycle,
aucune étape orpheline. **`servier_lats_raw.svg` et `servier_core_raw.svg` ont désormais un producteur
déclaré.**

Deux étapes se **déclarent terminales** (`topology`, rapport de preuve ; `package`, livrable final) : la règle
d'orphelinat n'a pas été assouplie, elle a été **rendue explicite**.

## 6. Entrypoint et replays clean-room

`run_pipeline.py` orchestre les étapes, s'arrête au premier échec, journalise en JSON, n'emploie jamais
`shell=True`, n'accède jamais au réseau, accepte un workspace vide, et offre `--dry-run`.

**Deux replays complets**, dans deux racines neuves dont une avec **espace et caractère Unicode** :

| Racine | master | compact | previews |
|---|---|---|---|
| `replay-1/` | `dbb57db3…` ✅ | `8024fd4c…` ✅ | **32** |
| `Replay 2 é/` | `dbb57db3…` ✅ | `8024fd4c…` ✅ | **32** |

**Les hashes historiques sont reproduits exactement.** Aucun hash de référence n'a été réécrit, aucune
ressemblance visuelle acceptée en substitut.

## 7. Package v2

```
manifest_scope: all-package-members-except-this-manifest
archive_entry_count = manifest_payload_entry_count + 1   →   62 = 61 + 1  ✅
```

**Auto-descriptif** : manifeste embarqué à la racine logique, portant schéma, identité, commit source,
`SOURCE_DATE_EPOCH`, hashes des sources, versions d'outils, membres triés avec taille/SHA-256/rôle, décomptes,
configuration Servier, hashes master et compact, licences, `ai_usage`, statut.

**Déterministe** : ordre lexicographique · chemins POSIX relatifs · timestamps normalisés · permissions
uniformes · compression explicite · commentaire vide · aucun `.DS_Store`, `._*`, xattr ni resource fork.
Construction depuis **deux racines distinctes** → **SHA-256 identique**.

| Champ | Valeur |
|---|---|
| Nom | `auren_bodymap_sb_asset_03_1_intake_package_v2.zip` |
| Entrées | **62** |
| Scripts | **14** |
| Previews | **32** |
| Octets | **1 449 359** |
| **SHA-256** | `f45e0dbf0a20fb9b11f0e0314c5588f19303724665e96b91ceb0e7c092957029` |

Le hash du ZIP reste **externe au ZIP** et n'est consigné que dans les documents Git.

## 8. Ce qui n'a pas changé

`MASTER: UNCHANGED` · `COMPACT: UNCHANGED` — la géométrie validée est **reproduite**, pas modifiée.
Contrat 11 zones, 14 IDs, `app/**`, `design/**`, `tests/**` et le gate d'intégration : **intouchés**.

## 9. Scope Git

**100 % `docs/**`** — 0 SVG, 0 ZIP, 0 PNG, 0 OBJ, 0 `.blend`, 0 `app/**`, 0 `tests/**`, 0 `design/**`,
0 dépendance, 0 fichier Custom.

---

## Verdict

**Verdict :** 🟢 **Sb_ASSET_03.1-fix: COMPLETE — REPRODUCIBILITY GAP CLOSED.** La cause racine
(`INCOMPLETE EXECUTABLE BUILD GRAPH`) est fermée : le producteur manquant est **scripté** avec les
**sélecteurs exacts** (117 `lats` / 157 `core`, récupérés et non reconstruits), et sa parité est **prouvée
byte-identique**. Le pipeline est **relocalisable** (module partagé, 14/14 scripts sans chemin absolu, sans
réseau, sans `shell=True`), son **graphe est complet et vérifié** (`NO ORPHAN INPUTS`, producteurs uniques,
sans cycle), et un **entrypoint** l'exécute de bout en bout depuis un workspace vide avec journal JSON et
`--dry-run`. **Deux replays clean-room** — dont un dans une racine à **espace et Unicode** — reproduisent
**exactement** les hashes historiques du master et du compact, avec **32 previews** chacun. Le **package v2**
est **auto-descriptif** (manifeste embarqué, règle `62 = 61 + 1` vérifiée) et **déterministe** (deux
constructions → même SHA-256). **Le package v1 et les preuves d'intake sont conservés** ; l'histoire du
premier échec n'est pas réécrite. `MASTER` et `COMPACT` **inchangés**. `AI_USAGE: NONE`.
`BODYMAP MASTER: NOT YET APPROVED` · `ASSET INTEGRATION GATE: BLOCKED`.

**Prochaine action** (séparée, non commencée) : `GO RESUME INTAKE — Sb_ASSET_03.2 from §11 using package v2`.
