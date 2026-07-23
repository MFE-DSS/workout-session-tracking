# SB_ASSET_03.1 — Clôture de reproductibilité

**Cycle** : `Sx_ASSET_03` (amendé SOURCE-REUSE-FIRST) · **Build** : `Sb_ASSET_03.1-fix` · **Date** : 2026-07-23

---

## 1. Cause racine (conservée telle qu'établie par l'intake)

```
INITIAL TECHNICAL INTAKE:
BLOCKED — NON-REPRODUCIBLE OUTPUT

ROOT CAUSES:
1. `servier_masks.py` consumes `servier_<zone>_raw.svg`;
2. no packaged script produces these files;
3. the Servier lats/core region selection was performed ad hoc;
4. scripts contain an absolute local BASE path;
5. the package manifest is external rather than embedded;
6. documented script count was 8, actual packaged count was 10.

CLASSIFICATION:
INCOMPLETE EXECUTABLE BUILD GRAPH
```

**Ce n'était pas du non-déterminisme.** Les étapes existantes étaient déterministes ; il manquait une **arête**
dans le graphe de build.

## 2. Correctif (1) — le producteur manquant

`procedure/scripts/extract_servier_regions.py` + `procedure/config/servier_region_selection.json`.

**Sélecteurs exacts récupérés**, jamais reconstruits par heuristique : les identifiants de formes ont été
extraits des artefacts validés de `Sb_ASSET_03.1`, en **ordre document**.

| Zone | Formes | Mode |
|---|---:|---|
| `lats` | **117** | `explicit-id-list` |
| `core` | **157** | `explicit-id-list` |

La région de bounding box initiale est conservée dans la configuration sous `historical_region_filter`,
**explicitement marquée comme non utilisée** pour la sélection.

Gardes : SHA-256 du PPTX vérifié **avant** extraction · refus si le nombre de formes converties ≠ **3 361** ·
refus sur sélecteur absent ou dupliqué · ordre stable · aucun choix interactif · aucune coordonnée locale ·
refus d'écriture hors `--workspace-root` · codes de sortie distincts (2 à 5).

## 3. Correctif (2) — relocalisation

Module partagé `procedure/scripts/pipeline_context.py` : résolution des racines, garde d'appartenance au
workspace, création bornée de dossiers, résolution d'exécutables (`shutil.which` + surcharges
`--blender/--inkscape/--potrace/--chrome`), codes d'erreur communs.

Les **8 scripts historiques porteurs d'un `BASE` absolu** ont été relocalisés vers ce module ; les 2 autres
prenaient déjà leurs chemins en arguments.

**Audit statique final : 14/14 scripts propres.**
`0` chaîne `/Users/` · `0` nom de compte · `0` `BASE` absolu · `0` `shell=True` · `0` import réseau ·
`0` `eval`/`exec` · `0` `__import__` dynamique · `0` suppression récursive · `0` secret ·
`0` chemin Homebrew ou `/Applications` obligatoire.

> Exception consignée : `__import__("mathutils")` dans `build_scene_and_render.py` — **argument littéral
> constant**, équivalent strict d'un import statique, module fourni par Blender. Accepté et déclaré.

## 4. Correctif (3) — graphe de build explicite

`procedure/config/pipeline_graph.json` déclare, pour chaque étape : script, entrées, sorties, configuration,
outils requis et dépendances amont. Un contrôleur prouve que **toute entrée est soit une source déclarée,
soit la sortie d'une étape**, qu'aucune sortie n'a deux producteurs, qu'il n'y a ni cycle ni étape orpheline.

```
BUILD GRAPH:
COMPLETE / NO ORPHAN INPUTS
```

`servier_lats_raw.svg` et `servier_core_raw.svg` ont désormais **`extract_servier_regions.py` comme
producteur déclaré**.

**Politique des étapes terminales** : une étape dont les sorties sont des livrables ou des preuves — et non
des intermédiaires — doit le **déclarer explicitement** (`terminal: true`). `topology` (rapport de preuve) et
`package` (livrable final) sont les deux seules concernées. La règle n'a pas été assouplie : elle a été
rendue explicite.

## 5. Correctif (4) — entrypoint complet

`procedure/scripts/run_pipeline.py` orchestre les étapes dans l'ordre, **s'arrête au premier échec**,
journalise chaque commande et son code retour en JSON, n'emploie **jamais `shell=True`**, n'accède **jamais au
réseau**, et accepte un **workspace entièrement vide**. Un mode `--dry-run` valide DAG, sources, outils et
destinations sans lancer Blender ni la vectorisation.

## 6. Correctif (5) — package auto-descriptif et déterministe

`intake_package_manifest.json` est désormais **embarqué à la racine logique** du ZIP.

```
manifest_scope: all-package-members-except-this-manifest
archive_entry_count = manifest_payload_entry_count + 1
```
Vérifié : **62 = 61 + 1**.

Le manifeste porte : `schema_version` · `package_id` · `package_version` · commit source ·
`SOURCE_DATE_EPOCH` · hashes des sources · versions d'outils · membres triés avec taille, SHA-256 et **rôle** ·
nombre de scripts · nombre de previews · configuration Servier · hashes master/compact · licences ·
`ai_usage` · statut.

**Convention de comptage des scripts, déclarée** : les **14** fichiers `.py` packagés comprennent les modules
utilitaires, les scripts exécutables **et** l'entrypoint. Le décompte « 8 scripts » du package v1 est
**abandonné** comme statut courant.

**Archive déterministe** : ordre lexicographique · chemins POSIX relatifs · timestamps normalisés
(`SOURCE_DATE_EPOCH` fixe, consigné) · permissions `0644` uniformes · `create_system` constant · compression
et niveau explicites · commentaire ZIP vide · aucun `.DS_Store`, `._*`, xattr ni resource fork.

## 7. Preuves

### Parité du maillon ajouté
| Sortie | SHA-256 | Verdict |
|---|---|---|
| `servier_slide3.svg` | `789fb3af5d805b70b1248f58585b34f195b7d36e1a270cb297995d30d459e188` | identique ✅ |
| `servier_lats_raw.svg` | `dc04a0171a880eaaf29c8ee83c03e6ddad5daa271b79cf314a2b9c5d114bca1b` | identique ✅ |
| `servier_core_raw.svg` | `fe01dc949af58e2adb53f429a6c65f71d9a0edf64f51d7492d3ce9ef4950e96b` | identique ✅ |

### Replay clean-room complet
| Artefact | SHA-256 attendu | Obtenu |
|---|---|---|
| master | `dbb57db333863434442b476277170017db442d83e2eced6e7191266ee9ecfa73` | **identique** ✅ |
| compact | `8024fd4ced62ca2010808bf85f94c3eaca4d334dde2b7c3b7683c3e5a4676c9a` | **identique** ✅ |

**32 previews** régénérées. **Aucun hash de référence n'a été réécrit.**

### Déterminisme de l'archive
Construction depuis **deux racines distinctes** → **SHA-256 identique**
`f45e0dbf0a20fb9b11f0e0314c5588f19303724665e96b91ceb0e7c092957029`.

## 8. Statuts

```
SERVIER PRODUCER: ADDED / BYTE-IDENTICAL PARITY PROVED
PIPELINE: RELOCATABLE / COMPLETE DAG / CLEAN-ROOM REPLAYED
PACKAGE V1: RETAINED / SUPERSEDED
PACKAGE V2: SELF-DESCRIBING / DETERMINISTIC / RELOCATABLE
MASTER: UNCHANGED
COMPACT: UNCHANGED
Sb_ASSET_03.2: READY TO RESUME AT §11
BODYMAP MASTER: NOT YET APPROVED
ASSET INTEGRATION GATE: BLOCKED
```

Le package v1 et les preuves d'intake `Sb_ASSET_03.2` sont **conservés intacts** comme preuves historiques du
premier échec. **L'histoire du blocage n'est pas réécrite.**
